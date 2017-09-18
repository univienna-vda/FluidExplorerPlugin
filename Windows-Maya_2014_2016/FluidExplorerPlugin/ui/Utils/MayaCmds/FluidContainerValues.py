import maya.cmds as cmds


class ContainerValuesUtils():
    
    def __init__(self, fluidName):
        self.fluidName = fluidName

    def setFluidContainerParameter(self, property, paramterValue):
        tmpCmd = self.fluidName + '.' + property
        cmds.setAttr(tmpCmd, paramterValue)
        
    def getFluidContainerParamter(self, property):
        tmpCmd = self.fluidName + '.' + property
        paramterValue = round(cmds.getAttr(tmpCmd), 3)
        return paramterValue

    def getSliderLockedState(self, label):
        return cmds.getAttr(label, se=True)
