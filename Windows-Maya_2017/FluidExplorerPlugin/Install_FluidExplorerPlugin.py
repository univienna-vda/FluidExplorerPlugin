########################################################################################################################
#                                                                                                                      #
#   This file creates the Fluid Explorer plugin icons within the Maya toolbar and                                       #
#   returns the main window instance.                                                                                  #
#                                                                                                                      #
#   Please execute the file from the python script editor in Maya                                                      #
#                                                                                                                      #
########################################################################################################################

import maya.cmds as cmds
import maya.mel 
import os.path 
 
import FluidExplorerPlugin.FluidMain


def get_script_folfer():
    scriptDir = cmds.internalVar(userScriptDir=True)
    path_fx = scriptDir + "FluidExplorerPlugin/ui/Icons/fx_32px.png"
    path_help = scriptDir + "FluidExplorerPlugin/ui/Icons/help_32px.png"
    path_icon_fx = '"' + path_fx + '"'
    path_icon_help = '"' + path_help + '"'
    
    if not os.path.isfile(path_fx):
       return [ "", "" ]
    if not os.path.isfile(path_help):
       return [ "", "" ]
    
    return [ path_icon_fx, path_icon_help ]

def create_fluidExplorer_shelf_text_only():
    maya.mel.eval('if (`shelfLayout -exists FluidExplorer `) deleteUI FluidExplorer;')
    shelfTab = maya.mel.eval('global string $gShelfTopLevel;')
    maya.mel.eval('global string $scriptsShelf;')
    maya.mel.eval('$scriptsShelf = `shelfLayout -p $gShelfTopLevel FluidExplorer`;')
    
    maya.mel.eval('shelfButton -parent $scriptsShelf -annotation "Fluid Explorer" ' + '-label "FluidExplorer" -sourceType "python" ' + '-command ("fluidExplorerWin = FluidExplorerPlugin.FluidMain.main(); fluidExplorerWin.show()") -style "textOnly";')
    maya.mel.eval('shelfButton -parent $scriptsShelf -annotation "Help" ' + '-label "Help" -sourceType "python" ' + '-command ("FluidExplorerPlugin.FluidMain.helpButton();") -style "textOnly";')
          
def create_fluidExplorer_shelf():
    try:
        maya.mel.eval('if (`shelfLayout -exists FluidExplorer `) deleteUI FluidExplorer;')
        shelfTab = maya.mel.eval('global string $gShelfTopLevel;')
        maya.mel.eval('global string $scriptsShelf;')
        maya.mel.eval('$scriptsShelf = `shelfLayout -p $gShelfTopLevel FluidExplorer`;')
        
        [ path_icon_fx, path_icon_help ] = get_script_folfer()
        iconFX = '-image ' + path_icon_fx
        iconHelp = '-image ' + path_icon_help
        
        cmd_fx = 'shelfButton -parent $scriptsShelf -annotation "Fluid Explorer" ' + '-label "FluidExplorer"' + iconFX + '-sourceType "python" ' +'-command ("fluidExplorerWin = FluidExplorerPlugin.FluidMain.main(); fluidExplorerWin.show()");'
        cmd_help = 'shelfButton -parent $scriptsShelf -annotation "Help" ' + '-label "FluidExplorer"' + iconHelp + '-sourceType "python" ' +'-command ("FluidExplorerPlugin.FluidMain.helpButtonToolBar();");'
        
        maya.mel.eval(cmd_fx)
        maya.mel.eval(cmd_help)

        maya.mel.eval('catchQuiet(jumpToNamedShelf("FluidExplorer"))')
    
    except:
        create_fluidExplorer_shelf_text_only()

#
# Run FluidExplorer
#
fluidExplorerWin = FluidExplorerPlugin.FluidMain.main()
if fluidExplorerWin:
    fluidExplorerWin.show()

#
# Create shelf buttons
#
create_fluidExplorer_shelf()
