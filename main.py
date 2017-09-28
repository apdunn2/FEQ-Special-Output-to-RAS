import sys

from PyQt5.QtWidgets import QApplication

# from gui.gui import WriteFlowFileMainWindow
from gui.feqrasmapper import FEQRASMapperMainWindow

if __name__ == "__main__":

    app = QApplication(sys.argv)
    main_window = FEQRASMapperMainWindow()
    main_window.show()
    sys.exit(app.exec_())
