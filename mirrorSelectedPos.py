import maya.cmds as cmds
from pymel.core import *
import json
import maya.api.OpenMaya as OpenMaya

def invertX(point):
    point.x *= -1
    return point

def mirrorSelected():
    with open(rootDic + '/data/topoMap.tpmap') as json_file:
        data = json.load(json_file)

    mesh_MPointArray = OpenMaya.MPointArray()
    selection = OpenMaya.MGlobal.getActiveSelectionList()
    meshDagPath = selection.getDagPath(0)
    meshFn = OpenMaya.MFnMesh(meshDagPath)
    mesh_MPointArray = meshFn.getPoints(OpenMaya.MSpace.kObject)
    for key in data:
        A = int(key)
        B = data[key]
        tempPos = invertX(mesh_MPointArray[A])
        meshFn.setPoint(A, invertX(mesh_MPointArray[B]))
        meshFn.setPoint(B, tempPos)
