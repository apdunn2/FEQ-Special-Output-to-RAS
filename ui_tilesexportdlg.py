# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tilesexportdlg.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_TilesExportDlg(object):
    def setupUi(self, TilesExportDlg):
        TilesExportDlg.setObjectName("TilesExportDlg")
        TilesExportDlg.setEnabled(True)
        TilesExportDlg.resize(401, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(TilesExportDlg)
        self.verticalLayout.setObjectName("verticalLayout")
        self.computeMessageTextEdit = QtWidgets.QTextEdit(TilesExportDlg)
        self.computeMessageTextEdit.setReadOnly(True)
        self.computeMessageTextEdit.setObjectName("computeMessageTextEdit")
        self.verticalLayout.addWidget(self.computeMessageTextEdit)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButton = QtWidgets.QPushButton(TilesExportDlg)
        self.pushButton.setEnabled(True)
        self.pushButton.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(TilesExportDlg)
        QtCore.QMetaObject.connectSlotsByName(TilesExportDlg)

    def retranslateUi(self, TilesExportDlg):
        _translate = QtCore.QCoreApplication.translate
        TilesExportDlg.setWindowTitle(_translate("TilesExportDlg", "Export Tiles"))
        self.pushButton.setText(_translate("TilesExportDlg", "Begin Export"))

