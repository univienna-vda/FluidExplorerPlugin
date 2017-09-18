import logging

class MayaCacheCmdSettings(object):
    def _init__(self):
        self._fluidBoxName = ""
        self._outputPath = ""
        self._numberSamples = 128
        self._numberOfFrames = 0
        self._prjName = ""
        self._cam_perspective = 1
        self._cam_viewcube = 0
        self._cam_sphere = 0
        self._cam_rotation = 0
        self._cam_custom_name = None
        self._animationStartTime = 0.0
        self._animationEndTime = 0.0
        self._createCacheCommandString = ""
        self._simulationNameMB = ""
        self._imageView = 0
        self._sampledValuesString = ""

    @property
    def fluidBoxName(self):
        return self._fluidBoxName

    @fluidBoxName.setter
    def fluidBoxName(self, value):
        self._fluidBoxName = value

    @property
    def outputPath(self):
        return self._outputPath

    @outputPath.setter
    def outputPath(self, value):
        self._outputPath = value

    @property
    def simulationNameMB(self):
        return self._simulationNameMB

    @simulationNameMB.setter
    def simulationNameMB(self, value):
        self._simulationNameMB = value

    @property
    def numberSamples(self):
        return self._numberSamples

    @numberSamples.setter
    def numberSamples(self, value):
        self._numberSamples = value

    @property
    def prjName(self):
        return self._prjName

    @prjName.setter
    def prjName(self, value):
        self._prjName = value

    @property
    def cam_perspective(self):
        return self._cam_perspective

    @cam_perspective.setter
    def cam_perspective(self, value):
        self._cam_perspective = value

    @property
    def cam_viewcube(self):
        return self._cam_viewcube

    @cam_viewcube.setter
    def cam_viewcube(self, value):
        self._cam_viewcube = value

    @property
    def cam_sphere(self):
        return self._cam_sphere

    @cam_sphere.setter
    def cam_sphere(self, value):
        self._cam_sphere = value

    @property
    def cam_rotation(self):
        return self._cam_rotation

    @cam_rotation.setter
    def cam_rotation(self, value):
        self._cam_rotation = value

    @property
    def cam_custom_name(self):
        return self._cam_custom_name

    @cam_custom_name.setter
    def cam_custom_name(self, value):
        self._cam_custom_name = value

    @property
    def animationStartTime(self):
        return self._animationStartTime

    @animationStartTime.setter
    def animationStartTime(self, value):
        self._animationStartTime = value

    @property
    def animationEndTime(self):
        return self._animationEndTime

    @animationEndTime.setter
    def animationEndTime(self, value):
        self._animationEndTime = value

    @property
    def createCacheCommandString(self):
        return self._createCacheCommandString

    @createCacheCommandString.setter
    def createCacheCommandString(self, value):
        self._createCacheCommandString = value

    @property
    def randomSliderSamples(self):
        return self._randomSliderSamples

    @randomSliderSamples.setter
    def randomSliderSamples(self, value):
        self._randomSliderSamples = value

    @property
    def imageView(self):
        return self._imageView

    @imageView.setter
    def imageView(self, value):
        self._imageView = value

    @property
    def numberOfFrames(self):
        return self._numberOfFrames

    @numberOfFrames.setter
    def numberOfFrames(self, value):
        self._numberOfFrames = value

    """
    sampledValuesString: contains the names of the attributes which the user selected for sampling.
                        e.g: Noise,0.0,1.0;Diffusion,0,2: ...
                        --> <value1,minRange,maxRange;value2,minRange,maxRange;value3,minRange,maxRange>
    """
    @property
    def sampledValuesString(self):
        return self._sampledValuesString

    @sampledValuesString.setter
    def sampledValuesString(self, value):
        self._sampledValuesString = value

    @staticmethod
    def printValues(valuesGeneral):
        lgr = logging.getLogger('FluidExplorerPlugin')

        lgr.info('Project settings:')
        lgr.info("  Proj. Name: %s", str(valuesGeneral.prjName))
        lgr.info("  Output Path: %s", str(valuesGeneral.outputPath))
        lgr.info("  Fluid Container: %s", str(valuesGeneral.fluidBoxName))
        lgr.info("  Num. Samples: %s", str(valuesGeneral.numberSamples))
        lgr.info("  Num. Frames: %s", str(valuesGeneral.numberOfFrames))
        lgr.info("  Scene Name: %s", str(valuesGeneral.simulationNameMB))
        lgr.info("  Available Images: %s", str(valuesGeneral.imageView))
        lgr.info("  Camera Perspective: %s", str(valuesGeneral.cam_perspective))
        lgr.info("  Camera ViewCube: %s", str(valuesGeneral.cam_viewcube))
        lgr.info("  Camera Custom: %s", str(valuesGeneral.cam_sphere) + "/" + str(valuesGeneral.cam_custom_name))
        lgr.info("  Camera Rotation: %s", str(valuesGeneral.cam_rotation))
        lgr.info("  Animation Start Time: %s", str(valuesGeneral.animationStartTime))
        lgr.info("  Animation End Time: %s", str(valuesGeneral.animationEndTime))
        lgr.info("  String Sampled Values: %s", str(valuesGeneral.sampledValuesString))