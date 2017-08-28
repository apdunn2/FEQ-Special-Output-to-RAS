RAS_VERSION = "5.03"


class RASSteadyFlowFileWriter:

    def __init__(self, constituent_df, title):
        self._ras_version = RAS_VERSION
        self._title = title
        self._constituent_df = constituent_df

    def _add_header_information(self, lines):
        lines.append("Flow Title={0}\n".format(self._title))
        lines.append("Program Version={0}\n".format(self._ras_version))
        lines.append("Number of Profiles= {0}\n".format(self._get_number_of_profiles()))
        lines.append("Profile Names={0}\n".format(self._get_profile_list()))

    def _add_reach_and_flows(self, lines):
        unique_river_and_reach = self._get_unique_river_and_reach()
        for river, reach in unique_river_and_reach:
            river_and_reach = river + ',' + reach
            cross_sections = self._constituent_df[river][reach].columns.values.astype('float')
            max_index = cross_sections.argmax()
            upstream_xs = self._constituent_df[river][reach].columns[max_index]
            lines.append("River Rch & RM={0: <27},{1}\n{2}\n".format(
                         river_and_reach, upstream_xs, self._create_dummy_flows()))

    def _add_reach_boundary_conditions(self, lines):
        unique_river_and_reach = self._get_unique_river_and_reach()
        for river, reach in unique_river_and_reach:
            river_and_reach = river + ',' + reach
            lines.append("Boundary for River Rch & Prof#={0: <27}, "
                         "{1}\nUp Type= 0\nDn Type= 3\nDn Slope=0.001\n".format(river_and_reach, 1))

    def _add_water_surface_elevations(self, lines):
        for river, reach, cross_section in self._constituent_df.columns.values:
            for profile_index in range(self._get_number_of_profiles()):
                    water_surface_elevation = self._constituent_df.ix[profile_index, (river, reach, cross_section)]
                    lines.append("Set Internal Change={0: <16},"
                                 "{1: <16},{2: <8}".format(river, reach, cross_section))
                    lines.append(", {0} , 3 , {1}\n".format(profile_index + 1, water_surface_elevation))

    def _create_dummy_flows(self):
        dummy_flows = ""
        count = 1
        for i in range(self._get_number_of_profiles()):
            dummy_flows += "     100"
            if count % 10 == 0:
                dummy_flows += "\n"
            count += 1
        return dummy_flows

    def _get_number_of_profiles(self):
        return self._constituent_df.shape[0]

    def _get_profile_list(self):
        try:
            profiles = self._constituent_df.index.strftime("%Y-%m-%d %H:%M:%S").tolist()
            profiles = ','.join(profiles)
            return profiles
        except AttributeError:
            profiles = self._constituent_df.index.tolist()
            profiles = ','.join(profiles)
            return profiles

    def _get_unique_river_and_reach(self):
        """

        :return:
        """

        river_and_reach_columns = self._constituent_df.columns.droplevel(2)
        unique_combinations = river_and_reach_columns.unique()
        return unique_combinations.values

    def write_flow_file(self, output_file_path):
        lines = []
        self._add_header_information(lines)
        self._add_reach_and_flows(lines)
        self._add_reach_boundary_conditions(lines)
        self._add_water_surface_elevations(lines)

        with open(output_file_path, "w+") as f:
            f.writelines(lines)
