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


class RasMapper:

    def __init__(self):

        self._doc = XmlDocument()
        self._results_group = ResultsGroup()

        self._setup_gdal()

    @staticmethod
    def _find_depth_map(plan_name, results_group):

        feq_forecast_results = None
        depth_map = None

        for results in results_group.FindAllResults():
            if results.Name == plan_name:
                feq_forecast_results = results
                break

        if feq_forecast_results is not None:

            for map_ in feq_forecast_results.FindAllMaps():
                if map_.Name == 'depth':
                    depth_map = map_
                    break

        return depth_map

    @staticmethod
    def _set_projection_path(xml_node_1):

        xmlNode2 = xml_node_1.SelectSingleNode("RASProjectionFilename")
        if xmlNode2 is not None:
            SharedData.SRSFilename = Path.MakeAbsolute(XML.StringAttribute(xmlNode2, "Filename", ""),
                                                       SharedData.RasMapFilename)

    def _get_tile_cache_computable(self, export_options):

        depth_map = self._load_depth_map('FEQ forecast')

        cache_computable = None

        if depth_map:

            depth_map_terrain = depth_map.Results.Geometry.Terrain
            terrain_center_point = depth_map_terrain.Extent.CenterPointM()

            depth_map.Results.Geometry.CompleteForComputations()
            depth_map.Results.Geometry.XSInterpolationSurface().LoadIfNeeded()

            tile_cache_options = TileCacheOptions(terrain_center_point, depth_map)

            tile_cache_options.DatasetIdentifier = 'depth'
            tile_cache_options.MaxZoom = 12
            tile_cache_options.IsProfile = True
            tile_cache_options.StartProfile = depth_map.Results.ProfileNames[0]
            tile_cache_options.EndProfile = depth_map.Results.ProfileNames[-1]

            cache_computable = TileCacheComputable(tile_cache_options, depth_map)

        return cache_computable

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

    def _load_depth_map(self, plan_name):

        self._results_group = ResultsGroup()

        xml_node_1 = self._doc.SelectSingleNode('RASMapper')
        results_node = xml_node_1.SelectSingleNode(self._results_group.XMLNodeName)

        self._load_layers(self._results_group, results_node)

        depth_map = self._find_depth_map(plan_name, self._results_group)

        return depth_map

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

    def export_tile_cache(self, export_options=None):

        plan_name = 'FEQ forecast'

        depth_map = self._load_depth_map(plan_name)

        if depth_map:

            depth_map_terrain = depth_map.Results.Geometry.Terrain
            terrain_center_point = depth_map_terrain.Extent.CenterPointM()

            depth_map.Results.Geometry.CompleteForComputations()
            depth_map.Results.Geometry.XSInterpolationSurface().LoadIfNeeded()

            tile_cache_options = TileCacheOptions(terrain_center_point, depth_map)

            if os.path.isfile(tile_cache_options.Filename):
                os.remove(tile_cache_options.Filename)

            tile_cache_options.DatasetIdentifier = 'depth'
            tile_cache_options.MaxZoom = 12
            tile_cache_options.IsProfile = True
            tile_cache_options.StartProfile = depth_map.Results.ProfileNames[0]
            tile_cache_options.EndProfile = depth_map.Results.ProfileNames[-1]

            cache_computable = TileCacheComputable(tile_cache_options, depth_map)

            computer = TileCacheComputer()
            computer.Run(cache_computable)

    def load_rasmap_file(self, rasmap_file_path):

        self._doc.Load(rasmap_file_path)

        SharedData.RasMapFilename = rasmap_file_path

        xml_node_1 = self._doc.SelectSingleNode('RASMapper')
        self._set_projection_path(xml_node_1)
