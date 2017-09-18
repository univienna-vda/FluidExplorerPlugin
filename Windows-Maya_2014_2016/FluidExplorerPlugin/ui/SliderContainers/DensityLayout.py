from FluidExplorerPlugin.ui.ParamterTab import SliderContainer
from FluidExplorerPlugin.ui.SliderContainerLayouts import SliderContainerLayout
from FluidExplorerPlugin.ui.Utils.MayaCmds.FluidContainerValues import ContainerValuesUtils


class DensityLayout(SliderContainerLayout):

    def getLayout(self):

        self.containerDensityScale = SliderContainer("Density Scale", 'densityScale', self.fluidBoxName, "Density Scale")
        self.containerDensityBuoyancy = SliderContainer("Buoyancy", 'densityBuoyancy', self.fluidBoxName)
        self.containerDensityDissipation = SliderContainer("Dissipation", 'densityDissipation', self.fluidBoxName)
        self.containerDensityDiffusion = SliderContainer("Diffusion", 'densityDiffusion', self.fluidBoxName)
        self.containerDensityPressure = SliderContainer("D. Pressure", 'densityPressure', self.fluidBoxName, "Density Pressure")
        self.containerDensityPressureThreshold = SliderContainer("Press. Th.", 'densityPressureThreshold', self.fluidBoxName, "Density Pressure Threshold")
        self.containerDensityNoise = SliderContainer("Noise", 'densityNoise', self.fluidBoxName)
        self.containerDensityTension = SliderContainer("D. Tension", 'densityTension', self.fluidBoxName, "Density Tension")
        self.containerTensionForce = SliderContainer("Tension Force", 'tensionForce', self.fluidBoxName, "Tension Force")
        self.containerDensityGradientForce = SliderContainer("Gradient F.", 'densityGradientForce', self.fluidBoxName, "Gradient Force")

        self.containerDensityScale.addToLayout(self.gridLayout_Box, 1)
        self.containerDensityBuoyancy.addToLayout(self.gridLayout_Box, 2)
        self.containerDensityDissipation.addToLayout(self.gridLayout_Box, 3)
        self.containerDensityDiffusion.addToLayout(self.gridLayout_Box, 4)
        self.containerDensityPressure.addToLayout(self.gridLayout_Box, 5)
        self.containerDensityPressureThreshold.addToLayout(self.gridLayout_Box, 6)
        self.containerDensityNoise.addToLayout(self.gridLayout_Box, 7)
        self.containerDensityTension.addToLayout(self.gridLayout_Box, 8)
        self.containerTensionForce.addToLayout(self.gridLayout_Box, 9)
        self.containerDensityGradientForce.addToLayout(self.gridLayout_Box, 10)

        self.sliderList.append(self.containerDensityScale)
        self.sliderList.append(self.containerDensityBuoyancy)
        self.sliderList.append(self.containerDensityDissipation)
        self.sliderList.append(self.containerDensityDiffusion)
        self.sliderList.append(self.containerDensityPressure)
        self.sliderList.append(self.containerDensityPressureThreshold)
        self.sliderList.append(self.containerDensityNoise)
        self.sliderList.append(self.containerDensityTension)
        self.sliderList.append(self.containerTensionForce)
        self.sliderList.append(self.containerDensityGradientForce)

        self.gridLayout_Box.addWidget(self.resetButton,  11, 12-1, 1, 4-1)
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