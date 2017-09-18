# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Patrick\Documents\maya\2014-x64\scripts\FluidExplorerPlugin\ui\Resources\MainWindow.ui'
#
# Created: Fri May 06 16:20:38 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(410, 150)
        MainWindow.setMinimumSize(QtCore.QSize(410, 150))
        MainWindow.setMaximumSize(QtCore.QSize(410, 150))
        MainWindow.setAutoFillBackground(False)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButtonNewProject = QtGui.QPushButton(self.centralwidget)
        self.pushButtonNewProject.setGeometry(QtCore.QRect(20, 80, 170, 40))
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.pushButtonNewProject.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/ico_add.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonNewProject.setIcon(icon)
        self.pushButtonNewProject.setIconSize(QtCore.QSize(30, 30))
        self.pushButtonNewProject.setObjectName("pushButtonNewProject")
        self.pushButtonLoadSimulation = QtGui.QPushButton(self.centralwidget)
        self.pushButtonLoadSimulation.setGeometry(QtCore.QRect(220, 80, 170, 40))
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.pushButtonLoadSimulation.setFont(font)
        self.pushButtonLoadSimulation.setStyleSheet("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/img/ico_search.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonLoadSimulation.setIcon(icon1)
        self.pushButtonLoadSimulation.setIconSize(QtCore.QSize(30, 30))
        self.pushButtonLoadSimulation.setObjectName("pushButtonLoadSimulation")
        self.labelMain = QtGui.QLabel(self.centralwidget)
        self.labelMain.setGeometry(QtCore.QRect(58, 20, 161, 30))
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(20)
        font.setItalic(False)
        font.setStrikeOut(False)
        self.labelMain.setFont(font)
        self.labelMain.setObjectName("labelMain")
        self.pushButtonHelpMain = QtGui.QPushButton(self.centralwidget)
        self.pushButtonHelpMain.setGeometry(QtCore.QRect(350, 16, 41, 40))
        self.pushButtonHelpMain.setAutoFillBackground(False)
        self.pushButtonHelpMain.setStyleSheet("")
        self.pushButtonHelpMain.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("icons/ico_help.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonHelpMain.setIcon(icon2)
        self.pushButtonHelpMain.setIconSize(QtCore.QSize(30, 30))
        self.pushButtonHelpMain.setDefault(False)
        self.pushButtonHelpMain.setObjectName("pushButtonHelpMain")
        self.labelIcon = QtGui.QLabel(self.centralwidget)
        self.labelIcon.setGeometry(QtCore.QRect(20, 22, 30, 30))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.labelIcon.setFont(font)
        self.labelIcon.setObjectName("labelIcon")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setEnabled(False)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Fluid Explorer", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonNewProject.setText(QtGui.QApplication.translate("MainWindow", "Create Simulation", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonLoadSimulation.setText(QtGui.QApplication.translate("MainWindow", "Load Simulation", None, QtGui.QApplication.UnicodeUTF8))
        self.labelMain.setText(QtGui.QApplication.translate("MainWindow", "Fluid Explorer", None, QtGui.QApplication.UnicodeUTF8))
        self.labelIcon.setText(QtGui.QApplication.translate("MainWindow", "HALL", None, QtGui.QApplication.UnicodeUTF8))

