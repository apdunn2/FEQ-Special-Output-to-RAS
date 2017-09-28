import copy

import feq
import feqtoras
import ras


class FEQRASMapper:

    def __init__(self, config):

        self._config = copy.deepcopy(config)
        self._export_options = None
        self._special_output = None
        self._ras_mapper = None
        ras.set_ras_path(self._config['RAS path'])

    def export_tile_cache(self):

        self._ras_mapper.export_tile_cache(self._export_options)

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
        feq_to_raser = feqtoras.FEQToRAS(node_file_path, self._special_output)

        time_step = self._config['Export time series']['Time step']
        number_of_days = self._config['Export time series']['Number of days']

        ras_elevation_df = feq_to_raser.get_ras_elevation(number_of_days=number_of_days, time_step=time_step)
        ras_flow_df = feq_to_raser.get_ras_flow(number_of_days=number_of_days, time_step=time_step)

        rasmap_file_path = self._config['RasMapper']['RASMAP file path']

        self._ras_mapper = ras.RasMapper()
        self._ras_mapper.load_rasmap_file(rasmap_file_path)

        self._export_options = self._ras_mapper.get_export_options()
        self._export_options.plan_name = self._config['RasMapper']['Plan name']
        self._export_options.file_name = self._config['RasMapper']['Export database path']
        self._export_options.max_zoom = self._config['RasMapper']['Cache level']

        h5_file_name = self._ras_mapper.get_results_file(self._export_options.plan_name)
        ras_results = ras.Results(h5_file_name)

        ras_results.write_data(ras_elevation_df, ras_flow_df)

    @classmethod
    def run_configuration(cls, config):

        feq_ras_mapper = cls(config)
        feq_ras_mapper.load_special_output()
        feq_ras_mapper.write_feq_results_to_ras()
        feq_ras_mapper.export_tile_cache()

