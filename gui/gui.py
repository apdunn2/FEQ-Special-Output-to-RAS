import os

from PyQt5.QtCore import pyqtSlot, QCoreApplication, Qt
from PyQt5.QtWidgets import QDialog, QFileDialog, QDialogButtonBox, QMessageBox

from feq import FEQSpecialOutput

from gui.ui_openspecoutputdlg import Ui_openSpecOutputDlg


class OpenSpecOutputDlg(QDialog, Ui_openSpecOutputDlg):

    def __init__(self, node_table, parent=None):

        super(OpenSpecOutputDlg, self).__init__(parent)
        self.setupUi(self)

        # remove the context help button
        window_flags = self.windowFlags()
        window_flags &= ~Qt.WindowContextHelpButtonHint
        self.setWindowFlags(Qt.WindowFlags(window_flags))

        self.buttonBox.button(QDialogButtonBox.Open).clicked.connect(self.on_buttonBox_open_clicked)

        if parent:
            self._pwd = parent.get_pwd()
        else:
            self._pwd = '.'
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

        file_path = QFileDialog.getOpenFileName(self, 'Select special output file to load', self._pwd)[0]

        if file_path:

            self._spec_output_path = file_path

            file_directory, file_name = os.path.split(file_path)
            self._pwd = file_directory
            self.fileLineDisplay.setText(file_name)

    def on_buttonBox_open_clicked(self):

        if self._spec_output_path:

            message_box = QMessageBox()
            message_box.setWindowTitle('Loading file')
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

            parent = self.parent()
            if parent:
                parent.set_pwd(self._pwd)

        else:
            QMessageBox.critical(self, 'No file selected', 'Select a special output file to open.')

    @pyqtSlot("int")
    def on_riverComboBox_currentIndexChanged(self, index):
        self._update_reach_names()

    def get_spec_output(self):

        return self._feq_special_output
