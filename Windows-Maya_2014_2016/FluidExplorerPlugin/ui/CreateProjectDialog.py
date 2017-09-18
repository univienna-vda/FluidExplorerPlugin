import os
import struct
import re
import platform
import webbrowser
import errno
import time
import itertools

from PySide import QtGui
from PySide import QtCore
import maya.cmds as cmds
import maya.mel as mel

from CreateProjectDialogUI import Ui_CreateProjectDialog
from Utils.DefaultUIValues import DefaultUIParameters
from FileOpenDialog import FileOpenDialog
from ChooseCameraDialog import ChooseCameraDialog
from MayaCacheCmdSettings import MayaCacheCmdSettings
from Utils import FluidExplorerUtils
from Utils.MayaUiDefaultValues import MayaUiDefaultValues
from Utils.MayaCmds.MayaCacheCmd import MayaCacheCmdString
from Utils.MayaCmds.MayaFunctions import MayaFunctionUtils
from ParamterTab import ParameterTab
from Utils.RangeSliderSpan import FluidValueSampler
from Utils.XmlFileWriter import XmlFileWriter
from Utils.GifCreatpr import GifCreator
import logging

# For Tests
from Test.Test import Test


class CreateProjectDialog(QtGui.QDialog):

    CLICK_FLAG_CAM_PV = True
    CLICK_FLAG_CAM_VC = False
    CLICK_FLAG_CAM_SPH = False  # CLICK_FLAG_CAM_SPH is the flag for the custom camera
    CLICK_FLAG_CAM_ROT = False
    choosenCamera = None

    FLUID_EXPLORER_URL = DefaultUIParameters.URL
    DIALOG_STYLE_SHEET = DefaultUIParameters.buttonStyleBold

    def __init__(self, args, fluidName, transformNode):

        QtGui.QDialog.__init__(self, args)

        # Logger
        self.lgr = logging.getLogger('FluidExplorerPlugin')

        self.lgr.info("Create animation - fluid name: %s", format(fluidName))

        # Getselected container name
        self.fluidName = fluidName

        # Store project settings
        self.simulationSettings = MayaCacheCmdSettings()
        self.simulationSettings.fluidBoxName = fluidName

        # Create the user interface from the ui file
        self.ui = Ui_CreateProjectDialog()
        self.ui.setupUi(self)

        # Store the selected fluid container name
        self.setFluidName(fluidName)
        self.transformNode = transformNode

        # Parameter Tab (second tab)
        self.tabParamtersObj = None
        self.tabParamters = None
        self.tabParameterValuesFirstOpened = False
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.tabWidget.update()

        # FFmpeg path
        self.ffmpegpath = self.getFFmpegPath()

        # FluidExplorer path
        self.fluidExplorerPath = self.getFluidExplorerPath()

        # Calculation of time
        self.isTimeCalculated = False
        self.time_Caching = 0
        self.time_Renering = 0
        self.time_GIF = 0
        self.progressSteps = 0

        # Tab order of first view
        self.setTabOrder(self.ui.lineEdit_SimulationName, self.ui.pushButtonCreateSimulation)
        self.setTabOrder(self.ui.pushButtonCreateSimulation, self.ui.label_2)

        # Initialize components
        self.createConnections()
        self.setupComponents()

        # Centre the main window
        # self.centre()
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowStaysOnTopHint)

        # //////////////////////////////////////////////////////////////////////////////////////////////////////////////
        # //////////////////////////////////////////////////////////////////////////////////////////////////////////////
        # Only for testing
        # self.runTests(self.workDirPath)
        # self.setAnimationStartEndTime()
        # //////////////////////////////////////////////////////////////////////////////////////////////////////////////
        # //////////////////////////////////////////////////////////////////////////////////////////////////////////////

        # Delete files from time calculation
        self.deleteFilesFromOutputFolder()

        # Select the transform node
        cmds.select(self.transformNode, r=True)

    def centre(self):
        # The dialog window is shifted to the right that the maya question dialogs are not hidden
        screen = QtGui.QDesktopWidget().screenGeometry()
        mysize = self.geometry()
        hpos = (screen.width() - mysize.width()) / 2
        vpos = (screen.height() - mysize.height()) / 2

        self.move(hpos + (mysize.width() / 3), vpos)

    def setFluidName(self, name):
        self.fluidName = name

    def setupComponents(self):

        self.ui.tabWidget.removeTab(1)
        self.setAnimationStartEndTime()

        # Set the help icon
        icon_help = QtGui.QIcon(QtGui.QPixmap(':/help_icon_orange.png'))
        self.ui.pushButtonNewPrjHelp.setIcon(icon_help)

        # Default simulation name
        self.ui.lineEdit_SimulationName.setText(DefaultUIParameters.DEF_SIMULATION_NAME)

        # Set the default output directory
        self.workDirPath = cmds.workspace(q=True, dir=True)
        self.lgr.info("Default workspace / output directory: %s", self.workDirPath)

        # self.workDirPath = "E:/TMP"

        if platform.system() == "Windows":
            self.workDirPath = self.workDirPath.replace("/", "\\")
        self.ui.lineEdit_ProjPath.setText(self.workDirPath)

        self.ui.pushButtonCreateSimulation.setStyleSheet(DefaultUIParameters.buttonStyleBold)
        self.ui.spinBox_rotDeg.setValue(DefaultUIParameters.DEF_SPIN_ROT)
        self.ui.spinBox_rotDeg.setMinimum(DefaultUIParameters.DEF_SPIN_ROT_MIN)
        self.ui.spinBox_rotDeg.setMaximum(DefaultUIParameters.DEF_SPIN_ROT_MAX)
        self.ui.label.setEnabled(False)
        self.ui.spinBox_rotDeg.setEnabled(False)

        self.ui.label_2.setStyleSheet("font-weight: bold;")
        self.ui.label_3.setStyleSheet("font-weight: bold;")
        self.ui.label_4.setStyleSheet("font-weight: bold;")
        self.ui.label_5.setStyleSheet("font-weight: bold;")
        self.ui.pushButtonCreateSimulation.setStyleSheet("font-weight: bold;")
        self.ui.groupBoxCameras.setStyleSheet("QGroupBox{font-weight: bold;}")

        self.setFluidNameLabel()
        self.initCamButtons()
        self.initSliderValues()
        self.addParamterTab()

    def setFluidNameLabel(self):
        self.ui.labelFluidBox_Value.setText(self.simulationSettings.fluidBoxName)

    def addParamterTab(self):
        self.tabParamtersObj = ParameterTab(self.simulationSettings.fluidBoxName)
        self.tabParamters = self.tabParamtersObj.getTab()
        self.ui.tabWidget.addTab(self.tabParamters, "Fluid Properties")

    def createConnections(self):
        self.ui.pushButtonNewPrjHelp.clicked.connect(self.buttonHelpCreateProj_Event)
        self.ui.pushButtonBrowse.clicked.connect(self.buttonBrowse_Event)
        self.ui.pushButtonCreateSimulation.clicked.connect(self.buttonCreateSimulation_Event)
        self.ui.horizontalSlider_numberSeq.valueChanged[int].connect(self.sliderNumberSequences_Event)
        self.ui.lineEdit_numberSeq.textChanged.connect(self.lineEdit_numberSeq_Event)
        self.ui.lineEdit_numberSeq.editingFinished.connect(self.lineEdit_numberSeq_EditFinished)
        self.ui.spinBox_rotDeg.valueChanged.connect(self.spinBoxRot_Event)
        self.ui.pushButtonBrowse_CalculateTime.clicked.connect(self.calculateTimeClicked)
        self.ui.lineEdit_numberSeq.editingFinished.connect(self.checkNumSimIsOne_Event)

    def setAnimationStartEndTime(self):
        uiStatus = MayaUiDefaultValues()
        uiStatus.getAnimationStartEnd()
        begin = uiStatus.animationMinTime
        end = uiStatus.animationEndTime

        txt = str(begin) + " / " + str(end)
        numberOfFrames = (end - begin) + 1

        self.ui.labelAnimationTimeStartEnd.setText(txt)
        self.simulationSettings.animationStartTime = begin
        self.simulationSettings.animationEndTime = end
        self.simulationSettings.numberOfFrames = int(numberOfFrames)

    @QtCore.Slot()
    def buttonHelpCreateProj_Event(self):
        webbrowser.open(self.FLUID_EXPLORER_URL, new=1)

    @QtCore.Slot()
    def buttonBrowse_Event(self):
        self.fileDialog = FileOpenDialog(self)
        choosenDir = self.fileDialog.openDirDialogQuick()

        if choosenDir is not None:
            choosenDir = choosenDir + "/"
            if (platform.system() == "Windows"):
                choosenDirNew = choosenDir.replace("/","\\")
            else:
                choosenDirNew = choosenDir

            self.ui.lineEdit_ProjPath.setText(choosenDirNew)

    @QtCore.Slot()
    def buttonCreateSimulation_Event(self):

        self.lgr.info('#')
        self.lgr.info("Simulation started")
        self.lgr.info('#')

        # If the fluid container is incorrect, the application closes
        if not FluidExplorerUtils.FluidExplorerUtils.containerIsCorrect(self.fluidName):
            self.showMessageBox('Error - Create Sumulation','Cannot select fluid attributes of of the selected container. Simulation stopped!\nFor more information please see the editor log.', 'warning')
            self.close()
            return

        # First of all check of ffmpeg and fluidExplorer executable files are ok
        ffmpegIsOk = FluidExplorerUtils.FluidExplorerUtils.checkIfFFmpgeIsExectuable(self.ffmpegpath)
        fluidExplorerIsOk = FluidExplorerUtils.FluidExplorerUtils.checkIfFluidExplorerIsExectuable(self.fluidExplorerPath)

        if not ffmpegIsOk:
            self.showMessageBox('Warning - Create Sumulation','Cannot execute FFmpeg. Simulation stopped!\nFor more information please see the editor log.', 'warning')
            self.close()
            return

        if not fluidExplorerIsOk:
            self.showMessageBox('Warning - Create Sumulation','Cannot execute Fluid Explorer application. Simulation stopped!\nFor more information please see the editor log.', 'warning')
            self.close()
            return

        #
        # Create project and all contents
        #

        self.currentMayaSceneName = ""
        pathName = self.ui.lineEdit_ProjPath.text()
        projName = self.ui.lineEdit_SimulationName.text()

        [pathOk, simulationNameAbsolut] = self.checkProjectPathOk(pathName, projName)
        if not pathOk:
            return
        else:
            # Save a copy of the current scene in the project folder
            # Student version -> Save dialog has to be confirmed
            self.currentMayaSceneName = cmds.file(q=True, sn=True)

            saveFileSuccessfully = True
            try:
                tmpMayaFilePath = self.simulationSettings.outputPath + "/fluid_simulation_scene.mb"
                cmds.file(rename=tmpMayaFilePath)
                dialogRes = cmds.file(save=True)
                self.simulationSettings.simulationNameMB = tmpMayaFilePath
            except:
                saveFileSuccessfully = False
                if len(self.currentMayaSceneName) == 0:
                    self.currentMayaSceneName = self.currentMayaSceneName + "untitled"

                cmds.file(rename=self.currentMayaSceneName) # Old name
                os.rmdir(self.simulationSettings.outputPath)

        if not saveFileSuccessfully:
            self.lgr.warning("Maya file not saved. Simulation stoped")
            self.close()
            return

        # Hide the dialog -> support minimize window
        self.hide()

        # Store information about the current scene
        self.simulationSettings.fluidBoxName = self.fluidName
        self.simulationSettings.numberSamples = self.ui.horizontalSlider_numberSeq.value()
        self.setCameraButtonSelection()

        # Minimum of samples = 2
        if self.simulationSettings.numberSamples == 1:
            self.simulationSettings.numberSamples = 2

        # Get current spans: Stores the min and max slider vqalues. e.g.: currentSpans.velocitySwirl_Span
        currentSpans = self.tabParamtersObj.getSelectedValuesFromSlider()

        # Get a list of all the sliders which were used and also save min and max values
        concatenatedString = ""
        delimiter_1 = ','
        delimiter_2 = ';'
        for iIndex in range(0, len(currentSpans.usedSpansMinMax)):
            str_min = str(round(currentSpans.usedSpansMinMax[iIndex].min, 1))
            str_max = str(round(currentSpans.usedSpansMinMax[iIndex].max, 1))
            str_val = str(currentSpans.usedSpansMinMax[iIndex].name)
            str_val_name_pattern = str(currentSpans.usedSpansMinMax[iIndex].nameForPattern)

            tmp = str_val + delimiter_1 + str_min + delimiter_1 + str_max + delimiter_1 + str_val_name_pattern
            concatenatedString += (tmp + delimiter_2)

        # e.g. Gravity,0.0,10.0,gravity;Viscosity,0.0,1.0,viscosity;Density Scale,0.0,2.0,densityScale
        concatenatedString = concatenatedString[0:len(concatenatedString)-1]   # delete the last delimeter
        self.simulationSettings.sampledValuesString = concatenatedString

        # Show setting parameters in console and create xml file
        MayaCacheCmdSettings.printValues(self.simulationSettings)
        fileCreated = self.createProjectSettingsFile(simulationNameAbsolut)
        if not fileCreated:
            self.show()
            self.lgr.error('Could not create settings file. Simulation stoped')
            self.showMessageBox('Error - Create Sumulation','An error occurred while the project file was created!\nFor more information please see the editor log.', 'critical')
            self.close()
            return

        # No return until here: Project folder and settings file were created ...

        # --------------------------------------------------------------------------------------------------------------
        # Generate a set of N cache commands and a set of N random samples
        # --------------------------------------------------------------------------------------------------------------

        # Current spans stores the min and max slider vqalues. e.g.: currentSpans.velocitySwirl_Span
        # currentSpans = self.tabParamtersObj.getSelectedValuesFromSlider()
        self.lgr.info("Create cache commands and random values")

        randomSamplesList = list()
        cacheCmdList = list()
        for iIndex in range(0, self.simulationSettings.numberSamples):

            # Create random samples
            fluidValueSampler = FluidValueSampler(currentSpans)
            fluidValueSampler.setSldierRangeValues()
            randomSamples = fluidValueSampler.getSampleSet()
            randomSamplesList.append(randomSamples)
            del fluidValueSampler
            del randomSamples

            # Create commands
            cacheName = self.simulationSettings.fluidBoxName + "_" + str(iIndex)
            cacheCmd = MayaCacheCmdString()
            pathOut = self.simulationSettings.outputPath + "/" + str(iIndex)
            cacheCmd.setRenderSettingsFromMaya(self.simulationSettings.animationStartTime, self.simulationSettings.animationEndTime, pathOut, cacheName)
            cmdStr = cacheCmd.getCacheCommandString()
            self.lgr.info("Cache command: %s", cmdStr)
            cacheCmdList.append(cmdStr)
            del cacheCmd

        self.simulationSettings.createCacheCommandString = cacheCmdList
        self.simulationSettings.randomSliderSamples = randomSamplesList

        """
        # Print cache command and random values
        print "\nCache Commands:\n"
        for iIndex in range(0, self.simulationSettings.numberSamples):
            print("[ Index: ", iIndex, " ]")
            print("   Command: ", self.simulationSettings.createCacheCommandString[iIndex])
            print("   velociySwirl: ", self.simulationSettings.randomSliderSamples[iIndex].velocitySwirl)
            print "\n"
        print "\n"
        """

        # Lock the node
        FluidExplorerUtils.FluidExplorerUtils.lockNodes(self.fluidName, self.transformNode)

        # --------------------------------------------------------------------------------------------------------------
        # Create the cache and render the images
        # --------------------------------------------------------------------------------------------------------------

        self.mayaCallObject = MayaFunctionUtils()
        self.progressSteps = (self.getNumberOfActiveCameras() + 1) * self.simulationSettings.numberSamples

        # Progress bar in maya toolbar - start
        self.progressSteps = (self.getNumberOfActiveCameras() + 1) * self.simulationSettings.numberSamples
        step_end = self.progressSteps
        gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')
        cmds.progressBar( gMainProgressBar,
                        edit=True,
                        beginProgress=True,
                        isInterruptable=False,
                        status='"Creating simulations ...',
                        maxValue=step_end )

        # Walk through the frames of the animation (timeline)
        self.render_forward()

        renderedImage = list()
        fluidIndex = 0
        progressIndex = 0
        for lCmd, lSamples in itertools.izip(self.simulationSettings.createCacheCommandString, self.simulationSettings.randomSliderSamples):
            """
            :type lSamples : MayaCacheCmd
            """

            # Progress bar - start
            progressBarText = "Creating simulation " + str(fluidIndex+1) + " / " + str(self.simulationSettings.numberSamples)
            # progress.setLabelText(progressBarText)
            cmds.progressBar(gMainProgressBar, edit=True, step=0, status=progressBarText)

            # 1. Set the values
            self.mayaCallObject.setSampledValue(self.simulationSettings.fluidBoxName, lSamples)

            # 2. Call maya cache function
            try:
                self.lgr.info("Caching started for index %s", fluidIndex)
                self.mayaCallObject.createFluid(lCmd, None)
            except Exception as e:
                self.show()
                self.showMessageBox('Error - Create Cache','An error occurred while the cache files were created!\nFor more information please see the editor log.', 'critical')
                # progress.close()
                cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
                self.close()
                return

            # Progress bar - update
            progressIndex += 1
            # progress.setValue(progressIndex)
            cmds.progressBar(gMainProgressBar, edit=True, step=1, status=progressBarText)

            # 3. Create the images
            if self.simulationSettings.imageView:
                self.mayaCallObject.changeToPerspCam()
                self.mayaCallObject.viewFromCamPosition('PERSPECTIVE', self.simulationSettings.fluidBoxName)
            if self.simulationSettings.imageView:
                try:
                    self.lgr.info("Rendering images started for index %s", fluidIndex)
                    [progressIndexUpdated, renderedImageSubList] = self.mayaCallObject.renderImagesFromCameras(
                        self.simulationSettings, fluidIndex, gMainProgressBar, progressIndex)
                except Exception as e:
                    self.show()
                    self.showMessageBox('Error - Render Images','An error occurred while the images were rendered!\nFor more information please see the editor log.', 'critical')
                    # progress.close()
                    cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
                    self.close()
                    return

                progressIndex = progressIndexUpdated
                renderedImage.append(renderedImageSubList)

            fluidIndex += 1

        if self.simulationSettings.imageView:
            self.mayaCallObject.changeToPerspCam()
            self.mayaCallObject.viewFromCamPosition('PERSPECTIVE', self.simulationSettings.fluidBoxName)

        self.mayaCallObject = None

        # Progress bar - close
        # progress.close()
        cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)

        # --------------------------------------------------------------------------------------------------------------

        # --------------------------------------------------------------------------------------------------------------
        # Create GIF images
        # --------------------------------------------------------------------------------------------------------------
        if self.simulationSettings.imageView:
            self.lgr.info("Creating GIF animations")

            """
            # Old progress bar
            progress = QtGui.QProgressDialog("", None, 0, self.progressSteps, self)
            progress.setWindowTitle("Please wait ...")
            progress.setMinimumDuration(0)
            progress.setMaximum(len(renderedImage))
            progress.setLabelText("<b>Creating GIF animations ...</b>")
            progress.show()
            progressIndex = 0
            """

            # Progress bar - start
            gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')
            cmds.progressBar( gMainProgressBar,
                            edit=True,
                            beginProgress=True,
                            isInterruptable=False,
                            status='"Creating GIF animations ...',
                            maxValue=len(renderedImage) )

            gifIndex = 0
            for idx, val in enumerate(renderedImage):
                tmpList = val
                for val in tmpList:
                    progressIndex += 1
                    # progress.setValue(progressIndex)

                    # Progress bar - update
                    txt = "Creating GIF animation" + " " + str(gifIndex+1) + " / " + str(len(renderedImage))
                    cmds.progressBar(gMainProgressBar, edit=True, step=1, status=txt)

                    # Store the path to the rendered images
                    directoryImagesDir = val
                    outputGifFileDir = val
                    outputGifFileName = 'animation.gif'
                    self.gifImageCreator = GifCreator()
                    start_time = self.simulationSettings.animationStartTime

                    isFFmpegExecutable = self.gifImageCreator.createGifFromImages(self.ffmpegpath, directoryImagesDir,
                                                                                  outputGifFileDir, outputGifFileName,
                                                                                  start_time, fps=25, gifOptimization=25)

                    if not isFFmpegExecutable:
                        self.show()
                        self.showMessageBox('Error - Create Animations','An error occurred while the animations were created!\nFor more information please see the editor log.', 'critical')
                        # progress.close()
                        self.close()
                        cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
                        return

                gifIndex += 1
                self.lgr.info('GIF Animation "%s" created', str(gifIndex))

            # Progress bar - close
            # progress.close()
            cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
        # --------------------------------------------------------------------------------------------------------------

        # Copy settings file to project folder
        pathToSettingsFile = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + '/Resources/settings_file/fluidExplorer.settings')
        copySettingsFileTo = os.path.abspath(self.simulationSettings.outputPath + '/fluidExplorer.settings')
        FluidExplorerUtils.FluidExplorerUtils.copySettingsFile(pathToSettingsFile, copySettingsFileTo)

        # Show the dialog again
        # self.show()

        text = "Simulations successfully created." + "\n\nProject Path: " + self.simulationSettings.outputPath + "" + "\nProject File: " + self.simulationSettings.simulationNameMB
        self.showMessageBox_centered("Information", text, 'information')

        # Delete render window
        FluidExplorerUtils.FluidExplorerUtils.deleteRenderWindow()

        # Select the transform node
        cmds.select(self.transformNode, r=True)

        self.lgr.info('#')
        self.lgr.info("# Simulation successfully created: %s", self.simulationSettings.outputPath)
        self.lgr.info('#')

        # Close window
        # self.close()

    @QtCore.Slot()
    def lineEdit_numberSeq_EditFinished(self):
        if not self.ui.lineEdit_numberSeq.text():
            self.ui.lineEdit_numberSeq.setText(str(DefaultUIParameters.DEF_NUMBER_SEQUENCES))

    @QtCore.Slot()
    def sliderNumberSequences_Event(self):
        tmp = str(self.ui.horizontalSlider_numberSeq.value())
        self.ui.lineEdit_numberSeq.setText(tmp)

        self.setTime()

    @QtCore.Slot()
    def lineEdit_numberSeq_Event(self):
        numberSeq = self.ui.lineEdit_numberSeq.text()
        try:
            val = int(numberSeq)
            #if int(numberSeq) < DefaultUIParameters.DEF_NUMBER_SEQUENCES_MIN :
            #    self.ui.lineEdit_numberSeq.setText(str(DefaultUIParameters.DEF_NUMBER_SEQUENCES_MIN))
            #    self.ui.horizontalSlider_numberSeq.setValue(DefaultUIParameters.DEF_NUMBER_SEQUENCES_MIN)
            #    self.ui.horizontalSlider_numberSeq.update()
            if int(numberSeq) == 0:
                self.ui.lineEdit_numberSeq.setText(str(DefaultUIParameters.DEF_NUMBER_SEQUENCES_MIN))
                self.ui.horizontalSlider_numberSeq.setValue(DefaultUIParameters.DEF_NUMBER_SEQUENCES_MIN)
                self.ui.horizontalSlider_numberSeq.update()
            elif int(numberSeq) > DefaultUIParameters.DEF_NUMBER_SEQUENCES_MAX:
                self.ui.lineEdit_numberSeq.setText(str(DefaultUIParameters.DEF_NUMBER_SEQUENCES_MAX))
                self.ui.horizontalSlider_numberSeq.setValue(DefaultUIParameters.DEF_NUMBER_SEQUENCES_MAX)
                self.ui.horizontalSlider_numberSeq.update()
            else:
                self.ui.horizontalSlider_numberSeq.setValue(val)

        except ValueError:
            if numberSeq == "":
                pass
            else:
                self.ui.lineEdit_numberSeq.setText(str(DefaultUIParameters.DEF_NUMBER_SEQUENCES))

    @QtCore.Slot()
    def pushButtonCamPV_Event(self):
        flag = self.CLICK_FLAG_CAM_PV
        if not flag:
            self.ui.pushButton_CamPV.setStyleSheet(DefaultUIParameters.StyleSheet_Button_On)
            self.CLICK_FLAG_CAM_PV = True
        elif flag:
            self.ui.pushButton_CamPV.setStyleSheet(DefaultUIParameters.StyleSheet_Button_Off)
            self.CLICK_FLAG_CAM_PV = False

        self.setTime()

    @QtCore.Slot()
    def pushButtonCamVC_Event(self):
        flag = self.CLICK_FLAG_CAM_VC
        if not flag:
            self.ui.pushButton_CamVC.setStyleSheet(DefaultUIParameters.StyleSheet_Button_On)
            self.CLICK_FLAG_CAM_VC = True
        elif flag:
            self.ui.pushButton_CamVC.setStyleSheet(DefaultUIParameters.StyleSheet_Button_Off)
            self.CLICK_FLAG_CAM_VC = False

        self.setTime()

    @QtCore.Slot()
    def pushButtonCamSPH_Event(self):
        flag = self.CLICK_FLAG_CAM_SPH
        if not flag:
            chooseCameraDialog = ChooseCameraDialog(self)
            chooseCameraDialog.exec_()
            choosenCam = chooseCameraDialog.getChoosenCamera
            if choosenCam:
                self.ui.label_selectedCam.setText('[ ' + choosenCam + ' ]')
                self.choosenCamera = choosenCam
                self.ui.pushButton_CamSPH.setStyleSheet(DefaultUIParameters.StyleSheet_Button_On)
                self.CLICK_FLAG_CAM_SPH = True
            else:
                pass

        elif flag:
            self.ui.pushButton_CamSPH.setStyleSheet(DefaultUIParameters.StyleSheet_Button_Off)
            self.ui.label_selectedCam.setText(' ')
            self.choosenCamera = None
            self.CLICK_FLAG_CAM_SPH = False

        self.setTime()

    @QtCore.Slot()
    def pushButtonROT_Event(self):
        flag = self.CLICK_FLAG_CAM_ROT
        if not flag:
            self.ui.pushButton_ROT.setStyleSheet(DefaultUIParameters.StyleSheet_Button_On)
            self.CLICK_FLAG_CAM_ROT = True
            self.ui.spinBox_rotDeg.setEnabled(True)
            self.ui.label.setEnabled(True)
        elif flag:
            self.ui.pushButton_ROT.setStyleSheet(DefaultUIParameters.StyleSheet_Button_Off)
            self.CLICK_FLAG_CAM_ROT = False
            self.ui.spinBox_rotDeg.setEnabled(False)
            self.ui.label.setEnabled(False)

        self.setTime()

    @QtCore.Slot()
    def spinBoxRot_Event(self):
        value = int(self.ui.spinBox_rotDeg.text())

        if value < DefaultUIParameters.DEF_SPIN_ROT_MIN:
            self.ui.spinBox_rotDeg.setValue(int(DefaultUIParameters.DEF_SPIN_ROT_MIN))
        if value > DefaultUIParameters.DEF_SPIN_ROT_MAX:
            self.ui.spinBox_rotDeg.setValue(int(DefaultUIParameters.DEF_SPIN_ROT_MAX))

        self.setTime()

    def initCamButtons(self):
        self.ui.pushButton_CamPV.setIcon(QtGui.QIcon(self.tr(":/icon_cam_perspective.png")))
        self.ui.pushButton_CamPV.setStyleSheet(DefaultUIParameters.StyleSheet_Button_On)
        self.ui.pushButton_CamVC.setIcon(QtGui.QIcon(self.tr(":/icon_cam_vc.png")))
        self.ui.pushButton_CamVC.setStyleSheet(DefaultUIParameters.StyleSheet_Button_Off)
        self.ui.pushButton_CamSPH.setIcon(QtGui.QIcon(self.tr(":/icon_cam_custom.png")))
        self.ui.pushButton_CamSPH.setStyleSheet(DefaultUIParameters.StyleSheet_Button_Off)
        self.ui.pushButton_ROT.setIcon(QtGui.QIcon(self.tr(":/icon_cam_rotation.png")))
        self.ui.pushButton_ROT.setStyleSheet(DefaultUIParameters.StyleSheet_Button_Off)
        self.ui.pushButton_CamPV.clicked.connect(self.pushButtonCamPV_Event)
        self.ui.pushButton_CamVC.clicked.connect(self.pushButtonCamVC_Event)
        self.ui.pushButton_CamSPH.clicked.connect(self.pushButtonCamSPH_Event)
        self.ui.pushButton_ROT.clicked.connect(self.pushButtonROT_Event)

    def initSliderValues(self):
        self.ui.horizontalSlider_numberSeq.setMinimum(DefaultUIParameters.DEF_NUMBER_SEQUENCES_MIN)
        self.ui.horizontalSlider_numberSeq.setMaximum(DefaultUIParameters.DEF_NUMBER_SEQUENCES_MAX)
        self.ui.horizontalSlider_numberSeq.setValue(DefaultUIParameters.DEF_NUMBER_SEQUENCES)

    def checkProjectPathOk(self, pathName, projName):
        if projName == "":
            self.showMessageBox("Warning - Create Simulation", "Cannot create project folder! Please enter a project name.", 'warning')
            self.ui.lineEdit_SimulationName.setFocus()
            return [False, '']

        if pathName == "":
            self.showMessageBox("Warning - Create Simulation", "Cannot create project folder! Please enter a project path.", 'warning')
            self.ui.lineEdit_ProjPath.setFocus()
            self.ui.lineEdit_ProjPath.setText(self.workDirPath)
            return [False, '']

        if not re.match("^[a-zA-Z0-9_]*$", projName):
            self.showMessageBox("Warning - Create Simulation", "Cannot create project! A file name cannot contain special "
                                                               "characters.\nValid characters: numbers, letters, - and _ ", 'warning')
            self.ui.lineEdit_SimulationName.setFocus()
            self.ui.lineEdit_SimulationName.setText("")

            return [False, '']

        pathName = os.path.abspath(pathName)
        if not pathName.endswith('/'):
            pathName += '/'
        if not pathName.endswith('\\'):
            pathName += '/'

        dirExists = FluidExplorerUtils.FluidExplorerUtils.dirExists(pathName)
        if dirExists:
            pathPrjAbsolut = os.path.abspath(pathName)
        else:
            try:
                os.mkdir(pathName)
                pathPrjAbsolut = os.path.abspath(pathName)
            except OSError as exc:
                errorText = ""
                if exc.errno == errno.EACCES:
                    errorText = "Error {0}: {1}" .format(exc.errno, exc.strerror)
                    self.lgr.error("%s", errorText)
                    self.ui.lineEdit_ProjPath.setText("")
                    self.ui.lineEdit_ProjPath.setFocus()
                elif exc.errno == 22:
                    errorText = "Error {0}: {1}" .format(exc.errno, exc.strerror)
                    self.lgr.error("%s", errorText)
                    self.ui.lineEdit_ProjPath.setText("")
                    self.ui.lineEdit_ProjPath.setFocus()
                else:
                    errorText = "Error {0}: {1}" .format(exc.errno, exc.strerror)
                    self.lgr.error("%s", errorText)

                self.showMessageBox("Warning - Create Simulation", "Cannot create project folder! Please check the project path entered.\nDetails: " + errorText, 'warning')
                self.ui.lineEdit_ProjPath.setFocus()
                self.ui.lineEdit_ProjPath.setText(self.workDirPath)

                return [False, '']

        projPathFull = pathName + projName
        dirExists = FluidExplorerUtils.FluidExplorerUtils.dirExists(projPathFull)
        simulationNameAbsolut = os.path.abspath(projPathFull)

        if dirExists:
            self.showMessageBox("Warning - Create Simulation", "Project already exists! Please change the project name.", 'warning')
            self.ui.lineEdit_SimulationName.setFocus()
            self.ui.lineEdit_SimulationName.setText("")
            simulationNameAbsolut = os.path.abspath(projPathFull)

            return [False, '']

        else:
            try:
                os.mkdir(simulationNameAbsolut)
            except OSError as exc:
                if exc.errno == errno.EACCES:
                    errorText = "Error {0}: {1}" .format(exc.errno, exc.strerror)
                    self.lgr.error("%s", errorText)
                    self.ui.lineEdit_ProjPath.setText("")
                    self.ui.lineEdit_ProjPath.setFocus()

                elif exc.errno == 22:
                    errorText = "Error {0}: {1}" .format(exc.errno, exc.strerror)
                    self.lgr.error("%s", errorText)
                    self.ui.lineEdit_ProjPath.setText("")
                    self.ui.lineEdit_ProjPath.setFocus()
                else:
                    errorText = "Error {0}: {1}" .format(exc.errno, exc.strerror)
                    self.lgr.error("%s", errorText)

                self.showMessageBox("Warning - Create Simulation", "Cannot create project folder! Please check the project name entered.\nDetails: " + errorText, 'warning')
                self.ui.lineEdit_ProjPath.setFocus()
                self.ui.lineEdit_ProjPath.setText(self.workDirPath)

                return [False, '']

            finally:
                self.simulationSettings.outputPath = os.path.abspath( projPathFull )
                self.simulationSettings.outputPath = self.simulationSettings.outputPath.replace('\\', '/')
                index = projPathFull.rfind(projName)
                self.simulationSettings.prjName = projPathFull[index:]
                self.simulationNameAbsolut = simulationNameAbsolut

                return [True, simulationNameAbsolut]

    def setCameraButtonSelection(self):
        # Default camera values [on/off]: Persp: 0/1; VC: 0/1; Custom: None/string; Rotation: 0/45-90
        self.simulationSettings.cam_perspective = 0
        self.simulationSettings.cam_viewcube = 0
        self.simulationSettings.imageView = 0
        self.simulationSettings.cam_sphere = 0
        self.simulationSettings.cam_rotation = 0

        if self.CLICK_FLAG_CAM_PV:
            self.simulationSettings.cam_perspective = 1;
            self.simulationSettings.imageView = 1

        if self.CLICK_FLAG_CAM_VC:
            self.simulationSettings.cam_viewcube = 1;
            self.simulationSettings.imageView = 1

        if self.CLICK_FLAG_CAM_SPH: # SPH is the flag for the custom camera
            self.simulationSettings.cam_sphere = self.CLICK_FLAG_CAM_SPH
            self.simulationSettings.cam_custom_name = self.choosenCamera
            self.simulationSettings.imageView = 1
        else:
            self.simulationSettings.cam_sphere = False
            self.simulationSettings.cam_custom_name = None

        if self.CLICK_FLAG_CAM_ROT:
            self.simulationSettings.cam_rotation = self.ui.spinBox_rotDeg.text()
            self.simulationSettings.imageView = 1
        else:
            self.simulationSettings.cam_rotation = 0

    def createProjectSettingsFile(self, simulationNameAbsolut):
        try:
            xmlSettingsWriter = XmlFileWriter()
            pathConfigFile = simulationNameAbsolut + "/" + str(self.simulationSettings.prjName) + ".fxp"
            xmlSettingsWriter.setXmlDocPath(pathConfigFile, "GlobalSettings")
            xmlSettingsWriter.writeSettingToXmlFile(self.simulationSettings)
        except:
            return False
        finally:
            if os.path.exists(os.path.abspath(pathConfigFile)):
                return True
            else:
                return False

    def checkNumSimIsOne_Event(self):
        if self.ui.lineEdit_numberSeq.text() == "1":
            self.ui.lineEdit_numberSeq.setText("2")

    def deleteFilesFromOutputFolder(self):
        # Delete / create output folder
        filePathMain = os.path.dirname(os.path.abspath(__file__))
        fxPathRel = os.path.dirname(os.path.abspath(filePathMain))
        outputFolder = fxPathRel + '/output/'
        outputFolderAbs = os.path.abspath(outputFolder)

        if os.path.exists(outputFolderAbs):
            # Delete content
            filelist = [f for f in os.listdir(outputFolderAbs) if f.endswith((".mc", ".xml", "png", "jpg", "jpeg", "gif"))]
            for f in filelist:
                tmpPath = outputFolder + '/' + f
                tmpPathAbs = os.path.abspath(tmpPath)
                os.remove(tmpPathAbs)
        else:
            os.mkdir(outputFolderAbs)

    def calculateTimeClicked(self):

        waitWindow = QtGui.QDialog(self)
        hbox = QtGui.QHBoxLayout()
        waitLabel = QtGui.QLabel("<b>Calculating sumilation. Please wait ...</b>")
        hbox.addWidget(waitLabel)
        waitWindow.setLayout(hbox)
        waitWindow.show()
        waitWindow.repaint()

        # Show from FRONT
        mayaUtils = MayaFunctionUtils()
        mayaUtils.changeToPerspCam()
        mayaUtils.viewFromCamPosition('FRONT', self.simulationSettings.fluidBoxName)

        # Delete / create output folder
        filePathMain = os.path.dirname(os.path.abspath(__file__))
        fxPathRel = os.path.dirname(os.path.abspath(filePathMain))
        outputFolder = fxPathRel + '/output/'
        outputFolderAbs = os.path.abspath(outputFolder)
        self.deleteFilesFromOutputFolder()

        # Caching
        start_time_cahching = time.time()

        cacheCmd = MayaCacheCmdString()
        cacheCmd.setRenderSettingsFromMaya(int(self.simulationSettings.animationStartTime), int(self.simulationSettings.animationEndTime), outputFolderAbs, "Untitled")
        execCommand = MayaFunctionUtils()
        execCommand.createFluid(cacheCmd.getCacheCommandString(), None)

        res_time_caching = time.time() - start_time_cahching

        # Rendering
        start_time_rendering = time.time()

        renderer = MayaFunctionUtils()
        renderer.renderImages(outputFolder, "None", int(self.simulationSettings.animationStartTime), int(self.simulationSettings.animationEndTime), 960, 540)

        res_time_rendering = time.time() - start_time_rendering

        # Create GIF
        start_time_gif = time.time()

        directoryImagesDir = outputFolderAbs
        outputGifFileDir = outputFolderAbs
        outputGifFileName = 'animation.gif'

        gifImageCreator = GifCreator()
        start_time = self.simulationSettings.animationStartTime
        gifImageCreator.createGifFromImages(self.ffmpegpath, directoryImagesDir, outputGifFileDir, outputGifFileName, start_time, fps=25, gifOptimization=25)

        res_time_gif = time.time() - start_time_gif

        # Back to persp cam
        mayaUtils.changeToPerspCam()
        mayaUtils.viewFromCamPosition('PERSPECTIVE', self.simulationSettings.fluidBoxName)

        # Store results
        self.time_Caching = res_time_caching
        self.time_Renering = res_time_rendering
        self.time_GIF = res_time_gif

        # SetTime
        self.isTimeCalculated = True
        self.setTime()

        waitWindow.close()

        # Delete render window
        FluidExplorerUtils.FluidExplorerUtils.deleteRenderWindow()

    def render_forward(self):
        if int(self.simulationSettings.animationStartTime) > 1:
            self.lgr.info("Initial rendering started")

            # Play the animation once in order to create correct results if the animation does not start at frame=1
            mayaUtils = MayaFunctionUtils()
            mayaUtils.changeToPerspCam()
            mayaUtils.viewFromCamPosition('PERSPECTIVE', self.simulationSettings.fluidBoxName)

            # Delete / create output folder
            filePathMain = os.path.dirname(os.path.abspath(__file__))
            fxPathRel = os.path.dirname(os.path.abspath(filePathMain))
            outputFolder = fxPathRel + '/output/'
            self.deleteFilesFromOutputFolder()

            # Render images
            renderer = MayaFunctionUtils()
            renderer.renderImages(outputFolder, "None", int(self.simulationSettings.animationStartTime), int(self.simulationSettings.animationEndTime), 960, 540)
            self.deleteFilesFromOutputFolder()
            cmds.refresh()

    def setTime(self):

        numberSamples = int(self.ui.horizontalSlider_numberSeq.value())
        numberCameras = self.getNumberOfActiveCameras()

        # Calculate time in seconds
        timeInSeconds = (self.time_Caching + (numberCameras * (self.time_Renering+self.time_GIF))) * numberSamples

        if timeInSeconds > 3599:
            str = time.strftime("%H:%M", time.gmtime(timeInSeconds))
            timeStr = str + ' h.'

        else:
            str = time.strftime("%M:%S", time.gmtime(timeInSeconds))
            timeStr = str + ' min.'

        if self.isTimeCalculated:
            self.ui.labelTime_Value.setText(timeStr)

    def getNumberOfActiveCameras(self):
        cameraCount = 0

        if self.CLICK_FLAG_CAM_PV:
            cameraCount = cameraCount + 1
        if self.CLICK_FLAG_CAM_VC:
            cameraCount = cameraCount + 3
        if self.CLICK_FLAG_CAM_SPH:
            cameraCount = cameraCount + 1
        if self.CLICK_FLAG_CAM_ROT:
            deg = 0
            count = 0
            step = int(self.ui.spinBox_rotDeg.text())

            while deg < 360:
                deg = deg + step
                count = count + 1

            cameraCount = cameraCount + count

        return cameraCount

    def getFFmpegPath(self):
        filePathMain = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filename = os.path.join(filePathMain, 'lib/ffmpeg/')

        # Determine platform. lease note that this command returns the platform of python and not
        # the platform of the underlying os. Assumption: Use 64 bit ffmpeg if 64 bit maya is running.
        is64_bit = ((struct.calcsize('P') * 8) == 64)
        if is64_bit:
            filename = os.path.join(filename, 'x64/')
        else:
            filename = os.path.join(filename, 'x86/')

        #filename = os.path.join(filename, '')
        fxPathRel = os.path.abspath(filename)

        return fxPathRel

    def getFluidExplorerPath(self):
        filePathMain = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filename = os.path.join(filePathMain, 'lib/fluidexplorer/')
        fxPathRel = os.path.abspath(filename)

        return fxPathRel

    def showMessageBox(self, title, text, _type):
        testMode = False
        if not testMode:
            msgBox = QtGui.QMessageBox(self)
            msgBox.setStyleSheet(self.DIALOG_STYLE_SHEET)
            msgBox.setText(text)
            msgBox.setWindowTitle(title)

            if _type == 'warning':
                msgBox.setIcon(QtGui.QMessageBox.Warning)
            if _type == 'critical':
                msgBox.setIcon(QtGui.QMessageBox.Critical)
            if _type == 'information':
                msgBox.setIcon(QtGui.QMessageBox.Information)

            msgBox.exec_()

    def showMessageBox_centered(self, title, text, _type):
        msgBox = QtGui.QMessageBox()
        icon_fluidExplorer_black = QtGui.QIcon(QtGui.QPixmap(':/icon_fluidexplorer_black.png'))
        msgBox.setWindowIcon(icon_fluidExplorer_black)
        msgBox.setStyleSheet(self.DIALOG_STYLE_SHEET)
        msgBox.setText(text)
        msgBox.setWindowTitle(title)

        if _type == 'warning':
            msgBox.setIcon(QtGui.QMessageBox.Warning)
        if _type == 'critical':
            msgBox.setIcon(QtGui.QMessageBox.Critical)
        if _type == 'information':
            msgBox.setIcon(QtGui.QMessageBox.Information)

        msgBox.exec_()

    #
    # //////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # Only for testing
    # //////////////////////////////////////////////////////////////////////////////////////////////////////////////

    def setuptInputFields(self, testObject):
        """
        :type testObject: Test
        """
        self.lgr.info("#")
        self.lgr.info("# Test started ...")
        self.lgr.info("#")

        if testObject.projectName:
            self.ui.lineEdit_SimulationName.setText(testObject.projectName)
        if testObject.projectPath:
            self.ui.lineEdit_ProjPath.setText(testObject.projectPath)
        if testObject.numberOfSamples:
            self.ui.lineEdit_numberSeq.setText(testObject.numberOfSamples)

        self.CLICK_FLAG_CAM_PV = testObject.cam_perspective
        self.CLICK_FLAG_CAM_VC = testObject.cam_viewcube
        self.CLICK_FLAG_CAM_SPH = testObject.cam_custom

        if self.CLICK_FLAG_CAM_SPH:
            self.choosenCamera = testObject.cam_custom_name
            self.lgr.info("Choosen camera: %s", self.choosenCamera)
            self.simulationSettings.cam_custom_name = self.choosenCamera

        if testObject.cam_rotation != 0:
            self.CLICK_FLAG_CAM_ROT = True
            self.ui.spinBox_rotDeg.setValue(testObject.cam_rotation)

        self.update()


    def runTests(self, workDir):

        containerName = self.fluidName
        testFolder = os.path.abspath(os.path.dirname(__file__) + '/Test')

        lgr = logging.getLogger('FluidExplorerPlugin')
        lgr.info(' ')
        lgr.info("### TESTS STARTED ###")
        lgr.info(' ')

        testUtils = Test()
        testUtils.initTest(testFolder, containerName)
        testUtils.setUpLogger()

        """
        testUtils.check_if_ffmpeg_exists()
        """

        """
        inputValues = testUtils.wrong_projectName()
        self.setuptInputFields(inputValues)
        testResults = self.buttonCreateSimulation_Event()
        testUtils.evaluate_wrong_projectName(testResults)

        inputValues = testUtils.empty_projectName()
        self.setuptInputFields(inputValues)
        testResults = self.buttonCreateSimulation_Event()
        testUtils.evaluate_empty_projectName(testResults)

        inputValues = testUtils.wrong_projectPath()
        self.setuptInputFields(inputValues)
        testResults = self.buttonCreateSimulation_Event()
        test        Utils.evaluate_wrong_projectPath(testResults)

        inputValues = testUtils.empty_projectPath()
        self.setuptInputFields(inputValues)
        testResults = self.buttonCreateSimulation_Event()
        testUtils.evaluate_empty_projectPath(testResults)

        inputValues = testUtils.create_sumulation_cache_only()
        self.setuptInputFields(inputValues)
        testResults = self.buttonCreateSimulation_Event()
        testUtils.evaluate_create_sumulation_cache_only(inputValues.projectPath, inputValues.projectName, inputValues.numberOfSamples)
        """

        """
        inputValues = testUtils.create_sumulation_cache_and_images_perspective()
        self.setuptInputFields(inputValues)
        testResults = self.buttonCreateSimulation_Event()
        testUtils.evaluate_create_sumulation_cache_and_images_perspective(inputValues.projectPath, inputValues.projectName, inputValues.numberOfSamples)


        inputValues = testUtils.create_sumulation_cache_and_images_viewcube()
        self.setuptInputFields(inputValues)
        testResults = self.buttonCreateSimulation_Event()
        testUtils.evaluate_create_sumulation_cache_and_images_viewcube(inputValues.projectPath, inputValues.projectName, inputValues.numberOfSamples)
        """

        """
        inputValues = testUtils.create_sumulation_cache_and_images_custom()
        self.setuptInputFields(inputValues)
        testResults = self.buttonCreateSimulation_Event()
        testUtils.evaluate_create_sumulation_cache_and_images_custom(inputValues.projectPath, inputValues.projectName, inputValues.numberOfSamples)
        """

        """
        inputValues = testUtils.create_sumulation_cache_and_images_rotation()
        self.setuptInputFields(inputValues)
        testResults = self.buttonCreateSimulation_Event()
        testUtils.evaluate_create_sumulation_cache_and_images_rotation(inputValues.projectPath, inputValues.projectName, inputValues.numberOfSamples, inputValues.cam_rotation)
        """

        """
        testUtils.check_if_fluid_attributes_exist(self.fluidName)
        """

        inputValues = testUtils.create_sumulation_cache_and_images_all_cameras()
        self.setuptInputFields(inputValues)
        testResults = self.buttonCreateSimulation_Event()
        testUtils.evaluation_create_sumulation_cache_and_images_all_cameras(inputValues.projectPath, inputValues.projectName, inputValues.numberOfSamples)

        self.close()

    # //////////////////////////////////////////////////////////////////////////////////////////////////////////////
