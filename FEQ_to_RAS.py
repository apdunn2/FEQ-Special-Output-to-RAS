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


class RASFlowFileWriter:
    def __init__(self, node_table_filepath, title, output_file_path, timestep):
        self.reaches = []
        self.lines = []
        self.program_version = "5.03"
        self.title = title
        self.output_file_path = output_file_path
        self._node_table = self._load_node_table(node_table_filepath)
        self.timestep = timestep

    def add_reach(self, FEQSpecialOutput):
        self.reaches.append(FEQSpecialOutput)

    def _load_node_table(self, node_table_filepath):
        node_table = pd.read_csv(node_table_filepath)
        node_table = node_table.set_index('Node')
        node_table['XS'] = node_table['XS'].astype(str)
        node_table['River & Reach'] = node_table['River'] + ',' + node_table['Reach']
        return node_table

    def get_program_version(self):
        return self.program_version

    def get_title(self):
        return self.title

    def filter_reach_timesteps(self):
        for reach in self.reaches:
            reach.filter_constituent_df_timestep(self.timestep)

    def write_header_information(self):
        self.lines.append("Flow Title={0}\n".format(self.get_title()))
        self.lines.append("Program Version={0}\n".format(self.program_version))
        self.lines.append("Number of Profiles= {0}\n".format(self.reaches[0].get_number_of_profiles()))
        self.lines.append("Profile Names={0}\n".format(self.reaches[0].get_profile_list()))

    def write_reach_and_flows(self):
        river_and_reach_groups = self.group_by_river_and_reach()
        for reach in self.reaches:
            river_and_reach = reach.get_river_and_reach_name()
            upstream_xs = river_and_reach_groups.get_group(river_and_reach)['XS'].max()
            self.lines.append("River Rch & RM={0: <27},{1}\n{2}\n".format(
                              river_and_reach, upstream_xs, reach.create_dummy_flows()))

    def write_reach_boundary_conditions(self):
        for reach_index in range(len(self.reaches)):
            reach = self.reaches[reach_index]
            self.lines.append("Boundary for River Rch & Prof#={0: <27}, "
                              "{1}\nUp Type= 0\nDn Type= 3\nDn Slope=0.001\n".format(
                              reach.get_river_and_reach_name(), reach_index + 1))

    def group_by_river_and_reach(self):
        return self._node_table.groupby('River & Reach')

    def write_water_surface_elevations(self):
        node_table_groupby = self.group_by_river_and_reach()
        for reach in self.reaches:
            river_and_reach = reach.get_river_and_reach_name()
            river_and_reach_node_table = node_table_groupby.get_group(river_and_reach)
            for profile_index in range(reach.get_number_of_profiles()):
                for node in reach.get_FEQ_node_list():
                    RAS_xs = river_and_reach_node_table['XS'][node]
                    water_surface_elevation = reach.get_water_surface_elevation(node, profile_index)
                    river_name = reach.get_river_name()
                    reach_name = reach.get_reach_name()
                    self.lines.append("Set Internal Change={0: <16},{1: <16},{2: <8}".format(river_name, reach_name, RAS_xs))
                    self.lines.append(", {0} , 3 , {1}\n".format(profile_index + 1, water_surface_elevation))

    def write_lines_to_flow_file(self):
        with open(self.output_file_path, "w+") as f:
            f.writelines(self.lines)

    def run_write_methods(self):
        self.filter_reach_timesteps()
        self.write_header_information()
        self.write_reach_and_flows()
        self.write_reach_boundary_conditions()
        self.write_water_surface_elevations()
        self.write_lines_to_flow_file()


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

    def get_profile_list(self):
        profiles = self._constituent_df.index.strftime("%Y-%m-%d %H:%M:%S").tolist()
        profiles = ','.join(profiles)
        return profiles

    def get_FEQ_node_list(self):
        return list(self._constituent_df.columns)

    def get_number_of_profiles(self):
        return self._constituent_df.shape[0]

    def get_water_surface_elevation(self, node, profile_index):
        return self._constituent_df[node][profile_index]

    def create_dummy_flows(self):
        dummy_flows = ""
        count = 1
        for i in range(self.get_number_of_profiles()):
            dummy_flows += "     100"
            if count % 10 == 0:
                dummy_flows += "\n"
            count += 1
        return dummy_flows


import os

data_directory = 'data'
data_file_name = 'WBuncutx.wsq'
data_file_path = os.path.join(data_directory, data_file_name)
node_table_filepath = r"D:\Python\FEQ to Ras\node_table.csv"

MainStem = FEQSpecialOutput(data_file_path, 'Elev', 'WestBranch', 'MainStem')
FlowDemo = RASFlowFileWriter(node_table_filepath, 'June22', 'D:\Dupage\WBMainStem\June22.f34', '1000H')
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