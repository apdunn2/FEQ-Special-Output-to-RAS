import numpy as np
import pandas as pd


class FEQSpecialOutput:

    def __init__(self, special_output_df):
        """Do not use __init__() directly. Use FEQSpecialOutput.read_special_output_file() to create an instance from
         an FEQ special output file.

        :param special_output_df:
        """

        self._special_output_df = special_output_df

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

        new_special_output_df = pd.concat([self._special_output_df, other.get_data()], axis=1)

        return type(self)(new_special_output_df)

    def get_constituent(self, constituent_name, start_date=None, end_date=None, time_step=None):
        """

        :param constituent_name:
        :param start_date:
        :param end_date:
        :param time_step:
        :return:
        """

        constituent_level = self._special_output_df.columns.names.index('value')

        # get a cross section of the constituent values
        constituent_df = self._special_output_df.xs(constituent_name, axis=1, level=constituent_level)

        # if a time step is specified
        if time_step is not None:

            # get a series of the frequency requested
            index_start_date = constituent_df.index[0].date()
            index_end_date = constituent_df.index[-1]
            interval_index = pd.date_range(index_start_date, index_end_date, freq=time_step)

            # get indices not included in the constituent DataFrame and create an empty DataFrame with the
            # missing indices
            time_step_difference = interval_index.difference(constituent_df.index)
            empty_df = pd.DataFrame(index=time_step_difference)

            # add the empty DataFrame to the constituent DataFrame, sort, resample as frequency, and drop null values
            constituent_df = constituent_df.append(empty_df)
            constituent_df = constituent_df.sort_index()
            constituent_df = constituent_df.resample(time_step).asfreq()
            constituent_df = constituent_df.dropna(how='all')

        return constituent_df.truncate(start_date, end_date)

    def get_data(self):
        """

        :return:
        """

        return self._special_output_df.copy(deep=True)

    def get_max_constituent_value(self, constituent_name, start_date=None, end_date=None):
        """

        :param constituent_name:
        :param start_date:
        :param end_date:
        :return:
        """

        constituent_df = self.get_constituent(constituent_name, start_date, end_date)

        max_constituent_values = pd.DataFrame(constituent_df.max())

        max_constituent_values = max_constituent_values.transpose()

        max_constituent_values.index = ['Maximum_' + constituent_name]

        return max_constituent_values

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
