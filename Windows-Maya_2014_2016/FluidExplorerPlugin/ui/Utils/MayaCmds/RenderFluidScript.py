import maya.cmds as cmds
import maya.mel as mel

# NOT IN USE
class RenderFluidScript():

    def __init__(self):
        pass

    def renderImages(self, path, filename, startFrame, endFrame, resWidth = 960, resHeight = 540):

        resWidth = int(resWidth)
        resHeight = int(resHeight)

        #print path
        #print filename
        #print startFrame
        #print endFrame
        #print resWidth
        #print resHeight

        cmds.setAttr('defaultRenderGlobals.currentRenderer', 'mayaSoftware', type='string')
        cmds.setAttr('defaultResolution.width', resWidth)
        cmds.setAttr('defaultResolution.height', resHeight)
        cmds.setAttr('perspShape.renderable', 1)
        cmds.setAttr('defaultRenderGlobals.imageFormat', 8)
        cmds.setAttr('defaultRenderGlobals.byFrameStep ', 1.0)

        renderPanel = ""
        renderPanels = mel.eval('getPanel -scriptType "renderWindowPanel";')

        if len(renderPanels) >= 1:
            renderPanel = renderPanels[0]
        else:
            mel.eval('scriptedPanel -type "renderWindowPanel" -unParent renderView;')
            mel.eval('scriptedPanel -e -label "Render View" $renderPanel;')

        cmds.setAttr('defaultRenderGlobals.imageFormat', 8)
        cmds.setAttr('defaultRenderGlobals.extensionPadding', 5)
        fileName = "imgage"
        cmds.setAttr('defaultRenderGlobals.imageFilePrefix', fileName, type='string')

        startFrom = startFrame
        renderTill = endFrame

        mel.eval('currentTime %s ;'%(startFrom))
        while startFrom <= renderTill:

            frameNumber = format(startFrom, '05')
            concatenateFileName = path + '/' + filename + '_' + str(frameNumber) + ".jpg"

            mel.eval('renderWindowRender redoPreviousRender' + ' ' + renderPanel + ';')
            cmd = 'catch(eval(renderWindowSaveImageCallback (_QM_renderView_QM_,' + '_QM_' + concatenateFileName + '_QM_' + ', 8)));'
            cmdMEL = cmd.replace('_QM_', "\"")
            mel.eval(cmdMEL)

            startFrom += 1
            mel.eval('currentTime %s ;'%(startFrom))

"""
#  -- TEST --
#path = "E:/TMP/XXX"
#filename = "image"
#startFrame = 10
#endFrame = 15
#renderImages(path, filename, startFrame, endFrame, resWidth=960, resHeight=540)
"""

