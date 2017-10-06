import sys
import os

from anytree import Node
import clr
import numpy as np
import pandas as pd
import pythoncom

clr.AddReference('System.Windows')

import System
from System.Windows.Forms import Application
from System.Xml import XmlDocument


defaultNamedNotOptArg = pythoncom.Empty

rasmapperlib = None
mapperlibaddon = None

RAS_PATH = None
RAS_VERSION = '5.0.3'


def set_ras_path(ras_path):
    global RAS_PATH

    if not os.path.isdir(ras_path):
        raise NotADirectoryError(ras_path + " is not a directory")

    RAS_PATH = ras_path

    _import_ras_assemblies(ras_path)


def set_ras_version(version):

    global RAS_VERSION
    RAS_VERSION = version


def _import_ras_assemblies(ras_path):

    sys.path.append(ras_path)

    global rasmapperlib
    clr.AddReference('RasMapperLib')
    import RasMapperLib
    rasmapperlib = RasMapperLib

    global mapperlibaddon
    clr.AddReference('MapperLibAddon')
    import MapperLibAddon
    mapperlibaddon = MapperLibAddon


class ExportOptions:

    def __init__(self, ras_mapper):

        self._ras_mapper = ras_mapper

        self._dataset_identifier = 'depth'
        self._file_name = None
        self._is_profile = True
        self._max_zoom = 12
        self._plan_name = None

        self._start_profile = None
        self._end_profile = None

    def set_tile_cache_options(self, tile_cache_options):

        tile_cache_options.DatasetIdentifier = self._dataset_identifier
        tile_cache_options.MaxZoom = self._max_zoom
        tile_cache_options.IsProfile = self._is_profile

        if self._file_name:
            tile_cache_options.Filename = self._file_name

        tile_cache_options.StartProfile = self._start_profile
        tile_cache_options.EndProfile = self._end_profile

    @property
    def dataset_identifier(self):
        return self._dataset_identifier

    @property
    def end_profile(self):
        return self._end_profile

    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, value):
        self._file_name = value

    @property
    def max_zoom(self):
        return self._max_zoom

    @max_zoom.setter
    def max_zoom(self, value):

        if (int(value) < 12) or (18 < int(value)):
            raise ValueError("Value must be an integer between 12 and 18.")

        self._max_zoom = int(value)

    @property
    def plan_name(self):
        return self._plan_name

    @plan_name.setter
    def plan_name(self, value):

        if value not in self._ras_mapper.get_plan_names():
            raise ValueError("Invalid plan name")

        self._plan_name = value
        depth_map = self._ras_mapper.get_depth_map(self._plan_name)
        self._start_profile = depth_map.Results.ProfileNames[0]
        self._end_profile = depth_map.Results.ProfileNames[-1]

    @property
    def start_profile(self):
        return self._start_profile


class RASControllerEventHandler:

    _message_client = None

    def set_message_client(self, message_client):
        self._message_client = message_client

    def OnComputeProgressEvent(self, Progress=defaultNamedNotOptArg):
        self._message_client.update_progress(Progress)

    def OnComputeMessageEvent(self, eventMessage=defaultNamedNotOptArg):
        self._message_client.add_message(eventMessage)

    def OnComputeComplete(self):
        self._message_client.compute_complete()


class RasMapper:

    def __init__(self):

        self._ras_mapper = rasmapperlib.RASMapper()

        self._setup_gdal()

    def _get_results(self, plan_name):

        plan_results = None

        for results in self._results_group.FindAllResults():
            if results.Name == plan_name:
                plan_results = results
                break

        return plan_results

    @staticmethod
    def _set_projection_path(xml_node_1):

        xmlNode2 = xml_node_1.SelectSingleNode("RASProjectionFilename")
        if xmlNode2 is not None:
            rasmapperlib.SharedData.SRSFilename = rasmapperlib.Utility.Path.MakeAbsolute(
                rasmapperlib.Utility.XML.StringAttribute(xmlNode2, "Filename", ""),
                rasmapperlib.SharedData.RasMapFilename)

    @staticmethod
    def _setup_gdal():

        gdal_sub_directory = 'GDAL'

        executable_directory, _ = os.path.split(Application.ExecutablePath)

        application_gdal_directory = os.path.join(executable_directory, gdal_sub_directory)

        if not os.path.isdir(application_gdal_directory):
            raise NotADirectoryError('Cannot find GDAL directory: ' + application_gdal_directory)

        system_path = System.Environment.GetEnvironmentVariable('PATH')

        gdal_path = os.path.join(RAS_PATH, gdal_sub_directory)

        gdal_tool_directory = os.path.join(gdal_path, 'bin')
        if gdal_tool_directory not in system_path:
            system_path += ';' + gdal_tool_directory

        System.Environment.SetEnvironmentVariable('PATH', system_path)

        gdal_data_directory = os.path.join(gdal_path, 'data')
        System.Environment.SetEnvironmentVariable('GDAL_DATA', gdal_data_directory)

        gdal_proj_lib_path = os.path.join(gdal_tool_directory, 'share')
        System.Environment.SetEnvironmentVariable('PROJ_LIB', gdal_proj_lib_path)

        gdal_plugin_directory = os.path.join(gdal_tool_directory, 'gdalplugins')
        System.Environment.SetEnvironmentVariable('GDAL_DRIVER_PATH', gdal_plugin_directory)

    def _load_results(self):

        self._results_group = self._ras_mapper.ResultsGroup

    def get_depth_map(self, plan_name):

        plan_results = self._get_results(plan_name)

        depth_map = None

        if plan_results is not None:

            for map_ in plan_results.FindAllMaps():
                if map_.Name == 'depth':
                    depth_map = map_
                    break

        return depth_map

    def get_export_options(self):
        return ExportOptions(self)

    def get_results_file(self, plan_name):

        plan_results = self._get_results(plan_name)
        return plan_results.HDFFilename

    def get_plan_names(self):

        plan_names = [results.Name for results in self._results_group.FindAllResults()]

        return plan_names

    def export_tile_cache(self, export_options):

        depth_map = self.get_depth_map(export_options.plan_name)

        depth_map_terrain = depth_map.Results.Geometry.Terrain
        terrain_center_point = depth_map_terrain.Extent.CenterPointM()

        depth_map.Results.Geometry.CompleteForComputations()
        depth_map.Results.Geometry.XSInterpolationSurface().LoadIfNeeded()

        tile_cache_options = rasmapperlib.TileCacheOptions(terrain_center_point, depth_map)

        export_options.set_tile_cache_options(tile_cache_options)

        # delete old database file if it exists
        if os.path.isfile(tile_cache_options.Filename):
            os.remove(tile_cache_options.Filename)

        cache_computable = rasmapperlib.TileCacheComputable(tile_cache_options, depth_map)

        computer = mapperlibaddon.TileCacheComputer()
        computer.Run(cache_computable)

    def load_rasmap_file(self, rasmap_file_path):

        rasmapperlib.SharedData.RasMapFilename = rasmap_file_path
        self._ras_mapper.LoadRASMapFile()

        self._load_results()


class ResultsFile:

    def __init__(self, hdf5_file_name):

        self._h5_file_name = hdf5_file_name
        self._h5_helper = mapperlibaddon.H5Helper(hdf5_file_name)

        self._root_node = self._create_hdf_tree()

    @staticmethod
    def _create_hdf_tree():

        root_node = Node('')

        results_group = Node('Results', parent=root_node)
        steady_group = Node('Steady', parent=results_group)
        steady_output_group = Node('Output', parent=steady_group)

        output_blocks_group = Node('Output Blocks', parent=steady_output_group)
        base_output_group = Node('Base Output', parent=output_blocks_group)
        steady_profiles_group = Node('Steady Profiles', parent=base_output_group)
        profile_names_location = Node('Profile Names', parent=steady_profiles_group)

        cross_sections_group = Node('Cross Sections', parent=steady_profiles_group)
        cross_section_variables_location = Node('Cross Section Variables', parent=cross_sections_group)
        water_surface_location = Node('Water Surface', parent=cross_sections_group)
        flow_location = Node('Flow', parent=cross_sections_group)

        additional_variables_group = Node('Additional Variables', parent=cross_sections_group)
        area_flow_total_location = Node('Area Flow Total', parent=additional_variables_group)
        area_including_location = Node('Area including Ineffective Total', parent=additional_variables_group)
        conveyance_total_location = Node('Conveyance Total', parent=additional_variables_group)
        top_width_total_location = Node('Top Width Total', parent=additional_variables_group)

        geometry_info_group = Node('Geometry Info', parent=steady_output_group)
        cross_section_info_group = Node('Cross Section Only', parent=geometry_info_group)

        return root_node

    def _fill_other_data(self, size):

        fill_data = np.tile(np.nan, size)

        cross_section_variables_location = self._get_hdf_path('Cross Section Variables')
        self._write_dataset(cross_section_variables_location, np.tile(np.nan, (size[0], 34, size[1])))

        area_flow_total_location = self._get_hdf_path('Area Flow Total')
        self._write_dataset(area_flow_total_location, fill_data)

        area_including_location = self._get_hdf_path('Area including Ineffective Total')
        self._write_dataset(area_including_location, fill_data)

        conveyance_total_location = self._get_hdf_path('Conveyance Total')
        self._write_dataset(conveyance_total_location, fill_data)

        top_width_total_location = self._get_hdf_path('Top Width Total')
        self._write_dataset(top_width_total_location, fill_data)

    def _get_columns(self):

        xs_info = self.get_cross_section_info()
        columns = \
            pd.MultiIndex.from_tuples(
                [(river, reach, cross_section) for river, reach, cross_section in xs_info.as_matrix()])

        return columns

    def _get_hdf_path(self, dataset_name):

        node_names = [node.name for node in self._root_node.descendants]
        dataset_node_index = node_names.index(dataset_name)
        dataset_node = self._root_node.descendants[dataset_node_index]

        return '/'.join([node.name for node in dataset_node.path])

    def _write_dataset(self, dataset_location, data):

        if isinstance(data, list):
            data_type = System.String
            array_to_write = System.Array.CreateInstance(data_type, len(data))
            for i in range(len(data)):
                array_to_write.SetValue(data_type(data[i]), i)

        elif (data.dtype == np.dtype("<f4")) or (data.dtype == np.double):
            data_type = System.Single
            array_to_write = System.Array.CreateInstance(data_type, data.shape)
            it = np.nditer(data, flags=['multi_index'])
            while not it.finished:
                array_to_write.SetValue(data_type(data[it.multi_index]), *it.multi_index)
                it.iternext()

        self._h5_helper.WriteHDF(dataset_location, array_to_write)

    def get_cross_section_info(self):

        xs_info_location = self._get_hdf_path('Cross Section Only')

        xs_info_dataset = self._h5_helper.Read1DimDataset[System.String](xs_info_location)

        data = [line.split() for line in xs_info_dataset]

        columns = ['River', 'Reach', 'RiverStation']

        return pd.DataFrame(data=data, columns=columns)

    def write_data(self, elevation_df=None, flow_df=None):

        columns = self._get_columns()

        water_surface_location = self._get_hdf_path('Water Surface')
        flow_location = self._get_hdf_path('Flow')

        if (elevation_df is not None) and (flow_df is not None):

            if not ((elevation_df.index == flow_df.index).all() and (elevation_df.columns == flow_df.columns).all()
                    and (elevation_df.columns == columns).all()):
                raise ValueError("DataFrames must have equal index, and columns")

            profile_df = elevation_df
            self._write_dataset(flow_location, flow_df.as_matrix().astype("<f4"))
            self._write_dataset(water_surface_location, elevation_df.as_matrix().astype("<f4"))

        elif elevation_df is not None:

            if not (elevation_df.columns == columns).all():
                raise ValueError("Columns must be equal")

            profile_df = elevation_df
            self._write_dataset(flow_location, np.nan)
            self._write_dataset(water_surface_location, elevation_df.as_matrix().astype("<f4"))

        elif flow_df is not None:

            if not (flow_df.columns == columns).all():
                raise ValueError("Columns must be equal")

            profile_df = flow_df
            self._write_dataset(flow_location, flow_df.as_matrix().astype("<f4"))
            self._write_dataset(water_surface_location, np.nan)

        else:

            raise ValueError("A DataFrame must be specified")

        profile_names = list(profile_df.index.map(str))
        profile_names_location = self._get_hdf_path('Profile Names')
        self._write_dataset(profile_names_location, profile_names)

        self._fill_other_data(profile_df.shape)


class SteadyFlowFile:

    def __init__(self, constituent_df, title):
        self._ras_version = RAS_VERSION
        self._title = title
        self._constituent_df = constituent_df

    def _add_header_information(self, lines):
        lines.append("Flow Title={0}\n".format(self._title))
        lines.append("Program Version={0}\n".format(self._ras_version))
        lines.append("Number of Profiles= {0}\n".format(self._get_number_of_profiles()))
        lines.append("Profile Names={0}\n".format(self._get_profile_list()))

    def _add_reach_and_flows(self, lines):

        max_number_of_columns = 10
        number_of_flow_values = self._get_number_of_profiles()
        number_of_rows = number_of_flow_values // max_number_of_columns + 1

        # get the number of full rows
        number_of_columns = [max_number_of_columns] * (number_of_rows - 1)

        # append the last row with the number of remaining columns
        number_of_columns.append(number_of_flow_values % max_number_of_columns)

        column_indices = np.cumsum(np.array([0] + number_of_columns))

        section_lines = []
        section_heading_format = 'River Rch & RM={},{},{}\n'

        flow_value_format = '{:8g}'

        for river, reach, river_mile, _ in self._constituent_df.columns.values:
            section_heading = section_heading_format.format(river, reach, river_mile)
            section_lines.append(section_heading)
            flow_series = self._constituent_df[(river, reach, river_mile, 'Flow')]
            for row_number in range(number_of_rows):
                row_flow_values = flow_series[column_indices[row_number]:column_indices[row_number + 1]].values
                row_flow_format = flow_value_format * number_of_columns[row_number]
                row_formatted_flow = row_flow_format.format(*row_flow_values)
                section_lines.append(row_formatted_flow + '\n')

        lines.extend(section_lines)

    def _add_reach_boundary_conditions(self, lines):
        for river, reach in self._get_unique_river_and_reach():
            river_and_reach = river + ',' + reach
            lines.append("Boundary for River Rch & Prof#={0: <27}, "
                         "{1}\nUp Type= 0\nDn Type= 3\nDn Slope=0.001\n".format(river_and_reach, 1))

    def _add_water_surface_elevations(self, lines):
        for river, reach, cross_section, _ in self._constituent_df.columns.values:
            for profile_index in range(self._get_number_of_profiles()):
                    water_surface_elevation = self._constituent_df.ix[profile_index,
                                                                      (river, reach, cross_section, 'Elev')]
                    lines.append("Set Internal Change={0: <16},"
                                 "{1: <16},{2: <8}".format(river, reach, cross_section))
                    lines.append(", {0} , 3 , {1}\n".format(profile_index + 1, water_surface_elevation))

    def _get_number_of_profiles(self):
        return self._constituent_df.shape[0]

    def _get_profile_list(self):
        try:
            profiles = self._constituent_df.index.strftime("%Y-%m-%d %H:%M:%S").tolist()
            profiles = ','.join(profiles)
            return profiles
        except AttributeError:
            profiles = self._constituent_df.index.tolist()
            profiles = ','.join(profiles)
            return profiles

    def _get_unique_river_and_reach(self):
        """

        :return:
        """

        river_and_reach_columns = self._constituent_df.columns.droplevel(3).droplevel(2)
        unique_combinations = river_and_reach_columns.unique()
        return unique_combinations.values

    def write_flow_file(self, output_file_path):
        lines = []
        self._add_header_information(lines)
        self._add_reach_and_flows(lines)
        self._add_reach_boundary_conditions(lines)
        self._add_water_surface_elevations(lines)

        with open(output_file_path, "w+") as f:
            f.writelines(lines)
