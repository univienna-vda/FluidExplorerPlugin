from FluidExplorerPlugin.ui.ParamterTab import SliderContainer
from FluidExplorerPlugin.ui.SliderContainerLayouts import SliderContainerLayout
#from FluidExplorerPlugin.ui.Utils.MayaCmds.FluidContainerValues import ContainerValuesUtils


class FuelLayout(SliderContainerLayout):

    def getLayout(self):

        self.containerFuelScale= SliderContainer("Fuel Scale", 'fuelScale', self.fluidBoxName)
        self.containerReactionSpeed = SliderContainer("Reac. Speed", 'reactionSpeed', self.fluidBoxName, "Reaction Speed")
        self.containerAirFuelRatio = SliderContainer("A./F. Ratio", 'airFuelRatio', self.fluidBoxName, "Air/Fuel Ratio")
        self.containerIgnition = SliderContainer("Ignit. Temp.", 'fuelIgnitionTemp', self.fluidBoxName, "Ignition Temperature")
        self.containerMaxReactionTemp = SliderContainer("Max Temp.", 'maxReactionTemp', self.fluidBoxName, "Max Temperature")
        self.containerHeatReleased = SliderContainer("Heat R.", 'heatReleased', self.fluidBoxName, "Heat Released")
        self.containerLightReleased = SliderContainer("Light R.", 'lightReleased', self.fluidBoxName, "Light Released")

        self.containerFuelScale.addToLayout(self.gridLayout_Box, 1)
        self.containerReactionSpeed.addToLayout(self.gridLayout_Box, 2)
        self.containerAirFuelRatio.addToLayout(self.gridLayout_Box, 3)
        self.containerIgnition.addToLayout(self.gridLayout_Box, 4)
        self.containerMaxReactionTemp.addToLayout(self.gridLayout_Box, 5)
        self.containerHeatReleased.addToLayout(self.gridLayout_Box, 6)
        self.containerLightReleased.addToLayout(self.gridLayout_Box, 7)

        self.sliderList.append(self.containerFuelScale)
        self.sliderList.append(self.containerReactionSpeed)
        self.sliderList.append(self.containerAirFuelRatio)
        self.sliderList.append(self.containerIgnition)
        self.sliderList.append(self.containerMaxReactionTemp)
        self.sliderList.append(self.containerHeatReleased)
        self.sliderList.append(self.containerLightReleased)

        self.gridLayout_Box.addWidget(self.resetButton,  8, 12-1, 1, 4-1)
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