import xml.etree.ElementTree as xml


class XmlFileWriter():

    path = ""
    elementName = ""

    projectPath = ""
    projectName = ""
    fluidBoxName = ""
    mayaFilePath = ""
    numberOfSamppes = ""
    numberOfFrames = ""
    imageView = ""
    perspectiveCamera = ""
    viewCubeCamera = ""
    customCamera = ""
    rotationCamera = ""
    animationStartTime = ""
    animationEndTime = ""
    sampledValuesNameRange = ""

    def __init__(self):
        pass

    def setXmlDocPath(self, path, elementName):
        self.path = path
        self.elementName = elementName

    # This method writes the properties in the xml file
    def writeValuesInFile(self):
        # Add root
        #root = xml.Element("ProjectSettings")
        appt = xml.Element(self.elementName)

        # Add children (project settings)
        el_ProjectPath = xml.SubElement(appt, "ProjectPath")
        el_ProjectPath.text = self.projectPath
        #xml.SubElement(appt,'\n')

        el_ProjectName = xml.SubElement(appt, "ProjectName", )
        el_ProjectName.text = self.projectName

        el_FluidBoxName = xml.SubElement(appt, "FluidBoxName")
        el_FluidBoxName.text = self.fluidBoxName

        el_FluidBoxName = xml.SubElement(appt, "MayaFilePath")
        el_FluidBoxName.text = self.mayaFilePath

        el_Samples = xml.SubElement(appt, "Samples")
        el_Samples.text = self.numberOfSamppes

        el_NumberOfFrames = xml.SubElement(appt, "NumberOfFrames")
        el_NumberOfFrames.text = self.numberOfFrames

        el_ImageView = xml.SubElement(appt, "ImageView")
        el_ImageView.text = self.imageView

        el_PerspectiveCamera = xml.SubElement(appt, "PerspectiveCamera")
        el_PerspectiveCamera.text = self.perspectiveCamera

        el_ViewCubeCamera = xml.SubElement(appt, "ViewCubeCamera")
        el_ViewCubeCamera.text = self.viewCubeCamera

        el_ViewCubeCamera = xml.SubElement(appt, "CustomCamera")
        el_ViewCubeCamera.text = self.customCamera

        el_RotationCamera = xml.SubElement(appt, "RotationCamera")
        el_RotationCamera.text = self.rotationCamera

        el_AnimationStartTime = xml.SubElement(appt, "AnimationStartTime")
        el_AnimationStartTime.text = self.animationStartTime

        el_AnimationEndTime = xml.SubElement(appt, "AnimationEndTime")
        el_AnimationEndTime.text = self.animationEndTime

        el_SampledValuesNameRange = xml.SubElement(appt, "SampledValuesNameRange")
        el_SampledValuesNameRange.text = self.sampledValuesNameRange

        self.indent(appt)

        # Create file
        tree = xml.ElementTree(appt)

        try:
            with open(self.path, "w") as fh:
                tree.write(fh, encoding="utf-8", xml_declaration=True)
                return True
        except:
            return False

    # Source:
    # http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    def indent(self, elem, level=0):
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    # Add nodes
    def writeSettingToXmlFile(self, projectSetting):

        self.addElement_ProjectPath(projectSetting.outputPath)
        self.addElement_ProjectName(projectSetting.prjName)
        self.addElement_FluidBoxName(projectSetting.fluidBoxName)
        self.addElement_NumberOfSamples(projectSetting.numberSamples)
        self.addElement_NumberOfFrames(projectSetting.numberOfFrames)
        self.addElement_ImageView(projectSetting.imageView)
        self.addElement_PerspectiveCamera(projectSetting.cam_perspective)
        self.addElement_ViewCubeCamera(projectSetting.cam_viewcube)
        self.addElement_CustomCamera(projectSetting.cam_custom_name)
        self.addElement_RotationCamera(projectSetting.cam_rotation)
        self.addElement_MayaFilePath(projectSetting.simulationNameMB)
        self.addElement_AnimationStartTime(projectSetting.animationStartTime)
        self.addElement_AnimationEndTime(projectSetting.animationEndTime)
        self.addElement_SampledValuesNameRange(projectSetting.sampledValuesString)

        self.writeValuesInFile()

    def addElement_ProjectPath(self, value):
        self.projectPath = str(value)

    def addElement_ProjectName(self, value):
        self.projectName = str(value)

    def addElement_FluidBoxName(self, value):
        self.fluidBoxName = str(value)

    def addElement_MayaFilePath(self, value):
        self.mayaFilePath = str(value)

    def addElement_NumberOfSamples(self, value):
        self.numberOfSamppes = str(value)

    def addElement_NumberOfFrames(self, value):
        self.numberOfFrames = str(value)

    def addElement_ImageView(self, value):
        self.imageView = str(value)

    def addElement_PerspectiveCamera(self, value):
        self.perspectiveCamera = str(value)

    def addElement_ViewCubeCamera(self, value):
        self.viewCubeCamera = str(value)

    def addElement_CustomCamera(self, value):
        self.customCamera = str(value)

    def addElement_RotationCamera(self, value):
        self.rotationCamera = str(value)

    def addElement_AnimationStartTime(self, value):
        self.animationStartTime = str(value)

    def addElement_AnimationEndTime(self, value):
        self.animationEndTime = str(value)

    def addElement_SampledValuesNameRange(self, value):
        self.sampledValuesNameRange = str(value)
