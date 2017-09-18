# Fluid Explorer - Maya plugin

Maya Plugin for creating and loading fluid simulations as well as for rendering
the simulation from different viewpoints. 

## Development

The plugin is based on python (version 2.7). The project was created with the
PyCharm IDE. Please note that the *.idea* folder stores local configuration settings for PyCharm.

Code which still has to be developed / adapted is tagged with the *TODO* keyword.

The UI elements were developed with the Qt designer. In order to create a *.py* file based
on a *.ui* file please use the following command: *pyside-uic file.ui -o file.py*

## Installation

Place the project in the *scripts* subdirectory of the module's root directory. 
The location of the scripts directory is: MAYA_APP_DIR/\<version\>/scripts

The default values for the MAYA_APP_DIR variable are:

* **Windows (>= Windows Vista):** \Users\<username>\Documents\maya
* **Mac OS X:** ~<username>/Library/Preferences/Autodesk/maya
* **Linux (64-bit):** ~<username>/maya

Example (Windows):  ... \Documents\maya\2014-x64\scripts

## Plugin structure

After copying the project files into the *scripts* subdirectory, the directory structure 
should look like this:

    |-- MAYA_APP_DIR
    |   |-- <version>
    |       |-- scripts
    |           |-- FluidExplorerPlugin
    |               |-- FluidMain.py
    |               |-- Install_FluidExplorerPlugin.py
    |               |-- ...
    
The *FluidExplorerPlugin* directory contains the source files of the plugin. 
The *FluidMain.py* file calls the plugin within the Maya application and
the *Install_FluidExplorerPlugin.py* script creates the shelf buttons 
within the Maya toolbar.

## Run the plugin

In order to install the plugin, open the Script Editor in Maya. Nagivate to
Window > General Edotors > Script Editor or open the editor by hitting the 
Script Editor button in the bottom right corner. In order to install the plugin 
and create the shortcuts in the toolbar, open
to the *Install_FluidExplorerPlugin.py* script and execute it in the editor.

Please note that the plugin has to be installed again, after the Maya application 
has been closed. 

## Run tests

In order to run a test please read the instructions in the *Test.py* file which 
is located in: FluidExplorerPlugin/ui/Test/Test.py 

## External tools

The Fluid Explorer plugin uses two external tools. Please be sure that the tools 
are located in the following directory:

    |-- FluidExplorerPlugin
    |   |-- lib
    |       |-- ffmpeg
    |            |-- x64
    |                |-- ffmpeg.exe (executable)
    |            |-- x86
    |                |-- ffmpeg.exe (executable)
    |       |-- fluidexplorer
    |           |-- fluidExplorer.exe (executable)
    |           |-- ...

**ffmpeg**: Contains the FFmpge tool in order to create GIF animations. Please check
whether the correct build is used for your system (operating system / architecture). 

**fluidexplorer**: Contains the stand-alone Fluid Explorer application. Please note that 
the tools is located in another repository (*fluidexplorer-application*). This repository
does not contain the executable or sources files. For more details please see: 
http://gitlab.cs.univie.ac.at.

## Adaptations for Maya 2017 

The plugin is based on Pyside which provides LGPL-licensed Python bindings for Qt.
For the Maya versions 2014-2016 the plugin is based on Qt4 and PySide. Since 
Maya 2017 only supports Qt5, the plugin code has to be converted from PySode to 
PySide2. Therefore, the following conversion tool is used: *topyside2.py*
Please use the script which is provided in this repository: https://github.com/clamdragon/pyqt4topyqt5

**Usage (PySide to PySide2)**: 
-   Open the Python interpreter
-   Load the *topyside2.py* script: sys.path.append('path/to/dir')
-   Import module: from topyside2 import *
-   Call main method: Main('path/to/scr') - e.g.: Main('.../FluidExplorerPlugin') -> .../FluidExplorerPlugin_PySide2

## Other

Additional content of the project can be found in the VDA owncloud: https://vdaowncloud.cs.univie.ac.at/