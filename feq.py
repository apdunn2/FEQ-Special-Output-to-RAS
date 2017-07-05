import numpy as np
import pandas as pd


class FEQSpecialOutput:

    def __init__(self, spec_output_file_path, river_name, reach_name):
        """

        :param spec_output_file_path:
        :param river_name:
        :param reach_name:
        """

        self._river_name = river_name
        self._reach_name = reach_name
        self._special_output_df = self._create_special_output_df(spec_output_file_path, river_name, reach_name)

    @classmethod
    def _create_special_output_df(cls, spec_output_file_path, river_name, reach_name):
        """

        :param spec_output_file_path:
        :param river_name:
        :param reach_name:
        :return:
        """

        # load the special output file into a DataFrame
        special_output_df = cls._parse_special_output(spec_output_file_path)

        # add the river and reach names as outer levels of the columns index
        transposed_special_output_df = special_output_df.transpose()

        old_index_order = list(transposed_special_output_df.index.names)

        transposed_special_output_df['reach'] = reach_name
        transposed_special_output_df.set_index('reach', append=True, inplace=True)

        transposed_special_output_df['river'] = river_name
        transposed_special_output_df.set_index('river', append=True, inplace=True)

        new_index_order = ['river', 'reach'] + old_index_order
        transposed_special_output_df.index = transposed_special_output_df.index.reorder_levels(new_index_order)

        new_special_output_df = transposed_special_output_df.transpose()
        index_type = special_output_df.index.dtype
        new_index = new_special_output_df.index.astype(index_type)
        new_special_output_df.index = new_index

        return new_special_output_df

    @staticmethod
    def _parse_special_output(spec_output_path):

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
                    date_time_stamp = pd.to_datetime(date_string, format='%Y,%m,%d') + pd.Timedelta(hour, unit='h')
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

    def get_constituent(self, constituent_name, time_step=None):
        """

        :param constituent_name:
        :param time_step:
        :return:
        """

        constituent_level = self._special_output_df.columns.names.index('value')

        if time_step is None:

            constituent_df = self._special_output_df.xs(constituent_name, axis=1, level=constituent_level)

        # TODO handle interpolation

        return constituent_df

if __name__ == "__main__":

    import os

    data_directory = '../rasobserved/data'
    data_file_name = 'WBuncutx.wsq'
    data_file_path = os.path.join(data_directory, data_file_name)

    river = 'WestBranch'
    reach = 'Main'

    special_output = FEQSpecialOutput(r"data\WBuncutx.wsq", river, reach)

    constituent = 'Elev'

    elevation_df = special_output.get_constituent(constituent)
