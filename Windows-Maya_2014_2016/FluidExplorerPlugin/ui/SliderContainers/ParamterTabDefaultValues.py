import maya.cmds as cmds


class ParameterTabDefaultValues:

    def __init__(self):
       pass

    @staticmethod
    def setSoftMinMaxValue(fieldName, nodeName):
        # Some values do not have a sotft min / max -> set manually

        # Dynaimc Simulation
        if fieldName == 'viscosity':
            minSoft = 0
            maxSoft = 1
        # Velocity
        elif fieldName == 'velocitySwirl':
            minSoft = 0
            maxSoft = 10
        # Turbulence
        elif fieldName == 'turbulenceStrength':
            minSoft = 0
            maxSoft = 1
        elif fieldName == 'turbulenceFrequency':
            minSoft = 0
            maxSoft = 2
        elif fieldName == 'turbulenceSpeed':
            minSoft = 0
            maxSoft = 2

        else:
            minSoft = cmds.attributeQuery(fieldName, node=nodeName, softMin=True)
            maxSoft = cmds.attributeQuery(fieldName, node=nodeName, softMax=True)
            minSoft = minSoft[0]
            maxSoft = maxSoft[0]

        return [minSoft, maxSoft]
