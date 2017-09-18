import os
import logging

import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel


class MayaFunctionUtils(object):

    def __init__(self):
        self.finished = False

        # Logging
        self.lgr = logging.getLogger('FluidExplorerPlugin')


    def getObjType(self, selection):
        t = cmds.objectType(selection)

        if t == "fluidShape":
            return t
        else:
            # objType = `listRelatives -s $selection`;
            objType = cmds.listRelatives(selection, s=True)
            if objType == None:
                return ""
            else:
                return cmds.nodeType(objType[0])

    def getSelectedContainerPy(self):
        selectedObjName = cmds.ls(sl=True)

        count_fluidShape = 0
        index_fluidShape = -1

        lenSelObj = len(selectedObjName)

        for i, item in enumerate(selectedObjName):
            res = self.getObjType(str(item))
            if res == "fluidShape" or res == "flameShape":
                count_fluidShape += 1
                index_fluidShape = i
        
        if int(lenSelObj) == 0:
            return [False, "Please select a valid Fluid Container first!", ""]

        elif int(count_fluidShape) >= 2:
            return [False, "Please select one Fluid Container only!", ""]

        else:
            if int(count_fluidShape) == 1:

                currentObj = selectedObjName[int(index_fluidShape)]
                nodetype = cmds.nodeType(currentObj)

                containerName = ''
                if nodetype == 'transform':
                    lr = cmds.listRelatives(currentObj, children=True)
                    if len(lr) >= 1:
                        containerName = lr[0]
                else:
                    containerName = currentObj

                # containerName = fluid node
                # currentObj = transform node
                return [True, containerName, currentObj]

            else:
                return [False, "Please select an valid Fluid Container!", ""]

    def createFluid(self, cmdStr, progressbar):
        try:
            pm.mel.eval(cmdStr)

        except Exception as e:
            self.lgr.error('An error occured while the cache files were created! Details: %s', e.message)
            raise Exception(e.message)

    def setSampledValue(self, fluidName, values):
        """
        :type values: ContainerValuesList
        """

        self.lgr.info('Set sampled values for: %s', fluidName)

        members = [attr for attr in dir(values) if not callable(values) and not attr.startswith("__")]
        for item in members:

            tmpCmd = fluidName + "." + str(item)
            try:
                attributeValue = float(getattr(values, item))
            except Exception as e:
                self.lgr.warning('Cannot read fluid attribute: %s - Details: %s', tmpCmd, e.message)

            # Set the attribute in the fluid container dialog
            attrExists = cmds.attributeQuery(item, node=fluidName, exists=True)
            if attrExists:
                try:
                    cmds.setAttr(tmpCmd, attributeValue)
                    # print(str(item), attributeValue)
                    # self.lgr.info('%s - %s', str(item), attributeValue)
                except Exception as e:
                    self.lgr.warning('Cannot set fluid attribute: %s - Details: %s', tmpCmd, e.message)

            else:
                self.lgr.warning('Fluid attribute %s does not exist', item)

    def changeToPerspCam(self):
        currentCam = cmds.lookThru(q=True)
        if currentCam != 'persp':
            # Select the perspective camera (default = modelPfloatanel4)attributeValue
            cmdStr = "lookThroughModelPanel" + " " + "persp" + " " + "modelPanel4;"
            mel.eval(cmdStr)
            cmds.lookThru('persp')


    def viewFromCamPosition(self, positionName, containerName):
        self.changeToPerspCam()

        cmd = ""
        if (positionName =='PERSPECTIVE'):
            cmd = "viewSet -animate `optionVar -query animateRollViewCompass` -p"
            #cmds.viewSet(p=True, an=False);
        elif (positionName == 'TOP'):
            cmd = "viewSet -animate `optionVar -query animateRollViewCompass` -top"
        elif (positionName == 'BOTTOM'):
            cmd = "viewSet -animate `optionVar -query animateRollViewCompass` -bottom"
        elif (positionName == 'RIGHT'):
            cmd = "viewSet -animate `optionVar -query animateRollViewCompass` -rightSide"
        elif (positionName == 'LEFT'):
            cmd = "viewSet -animate `optionVar -query animateRollViewCompass` -leftSide"
        elif (positionName == 'FRONT'):
            cmd = "viewSet -animate `optionVar -query animateRollViewCompass` -front"
        elif (positionName == 'BACK'):
            cmd = "viewSet -animate `optionVar -query animateRollViewCompass` -back"

        cmds.select(containerName)

        # Execute MEL command
        mel.eval(cmd)
        cmds.viewFit(an=False)

    def renderImagesFromCameras(self, generalSettings, fluidIndex, gMainProgressBar, progressIndex):
        """
        :type generalSettings: MayaCacheCmdSettings
        """
        listRenderedImages = list()

        self.viewFromCamPosition('PERSPECTIVE', generalSettings.fluidBoxName)

        renderImageFlag = False    # True --> Images are rendered
        if (generalSettings.cam_perspective) == True | (generalSettings.cam_viewcube == True) | (generalSettings.cam_custom_name != None) | (generalSettings.cam_rotation != 0):
            renderImageFlag = True

        # Create image folder
        path = generalSettings.outputPath + "/" + str(fluidIndex) + "/images/"
        if not os.path.exists(path) & renderImageFlag:
            os.mkdir(path)

        # Settings
        fileName = "image"
        start = str(int(round(generalSettings.animationStartTime)))
        end = str(int(round(generalSettings.animationEndTime)))

        if generalSettings.cam_perspective:
            self.viewFromCamPosition('PERSPECTIVE', generalSettings.fluidBoxName)
            path = generalSettings.outputPath + "/" + str(fluidIndex) + "/images/perspective/"
            listRenderedImages.append(path)

            try:
                os.mkdir(path)
            except Exception as e:
                self.lgr.warning('Cannot create directory: %s - Details: %s', path, e.message)

            mel.eval('RenderIntoNewWindow')

            # Rendering
            try:
                cmds.progressBar(gMainProgressBar, edit=True, step=1, status="Render images - Perspective Camera")
                self.renderImages(path, fileName, start, end)
            except Exception as e:
                raise e
                cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
                return

        if (generalSettings.cam_viewcube == True):
            # os.mkdir(generalSettings.outputPath + "/" + str(fluidIndex) + "/images/viewcube/")

            # FRONT
            self.viewFromCamPosition('FRONT', generalSettings.fluidBoxName)
            path = generalSettings.outputPath + "/" + str(fluidIndex) + "/images/vc_front/"
            listRenderedImages.append(path)

            try:
                os.mkdir(path)
            except Exception as e:
                self.lgr.warning('Cannot create directory: %s - Details: %s', path, e.message)

            mel.eval('RenderIntoNewWindow')

            # Rendering
            try:
                cmds.progressBar(gMainProgressBar, edit=True, step=1, status="Render images - View Cube Front")
                self.renderImages(path, fileName, start, end)
            except Exception as e:
                raise e
                cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
                return

            # RIGHT
            self.viewFromCamPosition('RIGHT', generalSettings.fluidBoxName)
            path = generalSettings.outputPath + "/" + str(fluidIndex) + "/images/vc_side/"
            listRenderedImages.append(path)

            try:
                os.mkdir(path)
            except Exception as e:
                self.lgr.warning('Cannot create directory: %s - Details: %s', path, e.message)

            mel.eval('RenderIntoNewWindow')

            # Rendering
            #self.renderImages(path, fileName, start, end)
            try:
                cmds.progressBar(gMainProgressBar, edit=True, step=1, status="Render images - View Cube Right")
                self.renderImages(path, fileName, start, end)
            except Exception as e:
                raise e
                cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
                return

            # TOP
            self.viewFromCamPosition('TOP', generalSettings.fluidBoxName)
            path = generalSettings.outputPath + "/" + str(fluidIndex) + "/images/vc_top/"
            listRenderedImages.append(path)

            try:
                os.mkdir(path)
            except Exception as e:
                self.lgr.warning('Cannot create directory: %s - Details: %s', path, e.message)

            mel.eval('RenderIntoNewWindow')

            try:
                cmds.progressBar(gMainProgressBar, edit=True, step=1, status="Render images - View Cube Top")
                self.renderImages(path, fileName, start, end)
            except Exception as e:
                raise e
                cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
                return

        if (generalSettings._cam_custom_name != None):
            # View from camera
            try:
                cmdStr = "lookThroughModelPanel" + " " + str(generalSettings.cam_custom_name) + " " + "modelPanel4;"
                mel.eval(cmdStr)
            except Exception as er:
                self.lgr.error('An error occured while camera was changed! Details: %s', er.message)
                self.lgr.error('Could not look through camera %s', generalSettings._cam_custom_name)
                raise Exception(er.message)
                return

            #cmdStr = "lookThroughModelPanel" + " " + str(generalSettings.cam_custom_name) + " " + "modelPanel4;"
            #mel.eval(cmdStr)

            path = generalSettings.outputPath + "/" + str(fluidIndex) + "/images/custom/"

            try:
                os.mkdir(path)
            except Exception as e:
                self.lgr.warning('Cannot create directory: %s - Details: %s', path, e.message)

            mel.eval('RenderIntoNewWindow')

            try:
                cmds.progressBar(gMainProgressBar, edit=True, step=1, status="Render images ... - Custom Camera")
                self.renderImages(path, fileName, start, end)
            except Exception as e:
                raise e
                cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
                return

            listRenderedImages.append(path)

            self.viewFromCamPosition('PERSPECTIVE', generalSettings.fluidBoxName)

        if generalSettings.cam_rotation != 0:

            # Change to perspective camera
            self.viewFromCamPosition('PERSPECTIVE', generalSettings.fluidBoxName)
            cmds.viewFit('persp', an=False)

            # path = generalSettings.outputPath + "/" + str(fluidIndex) + "/images/rotation/"
            # os.mkdir(path)

            # Rotate
            stepAcc = 0
            valueY = int(round(float(generalSettings.cam_rotation)))

            while stepAcc < 360:
                # Rotate camera
                cmds.setAttr('persp.rotateY',  stepAcc)
                cmds.viewFit('persp', an=False)
                # cmds.dolly(d=-15)

                path = generalSettings.outputPath + "/" + str(fluidIndex) + "/images/rotation_" + str(stepAcc) + "/"
                try:
                    os.mkdir(path)
                except Exception as e:
                    self.lgr.warning('Cannot create directory: %s - Details: %s', path, e.message)

                mel.eval('RenderIntoNewWindow')

                try:
                    cmds.progressBar(gMainProgressBar, edit=True, step=1, status="Render images ... - Rotating Camera")
                    self.renderImages(path, fileName, start, end)
                except Exception as e:
                    raise e
                    cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
                    return

                listRenderedImages.append(path)
                stepAcc = stepAcc + valueY

        cmds.viewFit('persp', an=False)

        return [int(progressIndex), listRenderedImages]

    def rotateCamerY(valueY):
        stepAcc = 0
        while stepAcc < 360:
            stepAcc = stepAcc + valueY
            cmds.setAttr('persp.rotateY',  stepAcc)
            cmds.viewFit('persp', an=False)

    def startPosition(self, generalSettings):
        self.viewFromCamPosition('PERSPECTIVE', generalSettings.fluidBoxName)

    """
    def executeMELRemderCmd(self, path, fileName, start, end, resW, resH):
        cmd = "renderImagesMEL(" + "\"" + path + "\"" + "," + "\"" + fileName + "\"" + "," + str(start) + "," + str(end) + "," + str(resW) + "," + str(resH) + ")"
        mel.eval(cmd)
    """

    def renderImages(self, path, filename, startFrame, endFrame, resWidth=960, resHeight=540):

        renderSuccess = True

        # print path
        # print filename
        # print startFrame
        # print endFrame
        # print resWidth
        # print resHeight

        self.lgr.info('Rendering started: %s', path)

        resWidth = 960
        resHeight = 540

        cmds.setAttr('defaultRenderGlobals.currentRenderer', 'mayaSoftware', type='string')
        cmds.setAttr('defaultResolution.width', resWidth)
        cmds.setAttr('defaultResolution.height', resHeight)
        cmds.setAttr('perspShape.renderable', 1);
        cmds.setAttr('defaultRenderGlobals.imageFormat', 8)
        cmds.setAttr('defaultRenderGlobals.byFrameStep ', 1.0)

        # Check render panel
        renderPanel = ""
        renderPanels = mel.eval('getPanel -scriptType "renderWindowPanel";')

        if len(renderPanels) >= 1:
            renderPanel = renderPanels[0]
        else:
            renderPanel = mel.eval('scriptedPanel -type "renderWindowPanel" -unParent renderView;')
            melCmd = 'scriptedPanel -e -label "Render View" ' + renderPanel + ';'
            #mel.eval('scriptedPanel -e -label "Render View" $renderPanel;')
            mel.eval(melCmd)

        cmds.setAttr('defaultRenderGlobals.imageFormat', 8)
        cmds.setAttr('defaultRenderGlobals.extensionPadding', 5)
        cmds.setAttr('defaultRenderGlobals.imageFilePrefix', "image", type='string')

        # Start and End Frame
        startFrom = int(startFrame)
        renderTill = int(endFrame)

        mel.eval('currentTime %s ;'%(startFrom))

        while(startFrom<=renderTill):

            frameNumber = '{0:05d}'.format(startFrom)
            concatenateFileName = path + 'image_' + frameNumber + ".jpg"
            concatenateFileName = concatenateFileName.replace('\\', '/')

            if os.path.exists(concatenateFileName):
                os.remove(concatenateFileName)

            melCmd = 'renderWindowRender redoPreviousRender' + ' ' + renderPanel + ';'
            mel.eval(melCmd)
            #mel.eval('renderWindowRender redoPreviousRender renderView;')
            startFrom += 1
            mel.eval('currentTime %s ;'%(startFrom))

            renderViewValue = renderPanel
            melStrCmd = 'catchQuiet(renderWindowSaveImageCallback("' + renderViewValue +'", "' + concatenateFileName +'", `getAttr defaultRenderGlobals.imageFormat`))'

            try:
                mel.eval(melStrCmd)
            except RuntimeError as err:
                self.lgr.error('An error occured while the images were rendered! Details: %s', err.message)
                raise Exception(err.message)
                renderSuccess = False
                return renderSuccess

            except Exception as er:
                self.lgr.error('An error occured while the images were rendered! Details: %s', er.message)
                raise Exception(er.message)
                renderSuccess = False
                return renderSuccess

        return renderSuccess