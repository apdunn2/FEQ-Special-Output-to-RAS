import warnings

import numpy as np
import pandas as pd

from hydraulic import HydraulicTimeSeries


class SpecialOutput(HydraulicTimeSeries):

    @classmethod
    def _create_special_output_df(cls, special_output_df, river_name, reach_name):
        """

        :param special_output_df:
        :param river_name:
        :param reach_name:
        :return:
        """

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

    def add_special_output(self, other):
        """

        :param other:
        :return:
        """
        # TODO: Deprecate method
        warnings.warn("add_special_output() is deprecated. Use combine_time_series() instead.", DeprecationWarning)

        return self.combine_time_series(other)

    @classmethod
    def read_special_output_file(cls, spec_output_file_path, river_name, reach_name):
        """

        :param spec_output_file_path:
        :param river_name:
        :param reach_name:
        :return:
        """

        # load the special output file into a DataFrame
        from_special_output = cls._parse_special_output(spec_output_file_path)
        special_output_df = cls._create_special_output_df(from_special_output, river_name, reach_name)

        return cls(special_output_df)
