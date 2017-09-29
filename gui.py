import copy
import os

import pandas as pd
import yaml
from PyQt5.QtCore import pyqtSlot, Qt, QCoreApplication
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QFileDialog, QMainWindow, QMessageBox

import feqtoras
import ras
from ui_feqrasexportdlg import Ui_FEQRASExportDlg
from ui_feqrasmapper import Ui_FEQRASMapperMainWindow
from ui_openspecoutputdlg import Ui_openSpecOutputDlg


class FEQRASMapperMainWindow(QMainWindow, Ui_FEQRASMapperMainWindow):

    def __init__(self, parent=None):

        super().__init__(parent)
        self.setupUi(self)

        self._config = self._get_empty_config()

        self._setup_ui()

        self._cwd = os.path.expanduser('~/Documents')
        # self._cwd = '.'
        self._node_table = None
        self._node_table_path = None
        self._ras_mapper = None

    @staticmethod
    def _check_node_table_required_headers(node_table):
        required_headers = pd.Index(['Node', 'XS', 'River', 'Reach'])

        return required_headers.isin(node_table.keys()).all()

    def _check_export_ready(self):

        node_table_path_isfile = self._config['Node table'] is not None and os.path.isfile(self._config['Node table'])
        ras_path_isdir = self._config['RAS path'] is not None and os.path.isdir(self._config['RAS path'])
        special_output_isnotempty = len(self._config['Special output']) > 0
        number_of_days_isnotnone = self._config['Export time series']['Number of days'] is not None
        export_db_isnotnone = self._config['RasMapper']['Export database path'] is not None
        plan_name_isnotnone = self._config['RasMapper']['Plan name'] is not None
        rasmap_file_isfile = self._config['RasMapper']['RASMAP file path'] is not None \
                             and os.path.isfile(self._config['RasMapper']['RASMAP file path'])

        export_ready = node_table_path_isfile \
                       and ras_path_isdir \
                       and special_output_isnotempty \
                       and number_of_days_isnotnone \
                       and export_db_isnotnone \
                       and plan_name_isnotnone \
                       and rasmap_file_isfile

        return export_ready

    @staticmethod
    def _get_empty_config():

        empty_config = {'Node table': None,
                        'RAS path': None,
                        'Special output': {},
                        'Export time series': {'Number of days': None,
                                               'Time step': '1H'},
                        'RasMapper': {'Cache level': 12,
                                      'Export database path': None,
                                      'Plan name': None,
                                      'RASMAP file path': None}
                        }

        return empty_config

    def _setup_ui(self):

        self.timeStepComboBox.addItems(['1H', '3H', '6H'])
        self.cacheLevelComboBox.addItems(map(str, range(12, 19)))

        program_files_32_dir = os.environ['PROGRAMFILES(x86)']
        hec_folder = 'HEC'
        ras_folder = r'HEC-RAS\5.0.3'
        ras_dir = os.path.join(program_files_32_dir, hec_folder, ras_folder)
        if os.path.isdir(ras_dir):
            self._config['RAS path'] = ras_dir
            self.rasDirLineEdit.setText(ras_dir)

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

        # update the ras path info
        self.rasDirLineEdit.setText(self._config['RAS path'])
        if self._config['RAS path']:
            ras.set_ras_path(self._config['RAS path'])

        # update map export info
        self.rasmapFileLineEdit.setText(self._config['RasMapper']['RASMAP file path'])
        self.exportDBLineEdit.setText(self._config['RasMapper']['Export database path'])

        cache_level_index = self.cacheLevelComboBox.findText(str(self._config['RasMapper']['Cache level']))
        self.cacheLevelComboBox.setCurrentIndex(cache_level_index)

        self.planNameComboBox.clear()
        if self._config['RAS path'] and self._config['RasMapper']['RASMAP file path']:
            self.planNameLabel.setEnabled(True)
            self.planNameComboBox.setEnabled(True)
            self._ras_mapper = ras.RasMapper()
            self._ras_mapper.load_rasmap_file(self._config['RasMapper']['RASMAP file path'])
            plan_names = self._ras_mapper.get_plan_names()
            self.planNameComboBox.addItems(plan_names)
            if self._config['RasMapper']['Plan name']:
                plan_name_index = self.planNameComboBox.findText(self._config['RasMapper']['Plan name'])
                self.planNameComboBox.setCurrentIndex(plan_name_index)
            else:
                self._config['Rasmapper']['Plan name'] = self.planNameComboBox.currentText()
        else:
            self.planNameLabel.setEnabled(False)
            self.planNameComboBox.setEnabled(False)

        if self._check_export_ready():
            self.exportTilesPushButton.setEnabled(True)
        else:
            self.exportTilesPushButton.setEnabled(False)

    @pyqtSlot()
    def on_actionNew_triggered(self):
        self._config = self._get_empty_config()
        self._update_ui()

    @pyqtSlot()
    def on_actionSave_triggered(self):

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

            self._config['RasMapper']['Export database path'] = db_path

            db_dir, _ = os.path.split(db_path)

            self._update_ui()

    @pyqtSlot()
    def on_exportTilesPushButton_clicked(self):

        export_dialog = FEQRASExportDlg(self._config, self)
        export_dialog.exec_()

    @pyqtSlot()
    def on_nodeTablePushButton_clicked(self):

        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Node Table File', self._cwd, filter='*.csv')

        if file_path:

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

        self._config['RasMapper']['Plan name'] = self.planNameComboBox.itemText(index)

    @pyqtSlot()
    def on_rasDirPushButton_clicked(self):

        if self._config['RAS path']:
            ras_path = self._config['RAS path']
        else:
            ras_path = self._cwd

        new_ras_path = QFileDialog.getExistingDirectory(self, 'Select HEC-RAS install directory', ras_path)

        if new_ras_path:

            self._config['RAS path'] = new_ras_path

            # file_directory, _ = os.path.split(new_ras_path)

            # self._cwd = file_directory

            self._update_ui()

    @pyqtSlot()
    def on_rasmapFilePushButton_clicked(self):

        if self._config['RasMapper']['RASMAP file path']:
            rasmap_dir, _ = os.path.split(self._config['RasMapper']['RASMAP file path'])
        else:
            rasmap_dir = self._cwd

        rasmap_file_path, _ = QFileDialog.getOpenFileName(self, 'Select RASMAP file', rasmap_dir, filter='*.rasmap')

        if rasmap_file_path:

            self._config['RasMapper']['RASMAP file path'] = rasmap_file_path

            rasmap_dir, _ = os.path.split(rasmap_file_path)

            self._cwd = rasmap_dir

            self._update_ui()

    @pyqtSlot("int")
    def on_timeStepComboBox_currentIndexChanged(self, index):

        self._config['Export time series']['Time step'] = self.timeStepComboBox.itemText(index)


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


class FEQRASExportDlg(QDialog, Ui_FEQRASExportDlg):

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # remove the context help button
        window_flags = self.windowFlags()
        window_flags &= ~Qt.WindowContextHelpButtonHint
        self.setWindowFlags(Qt.WindowFlags(window_flags))

        self._compute_cancelled = False

        self._config = config

    def add_message(self, message):
        self.computeMessageTextEdit.append(message)
        QCoreApplication.processEvents()

    def closeEvent(self, event):
        event.ignore()

    def begin_export(self):

        feq_ras_mapper = feqtoras.FEQRASMapper(self._config)

        self.computeMessageTextEdit.append("Loading special output...")
        QCoreApplication.processEvents()
        feq_ras_mapper.load_special_output()

        self.computeMessageTextEdit.append("Writing FEQ time series to RAS results...")
        QCoreApplication.processEvents()
        feq_ras_mapper.write_feq_results_to_ras()

        self.computeMessageTextEdit.append("Exporting tiles...")
        QCoreApplication.processEvents()
        feq_ras_mapper.export_tile_cache()

        self.computeMessageTextEdit.append("Export complete")
        self.pushButton.setText('OK')
        self.pushButton.setEnabled(True)

    def on_pushButton_pressed(self):

        if self.pushButton.text() == 'Begin Export':
            self.pushButton.setText('Cancel')
            self.pushButton.setEnabled(False)
            self.begin_export()
        elif self.pushButton.text() == 'Cancel':
            pass
        elif self.pushButton.text() == 'OK':
            if self._compute_cancelled:
                self.reject()
            else:
                self.accept()
