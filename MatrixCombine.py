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
class MatrixCombine(om.MPxNode):
    """
    A node to compute the arithmetic mean of two doubles.
    """
    ## the name of the nodeType
    kPluginNodeTypeName = 'MatrixCombine'
    ## the unique MTypeId for the node
    kPluginNodeId = om.MTypeId(0x0007310)

    inEditMode = om.MObject()
    inEditMatrix = om.MObject()

    inOverridingWeight = om.MObject()
    inOverridingIntensity = om.MObject()
    inOverridingPoseIndex = om.MObject()

    inInitialMatrix = None
    inMatrixList = om.MObject()
    inAllPoseInfoList = om.MObject()
    inPoseWeights = om.MObject()
    inPoseName = om.MObject()
    # outMatrix = None
    outTranslationX = om.MObject()
    outTranslationY = om.MObject()
    outTranslationZ = om.MObject()
    outRotationX = om.MObject()
    outRotationY = om.MObject()
    outRotationZ = om.MObject()
    # outRotation = None

    def __init__(self):
        om.MPxNode.__init__(self)

    @staticmethod
    def nodeCreator():
        return MatrixCombine()

    @staticmethod
    def initialize():
        nAttr0 = om.MFnMatrixAttribute()
        MatrixCombine.inInitialMatrix = nAttr0.create('initialMatrix', 'im')
        nAttr0.keyable = False

        nAttrAllWeightList = om.MFnCompoundAttribute()
        MatrixCombine.inAllPoseInfoList = nAttrAllWeightList.create('allPoseInfoList', 'pil')
        nAttrAllWeightList.keyable = True
        nAttrAllWeightList.array = True
        nAttrAllWeightList.storable = True
        nAttrAllWeightList.indexMatters = False

        nAttrPoseName = om.MFnTypedAttribute()
        MatrixCombine.inPoseName = nAttrPoseName.create('poseName', 'pl', om.MFnData.kString)
        nAttrPoseName.keyable = True

        nAttrMatList = om.MFnMatrixAttribute()
        MatrixCombine.inPoseMatrix = nAttrMatList.create("poseMatrix", 'pm')
        nAttrMatList.keyable = True

        nAttrWeightInPose = om.MFnNumericAttribute()
        MatrixCombine.inPoseWeights = nAttrWeightInPose.create('poseWeightList', 'pwl', om.MFnNumericData.kFloat, 0.0)
        nAttrWeightInPose.keyable = True
        nAttrWeightInPose.array = True
        nAttrWeightInPose.storable = True
        nAttrWeightInPose.indexMatters = False

        nAttrAllWeightList.addChild(MatrixCombine.inPoseName)
        nAttrAllWeightList.addChild(MatrixCombine.inPoseMatrix)
        nAttrAllWeightList.addChild(MatrixCombine.inPoseWeights)


        nAttrNum = om.MFnNumericAttribute()
        MatrixCombine.inEditMode = nAttrNum.create("editMode", "emd", om.MFnNumericData.kFloat, 0.0)
        nAttrNum.keyable = False

        nAttrEditMatrix = om.MFnMatrixAttribute()
        MatrixCombine.inEditMatrix = nAttrEditMatrix.create("editMatrix", "emx")
        nAttrEditMatrix.keyable = False

        nAttrNum1 = om.MFnNumericAttribute()
        MatrixCombine.inOverridingIntensity = nAttrNum1.create("overridingIntensity", "oi", om.MFnNumericData.kFloat, 0.0)
        nAttrNum1.keyable = False

        nAttrNum2 = om.MFnNumericAttribute()
        MatrixCombine.inOverridingWeight = nAttrNum2.create("overridingWeight", "ow", om.MFnNumericData.kFloat, 1.0)
        nAttrNum2.keyable = False

        nAttrNum2 = om.MFnNumericAttribute()
        MatrixCombine.inOverridingPoseIndex = nAttrNum2.create("overridingPoseIndex", "oid", om.MFnNumericData.kInt, 0)
        nAttrNum2.keyable = False




        nAttrOut = om.MFnNumericAttribute()
        MatrixCombine.outTranslationX = nAttrOut.create('outTranslationX', 'otx', om.MFnNumericData.kFloat, 0.0)
        nAttrOut.keyable = False
        nAttrOut.storable = False

        nAttrOut = om.MFnNumericAttribute()
        MatrixCombine.outTranslationY = nAttrOut.create('outTranslationY', 'oty', om.MFnNumericData.kFloat, 0.0)
        nAttrOut.keyable = False
        nAttrOut.storable = False

        nAttrOut = om.MFnNumericAttribute()
        MatrixCombine.outTranslationZ = nAttrOut.create('outTranslationZ', 'otz', om.MFnNumericData.kFloat, 0.0)
        nAttrOut.keyable = False
        nAttrOut.storable = False





        nAttrOut = om.MFnUnitAttribute()
        MatrixCombine.outRotationX = nAttrOut.create('outRotationX', 'orx', om.MFnUnitAttribute.kAngle, 0.0)
        nAttrOut.keyable = False
        nAttrOut.storable = False

        nAttrOut = om.MFnUnitAttribute()
        MatrixCombine.outRotationY = nAttrOut.create('outRotationY', 'ory', om.MFnUnitAttribute.kAngle , 0.0)
        nAttrOut.keyable = False
        nAttrOut.storable = False

        nAttrOut = om.MFnUnitAttribute()
        MatrixCombine.outRotationZ = nAttrOut.create('outRotationZ', 'orz', om.MFnUnitAttribute.kAngle , 0.0)
        nAttrOut.keyable = False
        nAttrOut.storable = False


        # add the attributes
        om.MPxNode.addAttribute(MatrixCombine.inInitialMatrix)
        om.MPxNode.addAttribute(MatrixCombine.inEditMode)
        om.MPxNode.addAttribute(MatrixCombine.inEditMatrix)
        om.MPxNode.addAttribute(MatrixCombine.inOverridingPoseIndex)
        om.MPxNode.addAttribute(MatrixCombine.inOverridingIntensity)
        om.MPxNode.addAttribute(MatrixCombine.inOverridingWeight)
        om.MPxNode.addAttribute(MatrixCombine.inAllPoseInfoList)

        om.MPxNode.addAttribute(MatrixCombine.outTranslationX)
        om.MPxNode.addAttribute(MatrixCombine.outTranslationY)
        om.MPxNode.addAttribute(MatrixCombine.outTranslationZ)
        om.MPxNode.addAttribute(MatrixCombine.outRotationX)
        om.MPxNode.addAttribute(MatrixCombine.outRotationY)
        om.MPxNode.addAttribute(MatrixCombine.outRotationZ)

        # establish effects on output
        om.MPxNode.attributeAffects(MatrixCombine.inOverridingIntensity, MatrixCombine.outTranslationX)
        om.MPxNode.attributeAffects(MatrixCombine.inOverridingPoseIndex, MatrixCombine.outTranslationX)
        om.MPxNode.attributeAffects(MatrixCombine.inOverridingWeight, MatrixCombine.outTranslationX)
        om.MPxNode.attributeAffects(MatrixCombine.inInitialMatrix, MatrixCombine.outTranslationX)
        om.MPxNode.attributeAffects(MatrixCombine.inAllPoseInfoList, MatrixCombine.outTranslationX)
        om.MPxNode.attributeAffects(MatrixCombine.inEditMode, MatrixCombine.outTranslationX)



        om.MPxNode.attributeAffects(MatrixCombine.inAllPoseInfoList, MatrixCombine.outRotationX)
        om.MPxNode.attributeAffects(MatrixCombine.inAllPoseInfoList, MatrixCombine.outRotationY)
        om.MPxNode.attributeAffects(MatrixCombine.inAllPoseInfoList, MatrixCombine.outRotationZ)


    def compute(self, plug, dataBlock):
        # get the incoming data
        inOverridingPoseIndex = dataBlock.inputValue(MatrixCombine.inOverridingPoseIndex).asInt()
        inOverridingWeight = dataBlock.inputValue(MatrixCombine.inOverridingWeight).asFloat()
        inOverridingIntensity = dataBlock.inputValue(MatrixCombine.inOverridingIntensity).asFloat()


        inInitialMatrix = dataBlock.inputValue(MatrixCombine.inInitialMatrix).asMatrix()
        inAllPoseInfoDataHandle = dataBlock.inputArrayValue(MatrixCombine.inAllPoseInfoList)
        inEditMode = dataBlock.inputValue(MatrixCombine.inEditMode).asFloat()
        inEditMatrix = dataBlock.inputValue(MatrixCombine.inEditMatrix).asMatrix()

        identityMatrix = om.MMatrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])

        poseTranslation = om.MVector()
        poseQuaternion = om.MQuaternion()
        poseTransformMatrix = om.MTransformationMatrix(identityMatrix)


        if inOverridingIntensity > 0.0:
            # set the outgoing plug
            inAllPoseInfoDataHandle.jumpToPhysicalElement(inOverridingPoseIndex)
            currentPoseInfoDataHandle = inAllPoseInfoDataHandle.inputValue()
            inPoseMatrixDataHandle = currentPoseInfoDataHandle.child(MatrixCombine.inPoseMatrix)
            poseMatrixData = inPoseMatrixDataHandle.asMatrix()
            poseMatrix = om.MMatrix(poseMatrixData)

            poseTransformMatrix = om.MTransformationMatrix(poseMatrix)
            poseTranslation = poseTransformMatrix .translation(1)
            poseQuaternion = om.MQuaternion(poseTransformMatrix.rotationComponents(asQuaternion = True))

        else:
            poseMatrixList = []
            poseWeightsList = []

            for i in range(len(inAllPoseInfoDataHandle)):
                inAllPoseInfoDataHandle.jumpToPhysicalElement(i)

                currentPoseInfoDataHandle = inAllPoseInfoDataHandle.inputValue()

                inPoseWeightDataHandle = currentPoseInfoDataHandle.child(MatrixCombine.inPoseWeights)
                inPoseMatrixDataHandle = currentPoseInfoDataHandle.child(MatrixCombine.inPoseMatrix)

                inPoseWeightArrayDataHandle = om.MArrayDataHandle(inPoseWeightDataHandle)

                poseMatrixData = inPoseMatrixDataHandle.asMatrix()
                poseMatrix = om.MMatrix(poseMatrixData)
                poseMatrixList.append(poseMatrix)

                poseWeight = 0

                for w in range(len(inPoseWeightArrayDataHandle)):
                    inPoseWeightArrayDataHandle.jumpToPhysicalElement(w)
                    poseWeight += inPoseWeightArrayDataHandle.inputValue().asFloat()

                if poseWeight > 1:
                    poseWeight = 1
                if poseWeight < 0:
                    poseWeight = 0

                poseWeightsList.append(poseWeight)


            # print 'poseWeightsList', poseWeightsList
            for i in range(len(poseMatrixList)):
                if poseWeightsList[i] > 0:
                    transMatrix = om.MTransformationMatrix(poseMatrixList[i])

                    translation = transMatrix.translation(1)
                    poseTranslation += translation * poseWeightsList[i]

                    quatTarget = om.MQuaternion(transMatrix.rotationComponents(asQuaternion = True))
                    quatIdentity = om.MQuaternion()
                    quatBlend = om.MQuaternion.slerp(quatIdentity, quatTarget, poseWeightsList[i])

                    poseQuaternion = poseQuaternion * quatBlend


        poseTransformMatrix.setRotationComponents(poseQuaternion, asQuaternion = True)
        poseTransformMatrix.setTranslation(poseTranslation, 1)

        inInitialTransform = om.MTransformationMatrix(inInitialMatrix)

        inInitialQuat = om.MQuaternion(inInitialTransform.rotationComponents())
        inInitTranslation = om.MVector(inInitialTransform.translation(1))

        poseTransformMatrix.translateBy(inInitTranslation, 1)

        finalTranslation = poseTransformMatrix.translation(1)
        finalQuaternion = poseQuaternion * inInitialQuat

        finalEuler = finalQuaternion.asEulerRotation()




        # set the outgoing plug
        outTranslationX = finalTranslation[0]
        outTranslationY = finalTranslation[1]
        outTranslationZ = finalTranslation[2]

        outRotationX = om.MAngle(finalEuler[0], 1)
        outRotationY = om.MAngle(finalEuler[1], 1)
        outRotationZ = om.MAngle(finalEuler[2], 1)

        # set the outgoing plug
        dataHandle0 = dataBlock.outputValue(MatrixCombine.outTranslationX)
        dataHandle0.setFloat(outTranslationX)

        dataHandle1 = dataBlock.outputValue(MatrixCombine.outTranslationY)
        dataHandle1.setFloat(outTranslationY)

        dataHandle2 = dataBlock.outputValue(MatrixCombine.outTranslationZ)
        dataHandle2.setFloat(outTranslationZ)

        dataHandleRot0 = dataBlock.outputValue(MatrixCombine.outRotationX)
        dataHandleRot0.setMAngle(outRotationX)

        dataHandleRot1 = dataBlock.outputValue(MatrixCombine.outRotationY)
        dataHandleRot1.setMAngle(outRotationY)

        dataHandleRot2 = dataBlock.outputValue(MatrixCombine.outRotationZ)
        dataHandleRot2.setMAngle(outRotationZ)

        dataBlock.setClean(plug)


# -----------------------------------------------------------------------------
# Initialize
# -----------------------------------------------------------------------------
def initializePlugin(obj):
    plugin = om.MFnPlugin(obj)
    try:
        plugin.registerNode(MatrixCombine.kPluginNodeTypeName, MatrixCombine.kPluginNodeId, MatrixCombine.nodeCreator,
                            MatrixCombine.initialize)
    except:
        raise Exception('Failed to register node: %s' % MatrixCombine.kPluginNodeTypeName)


# -----------------------------------------------------------------------------
# Uninitialize
# -----------------------------------------------------------------------------
def uninitializePlugin(obj):
    plugin = om.MFnPlugin(obj)
    try:
        plugin.deregisterNode(MatrixCombine.kPluginNodeId)
    except:
        raise Exception('Failed to unregister node: %s' % MatrixCombine.kPluginNodeTypeName)


def printMMatrix(matrix):
    '''
    Print the specified matrix values to the script editor
    @param matrix: Matrix to print
    @type matrix: maya.OpenMaya.MMatrix
    '''
    print ('%.3f' % matrix.getElement(0, 0)) + ', ' + ('%.3f' % matrix.getElement(0, 1)) + ', ' + (
            '%.3f' % matrix.getElement(0, 2)) + ', ' + ('%.3f' % matrix.getElement(0, 3))
    print ('%.3f' % matrix.getElement(1, 0)) + ', ' + ('%.3f' % matrix.getElement(1, 1)) + ', ' + (
            '%.3f' % matrix.getElement(1, 2)) + ', ' + ('%.3f' % matrix.getElement(1, 3))
    print ('%.3f' % matrix.getElement(2, 0)) + ', ' + ('%.3f' % matrix.getElement(2, 1)) + ', ' + (
            '%.3f' % matrix.getElement(2, 2)) + ', ' + ('%.3f' % matrix.getElement(2, 3))
    print ('%.3f' % matrix.getElement(3, 0)) + ', ' + ('%.3f' % matrix.getElement(3, 1)) + ', ' + (
            '%.3f' % matrix.getElement(3, 2)) + ', ' + ('%.3f' % matrix.getElement(3, 3))


def normalizeMatrix(matrix):
    r0 = om.MVector(matrix.getElement(0, 0), matrix.getElement(0, 1), matrix.getElement(0, 2))
    r1 = om.MVector(matrix.getElement(1, 0), matrix.getElement(1, 1), matrix.getElement(1, 2))
    r2 = om.MVector(matrix.getElement(2, 0), matrix.getElement(2, 1), matrix.getElement(2, 2))
    r3 = om.MVector(matrix.getElement(3, 0), matrix.getElement(3, 1), matrix.getElement(3, 2))

    r0 = r0.normalize()
    r1 = r1.normalize()
    r2 = r2.normalize()
    # r3 = r3.normalize()

    normalizedMat = om.MMatrix([r0[0], r0[1], r0[2], 0,
                                r1[0], r1[1], r1[2], 0,
                                r2[0], r2[1], r2[2], 0,
                                r3[0], r3[1], r3[2], 1])

    return normalizedMat
