# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'feqrasmapper.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_FEQRASMapperMainWindow(object):
    def setupUi(self, FEQRASMapperMainWindow):
        FEQRASMapperMainWindow.setObjectName("FEQRASMapperMainWindow")
        FEQRASMapperMainWindow.resize(686, 312)
        self.centralwidget = QtWidgets.QWidget(FEQRASMapperMainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.formLayout_3 = QtWidgets.QFormLayout(self.centralwidget)
        self.formLayout_3.setObjectName("formLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.nodeTablePushButton = QtWidgets.QPushButton(self.centralwidget)
        self.nodeTablePushButton.setObjectName("nodeTablePushButton")
        self.horizontalLayout.addWidget(self.nodeTablePushButton)
        self.nodeTableLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.nodeTableLineEdit.setReadOnly(True)
        self.nodeTableLineEdit.setObjectName("nodeTableLineEdit")
        self.horizontalLayout.addWidget(self.nodeTableLineEdit)
        self.formLayout_3.setLayout(0, QtWidgets.QFormLayout.LabelRole, self.horizontalLayout)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.rasDirPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.rasDirPushButton.setObjectName("rasDirPushButton")
        self.horizontalLayout_3.addWidget(self.rasDirPushButton)
        self.rasDirLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.rasDirLineEdit.setReadOnly(True)
        self.rasDirLineEdit.setObjectName("rasDirLineEdit")
        self.horizontalLayout_3.addWidget(self.rasDirLineEdit)
        self.formLayout_3.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_3)
        self.feqSpecOutputGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.feqSpecOutputGroupBox.setEnabled(False)
        self.feqSpecOutputGroupBox.setObjectName("feqSpecOutputGroupBox")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.feqSpecOutputGroupBox)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.addSpecOutputPushButton = QtWidgets.QPushButton(self.feqSpecOutputGroupBox)
        self.addSpecOutputPushButton.setObjectName("addSpecOutputPushButton")
        self.verticalLayout.addWidget(self.addSpecOutputPushButton)
        self.editSpecOutputPushButton = QtWidgets.QPushButton(self.feqSpecOutputGroupBox)
        self.editSpecOutputPushButton.setObjectName("editSpecOutputPushButton")
        self.verticalLayout.addWidget(self.editSpecOutputPushButton)
        self.clearSpecOutputPushButton = QtWidgets.QPushButton(self.feqSpecOutputGroupBox)
        self.clearSpecOutputPushButton.setObjectName("clearSpecOutputPushButton")
        self.verticalLayout.addWidget(self.clearSpecOutputPushButton)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.specOutputListWidget = QtWidgets.QListWidget(self.feqSpecOutputGroupBox)
        self.specOutputListWidget.setObjectName("specOutputListWidget")
        self.horizontalLayout_2.addWidget(self.specOutputListWidget)
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.feqSpecOutputGroupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName("groupBox_2")
        self.formLayout_2 = QtWidgets.QFormLayout(self.groupBox_2)
        self.formLayout_2.setObjectName("formLayout_2")
        self.rasmapFilePushButton = QtWidgets.QPushButton(self.groupBox_2)
        self.rasmapFilePushButton.setObjectName("rasmapFilePushButton")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.rasmapFilePushButton)
        self.rasmapFileLineEdit = QtWidgets.QLineEdit(self.groupBox_2)
        self.rasmapFileLineEdit.setReadOnly(True)
        self.rasmapFileLineEdit.setObjectName("rasmapFileLineEdit")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.rasmapFileLineEdit)
        self.exportDBPushButton = QtWidgets.QPushButton(self.groupBox_2)
        self.exportDBPushButton.setObjectName("exportDBPushButton")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.exportDBPushButton)
        self.exportDBLineEdit = QtWidgets.QLineEdit(self.groupBox_2)
        self.exportDBLineEdit.setReadOnly(True)
        self.exportDBLineEdit.setObjectName("exportDBLineEdit")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.exportDBLineEdit)
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setObjectName("label_3")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.cacheLevelComboBox = QtWidgets.QComboBox(self.groupBox_2)
        self.cacheLevelComboBox.setObjectName("cacheLevelComboBox")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.cacheLevelComboBox)
        self.planNameLabel = QtWidgets.QLabel(self.groupBox_2)
        self.planNameLabel.setEnabled(False)
        self.planNameLabel.setObjectName("planNameLabel")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.planNameLabel)
        self.planNameComboBox = QtWidgets.QComboBox(self.groupBox_2)
        self.planNameComboBox.setEnabled(False)
        self.planNameComboBox.setObjectName("planNameComboBox")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.planNameComboBox)
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.groupBox_2)
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_3.setObjectName("groupBox_3")
        self.formLayout = QtWidgets.QFormLayout(self.groupBox_3)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(self.groupBox_3)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.numDaysLineEdit = QtWidgets.QLineEdit(self.groupBox_3)
        self.numDaysLineEdit.setObjectName("numDaysLineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.numDaysLineEdit)
        self.label_2 = QtWidgets.QLabel(self.groupBox_3)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.timeStepComboBox = QtWidgets.QComboBox(self.groupBox_3)
        self.timeStepComboBox.setObjectName("timeStepComboBox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.timeStepComboBox)
        self.formLayout_3.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.groupBox_3)
        self.exportTilesPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.exportTilesPushButton.setEnabled(False)
        self.exportTilesPushButton.setObjectName("exportTilesPushButton")
        self.formLayout_3.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.exportTilesPushButton)
        FEQRASMapperMainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(FEQRASMapperMainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 686, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        FEQRASMapperMainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(FEQRASMapperMainWindow)
        self.statusbar.setObjectName("statusbar")
        FEQRASMapperMainWindow.setStatusBar(self.statusbar)
        self.actionNew = QtWidgets.QAction(FEQRASMapperMainWindow)
        self.actionNew.setObjectName("actionNew")
        self.actionOpen = QtWidgets.QAction(FEQRASMapperMainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionSave = QtWidgets.QAction(FEQRASMapperMainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionSaveAs = QtWidgets.QAction(FEQRASMapperMainWindow)
        self.actionSaveAs.setObjectName("actionSaveAs")
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSaveAs)
        self.menubar.addAction(self.menuFile.menuAction())
        self.label_3.setBuddy(self.cacheLevelComboBox)
        self.label.setBuddy(self.numDaysLineEdit)
        self.label_2.setBuddy(self.timeStepComboBox)

        self.retranslateUi(FEQRASMapperMainWindow)
        QtCore.QMetaObject.connectSlotsByName(FEQRASMapperMainWindow)
        FEQRASMapperMainWindow.setTabOrder(self.nodeTablePushButton, self.nodeTableLineEdit)
        FEQRASMapperMainWindow.setTabOrder(self.nodeTableLineEdit, self.addSpecOutputPushButton)
        FEQRASMapperMainWindow.setTabOrder(self.addSpecOutputPushButton, self.editSpecOutputPushButton)
        FEQRASMapperMainWindow.setTabOrder(self.editSpecOutputPushButton, self.clearSpecOutputPushButton)
        FEQRASMapperMainWindow.setTabOrder(self.clearSpecOutputPushButton, self.specOutputListWidget)
        FEQRASMapperMainWindow.setTabOrder(self.specOutputListWidget, self.numDaysLineEdit)
        FEQRASMapperMainWindow.setTabOrder(self.numDaysLineEdit, self.timeStepComboBox)
        FEQRASMapperMainWindow.setTabOrder(self.timeStepComboBox, self.rasDirPushButton)
        FEQRASMapperMainWindow.setTabOrder(self.rasDirPushButton, self.rasDirLineEdit)
        FEQRASMapperMainWindow.setTabOrder(self.rasDirLineEdit, self.rasmapFilePushButton)
        FEQRASMapperMainWindow.setTabOrder(self.rasmapFilePushButton, self.rasmapFileLineEdit)
        FEQRASMapperMainWindow.setTabOrder(self.rasmapFileLineEdit, self.exportDBPushButton)
        FEQRASMapperMainWindow.setTabOrder(self.exportDBPushButton, self.exportDBLineEdit)
        FEQRASMapperMainWindow.setTabOrder(self.exportDBLineEdit, self.cacheLevelComboBox)
        FEQRASMapperMainWindow.setTabOrder(self.cacheLevelComboBox, self.exportTilesPushButton)

    def retranslateUi(self, FEQRASMapperMainWindow):
        _translate = QtCore.QCoreApplication.translate
        FEQRASMapperMainWindow.setWindowTitle(_translate("FEQRASMapperMainWindow", "FEQ RAS mapper"))
        self.nodeTablePushButton.setText(_translate("FEQRASMapperMainWindow", "Node Table"))
        self.rasDirPushButton.setText(_translate("FEQRASMapperMainWindow", "RAS Directory"))
        self.feqSpecOutputGroupBox.setTitle(_translate("FEQRASMapperMainWindow", "FEQ Special Output"))
        self.addSpecOutputPushButton.setText(_translate("FEQRASMapperMainWindow", "Add"))
        self.editSpecOutputPushButton.setText(_translate("FEQRASMapperMainWindow", "Edit"))
        self.clearSpecOutputPushButton.setText(_translate("FEQRASMapperMainWindow", "Clear All"))
        self.groupBox_2.setTitle(_translate("FEQRASMapperMainWindow", "Map Export"))
        self.rasmapFilePushButton.setText(_translate("FEQRASMapperMainWindow", "RASMAP file"))
        self.exportDBPushButton.setText(_translate("FEQRASMapperMainWindow", "Export Database File"))
        self.label_3.setText(_translate("FEQRASMapperMainWindow", "Cache Level"))
        self.planNameLabel.setText(_translate("FEQRASMapperMainWindow", "Plan Name"))
        self.groupBox_3.setTitle(_translate("FEQRASMapperMainWindow", "Export Time Series"))
        self.label.setText(_translate("FEQRASMapperMainWindow", "Number of Days"))
        self.label_2.setText(_translate("FEQRASMapperMainWindow", "Time Step"))
        self.exportTilesPushButton.setText(_translate("FEQRASMapperMainWindow", "Export Tiles for Web Viewing"))
        self.menuFile.setTitle(_translate("FEQRASMapperMainWindow", "File"))
        self.actionNew.setText(_translate("FEQRASMapperMainWindow", "New"))
        self.actionOpen.setText(_translate("FEQRASMapperMainWindow", "Open"))
        self.actionSave.setText(_translate("FEQRASMapperMainWindow", "Save"))
        self.actionSaveAs.setText(_translate("FEQRASMapperMainWindow", "Save As"))

