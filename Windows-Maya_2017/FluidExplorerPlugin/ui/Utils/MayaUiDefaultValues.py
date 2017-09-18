import math
import maya.cmds as cmds


class MayaUiDefaultValues(object):

    def __init__(self):
        pass

    def getAnimationStartEnd(self):
        minValue = cmds.playbackOptions(q=True, animationStartTime=True)
        maxValue = cmds.playbackOptions(q=True, animationEndTime=True)

        self.animationMinTime = math.floor(minValue)
        self.animationEndTime = math.floor(maxValue)

    def getCamerasFromMaya(self):
        allCameras = cmds.listCameras()
        camerasList = allCameras

        return camerasList