import maya.cmds as cmds
import maya.mel as mel
import os
import logging


class LoadFluidCacheFile():

    @staticmethod
    def applyCacheFile(pathToCacheXMLFile, nodeName):
        lgr = logging.getLogger('FluidExplorerPlugin')

        lgr.info('Apply cache file')
        lgr.info('Selected object: %s', str(nodeName))
        lgr.info('Cache path: %s', str(pathToCacheXMLFile))

        # 1. Select the fluid container
        try:
            cmds.select(nodeName, r=True)
        except:
            errorMsg = "Fluid Container '" + str(nodeName) + "' does not exist!\nPlease visit the help page more information."
            raise Exception(errorMsg)

        # Check if path is available and executable
        if os.path.isfile(pathToCacheXMLFile) and os.access(pathToCacheXMLFile, os.R_OK):
            lgr.info("Load fluid cache file: Path to xml file is correct")
            pass
        else:
            lgr.error('Path to cache file is not correct or files are not accessible')
            raise Exception("Path to cache file is not correct or files are not accessible.")

        # 2. Delete current cache node
        # Catch Quiet: Otherwise, an error occurs if no cache is loaded!
        if cmds.objExists(nodeName):
            strCmd = 'catchQuiet (`deleteCacheFile 2 { "keep", "" }`) '
            try:
                mel.eval(strCmd)
            except Exception as e:
                lgr.error('Cannot delete the current cache for: %s', str(nodeName))
                lgr.error('Cache error details: %s', e.message)
                errorMsg = "Cannot delete the current cache for '" + str(nodeName) + "'!\nPlease visit the help page more information.\nDetails: " + e.message
                raise Exception(errorMsg)
        else:
            lgr.error('Fluid container %s does not exist', str(nodeName))
            errorMsg = "Fluid Container '" + str(nodeName) + "' does not exist!\nPlease visit the help page more information."
            raise Exception(errorMsg)

        # 3. Finally, attach the existing cache file
        try:
            lineToEval = 'doImportFluidCacheFile("{0}", "xmlcache", {{"{1}"}}, {{}});'.format(pathToCacheXMLFile, nodeName)
            mel.eval(lineToEval)
        except Exception as e:
            lgr.error('Cannot attach the cached file. Details: %s', e.message)
            errorMsg = "Cannot attach the cached file for '" + str(nodeName) + "'!\nPlease visit the help page more information.\nDetails: " + e.message
            raise Exception(errorMsg)

    """
    #####################################################################################################################
    # Maya Command
    pathToCacheXMLFile = "E:/TMP/ANNAANNA/0/flameShape_0.xml"
    nodeName = "flameShape"
    try:
        # lineToEval = 'doImportFluidCacheFile("{0}", "xmlcache", {{"{1}"}}, {{}});'.format( pathCache1, fluidsSel)
        applyCacheFile(pathToCacheXMLFile, nodeName)
    except Exception as e:
        print e.message
    #####################################################################################################################
    """

