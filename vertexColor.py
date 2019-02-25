import pymel.core as pm
import json
import maya.api.OpenMaya as OpenMaya

def mdagpath_from_name(name):
    if not pm.objExists(name):
        raise MayaNodeError, name
    slist = OpenMaya.MSelectionList()
    slist.add(name)
    dagpath = OpenMaya.MDagPath()
    dagpath = slist.getDagPath(0)
    return dagpath

def getSelectedMeshFn():
    mesh_MPointArray = OpenMaya.MPointArray()
    selection = OpenMaya.MGlobal.getActiveSelectionList()
    meshDagPath = selection.getDagPath(0)
    return maya.api.OpenMaya.MFnMesh(meshDagPath)

def serializeColor(mayaColors):
    colsSerilizable = []
    for col in mayaColors:
        colsSerilizable.append(col.__str__())
    return colsSerilizable

def deserializeColor(colors):
    mayaColors = []
    for col in colors:
        mayaColors.append(OpenMaya.MColor(eval(col)))
    return mayaColors

def saveVColor(slotName, dagName):
    # mesh_MPointArray = OpenMaya.MPointArray()
    # selection = OpenMaya.MGlobal.getActiveSelectionList()
    # meshDagPath = selection.getDagPath(0)
    dagpath = mdagpath_from_name(dagName)
    meshFn = maya.api.OpenMaya.MFnMesh(dagpath)
    colors = []
    try:
        colors = meshFn.getVertexColors()
    except RuntimeError:
        defaultColor = OpenMaya.MColor()
        meshFn.setVertexColors([defaultColor]*meshFn.numVertices, range(meshFn.numVertices))
        colors = meshFn.getVertexColors()
    # write colors into file
    with open(rootDic + '/data/vcol/{0}.vcol'.format(slotName), 'w') as outfile:
        json.dump(serializeColor(colors), outfile)


def loadVColor(slotName, dagName):
    # mesh_MPointArray = OpenMaya.MPointArray()
    # selection = OpenMaya.MGlobal.getActiveSelectionList()
    # meshDagPath = selection.getDagPath(0)
    dagpath = mdagpath_from_name(dagName)
    meshFn = maya.api.OpenMaya.MFnMesh(dagpath)
    # read colors into file
    with open(rootDic + '/data/vcol/{0}.vcol'.format(slotName)) as json_file:
        colors = json.load(json_file)
    meshFn.setVertexColors(deserializeColor(colors), range(meshFn.numVertices))

def compose():
    currentMFn = getSelectedMeshFn()
    dagpath = mdagpath_from_name('NeturalPoseBackupShape')  #Todo: replace the hardcoded name
    neturalMeshFn = maya.api.OpenMaya.MFnMesh(dagpath)
    duObj = pm.duplicate()
    duObj[0].tx.set(duObj[0].tx.get() + 15) #to offset the duplicated pose a little bit for better finding.
    dagpath = mdagpath_from_name(duObj[0].nodeName())
    DuMeshFn = maya.api.OpenMaya.MFnMesh(dagpath)
    mesh_MPointArray = DuMeshFn.getPoints(OpenMaya.MSpace.kObject)
    weightList = neturalMeshFn.getVertexColors()
    for i, key in enumerate(mesh_MPointArray):
        weight = weightList[i].r #get weight info only from R channel
        fromPos = neturalMeshFn.getPoint(i)
        toPos = DuMeshFn.getPoint(i)
        finalPos = fromPos + (toPos-fromPos)*weight
        DuMeshFn.setPoint(i, finalPos)



