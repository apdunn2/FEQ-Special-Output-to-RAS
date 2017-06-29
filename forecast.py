import numpy as np
import datetime
import pandas as pd
from RASSteadyFlowFileWriter import RASSteadyFlowFileWriter
from feq import FEQSpecialOutput


class forecast:
    def __init__(self, *args):
        # self._node_table = self._load_node_table(node_path)
        self._elevation_df = self._combine_dataframes(args)

    def _combine_dataframes(self, args):
        return pd.concat(args, axis=1)

    def load_node_table(self, node_table_path):
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

    def run_RAS_forecast(self, node_table_path):
        title = datetime.date.today().strftime("%B %d, %Y")
        output_file_path = title + 'f.40'
        node_table = self.load_node_table(node_table_path)
        self.node_to_cross_section(node_table)
        steady_flow_forecast = RASSteadyFlowFileWriter(self._elevation_df, title, output_file_path)
        steady_flow_forecast.run_write_methods()



node_path = r"D:\Python\FEQ to Ras\node_table2.csv"
forecaster = forecast(main_resample, creek_resample)
forecaster.run_RAS_forecast(node_path)
