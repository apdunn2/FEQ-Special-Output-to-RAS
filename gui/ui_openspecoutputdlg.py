# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'openspecoutputdlg.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_openSpecOutputDlg(object):
    def setupUi(self, openSpecOutputDlg):
        openSpecOutputDlg.setObjectName("openSpecOutputDlg")
        openSpecOutputDlg.resize(387, 130)
        openSpecOutputDlg.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(openSpecOutputDlg)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.selectFileButton = QtWidgets.QPushButton(openSpecOutputDlg)
        self.selectFileButton.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.selectFileButton.setObjectName("selectFileButton")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.selectFileButton)
        self.fileLineDisplay = QtWidgets.QLineEdit(openSpecOutputDlg)
        self.fileLineDisplay.setReadOnly(True)
        self.fileLineDisplay.setObjectName("fileLineDisplay")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.fileLineDisplay)
        self.label = QtWidgets.QLabel(openSpecOutputDlg)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)
        self.label_2 = QtWidgets.QLabel(openSpecOutputDlg)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.riverComboBox = QtWidgets.QComboBox(openSpecOutputDlg)
        self.riverComboBox.setEnabled(True)
        self.riverComboBox.setObjectName("riverComboBox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.riverComboBox)
        self.reachComboBox = QtWidgets.QComboBox(openSpecOutputDlg)
        self.reachComboBox.setEnabled(True)
        self.reachComboBox.setObjectName("reachComboBox")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.reachComboBox)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(openSpecOutputDlg)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Open)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        spacerItem = QtWidgets.QSpacerItem(20, 1, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.label.setBuddy(self.riverComboBox)
        self.label_2.setBuddy(self.reachComboBox)

        self.retranslateUi(openSpecOutputDlg)
        self.buttonBox.rejected.connect(openSpecOutputDlg.reject)
        QtCore.QMetaObject.connectSlotsByName(openSpecOutputDlg)

    def retranslateUi(self, openSpecOutputDlg):
        _translate = QtCore.QCoreApplication.translate
        openSpecOutputDlg.setWindowTitle(_translate("openSpecOutputDlg", "Open Special Output File"))
        self.selectFileButton.setText(_translate("openSpecOutputDlg", "&Select File"))
        self.label.setText(_translate("openSpecOutputDlg", "R&iver Name"))
        self.label_2.setText(_translate("openSpecOutputDlg", "R&each Name"))

