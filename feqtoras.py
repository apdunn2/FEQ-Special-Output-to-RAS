import pandas as pd


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
