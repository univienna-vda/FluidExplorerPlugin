# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'E:\WorkspacePython\FluidExplorerPlugin\ui\ChooseCameraUI.ui'
#
# Created: Wed Jul 15 15:03:35 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui


class Ui_DialogChooseCamer(object):
    def setupUi(self, DialogChooseCamer):
        DialogChooseCamer.setObjectName("DialogChooseCamer")
        DialogChooseCamer.resize(360, 100)
        DialogChooseCamer.setMinimumSize(QtCore.QSize(360, 100))
        DialogChooseCamer.setMaximumSize(QtCore.QSize(360, 100))
        self.label_Name = QtGui.QLabel(DialogChooseCamer)
        self.label_Name.setGeometry(QtCore.QRect(10, 19, 121, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_Name.setFont(font)
        self.label_Name.setObjectName("label_Name")
        self.comboBox = QtGui.QComboBox(DialogChooseCamer)
        self.comboBox.setGeometry(QtCore.QRect(140, 20, 210, 22))
        self.comboBox.setObjectName("comboBox")
        self.pushButtonSelect = QtGui.QPushButton(DialogChooseCamer)
        self.pushButtonSelect.setGeometry(QtCore.QRect(280, 58, 71, 25))
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.pushButtonSelect.setFont(font)
        self.pushButtonSelect.setStyleSheet("")
        self.pushButtonSelect.setObjectName("pushButtonSelect")
        self.pushButtonCancel = QtGui.QPushButton(DialogChooseCamer)
        self.pushButtonCancel.setGeometry(QtCore.QRect(200, 58, 71, 25))
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.pushButtonCancel.setFont(font)
        self.pushButtonCancel.setStyleSheet("")
        self.pushButtonCancel.setAutoDefault(False)
        self.pushButtonCancel.setObjectName("pushButtonCancel")

        self.retranslateUi(DialogChooseCamer)
        QtCore.QMetaObject.connectSlotsByName(DialogChooseCamer)

    def retranslateUi(self, DialogChooseCamer):
        DialogChooseCamer.setWindowTitle(QtGui.QApplication.translate("DialogChooseCamer", "Choose Camera", None, QtGui.QApplication.UnicodeUTF8))
        self.label_Name.setText(QtGui.QApplication.translate("DialogChooseCamer", "Select a camera:", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonSelect.setText(QtGui.QApplication.translate("DialogChooseCamer", "Select", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonCancel.setText(QtGui.QApplication.translate("DialogChooseCamer", "Cancel", None, QtGui.QApplication.UnicodeUTF8))