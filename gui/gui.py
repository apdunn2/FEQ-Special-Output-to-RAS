import datetime
import os

import pandas as pd

from PyQt5.QtCore import pyqtSlot, QCoreApplication, Qt
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QFileDialog, QMainWindow, QMessageBox

from feq import FEQSpecialOutput
from feqtoras import FEQToRAS

from gui.ui_openspecoutputdlg import Ui_openSpecOutputDlg
from gui.ui_writeflowfilemainwindow import Ui_MainWindow


class OpenSpecOutputDlg(QDialog, Ui_openSpecOutputDlg):

    def __init__(self, node_table, pwd='.', parent=None):

        super().__init__(parent)
        self.setupUi(self)

        # remove the context help button
        window_flags = self.windowFlags()
        window_flags &= ~Qt.WindowContextHelpButtonHint
        self.setWindowFlags(Qt.WindowFlags(window_flags))

        self.buttonBox.button(QDialogButtonBox.Open).clicked.connect(self.on_buttonBox_open_clicked)

        self._pwd = pwd

        self._spec_output_path = None
        self._feq_special_output = None
        self._river_reach_dict = self._get_river_reach_dict(node_table)

        self.riverComboBox.addItems(self._river_reach_dict.keys())
        self._update_reach_names()

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

    def _update_reach_names(self):

        current_river = self.riverComboBox.currentText()
        self.reachComboBox.clear()
        self.reachComboBox.addItems(self._river_reach_dict[current_river])

    @pyqtSlot()
    def on_selectFileButton_clicked(self):

        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Special Output File to Load', self._pwd)

        if file_path:

            self._spec_output_path = file_path

            file_directory, file_name = os.path.split(file_path)
            self._pwd = file_directory
            self.fileLineDisplay.setText(file_name)

    def on_buttonBox_open_clicked(self):

        if self._spec_output_path:

            message_box = QMessageBox()
            message_box.setWindowTitle('Loading File')
            message_box.setText('Loading special output file...')
            message_box.setIcon(QMessageBox.Information)
            message_box.setStandardButtons(QMessageBox.NoButton)
            message_box.show()

            QCoreApplication.processEvents()

            river_name = self.riverComboBox.currentText()
            reach_name = self.reachComboBox.currentText()

            try:

                self._feq_special_output = FEQSpecialOutput.read_special_output_file(self._spec_output_path,
                                                                                     river_name,
                                                                                     reach_name)

                self.accept()

            except ValueError:

                error_message_box = QMessageBox()
                error_message_box.setWindowTitle('Error')
                error_message_box.setText('Unable to load special output file')
                error_message_box.setIcon(QMessageBox.Critical)
                error_message_box.setStandardButtons(QMessageBox.Ok)
                error_message_box.exec_()

            message_box.close()

        else:
            QMessageBox.critical(self, 'No File Selected', 'Select a special output file to open.')

    @pyqtSlot("int")
    def on_riverComboBox_currentIndexChanged(self, index):
        self._update_reach_names()

    def get_spec_output(self):

        return self._feq_special_output

    def get_spec_output_file_path(self):

        return self._spec_output_path


class WriteFlowFileMainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):

        super().__init__(parent)
        self.setupUi(self)
        self.timeStepComboBox.addItems(['6H', '3H', '1H'])
        self._pwd = '.'
        self._node_table = None
        self._node_table_path = None
        self._feq_spec_output = None

    def get_pwd(self):
        return self._pwd

    @staticmethod
    def _check_node_table_required_headers(node_table):
        required_headers = pd.Index(['Node', 'XS', 'River', 'Reach'])

        return required_headers.isin(node_table.keys()).all()

    @pyqtSlot()
    def on_addSpecOutputPushButton_clicked(self):

        form = OpenSpecOutputDlg(self._node_table, pwd=self._pwd)
        if form.exec_():

            if not self._feq_spec_output:
                self._feq_spec_output = form.get_spec_output()
            else:
                feq_spec_output = form.get_spec_output()
                self._feq_spec_output = self._feq_spec_output.add_special_output(feq_spec_output)

            file_path = form.get_spec_output_file_path()
            file_directory, file_name = os.path.split(file_path)
            self._pwd = file_directory

            # add the file name to the list and enable the flow file group
            self.specOutputListWidget.addItem(file_name)
            self.flowFileGroupBox.setEnabled(True)

            # get minimum and maximum possible times
            feq_data = self._feq_spec_output.get_data()
            minimum_date_time_index = feq_data.index[0]
            maximum_date_time_index = feq_data.index[-1]

            # set the min/max times
            self.startDateTimeEdit.setMinimumDateTime(minimum_date_time_index)
            self.startDateTimeEdit.setMaximumDateTime(maximum_date_time_index)
            self.endDateTimeEdit.setMinimumDateTime(minimum_date_time_index)
            self.endDateTimeEdit.setMaximumDateTime(maximum_date_time_index)

            # set the default start and end dates
            self.endDateTimeEdit.setDateTime(maximum_date_time_index)
            default_start_date_time = maximum_date_time_index - datetime.timedelta(days=3)
            self.startDateTimeEdit.setDateTime(default_start_date_time)

    @pyqtSlot()
    def on_clearSpecOutputPushButton_clicked(self):

        self._feq_spec_output = None
        self.specOutputListWidget.clear()
        self.flowFileGroupBox.setEnabled(False)

    @pyqtSlot()
    def on_loadNodeTablePushButton_clicked(self):

        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Node Table File', self._pwd, '*.csv')

        if file_path:

            node_table = pd.read_csv(file_path)

            if self._check_node_table_required_headers(node_table):

                if not node_table.keys().isin(['Elev Adj']).any():
                    QMessageBox.information(self, 'Header Not Found', 'The elevation adjustment '
                                                                      '(Elev Adj) header was not found')

                self._node_table = node_table
                self._node_table_path = file_path

                file_directory, file_name = os.path.split(file_path)
                self.nodeTableLineEdit.setText(file_name)

                self._pwd = file_directory

                self.addSpecOutputPushButton.setEnabled(True)
                self.clearSpecOutputPushButton.setEnabled(True)
                self.specOutputListWidget.setEnabled(True)

            else:

                QMessageBox.critical(self, 'Unable to Load File', 'The node table file is missing required headers.')

    @pyqtSlot()
    def on_saveFlowFilePushButton_clicked(self):

        start_date = self.startDateTimeEdit.dateTime().toPyDateTime()
        end_date = self.endDateTimeEdit.dateTime().toPyDateTime()

        default_file_name = start_date.strftime("%B %d, %Y, %H%M") + '.f01'
        default_file_path = os.path.join(self._pwd, default_file_name)

        save_file_path, _ = QFileDialog.getSaveFileName(self, "Save Flow File", default_file_path)

        if save_file_path:

            message_box = QMessageBox()
            message_box.setWindowTitle('Saving File')
            message_box.setText('Saving flow file...')
            message_box.setIcon(QMessageBox.Information)
            message_box.setStandardButtons(QMessageBox.NoButton)
            message_box.show()
            QCoreApplication.processEvents()

            time_step = self.timeStepComboBox.currentText()

            elevation_df = self._feq_spec_output.get_constituent('Elev', start_date=start_date,
                                                                 end_date=end_date,
                                                                 time_step=time_step)

            feq_to_ras_writer = FEQToRAS(self._node_table_path, elevation_df)
            feq_to_ras_writer.write_ras_flow_file(save_file_path)

            message_box.close()

            message_box = QMessageBox()
            message_box.setWindowTitle('Save File')
            message_box.setText('Done saving flow file.')
            message_box.setIcon(QMessageBox.Information)
            message_box.setStandardButtons(QMessageBox.Ok)
            message_box.exec_()

    def set_pwd(self, pwd):

        self._pwd = pwd
