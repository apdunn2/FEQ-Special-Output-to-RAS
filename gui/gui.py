import os

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QFileDialog

from feq import FEQSpecialOutput

from gui.ui_openspecoutputdlg import Ui_openSpecOutputDlg


class OpenSpecOutputDlg(QDialog, Ui_openSpecOutputDlg):

    def __init__(self, parent=None, pwd='.'):

        super(OpenSpecOutputDlg, self).__init__(parent)
        self.setupUi(self)
        self._pwd = pwd
        self._spec_output_path = None
        self._feq_special_output = None

    @pyqtSlot()
    def on_addButton_clicked(self):

        file_path = QFileDialog.getOpenFileName(self, 'Select special output file to load', self._pwd)

        if file_path:

            self._spec_output_path = file_path[0]

            file_directory, file_name = os.path.split(file_path[0])
            self._pwd = file_directory
            self.fileLineDisplay.setText(file_name)

    @pyqtSlot()
    def on_buttonBox_accepted(self):

        river_name = self.riverLineEdit.text()
        reach_name = self.reachLineEdit.text()

        while self._feq_special_output is None:
            self._feq_special_output = FEQSpecialOutput.read_special_output_file(self._spec_output_path,
                                                                                 river_name,
                                                                                 reach_name)

    def get_spec_output(self):

        return self._feq_special_output
