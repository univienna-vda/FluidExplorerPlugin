from FluidExplorerPlugin.ui.ParamterTab import SliderContainer
from FluidExplorerPlugin.ui.SliderContainerLayouts import SliderContainerLayout
from FluidExplorerPlugin.ui.Utils.MayaCmds.FluidContainerValues import ContainerValuesUtils


class TurbulenceLayout(SliderContainerLayout):

    def getLayout(self):

        self.containerStrength = SliderContainer("Strength", 'turbulenceStrength', self.fluidBoxName)
        self.containerFrequency = SliderContainer("Frequency", 'turbulenceFrequency', self.fluidBoxName)
        self.containerSpeed = SliderContainer("Speed", 'turbulenceSpeed', self.fluidBoxName)

        self.containerStrength.addToLayout(self.gridLayout_Box, 1)
        self.containerFrequency.addToLayout(self.gridLayout_Box, 2)
        self.containerSpeed.addToLayout(self.gridLayout_Box, 3)

        self.sliderList.append(self.containerStrength)
        self.sliderList.append(self.containerFrequency)
        self.sliderList.append(self.containerSpeed)

        self.gridLayout_Box.addWidget(self.resetButton,  4, 12-1, 1, 4-1)
        self.setAllValues(self.sliderList)  # Set all values to start position

        return self.gridLayout_Box

    def resetButton_Event(self):
        self.reset(self.sliderList)

    def setAllValues(self, sliderList):
        for sliderItem in sliderList:
            sliderItem.resetValues()

    def setInitialVisibility(self, sliderList):
        for sliderItem in sliderList:
            sliderItem.resetValues()