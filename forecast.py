import datetime
import pandas as pd
from RASSteadyFlowFileWriter import RASSteadyFlowFileWriter


class Forecast:
    def __init__(self, elevation_df):
        self._elevation_df = elevation_df

    @staticmethod
    def _combine_dataframes(args):
        return pd.concat(args, axis=1)

    def _get_unique_river_and_reach(self):
        """

        :return:
        """

        river_and_reach_columns = self._elevation_df.columns.droplevel(2)
        unique_combinations = river_and_reach_columns.unique()
        return unique_combinations.values

    @staticmethod
    def load_node_table(node_table_path):
        node_table = pd.read_csv(node_table_path)
        node_table['Node'] = node_table['Node'].astype(str)
        node_table['XS'] = node_table['XS'].astype(str)
        node_table['River & Reach'] = node_table['River'] + ',' + node_table['Reach']
        return node_table

    def node_to_cross_section(self, node_table):
        self._elevation_df.columns.names = ['river', 'reach', 'cross section']

        node_reference_table = node_table.copy(deep=True)
        node_reference_table.set_index('River', inplace=True)
        node_reference_table.set_index('Reach', inplace=True, append=True)
        node_reference_table.set_index('Node', inplace=True, append=True)

        list_of_tuples = [(river, reach, node_reference_table.loc[river, reach, node][0])
                          for river, reach, node in self._elevation_df.columns.values]

        new_columns = pd.MultiIndex.from_tuples(list_of_tuples)

        self._elevation_df.columns = new_columns

    def run_ras_forecast(self, node_table_path):
        title = datetime.date.today().strftime("%B %d, %Y")
        output_file_path = title + '.f01'
        node_table = self.load_node_table(node_table_path)
        self.node_to_cross_section(node_table)
        steady_flow_forecast = RASSteadyFlowFileWriter(self._elevation_df, title, output_file_path)
        steady_flow_forecast.run_write_methods()


if __name__ == '__main__':
    import os
    import feq

    data_directory = 'data'
    data_file_name = 'WBuncutx.wsq'
    data_file_path = os.path.join(data_directory, data_file_name)

    river = 'WestBranch'
    reach = 'MainStem'

    special_output = feq.FEQSpecialOutput(r"data\WBuncutx.wsq", river, reach)

    constituent = 'Elev'

    elevation_df = special_output.get_constituent(constituent)
    elevation_df = elevation_df[-4:]

    node_path = r"data\node_table.csv"

    forecaster = Forecast(elevation_df)
    forecaster.run_ras_forecast(node_path)

