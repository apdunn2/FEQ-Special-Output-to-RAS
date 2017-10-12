import copy

import pandas as pd

import feq
from hydraulic import HydraulicTimeSeries
import ras


class FEQToRAS:

    def __init__(self, node_table_path, feq_special_output):
        self._node_table = self._load_node_table(node_table_path)
        self._feq_special_output = feq_special_output

    @staticmethod
    def _adjust_node_elevation(node_table, hydraulic_data):

        if 'Elev Adj' in node_table.keys():
            for river, reach, node, _ in hydraulic_data.columns:
                river_index = node_table['River'] == river
                reach_index = node_table['Reach'] == reach
                node_index = node_table['Node'] == node
                elevation_adjustment = node_table.loc[river_index & reach_index & node_index, 'Elev Adj'].values[0]
                hydraulic_data.loc[:, (river, reach, node, 'Elev')] += elevation_adjustment

    @staticmethod
    def _combine_dataframes(args):
        return pd.concat(args, axis=1)

    @staticmethod
    def _convert_node_to_cross_section(node_table, constituent_df):

        node_reference_table = node_table.copy(deep=True)
        node_reference_table.set_index('River', inplace=True)
        node_reference_table.set_index('Reach', inplace=True, append=True)
        node_reference_table.set_index('Node', inplace=True, append=True)

        list_of_tuples = [(river, reach, node_reference_table.loc[river, reach, node][0], value)
                          for river, reach, node, value in constituent_df.columns.values]

        new_columns = pd.MultiIndex.from_tuples(list_of_tuples, names=['river', 'reach', 'cross section', 'value'])

        constituent_df.columns = new_columns

    def _get_unique_river_and_reach(self):
        """

        :return:
        """

        river_and_reach_columns = self._elevation_df.columns.droplevel(2)
        unique_combinations = river_and_reach_columns.unique()
        return unique_combinations.values

    @staticmethod
    def _load_node_table(node_table_path):
        node_table = pd.read_csv(node_table_path, dtype={'Node': str, 'XS': str})
        node_table['River & Reach'] = node_table['River'] + ',' + node_table['Reach']
        return node_table

    def get_ras_time_series(self):
        feq_data = self._feq_special_output.get_data()
        self._adjust_node_elevation(self._node_table, feq_data)
        self._convert_node_to_cross_section(self._node_table, feq_data)
        return HydraulicTimeSeries(feq_data)

    def get_ras_elevation(self, start_date=None, end_date=None, number_of_days=None, time_step=None):

        ras_time_series = self.get_ras_time_series()
        elevation_df = ras_time_series.get_constituent('Elev',
                                                       start_date=start_date,
                                                       end_date=end_date,
                                                       number_of_days=number_of_days,
                                                       time_step=time_step)

        return elevation_df

    def get_ras_flow(self, start_date=None, end_date=None, number_of_days=None, time_step=None):

        ras_time_series = self.get_ras_time_series()
        flow_df = ras_time_series.get_constituent('Flow',
                                                  start_date=start_date,
                                                  end_date=end_date,
                                                  number_of_days=number_of_days,
                                                  time_step=time_step)

        return flow_df


class FEQRASMapper:

    def __init__(self, config):

        self._config = copy.deepcopy(config)
        self._special_output = None
        ras.set_ras_path(self._config['RAS path'])

    def load_special_output(self):

        special_output = []

        for reach, reach_config in self._config['Special output'].items():
            river = reach_config['River']
            spec_output_path = reach_config['File location']
            special_output.append(feq.SpecialOutput.read_special_output_file(spec_output_path, river, reach))

        feq_special_output = special_output[0]

        for spec_out in special_output[1:]:
            feq_special_output = feq_special_output.add_special_output(spec_out)

        self._special_output = feq_special_output

    def write_steady_flow_file(self, flow_file_name):

        node_file_path = self._config['Node table']
        feq_to_raser = FEQToRAS(node_file_path, self._special_output)

        time_step = self._config['Export time series']['Time step']
        number_of_days = self._config['Export time series']['Number of days']

        ras_time_series = feq_to_raser.get_ras_time_series()
        ras_data = ras_time_series.get_data(number_of_days=number_of_days, time_step=time_step)

        ras_steady_flow_file = ras.SteadyFlowFile(ras_data, self._config['Plan name'])
        ras_steady_flow_file.write_flow_file(flow_file_name)
