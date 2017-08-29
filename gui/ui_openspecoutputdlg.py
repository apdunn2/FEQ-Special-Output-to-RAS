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
        self.addButton = QtWidgets.QPushButton(openSpecOutputDlg)
        self.addButton.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.addButton.setObjectName("addButton")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.addButton)
        self.fileLineDisplay = QtWidgets.QLineEdit(openSpecOutputDlg)
        self.fileLineDisplay.setReadOnly(True)
        self.fileLineDisplay.setObjectName("fileLineDisplay")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.fileLineDisplay)
        self.label = QtWidgets.QLabel(openSpecOutputDlg)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)
        self.riverLineEdit = QtWidgets.QLineEdit(openSpecOutputDlg)
        self.riverLineEdit.setObjectName("riverLineEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.riverLineEdit)
        self.label_2 = QtWidgets.QLabel(openSpecOutputDlg)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.reachLineEdit = QtWidgets.QLineEdit(openSpecOutputDlg)
        self.reachLineEdit.setObjectName("reachLineEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.reachLineEdit)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(openSpecOutputDlg)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        spacerItem = QtWidgets.QSpacerItem(20, 1, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.label.setBuddy(self.riverLineEdit)
        self.label_2.setBuddy(self.reachLineEdit)

        self.retranslateUi(openSpecOutputDlg)
        self.buttonBox.accepted.connect(openSpecOutputDlg.accept)
        self.buttonBox.rejected.connect(openSpecOutputDlg.reject)
        QtCore.QMetaObject.connectSlotsByName(openSpecOutputDlg)

    def retranslateUi(self, openSpecOutputDlg):
        _translate = QtCore.QCoreApplication.translate
        openSpecOutputDlg.setWindowTitle(_translate("openSpecOutputDlg", "Open Special Output File"))
        self.addButton.setText(_translate("openSpecOutputDlg", "&Select File"))
        self.label.setText(_translate("openSpecOutputDlg", "R&iver Name"))
        self.label_2.setText(_translate("openSpecOutputDlg", "R&each Name"))

