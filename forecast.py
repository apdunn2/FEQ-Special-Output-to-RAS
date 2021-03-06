import datetime
import pandas as pd
from RASSteadyFlowFileWriter import RASSteadyFlowFileWriter


class Forecast:
    def __init__(self, elevation_df):
        self._elevation_df = elevation_df

    @staticmethod
    def _combine_dataframes(args):
        return pd.concat(args, axis=1)

    @staticmethod
    def load_node_table(node_table_path):
        node_table = pd.read_csv(node_table_path)
        node_table['Node'] = node_table['Node'].astype(str)
        node_table['XS'] = node_table['XS'].astype(str)
        node_table['River & Reach'] = node_table['River'] + ',' + node_table['Reach']
        return node_table

    def node_to_cross_section(self, node_table):
        self._elevation_df.columns.names = ['river', 'reach', 'cross section']
        for river in node_table['River'].unique():
            for reach in node_table['Reach'].unique():
                river_df = node_table[node_table['River'] == river]
                reach_df = river_df[river_df['Reach'] == reach]
                for index in reach_df.index:
                    node = reach_df['Node'][index]
                    cross_section = reach_df['XS'][index]
                    self._elevation_df.rename(columns={node: cross_section}, level=2, inplace=True)

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
    elevation_df = elevation_df['2017-04-29 19:00:00':'2017-04-30 19:00:00']

    node_path = r"data\node_table.csv"

    forecaster = Forecast(elevation_df)
    forecaster.run_ras_forecast(node_path)

