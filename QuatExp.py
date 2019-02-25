
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
class QuatExponentialMapping(om.MPxNode):
    """
    A node to compute the arithmetic mean of two doubles.
    """
    ## the name of the nodeType
    kPluginNodeTypeName = 'QuatExponentialMapping'
    ## the unique MTypeId for the node
    kPluginNodeId = om.MTypeId(0x0007320)

    inputQuatX = om.MObject()
    inputQuatY = om.MObject()
    inputQuatZ = om.MObject()
    inputQuatW = om.MObject()

    initQuatX = om.MObject()
    initQuatY = om.MObject()
    initQuatZ = om.MObject()
    initQuatW = om.MObject()

    outputExpQuatX = om.MObject()
    outputExpQuatY = om.MObject()
    outputExpQuatZ = om.MObject()

    kOutputQuatAttrName = 'o'
    kOutputQuatAttrLongName = 'outputQuaternion'

    def __init__(self):
        om.MPxNode.__init__(self)


    @staticmethod
    def nodeCreator():
        return QuatExponentialMapping()

    @staticmethod
    def initialize():
        nAttr = om.MFnNumericAttribute()

        # Current quaternion value
        QuatExponentialMapping.inputQuatX = nAttr.create('inputQuatX', 'iqx', om.MFnNumericData.kFloat, 0.0)
        nAttr.keyable = True

        QuatExponentialMapping.inputQuatY = nAttr.create('inputQuatY', 'iqy', om.MFnNumericData.kFloat, 0.0)
        nAttr.keyable = True

        QuatExponentialMapping.inputQuatZ = nAttr.create('inputQuatZ', 'iqz', om.MFnNumericData.kFloat, 0.0)
        nAttr.keyable = True

        QuatExponentialMapping.inputQuatW = nAttr.create('inputQuatW', 'iqw', om.MFnNumericData.kFloat, 0.0)
        nAttr.keyable = True

        # Initial quaternion value
        QuatExponentialMapping.initQuatX = nAttr.create('initQuatX', 'initiqx', om.MFnNumericData.kFloat, 0.0)
        nAttr.keyable = True

        QuatExponentialMapping.initQuatY = nAttr.create('initQuatY', 'initiqy', om.MFnNumericData.kFloat, 0.0)
        nAttr.keyable = True

        QuatExponentialMapping.initQuatZ = nAttr.create('initQuatZ', 'initiqz', om.MFnNumericData.kFloat, 0.0)
        nAttr.keyable = True

        QuatExponentialMapping.initQuatW = nAttr.create('initQuatW', 'initqw', om.MFnNumericData.kFloat, 0.0)
        nAttr.keyable = True

        nAttrOut = om.MFnNumericAttribute()
        QuatExponentialMapping.outputExpQuatX = nAttrOut.create('outputQuatX', 'oqx', om.MFnNumericData.kFloat, 0.0)
        QuatExponentialMapping.outputExpQuatY = nAttrOut.create('outputQuatY', 'oqy', om.MFnNumericData.kFloat, 0.0)
        QuatExponentialMapping.outputExpQuatZ = nAttrOut.create('outputQuatZ', 'oqz', om.MFnNumericData.kFloat, 0.0)
        # nAttrOut.indexMatters = True

        # add the attributes
        om.MPxNode.addAttribute(QuatExponentialMapping.initQuatX)
        om.MPxNode.addAttribute(QuatExponentialMapping.initQuatY)
        om.MPxNode.addAttribute(QuatExponentialMapping.initQuatZ)
        om.MPxNode.addAttribute(QuatExponentialMapping.initQuatW)

        om.MPxNode.addAttribute(QuatExponentialMapping.inputQuatX)
        om.MPxNode.addAttribute(QuatExponentialMapping.inputQuatY)
        om.MPxNode.addAttribute(QuatExponentialMapping.inputQuatZ)
        om.MPxNode.addAttribute(QuatExponentialMapping.inputQuatW)

        om.MPxNode.addAttribute(QuatExponentialMapping.outputExpQuatX)
        om.MPxNode.addAttribute(QuatExponentialMapping.outputExpQuatY)
        om.MPxNode.addAttribute(QuatExponentialMapping.outputExpQuatZ)

        # establish effects on output
        om.MPxNode.attributeAffects(QuatExponentialMapping.inputQuatX, QuatExponentialMapping.outputExpQuatX)
        om.MPxNode.attributeAffects(QuatExponentialMapping.inputQuatY, QuatExponentialMapping.outputExpQuatX)
        om.MPxNode.attributeAffects(QuatExponentialMapping.inputQuatZ, QuatExponentialMapping.outputExpQuatX)
        om.MPxNode.attributeAffects(QuatExponentialMapping.inputQuatW, QuatExponentialMapping.outputExpQuatX)

        om.MPxNode.attributeAffects(QuatExponentialMapping.inputQuatX, QuatExponentialMapping.outputExpQuatY)
        om.MPxNode.attributeAffects(QuatExponentialMapping.inputQuatY, QuatExponentialMapping.outputExpQuatY)
        om.MPxNode.attributeAffects(QuatExponentialMapping.inputQuatZ, QuatExponentialMapping.outputExpQuatY)
        om.MPxNode.attributeAffects(QuatExponentialMapping.inputQuatW, QuatExponentialMapping.outputExpQuatY)

        om.MPxNode.attributeAffects(QuatExponentialMapping.inputQuatX, QuatExponentialMapping.outputExpQuatZ)
        om.MPxNode.attributeAffects(QuatExponentialMapping.inputQuatY, QuatExponentialMapping.outputExpQuatZ)
        om.MPxNode.attributeAffects(QuatExponentialMapping.inputQuatZ, QuatExponentialMapping.outputExpQuatZ)
        om.MPxNode.attributeAffects(QuatExponentialMapping.inputQuatW, QuatExponentialMapping.outputExpQuatZ)


    def compute(self, plug, dataBlock):
        """Compute the arithmetic mean of input 1 and input 2."""
        # get the incoming data
        inputX = dataBlock.inputValue(QuatExponentialMapping.inputQuatX).asFloat()
        inputY = dataBlock.inputValue(QuatExponentialMapping.inputQuatY).asFloat()
        inputZ = dataBlock.inputValue(QuatExponentialMapping.inputQuatZ).asFloat()
        inputW = dataBlock.inputValue(QuatExponentialMapping.inputQuatW).asFloat()
        inputQuat = om.MQuaternion(inputX, inputY, inputZ, inputW)

        initX = dataBlock.inputValue(QuatExponentialMapping.initQuatX).asFloat()
        initY = dataBlock.inputValue(QuatExponentialMapping.initQuatY).asFloat()
        initZ = dataBlock.inputValue(QuatExponentialMapping.initQuatZ).asFloat()
        initW = dataBlock.inputValue(QuatExponentialMapping.initQuatW).asFloat()
        initialQuat = om.MQuaternion(initX, initY, initZ, initW)

        if quatDot(inputQuat, initialQuat) < 0:
            inputQuat = -inputQuat

        exponentialMappingQuat = om.MQuaternion.log(inputQuat)

        outputExpQuatX_dataHandle = dataBlock.outputValue(QuatExponentialMapping.outputExpQuatX)
        outputExpQuatY_dataHandle = dataBlock.outputValue(QuatExponentialMapping.outputExpQuatY)
        outputExpQuatZ_dataHandle = dataBlock.outputValue(QuatExponentialMapping.outputExpQuatZ)

        outputExpQuatX_dataHandle.setFloat(exponentialMappingQuat.x)
        outputExpQuatY_dataHandle.setFloat(exponentialMappingQuat.y)
        outputExpQuatZ_dataHandle.setFloat(exponentialMappingQuat.z)

        dataBlock.setClean(plug)
        return None

# for some reason the dot product operator (*) in MQuaternion is not working for me...
def quatDot(quat1, quat2):
    return quat1.x * quat2.x + quat1.y * quat2.y + quat1.z * quat2.z + quat1.w * quat2.w

# -----------------------------------------------------------------------------
# Initialize
# -----------------------------------------------------------------------------
def initializePlugin(obj):
    plugin = om.MFnPlugin(obj)
    try:
        plugin.registerNode(QuatExponentialMapping.kPluginNodeTypeName, QuatExponentialMapping.kPluginNodeId, QuatExponentialMapping.nodeCreator, QuatExponentialMapping.initialize)
    except:
        raise Exception('Failed to register node: %s'%QuatExponentialMapping.kPluginNodeTypeName)

# -----------------------------------------------------------------------------
# Uninitialize
# -----------------------------------------------------------------------------
def uninitializePlugin(obj):
    plugin = om.MFnPlugin(obj)
    try:
        plugin.deregisterNode(QuatExponentialMapping.kPluginNodeId)
    except:
        raise Exception('Failed to unregister node: %s'%QuatExponentialMapping.kPluginNodeTypeName)
