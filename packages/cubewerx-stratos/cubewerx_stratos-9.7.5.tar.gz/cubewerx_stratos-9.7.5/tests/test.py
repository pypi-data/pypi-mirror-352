#  $Id: test.py 79132 2025-06-02 14:48:52Z pomakis $

import sys
import os
import datetime
from getpass import getpass


sys.path.append(os.path.join(sys.path[0], '..', 'src'))
from cubewerx.stratos import *

#deploymentUrl = "https://test.cubewerx.com/cubewerx/"
#username = "admin"

deploymentUrl = "https://dev.cubewerx.com/~pomakis/cubewerx/"
username = "pomakis"

print('Connecting to "%s"' % deploymentUrl)
print('Username: ' + username)
password = getpass()

try:
    stratos = Stratos(deploymentUrl, username, password)
except InvalidCredentialsException as e:
    print("Invalid credentials!")
    exit(1)
except LoginException as e:
    print("Login exception:", e)
    exit(1)
except Exception as e:
    print("Exception:", e)
    exit(1)

displayName  = stratos.credentials.displayName
print("Hello %s!" % displayName)

print("full version string: %s" % stratos.serverVersionFull)
print("license expiration date: %s" % stratos.licenseExpirationDate)

print("----------------------------------------------------------------")
stats = stratos.getStats(nPeriods=12)
print("# active users:", end="")
for n in stats.nActiveUsers: print(" %d" % n, end="")
print()
print("load average: %f %f %f" %
    (stats.loadAverage[0], stats.loadAverage[1], stats.loadAverage[2]))
print("nCpus: %d" % stats.nCpus)
print("memory: %d bytes (%d used)" % (stats.memoryTotal, stats.memoryUsed))

print("----------------------------------------------------------------")
users = stratos.getAuthUsers()
print(users)

print("----------------------------------------------------------------")
user = stratos.getAuthUser("jimbob")
if user:
    print("user: %s, %s" % (user.displayName, user.emailAddress))

    print("----------------------------------------------------------------")
    user.firstName += "m"
    stratos.updateAuthUser(user);
    print("user updated")

    print("----------------------------------------------------------------")
    user = stratos.getAuthUser("jimbob")
    if user:
        print("user: %s, %s" % (user.displayName, user.emailAddress))
    else:
        print('no such user user "jimbob"')

    print("----------------------------------------------------------------")
    stratos.removeAuthUser("jimbob")
    print("user removed")
else:
    print('no such user user "jimbob"')

print("----------------------------------------------------------------")
user = AuthUser("jimbob")
user.firstName = "Jim"
user.lastName = "Bob"
user.emailAddress = "bob@bobland.com"
user.password = "bob"
user.addRole("OpenImageMap User")
stratos.addOrReplaceAuthUser(user)
print("user added")

print("----------------------------------------------------------------")
user = stratos.getAuthUser("jimbob")
if user:
    print("user: %s, %s" % (user.displayName, user.emailAddress))
else:
    print('no such user user "jimbob"')

print("----------------------------------------------------------------")
role = Role("Test Role")
role.addOidUser({"issuer": "https://myissuer.com/", "sub": "mysub"})
role.addOidUser({"issuer": "https://myissuer2.com/"})
stratos.addOrReplaceRole(role)
role = stratos.getRole("Test Role")
print(role.oidUsers)
print(role.oidUsers[0].get("issuer"))

print("----------------------------------------------------------------")
requestHistory = stratos.getRequestHistory(maxPeriods=4)
print("request history period type: %s, %s" %
    (requestHistory.periodTypeNoun, requestHistory.periodTypeAdjective))
print("periods:")
for period in requestHistory.periods:
    print("    %s to %s:" % (period.fromDate, period.toDate))
    summaries = period.summaries
    print("        coverages: %d requests, %d bytes" %
        (summaries.coverages.nRequests, summaries.coverages.nBytes))
    print("        vectors: %d requests, %d bytes" %
        (summaries.vectors.nRequests, summaries.vectors.nBytes))
    print("        total: %d requests, %d bytes" %
        (summaries.total.nRequests, summaries.total.nBytes))
print("daily averages:")
dailyAverages = requestHistory.dailyAverages
print("    coverages: %d requests, %d bytes" %
    (dailyAverages.coverages.nRequests, dailyAverages.coverages.nBytes))
print("    vectors: %d requests, %d bytes" %
    (dailyAverages.vectors.nRequests, dailyAverages.vectors.nBytes))
print("    total: %d requests, %d bytes" %
    (dailyAverages.total.nRequests, dailyAverages.total.nBytes))

print("----------------------------------------------------------------")
loginHistory = stratos.getLoginHistory(num=10)
print("login history:")
for entry in loginHistory:
    print("    %s  %s  %s" % (entry.timestamp, entry.ipAddress, entry.user))

print("----------------------------------------------------------------")
configParams = stratos.getConfigParams()
configParamsArray = list(configParams.values())
del configParamsArray[10:]
print("first 10 config params:")
for configParam in configParamsArray:
    print("    %s (%s)" % (configParam.name, configParam.type))
    print("        %s" % configParam.defaultValueStr)

print("----------------------------------------------------------------")
configParams = stratos.getConfigParams()
param = configParams.get("audit.nAcceptable5xxErrorsPerHour");
print("audit.nAcceptable5xxErrorsPerHour: %s" % param.explicitValue)
param.explicitValueStr = "2e3"
print("audit.nAcceptable5xxErrorsPerHour: %s" % param.explicitValue)
param.explicitValueStr = None
print("audit.nAcceptable5xxErrorsPerHour: %s" % param.explicitValue)

param.explicitValue = 42
print("audit.nAcceptable5xxErrorsPerHour: %s" % param.explicitValueStr)
param.explicitValue = "43"
print("audit.nAcceptable5xxErrorsPerHour: %s" % param.explicitValueStr)
param.explicitValue = None
print("audit.nAcceptable5xxErrorsPerHour: %s" % param.explicitValueStr)

print("----------------------------------------------------------------")
apiKeys = stratos.getApiKeys()
print("API keys:")
for apiKey in apiKeys:
    print("    %s (%s)" % (apiKey.key, apiKey.description))

print("----------------------------------------------------------------")
apiKey = ApiKey()
apiKey.description = "une clé"
stratos.addOrReplaceApiKey(apiKey)
print("    %s (%s)" % (apiKey.key, apiKey.description))

keyStr = apiKey.key
apiKey = stratos.getApiKey(keyStr)
print("    %s (%s)" % (apiKey.key, apiKey.description))

apiKey.description = "a key"
stratos.addOrReplaceApiKey(apiKey)
print("    %s (%s)" % (apiKey.key, apiKey.description))
apiKey = stratos.getApiKey(keyStr)
print("    %s (%s)" % (apiKey.key, apiKey.description))

apiKey.description = "still a key"
apiKey.expiresAt = datetime.datetime.fromisoformat("2029-06-13T12:13:14Z");
print("    %s" % (apiKey._patchDict))
stratos.updateApiKey(apiKey)
print("    %s (%s)" % (apiKey.key, apiKey.description))
apiKey = stratos.getApiKey(keyStr)
print("    %s (%s)" % (apiKey.key, apiKey.description))

stratos.removeApiKey(apiKey)
apiKey = stratos.getApiKey(keyStr)
print("    %s" % apiKey)

print("----------------------------------------------------------------")
quotas = stratos.getQuotas()
print("quotas:")
for quota in quotas:
    print("    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" %
        (quota.id, quota.identityType, quota.identity, quota.field,
        quota.service, quota.operation, quota.granularity, quota.fromDate,
        quota.toDate, quota.limit, quota.usage, quota.warningNumSent))

print("----------------------------------------------------------------")
quota = stratos.addQuota(QuotaIdentityType.ROLE, "kpptest",
    QuotaField.N_POINTS, "*", "*", QuotaGranularity.WEEKLY, 2000)
print("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" %
    (quota.id, quota.identityType, quota.identity, quota.field,
    quota.service, quota.operation, quota.granularity, quota.fromDate,
    quota.toDate, quota.limit, quota.usage, quota.warningNumSent))
stratos.updateQuota(quota, limit=4000)
print("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" %
    (quota.id, quota.identityType, quota.identity, quota.field,
    quota.service, quota.operation, quota.granularity, quota.fromDate,
    quota.toDate, quota.limit, quota.usage, quota.warningNumSent))
quotaId = quota.id
quota = stratos.getQuota(quotaId)
print("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" %
    (quota.id, quota.identityType, quota.identity, quota.field,
    quota.service, quota.operation, quota.granularity, quota.fromDate,
    quota.toDate, quota.limit, quota.usage, quota.warningNumSent))
stratos.removeQuota(quota)
quota = stratos.getQuota(quotaId)
print(quota)

print("----------------------------------------------------------------")
cubestors = stratos.getCubeSTORs()
print("cubestors:")
for cubestor in cubestors:
    print("    %s, %s, %s, %s, %s, %s" % (cubestor.dbName, cubestor.title,
        cubestor.description, cubestor.nFeatureSets, cubestor.dataStoreName,
        cubestor.canDelete));

print("----------------------------------------------------------------")
cubestor = stratos.addCubeSTOR("kppTestDb", "KPP Test DB",
    "A KPP Test Database");
print("%s, %s, %s, %s, %s, %s" % (cubestor.dbName, cubestor.title,
    cubestor.description, cubestor.nFeatureSets, cubestor.dataStoreName,
    cubestor.canDelete));
cubestor = stratos.getCubeSTOR("kppTestDb");
print("%s, %s, %s, %s, %s, %s" % (cubestor.dbName, cubestor.title,
    cubestor.description, cubestor.nFeatureSets, cubestor.dataStoreName,
    cubestor.canDelete));
stratos.updateCubeSTOR(cubestor, description="A KPP Test Database!")
print("%s, %s, %s, %s, %s, %s" % (cubestor.dbName, cubestor.title,
    cubestor.description, cubestor.nFeatureSets, cubestor.dataStoreName,
    cubestor.canDelete));
cubestor = stratos.getCubeSTOR("kppTestDb");
print("%s, %s, %s, %s, %s, %s" % (cubestor.dbName, cubestor.title,
    cubestor.description, cubestor.nFeatureSets, cubestor.dataStoreName,
    cubestor.canDelete));
stratos.removeCubeSTOR(cubestor);
cubestor = stratos.getCubeSTOR("kppTestDb");
print(cubestor)

print("----------------------------------------------------------------")
dataStores = stratos.getDataStores()
print("data stores:")
for dataStore in dataStores:
    print("    %s, %s, %s" % (dataStore.name, dataStore.type,
        dataStore.source))

print("----------------------------------------------------------------")
dataStore = stratos.getDataStore("newCubestor")
print(dataStore._patchDict)
dataStore.title = "New Title"
dataStore.title["fr"] = "Nouveau Titre"
simulateTiles = dataStore.simulateTiles
simulateTiles.append("4326")
dataStore.isExternalService = False # already False
dataStore.provideSpectralIndexStyles = True

rule = dataStore.accessControlRules[0]
grantClause = rule.grants[0]
contentRef = grantClause.content[1]
contentRef.finestResolution =  { "resolution": 10000, "crs": "EPSG:3857" }

print(dataStore._patchDict)
print(dataStore._jsonRep)

print("----------------------------------------------------------------")
dataStore = stratos.getDataStore("MERN")
print(dataStore._jsonRep)

print("----------------------------------------------------------------")
dataStore = stratos.getDataStore("newCubestor")
layers = dataStore.getLayers()
for layer in layers:
    print("***** %s" % layer.id)
    print("    %s, %s" % (layer.title, layer.description))
    extent = layer.wgs84Extent
    if extent:
        print("    extent: %f, %f, %f, %f" %
              (extent[0], extent[1], extent[2], extent[3]))
    else:
        print("    NO EXTENT")
    print("    isVectors: %s, isCoverage: %s" %
              (layer.isVectors, layer.isCoverage))
    print("    isMappable: %s, canBeManaged: %s" %
              (layer.isMappable, layer.canBeManaged))

print("----------------------------------------------------------------")
dataStore = stratos.getDataStore("newCubestor")
layers = dataStore.getLayers() # TODO: why does this take so long?
nlLayer = None
for layer in layers:
    if layer.id == "nl":
        nlLayer = layer
        break
sourceImages = nlLayer.getSourceImages()
print("source images:")
for sourceImage in sourceImages:
    print("    %s: %s (good: %s)" %
        (sourceImage.id, sourceImage.title, sourceImage.isGood))
    for hintName, hintValue in sourceImage.hints._dict.items():
        print("        %s: %s" % (hintName, hintValue))

print("----------------------------------------------------------------")
sourceImage = sourceImages[0]
hints = sourceImage.hints
hints.nullColor1 = None
hints.rasterNBits = 8
sourceImage.commitHintChanges()
sourceImages = nlLayer.getSourceImages()
print("source images:")
for sourceImage in sourceImages:
    print("    %s: %s (good: %s)" %
        (sourceImage.id, sourceImage.title, sourceImage.isGood))
    for hintName, hintValue in sourceImage.hints._dict.items():
        print("        %s: %s" % (hintName, hintValue))

print("----------------------------------------------------------------")
sourceImage = sourceImages[0]
hints = sourceImage.hints
hints.nullColor1 = "000000"
hints.rasterNBits = None
sourceImage.commitHintChanges()
sourceImages = nlLayer.getSourceImages()
print("source images:")
for sourceImage in sourceImages:
    print("    %s: %s (good: %s)" %
        (sourceImage.id, sourceImage.title, sourceImage.isGood))
    for hintName, hintValue in sourceImage.hints._dict.items():
        print("        %s: %s" % (hintName, hintValue))

##############################################################################
# Test adding, adjusting and removing of layers.
##############################################################################

# List the existing layers of the newCubestor data store.
print("----------------------------------------------------------------")
dataStore = stratos.getDataStore("newCubestor")
layers = dataStore.getLayers()
for layer in layers:
    print("***** %s" % layer.id)
    print("    %s, %s" % (layer.title, layer.description))
    print("    isVectors: %s, isCoverage: %s" %
              (layer.isVectors, layer.isCoverage))
    print("    isMappable: %s, canBeManaged: %s" %
              (layer.isMappable, layer.canBeManaged))

# Add a "newCoverageLayer" layer.
print("----------------------------------------------------------------")
newLayer = dataStore.addCoverageLayer("newCoverageLayer",
    "New Coverage Layer", "This is a new coverage layer.")

# Re-title the "newCoverageLayer" layer.
newLayer.title = "New Coverage Layer!"

# List the layers again (direct from the existing layers list, to make sure
# the cache mechanism is working).
print("----------------------------------------------------------------")
for layer in layers:
    print("***** %s" % layer.id)
    print("    %s, %s" % (layer.title, layer.description))
    print("    isVectors: %s, isCoverage: %s" %
              (layer.isVectors, layer.isCoverage))
    print("    isMappable: %s, canBeManaged: %s" %
              (layer.isMappable, layer.canBeManaged))

# Get the data store and layers again, then list the layers again.
print("----------------------------------------------------------------")
dataStore = stratos.getDataStore("newCubestor")
layers = dataStore.getLayers()
for layer in layers:
    print("***** %s" % layer.id)
    print("    %s, %s" % (layer.title, layer.description))
    print("    isVectors: %s, isCoverage: %s" %
              (layer.isVectors, layer.isCoverage))
    print("    isMappable: %s, canBeManaged: %s" %
              (layer.isMappable, layer.canBeManaged))

# Remove the "newCoverageLayer" layer.
print("----------------------------------------------------------------")
isRemoved = dataStore.removeLayer("newCoverageLayer")
print("isRemoved: %s" % isRemoved)

# List the layers again (direct from the existing layers list, to make sure
# the cache mechanism is working).
print("----------------------------------------------------------------")
for layer in layers:
    print("***** %s" % layer.id)
    print("    %s, %s" % (layer.title, layer.description))
    print("    isVectors: %s, isCoverage: %s" %
              (layer.isVectors, layer.isCoverage))
    print("    isMappable: %s, canBeManaged: %s" %
              (layer.isMappable, layer.canBeManaged))

# Add a "newVectorLayer" layer with data from source files.
print("----------------------------------------------------------------")
sourceImageFiles = [
    "/disk2/data/hydro_feature/TAS_HYDRO_FEATURE_shp.mdf",
    "/disk2/data/hydro_feature/TAS_HYDRO_FEATURE_shp.mdx",
]
newLayer = dataStore.addVectorLayerWithData("newVectorLayer", sourceImageFiles,
    "New Vector Layer", "This is a new vector layer.",
    nominalResM=100000, updateTiles=False)
print("new layer added: " + newLayer.id)

isRemoved = dataStore.removeLayer("newVectorLayer")
print("isRemoved: %s" % isRemoved)

# Add a "newVectorLayer" layer with data from inline GeoJSON.
print("----------------------------------------------------------------")
featureCollection = geojson.loads('''{
  "type":"FeatureCollection",
  "features": [
    {"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[-134.961057,60.617527],[-134.960931,60.617565],[-134.96104,60.617653],[-134.961166,60.617616],[-134.961057,60.617527]]]},"properties":{}},
    {"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[-135.091604,60.753793],[-135.091603,60.753846],[-135.091683,60.753846],[-135.091681,60.753938],[-135.091761,60.753938],[-135.091765,60.753794],[-135.091604,60.753793]]]},"properties":{}},
    {"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[-135.102397,60.749029],[-135.102494,60.748996],[-135.102543,60.74896],[-135.102574,60.74891],[-135.102625,60.748892],[-135.102854,60.748726],[-135.102942,60.748696],[-135.102968,60.748653],[-135.103007,60.748624],[-135.103111,60.748589],[-135.103156,60.748515],[-135.103078,60.748489],[-135.103097,60.748458],[-135.103062,60.748434],[-135.102989,60.748423],[-135.102793,60.74849],[-135.102756,60.748549],[-135.102614,60.748598],[-135.102351,60.74879],[-135.102154,60.748761],[-135.10204,60.7488],[-135.102007,60.748854],[-135.102124,60.748892],[-135.101894,60.749263],[-135.101785,60.749342],[-135.101777,60.749355],[-135.101851,60.749406],[-135.102137,60.749448],[-135.102397,60.749029]]]},"properties":{}},
    {"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[-135.088304,60.750905],[-135.088062,60.750905],[-135.088062,60.75096],[-135.088304,60.75096],[-135.088304,60.750905]]]},"properties":{}},
    {"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[-135.093363,60.736024],[-135.09347,60.73594],[-135.093253,60.735874],[-135.093146,60.735959],[-135.093363,60.736024]]]},"properties":{}},
    {"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[-135.06369,60.72382],[-135.063725,60.723878],[-135.063535,60.723905],[-135.063653,60.724099],[-135.063971,60.724052],[-135.063907,60.723948],[-135.064294,60.723891],[-135.064206,60.723746],[-135.06369,60.72382]]]},"properties":{}}
  ]
}''')
newLayer = dataStore.addVectorLayerWithData("newVectorLayer",
    featureCollection, "New Vector Layer", "This is a new vector layer.",
    updateTiles=True)
print("new layer added: " + newLayer.id)

isRemoved = dataStore.removeLayer("newVectorLayer")
print("isRemoved: %s" % isRemoved)

# (2025-05-29: Doesn't work yet; Peter is working on it.)
# Add an empty "newVectorLayer" layer.
#print("----------------------------------------------------------------")
#newLayer = dataStore.addVectorLayer("newVectorLayer",
#    "/home/pomakis/putCollectionTests/mdfTest-schema.json",
#    "New Vector Layer", "This is a new vector layer.");
#print("new layer added: " + newLayer.id)

##############################################################################
# Test adding source images.
##############################################################################

# Add a "newCoverageLayer" layer.
print("----------------------------------------------------------------")
newLayer = dataStore.addCoverageLayer("newCoverageLayer",
    "New Coverage Layer", "This is a new coverage layer.")

# Add new source images.
hints = SourceImageHints()
hints.nullColor1 = '#000000'
sourceImageFiles = [
    "/cw/testdata/tiff/nl/001027_0100_020904_l7_743_utm22.tif",
    "/cw/testdata/tiff/nl/002025_0100_010722_l7_743_utm21.tif",
]
newSourceImages = newLayer.addSourceImages(sourceImageFiles, hints)

# List the new source images.
print("new source images:")
for sourceImage in newSourceImages:
    print("    %s: %s (good: %s)" %
        (sourceImage.id, sourceImage.title, sourceImage.isGood))
    for hintName, hintValue in sourceImage.hints._dict.items():
        print("        %s: %s" % (hintName, hintValue))

# Remove the first of these new source images.
newLayer.removeSourceImage(newSourceImages[0])

# Fetch and list the new list of source images.
newSourceImages = newLayer.getSourceImages()
print("new source images:")
for sourceImage in newSourceImages:
    print("    %s: %s (good: %s)" %
        (sourceImage.id, sourceImage.title, sourceImage.isGood))
    for hintName, hintValue in sourceImage.hints._dict.items():
        print("        %s: %s" % (hintName, hintValue))

# Remove the "newCoverageLayer" layer.
dataStore.removeLayer("newCoverageLayer")
