from PySide import QtGui
from PySide import QtCore


class SliderContainerLayout(QtGui.QWidget):

    def __init__(self):
        QtGui.QWidget.__init__(self)

        # Header
        self.gridLayout_Box = QtGui.QGridLayout()
        self.gridLayout_Box.setSpacing(8)
        self.gridLayout_Box.addWidget(QtGui.QLabel("<b>Range&nbsp;&nbsp;&nbsp;</b>"), 0, 2, QtCore.Qt.AlignCenter)
        self.gridLayout_Box.addWidget(QtGui.QLabel("<b>Def.</b>"), 0, 4, QtCore.Qt.AlignCenter)
        self.gridLayout_Box.addWidget(QtGui.QLabel("<b>Min</b>"), 0, 5, QtCore.Qt.AlignCenter)
        self.gridLayout_Box.addWidget(QtGui.QLabel("<b>Max</b>"), 0, 13, QtCore.Qt.AlignCenter)

        self.resetButton = QtGui.QPushButton("Reset all Values")
        self.resetButton.clicked.connect(self.resetButton_Event)

        self.sliderList = list()
        self.fluidBoxName = ""

    def resetButton_Event(self, sliderList):
        self.reset(sliderList)

    def reset(self, sliderList):
        for listItem in sliderList:
            listItem.resetValues()

    def setFluidBoxName(self, boxName):
        self.fluidBoxName = boxName