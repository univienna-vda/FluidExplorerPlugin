import random
import logging


class UsedSpansMinMax():

    def __init__(self):
        self.min = ""
        self.max = ""
        self.name = ""
        self.nameForPattern = "'"

class SliderSpanSelected():
    def __init__(self, dynamicSimulationLayout, densityLayout, velocityLayout, turbulenceLayout, temperatureLayout, fuelLayout, colorLayout):

        # Logging
        self.lgr = logging.getLogger('FluidExplorerPlugin')

        # Stores a list with objects of 'UsedSpansMinMax' which  saves all ranges used by the user
        self.usedSpansMinMax = list()

        self.gravity_Span = self.setSpanValues(dynamicSimulationLayout.containerGravity)
        self.viscosity_Span = self.setSpanValues(dynamicSimulationLayout.containerViscosity)
        self.friction_Span = self.setSpanValues(dynamicSimulationLayout.containerFriction)
        self.velocityDamp_Span = self.setSpanValues(dynamicSimulationLayout.containerDamp)

        self.densityScale_Span = self.setSpanValues(densityLayout.containerDensityScale)
        self.densityBuoyancy_Span = self.setSpanValues(densityLayout.containerDensityBuoyancy)
        self.densityDissipation_Span = self.setSpanValues(densityLayout.containerDensityDissipation)
        self.densityDiffusion_Span = self.setSpanValues(densityLayout.containerDensityDiffusion)
        self.densityPressure_Span = self.setSpanValues(densityLayout.containerDensityPressure)
        self.densityPressureThreshold_Span = self.setSpanValues(densityLayout.containerDensityPressureThreshold)
        self.densityNoise_Span = self.setSpanValues(densityLayout.containerDensityNoise)
        self.densityTension_Span = self.setSpanValues(densityLayout.containerDensityTension)
        self.tensionForce_Span = self.setSpanValues(densityLayout.containerTensionForce)
        self.densityGradientForce_Span = self.setSpanValues(densityLayout.containerDensityGradientForce)

        self.velocitySwirl_Span = self.setSpanValues(velocityLayout.containerSwirl)
        self.velocityNoise_Span = self.setSpanValues(velocityLayout.containerNoise)

        self.turbulenceStrength_Span = self.setSpanValues(turbulenceLayout.containerStrength)
        self.turbulenceFrequency_Span = self.setSpanValues(turbulenceLayout.containerFrequency)
        self.turbulenceSpeed_Span = self.setSpanValues(turbulenceLayout.containerSpeed)

        self.temperatureScale_Span = self.setSpanValues(temperatureLayout.temperatureScale)
        self.buoyancy_Span = self.setSpanValues(temperatureLayout.buoyancy)
        self.temperaturePressure_Span = self.setSpanValues(temperatureLayout.temperaturePressure)
        self.temperaturePressureThreshold_Span = self.setSpanValues(temperatureLayout.temperaturePressureThreshold)
        self.temperatureDissipation_Span = self.setSpanValues(temperatureLayout.temperatureDissipation)
        self.temperatureDiffusion_Span = self.setSpanValues(temperatureLayout.temperatureDiffusion)
        self.temperatureTurbulence_Span = self.setSpanValues(temperatureLayout.temperatureTurbulence)
        self.temperatureNoise_Span = self.setSpanValues(temperatureLayout.temperatureNoise)
        self.temperatureTension_Span = self.setSpanValues(temperatureLayout.temperatureTension)

        self.fuelScale_Span = self.setSpanValues(fuelLayout.containerFuelScale)
        self.reactionSpeed_Span = self.setSpanValues(fuelLayout.containerReactionSpeed)
        self.airFuelRatio_Span = self.setSpanValues(fuelLayout.containerAirFuelRatio)
        self.fuelIgnitionTemp_Span = self.setSpanValues(fuelLayout.containerIgnition)
        self.maxReactionTemp_Span = self.setSpanValues(fuelLayout.containerMaxReactionTemp)
        self.heatReleased_Span = self.setSpanValues(fuelLayout.containerHeatReleased)
        self.lightReleased_Span = self.setSpanValues(fuelLayout.containerLightReleased)

        self.colorDissipation_Span = self.setSpanValues(colorLayout.containerColorDissipation)
        self.colorDiffusion_Span = self.setSpanValues(colorLayout.containerColorDiffusion)

    def setSpanValues(self, container):
        if container.checkBox.isChecked():
            tmp = container.label.text()
            str_label = tmp[tmp.index('>')+1:len(tmp)-7]
            infoTxt = str_label + " : " + container.lineEditMin.text() + " - " + container.lineEditMax.text()
            self.lgr.info(infoTxt)

            # Add to list
            objUsdRanges = self.createUsedRangesAndMinMaxValues(container)
            self.usedSpansMinMax.append(objUsdRanges)

            return [container.lineEditMin.text(), container.lineEditMax.text()]
        else:
            tmp = container.label.text()
            str_label = tmp[tmp.index('>')+1:len(tmp)-7]
            infoTxt = str_label + " : " + container.lineEditDefault.text()
            #infoTxt = (container.label.text(), ": ", container.lineEditDefault.text())
            self.lgr.info(infoTxt)
            return [container.lineEditDefault.text(), container.lineEditDefault.text()]

    def createUsedRangesAndMinMaxValues(self, container):
        tmp = UsedSpansMinMax()
        tmp.min = container.rangeSlider.minValue
        tmp.max = container.rangeSlider.maxValue
        tmp.name = container.labelName
        tmp.nameForPattern = container.propertyName

        return tmp

    def foo(self):
        return self.usedSpansMinMax




class FluidContainerValues():
    def __init__(self):
        # Values - Dynamic Simulation
        self.gravity = None
        self.viscosity = None
        self.friction = None
        self.velocityDamp = None

        # Values - Density
        self.densityScale = None
        self.densityBuoyancy = None
        self.densityDissipation = None
        self.densityDiffusion = None
        self.densityPressure = None
        self.densityPressureThreshold = None
        self.densityNoise = None
        self.densityTension = None
        self.tensionForce = None
        self.densityGradientForce = None

        # Values - Velocity
        self.velocitySwirl = None
        self.velocityNoise = None

        # Values - Turbulence
        self.turbulenceStrength = None
        self.turbulenceFrequency = None
        self.turbulenceSpeed = None

        # Values - Temperature
        self.temperatureScale = None
        self.buoyancy = None
        self.temperaturePressure = None
        self.temperaturePressureThreshold = None
        self.temperatureDissipation = None
        self.temperatureDiffusion = None
        self.temperatureTurbulence = None
        self.temperatureNoise = None
        self.temperatureTension = None

        # Values - Fuel
        self.fuelScale = None
        self.reactionSpeed = None
        self.airFuelRatio = None
        self.fuelIgnitionTemp = None
        self.maxReactionTemp = None
        self.heatReleased = None
        self.lightReleased = None

        # Values Color
        self.colorDissipation = None
        self.colorDiffusion = None


class FluidValueSampler():

    def __init__(self, sliderRanges):
        """
        :type sliderRanges: SliderSpanSelected
        """
        self.randomValuesSet = FluidContainerValues()
        self.sliderRanges = sliderRanges

    def setSldierRangeValues(self):

        self.randomValuesSet.gravity = self.getMinMaxValuesRound(self.sliderRanges.gravity_Span)
        self.randomValuesSet.viscosity = self.getMinMaxValuesRound(self.sliderRanges.viscosity_Span)
        self.randomValuesSet.friction = self.getMinMaxValuesRound(self.sliderRanges.friction_Span)
        self.randomValuesSet.velocityDamp = self.getMinMaxValuesRound(self.sliderRanges.velocityDamp_Span)

        self.randomValuesSet.densityScale = self.getMinMaxValuesRound(self.sliderRanges.densityScale_Span)
        self.randomValuesSet.densityBuoyancy = self.getMinMaxValuesRound(self.sliderRanges.densityBuoyancy_Span)
        self.randomValuesSet.densityDissipation = self.getMinMaxValuesRound(self.sliderRanges.densityDissipation_Span)
        self.randomValuesSet.densityDiffusion = self.getMinMaxValuesRound(self.sliderRanges.densityDiffusion_Span)
        self.randomValuesSet.densityPressure = self.getMinMaxValuesRound(self.sliderRanges.densityPressure_Span)
        self.randomValuesSet.densityPressureThreshold = self.getMinMaxValuesRound(self.sliderRanges.densityPressureThreshold_Span)
        self.randomValuesSet.densityNoise = self.getMinMaxValuesRound(self.sliderRanges.densityNoise_Span)
        self.randomValuesSet.densityTension = self.getMinMaxValuesRound(self.sliderRanges.densityTension_Span)
        self.randomValuesSet.tensionForce = self.getMinMaxValuesRound(self.sliderRanges.tensionForce_Span)
        self.randomValuesSet.densityGradientForce = self.getMinMaxValuesRound(self.sliderRanges.densityGradientForce_Span)

        self.randomValuesSet.velocitySwirl = self.getMinMaxValuesRound(self.sliderRanges.velocitySwirl_Span)
        self.randomValuesSet.velocityNoise = self.getMinMaxValuesRound(self.sliderRanges.velocityNoise_Span)

        self.randomValuesSet.turbulenceStrength = self.getMinMaxValuesRound(self.sliderRanges.turbulenceStrength_Span)
        self.randomValuesSet.turbulenceFrequency = self.getMinMaxValuesRound(self.sliderRanges.turbulenceFrequency_Span)
        self.randomValuesSet.turbulenceSpeed = self.getMinMaxValuesRound(self.sliderRanges.turbulenceSpeed_Span)

        self.randomValuesSet.temperatureScale = self.getMinMaxValuesRound(self.sliderRanges.temperatureScale_Span)
        self.randomValuesSet.buoyancy = self.getMinMaxValuesRound(self.sliderRanges.buoyancy_Span)
        self.randomValuesSet.temperaturePressure = self.getMinMaxValuesRound(self.sliderRanges.temperaturePressure_Span)
        self.randomValuesSet.temperaturePressureThreshold = self.getMinMaxValuesRound(self.sliderRanges.temperaturePressureThreshold_Span)
        self.randomValuesSet.temperatureDissipation = self.getMinMaxValuesRound(self.sliderRanges.temperatureDissipation_Span)
        self.randomValuesSet.temperatureDiffusion = self.getMinMaxValuesRound(self.sliderRanges.temperatureDiffusion_Span)
        self.randomValuesSet.temperatureTurbulence = self.getMinMaxValuesRound(self.sliderRanges.temperatureTurbulence_Span)
        self.randomValuesSet.temperatureNoise = self.getMinMaxValuesRound(self.sliderRanges.temperatureNoise_Span)
        self.randomValuesSet.temperatureTension = self.getMinMaxValuesRound(self.sliderRanges.temperatureTension_Span)

        self.randomValuesSet.fuelScale = self.getMinMaxValuesRound(self.sliderRanges.fuelScale_Span)
        self.randomValuesSet.reactionSpeed = self.getMinMaxValuesRound(self.sliderRanges.reactionSpeed_Span)
        self.randomValuesSet.airFuelRatio = self.getMinMaxValuesRound(self.sliderRanges.airFuelRatio_Span)
        self.randomValuesSet.fuelIgnitionTemp = self.getMinMaxValuesRound(self.sliderRanges.fuelIgnitionTemp_Span)
        self.randomValuesSet.maxReactionTemp = self.getMinMaxValuesRound(self.sliderRanges.maxReactionTemp_Span)
        self.randomValuesSet.heatReleased = self.getMinMaxValuesRound(self.sliderRanges.heatReleased_Span)
        self.randomValuesSet.lightReleased = self.getMinMaxValuesRound(self.sliderRanges.lightReleased_Span)

        self.randomValuesSet.colorDissipation = self.getMinMaxValuesRound(self.sliderRanges.colorDissipation_Span)
        self.randomValuesSet.colorDiffusion = self.getMinMaxValuesRound(self.sliderRanges.colorDiffusion_Span)

    def getSampleSet(self):
        return self.randomValuesSet

    def getMinMaxValuesRound(self, span):
        return round(random.uniform(round(float(span[0]), 3), round(float(span[1]), 3)), 3)