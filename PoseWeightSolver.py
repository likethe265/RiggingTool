
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
class PoseWeightSolver(om.MPxNode):
    """
    A node to compute the arithmetic mean of two doubles.
    """
    ## the name of the nodeType
    kPluginNodeTypeName = 'PoseWeightSolver'
    ## the unique MTypeId for the node
    kPluginNodeId = om.MTypeId(0x0007311)

    inWeightList = None
    inWeightMulList = None
    inOverridingWeight = om.MObject()
    inOverridingInt = om.MObject()
    outWeight = om.MObject()

    def __init__(self):
        om.MPxNode.__init__(self)
    

    @staticmethod
    def nodeCreator():
        return PoseWeightSolver()

    @staticmethod
    def initialize():
        nAttr1 = om.MFnNumericAttribute()
        PoseWeightSolver.inOverridingWeight = nAttr1.create('overridingWeight', 'iow', om.MFnNumericData.kFloat, 1.0)
        nAttr1.keyable = True

        nAttr1 = om.MFnNumericAttribute()
        PoseWeightSolver.inOverridingInt = nAttr1.create('overridingIntensity', 'ioi', om.MFnNumericData.kFloat, 0.0)
        nAttr1.keyable = True


        nAttr2 = om.MFnNumericAttribute()
        PoseWeightSolver.inWeightList = nAttr2.create('inWeightList', 'iWal', om.MFnNumericData.kFloat, 0.0)
        nAttr2.keyable = True
        nAttr2.array = True

        nAttr3 = om.MFnNumericAttribute()
        PoseWeightSolver.inWeightMulList = nAttr3.create('inWeightMulList', 'iWml', om.MFnNumericData.kFloat, 0.0)
        nAttr3.keyable = True
        nAttr3.array = True

        nAttrOut = om.MFnNumericAttribute()
        PoseWeightSolver.outWeight= nAttrOut.create('outWeight', 'ow', om.MFnNumericData.kFloat, 0.0)
        nAttrOut.keyable = False
        nAttrOut.storable = False

        # add the attributes
        om.MPxNode.addAttribute(PoseWeightSolver.inWeightList)
        om.MPxNode.addAttribute(PoseWeightSolver.inWeightMulList)
        om.MPxNode.addAttribute(PoseWeightSolver.inOverridingWeight)
        om.MPxNode.addAttribute(PoseWeightSolver.inOverridingInt)
        om.MPxNode.addAttribute(PoseWeightSolver.outWeight)
        
        # establish effects on output
        om.MPxNode.attributeAffects(PoseWeightSolver.inWeightList, PoseWeightSolver.outWeight)
        om.MPxNode.attributeAffects(PoseWeightSolver.inWeightMulList, PoseWeightSolver.outWeight)
        om.MPxNode.attributeAffects(PoseWeightSolver.inOverridingWeight, PoseWeightSolver.outWeight)
        om.MPxNode.attributeAffects(PoseWeightSolver.inOverridingInt, PoseWeightSolver.outWeight)


    def compute(self, plug, dataBlock):
        # get the incoming data
        inWeightListData    = dataBlock.inputArrayValue(PoseWeightSolver.inWeightList)
        inWeightMulListData = dataBlock.inputArrayValue(PoseWeightSolver.inWeightMulList)

        inWeightList = []

        inOverridingWeight = dataBlock.inputValue(PoseWeightSolver.inOverridingWeight).asFloat()
        inOverridingInt = dataBlock.inputValue(PoseWeightSolver.inOverridingInt).asFloat()

        for i in range(len(inWeightListData)):
            inWeightListData.jumpToPhysicalElement(i)

            w = inWeightListData.inputValue().asFloat()

            inWeightList.append(w)

        outWeight = sum(inWeightList)

        outWeight = min(max(outWeight, 0.0), 1.0)

        for i in range(len(inWeightMulListData)):
            inWeightMulListData.jumpToPhysicalElement(i)

            w = inWeightMulListData.inputValue().asFloat()
            outWeight *= w

        outWeight = min(max(outWeight, 0.0), 1.0)

        outWeight = outWeight * (1 - inOverridingInt) + inOverridingWeight * inOverridingInt

        # set the outgoing plug
        outputDataHandle = dataBlock.outputValue(PoseWeightSolver.outWeight)
        outputDataHandle.setFloat(outWeight)
        dataBlock.setClean(plug)

# -----------------------------------------------------------------------------
# Initialize
# -----------------------------------------------------------------------------
def initializePlugin(obj):
    plugin = om.MFnPlugin(obj)
    try:
        plugin.registerNode(PoseWeightSolver.kPluginNodeTypeName, PoseWeightSolver.kPluginNodeId, PoseWeightSolver.nodeCreator, PoseWeightSolver.initialize)
    except:
        raise Exception('Failed to register node: %s'%PoseWeightSolver.kPluginNodeTypeName)

# -----------------------------------------------------------------------------
# Uninitialize
# -----------------------------------------------------------------------------
def uninitializePlugin(obj):
    plugin = om.MFnPlugin(obj)
    try:
        plugin.deregisterNode(PoseWeightSolver.kPluginNodeId)
    except:
        raise Exception('Failed to unregister node: %s'%PoseWeightSolver.kPluginNodeTypeName)
