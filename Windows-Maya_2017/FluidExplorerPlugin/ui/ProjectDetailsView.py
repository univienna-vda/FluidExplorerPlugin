from PySide2 import QtCore, QtGui, QtWidgets
from ProjectDetailsViewUI import Ui_ProjectDetailsView

from FluidExplorerPlugin.ui.Utils.DefaultUIValues import DefaultUIParameters
from FluidExplorerPlugin.ui.Utils.ProjectDetailsViewUtils import ProjectDetailsViewUtils
from FluidExplorerPlugin.ui.Utils.ProjectDetailsViewUtils import ExternalCallSetting
from FluidExplorerPlugin.ui.Utils.LoadFluidCacheFile import LoadFluidCacheFile
from FluidExplorerPlugin.ui.Utils.FluidExplorerUtils import FluidExplorerUtils
from FluidExplorerPlugin.ui.Utils.DefaultUIValues import DefaultUIParameters
# from FluidExplorerPlugin.ui.Utils.ExternalCallWorkerThread import WorkThread

from maya import OpenMayaUI as omui
import maya.cmds as cmds
from shiboken2 import wrapInstance
import os, sys
import logging
import subprocess
import webbrowser


class ProjectDetailsView(QtWidgets.QDialog):

    PERSPECTIVE_CAMERA_AVAILABLE = '1'
    PERSPECTIVE_CAMERA_NOT_AVAILABLE = '0'

    def __init__(self, args, pathToXMLFile):

        QtWidgets.QDialog.__init__(self, args)

        # Logger
        self.lgr = logging.getLogger('FluidExplorerPlugin')

        # Stores th path to the XML file
        self.pathToXMLFile = pathToXMLFile
        self.PathToXMLCache = ''
        self.selectedProjectFolder = ''

        # Members
        self.projectSettings = None
        self.hashMapToXMLProjectFile = {}
        self.hashMapToGIF = {}
        self.currentAnimationLoaded = None

        # Thread which starts the FX app
        self.workThread = None
        self.FLUIDEXPLORER_APP_NAME = "fluidexplorer"

        # Set up the user interface from the ui file
        self.ui = Ui_ProjectDetailsView()
        self.ui.setupUi(self)

        # Move window to the 'modelPanel1' position
        [xPos, yPos] = self.moveWindowToPanel()
        self.move(xPos, yPos)

        # Load icons
        self.init_icons()

        # QMovie
        self.movie = QtGui.QMovie(self)

        # Create connections
        self.createConnections()

        # Initialize widget
        self.initializewidget()
        self.setWindowHeightWithoutPreview()
        self.initializeComponentss()
        self.setWindowTitle('Fluid Explorer - Project View')

        # Window flags - top and buttons
        self.setWindowFlags(self.windowFlags() |
            QtCore.Qt.WindowMinimizeButtonHint |
            QtCore.Qt.WindowStaysOnTopHint)

        # Check if project file correct
        if not os.path.exists(self.pathToXMLFile):
            self.lgr.warning('Cannot load project file')
            self.showMessageBox('The project file could not be loaded!', 'warning')
            self.close(0)
            return
        elif os.path.exists(self.pathToXMLFile):
            self.selectedProjectFolder = os.path.dirname(self.pathToXMLFile)

        self.show()

        # Set values from project configuration file
        statusCode = self.projectSettings = self.readProjectProperties(self.pathToXMLFile)
        if statusCode:
            canSetAllFields = self.setValuesFromConfigurationFile(self.projectSettings)
            if not canSetAllFields:
                self.showMessageBox('Could not read all project attributes from the\nconfiguration file!', 'warning')
        else:
            self.setAllFieldsEnabled()

        # Initialize the combo box and the preview functionality
        if self.projectSettings:
            self.initComboBoxSimulations(self.projectSettings)
            self.initPreview(self.projectSettings)

        # Register scriptJob
        self.FXScriptJob()
        self._rcwin = 1

        # Create file for current selection
        ProjectDetailsViewUtils.create_file_current_selection(self.selectedProjectFolder)

        # File watcher
        self.init_file_watcher()

        # External call
        self.externalCall = ExternalCallSetting()
        self.setupExternallCall()

        self.lgr.info('Load project view created')
        self.lgr.info('Project path: %s', pathToXMLFile)


    def init_icons(self):
        self.icon_help = QtGui.QIcon(QtGui.QPixmap(':/help_icon_orange.png'))
        self.fav_icon_on = QtGui.QIcon(QtGui.QPixmap(':/favorites_on.png'))
        self.fav_icon_off = QtGui.QIcon(QtGui.QPixmap(':/favorites_off.png'))

    def setPathToProjectFile(self, path):
        self.pathToXMLFile = path

    def setAllFieldsEnabled(self):
        self.ui.pushButton_applyCache.setEnabled(False)
        self.ui.pushButton_exploreSimulations.setEnabled(False)
        self.ui.checkBox_showPreview.setEnabled(False)
        self.ui.comboBox_simulations.setEnabled(False)
        self.update()

    def moveWindowToPanel(self):
        try:
            panelPtr = omui.MQtUtil.findControl('modelPanel1')

            if not panelPtr:
                xPos = 0
                yPos = 0
            else:
                panel = wrapInstance(long(panelPtr), QtWidgets.QWidget)
                position = panel.mapToGlobal(panel.pos())
                if not panelPtr:
                    xPos = 0
                    yPos = 0
                else:
                    xPos = position.x()
                    yPos = position.y()
        except:
            xPos = 0
            yPos = 0

        return [xPos, yPos]

    def initializewidget(self):
        self.setMinimumWidth(340)
        self.setMaximumWidth(340)

    def setWindowHeightWithPreview(self):
        self.setMinimumHeight(620-12)
        self.setMaximumHeight(620-12)
        self.update()
        self.repaint()

    def setWindowHeightWithoutPreview(self):
        self.setMinimumHeight(380-2)
        self.setMaximumHeight(380-2)

    def initializeComponentss(self):
        self.ui.pushButton_help.setIcon(self.icon_help)

        self.setWindowTitle('Fluid Explorer - Simulation Details View')
        self.changeHLineStyle()
        self.setLineEditEnabledAndReadOnly(self.ui.lineEdit_projectName)
        self.setLineEditEnabledAndReadOnly(self.ui.lineEdit_projectPath)
        self.setLineEditEnabledAndReadOnly(self.ui.lineEdit_fluidContainer)
        self.setLineEditEnabledAndReadOnly(self.ui.lineEdit_startTime)
        self.setLineEditEnabledAndReadOnly(self.ui.lineEdit_endTime)

        self.ui.label_moviePreview.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.label_moviePreview.setStyleSheet("background-color: black;")

        self.scaleMovieLabel()
        self.ui.label_moviePreview.setMaximumHeight(170)
        self.ui.label_moviePreview.setMinimumHeight(170)

        txt = "File: " + "-"
        self.ui.label_fluidContainer_2.setText(txt)
        font = self.ui.label_fluidContainer_2.font()
        font.setPointSize(8)
        self.ui.label_fluidContainer_2.setFont(font)

    def setupExternallCall(self):
        # e.g. fluidexplorer.exe /settings path="E:/TMP/Fire_1/Fire_1.fxp" /load path="E:/TMP/Fire_1"

        # FluidExplorer path
        if sys.platform.lower().startswith('win'):
            # Windows
            self.externalCall.fluidExplorerCmd = 'fluidExplorer.exe'
        elif sys.platform.lower().startswith('darwin'):
            # MacOS
            self.externalCall.fluidExplorerCmd = 'fluidExplorer'

        self.externalCall.pathToFluidExplorer = ProjectDetailsViewUtils.getPathFluidExplorer(self.externalCall.fluidExplorerCmd)

        # Settings file
        settingXMLFile = self.pathToXMLFile # e.g. E:/TMP/Projects/TestProject1.fxp -> selected project file

        # Path to cached files
        cacheFile = ProjectDetailsViewUtils.getPathCacheFiles(self.pathToXMLFile)

        if os.path.exists(settingXMLFile) and os.path.exists(cacheFile):
            self.externalCall.isArgumentCorrect = True
        else:
            self.externalCall.isArgumentCorrect = False

        # Args
        self.externalCall.fluidExplorerArgs = ['/settings', 'path='+str(settingXMLFile), '/load', 'path='+str(cacheFile)]

    def scaleMovieLabel(self):
        # Is supposed to be: 960x540
        # Width = 300
        size = self.ui.label_moviePreview.size()
        newSize = QtCore.QSize(300, 169)
        self.movie.setScaledSize(newSize)

    def setValuesFromConfigurationFile(self, projectSettings):
        canReadAllAttributes = True

        self.lgr.info('Read projects attributes:')
        for attr, value in projectSettings.__dict__.iteritems():
            # txt = attr + ": " + value
            self.lgr.info('%s : %s', attr, value)
            if value == None:
                canReadAllAttributes = False
                self.lgr.warning('Cannot read attribute %s', attr)

        if projectSettings:
            self.ui.lineEdit_projectName.setText(projectSettings.projectName)
            self.ui.lineEdit_projectPath.setText(self.selectedProjectFolder)
            self.ui.lineEdit_fluidContainer.setText(projectSettings.fluidContainerName)

            # Convert values
            try:
                floatStartTime = float(projectSettings.animationStartTime)
                strStartTime = str(round(floatStartTime, 2))
            except ValueError:
                self.lgr.warning('Cannot convert animation start time to float type')
                strStartTime = "Error"

            try:
                floatEndTime = float(projectSettings.animationEndTime)
                strEndTime = str(round(floatEndTime, 2))
            except ValueError:
                self.lgr.warning('Cannot convert animation end time to float type')
                strEndTime = "Error"

            self.ui.lineEdit_startTime.setText(strStartTime)
            self.ui.lineEdit_endTime.setText(strEndTime)

        return canReadAllAttributes

    def initComboBoxSimulations(self, projectSettings):
        old_index = self.ui.comboBox_simulations.currentIndex()     # def = -1

        # Stores animation index and path
        haspMap = {}

        # Clear list id items are available
        item_len = self.ui.comboBox_simulations.count()
        if item_len > 0:
            self.ui.comboBox_simulations.clear()

        # Read the number of samples information
        try:
            num = int(projectSettings.numberOfSimulations)
        except:
            num = 0

        # Read textfile which stores the favorites
        list_of_favorites = ProjectDetailsViewUtils.get_favorites(self.selectedProjectFolder, num)

        # First item
        self.ui.comboBox_simulations.addItem('Select Sequence ...')

        show_favorites_icon = False
        if num == len(list_of_favorites):
            show_favorites_icon = True

        if num > 0:
            for i in range(num):
                # Firste entry
                tmpNameForElement = 'Sequence ' + str(i)

                # Folders
                # tmpProject = projectSettings.projectName + '.fxp'
                # index = self.pathToXMLFile.find(tmpProject)
                # tmp = self.pathToXMLFile[0:index]
                # tmp = tmp + '/' + str(i) + '/'

                tmp = self.selectedProjectFolder + '/' + str(i) + '/'
                if os.path.exists(tmp):
                    pathToXMLProjectFileList = ProjectDetailsViewUtils.getPathToXMLFile(tmp)

                    if len(pathToXMLProjectFileList) == 1:
                        if os.path.exists(pathToXMLProjectFileList[0]):
                            haspMap[i] = pathToXMLProjectFileList[0]

                            if show_favorites_icon:
                                # Show icons left from item
                                is_favorite = list_of_favorites[i]

                                txt = tmpNameForElement
                                if is_favorite:
                                    self.ui.comboBox_simulations.addItem(self.fav_icon_on, txt)
                                    # self.ui.comboBox_simulations.addItem(txt)
                                else:
                                    self.ui.comboBox_simulations.addItem(self.fav_icon_off, txt)
                                    # self.ui.comboBox_simulations.addItem(txt)

                                self.ui.comboBox_simulations.update()
                            else:
                                # Do not show icons
                                txt = tmpNameForElement
                                self.ui.comboBox_simulations.addItem(txt)

            # Save map
            self.hashMapToXMLProjectFile = haspMap

            # Select index
            if old_index == -1:
                self.ui.comboBox_simulations.setCurrentIndex(0)
            else:
                if old_index <= self.ui.comboBox_simulations.count():
                    self.ui.comboBox_simulations.setCurrentIndex(old_index)


    def initPreview(self, projectSettings):
        if (projectSettings.cam_persp == '1') or (projectSettings.cam_vc == '1') or \
                (projectSettings.cam_custom != 'None') or (projectSettings.cam_rotation != '0'):
            self.hashMapToGIF = ProjectDetailsViewUtils.getGIFHashMap(projectSettings, self.selectedProjectFolder)
        else:
            self.ui.checkBox_showPreview.setEnabled(False)

    def createConnections(self):
        self.ui.pushButton_applyCache.clicked.connect(self.applyCacheClicked)
        self.ui.pushButton_exploreSimulations.clicked.connect(self.exploreSimulationsClicked)
        self.ui.checkBox_showPreview.stateChanged[int].connect(self.checkBoxPreviewValueChanged)
        self.ui.comboBox_simulations.currentIndexChanged['QString'].connect(self.comboBoxSimulationsIndexChanged)
        self.ui.pushButton_help.clicked.connect(self.helpButtonClicked)
        self.movie.frameChanged[int].connect(self.frameChangedHandler)

    def playAnimation(self, simulationIndex):
        if self.hashMapToGIF == None:
            return

        # Index for the hash map
        hashIndex = simulationIndex - 1

        if simulationIndex == 0:
            self.stopPlayingAnimation()
            return

        if (hashIndex > len(self.hashMapToGIF)-1) or (len(self.hashMapToGIF) == 0):
            self.ui.label_moviePreview.setText("<b>[ Cannot find animation ... ]</b>")
            self.stopPlayingAnimation()
            return

        fileName = self.hashMapToGIF[hashIndex]

        if not os.path.exists(fileName):
            self.ui.label_moviePreview.setText("<b>[ Cannot find animation ... ]</b>")
            self.stopPlayingAnimation()
            return
        else:
            self.ui.label_moviePreview.setText("")
            self.ui.label_moviePreview.setMovie(self.movie)

        # Play animation
        currentState = self.movie.state()

        if currentState == QtGui.QMovie.Running:
            self.movie.stop()
            self.movie.setFileName(fileName)
            self.movie.start()

        elif currentState == QtGui.QMovie.NotRunning:
            self.movie.setFileName(fileName)
            self.movie.start()

    def stopPlayingAnimation(self):
        self.movie.stop()
        self.ui.label_moviePreview.setText("<b>[ No Simulation selected ... ]</b>")

    def init_file_watcher(self):
        # A file watcher detects changes in text files

        # favorites: fluidExplorer.favorites
        file_favorites = self.selectedProjectFolder + '/' + 'fluidExplorer.favorites'
        if os.path.exists(file_favorites):
            self.fs_watcher_favorites = QtCore.QFileSystemWatcher([file_favorites])
            self.fs_watcher_favorites.fileChanged['QString'].connect(self.file_favorites_changed)

        # favorites: fluidExplorer.currentselection
        file_selection = self.selectedProjectFolder + '/' + 'fluidExplorer.currentselection'
        if os.path.exists(file_favorites):
            self.fs_watcher_selection = QtCore.QFileSystemWatcher([file_selection])
            self.fs_watcher_selection.fileChanged['QString'].connect(self.file_selection_changed)

    def file_favorites_changed(self):
        self.initComboBoxSimulations(self.projectSettings)

    def file_selection_changed(self):
        seletion_index = ProjectDetailsViewUtils.get_selection_from_file(self.selectedProjectFolder)
        seletion_index_cb = seletion_index + 1

        if seletion_index_cb <= self.ui.comboBox_simulations.count():
            if self.ui.comboBox_simulations.currentIndex() != seletion_index_cb:
                self.ui.comboBox_simulations.setCurrentIndex(seletion_index_cb)
        else:
            if self.ui.comboBox_simulations.currentIndex() != 0:
                self.ui.comboBox_simulations.setCurrentIndex(0)

    # - Event handlers -
    @QtCore.Slot()
    def applyCacheClicked(self):
        # self.lgr.info('Apply Cache clicked')

        # Check if correct scene is opened
        currentSceneName = cmds.file(q=True, sceneName=True)
        if self.selectedProjectFolder[len(self.selectedProjectFolder)-1] == '/':
            self.selectedProjectFolder = self.selectedProjectFolder[0:len(self.selectedProjectFolder)-1]
        project_file = self.selectedProjectFolder + '/' + 'fluid_simulation_scene.mb'

        sceneFromConfigFile = project_file
        isSameScene = ProjectDetailsViewUtils.checkIfCorrectSceneIsOpened(currentSceneName, sceneFromConfigFile)

        if not isSameScene:
            strError = 'Please open the correct Maya scene first!\nPath: ' + sceneFromConfigFile
            self.lgr.warning('Please open the correct Maya scene first! Path: %s', sceneFromConfigFile)
            self.showMessageBox(strError, 'warning')
            return

        # Same scene ...
        currentIndex = self.ui.comboBox_simulations.currentIndex()
        if currentIndex >= 1:
            self.PathToXMLCache = self.hashMapToXMLProjectFile[currentIndex-1]
            if self.PathToXMLCache == self.currentAnimationLoaded:
                # Do not load the cache which is already loaded! -> pass
                cmds.select(self.projectSettings.fluidContainerName, r=True)
                pass
            else:
                self.lgr.info('Load cache file: %s', self.PathToXMLCache)
                self.currentAnimationLoaded = self.PathToXMLCache

                # Set animation start and edn time
                canSetTime = ProjectDetailsViewUtils.setAnimationStartEndTime(self.projectSettings.animationStartTime, self.projectSettings.animationEndTime)
                if not canSetTime:
                    self.lgr.warning('Cannot set the start / end time of the animation')
                    self.showMessageBox('Cannot set the start / end time of the animation.', 'warning')

                # Load cache file
                try:
                    LoadFluidCacheFile.applyCacheFile(self.PathToXMLCache, self.projectSettings.fluidContainerName)
                except Exception as e:
                    self.lgr.error('%s', e.message)
                    self.showMessageBox(e.message, 'critical')

            # Set the values
            ProjectDetailsViewUtils.applyValuesFromXMLFile(self.PathToXMLCache, self.projectSettings.fluidContainerName)

    @QtCore.Slot()
    def exploreSimulationsClicked(self):
        self.lgr.info('Explore simulations')

        # Check if correct scene is opened
        currentSceneName = cmds.file(q=True, sceneName=True)
        if self.selectedProjectFolder[len(self.selectedProjectFolder)-1] == '/':
            self.selectedProjectFolder = self.selectedProjectFolder[0:len(self.selectedProjectFolder)-1]
        project_file = self.selectedProjectFolder + '/' + 'fluid_simulation_scene.mb'

        sceneFromConfigFile = project_file
        isSameScene = ProjectDetailsViewUtils.checkIfCorrectSceneIsOpened(currentSceneName, sceneFromConfigFile)

        if not isSameScene:
            strError = 'Please open the correct Maya scene first!\nPath: ' + sceneFromConfigFile
            self.lgr.warning('Please open the correct Maya scene first! Path: %s', sceneFromConfigFile)
            self.showMessageBox(strError, 'warning')
            return

        # Check if xml files are available
        if not len(self.hashMapToXMLProjectFile) == int(self.projectSettings.numberOfSimulations): #+ 1:
            self.lgr.warning('Number of XML cache files is not correct')
            errorMsg = "The number of .xml cache files is not correct!\nPlease check the project folder or create the simulation again."
            self.showMessageBox(errorMsg, 'warning')
            return

        # Check if fluidexplorer app is running
        isFXProcessRunning = ProjectDetailsViewUtils.checkIfProcessIsRunning(self.FLUIDEXPLORER_APP_NAME)
        if isFXProcessRunning:
            return

        # Check if app path exists
        pathToFXAPP = self.externalCall.pathToFluidExplorer + '/' + self.externalCall.fluidExplorerCmd
        if not os.path.exists(os.path.abspath(pathToFXAPP)):
            self.lgr.error('Cannot find the Fluid Explorer application executable')
            errorMsg = "Cannot find the Fluid Explorer application executable!" + "\n" + "Please check if the executable file is available."
            self.showMessageBox(errorMsg, 'warning')
            return

        # Check th folder structure
        if ProjectDetailsViewUtils.check_project_folder_structure(self.selectedProjectFolder, self.projectSettings, self.hashMapToXMLProjectFile):

            # Show a warning if cuda version check is not successfully
            # [nvcc_success, output] = ProjectDetailsViewUtils.check_if_cuda_compiler_available()
            # if not nvcc_success:
            # errorText = "The graphics driver could not find compatible graphics hardware!\nPlease check if CUDA is supported on your machine.\n\nThe aplication might not work correctly."
            # self.showMessageBox(errorText, 'warning')
            # self.lgr.warning('CUDA version check was no successfully. Result of nvcc -V: %s', output)

            if self.externalCall.isArgumentCorrect:
                #
                # Start the fluid explorer
                #
                exec_res = self.execute_fx(self.externalCall)
                if not exec_res:
                    errorMsg = "Cannot open the Fluid Explorer application!\nSee the console output for details."
                    self.showMessageBox(errorMsg, 'critical')
                    return
            else:
                self.lgr.error('External call - argument is not correct. Please check if path exists: %s', self.externalCall.fluidExplorerArgs)
                errorMsg = "Cannot start the Fluid Explorer application! The arguments are not valid.\nSee console output for details."
                self.showMessageBox(errorMsg, 'critical')


        else:
            self.lgr.error('Project structure is not correct. Check the folder numbers')
            errorMsg = "The project structure is not correct!\nPlease check the project folder or create the simulation again."
            self.showMessageBox(errorMsg, 'warning')
            return

        """
        #
        # Threading
        #
        # Run the worker thread
        if self.workThread:
            self.workThread.stop()

            # Start thread again
            self.workThread = WorkThread(self.externalCall)
            self.connect(self.workThread, QtCore.SIGNAL("update(QString)"), self.updateIndexFromThread)
            self.workThread.start()

        else:
            # Start thread
            self.workThread = WorkThread(self.externalCall)
            self.connect(self.workThread, QtCore.SIGNAL("update(QString)"), self.updateIndexFromThread)
            self.workThread.start()
        #
        #
        """

    @QtCore.Slot()
    def checkBoxPreviewValueChanged(self, state):
        # State starts with 0
        if self.ui.checkBox_showPreview.checkState() == QtCore.Qt.Checked:
            # active
            self.setWindowHeightWithPreview()
            self.playAnimation(self.ui.comboBox_simulations.currentIndex())
        elif self.ui.checkBox_showPreview.checkState() == QtCore.Qt.Unchecked:
            # not active
            self.setWindowHeightWithoutPreview()
            self.movie.stop()

    @QtCore.Slot()
    def comboBoxSimulationsIndexChanged(self, index):
        if self.ui.comboBox_simulations.count() == 0:
            return

        if self.ui.checkBox_showPreview.checkState() == QtCore.Qt.Checked:
            currentIndex = self.ui.comboBox_simulations.currentIndex()

            # Play animation
            self.playAnimation(currentIndex)

        # Info text
        if self.ui.comboBox_simulations.currentIndex() == 0:
            txt = "File: -"
        else:
            [dirProjectName, dirNumberName, cacheXMLName] = self.getCacheNameFromPath(str(self.hashMapToXMLProjectFile[(self.ui.comboBox_simulations.currentIndex()-1)]))
            if len(cacheXMLName) == 0:
                txt = "File: -"
            else:
                txt = "File: " + str(dirProjectName) + '/' + str(dirNumberName) + '/' + str(cacheXMLName) # Do not show the entire path

        self.ui.label_fluidContainer_2.setText(txt)

        # Set tooltip
        if self.ui.comboBox_simulations.currentIndex() == 0:
            self.ui.label_fluidContainer_2.setToolTip("")
        else:
            space = " "
            tooltip = str(self.hashMapToXMLProjectFile[(self.ui.comboBox_simulations.currentIndex())-1]) + space
            self.ui.label_fluidContainer_2.setToolTip(tooltip)

    @QtCore.Slot()
    def helpButtonClicked(self):
        webbrowser.open("http://fluidexplorer.cs.univie.ac.at/helpsection.php#load_simulation", new=1)

    @QtCore.Slot()
    def frameChangedHandler(self, frameNumber):
        pass
    # - Event handlers end -

    # - Help functions -
    def execute_fx(self, externalCallSettings):

        pathToFXApp = externalCallSettings.pathToFluidExplorer
        cmdFXAPP = externalCallSettings.fluidExplorerCmd
        cmdFXArg = externalCallSettings.fluidExplorerArgs

        # --------------------------------------------------------------------------------------------------------------
        # Version 1 - Without console output
        # --------------------------------------------------------------------------------------------------------------
        currentDir = os.getcwd()
        try:
            os.chdir(pathToFXApp)
            program_name = cmdFXAPP
            arguments = [str(cmdFXArg[0]), str(cmdFXArg[1]), str(cmdFXArg[2]), str(cmdFXArg[3])]

            command = [program_name]
            command.extend(arguments)
            output = subprocess.Popen(command, shell=True)

            self.lgr.info('External application started')
            self.lgr.info('External call (path): %s', pathToFXApp)
            self.lgr.info('External call (cmd): %s', cmdFXAPP)
            self.lgr.info('External call (args): %s', cmdFXArg)
        except Exception as e:
            self.lgr.error('Critical: Cannot execute Fluid Fxplorer app. Details: %s', e.message)
            return False
        finally:
            os.chdir(currentDir)
            subprocess._cleanup()
            return True
        # --------------------------------------------------------------------------------------------------------------

    def setLineEditEnabledAndReadOnly(self, component):
        component.setStyleSheet(self.getStyle())
        component.setReadOnly(True)

    def changeHLineStyle(self):
        self.ui.line_1.setGeometry(20, 40, 300, 1)
        self.ui.line_2.setGeometry(20, 240, 300, 1)
        self.ui.line_3.setGeometry(20, 409, 300, 1)
        self.ui.line_1.setLineWidth(1)
        self.ui.line_2.setLineWidth(1)
        self.ui.line_3.setLineWidth(1)
        self.ui.line_1.setStyleSheet("QFrame{background-color: gray;}")
        self.ui.line_2.setStyleSheet("QFrame{background-color: gray;}")
        self.ui.line_3.setStyleSheet("QFrame{background-color: gray;}")

    def getStyle(self):
        styleEnabled = ("QLineEdit:read-only{"
            "font-size: 12px;"
            "/*font-weight: bold;*/"
            "}"
            )
        return styleEnabled

    def readProjectProperties(self, pathToXMLFile):
        xmReader = ProjectDetailsViewUtils()

        projectSettings = None
        try:
            projectSettings = xmReader.getProjectSubSettings(pathToXMLFile)
            # Set the path from the selected file (override)
            # Do not read projec path from setting file
            projectSettings.projectPath = self.selectedProjectFolder
            projectSettings.mayaFilePath = ""

        except Exception as e:
            errorText = "An error occured while loading the project configuration file!\nDetails: " + str(e.message)
            self.showMessageBox(errorText, 'critical')
            self.lgr.error('Loading the project configuration file: %s', errorText)
            return None

        return projectSettings

    def showMessageBox(self, errorMsg, type):
        msgBox = QtWidgets.QMessageBox(self)
        msgBox.setText(errorMsg)
        if type == 'critical':
            msgBox.setWindowTitle("Error")
            msgBox.setIcon(QtWidgets.QMessageBox.Critical)
        if type == 'warning':
            msgBox.setWindowTitle("Warning")
            msgBox.setIcon(QtWidgets.QMessageBox.Warning)

        msgBox.setStyleSheet(DefaultUIParameters.buttonStyleBold)
        msgBox.exec_()

    def closeEvent(self, event):
        """
        # Stop thread if running
        if self.workThread:
            self.workThread.stop()
            # self.workThread.terminate()
        """
        FluidExplorerUtils.killProcess(self.FLUIDEXPLORER_APP_NAME)

    def getCacheNameFromPath(self, text):
        text = text + "/"

        if text:
            lastChar = text[len(text)-1]
            if lastChar == '/' or '\\':
                text = text[0:len(text)-1]

            elements = text.split("/")
            if len(elements) == 0:
                return ""
            else:
                return [elements[len(elements)-3], elements[len(elements)-2], elements[len(elements)-1]]

    """
    # Not in use -> see threading
    def updateIndexFromThread(self, text):
        self.lgr.info('Update index: %s', text)

        # If the thread sends am error -> stop
        if text == "ERROR":
            self.lgr.error('Cannot execute the FluidExplorer application')
            self.showMessageBox('Cannot execute the FluidExplorer application!\nSee editor output for details.', 'critical')
            return

        # Else, update the combobox
        try:
            intIndex = int(text)
        except:
            intIndex = 0
        finally:
            if intIndex > 2:
                self.ui.comboBox_simulations.setCurrentIndex(0)
                self.update()
            else:
                self.ui.comboBox_simulations.setCurrentIndex(1)
                self.update()
    """
    # - Help functions end -

    # ScriptJob
    def FXScriptJob(self):
            import maya.cmds as cmds
            Job1 = cmds.scriptJob(event=['deleteAll', self.ScriptJobMethodCall])        # new file
            Job2 = cmds.scriptJob(event=['quitApplication', self.ScriptJobMethodCall])

    def ScriptJobMethodCall(self):
        # Check if maya is open and close it
        FluidExplorerUtils.killProcess(self.FLUIDEXPLORER_APP_NAME)
