from FluidExplorerPlugin.ui.ParamterTab import SliderContainer
from FluidExplorerPlugin.ui.SliderContainerLayouts import SliderContainerLayout
from FluidExplorerPlugin.ui.Utils.MayaCmds.FluidContainerValues import ContainerValuesUtils


class VelocityLayout(SliderContainerLayout):

    def getLayout(self):
        self.containerSwirl = SliderContainer("Swirl", 'velocitySwirl', self.fluidBoxName)
        self.containerNoise = SliderContainer("Noise", 'velocityNoise', self.fluidBoxName)

        self.containerSwirl.addToLayout(self.gridLayout_Box, 1)
        self.containerNoise.addToLayout(self.gridLayout_Box, 2)

        self.sliderList.append(self.containerSwirl)
        self.sliderList.append(self.containerNoise)

        self.gridLayout_Box.addWidget(self.resetButton,  5, 12-1, 1, 4-1)
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