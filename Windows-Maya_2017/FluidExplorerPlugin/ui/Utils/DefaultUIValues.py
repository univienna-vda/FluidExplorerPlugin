# Stores the default values/stylesof the create project dialog and the main dialog
class DefaultUIParameters(object):

    #
    # QSS styles
    #

    # Camera button selected or not selected
    StyleSheet_Button_Off = "QPushButton { background-color: None; border: 3px solid grey; border-radius: 5px; }"
    StyleSheet_Button_On  = "QPushButton { background-color: None; border: 3px solid rgb(255,160,47); border-radius: 5px;s}"

    # Size of OK button in message box
    buttonStyleBold = "QPushButton{min-width: 70px;} QMessageBox{font-size: 12px;}"

    # Horizontal slider in ParameterTab view
    @staticmethod
    def getCustomSliderStyleSheet(disabled):

        sliderStyleSheet = ("QSlider::groove:horizontal {"
            "border: 1px solid #999999;"
            "height: 11px;"
            "background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);"
            "margin: 2px 0;"
            "}"
            "QSlider::handle:horizontal {"
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgb(255, 160, 47), stop:1 rgb(255, 148, 22));"
            "border: 1px solid #5c5c5c;"
            "width: 18px;"
            "margin: -2px 0; /* handle is placed by default on the contents rect of the groove. Expand outside the groove */"
            "border-radius: 3px;"
            "}"

            "QSlider::sub-page:qlineargradient {"
            "border: 1px solid #999999;"
            "height: 8px; /* the groove expands to the size of the slider by default. by giving it a height, it has a fixed size */"
            "/*background: rgb(255, 160, 47);*/"
            "margin: 2px 0;"
            "}")

        sliderStyleSheet_Disabled = ("QSlider::groove:horizontal {"
            "border: 1px solid #999999;"
            "height: 11px;"
            "background: transparent;"
            "margin: 2px 0;"
            "}"

            "QSlider::handle:horizontal {"
            "background: rgb(70,70,70);"
            "border: 1px solid #999999;"
            "width: 18px;"
            "margin: -2px 0;"
            "border-radius: 3px;"
            "}"
            )

        if disabled:
            return sliderStyleSheet_Disabled
        else:
            return sliderStyleSheet

    #
    # Defalt values
    #

    # Project name
    DEF_SIMULATION_NAME = "Untitled"

    # Camera rotations (degrees)
    DEF_SPIN_ROT_MIN = 10
    DEF_SPIN_ROT_MAX = 90
    DEF_SPIN_ROT = 45

    # Slider: Number of Sequences
    DEF_NUMBER_SEQUENCES = 15
    DEF_NUMBER_SEQUENCES_MIN = 1
    DEF_NUMBER_SEQUENCES_MAX = 200

    # Url to the help page
    URL = "http://fluidexplorer.cs.univie.ac.at/"