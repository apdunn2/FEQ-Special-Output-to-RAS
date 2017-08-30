import sys

from PyQt5.QtWidgets import QApplication

from gui.gui import WriteFlowFileMainWindow

app = QApplication(sys.argv)
main_window = WriteFlowFileMainWindow()
main_window.show()
app.exec_()
