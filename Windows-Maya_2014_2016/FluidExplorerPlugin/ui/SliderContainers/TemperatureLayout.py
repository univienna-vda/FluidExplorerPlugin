from FluidExplorerPlugin.ui.ParamterTab import SliderContainer
from FluidExplorerPlugin.ui.SliderContainerLayouts import SliderContainerLayout
from FluidExplorerPlugin.ui.Utils.MayaCmds.FluidContainerValues import ContainerValuesUtils


class TemperatureLayout(SliderContainerLayout):

    def getLayout(self):

        self.temperatureScale = SliderContainer("Temp. Scale", 'temperatureScale', self.fluidBoxName, "Temperature Scale")
        self.buoyancy = SliderContainer("Buoyancy", 'buoyancy', self.fluidBoxName)
        self.temperaturePressure = SliderContainer("Pressure", 'temperaturePressure', self.fluidBoxName)
        self.temperaturePressureThreshold = SliderContainer("Press. Th.", 'temperaturePressureThreshold', self.fluidBoxName, "Pressure Threshold")
        self.temperatureDissipation = SliderContainer("Dissipation", 'temperatureDissipation', self.fluidBoxName)
        self.temperatureDiffusion = SliderContainer("Diffusion", 'temperatureDiffusion', self.fluidBoxName)
        self.temperatureTurbulence = SliderContainer("Turbulence", 'temperatureTurbulence', self.fluidBoxName)
        self.temperatureNoise = SliderContainer("Noise", 'temperatureNoise', self.fluidBoxName)
        self.temperatureTension = SliderContainer("Tension", 'temperatureTension', self.fluidBoxName)

        self.temperatureScale.addToLayout(self.gridLayout_Box, 1)
        self.buoyancy.addToLayout(self.gridLayout_Box, 2)
        self.temperaturePressure.addToLayout(self.gridLayout_Box, 3)
        self.temperaturePressureThreshold.addToLayout(self.gridLayout_Box, 4)
        self.temperatureDissipation.addToLayout(self.gridLayout_Box, 5)
        self.temperatureDiffusion.addToLayout(self.gridLayout_Box, 6)
        self.temperatureTurbulence.addToLayout(self.gridLayout_Box, 7)
        self.temperatureNoise.addToLayout(self.gridLayout_Box, 8)
        self.temperatureTension.addToLayout(self.gridLayout_Box, 9)

        self.sliderList.append(self.temperatureScale)
        self.sliderList.append(self.buoyancy)
        self.sliderList.append(self.temperaturePressure)
        self.sliderList.append(self.temperaturePressureThreshold)
        self.sliderList.append(self.temperatureDissipation)
        self.sliderList.append(self.temperatureDiffusion)
        self.sliderList.append(self.temperatureTurbulence)
        self.sliderList.append(self.temperatureNoise)
        self.sliderList.append(self.temperatureTension)

        self.gridLayout_Box.addWidget(self.resetButton,  10, 12-1, 1, 4-1)
        self.setAllValues(self.sliderList)  # Set all values to start position

        return self.gridLayout_Box

    def resetButton_Event(self):
        self.reset(self.sliderList)

    def initializeSliderDefaultValues(self):
        fluidContainerObj = ContainerValuesUtils(self.fluidBoxName)
        del fluidContainerObj

    def setAllValues(self, sliderList):
        for sliderItem in sliderList:
            sliderItem.resetValues()

    def setInitialVisibility(self, sliderList):
        for sliderItem in sliderList:
            sliderItem.resetValues()