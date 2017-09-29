# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'feqrasexportdlg.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_FEQRASExportDlg(object):
    def setupUi(self, FEQRASExportDlg):
        FEQRASExportDlg.setObjectName("FEQRASExportDlg")
        FEQRASExportDlg.setEnabled(True)
        FEQRASExportDlg.resize(401, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(FEQRASExportDlg)
        self.verticalLayout.setObjectName("verticalLayout")
        self.computeMessageTextEdit = QtWidgets.QTextEdit(FEQRASExportDlg)
        self.computeMessageTextEdit.setReadOnly(True)
        self.computeMessageTextEdit.setObjectName("computeMessageTextEdit")
        self.verticalLayout.addWidget(self.computeMessageTextEdit)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButton = QtWidgets.QPushButton(FEQRASExportDlg)
        self.pushButton.setEnabled(True)
        self.pushButton.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(FEQRASExportDlg)
        QtCore.QMetaObject.connectSlotsByName(FEQRASExportDlg)

    def retranslateUi(self, FEQRASExportDlg):
        _translate = QtCore.QCoreApplication.translate
        FEQRASExportDlg.setWindowTitle(_translate("FEQRASExportDlg", "Export Tiles"))
        self.pushButton.setText(_translate("FEQRASExportDlg", "Begin Export"))

