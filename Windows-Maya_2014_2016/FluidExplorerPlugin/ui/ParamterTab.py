from PySide import QtGui
from PySide import QtCore
import maya.cmds as cmds
import logging

from RangeSlider.HRangeSlider import QHRangeSlider
from SliderContainers.ParamterTabDefaultValues import ParameterTabDefaultValues
from FluidExplorerPlugin.ui.Utils.DefaultUIValues import DefaultUIParameters


class SliderContainer(object):
        def __init__(self, property, propertyName, nodeName, fullPropertyName=""):
            # Logging
            self.lgr = logging.getLogger('FluidExplorerPlugin')

            self.propertyName = propertyName
            self.propertyString = property

            self.groupBox_Box = QtGui.QWidget()
            gridLayout_Box = QtGui.QGridLayout()
            self.groupBox_Box.setLayout(gridLayout_Box)

            QtGui.QToolTip.setFont(QtGui.QFont('MS Shell', 10))
            txt = "<span style=\" font-size:8pt;\">" + property + "</span>"
            self.label = QtGui.QLabel(txt)

            [sliderMinValue, sliderMaxValue, sliderDefValue] = self.getFielDefaultValues(propertyName, nodeName)
            isAttrLocked = self.chekIfAttrIsLocked(propertyName, nodeName)
            self.isContainerLocked = isAttrLocked

            if len(fullPropertyName) > 0:
                toolTipTxt = "Full Name: " + fullPropertyName + ' '
                self.label.setToolTip(toolTipTxt)

            self.checkBox = QtGui.QCheckBox("")
            self.lineEditMin = QtGui.QLineEdit(str(sliderMinValue))
            self.lineEditMax = QtGui.QLineEdit(str(sliderMaxValue))
            self.lineEditDefault = QtGui.QLineEdit(str(sliderDefValue))
            self.rangeSlider = QHRangeSlider(self.lineEditMin, self.lineEditMax, self.lineEditDefault, range = [sliderMinValue, sliderMaxValue], enabledFlag=True)
            self.sliderDefValue = QtGui.QSlider(QtCore.Qt.Horizontal)   # delete
            self.sliderDefValue.setStyleSheet(DefaultUIParameters.getCustomSliderStyleSheet(isAttrLocked))
            self.rangeSlider.defaultSingleValue = sliderDefValue
            self.lineEditMin.setFixedWidth(35), self.lineEditMin.setAlignment(QtCore.Qt.AlignCenter)
            self.lineEditMax.setFixedWidth(35), self.lineEditMax.setAlignment(QtCore.Qt.AlignCenter)
            self.lineEditDefault.setFixedWidth(35), self.lineEditDefault.setAlignment(QtCore.Qt.AlignRight)
            self.rangeSlider.setValues([sliderMinValue, sliderMaxValue])
            self.rangeSlider.setEmitWhileMoving(True)
            self.resetButton = QtGui.QPushButton("Reset all Values")

            if len(fullPropertyName) > 0:
                self.labelName = fullPropertyName
            else:
                self.labelName = self.propertyString

            # Lock icon
            self.pix = QtGui.QPixmap(":/icon_lock.png").scaled(12, 12)
            self.lockImage = QtGui.QLabel()
            self.lockImage.setPixmap(self.pix)
            self.lockImage.setAlignment(QtCore.Qt.AlignLeft)

            self.createConnections()
            self.initialComponents()
            self.iniSliderValues2()

        def setContainerLockedState(self, state):
            if not state:
                self.label.setEnabled(state)
                self.checkBox.setEnabled(state)
                self.lineEditDefault.setEnabled(state)
                self.lineEditMin.setEnabled(state)
                self.lineEditMax.setEnabled(state)
                self.rangeSlider.setEnabled(state)
                self.rangeSlider.enabledFlag = state

        def iniSliderValues2(self):
            self.rangeSlider.setValues([float(self.lineEditMin.text()), float(self.lineEditMax.text())])
            self.rangeSlider.update()
            self.sliderDefValue.setValue(self.translate(self.rangeSlider.defaultSingleValue, self.rangeSlider.rangeValues[0], self.rangeSlider.rangeValues[1], 0, 250))

        def initialComponents(self):
            self.lineEditDefault.setEnabled(True)
            self.lineEditMin.setEnabled(False)
            self.lineEditMax.setEnabled(False)
            self.lineEditMin.setMaxLength(5)
            self.lineEditMax.setMaxLength(4)
            self.lineEditDefault.setMaxLength(4)
            self.checkBox.setChecked(False)
            self.rangeSlider.isRangeActive = False
            self.rangeSlider.setVisible(False)
            self.sliderDefValue.setRange(0, 250)
            self.rangeSlider.setMaximumWidth(288)
            self.rangeSlider.setMinimumWidth(288)
            self.sliderDefValue.setMaximumWidth(self.rangeSlider.width())
            self.sliderDefValue.setMinimumWidth(self.rangeSlider.width())

        def addToLayout(self, gridLayout_Box, position):
            gridLayout_Box.addWidget(self.label, position, 0, 1, 2, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
            gridLayout_Box.addWidget(self.checkBox, position, 2, QtCore.Qt.AlignCenter)
            gridLayout_Box.addWidget(self.lineEditDefault, position, 4, QtCore.Qt.AlignCenter)
            gridLayout_Box.addWidget(self.lineEditMin, position, 5, QtCore.Qt.AlignCenter)
            gridLayout_Box.addWidget(self.rangeSlider, position, 6, 1, 9-2)
            gridLayout_Box.addWidget(self.sliderDefValue, position, 6, 1, 9-2)
            gridLayout_Box.addWidget(self.lineEditMax, position, 15-2, QtCore.Qt.AlignCenter)

            if self.isContainerLocked:
                gridLayout_Box.addWidget(self.lockImage, position, 0, 1, 2, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
                self.checkBox.setEnabled(False)
                self.lineEditDefault.setEnabled(False)
                self.lineEditMin.setEnabled(False)
                self.rangeSlider.setEnabled(False)
                self.rangeSlider.changeSliderEnabled(False)
                self.lineEditMax.setEnabled(False)
                self.sliderDefValue.setEnabled(False)

                # Use this code because some labes are to long
                if self.propertyName == "densityScale":
                    self.label.setText("Dens. Scale")
                if self.propertyName == "tensionForce":
                    self.label.setText("Tension F.")
                if self.propertyName == "reactionSpeed":
                    self.label.setText("Reac. Sp.")

                self.label.update()


        def createConnections(self):
            self.checkBox.clicked.connect(self.checkBoxModeChanged_Event)
            self.lineEditDefault.editingFinished.connect(self.leaveLineEditDef_A)
            self.lineEditMin.editingFinished.connect(self.leaveLineEditMin_A)
            self.lineEditMax.editingFinished.connect(self.leaveLineEditMax_A)
            self.resetButton.clicked.connect(self.resetValues)
            self.sliderDefValue.valueChanged.connect(self.sliderDefValueEvent)

        # --------------------------------------------------------------------------------------------------------------
        @QtCore.Slot()
        def checkBoxModeChanged_Event(self):
            self.changeSliderMode(self.rangeSlider, self.checkBox, self.lineEditDefault, self.lineEditMin, self.lineEditMax, self.sliderDefValue)

        @QtCore.Slot()
        def leaveLineEditDef_A(self):
            pass
            self.leaveLineEditEvent(self.lineEditDefault,  self.sliderDefValue, self.rangeSlider)

        @QtCore.Slot()
        def leaveLineEditMin_A(self):
            self.leaveLineEditMinEvent(self.lineEditMin, self.lineEditMax, self.rangeSlider)

        @QtCore.Slot()
        def leaveLineEditMax_A(self):
            self.leaveLineEditMaxEvent(self.lineEditMin, self.lineEditMax,  self.rangeSlider)

        @QtCore.Slot()
        def sliderDefValueEvent(self):
            sliderDoubleValue = self.translate(self.sliderDefValue.value(), 0, 250, self.rangeSlider.rangeValues[0], self.rangeSlider.rangeValues[1])
            self.lineEditDefault.setText(str(format(sliderDoubleValue, '.2f')))
        # --------------------------------------------------------------------------------------------------------------

        def changeSliderMode(self, slider, checkBox, lineEditDefault, lineEditMin, lineEditMax, sliderDefValue):
            self.rangeSlider.isRangeActive = True
            if checkBox.checkState():
                # Range is active
                sliderDefValue.setVisible(False)
                lineEditDefault.setEnabled(False)
                lineEditDefault.setText(str(format(slider.defaultSingleValue, '.2f')))

                slider.setValues([slider.rangeValues[0], slider.rangeValues[1]])
                slider.setVisible(True)

                lineEditMin.setEnabled(True)
                lineEditMax.setEnabled(True)
                lineEditMin.setText(str(format(slider.rangeValues[0], '.2f')))
                lineEditMax.setText(str(format(slider.rangeValues[1], '.2f')))
                lineEditMin.setFocus()

            else:
                # Range is NOT active
                slider.setVisible(False)
                lineEditMin.setEnabled(False)
                lineEditMax.setEnabled(False)
                lineEditMin.setText(str(format(slider.rangeValues[0], '.2f')))
                lineEditMax.setText(str(format(slider.rangeValues[1], '.2f')))

                lineEditDefault.setEnabled(True)
                lineEditDefault.setText(str(format(slider.defaultSingleValue, '.2f')))
                lineEditDefault.setFocus()

                sliderDefValue.setVisible(True)
                sliderValueTranslated = self.translate(slider.defaultSingleValue, slider.rangeValues[0], slider.rangeValues[1], 0, 250)
                sliderDefValue.setValue(sliderValueTranslated)

        def leaveLineEditMinEvent(self, lineEditMin, lineEditMax, slider):
                v_str = lineEditMin.text()
                try:
                    v = float(v_str)

                    if v < float(slider.rangeValues[0]):
                        # print "error to small"
                        lineEditMin.setText(str(format(slider.rangeValues[0], '.2f')))
                    elif v > float(slider.rangeValues[1]):
                        # print "error to big"
                        lineEditMin.setText(str(format(slider.rangeValues[1], '.2f')))
                        lineEditMax.setText(str(format(slider.rangeValues[1], '.2f')))
                    else:
                        # print "ok"
                        pass

                except ValueError:
                    lineEditMin.setText(str(format(slider.rangeValues[0], '.2f')))

                v1 = float(lineEditMin.text())
                v2 = float(lineEditMax.text())

                # Update slider and line edit
                slider.setValues([v1, v2])
                slider.update()
                lineEditMin.setText(str(format(v1, '.2f')))

        def leaveLineEditMaxEvent(self, lineEditMin, lineEditMax, slider):
            v_str = lineEditMax.text()
            try:
                v = float(v_str)

                if v < float(slider.rangeValues[0]):
                    # print "error to small"
                    lineEditMax.setText(str(format(slider.rangeValues[0], '.2f')))
                    lineEditMin.setText(str(format(slider.rangeValues[0], '.2f')))
                elif v > float(slider.rangeValues[1]):
                    # print "error to big"
                    lineEditMax.setText(str(format(slider.rangeValues[1], '.2f')))
                else:
                    # print "ok"
                    pass

            except ValueError:
                lineEditMax.setText(str(format(slider.rangeValues[1], '.2f')))

            v1 = float(lineEditMin.text())
            v2 = float(lineEditMax.text())

            # Update slider
            slider.setValues([v1, v2])
            slider.update()
            lineEditMax.setText(str(format(v2, '.2f')))

        def leaveLineEditEvent(self, lineEdit, slider, rangeSlider):

            v_str = lineEdit.text()
            try:
                v = float(v_str)
                v = round(v, 2)

                if v < float(rangeSlider.rangeValues[0]):
                    # print "error to small"
                    lineEdit.setText(str(format(rangeSlider.rangeValues[0], '.2f')))
                    v = rangeSlider.rangeValues[0]
                elif v > float(rangeSlider.rangeValues[1]):
                    # print "error to big"
                    lineEdit.setText(str(format(rangeSlider.rangeValues[1], '.2f')))
                    v = rangeSlider.rangeValues[1]
                else:
                    pass
                    # print "OK"

            except ValueError:
                lineEdit.setText(str(format(rangeSlider.defaultSingleValue, '.2f')))
                v = float(rangeSlider.defaultSingleValue)

            # Set value
            sliderValueTranslated = self.translate(v, rangeSlider.rangeValues[0], rangeSlider.rangeValues[1], 0, 250)
            slider.setValue(sliderValueTranslated)
            lineEdit.setText(str(format(v, '.2f')))

        def resetValues(self):
            self.rangeSlider.setValues([self.rangeSlider.rangeValues[0], self.rangeSlider.rangeValues[1]])
            self.lineEditMin.setText(str(format(self.rangeSlider.rangeValues[0], '.2f')))
            self.lineEditMax.setText(str(format(self.rangeSlider.rangeValues[1], '.2f')))
            self.lineEditDefault.setText(str(format(self.rangeSlider.defaultSingleValue, '.2f')))
            self.sliderDefValue.setValue(self.translate(self.rangeSlider.defaultSingleValue, self.rangeSlider.rangeValues[0], self.rangeSlider.rangeValues[1], 0, 250))
            self.rangeSlider.update()

        def getFielDefaultValues(self, fieldName, nodeName):

            [minSoft, maxSoft] = ParameterTabDefaultValues.setSoftMinMaxValue(fieldName, nodeName)

            cmdStr = nodeName + '.' + fieldName
            currentValue = cmds.getAttr(cmdStr)

            return [minSoft, maxSoft, currentValue]

        def chekIfAttrIsLocked(self, fieldName, nodeName):

            isFieldLocked = False
            cmdStr = nodeName + '.' + fieldName
            try:
                isFieldLocked = cmds.getAttr(cmdStr, lock=True)
                return isFieldLocked
            except ValueError:
                self.lgr.warning('Cannot get lock state of attribute: %s', cmdStr)
                return isFieldLocked

        def translate(self, value, leftMin, leftMax, rightMin, rightMax):
            # Get 'wide' of each range
            leftSpan = leftMax - leftMin
            rightSpan = rightMax - rightMin

            # Convert the left range into a range (rightMin-rightMax)
            valueScaled = float(value - leftMin) / float(leftSpan)

            return rightMin + (valueScaled * rightSpan)


class ParameterTab(object):

    def __init__(self, boxName):
        # Logging
        self.lgr = logging.getLogger('FluidExplorerPlugin')
        self.fluidBoxName = boxName
        self.setupTabWidget()

    def initialToolBoxComponents(self):
        for itemIndex in range(0, self.toolBox.count()):
            self.toolBox.setItemIcon(itemIndex, QtGui.QIcon(':/arrow_small_1.png'))
        self.toolBox.setItemIcon(0, QtGui.QIcon(':/arrow_small_2.png'))

    def setupTabWidget(self):

        from SliderContainers.DensityLayout import DensityLayout
        from SliderContainers.VelocityLayout import VelocityLayout
        from SliderContainers.TurbulenceLayout import TurbulenceLayout
        from SliderContainers.TemperatureLayout import TemperatureLayout
        from SliderContainers.FuelLayout import FuelLayout
        from SliderContainers.ColorLayout import ColorLayout
        from SliderContainers.DynamicSimulationLayout import DynamicSimulationLayout

        # --------------------------------------------------------------------------------------------------------------
        DensityBox = QtGui.QGroupBox()
        self.DensityLayout = DensityLayout()
        self.DensityLayout.setFluidBoxName(self.fluidBoxName)
        DensityBox.setLayout(self.DensityLayout.getLayout())

        VelocityBox = QtGui.QGroupBox()
        self.VelocityLayout = VelocityLayout()
        self.VelocityLayout.setFluidBoxName(self.fluidBoxName)
        VelocityBox.setLayout(self.VelocityLayout.getLayout())

        TurbulenceBox = QtGui.QGroupBox()
        self.TurbulenceLayout = TurbulenceLayout()
        self.TurbulenceLayout.setFluidBoxName(self.fluidBoxName)
        TurbulenceBox.setLayout(self.TurbulenceLayout.getLayout())

        TemperatureBox = QtGui.QGroupBox()
        self.TemperatureLayout = TemperatureLayout()
        self.TemperatureLayout.setFluidBoxName(self.fluidBoxName)
        TemperatureBox.setLayout(self.TemperatureLayout.getLayout())


        FuelBox = QtGui.QGroupBox()
        self.FuelLayout = FuelLayout()
        self.FuelLayout.setFluidBoxName(self.fluidBoxName)
        FuelBox.setLayout(self.FuelLayout.getLayout())

        ColorBox = QtGui.QGroupBox()
        self.ColorLayout = ColorLayout()
        self.ColorLayout.setFluidBoxName(self.fluidBoxName)
        ColorBox.setLayout(self.ColorLayout.getLayout())


        DynamicSimulationBox = QtGui.QGroupBox()
        self.DynamicSimulationLayout = DynamicSimulationLayout()
        self.DynamicSimulationLayout.setFluidBoxName(self.fluidBoxName)
        DynamicSimulationBox.setLayout(self.DynamicSimulationLayout.getLayout())
        # --------------------------------------------------------------------------------------------------------------

        # The toolbox stores all slider containers
        self.toolBox = QtGui.QToolBox()
        self.toolBox.addItem(DynamicSimulationBox, "Dynamic Simulation")
        self.toolBox.addItem(DensityBox, "Density")
        self.toolBox.addItem(VelocityBox, "Velocity")
        self.toolBox.addItem(TurbulenceBox, "Turbulence")
        self.toolBox.addItem(TemperatureBox, "Temperature")
        self.toolBox.addItem(FuelBox, "Fuel")
        self.toolBox.addItem(ColorBox, "Color")

        # Disable tool box items if method is set to 0 in maya
        self.toolBox.setItemEnabled(1, self.isItemEbabled(self.fluidBoxName + '.' + 'densityMethod'))
        self.toolBox.setItemEnabled(2, self.isItemEbabled(self.fluidBoxName + '.' + 'velocityMethod'))
        self.toolBox.setItemEnabled(4, self.isItemEbabled(self.fluidBoxName + '.' + 'temperatureMethod'))
        self.toolBox.setItemEnabled(5, self.isItemEbabled(self.fluidBoxName + '.' + 'fuelMethod'))
        self.toolBox.setItemEnabled(6, self.isItemEbabled(self.fluidBoxName + '.' + 'colorMethod'))

        self.initialToolBoxComponents()
        self.toolBox.currentChanged.connect(self.toolBoxChanged_Event)

        vBoxlayout = QtGui.QVBoxLayout()
        vBoxlayout.addWidget(self.toolBox)

        self.parameterTab = QtGui.QWidget()
        self.parameterTab.setLayout(vBoxlayout)

    def createConnections(self):
        pass

    def getSelectedValuesFromSlider(self):
        self.lgr.info('Read selected values from paramter tab')

        from Utils.RangeSliderSpan import SliderSpanSelected

        self.selectedSliderValues = SliderSpanSelected(self.DynamicSimulationLayout, self.DensityLayout,
                                                       self.VelocityLayout, self.TurbulenceLayout,
                                                       self.TemperatureLayout, self.FuelLayout, self.ColorLayout)

        return self.selectedSliderValues

    def randomValuesSnapshot(self):
        return self.VelocityLayout.containerSwirl.getSliderValues()

    def toolBoxChanged_Event(self):
        currentTabIndex = self.toolBox.currentIndex()
        for itemIndex in range(self.toolBox.count()):
            self.toolBox.setItemIcon(itemIndex, QtGui.QIcon(':/arrow_small_1.png'))
            if itemIndex == currentTabIndex:
                self.toolBox.setItemIcon(itemIndex, QtGui.QIcon(':/arrow_small_2.png'))

        self.initAllSlidersOfTheBox()

    def getTab(self):
        return self.parameterTab

    def initAllSlidersOfTheBox(self):
        pass

    def isItemEbabled(self, cmdStr):
        try:
            flag = cmds.getAttr(cmdStr)
            if flag == 0:
                return False
            else:
                return True
        except ValueError:
            return True



