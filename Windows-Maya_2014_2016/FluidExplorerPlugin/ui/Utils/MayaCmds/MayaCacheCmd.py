import maya.cmds as cmds


class MayaCacheCmdString(object):

    def __init__(self):

        self.fluidCacheTimeRange = ""
        self.fluidCacheStartTime = ""
        self.fluidCacheEndTime = ""
        self.fluidCacheDistribMode = ""
        self.fluidRefresh = ""
        self.fluidCacheDirName = ""
        self.fluidCachePerGeometry = ""
        self.fluidCacheName = ""
        self.fluidCacheUsePrefix = ""
        self.fluidCacheAction = ""
        self.fluidCacheForceOverwrite = ""
        self.fluidCacheSimulationRate = ""
        self.fluidCacheSampleMultiplier = ""
        self.fluidCacheInheritModifications = ""
        self.fluidCacheStoreFloats = ""
        self.fluidCacheFormat = ""
        self.fluidCachePBDensity = ""
        self.fluidCachePBVelocity = ""
        self.fluidCachePBTemperature = ""
        self.fluidCachePBFuel = ""
        self.fluidCachePBColor = ""
        self.fluidCachePBTextureCoords = ""
        self.fluidCachePBFalloff = ""

    def setRenderSettingsFromMaya(self, startTime, endTime, cacheDir, chacheName):

        self.fluidCacheTimeRange = "0"
        self.fluidCacheStartTime = str(startTime)
        self.fluidCacheEndTime = str(endTime)

        self.fluidCacheDistribMode = "OneFilePerFrame"
        tmp = cmds.optionVar(q='fluidCacheDistrib')

        # Always use 'OneFilePerFrame'
        if tmp == 1:
            self.fluidCacheDistribMode = "OneFilePerFrame"
            #self.fluidCacheDistribMode = "OneFile"
        if tmp == 2:
            #self.fluidCacheDistribMode = "OneFile"
            self.fluidCacheDistribMode = "OneFilePerFrame"

        self.fluidRefresh = cmds.optionVar(q='fluidRefresh')
        self.fluidCacheDirName = cacheDir
        self.fluidCachePerGeometry = "0"
        self.fluidCacheName = chacheName
        self.fluidCacheUsePrefix = cmds.optionVar(q='fluidCacheUsePrefix')
        self.fluidCacheAction = "replace"
        self.fluidCacheForceOverwrite = "1"
        self.fluidCacheSimulationRate = cmds.optionVar(q='fluidCacheSimulationRate')
        self.fluidCacheSampleMultiplier = cmds.optionVar(q='fluidCacheSampleMultiplier')
        self.fluidCacheInheritModifications = cmds.optionVar(q='fluidCacheInheritModifications')
        self.fluidCacheStoreFloats = cmds.optionVar(q='fluidCacheStoreFloats')
        self.fluidCacheFormat = cmds.optionVar(q='fluidCacheFormat')
        self.fluidCacheFormat = 'mcc'
        self.fluidCachePBDensity = cmds.optionVar(q='fluidCachePBDensity')
        self.fluidCachePBVelocity = cmds.optionVar(q='fluidCachePBVelocity')
        self.fluidCachePBTemperature = cmds.optionVar(q='fluidCachePBTemperature')
        self.fluidCachePBFuel = cmds.optionVar(q='fluidCachePBFuel')
        self.fluidCachePBColor = cmds.optionVar(q='fluidCachePBColor')
        self.fluidCachePBTextureCoords = cmds.optionVar(q='fluidCachePBTextureCoords')
        self.fluidCachePBFalloff = cmds.optionVar(q='fluidCachePBFalloff')

    def getCacheCommandString(self):

        command = "doCreateFluidCache 5 { " \
            + "\"" + str(self.fluidCacheTimeRange) + "\", " \
            + "\"" + str(self.fluidCacheStartTime) + "\", " \
            + "\"" + str(self.fluidCacheEndTime) + "\", " \
            + "\"" + str(self.fluidCacheDistribMode) + "\", " \
            + "\"" + str(self.fluidRefresh) + "\", " \
            + "\"" + str(self.fluidCacheDirName) + "\"," \
            + "\"" + str(self.fluidCachePerGeometry) + "\", " \
            + "\"" + str(self.fluidCacheName) + "\"," \
            + "\"" + str(self.fluidCacheUsePrefix) + "\", " \
            + "\"" + str(self.fluidCacheAction) + "\", " \
            + "\"" + str(self.fluidCacheForceOverwrite) + "\", " \
            + "\"" + str(self.fluidCacheSimulationRate) + "\", " \
            + "\"" + str(self.fluidCacheSampleMultiplier) + "\", " \
            + "\"" + str(self.fluidCacheInheritModifications) + "\", " \
            + "\"" + str(self.fluidCacheStoreFloats) + "\", " \
            + "\"" + str(self.fluidCacheFormat) + "\", " \
            + "\"" + str(self.fluidCachePBDensity) + "\", " \
            + "\"" + str(self.fluidCachePBVelocity) + "\", " \
            + "\"" + str(self.fluidCachePBTemperature) + "\", " \
            + "\"" + str(self.fluidCachePBFuel) + "\", " \
            + "\"" + str(self.fluidCachePBColor) + "\", " \
            + "\"" + str(self.fluidCachePBTextureCoords) + "\", " \
            + "\"" + str(self.fluidCachePBFalloff) + "\"" \
            + " }"

        command = command.replace('\\','/')

        return command

    """
	// Description:
	//	Create cache files on disk for the select fluid object(s) according
	//  to the specified flags described below.
	//
	// $version == 1:
	//	$args[0] = time range mode:
	//		time range mode = 0 : use $args[1] and $args[2] as start-end
	//		time range mode = 1 : use render globals
	//		time range mode = 2 : use timeline
	//  $args[1] = start frame (if time range mode == 0)
	//  $args[2] = end frame (if time range mode == 0)
	//
	// $version == 2:
	//  $args[3] = cache file distribution, either "OneFile" or "OneFilePerFrame"
	//	$args[4] = 0/1, whether to refresh during caching
	//  $args[5] = directory for cache files, if "", then use project data dir
	//	$args[6] = 0/1, whether to create a cache per geometry
	//	$args[7] = name of cache file. An empty string can be used to specify that an auto-generated name is acceptable.
	//	$args[8] = 0/1, whether the specified cache name is to be used as a prefix
	// $version == 3:
	//  $args[9] = action to perform: "add", "replace", "merge" or "mergeDelete"
	//  $args[10] = force save even if it overwrites existing files
	//	$args[11] = simulation rate, the rate at which the fluid simulation is forced to run
	//	$args[12] = sample mulitplier, the rate at which samples are written, as a multiple of simulation rate.
	// $version == 4:
	//	$args[13] = 0/1, whether modifications should be inherited from the cache about to be replaced.
	//	$args[14] = 0/1, whether to store doubles as floats
	//	$args[15] = name of cache format
	//
	// $version == 5:
	//	$args[16] = 0/1, whether density should be cached
	//	$args[17] = 0/1, whether velocity should be cached
	//	$args[18] = 0/1, whether temperature should be cached
	//	$args[19] = 0/1, whether fuel should be cached
	//	$args[20] = 0/1, whether color should be cached
	//	$args[21] = 0/1, whether texture coordinates should be cached
	//	$args[22] = 0/1, whether falloff should be cached
	//
    """






