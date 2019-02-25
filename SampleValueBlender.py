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
class SampleValueBlender(om.MPxNode):
    """
    A node to compute the arithmetic mean of two doubles.
    """
    ## the name of the nodeType
    kPluginNodeTypeName = 'SampleValueBlender'
    ## the unique MTypeId for the node
    kPluginNodeId = om.MTypeId(0x0027512)

    inAllSampleInfoList = om.MObject()
    inPoseName = om.MObject()
    inSampleValue = om.MObject()
    inSampleValueMode = om.MObject()
    outWeightList = om.MObject()

    def __init__(self):
        om.MPxNode.__init__(self)

    @staticmethod
    def nodeCreator():
        return SampleValueBlender()

    @staticmethod
    def initialize():
        nAttrAllPoseInfoList = om.MFnCompoundAttribute()
        SampleValueBlender.inAllSampleInfoList = nAttrAllPoseInfoList.create('allSampleInfoList', 'pil')
        nAttrAllPoseInfoList.keyable = True
        nAttrAllPoseInfoList.array = True
        nAttrAllPoseInfoList.storable = True
        nAttrAllPoseInfoList.indexMatters = False

        nAttrPoseName = om.MFnTypedAttribute()
        SampleValueBlender.inPoseName = nAttrPoseName.create('poseName', 'pn', om.MFnData.kString)
        nAttrPoseName.keyable = True

        nAttrSampleValue = om.MFnNumericAttribute()
        SampleValueBlender.inSampleValue = nAttrSampleValue.create('sampleValue', 'sv', om.MFnNumericData.kFloat, 0.0)
        nAttrSampleValue.keyable = True
        nAttrSampleValue.array = True
        nAttrSampleValue.storable = True

        nAttrValueMode = om.MFnEnumAttribute()
        SampleValueBlender.inSampleValueMode = nAttrValueMode.create('sampleValueMode', 'm', 0)
        nAttrValueMode.addField("normal", 0)
        nAttrValueMode.addField("multiply", 1)

        nAttrAllPoseInfoList.addChild(SampleValueBlender.inPoseName)
        nAttrAllPoseInfoList.addChild(SampleValueBlender.inSampleValue)
        nAttrAllPoseInfoList.addChild(SampleValueBlender.inSampleValueMode)

        nAttrNum1 = om.MFnNumericAttribute()
        SampleValueBlender.inOverridingIntensity = nAttrNum1.create("overridingIntensity", "oi", om.MFnNumericData.kFloat, 0.0)
        nAttrNum1.keyable = False

        nAttrNum2 = om.MFnNumericAttribute()
        SampleValueBlender.inOverridingWeight = nAttrNum2.create("overridingWeight", "ow", om.MFnNumericData.kFloat, 1.0)
        nAttrNum2.keyable = False


        nAttrOut = om.MFnNumericAttribute()
        SampleValueBlender.outWeightList = nAttrOut.create('outWeightList', 'owl', om.MFnNumericData.kFloat, 0.0)
        nAttrOut.array = True
        nAttrOut.storable = True
        nAttrOut.usesArrayDataBuilder = True


        # add the attributes
        om.MPxNode.addAttribute(SampleValueBlender.inAllSampleInfoList)
        om.MPxNode.addAttribute(SampleValueBlender.outWeightList)

        om.MPxNode.attributeAffects(SampleValueBlender.inAllSampleInfoList, SampleValueBlender.outWeightList)

    def compute(self, plug, dataBlock):
        # get the incoming data
        # print 'compute'
        inAllSampleInfoList_mArrayDataHandle = dataBlock.inputArrayValue(SampleValueBlender.inAllSampleInfoList)

        poseNameList = []

        sampleValueList = []

        for i in range(len(inAllSampleInfoList_mArrayDataHandle)):
            # print 'i, ', i
            inAllSampleInfoList_mArrayDataHandle.jumpToPhysicalElement(i)
            currentSampleInfoDataHandle = inAllSampleInfoList_mArrayDataHandle.inputValue()

            poseName = currentSampleInfoDataHandle.child(SampleValueBlender.inPoseName).asString()
            poseNameList.append(poseName)

            blendMode = currentSampleInfoDataHandle.child(SampleValueBlender.inSampleValueMode).asInt()

            sampleValListData = om.MArrayDataHandle(currentSampleInfoDataHandle.child(SampleValueBlender.inSampleValue))

            sampleValueSum = 0
            # print 'len of sampleValListData, ', len(sampleValListData)

            if blendMode == 0:
                sampleValueSum = 0
            elif blendMode == 1:
                sampleValueSum = 1

            for s in range(len(sampleValListData)):
                sampleValListData.jumpToPhysicalElement(s)
                f = sampleValListData.inputValue().asFloat()

                if blendMode == 0:
                    sampleValueSum += f
                elif blendMode == 1:
                    sampleValueSum *= f


            sampleValueList.append(sampleValueSum)

        out_mArrayData = dataBlock.outputArrayValue(SampleValueBlender.outWeightList)
        builder  = out_mArrayData.builder()

        for n in range(len(sampleValueList)):
            newElem = builder.addElement(n)

            val = sampleValueList[n]
            val = max(min(val, 1), 0)
            newElem.setFloat(val)

        out_mArrayData.set(builder)

        dataBlock.setClean(plug)

def clamp(x, clampMin, clampMax):
    return max(min(x, clampMax),clampMin)

def linearStep(x, clampMin, clampMax):
    return clamp((x - clampMin) / (clampMax - clampMin + 0.000001), 0.0, 1.0)

def lerp(x, a, b):
    return (1 - x) * a + x * b

# -----------------------------------------------------------------------------
# Initialize
# -----------------------------------------------------------------------------
def initializePlugin(obj):
    plugin = om.MFnPlugin(obj)
    try:
        plugin.registerNode(SampleValueBlender.kPluginNodeTypeName, SampleValueBlender.kPluginNodeId,
                            SampleValueBlender.nodeCreator, SampleValueBlender.initialize)
    except:
        raise Exception('Failed to register node: %s' % SampleValueBlender.kPluginNodeTypeName)


# -----------------------------------------------------------------------------
# Uninitialize
# -----------------------------------------------------------------------------
def uninitializePlugin(obj):
    plugin = om.MFnPlugin(obj)
    try:
        plugin.deregisterNode(SampleValueBlender.kPluginNodeId)
    except:
        raise Exception('Failed to unregister node: %s' % SampleValueBlender.kPluginNodeTypeName)
