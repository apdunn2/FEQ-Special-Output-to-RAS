# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'rasresultsviewdialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_RASResultsViewDialog(object):
    def setupUi(self, RASResultsViewDialog):
        RASResultsViewDialog.setObjectName("RASResultsViewDialog")
        RASResultsViewDialog.resize(386, 157)
        self.gridLayout = QtWidgets.QGridLayout(RASResultsViewDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label = QtWidgets.QLabel(RASResultsViewDialog)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.riverComboBox = QtWidgets.QComboBox(RASResultsViewDialog)
        self.riverComboBox.setObjectName("riverComboBox")
        self.horizontalLayout_3.addWidget(self.riverComboBox)
        self.gridLayout.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.viewProfilePushButton = QtWidgets.QPushButton(RASResultsViewDialog)
        self.viewProfilePushButton.setObjectName("viewProfilePushButton")
        self.verticalLayout.addWidget(self.viewProfilePushButton)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.viewCrossSectionPushButton = QtWidgets.QPushButton(RASResultsViewDialog)
        self.viewCrossSectionPushButton.setObjectName("viewCrossSectionPushButton")
        self.verticalLayout.addWidget(self.viewCrossSectionPushButton)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.gridLayout.addLayout(self.verticalLayout, 0, 1, 4, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(RASResultsViewDialog)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.reachComboBox = QtWidgets.QComboBox(RASResultsViewDialog)
        self.reachComboBox.setObjectName("reachComboBox")
        self.horizontalLayout_2.addWidget(self.reachComboBox)
        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_3 = QtWidgets.QLabel(RASResultsViewDialog)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.riverStationComboBox = QtWidgets.QComboBox(RASResultsViewDialog)
        self.riverStationComboBox.setObjectName("riverStationComboBox")
        self.horizontalLayout.addWidget(self.riverStationComboBox)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 1)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem3)
        self.openRASPushButton = QtWidgets.QPushButton(RASResultsViewDialog)
        self.openRASPushButton.setObjectName("openRASPushButton")
        self.horizontalLayout_4.addWidget(self.openRASPushButton)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem4)
        self.openRASMapperPushButton = QtWidgets.QPushButton(RASResultsViewDialog)
        self.openRASMapperPushButton.setObjectName("openRASMapperPushButton")
        self.horizontalLayout_4.addWidget(self.openRASMapperPushButton)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem5)
        self.gridLayout.addLayout(self.horizontalLayout_4, 3, 0, 1, 1)

        self.retranslateUi(RASResultsViewDialog)
        QtCore.QMetaObject.connectSlotsByName(RASResultsViewDialog)

    def retranslateUi(self, RASResultsViewDialog):
        _translate = QtCore.QCoreApplication.translate
        RASResultsViewDialog.setWindowTitle(_translate("RASResultsViewDialog", "View RAS Results"))
        self.label.setText(_translate("RASResultsViewDialog", "River"))
        self.viewProfilePushButton.setText(_translate("RASResultsViewDialog", "View Profile"))
        self.viewCrossSectionPushButton.setText(_translate("RASResultsViewDialog", "View Cross Section"))
        self.label_2.setText(_translate("RASResultsViewDialog", "Reach"))
        self.label_3.setText(_translate("RASResultsViewDialog", "River Sta."))
        self.openRASPushButton.setText(_translate("RASResultsViewDialog", "Open RAS"))
        self.openRASMapperPushButton.setText(_translate("RASResultsViewDialog", "Open RASMapper"))

