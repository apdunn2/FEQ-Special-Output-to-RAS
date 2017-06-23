import numpy as np
import pandas as pd


def parse_spec_output(spec_output_path):

    number_of_header_lines = 3

    date_time_list = []
    spec_output_list = []
    
    with open(spec_output_path, 'r') as spec_output_file:
    
        # get the header lines
        headers = [next(spec_output_file) for x in range(number_of_header_lines)]
        
        values = []
        for value in headers[2].strip().split()[4:]:
            if value not in values:
                values.append(value)
            
        for line in spec_output_file.readlines():
            
            split_line = line.strip().split()
            date_string = ','.join(split_line[:3])
            try:
            
                hour = float(split_line[3])
                date_time_stamp = pd.to_datetime(date_string, format='%Y,%m,%d') \
                    + pd.Timedelta(hour, unit='h')
                date_time_list.append(date_time_stamp)
                
                first_value_column = 4
                
                # append values
                output_data = np.array(split_line[first_value_column:], dtype='|S7')
                output_data = np.genfromtxt(output_data)
                spec_output_list.append(output_data)
                
            except ValueError:
                continue
                
            except IndexError:
                continue

    date_time_index = pd.DatetimeIndex(date_time_list)
    
    nodes = headers[1].strip().split()
        
    columns = pd.MultiIndex.from_product([nodes, values], names=['node', 'value'])

    data = np.array(spec_output_list)
    
    spec_output_df = pd.DataFrame(data=data, index=date_time_index, columns=columns)

    return spec_output_df


class RASSteadyFlowFileWriter:
    def __init__(self, constituent_df, title, output_file_path, timestep):
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


class FEQSpecialOutput:
    def __init__(self, spec_output_filepath, constituent, river_name, reach_name):
        self._river_name = river_name
        self._reach_name = reach_name
        self._constituent_df = self._create_constituent_df(spec_output_filepath, constituent)

    def _create_constituent_df(self, filepath, constituent):
        special_output_df = parse_spec_output(filepath)
        special_output_df = special_output_df.xs(constituent, axis=1, level=1)
        special_output_df.columns = special_output_df.columns.astype('int')
        return special_output_df

    def filter_constituent_df_timestep(self, timestep_as_string):
        self._constituent_df = self._constituent_df.asfreq(timestep_as_string)

    def get_river_name(self):
        return self._river_name

    def get_reach_name(self):
        return self._reach_name

    def get_river_and_reach_name(self):
        return self.get_river_name() + ',' + self.get_reach_name()



    def get_FEQ_node_list(self):
        return list(self._constituent_df.columns)



    def get_water_surface_elevation(self, node, profile_index):
        return self._constituent_df[node][profile_index]




import os

data_directory = 'data'
data_file_name = 'WBuncutx.wsq'
data_file_path = os.path.join(data_directory, data_file_name)
node_table_filepath = r"D:\Python\FEQ to Ras\node_table.csv"

MainStem = FEQSpecialOutput(data_file_path, 'Elev', 'WestBranch', 'MainStem')
FlowDemo = RASSteadyFlowFileWriter(node_table_filepath, 'June22', 'D:\Dupage\WBMainStem\June22.f34', '1000H')
FlowDemo.add_reach(MainStem)
FlowDemo.run_write_methods()



"""if __name__ == "__main__":

    import os

    data_directory = 'data'
    data_file_name = 'WBuncutx.wsq'
    data_file_path = os.path.join(data_directory, data_file_name)

    special_output_df = parse_spec_output(data_file_path)

    constituent = 'Elev'

    elevation_df = special_output_df.xs(constituent, axis=1, level=1)

    spec_output_to_steady_flow(elevation_df, 'node_table.csv', 'D:\Dupage\WBMainStem\june20v2.f32')"""