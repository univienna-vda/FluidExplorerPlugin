from PySide import QtGui

import os
import logging
import maya.cmds as cmds

from FluidExplorerPlugin.ui.Utils.FluidExplorerUtils import FluidExplorerUtils
from FluidExplorerPlugin.ui.Utils.DefaultUIValues import DefaultUIParameters


class FileOpenDialog(QtGui.QDialog):

    global WORKING_DIRECTORY
    global FX_RELATIVE_PATH

    WORKING_DIRECTORY = cmds.workspace(q=True, dir=True)

    #FX_RELATIVE_PATH = '/FluidExplorerPlugin/tmp/README.txt'

    def __init__(self, styleSheet):
        QtGui.QDialog.__init__(self)
        self.lgr = logging.getLogger('FluidExplorerPlugin')
        self.style = styleSheet

    """
    #
    # NOT IN USE
    #
    def openSimulation(self, choosenFile, fxPathRoot):
        # choosenFile: Path to the .fxp file
        # fxPathRoot: script folder

        if not os.path.exists(self.PATH_FLUIDEXPLORER_APP):
            errorMsg = "Cannot find the FluidExplorer application executable!" + "\n" + "Please check if  the executable file is available."
            self.showMessageBox(errorMsg, 'warning')

        else:
            simulationDataPath = self.readSimulationDataPath(choosenFile)
            try:
                path = os.getcwd()
                os.chdir(self.PATH_FLUIDEXPLORER_APP)

                # Path to the raw data for the fluid explorer
                str_load_path = "/load path=" + simulationDataPath

                # Path to the settings file
                str_settings_path = "/load path=" + choosenFile

                logging.info('Open FluidExplorer application')
                logging.info('Load path: %s', str_load_path)
                logging.info('Settings file: %s', str_settings_path)

                # Call Subprocess
                #pid = subprocess.Popen(["fluidexplorer.exe", str_load_path], stdout=subprocess.PIPE, shell=True) # call subprocess

            except Exception as e:
                errorMsg = "Unable to start the FluidExplorer application!" + "\nDetails: " + e.message
                self.showMessageBox(errorMsg, 'critical')
                logging.error("Unable to start the FluidExplorer application! Details: %s", e.message)
                os.chdir(os.path.abspath(path))

            finally:
                pass
                #subprocess._cleanup()

            # Return back to root directory
            os.chdir(os.path.abspath(path))
            logging.info('Changed directory back after calling FluidExplorer app: %s', os.path.abspath(path))
    """

    def checkPrjRoot(self, choosenDir, currentScene):
        isSameScene = True
        isNumberOk = True
        canReadConfigFile = True

        fileExists = os.path.exists(choosenDir)
        if not fileExists:
            canReadConfigFile = False
            self.lgr.warning("File does not exist: %s", choosenDir)
            errorText = "Project configuration file does not exists!"
            return [canReadConfigFile, isNumberOk, isSameScene, errorText]

        try:
            tmpSimulationName = FluidExplorerUtils.readAttributeFromXmlConfigurationsFile(choosenDir, 'ProjectName')
            tmpPath = FluidExplorerUtils.readAttributeFromXmlConfigurationsFile(choosenDir, 'MayaFilePath')

            # tmpPath: Stores the file which holds the fluid container based on the selected directory
            dir_path = os.path.dirname(choosenDir)
            tmpPath = dir_path + '/' + 'fluid_simulation_scene.mb'

            # Stores the name of the project
            tmpSimulationName = os.path.dirname(dir_path)

            # tmpPath = scene name ('fluid_simulation_scene.mb') based on the selected directory
            # currentScene = scene which is opend at the moment
            # print os.path.abspath(tmpPath)
            # print os.path.abspath(currentScene)

            self.lgr.info("Path of the maya file to load: %s", tmpSimulationName)

        except:
            canReadConfigFile = False
            errorText = "An error occured while loading the project configuration file!"
            return [canReadConfigFile, isNumberOk, isSameScene, errorText]

        if tmpSimulationName == "" or tmpSimulationName == None:
            canReadConfigFile = False
            errorText = "An error occured while loading the project configuration file!\nProperty: 'MayaFilePath'"
            return [canReadConfigFile, isNumberOk, isSameScene, errorText]

        # Check if same scene opened
        tmpSimulationName_low = os.path.abspath(tmpPath).lower()
        # currentScene_low = currentScene.lower()
        currentScene_low = os.path.abspath(currentScene).lower()

        if tmpSimulationName_low != currentScene_low:
            isSameScene = False
            errorTxt = "Please load the correct Maya scene file first!\nScene Path: " + tmpPath

            return [canReadConfigFile, isNumberOk, isSameScene, errorTxt]

        return [canReadConfigFile, isNumberOk, isSameScene, ""]

    def openDirDialog(self, currentSceneName, fxPathRoot):

        # currentSceneName: e.g. E:/Tmp/test.mb
        # fxPathRoot: e.g.: .../maya/2014-x64/scripts

        self.lgr.info("Load Animation")

        # Current scene name
        # self.rawName = cmds.file(query = True, sceneName = True);
        self.rawName = currentSceneName
        strStarted = "started"

        dialog = QtGui.QFileDialog()
        dialog.show()
        dialog.close()

        dialog.setStyleSheet(self.style)
        dialog.setWindowTitle(self.tr("Fluid Explorer - Load Simulation"))
        dialog.setFileMode(QtGui.QFileDialog.ExistingFile)
        dialog.setNameFilter("Fluid Explorer Project (*.fxp)")
        dialog.setViewMode(QtGui.QFileDialog.List) # or Detail

        if len(self.rawName) > 0:
            # print os.path.dirname(self.rawName)
            dialog.setDirectory(os.path.dirname(self.rawName))
        else:
            dialog.setDirectory(WORKING_DIRECTORY)

        if dialog.exec_():

            selectedFile = dialog.selectedFiles()
            if len(selectedFile) == 1:
                choosenDir = selectedFile[0]
                
                # Get the current maya scene name
                [canReadConfigFile, isNumberOk, isSameScene, errorText] = self.checkPrjRoot(choosenDir, self.rawName)
              
                if not canReadConfigFile:
                    # Can not read xml project file with
                    self.showMessageBox(errorText, 'critical')
                    self.lgr.error(errorText)
                    return ["", "", ""]

                else:
                    if not isSameScene:
                        # Warning - not the same scene is loaded
                        self.showMessageBox(errorText, 'warning')
                        self.lgr.warning(errorText)
                        return ["", "", ""]

                    # Check if the fluid container exists in the scene
                    [nodeExists, errorMsg] = self.checkIfFluidNodeExistsInScene(choosenDir)
                    if not nodeExists:
                        self.showMessageBox(errorMsg, 'warning')
                        self.lgr.warning(errorMsg)
                        return ["", "", ""]

                    #        # Warning scene is loaded
                    #        self.showMessageBox(errorText, 'warning')

                    else:
                        try:
                            import exceptions

                            #fluidExplorerPath = self.getFXPath(fxPathRoot, FX_RELATIVE_PATH)

                            """
                            if not fluidExplorerPath == "":
                                pass
                                #pid = self.openSimulation(choosenDir, fxPathRoot)
                                pid = 1
                            else:
                                self.lgr.error('FluidExplorer executable file not found')
                                raise Exception("FluidExplorer executable file not found!")
                            
                            # return "started"
                            """

                        except Exception as e:
                            errorMsg = "Unable to start the Fluid Explorer application!" + "\nDetails: " + e.message
                            self.lgr.error('Unable to start the Fluid Explorer application! Details: %s', e.message)
                            self.showMessageBox(errorMsg, 'critical')

                        return [strStarted, choosenDir, 1]   # return started -> everything fine!
        else:
            # cancel
            return ["", "", ""]

    def readSimulationDataPath(self, choosenDir):
        try:
            tmpProjectName = FluidExplorerUtils.readAttributeFromXmlConfigurationsFile(choosenDir, 'ProjectName')
            tmpProjectPath = FluidExplorerUtils.readAttributeFromXmlConfigurationsFile(choosenDir, 'ProjectPath')

        except:
            return ""

        path = tmpProjectPath + '/' + tmpProjectName
        return path

    def getFXPath(self, fxPathRoot, fxRelativePath):
        fullPathToFluidExplorer = ""
       
        tmpPath = fxPathRoot + fxRelativePath
        if os.path.exists(tmpPath):
            fullPathToFluidExplorer = tmpPath

        return fullPathToFluidExplorer

    def checkIfFluidNodeExistsInScene(self, choosenFile):
        tmpFluidNodeName = FluidExplorerUtils.readAttributeFromXmlConfigurationsFile(choosenFile, 'FluidBoxName')
        self.lgr.info("Fluid container name from the settings file: %s", tmpFluidNodeName)

        if cmds.objExists(tmpFluidNodeName):
            return [True, ""]
        else:
            return [False, "Cannot find the specified Fluid Container in the opened project!\n"
                           "Please check if the the node '" + tmpFluidNodeName + "' exists."]

    def showMessageBox(self, errorMsg, type):
        self.msgBox = QtGui.QMessageBox(self)
        self.msgBox.setText(errorMsg)
        if type == 'critical':
            self.msgBox.setWindowTitle("Error - Load Simulation")
            self.msgBox.setIcon(QtGui.QMessageBox.Critical)
        if type == 'warning':
            self.msgBox.setWindowTitle("Warning - Load Simulation")
            self.msgBox.setIcon(QtGui.QMessageBox.Warning)

        self.msgBox.setStyleSheet(DefaultUIParameters.buttonStyleBold)
        self.msgBox.exec_()

    # The dialog to get to the directory of the simulations
    def openDirDialogQuick(self):
        dialog = QtGui.QFileDialog(self)
        dialog.setWindowTitle(self.tr("Fluid Explorer - Choose Project Directory"))
        dialog.setFileMode(QtGui.QFileDialog.DirectoryOnly)
        dir = cmds.workspace(q=True, dir=True)
        dialog.setDirectory(dir)
        dialog.setViewMode(QtGui.QFileDialog.List) # or Detail

        if dialog.exec_():
            fileSelected= dialog.selectedFiles()
            if len(fileSelected) == 1:
                choosenDir = fileSelected[0]

                isOk = True
                if isOk:
                    return choosenDir
                else:
                    msgBox = QtGui.QMessageBox()
                    msgBox.setText("Please select a valid directory!")
                    msgBox.setWindowTitle("Warning - Load Simulation")
                    msgBox.setIcon(QtGui.QMessageBox.Warning)
                    msgBox.setStyleSheet(DefaultUIParameters.buttonStyleBold)
                    msgBox.exec_()

    # Gets the project name from the whole path
    def getPrpjectNameFromString(self, path):
        projectName = ''

        posSceneName = path.find('fluid_simulation_scene.mb')
        if not posSceneName == -1:
            tmp = path[0:posSceneName-1]

            pos = self.find(tmp, '/')
            if pos >= 2:
                index = pos[len(pos)-1]
                projectName = path[index:posSceneName]
                if projectName.endswith('/'): projectName = projectName[0:len(projectName)-1]
                if projectName.startswith('/'): projectName = projectName[1:len(projectName)]

        return projectName

    def find(self, s, ch):
        return [i for i, ltr in enumerate(s) if ltr == ch]

