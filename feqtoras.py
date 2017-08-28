import datetime
import pandas as pd

from ras import RASSteadyFlowFileWriter


class FEQToRAS:

    def __init__(self, elevation_df):
        self._elevation_df = elevation_df.copy(deep=True)

    def _adjust_node_elevation(self, node_table):
        for i in range(node_table.shape[0]):
            river = node_table.loc[i, 'River']
            reach = node_table.loc[i, 'Reach']
            node = node_table.loc[i, 'Node']
            elevation_adjustment = node_table.loc[i, 'Elev Adj']
            self._elevation_df.loc[:, (river, reach, node)] += elevation_adjustment

    @staticmethod
    def _combine_dataframes(args):
        return pd.concat(args, axis=1)

    def _convert_node_to_cross_section(self, node_table):
        self._elevation_df.columns.names = ['river', 'reach', 'cross section']

        node_reference_table = node_table.copy(deep=True)
        node_reference_table.set_index('River', inplace=True)
        node_reference_table.set_index('Reach', inplace=True, append=True)
        node_reference_table.set_index('Node', inplace=True, append=True)

        list_of_tuples = [(river, reach, node_reference_table.loc[river, reach, node][0])
                          for river, reach, node in self._elevation_df.columns.values]

        new_columns = pd.MultiIndex.from_tuples(list_of_tuples)

        self._elevation_df.columns = new_columns

    def _get_unique_river_and_reach(self):
        """

        :return:
        """

        river_and_reach_columns = self._elevation_df.columns.droplevel(2)
        unique_combinations = river_and_reach_columns.unique()
        return unique_combinations.values

    @staticmethod
    def _load_node_table(node_table_path):
        node_table = pd.read_csv(node_table_path)
        node_table['Node'] = node_table['Node'].astype(str)
        node_table['XS'] = node_table['XS'].astype(str)
        node_table['River & Reach'] = node_table['River'] + ',' + node_table['Reach']
        return node_table

    def write_ras_flow_file(self, node_table_path):
        title = datetime.datetime.today().strftime("%B %d, %Y, %H%M")
        output_file_path = title + '.f01'
        node_table = self._load_node_table(node_table_path)

        if 'Elev Adj' in node_table.keys():
            self._adjust_node_elevation(node_table)

        self._convert_node_to_cross_section(node_table)
        steady_flow_forecast = RASSteadyFlowFileWriter(self._elevation_df, title)
        steady_flow_forecast.write_flow_file(output_file_path)


if __name__ == '__main__':
    import os
    import feq

    data_directory = 'data'
    data_file_name_main = "WB_mainstem.wsq"
    data_path_main = os.path.join(data_directory, data_file_name_main)

    data_file_name_wf = "WB_WinfieldCr.wsq"
    data_path_wf = os.path.join(data_directory, data_file_name_wf)

    main = feq.FEQSpecialOutput.read_special_output_file(data_path_main, 'WestBranch', 'MainStem')
    wf_creek = feq.FEQSpecialOutput.read_special_output_file(data_path_wf, 'WestBranch', 'WinfieldCr')

    combined_spec_output = main.add_special_output(wf_creek)
    elevation_df = combined_spec_output.get_constituent('Elev', start_date='2017-07-15 00:00:00', time_step='6H')

    forecaster = FEQToRAS(elevation_df)

    node_directory = 'data'
    node_file_name = "node_table.csv"
    node_file_path = os.path.join(node_directory, node_file_name)

    forecaster.write_ras_flow_file(node_file_path)
