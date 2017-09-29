import copy

import pandas as pd

import feq
import ras


class FEQToRAS:

    def __init__(self, node_table_path, feq_special_output):
        self._node_table = self._load_node_table(node_table_path)
        self._feq_special_output = feq_special_output

    @staticmethod
    def _adjust_node_elevation(node_table, elevation_df):

        if 'Elev Adj' in node_table.keys():
            for river, reach, node in elevation_df.columns:
                river_index = node_table['River'] == river
                reach_index = node_table['Reach'] == reach
                node_index = node_table['Node'] == node
                elevation_adjustment = node_table.loc[river_index & reach_index & node_index, 'Elev Adj'].values[0]
                elevation_df.loc[:, (river, reach, node)] += elevation_adjustment

    @staticmethod
    def _combine_dataframes(args):
        return pd.concat(args, axis=1)

    @staticmethod
    def _convert_node_to_cross_section(node_table, constituent_df):
        constituent_df.columns.names = ['river', 'reach', 'cross section']

        node_reference_table = node_table.copy(deep=True)
        node_reference_table.set_index('River', inplace=True)
        node_reference_table.set_index('Reach', inplace=True, append=True)
        node_reference_table.set_index('Node', inplace=True, append=True)

        list_of_tuples = [(river, reach, node_reference_table.loc[river, reach, node][0])
                          for river, reach, node in constituent_df.columns.values]

        new_columns = pd.MultiIndex.from_tuples(list_of_tuples)

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

    def get_ras_elevation(self, start_date=None, end_date=None, number_of_days=None, time_step=None):

        elevation_df = self._feq_special_output.get_constituent('Elev',
                                                                start_date=start_date,
                                                                end_date=end_date,
                                                                number_of_days=number_of_days,
                                                                time_step=time_step)

        self._adjust_node_elevation(self._node_table, elevation_df)
        self._convert_node_to_cross_section(self._node_table, elevation_df)

        return elevation_df

    def get_ras_flow(self, start_date=None, end_date=None, number_of_days=None, time_step=None):

        flow_df = self._feq_special_output.get_constituent('Flow',
                                                           start_date=start_date,
                                                           end_date=end_date,
                                                           number_of_days=number_of_days,
                                                           time_step=time_step)
        self._convert_node_to_cross_section(self._node_table, flow_df)

        return flow_df


class FEQRASMapper:

    def __init__(self, config):

        self._config = copy.deepcopy(config)
        self._export_options = None
        self._special_output = None
        self._ras_mapper = None
        ras.set_ras_path(self._config['RAS path'])

    def export_tile_cache(self):

        self._ras_mapper.export_tile_cache(self._export_options)

    def load_export_options(self):

        self._export_options = self._ras_mapper.get_export_options()
        self._export_options.plan_name = self._config['RasMapper']['Plan name']
        self._export_options.file_name = self._config['RasMapper']['Export database path']
        self._export_options.max_zoom = self._config['RasMapper']['Cache level']

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

    def write_feq_results_to_ras(self):

        node_file_path = self._config['Node table']
        feq_to_raser = FEQToRAS(node_file_path, self._special_output)

        time_step = self._config['Export time series']['Time step']
        number_of_days = self._config['Export time series']['Number of days']

        ras_elevation_df = feq_to_raser.get_ras_elevation(number_of_days=number_of_days, time_step=time_step)
        ras_flow_df = feq_to_raser.get_ras_flow(number_of_days=number_of_days, time_step=time_step)

        rasmap_file_path = self._config['RasMapper']['RASMAP file path']

        self._ras_mapper = ras.RasMapper()
        self._ras_mapper.load_rasmap_file(rasmap_file_path)

        h5_file_name = self._ras_mapper.get_results_file(self._export_options.plan_name)
        ras_results = ras.Results(h5_file_name)

        ras_results.write_data(ras_elevation_df, ras_flow_df)

    @classmethod
    def run_configuration(cls, config):

        feq_ras_mapper = cls(config)
        feq_ras_mapper.load_special_output()
        feq_ras_mapper.load_export_options()
        feq_ras_mapper.write_feq_results_to_ras()
        feq_ras_mapper.export_tile_cache()
