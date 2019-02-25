
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
class SampleValueOut(om.MPxNode):
    """
    A node to compute the arithmetic mean of two doubles.
    """
    ## the name of the nodeType
    kPluginNodeTypeName = 'SampleValueOut'
    ## the unique MTypeId for the node
    kPluginNodeId = om.MTypeId(0x0008311)

    inValueList = None

    inSampleValueMode = om.MObject()

    inRemapFromX = om.MObject()
    inRemapFromY = om.MObject()
    inRemapToX = om.MObject()
    inRemapToY = om.MObject()
    outValue = om.MObject()

    def __init__(self):
        om.MPxNode.__init__(self)
    

    @staticmethod
    def nodeCreator():
        return SampleValueOut()

    @staticmethod
    def initialize():
        nAttr2 = om.MFnNumericAttribute()
        SampleValueOut.inValue = nAttr2.create('inValue', 'iv', om.MFnNumericData.kFloat, 0.0)
        nAttr2.keyable = True

        nAttrValueMode = om.MFnEnumAttribute()
        SampleValueOut.inSampleValueMode = nAttrValueMode.create('mode', 'im', 0)
        nAttrValueMode.addField("normal", 0)
        nAttrValueMode.addField("multiply", 1)

        nAttrRemapFromX = om.MFnNumericAttribute()
        SampleValueOut.inRemapFromX = nAttrRemapFromX.create('remapFromX', 'rfx', om.MFnNumericData.kFloat, 0.0)
        nAttrRemapFromX.keyable = True
        nAttrRemapFromX.storable = True

        nAttrRemapFromY = om.MFnNumericAttribute()
        SampleValueOut.inRemapFromY = nAttrRemapFromY.create('remapFromY', 'rfy', om.MFnNumericData.kFloat, 1.0)
        nAttrRemapFromY.keyable = True
        nAttrRemapFromY.storable = True

        nAttrRemapToX = om.MFnNumericAttribute()
        SampleValueOut.inRemapToX = nAttrRemapToX.create('remapToX', 'rtx', om.MFnNumericData.kFloat, 0.0)
        nAttrRemapToX.keyable = True
        nAttrRemapToX.storable = True

        nAttrRemapToY = om.MFnNumericAttribute()
        SampleValueOut.inRemapToY = nAttrRemapToY.create('remapToY', 'rty', om.MFnNumericData.kFloat, 1.0)
        nAttrRemapToY.keyable = True
        nAttrRemapToY.storable = True

        nAttrOut = om.MFnNumericAttribute()
        SampleValueOut.outValue= nAttrOut.create('outValue', 'ov', om.MFnNumericData.kFloat, 0.0)
        nAttrOut.keyable = False
        nAttrOut.storable = False

        # add the attributes
        om.MPxNode.addAttribute(SampleValueOut.inValue)
        om.MPxNode.addAttribute(SampleValueOut.inSampleValueMode)
        om.MPxNode.addAttribute(SampleValueOut.inRemapFromX)
        om.MPxNode.addAttribute(SampleValueOut.inRemapFromY)
        om.MPxNode.addAttribute(SampleValueOut.inRemapToX)
        om.MPxNode.addAttribute(SampleValueOut.inRemapToY)

        om.MPxNode.addAttribute(SampleValueOut.outValue)
        
        # establish effects on output
        om.MPxNode.attributeAffects(SampleValueOut.inValue,        SampleValueOut.outValue)
        om.MPxNode.attributeAffects(SampleValueOut.inRemapFromX,        SampleValueOut.outValue)
        om.MPxNode.attributeAffects(SampleValueOut.inRemapFromY,        SampleValueOut.outValue)
        om.MPxNode.attributeAffects(SampleValueOut.inRemapToX,          SampleValueOut.outValue)
        om.MPxNode.attributeAffects(SampleValueOut.inRemapToY,          SampleValueOut.outValue)

    def compute(self, plug, dataBlock):
        # get the incoming data
        remapFromX = dataBlock.inputValue(SampleValueOut.inRemapFromX).asFloat()
        remapFromY = dataBlock.inputValue(SampleValueOut.inRemapFromY).asFloat()

        remapToX = dataBlock.inputValue(SampleValueOut.inRemapToX).asFloat()
        remapToY = dataBlock.inputValue(SampleValueOut.inRemapToY).asFloat()

        inValue = dataBlock.inputValue(SampleValueOut.inValue).asFloat()

        inValue = min(max(inValue, 0.0), 1.0)

        outValue = linearStep(inValue, remapFromX, remapFromY)
        outValue = lerp(outValue, remapToX, remapToY)

        # set the outgoing plug
        outputDataHandle = dataBlock.outputValue(SampleValueOut.outValue)
        outputDataHandle.setFloat(outValue)
        dataBlock.setClean(plug)

# -----------------------------------------------------------------------------
# Initialize
# -----------------------------------------------------------------------------
def initializePlugin(obj):
    plugin = om.MFnPlugin(obj)
    try:
        plugin.registerNode(SampleValueOut.kPluginNodeTypeName, SampleValueOut.kPluginNodeId, SampleValueOut.nodeCreator, SampleValueOut.initialize)
    except:
        raise Exception('Failed to register node: %s'%SampleValueOut.kPluginNodeTypeName)

# -----------------------------------------------------------------------------
# Uninitialize
# -----------------------------------------------------------------------------
def uninitializePlugin(obj):
    plugin = om.MFnPlugin(obj)
    try:
        plugin.deregisterNode(SampleValueOut.kPluginNodeId)
    except:
        raise Exception('Failed to unregister node: %s'%SampleValueOut.kPluginNodeTypeName)

def clamp(x, clampMin, clampMax):
    return max(min(x, clampMax),clampMin)

def linearStep(x, clampMin, clampMax):
    return clamp((x - clampMin) / (clampMax - clampMin + 0.000001), 0.0, 1.0)

def lerp(x, a, b):
    return (1 - x) * a + x * b