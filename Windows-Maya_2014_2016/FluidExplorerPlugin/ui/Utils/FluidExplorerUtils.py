import os
import ConfigParser
import subprocess
import xml.etree.cElementTree as ET
import sys
import logging
import shutil

import maya.cmds as cmds
import maya.mel as mel


class FluidExplorerUtils(object):

    @staticmethod
    def dirExists(path):
        exists = os.path.exists(path)
        return exists

    @staticmethod
    def readAttributeFromConfigurationFile(choosenDir, category, attribute):
        config = ConfigParser.ConfigParser()
        config.read(choosenDir)

        result = config.get(category, attribute)
        return result

    @staticmethod
    def readAttributeFromXmlConfigurationsFile(xml_file, childName):
        try:
            tree = ET.ElementTree(file=xml_file)
            root = tree.getroot()

            for child in root:
                if child.tag.lower() == childName.lower():
                    el_child_text = child.text

                    return el_child_text
        except:
            lgr = logging.getLogger('FluidExplorerPlugin')
            lgr.warning("Cannot read XML attribute")

    @staticmethod
    def containerIsCorrect(containerName):

        nodeName = containerName
        objectExists = cmds.objExists(nodeName)
        attrExists = cmds.attributeQuery('gravity', node=nodeName, exists=True)

        containerOK = objectExists and attrExists

        if not containerOK:
            lgr = logging.getLogger('FluidExplorerPlugin')
            lgr.error("Cannot select container attribute! Please check the nodeName and the container type")

        return containerOK

    @staticmethod
    def checkIfFFmpgeIsExectuable(pathToFFmpeg):
        if sys.platform.startswith('win'):
            pathToFFmpeg = pathToFFmpeg + "/ffmpeg.exe"
        else:
            pathToFFmpeg = pathToFFmpeg + "/ffmpeg"
            pass

        if not os.path.exists(pathToFFmpeg):
            lgr = logging.getLogger('FluidExplorerPlugin')
            lgr.error("Fatal Error: Cannot find ffmpeg path.")
            lgr.error("Please check if executable file exists: %s", pathToFFmpeg)
            return False

        try:
            subprocess.call([pathToFFmpeg], shell=True)
        except OSError as e:
            if e.errno == os.errno.ENOENT:
                # Handle file not found error.
                lgr = logging.getLogger('FluidExplorerPlugin')
                lgr.error("Fatal Error: Cannot find ffmpeg. Details: %s", e.message)
                lgr.error("Please check if executable file exists: %s", pathToFFmpeg)

                return False
            else:
                # Something else went wrong while trying to run ffmpeg
                lgr = logging.getLogger('FluidExplorerPlugin')
                lgr.error("Cannot execute ffmpeg. Details: %s", e.message)

                return False

        return True

    @staticmethod
    def checkIfFluidExplorerIsExectuable(pathToFluidExplorer):
        if sys.platform.startswith('win'):
            pathToFluidExplorer = pathToFluidExplorer + '/fluidexplorer.exe'
        else:
            pathToFluidExplorer = pathToFluidExplorer + '/fluidexplorer'

        """
        try:
            subprocess.call([pathToFluidExplorer], shell=False)
        except OSError as e:
            if e.errno == os.errno.ENOENT:
                # Handle file not found error.
                print("Fatal Error: Cannot find ffmpeg. Details: ", e.message)
                return False
            else:
                # Something else went wrong while trying to run ffmpeg
                print("Fatal Error: Cannot execute ffmpeg. Details: ", e.message)
                return False
        """

        return True

    @staticmethod
    def lockNodes(fluidNode, transformNOde):
        if not fluidNode == "":
            cmds.lockNode(fluidNode)
        if not transformNOde == "":
            cmds.lockNode(transformNOde)

    #
    #

    @staticmethod
    def killProcess(processnameArg):
        if sys.platform.lower().startswith('win'):
            FluidExplorerUtils.killProcess_WIN(processnameArg)
        elif sys.platform.startswith(''):
            # TODO: unix implementation
            pass

    @staticmethod
    def killProcess_WIN(processnameArg):
        tasklist_available = True
        taskkill_available = True

        lgr = logging.getLogger('FluidExplorerPlugin')

        processname = processnameArg + '.exe'
        processFound = False

        if os.path.exists('C:/Windows/System32/tasklist.exe'):
            tlcall = 'C:/Windows/System32/tasklist.exe', '/FI', 'imagename eq %s' % processname
        else:
            tlcall = 'TASKLIST', '/FI', 'imagename eq %s' % processname
            try:
                subprocess.Popen('TASKLIST', shell=True)
            except:
                tasklist_available = False
                lgr.error('Cannot execute TASKLIST.EXE command - fluidexplorer.exe hast not been closed')

        if not tasklist_available:
            return

        try:
            # communicate() - gets the tasklist command result
            tlproc = subprocess.Popen(tlcall, shell=True, stdout=subprocess.PIPE)
            # trimming it to the actual lines with information
            tlout = tlproc.communicate()[0].strip().split('\r\n')
            # if TASKLIST returns single line without processname: it's not running
            if len(tlout) > 1 and processname in tlout[-1]:
                # print('Process "%s" is running .' % processname)
                lgr.info('Process "%s" is running', processname)
                processFound = True
            else:
                # print('Process "%s" is NOT running.' % processname)
                lgr.info('Process "%s" is not running', processname)
        except:
            lgr.error('Cannot execute TASKLIST.EXE command - fluidexplorer.exe hast not been closed')
            processFound = False

        if processFound:

            """
            # Close by number
            cmdProcessPidCmd = 'wmic process where caption=' + '\"' + processname + '\"' + ' get processid'
            cmdProcessPid = subprocess.Popen(cmdProcessPidCmd, stdout=subprocess.PIPE, shell=True)
            pid = cmdProcessPid.communicate()[0].strip().split('\r\n')

            print('Process PID: for "%s" found ' % processname)
            #for p in pid:
            #    print p
            """

            if os.path.exists('C:/Windows/System32/taskkill.exe'):
                cmdStr = 'C:/Windows/System32/taskkill.exe /im' + ' ' + processname + ' ' + '/F'
            else:
                cmdStr = 'taskkill /im' + ' ' + processname + ' ' + '/F'
                try:
                    subprocess.Popen('TASKKILL', shell=True)
                except (OSError, IOError) as e:
                    lgr.error('Cannot execute TASKKILL.EXE command - fluidexplorer.exe hast not been closed')
                    taskkill_available = False

            if not taskkill_available:
                return

            # Cloee the process
            try:
                # cmdStr = 'taskkill /im' + ' ' + processname
                kill = subprocess.Popen(cmdStr, shell=True, stdout=subprocess.PIPE)
                lgr.info('Process "%s" closed ', processname)

            except Exception as e:
                lgr.error('Process "%s" not closed', processname)
                lgr.error('Details: %s', e.message)
                lgr.error('Details: %s', e.message)


    @staticmethod
    def copySettingsFile(scr, dst):
        shutil.copyfile(scr, dst)

    @staticmethod
    def deleteRenderWindow():
        win_list = cmds.lsUI(windows=True)
        if ('renderViewWindow' in win_list):
            cmds.deleteUI('renderViewWindow', window=True)
            cmds.refresh()
            # mel.eval('catchQuiet(`deleteUI renderViewWindow`)')

    """
    If a user deletes the prefs folder, the query commands (e.g. cmds.optionVar(q='fluidCacheSimulationRate'))
    return 0 instead of the correct values. This causes an error during caching.
    In order to solve the probllem, this method opens the fluid cache options menue and cloes the window again.
    Afterwards, the values should be retrieved correctly.
    Please note that a more efficient method probably exists.
    """
    @staticmethod
    def initCahceSettings():
        simulationRate = cmds.optionVar(q='fluidCacheSimulationRate')
        if simulationRate == 0:
            mel.eval('CreateFluidCacheOptions;')
            mel.eval('saveOptionBoxSize();')
            mel.eval('if (`window -exists OptionBoxWindow`) deleteUI -window OptionBoxWindow;')
