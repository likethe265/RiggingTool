
import sys
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as omanim
import maya.api.OpenMayaRender as omrender
import maya.api.OpenMayaUI as omui

def maya_useNewAPI():
    pass

# -----------------------------------------------------------------------------
# Node Definition
# -----------------------------------------------------------------------------
class FacialControllerConstraint(om.MPxNode):
    """
    A node to compute the arithmetic mean of two doubles.
    """
    ## the name of the nodeType
    kPluginNodeTypeName = 'FacialControllerConstraint'
    ## the unique MTypeId for the node
    kPluginNodeId = om.MTypeId(0x0007318)

    inBlendshapeInfoList = om.MObject()
    inBaseMesh = om.MObject()
    inMesh = om.MObject()
    inOffsetX = om.MObject()
    inOffsetY = om.MObject()
    inOffsetZ = om.MObject()

    inPointIndex = om.MObject()
    inWeightList = om.MObject()

    outPositionX = om.MObject()
    outPositionY = om.MObject()
    outPositionZ = om.MObject()

    def __init__(self):
        om.MPxNode.__init__(self)
    

    @staticmethod
    def nodeCreator():
        return FacialControllerConstraint()

    @staticmethod
    def initialize():
        nAttrBaseMesh = om.MFnTypedAttribute()
        FacialControllerConstraint.inBaseMesh = nAttrBaseMesh.create('inBaseMesh', 'ibm', om.MFnMeshData.kMesh)
        nAttrBaseMesh.keyable = True


        nAttr1 = om.MFnNumericAttribute()
        FacialControllerConstraint.inPointIndex = nAttr1.create('inPointIndex', 'ivi', om.MFnNumericData.kInt, 0)
        nAttr1.keyable = True


        nAttr2 = om.MFnNumericAttribute()
        FacialControllerConstraint.inWeightList = nAttr2.create('inWeightList', 'iwl', om.MFnNumericData.kFloat, 0.0)
        nAttr2.keyable = True
        nAttr2.array = True

        nAttr2 = om.MFnNumericAttribute()
        FacialControllerConstraint.inOffsetX = nAttr2.create('inOffsetX', 'iox', om.MFnNumericData.kFloat, 0.0)
        nAttr2.keyable = True

        nAttr2 = om.MFnNumericAttribute()
        FacialControllerConstraint.inOffsetY = nAttr2.create('inOffsetY', 'ioy', om.MFnNumericData.kFloat, 0.0)
        nAttr2.keyable = True

        nAttr2 = om.MFnNumericAttribute()
        FacialControllerConstraint.inOffsetZ = nAttr2.create('inOffsetZ', 'ioz', om.MFnNumericData.kFloat, 0.0)
        nAttr2.keyable = True

        nAttrBlendshapeInfoList = om.MFnCompoundAttribute()
        FacialControllerConstraint.inBlendshapeInfoList = nAttrBlendshapeInfoList.create('inBlendshapeInfoList', 'ibsl')
        nAttrBlendshapeInfoList.keyable = True
        nAttrBlendshapeInfoList.array = True
        nAttrBlendshapeInfoList.indexMatters = False

        nAttr0 = om.MFnTypedAttribute()
        FacialControllerConstraint.inMesh = nAttr0.create('inMesh', 'ims', om.MFnMeshData.kMesh)
        nAttr0.keyable = True

        nAttrBlendshapeInfoList.addChild(FacialControllerConstraint.inMesh)
        nAttrBlendshapeInfoList.addChild(FacialControllerConstraint.inWeightList)

        nAttrOut = om.MFnNumericAttribute()
        FacialControllerConstraint.outPositionX = nAttrOut.create('outPositionX', 'ox', om.MFnNumericData.kFloat, 0.0)
        nAttrOut.keyable = False
        nAttrOut.storable = False

        FacialControllerConstraint.outPositionY = nAttrOut.create('outPositionY', 'oy', om.MFnNumericData.kFloat, 0.0)
        nAttrOut.keyable = False
        nAttrOut.storable = False

        FacialControllerConstraint.outPositionZ = nAttrOut.create('outPositionZ', 'oz', om.MFnNumericData.kFloat, 0.0)
        nAttrOut.keyable = False
        nAttrOut.storable = False

        # add the attributes
        om.MPxNode.addAttribute(FacialControllerConstraint.inBlendshapeInfoList)
        om.MPxNode.addAttribute(FacialControllerConstraint.inPointIndex)
        om.MPxNode.addAttribute(FacialControllerConstraint.inBaseMesh)
        om.MPxNode.addAttribute(FacialControllerConstraint.inOffsetX)
        om.MPxNode.addAttribute(FacialControllerConstraint.inOffsetY)
        om.MPxNode.addAttribute(FacialControllerConstraint.inOffsetZ)
        om.MPxNode.addAttribute(FacialControllerConstraint.outPositionX)
        om.MPxNode.addAttribute(FacialControllerConstraint.outPositionY)
        om.MPxNode.addAttribute(FacialControllerConstraint.outPositionZ)

        # establish effects on output
        om.MPxNode.attributeAffects(FacialControllerConstraint.inPointIndex, FacialControllerConstraint.outPositionX)
        om.MPxNode.attributeAffects(FacialControllerConstraint.inPointIndex, FacialControllerConstraint.outPositionY)
        om.MPxNode.attributeAffects(FacialControllerConstraint.inPointIndex, FacialControllerConstraint.outPositionZ)
        om.MPxNode.attributeAffects(FacialControllerConstraint.inOffsetX, FacialControllerConstraint.outPositionX)
        om.MPxNode.attributeAffects(FacialControllerConstraint.inOffsetY, FacialControllerConstraint.outPositionY)
        om.MPxNode.attributeAffects(FacialControllerConstraint.inOffsetZ, FacialControllerConstraint.outPositionZ)
        om.MPxNode.attributeAffects(FacialControllerConstraint.inBlendshapeInfoList, FacialControllerConstraint.outPositionX)
        om.MPxNode.attributeAffects(FacialControllerConstraint.inBlendshapeInfoList, FacialControllerConstraint.outPositionY)
        om.MPxNode.attributeAffects(FacialControllerConstraint.inBlendshapeInfoList, FacialControllerConstraint.outPositionZ)


    def compute(self, plug, dataBlock):
        pointIndex = dataBlock.inputValue(FacialControllerConstraint.inPointIndex).asInt()
        baseMeshData = dataBlock.inputValue(FacialControllerConstraint.inBaseMesh).asMesh()


        baseMeshFn = om.MFnMesh(baseMeshData)

        inBlendShapeHandle = dataBlock.inputArrayValue(FacialControllerConstraint.inBlendshapeInfoList)

        basePointPos = baseMeshFn.getPoint(pointIndex, om.MSpace.kObject)

        outPos = [0,0,0]

        for i in range(len(inBlendShapeHandle)):
            # print 'i,', i
            inBlendShapeHandle.jumpToPhysicalElement(i)
            currentBlendshapeInfoHandle = inBlendShapeHandle.inputValue()

            meshData = currentBlendshapeInfoHandle.child(FacialControllerConstraint.inMesh).asMesh()

            if meshData:
                meshFn = om.MFnMesh(meshData)

                weightListDataHandle = om.MArrayDataHandle(currentBlendshapeInfoHandle.child(FacialControllerConstraint.inWeightList))

                weightSum = 0

                for s in range(len(weightListDataHandle)):
                    # print 'i,', i
                    # print '--s,', s
                    weightListDataHandle.jumpToPhysicalElement(s)
                    weightSum += weightListDataHandle.inputValue().asFloat()

                # print '-weightSum,', weightSum

                pos = meshFn.getPoint(pointIndex, om.MSpace.kObject)
                # print '-pos,', pos

                deltaPos = [pos[0] - basePointPos[0], pos[1] - basePointPos[1], pos[2] - basePointPos[2]]
                # print '-deltaPos,', deltaPos
                deltaPos = [deltaPos[0] * weightSum, deltaPos[1] * weightSum, deltaPos[2] * weightSum]
                # print '-weighted delta pos,', deltaPos

                outPos[0] += deltaPos[0]
                outPos[1] += deltaPos[1]
                outPos[2] += deltaPos[2]

                # print '-outPos,', outPos

        offsetX = dataBlock.inputValue(FacialControllerConstraint.inOffsetX).asFloat()
        offsetY = dataBlock.inputValue(FacialControllerConstraint.inOffsetY).asFloat()
        offsetZ = dataBlock.inputValue(FacialControllerConstraint.inOffsetZ).asFloat()

        outPos[0] += basePointPos[0] + offsetX
        outPos[1] += basePointPos[1] + offsetY
        outPos[2] += basePointPos[2] + offsetZ

        outputDataHandle = dataBlock.outputValue(FacialControllerConstraint.outPositionX)
        outputDataHandle.setFloat(outPos[0])

        outputDataHandle = dataBlock.outputValue(FacialControllerConstraint.outPositionY)
        outputDataHandle.setFloat(outPos[1])

        outputDataHandle = dataBlock.outputValue(FacialControllerConstraint.outPositionZ)
        outputDataHandle.setFloat(outPos[2])

        dataBlock.setClean(plug)

# -----------------------------------------------------------------------------
# Initialize
# -----------------------------------------------------------------------------
def initializePlugin(obj):
    plugin = om.MFnPlugin(obj)
    try:
        plugin.registerNode(FacialControllerConstraint.kPluginNodeTypeName, FacialControllerConstraint.kPluginNodeId, FacialControllerConstraint.nodeCreator, FacialControllerConstraint.initialize)
    except:
        raise Exception('Failed to register node: %s'%FacialControllerConstraint.kPluginNodeTypeName)

# -----------------------------------------------------------------------------
# Uninitialize
# -----------------------------------------------------------------------------
def uninitializePlugin(obj):
    plugin = om.MFnPlugin(obj)
    try:
        plugin.deregisterNode(FacialControllerConstraint.kPluginNodeId)
    except:
        raise Exception('Failed to unregister node: %s'%FacialControllerConstraint.kPluginNodeTypeName)
