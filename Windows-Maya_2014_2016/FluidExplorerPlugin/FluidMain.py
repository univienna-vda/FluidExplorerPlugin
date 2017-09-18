########################################################################################################################
#                                                                                                                      #
#   This file calls the Fluid Explorer plugin. Please store the file in the following directory:                       #
#                                                                                                                      #
#       Windows: \Users\<username>\Documents\maya\<version>\scripts\FluidExplorerPlugin\FluidMain.py                   #
#                                                                                                                      #
#   Path to the Fluid Explorer plugin:                                                                                 #
#                                                                                                                      #
#       Windows: \Users\<username>\Documents\maya\<version>\scripts\FluidExplorerPlugin                                #
#                                                                                                                      #
########################################################################################################################

import os
import webbrowser
import logging

from PySide import QtCore, QtGui
from shiboken import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui
import maya.mel as mel

from FluidExplorerPlugin.ui.FileOpenDialog import FileOpenDialog
from FluidExplorerPlugin.ui.CreateProjectDialog import CreateProjectDialog
from FluidExplorerPlugin.ui.Utils.MayaCmds.MayaFunctions import MayaFunctionUtils
from FluidExplorerPlugin.ui.Utils.MayaCmds import MayaFunctions
from FluidExplorerPlugin.ui.Utils.FluidExplorerUtils import FluidExplorerUtils
from FluidExplorerPlugin.ui.Utils import Settings
from FluidExplorerPlugin.ui.Icons import icons
from FluidExplorerPlugin.ui.ProjectDetailsView import ProjectDetailsView
from FluidExplorerPlugin.ui.Utils.DefaultUIValues import DefaultUIParameters

import FluidExplorerPlugin.ui.MainWindow as mainUi

FLUID_EXPLORER_URL = DefaultUIParameters.URL


# Get the maya main window as a QMainWindow instance
def getMayaWindow():
    mayaMainWindowPtr = omui.MQtUtil.mainWindow()
    mayaMainWindow= wrapInstance(long(mayaMainWindowPtr), QtGui.QDialog)


#
# Main window control called from maya app
#
class ControlMainWindow(QtGui.QMainWindow):

    def __init__(self, parent = getMayaWindow()):

        # Initialize qt window
        super(ControlMainWindow, self).__init__(parent)
        self.ui = mainUi.Ui_MainWindow()
        self.ui = mainUi.Ui_MainWindow()
        self.ui.setupUi(self)

        # Show always on top
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        # Set up dark_orange style sheet
        self.setStyleSheet( ControlMainWindow.getStyleSheet() )

        # Url for the help page
        self.url = FLUID_EXPLORER_URL

        # Initialize connections and icons for the buttons
        self.createConnections()
        self.setupButtons()

        # Position of the plugin main window in the maya app
        self.centre()

        # Subprocess number
        self.pid = None

        # Details View
        self.detailsView = None
        if self.detailsView:
            self.detailsView.close()

        # //////////////////////////////////////////////////////////////////////////////////////////////////////////////
        # //////////////////////////////////////////////////////////////////////////////////////////////////////////////
        # For tests only
        # runTests = True
        runTests = False
        if runTests:
            import maya.mel as mel

            # Animation Start/End Time
            cmds.playbackOptions(animationStartTime=1.00)
            cmds.playbackOptions(animationEndTime=15.00)
        # //////////////////////////////////////////////////////////////////////////////////////////////////////////////
        # //////////////////////////////////////////////////////////////////////////////////////////////////////////////

        FluidExplorerUtils.killProcess("fluidexplorer")

        # Check if cache values are correct
        FluidExplorerUtils.initCahceSettings()

        # Register script job for closing the application
        self.FXScriptJobDeleteShelf()

        # Logging
        self.lgr = logging.getLogger('FluidExplorerPlugin')


    # Places the plugin in the maya app
    def centre(self):
        panelPtr = omui.MQtUtil.findControl('modelPanel1')

        if panelPtr == None:
            """
            Center the main window on the screen. This implemention will handle the window
            being resized or the screen resolution changing.
            """
            # Get the current screens' dimensions
            screen = QtGui.QDesktopWidget().screenGeometry()
            # Get this windows' dimensions
            mysize = self.geometry()
            # The horizontal position is calulated as screenwidth - windowwidth /2
            hpos = ( screen.width() - mysize.width() ) / 2
            # And vertical position the same, but with the height dimensions
            vpos = ( screen.height() - mysize.height() ) / 2
            # And the move call repositions the window
            self.move(hpos + 300, vpos - 100)
        else:
            panel = wrapInstance(long(panelPtr), QtGui.QWidget)
            position =  panel.mapToGlobal(panel.pos())
            #self.move(position.x(), position.y() + (panel.geometry().height() / 2 - self.geometry().height() / 2) + 5)
            self.move(position.x(), position.y())

            self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

    # Read the dark orange stylesheet
    @staticmethod
    def getStyleSheet():
        style_sheet_file = os.path.join(Settings.PKG_RESOURCE_PATH, 'darkorange.stylesheet')
        custome_style_sheet = open(style_sheet_file, 'r')
        sheet = custome_style_sheet.read()
        custome_style_sheet.close()

        return sheet

    # Connect buttons and event listeners
    def createConnections(self):
        self.ui.pushButtonLoadSimulation.clicked.connect(self.buttonLoadSimulation_Event)
        self.ui.pushButtonNewProject.clicked.connect(self.buttonNewProject_Event)
        self.ui.pushButtonHelpMain.clicked.connect(self.buttonHelpMain_Event)

    # Initialize buttons (icons)
    def setupButtons(self):
        icon_open = QtGui.QIcon(QtGui.QPixmap(':/open_icon_orange.png'))
        icon_create = QtGui.QIcon(QtGui.QPixmap(':/new_icon_orange.png'))
        icon_help = QtGui.QIcon(QtGui.QPixmap(':/help_icon_orange.png'))
        icon_fluidExplorer = QtGui.QIcon(QtGui.QPixmap(':/help_icon_orange.png'))
        icon_fluidExplorer_black = QtGui.QIcon(QtGui.QPixmap(':/icon_fluidexplorer_black.png'))
        pixmap_help = QtGui.QPixmap(':/icon_fluidexplorer.png')
        pixmap_help_scaled = pixmap_help.scaled(30, 30, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)

        self.ui.pushButtonNewProject.setIcon(icon_create)
        self.ui.pushButtonLoadSimulation.setIcon(icon_open)
        self.ui.pushButtonHelpMain.setIcon(icon_help)
        self.ui.labelIcon.setText("")
        self.ui.labelIcon.setPixmap(pixmap_help_scaled)
        self.setWindowIcon(icon_fluidExplorer_black)

        buttonStyleBold = "QPushButton { font-weight: bold; }"
        self.ui.pushButtonNewProject.setStyleSheet(buttonStyleBold)
        self.ui.pushButtonLoadSimulation.setStyleSheet(buttonStyleBold)

    # Eventhandler - Load simulation
    @QtCore.Slot()
    def buttonLoadSimulation_Event(self):
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowStaysOnTopHint)
        self.close()

        # Get current scene name
        currentSceneName = cmds.file(q=True, sceneName=True)

        # Path of the Fluid Explorer folder
        filePathMain = os.path.dirname(os.path.abspath(__file__))
        fxPathRel = os.path.abspath(filePathMain)

        styleSheet = ControlMainWindow.getStyleSheet()
        self.openDialog = FileOpenDialog(styleSheet)
        [dialogResult, selectedDir, pid] = self.openDialog.openDirDialog(currentSceneName, fxPathRel)

        # Scene opened flag
        sceneOpened = False

        # cancel --> Show dialog again, result=started --> call fluid explorer
        if not dialogResult == "started":

            self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
            self.centre()
            self.show()
        else:
            self.lgr.info("Scene %s successfully opened", selectedDir)
            sceneOpened = True
            self.pid = pid

        # --------------------------------------------------------------------------------------
        # Create scene details window
        if sceneOpened:
            #self.detailsView.close()
            self.detailsView = ProjectDetailsView(self, selectedDir)
            self.detailsView.show()
        # --------------------------------------------------------------------------------------

    # Eventhandler - create simulation
    @QtCore.Slot()
    def buttonNewProject_Event(self):

        # Chek if pne fluid container is selected
        helpFunc = MayaFunctionUtils()
        [status, errorMsg, transformNode] = helpFunc.getSelectedContainerPy()

        self.lgr.info("Selected container (type: - transform node): %s",  transformNode)

        if status == False:
            errorMsg = errorMsg
            self.lgr.warning("%s", errorMsg)
            self.showMessageBox(errorMsg, 'warning')

        else:

            fluidShapeName = errorMsg   # errorMsg: stores the name of the selected fluid
            try:
                cmds.select(fluidShapeName, r=True)

                self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)    # Hide main window
                self.lgr.info("Selected container (type: - transform node): %s",  errorMsg)

                # Show create simulation dialog
                # errorMsg -> fluidName or error message
                # transformNode -> transform node
                createDialog = CreateProjectDialog(self, errorMsg, transformNode)
                createDialog.setFluidName(errorMsg)
                dialogCode = createDialog.exec_()

                # Dialog canceled
                if dialogCode == QtGui.QDialog.Rejected:
                    self.show()

            except ValueError as er:
                errorMsg = "Cannot use selected fluid container '"+ fluidShapeName + "'" + ".\nDetails: " + er.message
                self.lgr.error("Cannot use selected fluid container: %s",  er.message)
                self.showMessageBox(errorMsg, 'critical')

    # Eventhandler - Help button
    @QtCore.Slot()
    def buttonHelpMain_Event(self):
        _url = self.url
        webbrowser.open(_url, new=1)

    def showMessageBox(self, text, type):
        msgBox = QtGui.QMessageBox(self)
        msgBox.setStyleSheet("QPushButton{min-width: 70px;} QMessageBox{font-size: 12px;}")
        msgBox.setText(text)

        if type == 'warning':
            msgBox.setWindowTitle("Warning")
            msgBox.setIcon(QtGui.QMessageBox.Warning)
        if type == 'critical':
            msgBox.setWindowTitle("Error")
            msgBox.setIcon(QtGui.QMessageBox.Critical)

        msgBox.exec_()

    def closeEvent(self, event):
        # close (x button) event
        FluidExplorerUtils.killProcess("fluidexplorer")

    # This script job ('quitApplication') is called when the application is closed
    def FXScriptJobDeleteShelf(self):
        # Read the adapted mel script and load it
        path_mel_script = os.path.join(Settings.PKG_RESOURCE_PATH, 'mel_scripts/RemoveShelfButton.mel')
        fC = False
        if os.path.exists(path_mel_script):
            with open(path_mel_script, 'r') as content_file:
                content = content_file.read()
                if len(content) > 100:
                    fC = True
        if fC:
            # Register th mel script
            mel.eval(content)

            # Register the script job
            cmds.scriptJob(event=['quitApplication', self.shelf_command])

    @staticmethod
    def shelf_command():
        if cmds.shelfLayout('FluidExplorer', ex=True):
            cmd = 'deleteShelfTab FluidExplorer'
            mel.eval('deleteShelfTabWithoutConfirm FluidExplorer')
#
# MAIN
#
def main():

    # Logger
    lgr = logging.getLogger('FluidExplorerPlugin')

    # Check if maya version is correct (>= 2014)
    isVersionOK = checkMayaVersion()
    isPlattformOK = checkPlatform()

    lgr.info(' ')
    lgr.info('Maya version correct: %s', isVersionOK)
    lgr.info('Platform correct: %s', isVersionOK)

    if not isPlattformOK:
        showMessageBoxPlugin("The current operating system not supported!\nPlease use a Windows based version.", "warning")
        lgr.error('The current operating system not supported')
        return None

    if not isVersionOK:
        showMessageBoxPlugin("The current Maya version is not supported!\nPlease install version 2014 or higher.", "warning")
        lgr.error('The current Maya version is not supported')
        return None

    if isVersionOK and isPlattformOK:
        # Check if a window has already been opened. If yes, close it. Otherwise create new maya main window
        if cmds.window("FluidExplorer",ex=True) == 1:
            cmds.deleteUI("FluidExplorer")

        # Initialize main window and show in maya
        mainWin = ControlMainWindow( parent = getMayaWindow() )
        lgr.info('FluidExplorer plugin started')
        lgr.info(' ')
        #FXScriptJob();

        return mainWin


def helpButtonToolBar():
    webbrowser.open(FLUID_EXPLORER_URL, new=1)

def checkMayaVersion():
    versionStr = cmds.about(version=True)
    if len(versionStr) >= 4:
        version = versionStr[0:4]
        try:
            versionInteger = int(version)
        except ValueError:
            versionIsOk = False
        finally:
            if versionInteger >= 2014:
                versionIsOk = True
            else:
                versionIsOk = False

    else:
        versionIsOk = False

    return versionIsOk

def checkPlatform():
    currentPlatfromOK = cmds.about(win=True)  # Check if paltform is windows based

    return currentPlatfromOK

def showMessageBoxPlugin(text, type):
    msgBox = QtGui.QMessageBox()
    msgBox.setStyleSheet("QPushButton{min-width: 70px;} QMessageBox{font-size: 12px;}")
    msgBox.setText(text)

    if type== 'warning':
        msgBox.setWindowTitle("Warning")
        msgBox.setIcon(QtGui.QMessageBox.Warning)
    if type== 'critical':
        msgBox.setWindowTitle("Error")
        msgBox.setIcon(QtGui.QMessageBox.Critical)

    msgBox.exec_()