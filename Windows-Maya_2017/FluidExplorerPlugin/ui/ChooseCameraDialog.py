from PySide2 import QtGui, QtWidgets
from PySide2 import QtCore, QtWidgets

from ChooseCameraUI import Ui_DialogChooseCamer
from Utils.MayaUiDefaultValues import MayaUiDefaultValues
import maya.cmds as cmds


class ChooseCameraDialog(QtWidgets.QDialog):
    selectedCamera = None

    def __init__(self, *args):
        QtWidgets.QDialog.__init__(self, *args)

        # Set up the user interface from Designer
        self.ui = Ui_DialogChooseCamer()
        self.ui.setupUi(self)
        self.ui.pushButtonSelect.setAutoDefault(True)

        # Get the cameras from Maya and fill the combo box
        utils = MayaUiDefaultValues()
        listCameras = utils.getCamerasFromMaya()

        for iIndex, iItem in enumerate(listCameras):
            self.ui.comboBox.addItem(iItem)

        # Eventhandler for the buttons
        self.ui.pushButtonSelect.clicked.connect(self.buttonSelectClicked)
        self.ui.pushButtonCancel.clicked.connect(self.buttonCancelClicked)

    @QtCore.Slot()
    def buttonSelectClicked(self):
        cam = str(self.ui.comboBox.currentText())
        self.selectedCamera = cam
        self.close()

    @QtCore.Slot()
    def buttonCancelClicked(self):
        self.close()

    @property
    def getChoosenCamera(self):
        return self.selectedCamera

    def getCamerasFromMaya(self):
        allCameras = cmds.listCameras()
        camerasList = allCameras

        return camerasList
