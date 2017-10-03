import pandas as pd


class HydraulicTimeSeries:

    def __init__(self, time_series_df):

        self._time_series = time_series_df.copy(deep=True)

    def combine_time_series(self, other):

        new_time_series_df = pd.concat([self._time_series, other.get_data()], axis=1)

        return type(self)(new_time_series_df)

    def get_constituent(self, constituent_name, start_date=None, end_date=None, number_of_days=None, time_step=None):
        """

        :param constituent_name:
        :param start_date:
        :param end_date:
        :param number_of_days:
        :param time_step:
        :return:
        """

        time_series_df = self.get_data(start_date, end_date, number_of_days, time_step)

        constituent_level = time_series_df.columns.names.index('value')

        # get a cross section of the constituent values
        constituent_df = time_series_df.xs(constituent_name, axis=1, level=constituent_level)

        return constituent_df

    def get_data(self, start_date=None, end_date=None, number_of_days=None, time_step=None):
        """

        :param start_date:
        :param end_date:
        :param number_of_days:
        :param time_step:
        :return:
        """

        time_series = self._time_series.copy(deep=True)

        if number_of_days and (start_date or end_date):
            raise TypeError("start_date and end_date cannot be specified if number_of_days is")

        # if a time step is specified
        if time_step is not None:

            # get a series of the frequency requested
            index_start_date = time_series.index[0].date()
            index_end_date = time_series.index[-1]
            interval_index = pd.date_range(index_start_date, index_end_date, freq=time_step)

            # get indices not included in the constituent DataFrame and create an empty DataFrame with the
            # missing indices
            time_step_difference = interval_index.difference(time_series.index)
            empty_df = pd.DataFrame(index=time_step_difference)

            # add the empty DataFrame to the constituent DataFrame, sort, interpolate, resample as frequency,
            # and drop null values
            time_series = time_series.append(empty_df)
            time_series.sort_index(inplace=True)
            time_series.interpolate('time', inplace=True)
            time_series = time_series.resample(time_step).asfreq()
            time_series = time_series.dropna(how='all')

        if number_of_days:
            end_date = time_series.index[-1]
            start_date = end_date - pd.to_timedelta(number_of_days, 'days')

        return time_series.truncate(start_date, end_date)

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
