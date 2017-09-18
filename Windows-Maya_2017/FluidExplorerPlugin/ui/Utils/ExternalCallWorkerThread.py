"""
from PySide import QtCore

import shlex
import subprocess
import os
import logging


class WorkThread(QtCore.QThread):

    def __init__(self, externalCallSettings):
        QtCore.QThread.__init__(self)

        # Logging
        self.lgr = logging.getLogger('FluidExplorerPlugin')

        self.running = True
        self.SEARCH_PATTERN_CMD = 'PATRICK'

        self.pathToFXApp = externalCallSettings.pathToFluidExplorer
        self.cmdFXAPP = externalCallSettings.fluidExplorerCmd
        self.cmdFXArg = externalCallSettings.fluidExplorerArgs

    def run(self):
        currentDir = os.getcwd()

        try:
            os.chdir(self.pathToFXApp)
            process = subprocess.Popen([shlex.split(self.cmdFXAPP), self.cmdFXArg], shell=True, stdout=subprocess.PIPE)
            self.lgr.info('Exteral application started')
        except Exception as e:
            self.lgr.error('Critical: Cannot execute fluid explorer app. Details: %s', e.message)
            self.emit(QtCore.SIGNAL('update(QString)'), "ERROR")
            return

        finally:
            os.chdir(currentDir)
            subprocess._cleanup()

        while self.running:

            output = process.stdout.readline()
            if output.startswith(self.SEARCH_PATTERN_CMD):
                self.lgr.info('Received event from fluid explorer app')

            if output == '' and process.poll() is not None:
                break
            if output:
                self.lgr.info(output.strip())
                #print output.strip()

        rc = process.poll()
        return rc

    def stop(self):
        # Stop the loop
        self.running = False
"""