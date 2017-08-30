import pdb
import sys

from PyQt5.QtWidgets import QApplication

from gui.gui import WriteFlowFileMainWindow

if __name__ == "__main__":

    app = QApplication(sys.argv)
    main_window = WriteFlowFileMainWindow()
    main_window.show()
    sys.exit(app.exec_())
