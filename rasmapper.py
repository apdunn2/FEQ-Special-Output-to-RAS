import sys
import os

RAS_PATH = r'C:\Program Files (x86)\HEC\HEC-RAS\5.0.3'
sys.path.append(RAS_PATH)

import clr
clr.AddReference('System.Windows')
clr.AddReference('RasMapperLib')
clr.AddReference('MapperLibAddon')

import System
from System.Windows.Forms import Application
from System.Xml import XmlDocument

from RasMapperLib import RASMapper, ResultsGroup, SharedData, TileCacheComputable, TileCacheOptions
from RasMapperLib.Utility import Path, XML
from MapperLibAddon import TileCacheComputer


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


class RasMapper:

    def __init__(self):

        self._doc = XmlDocument()
        self._results_group = ResultsGroup()

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
            SharedData.SRSFilename = Path.MakeAbsolute(XML.StringAttribute(xmlNode2, "Filename", ""),
                                                       SharedData.RasMapFilename)

    @staticmethod
    def _setup_gdal():

        gdal_sub_directory = 'GDAL'

        executable_directory, _ = os.path.split(Application.ExecutablePath)

        application_gdal_directory = os.path.join(executable_directory)

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

    def _load_layers(self, parent, xml_node):

        if xml_node is None:
            return

        xml_node_list = xml_node.SelectNodes("Layer")

        for xmlNode in xml_node_list:
            layer = RASMapper.LoadLayer(parent, xmlNode)
            if layer is not None:
                parent.Nodes.Add(layer)
                layer.XMLLoad(xmlNode)
                self._load_layers(layer, xmlNode)

    def _load_results(self):

        self._results_group = ResultsGroup()

        xml_node_1 = self._doc.SelectSingleNode('RASMapper')
        results_node = xml_node_1.SelectSingleNode(self._results_group.XMLNodeName)

        self._load_layers(self._results_group, results_node)

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

        tile_cache_options = TileCacheOptions(terrain_center_point, depth_map)

        export_options.set_tile_cache_options(tile_cache_options)

        # delete old database file if it exists
        if os.path.isfile(tile_cache_options.Filename):
            os.remove(tile_cache_options.Filename)

        cache_computable = TileCacheComputable(tile_cache_options, depth_map)

        computer = TileCacheComputer()
        computer.Run(cache_computable)

    def load_rasmap_file(self, rasmap_file_path):

        self._doc.Load(rasmap_file_path)

        SharedData.RasMapFilename = rasmap_file_path

        xml_node_1 = self._doc.SelectSingleNode('RASMapper')
        self._set_projection_path(xml_node_1)

        self._load_results()
