import copy
import os
import time

import pandas as pd
import yaml

from PyQt5.QtCore import pyqtSlot, Qt, QCoreApplication
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QFileDialog, QMainWindow, QMessageBox

import feq
import feqtoras
import ras
from ui_computedlg import Ui_Compute
from ui_feqrasmapper import Ui_FEQRASMapperMainWindow
from ui_openspecoutputdlg import Ui_openSpecOutputDlg
from ui_rasresultsviewdialog import Ui_RASResultsViewDialog
from ui_tilesexportdlg import Ui_TilesExportDlg


class ComputeDlg(QDialog, Ui_Compute):

    def __init__(self, computable_object, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._compute_cancelled = False

        self._computable_object = computable_object
        self._computable_object.set_message_client(self)

        if not self._computable_object.is_cancellable:
            self.pushButton.setEnabled(False)

        self.start_compute()

    def add_message(self, message):

        self.textBrowser.append(message)

    @pyqtSlot()
    def on_pushButton_pressed(self):

        if self.pushButton.text() == 'Cancel':
            self._compute_cancelled = True
            self._computable_object.cancel()
            self.pushButton.setText('OK')
        elif self.pushButton.text() == 'OK':
            if self._compute_cancelled:
                self.reject()
            else:
                self.accept()

    def start_compute(self):

        # compute_thread = Thread(target=self._computable_object.start_compute)
        # compute_thread.start()
        self._computable_object.start_compute()

        while not self._computable_object.compute_complete():
            QCoreApplication.processEvents()
            time.sleep(0.1)

        self.pushButton.setEnabled(True)
        self.pushButton.setText('OK')


class DummyRASMessageClient:

    def __init__(self, ras_controller, number_of_tabs=0):

        ras_controller.set_message_client(self)
        self._number_of_tabs = number_of_tabs

    def update_progress(self, progress):
        print('\t'*self._number_of_tabs + progress)

    def add_message(self, event_message):
        print('\t'*self._number_of_tabs + event_message)

    def compute_complete(self):
        print('\t'*self._number_of_tabs + 'Compute complete!')


class FEQRASExportDlg(QDialog, Ui_TilesExportDlg):

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # remove the context help button
        window_flags = self.windowFlags()
        window_flags &= ~Qt.WindowContextHelpButtonHint
        self.setWindowFlags(Qt.WindowFlags(window_flags))

        self._compute_cancelled = False
        self._compute_started = False

        self._config = config

    def add_message(self, message):
        self.computeMessageTextEdit.append(message)
        QCoreApplication.processEvents()

    def closeEvent(self, event):
        if self._compute_started:
            event.ignore()
        else:
            super().closeEvent(event)

    def begin_export(self):

        ras_mapper = ras.RasMapper()
        ras_mapper.load_rasmap_file(self._config['RasMapper']['RASMAP file path'])

        export_options = ras_mapper.get_export_options()
        export_options.file_name = self._config['RasMapper']['Export database path']
        export_options.plan_name = self._config['Plan name']
        export_options.max_zoom = self._config['RasMapper']['Cache level']

        self.computeMessageTextEdit.append("Exporting tiles...")
        QCoreApplication.processEvents()
        ras_mapper.export_tile_cache(export_options)

        QCoreApplication.processEvents()
        self.computeMessageTextEdit.append("Export complete")
        self.pushButton.setText('OK')
        self.pushButton.setEnabled(True)

    @pyqtSlot()
    def on_pushButton_pressed(self):

        if self.pushButton.text() == 'Begin Export':
            self.pushButton.setText('Cancel')
            self.pushButton.setEnabled(False)
            self._compute_started = True
            self.begin_export()
        elif self.pushButton.text() == 'Cancel':
            pass
        elif self.pushButton.text() == 'OK':
            if self._compute_cancelled:
                self.reject()
            else:
                self.accept()


class FEQRASMapperMainWindow(QMainWindow, Ui_FEQRASMapperMainWindow):

    def __init__(self, parent=None):

        super().__init__(parent)
        self.setupUi(self)

        self._config = self._get_empty_config()

        self._ras_controller = ras.ras_controller

        self._setup_ui()

        self._cwd = os.path.expanduser('~/Documents')
        self._last_config_file_path = None
        self._node_table = None
        self._node_table_path = None

    @staticmethod
    def _check_node_table_required_headers(node_table):
        required_headers = pd.Index(['Node', 'XS', 'River', 'Reach'])

        return required_headers.isin(node_table.keys()).all()

    def _check_export_ready(self):

        export_db_isnotnone = self._config['RasMapper']['Export database path'] is not None
        plan_name_isnotnone = self._config['Plan name'] is not None
        rasmap_file_isfile = self._config['RasMapper']['RASMAP file path'] is not None \
                             and os.path.isfile(self._config['RasMapper']['RASMAP file path'])

        export_ready = export_db_isnotnone \
                       and plan_name_isnotnone \
                       and rasmap_file_isfile

        return export_ready

    def _check_update_results_ready(self):

        ras_path_isdir = self._config['RAS path'] is not None and os.path.isdir(self._config['RAS path'])
        ras_project_isopen = self._config['RAS project file'] == self._ras_controller.Project_Current()
        special_output_isnotempty = len(self._config['Special output']) > 0
        number_of_days_isnotnone = self._config['Export time series']['Number of days'] is not None

        update_results_ready = ras_path_isdir \
                               and ras_project_isopen \
                               and special_output_isnotempty \
                               and number_of_days_isnotnone

        return update_results_ready

    @staticmethod
    def _get_empty_config():

        program_files_32_dir = os.environ['PROGRAMFILES(x86)']
        hec_folder = 'HEC'
        ras_folder = r'HEC-RAS\5.0.3'
        ras_dir = os.path.join(program_files_32_dir, hec_folder, ras_folder)
        if not os.path.isdir(ras_dir):
            ras_dir = None

        empty_config = {'Node table': None,
                        'RAS path': ras_dir,
                        'Special output': {},
                        'Export time series': {'Number of days': None,
                                               'Time step': '1H'},
                        'RAS project file': None,
                        'Plan name': None,
                        'RasMapper': {'Cache level': 12,
                                      'Export database path': None,
                                      'RASMAP file path': None}
                        }

        return empty_config

    def _setup_ui(self):

        self.timeStepComboBox.addItems(['1H', '3H', '6H'])
        self.cacheLevelComboBox.addItems(map(str, range(12, 19)))

        self._update_ui()

    def _update_spec_output(self, reach_config):

        self._config['Special output'].update(reach_config)

        reach_name = list(reach_config.keys())[0]
        file_directory, _ = os.path.split(reach_config[reach_name]['File location'])
        self._cwd = file_directory

        self._update_ui()

    def _update_ui(self):

        # update the node table.
        if self._config['Node table']:
            self._node_table = pd.read_csv(self._config['Node table'])
            _, node_table_name = os.path.split(self._config['Node table'])
            self.nodeTableLineEdit.setText(node_table_name)
            self.feqSpecOutputGroupBox.setEnabled(True)
        else:
            self._node_table = None
            self.nodeTableLineEdit.setText(None)
            self.feqSpecOutputGroupBox.setEnabled(False)

        # update special output info
        self.specOutputListWidget.clear()
        if len(self._config['Special output']) > 0:
            for reach_name in self._config['Special output'].keys():
                self.specOutputListWidget.addItem(reach_name)

        # update time series info
        if self._config['Export time series']['Number of days']:
            self.numDaysLineEdit.setText('{:g}'.format(self._config['Export time series']['Number of days']))
        else:
            self.numDaysLineEdit.setText(None)

        time_step_index = self.timeStepComboBox.findText(self._config['Export time series']['Time step'])
        self.timeStepComboBox.setCurrentIndex(time_step_index)

        ras.set_ras_version('5.0.3')

        # update the ras path info
        self.rasDirLineEdit.setText(self._config['RAS path'])
        if self._config['RAS path']:
            ras_path = os.path.join(self._config['RAS path'])
            ras.set_ras_path(ras_path)

        # update map export info
        rasmap_file = self._config['RasMapper']['RASMAP file path']
        self.rasmapFileLineEdit.setText(rasmap_file)
        db_file = self._config['RasMapper']['Export database path']
        self.exportDBLineEdit.setText(db_file)

        # update plan name info
        self.planNameComboBox.clear()
        if self._config['RAS project file']:

            self.rasProjectLineEdit.setText(self._config['RAS project file'])

            self.planNameComboBox.setEnabled(True)
            self.planNameLabel.setEnabled(True)
            self._ras_controller.Project_Open(self._config['RAS project file'])
            plan_counts, plan_names, _ = self._ras_controller.Plan_Names(None, None, False)
            self.planNameComboBox.addItems(plan_names)
            if self._config['Plan name']:
                plan_name_index = self.planNameComboBox.findText(self._config['Plan name'])
                self.planNameComboBox.setCurrentIndex(plan_name_index)
            else:
                self._config['Plan name'] = self.planNameComboBox.currentText()
            self._ras_controller.Plan_SetCurrent(self._config['Plan name'])
        else:
            self.planNameLabel.setEnabled(False)
            self.planNameComboBox.setEnabled(False)
            self.rasProjectLineEdit.clear()

        if self._check_update_results_ready():
            self.updateResultsPushButton.setEnabled(True)
        else:
            self.updateResultsPushButton.setEnabled(False)

        if self._config['RAS project file'] == self._ras_controller.Project_Current():
            self.viewResultsPushButton.setEnabled(True)
        else:
            self.viewResultsPushButton.setEnabled(False)

        # cache level
        cache_level_index = self.cacheLevelComboBox.findText(str(self._config['RasMapper']['Cache level']))
        self.cacheLevelComboBox.setCurrentIndex(cache_level_index)

        if self._check_export_ready():
            self.exportTilesPushButton.setEnabled(True)
        else:
            self.exportTilesPushButton.setEnabled(False)

    @pyqtSlot()
    def on_actionNew_triggered(self):
        self._last_config_file_path = None
        self._config = self._get_empty_config()
        self._update_ui()

    @pyqtSlot()
    def on_actionSave_triggered(self):

        if self._last_config_file_path:

            with open(self._last_config_file_path, 'w') as f:
                yaml.dump(self._config, f, default_flow_style=False)

        else:
            config_file_path, _ = QFileDialog.getSaveFileName(self, 'Save configuration', self._cwd, '*.yaml')

            if config_file_path:
                with open(config_file_path, 'w') as f:
                    yaml.dump(self._config, f, default_flow_style=False)

                config_file_dir, _ = os.path.split(config_file_path)
                self._last_config_file_path = config_file_path

                self._cwd = config_file_dir

    @pyqtSlot()
    def on_actionSaveAs_triggered(self):

        config_file_path, _ = QFileDialog.getSaveFileName(self, 'Save configuration', self._cwd, '*.yaml')

        if config_file_path:

            with open(config_file_path, 'w') as f:
                yaml.dump(self._config, f, default_flow_style=False)

            config_file_dir, _ = os.path.split(config_file_path)

            self._cwd = config_file_dir

    @pyqtSlot()
    def on_actionOpen_triggered(self):

        config_file_path, _ = QFileDialog.getOpenFileName(self, 'Open configuration', self._cwd, '*.yaml')

        if config_file_path:

            with open(config_file_path, 'r') as f:
                new_config = yaml.load(f)

            old_config = self._config
            self._config = new_config

            config_file_dir, _ = os.path.split(config_file_path)
            self._cwd = config_file_dir

            self._last_config_file_path = config_file_path

            try:
                self._update_ui()
            except Exception:
                QMessageBox.critical(self, 'Unable to load', 'Unable to load configuration')
                self._config = old_config
                self._update_ui()

    @pyqtSlot()
    def on_addSpecOutputPushButton_clicked(self):

        form = OpenSpecOutputDlg(self._node_table, cwd=self._cwd)
        if form.exec_():

            reach_config = form.get_reach_config()

            self._update_spec_output(reach_config)

    @pyqtSlot("int")
    def on_cacheLevelComboBox_currentIndexChanged(self, index):

        self._config['RasMapper']['Cache level'] = int(self.cacheLevelComboBox.itemText(index))

    @pyqtSlot()
    def on_clearSpecOutputPushButton_clicked(self):

        self._config['Special output'] = {}
        self._update_ui()

    @pyqtSlot()
    def on_editSpecOutputPushButton_clicked(self):

        current_item = self.specOutputListWidget.currentItem()

        if current_item:

            selected_reach = current_item.text()

            config_info = self._config['Special output'][selected_reach]

            reach_config = {selected_reach: config_info}

            form = OpenSpecOutputDlg(self._node_table, reach_config, self._cwd)

            if form.exec_():

                reach_config = form.get_reach_config()

                self._update_spec_output(reach_config)

    @pyqtSlot()
    def on_exportDBPushButton_clicked(self):

        if self._config['RasMapper']['Export database path']:
            db_dir, _ = os.path.split(self._config['RasMapper']['Export database path'])
        else:
            db_dir = self._cwd

        db_path, _ = QFileDialog.getSaveFileName(self, 'Select export database save location', db_dir, "*.db")

        if db_path:

            db_path = db_path.replace('/', '\\')

            self._config['RasMapper']['Export database path'] = db_path

            db_dir, _ = os.path.split(db_path)

            self._cwd = db_dir

            self._update_ui()

    @pyqtSlot()
    def on_exportTilesPushButton_clicked(self):

        export_dialog = FEQRASExportDlg(self._config, self)
        export_dialog.exec_()

    @pyqtSlot()
    def on_nodeTablePushButton_clicked(self):

        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Node Table File', self._cwd, filter='*.csv')

        if file_path:

            file_path = file_path.replace('/', '\\')

            node_table = pd.read_csv(file_path)

            if self._check_node_table_required_headers(node_table):

                if not node_table.keys().isin(['Elev Adj']).any():
                    QMessageBox.information(self, 'Header Not Found', 'The elevation adjustment '
                                                                      '(Elev Adj) header was not found')

                self._node_table = node_table
                self._config['Node table'] = file_path

                file_directory, _ = os.path.split(file_path)

                self._cwd = file_directory

                self._update_ui()

            else:

                QMessageBox.critical(self, 'Unable to Load File', 'The node table file is missing required headers.')

    @pyqtSlot()
    def on_numDaysLineEdit_editingFinished(self):

        if len(self.numDaysLineEdit.text()) == 0:
            self._config['Export time series']['Number of days'] = None
        else:
            try:
                number_of_days = float(self.numDaysLineEdit.text())
                self._config['Export time series']['Number of days'] = number_of_days
            except ValueError:
                pass

        self._update_ui()

    @pyqtSlot("int")
    def on_planNameComboBox_currentIndexChanged(self, index):

        self._config['Plan name'] = self.planNameComboBox.itemText(index)

    @pyqtSlot()
    def on_rasDirPushButton_clicked(self):

        if self._config['RAS path']:
            ras_path = self._config['RAS path']
        else:
            ras_path = self._cwd

        new_ras_path = QFileDialog.getExistingDirectory(self, 'Select HEC-RAS install directory', ras_path)

        if new_ras_path:

            self._config['RAS path'] = os.path.join(new_ras_path)

            self._update_ui()

    @pyqtSlot()
    def on_rasProjectPushButton_clicked(self):

        ras_project_file, _ = QFileDialog.getOpenFileName(self, 'Select HEC-RAS project file', self._cwd, '*.prj')

        if ras_project_file:

            ras_project_file = ras_project_file.replace('/', '\\')

            self._config['RAS project file'] = ras_project_file

            self._cwd, _ = os.path.split(ras_project_file)

            self._update_ui()

    @pyqtSlot()
    def on_rasmapFilePushButton_clicked(self):

        if self._config['RasMapper']['RASMAP file path']:
            rasmap_dir, _ = os.path.split(self._config['RasMapper']['RASMAP file path'])
        else:
            rasmap_dir = self._cwd

        rasmap_file_path, _ = QFileDialog.getOpenFileName(self, 'Select RASMAP file', rasmap_dir, filter='*.rasmap')

        if rasmap_file_path:

            rasmap_file_path = rasmap_file_path.replace('/', '\\')

            self._config['RasMapper']['RASMAP file path'] = rasmap_file_path.replace('/', '\\')

            rasmap_dir, _ = os.path.split(rasmap_file_path)

            self._cwd = rasmap_dir

            self._update_ui()

    @pyqtSlot("int")
    def on_timeStepComboBox_currentIndexChanged(self, index):

        self._config['Export time series']['Time step'] = self.timeStepComboBox.itemText(index)

    @pyqtSlot()
    def on_updateResultsPushButton_clicked(self):

        print("Loading special output...")

        special_output = []

        for reach, reach_config in self._config['Special output'].items():
            river = reach_config['River']
            spec_output_path = reach_config['File location']
            print("\tSpecial output file: " + spec_output_path)
            special_output.append(feq.SpecialOutput.read_special_output_file(spec_output_path, river, reach))

        feq_special_output = special_output[0]

        for spec_out in special_output[1:]:
            feq_special_output = feq_special_output.add_special_output(spec_out)

        print("Converting FEQ nodes to RAS cross sections...")

        node_file_path = self._config['Node table']
        feq_to_raser = feqtoras.FEQToRAS(node_file_path, feq_special_output)

        time_step = self._config['Export time series']['Time step']
        number_of_days = self._config['Export time series']['Number of days']

        print("Creating interpolated time series...")

        ras_time_series = feq_to_raser.get_ras_time_series()
        ras_data = ras_time_series.get_data(number_of_days=number_of_days, time_step=time_step)

        print("Writing steady flow file...")

        ras_steady_flow_file = ras.SteadyFlowFile(ras_data, self._config['Plan name'])

        flow_file_name = self._ras_controller.CurrentSteadyFile()
        ras_steady_flow_file.write_flow_file(flow_file_name)

        print("Running RAS...")

        self._ras_controller.Project_Open(self._config['RAS project file'])
        message_client = DummyRASMessageClient(self._ras_controller, 5)

        self._ras_controller.Compute_HideComputationWindow()
        compute_success, nmsg, ras_messages, blocking_mode = self._ras_controller.Compute_CurrentPlan(None, None, True)
        if not compute_success:
            print("RAS computed failed!")
        else:
            print("RAS compute succeeded!")

        print("RAS messages:")
        for message in ras_messages:
            print("\t" + message)

    @pyqtSlot()
    def on_viewResultsPushButton_clicked(self):
        view_results_dialog = RasResultsViewDialog(self._ras_controller, self)
        view_results_dialog.exec_()


class OpenSpecOutputDlg(QDialog, Ui_openSpecOutputDlg):

    def __init__(self, node_table, reach_config=None, cwd=None, parent=None):

        super().__init__(parent)
        self.setupUi(self)

        # remove the context help button
        window_flags = self.windowFlags()
        window_flags &= ~Qt.WindowContextHelpButtonHint
        self.setWindowFlags(Qt.WindowFlags(window_flags))

        self.buttonBox.button(QDialogButtonBox.Open).clicked.connect(self.on_buttonBox_open_clicked)

        self._spec_output_path = None

        self._river_reach_dict = self._get_river_reach_dict(node_table)

        self.riverComboBox.addItems(self._river_reach_dict.keys())
        self._update_reach_names()

        if cwd:
            self._cwd = cwd
        else:
            self._cwd = '.'

        if reach_config:
            self._load_config(reach_config)
            self._reach_config = copy.deepcopy(reach_config)
        else:
            self._reach_config = {}

    @staticmethod
    def _get_river_reach_dict(node_table):

        river_reach_dict = {}
        unique_rivers = node_table['River'].unique()

        for river in unique_rivers:
            river_rows = node_table['River'] == river
            reaches_in_river = node_table.loc[river_rows, 'Reach']
            unique_reaches = list(reaches_in_river.unique())
            river_reach_dict[river] = unique_reaches

        return river_reach_dict

    def _load_config(self, config):

        reach_name = list(config.keys())[0]
        reach_index = self.reachComboBox.findText(reach_name)
        self.reachComboBox.setCurrentIndex(reach_index)

        file_location = config[reach_name]['File location']
        _, file_name = os.path.split(file_location)
        self.fileLineDisplay.setText(file_name)
        self._spec_output_path = file_location

        river_name = config[reach_name]['River']
        river_index = self.riverComboBox.findText(river_name)
        self.riverComboBox.setCurrentIndex(river_index)

    def _update_reach_names(self):

        current_river = self.riverComboBox.currentText()
        self.reachComboBox.clear()
        self.reachComboBox.addItems(self._river_reach_dict[current_river])

    @pyqtSlot()
    def on_selectFileButton_clicked(self):

        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Special Output File to Load', self._cwd)

        if file_path:

            self._spec_output_path = file_path

            file_directory, file_name = os.path.split(file_path)
            self._cwd = file_directory
            self.fileLineDisplay.setText(file_name)

    def on_buttonBox_open_clicked(self):

        if self._spec_output_path:

            river_name = self.riverComboBox.currentText()
            reach_name = self.reachComboBox.currentText()

            self._reach_config[reach_name] = {'File location': self._spec_output_path, 'River': river_name}

            self.accept()

        else:
            QMessageBox.critical(self, 'No File Selected', 'Select a special output file to open.')

    @pyqtSlot("int")
    def on_riverComboBox_currentIndexChanged(self, index):
        self._update_reach_names()

    def get_reach_config(self):

        return self._reach_config


class RasResultsViewDialog(QDialog, Ui_RASResultsViewDialog):

    def __init__(self, ras_controller, parent=None):

        super().__init__(parent)
        self.setupUi(self)

        # remove the context help button
        window_flags = self.windowFlags()
        window_flags &= ~Qt.WindowContextHelpButtonHint
        self.setWindowFlags(Qt.WindowFlags(window_flags))

        self._ras_controller = ras_controller

        self._setup_ui()

    def _setup_ui(self):

        _, river_names = self._ras_controller.Geometry_GetRivers(None, None)
        self.riverComboBox.addItems(river_names)

        self._update_reaches(1)
        self._update_river_stations(1, 1)

    def _update_reaches(self, river_number):
        self.reachComboBox.clear()
        _, _, reach_names = self._ras_controller.Geometry_GetReaches(river_number, None, None)
        self.reachComboBox.addItems(reach_names)

    def _update_river_stations(self, river_number, reach_number):
        self.riverStationComboBox.clear()
        _, _, _, cross_sections, _ = self._ras_controller.Geometry_GetNodes(river_number, reach_number,
                                                                            None, None, None)
        try:
            self.riverStationComboBox.addItems(cross_sections)
        except TypeError:
            pass

    @pyqtSlot("int")
    def on_reachComboBox_currentIndexChanged(self, index):
        river_number = self.riverComboBox.currentIndex() + 1
        self._update_river_stations(river_number, index + 1)

    @pyqtSlot("int")
    def on_riverComboBox_currentIndexChanged(self, index):
        self._update_reaches(index+1)
        self._update_river_stations(index+1, 1)

    @pyqtSlot()
    def on_openRASMapperPushButton_clicked(self):
        self._ras_controller.ShowRasMapper()

    @pyqtSlot()
    def on_openRASPushButton_clicked(self):
        self._ras_controller.ShowRas()

    @pyqtSlot()
    def on_viewCrossSectionPushButton_clicked(self):

        river_name = self.riverComboBox.currentText()
        reach_name = self.reachComboBox.currentText()
        river_station = self.riverStationComboBox.currentText()

        self._ras_controller.PlotXS(river_name, reach_name, river_station)

    @pyqtSlot()
    def on_viewProfilePushButton_clicked(self):

        river_name = self.riverComboBox.currentText()
        reach_name = self.reachComboBox.currentText()

        self._ras_controller.PlotPF(river_name, reach_name)
