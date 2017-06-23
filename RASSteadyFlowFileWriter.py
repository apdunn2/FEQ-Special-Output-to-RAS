class RASSteadyFlowFileWriter:
    def __init__(self, constituent_df, title, output_file_path):
        self.reaches = []
        self.lines = []
        self.program_version = "5.03"
        self.title = title
        self.output_file_path = output_file_path
        self._constituent_df = constituent_df

    def get_program_version(self):
        return self.program_version

    def get_title(self):
        return self.title

    def get_number_of_profiles(self):
        return self._constituent_df.shape[0]

    def get_profile_list(self):
        profiles = self._constituent_df.index.strftime("%Y-%m-%d %H:%M:%S").tolist()
        profiles = ','.join(profiles)
        return profiles

    def create_dummy_flows(self):
        dummy_flows = ""
        count = 1
        for i in range(self.get_number_of_profiles()):
            dummy_flows += "     100"
            if count % 10 == 0:
                dummy_flows += "\n"
            count += 1
        return dummy_flows

    def write_header_information(self, lines):
        lines.append("Flow Title={0}\n".format(self.get_title()))
        lines.append("Program Version={0}\n".format(self.program_version))
        lines.append("Number of Profiles= {0}\n".format(self.get_number_of_profiles()))
        lines.append("Profile Names={0}\n".format(self.get_profile_list()))

    def write_reach_and_flows(self, lines):
        for river in self._constituent_df.columns.get_level_values(0):
            for reach in self._constituent_df.columns.get_level_values(1):
                river_and_reach = river + ',' + reach
                upstream_xs = self._constituent_df[river][reach].columns.max()
                lines.append("River Rch & RM={0: <27},{1}\n{2}\n".format(
                                  river_and_reach, upstream_xs, self.create_dummy_flows()))

    def write_reach_boundary_conditions(self, lines):
        for river in self._constituent_df.columns.get_level_values(0):
            for reach in self._constituent_df.columns.get_level_values(1):
                river_and_reach = river + ',' + reach
                lines.append("Boundary for River Rch & Prof#={0: <27}, "
                                  "{1}\nUp Type= 0\nDn Type= 3\nDn Slope=0.001\n".format(
                                  river_and_reach, 1))

    def write_water_surface_elevations(self, lines):
        for river in self._constituent_df.columns.get_level_values(0):
            for reach in self._constituent_df[river].columns.get_level_values(0):
                for cross_section in self._constituent_df[river][reach].columns.get_level_values(0):
                    for profile_index in range(self.get_number_of_profiles()):
                            water_surface_elevation = self._constituent_df[river][reach][cross_section][profile_index]
                            lines.append("Set Internal Change={0: <16},"
                                              "{1: <16},{2: <8}".format(river, reach, cross_section))
                            lines.append(", {0} , 3 , {1}\n".format(profile_index + 1, water_surface_elevation))

    def write_lines_to_flow_file(self, lines):
        with open(self.output_file_path, "w+") as f:
            f.writelines(lines)

    def run_write_methods(self):
        lines = []
        self.write_header_information(lines)
        self.write_reach_and_flows(lines)
        self.write_reach_boundary_conditions(lines)
        self.write_water_surface_elevations(lines)
        self.write_lines_to_flow_file(lines)
