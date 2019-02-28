import pymel.core as pm
import pymel.core.rendering as rd
import pymel.core.general as gen
import pymel.core.animation as anim
# import lxml.etree as ET
import xml.dom.minidom as dom
from pymel.all import *
import maya.cmds as cmd

namespace = ''
rootDic = 'E:\Pojects\Eve\Rigging\RiggingTool'

class Facial:
    name = ""
    facialMesh = 0
    facialMeshBackup = 0
    riggingFileParser = 0
    rootJoint = 0


    riggingFilePath = rootDic + '/rigging.xml'
    poseFilePath = rootDic + '/pose.xml'
    fbrFilePath = rootDic + '/Head.xml'


    jointManager = 0
    # controllerManager = 0
    samplerManager = 0
    poseManager = 0

    blendShapeCombinerNode = 0
    blendShapeMeshList = []
    poseWeightSolverList = []

    def __init__(self):
        self.facialMesh = pm.ls('NeturalPose')[0]
        self.facialMeshBackup = pm.ls('NeturalPoseBackup')[0]
        self.jointManager = JointManager()

        self.poseManager = PoseManager(self.jointManager)
        self.samplerManager = SampleManager(self.jointManager, self.poseManager)

        self.poseWeightSolverList = []
        self.scanRig()

    def scanRig(self):
        self.jointManager.collectAllFacialJoints()
        self.poseManager.collectAllPoses()
        self.samplerManager.collectAllSamples()

    # save the rigging scene into xml file
    def saveXML(self):
        doc = dom.getDOMImplementation().createDocument(None, 'Facial_Rig', None)
        root = doc.documentElement

        sampleGroupRoot = doc.createElement('Samples')
        poseRoot = doc.createElement('Poses')
        jointRoot = doc.createElement('Joints')
        attrRoot = doc.createElement('Attributes')

        for sampleGroup in self.samplerManager.sampleGroupList:
            elemSampleGrp = doc.createElement(sampleGroup.name)
            elemSampleGrp.setAttribute('controller', str(sampleGroup.controller))

            sampleGroupRoot.appendChild(elemSampleGrp)

            for sample in sampleGroup.sampleList:
                elemSample = doc.createElement(sample.name)
                elemSample.setAttribute('tx', str(sample.translation[0]))
                elemSample.setAttribute('ty', str(sample.translation[1]))
                elemSample.setAttribute('tz', str(sample.translation[2]))
                elemSampleGrp.appendChild(elemSample)

                for p in range(len(sample.poseBlendInfoList)):
                    pose = sample.poseBlendInfoList[p].pose
                    elemPose = doc.createElement(pose.name)
                    elemPose.setAttribute('weight', str(sample.poseBlendInfoList[p].value))
                    elemPose.setAttribute('mode', sample.poseBlendInfoList[p].mode)
                    elemSample.appendChild(elemPose)

        for pose in self.poseManager.allPoseList:
            elemPose = doc.createElement(pose.name)
            poseRoot.appendChild(elemPose)

            for faceJoint in pose.jointList:
                elemJoint = doc.createElement(faceJoint.name)
                elemJoint.setAttribute('transform', XMLUtility.encodeMatrixString(faceJoint.getPoseTransformLocal(pose)))
                elemPose.appendChild(elemJoint)

        for faceJoint in self.jointManager.faceJointList:
            elemJoint = doc.createElement(faceJoint.name)

            elemJoint.setAttribute('transform', XMLUtility.encodeMatrixString(faceJoint.initialTransform))
            elemJoint.setAttribute('parent', str(faceJoint.node.getParent()))
            jointRoot.appendChild(elemJoint)

        root.appendChild(sampleGroupRoot)
        root.appendChild(poseRoot)
        root.appendChild(jointRoot)
        root.appendChild(attrRoot)

        root.toxml()
        import codecs
        f = file(self.riggingFilePath, 'w')
        writer = codecs.lookup('utf-8')[3](f)
        doc.writexml(writer, '\n', '\t')

    def loadAllJoints(self, root):
        print '\nLoading All Joints...'
        elemAllJoints = root.getElementsByTagName("Joints")[0]
        for elemJoint in elemAllJoints.childNodes:
            if elemJoint.nodeType != 1:
                continue

            jointName = elemJoint.nodeName
            parentName = str(elemJoint.getAttribute('parent'))
            matrix = XMLUtility.decodeMatrixString(elemJoint.getAttribute('transform'))
            self.jointManager.createNewJoint(jointName, matrix, parentName)

    def loadAllPoses(self, root):
        print '\nLoading All Poses...'
        elemAllPoses = root.getElementsByTagName("Poses")[0]
        for elemPose in elemAllPoses.childNodes:
            if elemPose.nodeType != 1:
                continue
            pose = Pose(elemPose.tagName)
            for elemJoint in elemPose.childNodes:
                if elemJoint.nodeType != 1:
                    continue

                matrix = XMLUtility.decodeMatrixString(elemJoint.getAttribute('transform'))

                faceJoint = self.jointManager.getJointByName(elemJoint.tagName)
                faceJoint.addPoseTransform(pose, matrix)
                pose.jointList.append(faceJoint)

            print pose.name
            self.poseManager.allPoseList.append(pose)

    def loadBlendInfo(self, elemPose):
        outInst = BlendInfo()

        outInst.pose = self.poseManager.getPoseByName(elemPose.tagName)

        if elemPose.hasAttribute('remapFrom'):
            outInst.remapFrom = eval(elemPose.getAttribute('remapFrom'))

        if elemPose.hasAttribute('remapTo'):
            outInst.remapTo = eval(elemPose.getAttribute('remapTo'))

        return outInst

    def loadAllSamplesGroup(self, root):
        print '\nLoading All Sample Group ...'

        def loadPoseList(elemPoseList, sourcePoseList, sourceModeList):
            for elemPose in elemPoseList.childNodes:
                if elemPose.nodeType != 1:
                    continue

                poseName = elemPose.tagName
                pose = self.poseManager.getPoseByName(poseName)

                blendMode = "Normal"

                if elemPose.hasAttribute('mode'):
                    blendMode = elemPose.getAttribute('mode')

                sourcePoseList.append(pose)

                if blendMode == "Multiply":
                    sourceModeList.append(1)
                else:
                    sourceModeList.append(0)

        def loadAttributeList(elemAttributePoseList):
            for elemAttr in elemAttributePoseList.childNodes:
                if elemAttr.nodeType != 1:
                    continue

                newAttr = Attribute(elemAttr.tagName, newSampleGrp)

                for elemAttrPose in elemAttr.childNodes:
                    if elemAttrPose.nodeType != 1:
                        continue

                    blendInfoInst = self.loadBlendInfo(elemAttrPose)
                    newAttr.addLinkedPoseBlendInfoToAttribute(blendInfoInst)


        def loadSampleList(elemSampleList):
            print '\n --- Loading Samples ...'
            for elemSample in elemSampleList.childNodes:
                if elemSample.nodeType != 1:
                    continue

                nodeTranslation = [float(elemSample.getAttribute('tx')),
                                   float(elemSample.getAttribute('ty')),
                                   float(elemSample.getAttribute('tz'))]

                sample = Sample(elemSample.tagName, newSampleGrp, translation = nodeTranslation)
                sample.createNode()

                for elemPose in elemSample.childNodes:
                    if elemPose.nodeType != 1:
                        continue

                    blendInfoInst = self.loadBlendInfo(elemPose)
                    sample.addLinkedPoseBlendInfoToSample(blendInfoInst)



        def loadConstraintPoseList(elemConstraintPoseList):
            if elemConstraintPoseList:
                for elemConstraintPose in elemConstraintPoseList.childNodes:
                    if elemConstraintPose.nodeType != 1:
                        continue

                    poseName = elemConstraintPose.tagName
                    pose = self.poseManager.getPoseByName(poseName)
                    newSampleGrp.facialConstraintPoseList.append(pose)


        print '\nLoading All Samples...'
        elemAllSampleGroups = root.getElementsByTagName("SampleGroupList")[0]

        for elemSampleGrp in elemAllSampleGroups.childNodes:
            if elemSampleGrp.nodeType != 1:
                continue

            ctrlName = namespace + elemSampleGrp.getAttribute('controller')
            controller = ls(ctrlName)[0]

            newSampleGrp = SampleGroup(elemSampleGrp.tagName, controller, self)


            for grpChild in elemSampleGrp.childNodes:
                if grpChild.nodeType != 1:
                    continue

                if grpChild.tagName == "SamplePoseList":
                    loadPoseList(grpChild, newSampleGrp.samplePoseList, newSampleGrp.samplePoseBlendModeList)

                if grpChild.tagName == "AttributePoseList":
                    loadPoseList(grpChild, newSampleGrp.attributePoseList, newSampleGrp.attributePoseBlendModeList)

                elif grpChild.tagName == "SampleList":
                    loadSampleList(grpChild)

                elif grpChild.tagName == "AttributeList":
                    loadAttributeList(grpChild)

                elif grpChild.tagName == "ConstraintPoseList":
                    newSampleGrp.facialConstraintPointIndex = int(grpChild.getAttribute("pointIndex"))
                    newSampleGrp.facialConstraintOffset = eval(grpChild.getAttribute("offset"))
                    loadConstraintPoseList(grpChild)

            self.samplerManager.sampleGroupList.append(newSampleGrp)

            print '\nnew samplers'
            print newSampleGrp.name
            print '\n'




    def createBlendshapeHub(self):
        blendShapeNodeName = namespace + 'FB_BlendShapeHub_UTL'
        cmd.blendShape(str(self.facialMesh), name = blendShapeNodeName)

        self.blendShapeCombinerNode = pm.ls(blendShapeNodeName)[0]

        num = 0
        for p in range(len(self.poseManager.allPoseList)):
            poseName = self.poseManager.allPoseList[p].name
            poseWeightSolver = rd.shadingNode('PoseWeightSolver', name = namespace + 'FB_' + poseName + '_WeightCombiner_UTL', asUtility = True)
            self.poseWeightSolverList.append(poseWeightSolver)

            blendShapeMesh = pm.ls('FB_' + poseName + '_BT')

            if blendShapeMesh:
                blendShapeMesh = blendShapeMesh[0]
                self.blendShapeMeshList.append(blendShapeMesh)

                cmd.blendShape(blendShapeNodeName, edit=True, target=(str(self.facialMesh), num, str(blendShapeMesh), 1))

                poseWeightSolver.outWeight.connect(self.blendShapeCombinerNode.weight[num])

                num += 1


    # load the xml file and reconstruct the scene
    def reconstructSampler(self, rigMode):
        print '\nApplying Rig...'
        self.samplerManager.clear()

        toBeDel = []
        toBeDel.append(pm.ls('FB_*_SP'))
        toBeDel.append(pm.ls('FB_*_SP1'))
        toBeDel.append(pm.ls('FB_*_SP2'))
        toBeDel.append(pm.ls('FB_*_SP3'))
        toBeDel.append(pm.ls('FB_*_SP4'))
        toBeDel.append(pm.ls('FB_*_SP5'))
        toBeDel.append(pm.ls('*_*UTL*'))

        pm.delete(toBeDel)

        doc = dom.parse(self.riggingFilePath)
        root = doc.documentElement

        self.loadAllPoses(root)

        if rigMode == "Blendshape":
            self.createBlendshapeHub()

        self.loadAllSamplesGroup(root)

        self.samplerManager.setupAllSampleGroup(rigMode)
        self.samplerManager.setupAllFacialConstraint()

        print "\nAPPLYING XML FINISHED!"



    def loadXML(self):
        print '\nLOADING XML...'
        self.clearEverything()

        doc = dom.parse(self.riggingFilePath)
        root = doc.documentElement

        self.loadAllJoints(root)
        self.loadAllPoses(root)
        self.loadAllSamplesGroup(root)

        self.samplerManager.setupAllSampleGroup()

        print "\nLOADING XML FINISHED!"

    def clearEverything(self):
        # pm.delete(pm.ls(namespace + '*'))
        pm.delete(pm.ls(namespace + '*_EDT'))
        pm.delete(pm.ls(namespace + '*_UTL'))
        pm.delete(pm.ls(namespace + '*_UTL*'))
        pm.delete(pm.ls(namespace + '*SP'))

        self.jointManager.clear()
        self.samplerManager.clear()
        self.poseManager.clear()
        self.rootJoint = 0


class SampleManager:
    sampleGroupList = []
    jointManager = 0
    poseManager = 0

    def __init__(self, jointManager, poseManager):
        self.jointManager = jointManager
        self.poseManager = poseManager

    def clear(self):
        self.sampleGroupList = []

    def setupAllFacialConstraint(self):
        for sampleGroup in self.sampleGroupList:
            sampleGroup.setupFacialConstraint()

    def setupAllSampleGroup(self, rigMode):
        for sampleGroup in self.sampleGroupList:
            sampleGroup.setupAttribute()

            sampleGroup.setupRBFSolver()

            sampleGroup.setupSampleDataFlow(sampleGroup.rbfOutValueBlender)
            sampleGroup.setupSampleDataFlow(sampleGroup.attributeOutValueBlender)


    def getSampleByName(self, name):
        for sampleGroup in self.sampleGroupList:
            for sample in sampleGroup.sampleList:
                if sample.name == name:
                    return sample

        return None

    def getSampleGroupByName(self, name):
        for sampleGroup in self.sampleGroupList:
            if sampleGroup.name == name:
                return sampleGroup
        return None

    def createNewSample(self, sampleName, sampleGroupName = None):
        if not sampleGroupName:
            print 'ERROR: No Sample Group named ', sampleGroupName
            return

        sampleGroup = self.getSampleGroupByName(sampleGroupName)
        samplePosition = sampleGroup.controller.getMatrix().translate
        newSample = Sample(sampleName, sampleGroup, translation = samplePosition)
        newSample.createNode()


    def collectAllSamples(self):
        print 'collect all samples...'
        allSampleNodes = pm.ls(namespace + '*_SPGrp')

        if len(allSampleNodes) == 0:
            return

        for sgNode in allSampleNodes:
            sgName = str(sgNode)
            children = pm.listRelatives(sgNode)
            ctrlNode = 0

            for child in children:
                if '_CTL' in str(child):
                    ctrlNode = child

            grp = SampleGroup(sgName, ctrlNode, self)
            self.sampleGroupList.append(grp)

            tmp = pm.ls(grp.fullName + '_RBF_UTL')
            if len(tmp) > 0:
                grp.rbfSolver = tmp[0]



class SampleGroup:
    name = 0
    fullName = 0
    controller = 0
    facialConstraint = 0
    facialConstraintPointIndex = 0
    facialConstraintOffset = [0,0,0]
    facialConstraintPoseList = []
    sampleList = []
    rbfSolver = 0
    samplePoseList = []
    attributePoseList = []
    samplePoseBlendModeList = []
    attributePoseBlendModeList = []
    rbfOutValueBlender = 0
    attributeOutValueBlender = 0
    node = 0
    attributeList = []
    facial = 0

    def __init__(self, name, controller, facial):
        self.name = name
        self.fullName = namespace + name
        self.controller = controller
        self.sampleList = []
        self.node = pm.ls(self.fullName)[0]
        pm.parent(self.controller, self.node)
        self.controller.setAttr('tx', 0.0)
        self.controller.setAttr('ty', 0.0)
        self.controller.setAttr('tz', 0.0)

        self.samplePoseList = []
        self.attributePoseList = []
        self.samplePoseBlendModeList = []
        self.attributePoseBlendModeList = []
        self.attributePoseList = []
        self.facialConstraintPoseList = []
        self.attributeList = []
        self.facial = facial

    def setupFacialConstraint(self):
        if len(self.facialConstraintPoseList) > 0:
            self.facialConstraint = rd.shadingNode('FacialControllerConstraint', name = self.fullName + '_FC_UTL', asUtility = True)
            self.facial.facialMeshBackup.outMesh.connect(self.facialConstraint.inBaseMesh)
            self.facialConstraint.setAttr('inPointIndex', self.facialConstraintPointIndex)
            self.facialConstraint.setAttr('inOffsetX', self.facialConstraintOffset[0])
            self.facialConstraint.setAttr('inOffsetY', self.facialConstraintOffset[1])
            self.facialConstraint.setAttr('inOffsetZ', self.facialConstraintOffset[2])

            self.facialConstraint.outPositionX.connect(self.node.translate.translateX)
            self.facialConstraint.outPositionY.connect(self.node.translate.translateY)
            self.facialConstraint.outPositionZ.connect(self.node.translate.translateZ)

            for fcPose in self.facialConstraintPoseList:
                blendshapeMesh = pm.ls('FB_' + fcPose.name + '_BT')[0]
                blendShapeListAttr = self.facialConstraint.inBlendshapeInfoList
                numBT = pm.Attribute.numElements(blendShapeListAttr)
                blendshapeMesh.outMesh.connect(blendShapeListAttr[numBT].inMesh)

                relatedWeightCombinerList = pm.ls('FB_' + fcPose.name + '_WeightCombiner_UTL')

                for weightCombiner in relatedWeightCombinerList:
                    weightListAttr = self.facialConstraint.inBlendshapeInfoList[numBT].inWeightList

                    numWeight = pm.Attribute.numElements(weightListAttr)
                    weightCombiner.outWeight.connect(weightListAttr[numWeight])

    def setupAttribute(self):
        print '---> setup all attributes'
        for attribute in self.attributeList:
            attribute.createReferenceOnNode()

        self.attributeOutValueBlender = rd.shadingNode('SampleValueBlender', name = self.fullName + '_AttrValueBlender_UTL', asUtility = True)

        self.setupValueBlender(self.attributeOutValueBlender, self.attributePoseList, self.attributePoseBlendModeList)

        # link attributes list to value blender
        for i in range(len(self.attributeList)):
            attribute = self.attributeList[i]
            self.createAndConnectValueOut(attribute,
                                          self.attributeOutValueBlender,
                                          attribute.referenceOnNode)


    def setupRBFSolver(self):
        self.rbfSolver = rd.shadingNode('rbfBlender', name = self.fullName + '_RBF_UTL', asUtility = True)
        mel.addElement(str(self.rbfSolver) + '.inputsCompound')

        self.rbfSolver.setAttr('inputsCompound[0].sample[0]', 1.0)

        self.rbfOutValueBlender = rd.shadingNode('SampleValueBlender', name = self.fullName + '_RBFValueBlender_UTL', asUtility = True)

        # link the controller's translation to the blender lookup
        self.controller.tx.connect(self.rbfSolver.lookup[0])
        self.controller.ty.connect(self.rbfSolver.lookup[1])
        self.controller.tz.connect(self.rbfSolver.lookup[2])
        
        self.setupValueBlender(self.rbfOutValueBlender, self.samplePoseList, self.samplePoseBlendModeList)

        # link sample list to value blender
        for i in range(len(self.sampleList)):
            sample = self.sampleList[i]
            self.connectSample2RBF(sample, i + 1)
            self.createAndConnectValueOut(sample,
                                          self.rbfOutValueBlender,
                                          self.rbfSolver.output[i+1])

    def setupValueBlender(self, valueBlender, poseList, modeList):
        for p in range(len(poseList)):
            pose = poseList[p]
            mode = modeList[p]
            num = pm.Attribute.numElements(valueBlender.allSampleInfoList)
            valueBlender.setAttr('allSampleInfoList[%s].poseName' % str(num), pose.name)
            valueBlender.setAttr('allSampleInfoList[%s].sampleValueMode' % str(num), mode)


    def getPoseIndexInValueBlender(self, valueBlender, pose):
        num = pm.Attribute.numElements(valueBlender.allSampleInfoList)
        for n in range(num):
            poseNameInBlender = valueBlender.getAttr('allSampleInfoList[%s].poseName' %n)
            if poseNameInBlender == pose.name:
                return n
        return -1

    def getPoseIndexInValueBlenderByName(self, valueBlender, poseName):
        num = pm.Attribute.numElements(valueBlender.allSampleInfoList)
        for n in range(num):
            poseNameInBlender = valueBlender.getAttr('allSampleInfoList[%s].poseName' %n)
            if poseNameInBlender == poseName:
                return n
        return -1

    def connectSample2RBF(self, sample, index):
        mel.addElement(str(self.rbfSolver) + '.inputsCompound')

        mel.addSampleDimension(str(self.rbfSolver) + ".inputsCompound")

        sample.node.tx.connect(self.rbfSolver.inputsCompound[index].dataPoint[0])
        sample.node.ty.connect(self.rbfSolver.inputsCompound[index].dataPoint[1])
        sample.node.tz.connect(self.rbfSolver.inputsCompound[index].dataPoint[2])

        self.rbfSolver.setAttr('inputsCompound[%s].sample[%s]' % (str(index), str(index)), 1.0)

    # connect value out node to RBF solver and sample value blender
    # Source can be sample or attribute
    def createAndConnectValueOut(self, source, valueBlender, valueOutput):
        print 'createAndConnectValueOut'
        for k in range(len(source.poseBlendInfoList)):
            print '--- k', k
            pose = source.poseBlendInfoList[k].pose

            valueOutNodeName = source.fullName + '_' + pose.name + '_ValueOut_UTL'

            valueOutNode =  rd.shadingNode('SampleValueOut', name = valueOutNodeName, asUtility = True)
            valueOutNode.setAttr('remapFromX',  source.poseBlendInfoList[k].remapFrom[0])
            valueOutNode.setAttr('remapFromY',  source.poseBlendInfoList[k].remapFrom[1])
            valueOutNode.setAttr('remapToX',    source.poseBlendInfoList[k].remapTo[0])
            valueOutNode.setAttr('remapToY',    source.poseBlendInfoList[k].remapTo[1])

            valueOutput.connect(valueOutNode.inValue)

            source.valueOutNodeList.append(valueOutNode)

            # Connect to value blender
            poseInfoNum = pm.Attribute.numElements(valueBlender.allSampleInfoList)
            for n in range(poseInfoNum):
                poseName = valueBlender.getAttr('allSampleInfoList[%s].poseName' %(n))
                if poseName == pose.name:
                    sampleNum = pm.Attribute.numElements(valueBlender.allSampleInfoList[n].sampleValue)
                    valueOutNode.outValue.connect(valueBlender.allSampleInfoList[n].sampleValue[sampleNum])

    # connect Sample Value Bender to the Matrix Combiner of eachFace Joint, by matching the pose name
    # Source can be sample or attribute
    def connectSampleValueBlender2Joint(self, sourceList, valueBlender):
        numPose = pm.Attribute.numElements(valueBlender.allSampleInfoList)
        for i in range(numPose):
            poseName = valueBlender.getAttr('allSampleInfoList[%s].poseName' %i)

            # find the pose in all sample, if the pose exist, then connect the blender value to it
            for source in sourceList:
                poseIndexInSample = source.getLocalPoseIndexByName(poseName)
                print '-----> pose index in sample --->', poseIndexInSample
                if poseIndexInSample != -1:
                    poseInSample = source.poseBlendInfoList[poseIndexInSample].pose

                    for jnt in poseInSample.jointList:
                        jnt.connectValue2Joint(poseInSample, valueBlender.allSampleInfoList.outWeightList[i])

                    break

    def setupSampleDataFlow(self, valueBlender):
        numPose = pm.Attribute.numElements(valueBlender.allSampleInfoList)
        for i in range(numPose):
            poseName = valueBlender.getAttr('allSampleInfoList[%s].poseName' %i)
            valueBlendMode = valueBlender.getAttr('allSampleInfoList[%s].sampleValueMode' %i)
            poseIndexInAll = self.facial.poseManager.getPoseIndexByName(poseName)

            poseIndex = self.getPoseIndexInValueBlenderByName(valueBlender, poseName)

            print '\n-----> pose name --->', poseName
            print '-----> pose index in sample --->', poseIndex
            if poseIndex != -1:
                blenderAtt = valueBlender.allSampleInfoList.outWeightList[poseIndex]

                if valueBlendMode == 0:
                    weightAttr = self.facial.poseWeightSolverList[poseIndexInAll].inWeightList
                else:
                    weightAttr = self.facial.poseWeightSolverList[poseIndexInAll].inWeightMulList

                n = pm.Attribute.numElements(weightAttr)
                blenderAtt.connect(weightAttr[n])

        return False



class BlendingMode:
    Mul = "Multiplier"

class BlendInfo:
    pose = 0
    value = 0
    mode = 0
    remapFrom = ()
    remapTo = ()

    def __init__(self):
        self.pose = 0
        self.value = 0
        # self.mode = 0
        self.remapFrom = (0.0, 1.0)
        self.remapTo = (0.0, 1.0)



class Sample:
    name = 0
    fullName = 0
    node = 0
    controller = 0
    translation = [0, 0, 0]
    valueOutNodeList = []
    parentSampleGroup = 0
    poseBlendInfoList = []

    def __init__(self, name, sampleGroup, node = None, translation = None):
        self.name = name
        self.fullName = namespace + name
        self.valueOutNodeList = []
        self.blendControllerList = []
        self.blendAttributeList = []
        self.poseBlendInfoList = []

        if translation:
            self.translation = translation
        if node:
            self.node = node
            self.translation = [self.node.getAttr('tx'),
                                self.node.getAttr('ty'),
                                self.node.getAttr('tz')]

        self.parentSampleGroup = sampleGroup

        sampleGroup.sampleList.append(self)
        self.controller = sampleGroup.controller

    def createNode(self):
        s = pm.ls(self.fullName)
        if len(s) > 0:
            self.node = s[0]
        else:
            self.node = pm.spaceLocator(name = self.fullName)
        pm.parent(self.node, self.parentSampleGroup.node)
        self.node.setAttr('tx', self.translation[0])
        self.node.setAttr('ty', self.translation[1])
        self.node.setAttr('tz', self.translation[2])

        self.node.setAttr('rx', 0.0)
        self.node.setAttr('ry', 0.0)
        self.node.setAttr('rz', 0.0)

        self.node.addAttr('poseInfo', dt="string")
        self.node.setAttr('poseInfo', "[]")
    def addLinkedPoseBlendInfoToSample(self, poseBlendInfo):
        self.poseBlendInfoList.append(poseBlendInfo)
    def getLocalPoseIndexByName(self, poseName):
        for p in range(len(self.poseBlendInfoList)):
            if self.poseBlendInfoList[p].pose.name == poseName:
                return p
        return -1


# Data class for attributes
class Attribute:
    name = 0
    fullName = 0
    referenceOnNode = 0
    controller = 0
    valueList = []
    valueOutNodeList = []
    poseBlendInfoList = []

    def __init__(self, name, samplerGroup):
        self.name = name
        self.fullName = namespace + name
        self.controller = pm.ls(str(samplerGroup.controller))[0]
        self.valueList = []
        self.modeList = []
        self.valueOutNodeList = []

        samplerGroup.attributeList.append(self)

    def createReferenceOnNode(self):
        if not self.controller.hasAttr(self.name):
            self.controller.addAttr(self.name, at='double', k=1, maxValue = 1, minValue = 0)
        self.referenceOnNode = eval("pm.ls(\"%s\")[0].%s" %(str(self.controller), self.name))


    def addLinkedPoseBlendInfoToAttribute(self, poseBlendInfo):
        self.poseBlendInfoList.append(poseBlendInfo)
    def getLocalPoseIndexByName(self, poseName):
        for p in range(len(self.poseBlendInfoList)):
            if self.poseBlendInfoList[p].pose.name == poseName:
                return p
        return -1


# The wrapper class for joint,
# All functions that manipulate the Maya joint in the scene
class JointManager:
    faceJointList = []
    jointParentNameList = []
    editNodeRoot = 0

    def __init__(self):
        self.faceJointList = []
        self.jointParentNameList = []

    def clear(self):
        for faceJoint in self.faceJointList:
            faceJoint.clear()

        self.faceJointList = []
        self.jointParentNameList = []

        self.editNodeRoot = pm.shadingNode('transform', name = namespace + 'Root_EDT', asUtility=True)


    def collectAllFacialJoints(self):
        jointNodeList = pm.ls( namespace + 'FB*', type = Joint)
        print 'collectAllFacialJoints...'

        for each in jointNodeList:
            newJointInst = FaceJoint(self)
            hasRig = newJointInst.scanJointNode(each)

            if hasRig:
                self.faceJointList.append(newJointInst)
                self.jointParentNameList.append(str(each.getParent()))


    def createNewJoint(self, name, matrix, parentName = None):
        pm.select(cl=True)
        newJoint = FaceJoint(self)
        newJoint.createNode(name, matrix)
        self.faceJointList.append(newJoint)
        self.jointParentNameList.append(parentName)

    def setupHierachy(self):
        for i in range(len(self.faceJointList)):
            faceJoint = self.faceJointList[i]
            parentJnt = NodesUtility.getNodeByName(namespace + self.jointParentNameList[i])
            pm.parent(faceJoint.node, parentJnt)

    def getJointByName(self, name):
        for jnt in self.faceJointList:
            if jnt.fullName.find(name) != -1:
                return jnt

        return None

    def togglePoseOverrding(self, poseName, onOff):
        for faceJoint in self.faceJointList:
            poseIndex = faceJoint.getPoseIndexByName(poseName)

            if poseIndex != -1:
                faceJoint.matrixCombiner.setAttr('inOverridingPoseIndex', poseIndex)
                faceJoint.matrixCombiner.setAttr('inOverridingWeight', 1.0)

                if onOff:
                    faceJoint.matrixCombiner.setAttr('inOverridingIntensity', 1.0)
                else:
                    faceJoint.matrixCombiner.setAttr('inOverridingIntensity', 0.0)
            else:
                faceJoint.matrixCombiner.setAttr('inOverridingPoseIndex', 0)
                faceJoint.matrixCombiner.setAttr('inOverridingWeight', 1.0)
                faceJoint.matrixCombiner.setAttr('inOverridingIntensity', 0.0)


class FaceJoint:
    name = ''
    fullName = ''
    node = 0
    initialTransform = 0

    editTransformNode = 0

    matrixCombiner = 0
    jointManager = 0

    def __init__(self, jointManager):
        # self.poseTransformList = []
        self.jointManager = jointManager

    def clear(self):
        self.initialTransform = 0
        self.editTransformNode = 0
        # self.poseTransformList = []

        self.matrixCombiner = 0

    def createNode(self, name, matrix):
        self.name = name
        self.fullName = namespace + name

        self.node = pm.ls(self.fullName)[0]

        self.initialTransform = matrix
        self.createNewGraph()

    def scanJointNode(self, node):
        self.fullName = str(node)
        self.name = self.fullName
        self.node = node
        self.initialTransform = self.node.getAttr('xformMatrix')

        m = pm.ls(self.fullName + '_matCombine_UTL')
        if len(m) != 0:
            self.matrixCombiner = m[0]
        else:
            return False

        return True

    def checkHasGraph(self):
        hasMatCombiner = ls(self.name + '_matCombine_UTL')
        if hasMatCombiner:
            return True
        return False

    def createNewGraph(self):
        self.setupTransformSolver()

    def setEditMode(self, isEditModeOn, poseToEdit = None):
        if isEditModeOn:
            self.matrixCombiner.setAttr('editMode', 1.0)
            poseIndex = self.getPoseIndexByName(poseToEdit)
            poseMatrixLocal = self.matrixCombiner.getAttr('allPoseInfoList[%s].poseMatrix' %(str(poseIndex)))
            poseMatrixWorld = poseMatrixLocal * self.initialTransform
            self.editTransformNode.setMatrix(poseMatrixWorld)
        else:
            self.matrixCombiner.setAttr('editMode', 0.0)

    def applyEdit(self, pose):
        print 'pose', pose.name
        poseIndex = self.getPoseIndexByName(pose.name)
        print 'pose index', poseIndex
        poseMatrixWorld = self.editTransformNode.getMatrix()
        poseMatrixLocal = poseMatrixWorld * self.initialTransform.inverse()
        print 'pose world ', poseMatrixWorld
        print 'initial world ', self.initialTransform
        print 'pose local', poseMatrixLocal
        self.matrixCombiner.setAttr('allPoseInfoList[%s].poseMatrix' %(str(poseIndex)), poseMatrixLocal)

        # self.poseTransformList[poseIndex] = poseMatrixLocal
        self.setEditMode(False)

    def connectValue2Joint(self, pose, poseValueAttribute):
        poseIndex = self.getPoseIndexByName(pose.name)

        if poseIndex != -1:
            poseWeightIndex = 0
            safeBreak = 0
            while self.matrixCombiner.allPoseInfoList[poseIndex].poseWeightList[poseWeightIndex].isConnected() and safeBreak < 20:
                poseWeightIndex += 1
                safeBreak += 1

            poseValueAttribute.connect(self.matrixCombiner.allPoseInfoList[poseIndex].poseWeightList[poseWeightIndex])

    def getPoseNameList(self):
        poseNameList = []
        n = gen.Attribute.numElements(self.matrixCombiner.allPoseInfoList)
        for i in range(n):
            poseName = self.matrixCombiner.getAttr("allPoseInfoList[" + str(i) + "].poseName")
            poseNameList.append(poseName)

        return poseNameList

    def getPoseIndexByName(self, name):
        poseNameList = self.getPoseNameList()
        for i in range(len(poseNameList)):
            poseName = self.matrixCombiner.getAttr("allPoseInfoList[" + str(i) + "].poseName")
            if poseName == name:
                return i
        return -1

    def getPoseTransformLocal(self, pose):
        i = self.getPoseIndexByName(pose.name)
        matrixLocal = self.matrixCombiner.getAttr("allPoseInfoList[" + str(i) + "].poseMatrix")
        return matrixLocal



    def setupTransformSolver(self):
        self.matrixCombiner = rd.shadingNode('MatrixCombine', name = self.fullName + '_matCombine_UTL', asUtility = True)

        self.matrixCombiner.outTranslationX.connect(self.node.translateX)
        self.matrixCombiner.outTranslationY.connect(self.node.translateY)
        self.matrixCombiner.outTranslationZ.connect(self.node.translateZ)
        self.matrixCombiner.outRotationX.connect(self.node.rotateX)
        self.matrixCombiner.outRotationY.connect(self.node.rotateY)
        self.matrixCombiner.outRotationZ.connect(self.node.rotateZ)

        self.matrixCombiner.setAttr("initialMatrix", self.initialTransform)

        self.editTransformNode = pm.spaceLocator(name = NodesUtility.swapSuffix('_EDT', nodeName=self.fullName))
        self.editTransformNode.matrix.connect(self.matrixCombiner.editMatrix)
        pm.parent(self.editTransformNode, self.jointManager.editNodeRoot)



    def addPoseTransform(self, pose, matrix):
        # Connect the weight solver to the RBF solver
        relatedValueOutNodeList = ls(namespace + '*' + pose.name + '_ValueOut_UTL')

        # There should be 0 item in the relatedValueOutNodeList in the 1st rig construction
        for valueOutNode in relatedValueOutNodeList:
            self.connectValue2Joint(pose, valueOutNode)

        n = len(self.getPoseNameList())

        self.matrixCombiner.setAttr('allPoseInfoList[%s].poseMatrix' %n, matrix)
        self.matrixCombiner.setAttr('allPoseInfoList[%s].poseName' %n, pose.name)

class PoseManager:
    allPoseList = []
    editNodeList = []
    jointManager = 0

    def __init__(self, jointManager):
        self.allPoseList = []
        self.jointManager = jointManager

        return

    def editPose(self, poseName):
        pose = self.getPoseByName(poseName)
        pose.enterEditMode()

    def applyPoseEditByName(self, poseName):
        pose = self.getPoseByName(poseName)
        pose.applyPoseEdit()

    def clear(self):
        self.allPoseList = []

    def addNewPose(self, name):
        newPose = Pose(name)
        self.allPoseList.append(newPose)

    def getPoseByName(self, name):
        for pose in self.allPoseList:
            if pose.name == name:
                return pose
        return None

    def getPoseIndexByName(self, name):
        for i in range(len(self.allPoseList)):
            pose = self.allPoseList[i]
            if pose.name == name:
                return i
        return -1

    def includeJointsToPose(self, poseName, jointNodeList):
        pose = self.getPoseByName(poseName)
        for nd in jointNodeList:
            faceJoint = self.jointManager.getJointByName(str(nd))
            if faceJoint:
                pose.jointList.append(faceJoint)
                faceJoint.addPoseTransform(pose, datatypes.Matrix())


    def collectAllPoses(self):
        print 'collect all poses...'
        for faceJoint in self.jointManager.faceJointList:
            poseNameList = faceJoint.getPoseNameList()

            for i in range(len(poseNameList)):
                jointPoseName = poseNameList[i]
                pose = self.getPoseByName(jointPoseName)

                # if the pose is not in the list yet, then create a new pose
                if not pose:
                    pose = Pose(jointPoseName)
                    self.allPoseList.append(pose)

                # add the joint's transform into the pose joint transform list
                pose.jointList.append(faceJoint)


# Data class for pose
class Pose:
    name = 0
    jointList = []
    # transformList = []
    active = False
    inEditMode = True

    def __init__(self, name):
        self.name = name
        self.jointList = []
        # self.transformList = []

    def enterEditMode(self):
        self.inEditMode = True
        for faceJoint in self.jointList:
            faceJoint.setEditMode(True, poseToEdit=self.name)
        return

    def applyPoseEdit(self):
        for faceJoint in self.jointList:
            faceJoint.applyEdit(self)

        self.inEditMode = False


# The wrapper class for controller,
# All functions that manipulate the Maya shape-controller in the scene
# class Controller():
#     name = 0
#     fullname = 0
#     nodeType = 0
#     node = 0
#     size = 0
#     translation = 0
#     sampleList = []
#     attributeList = []
#
#     rbfSolver = 0
#
#     def __init__(self, name):
#         self.fullname = name
#         self.name = NodesUtility.removePrefix(name)
#         self.node = pm.ls(self.fullname)[0]




# class ControllerManager:
#     controllerList = []
#
#
#     def __init__(self):
#         pass





# DAG node class for RBF solving,
# Input: sample and controller,
# Output: the weight list
class RBFSolver:
    def __init__(self):
        pass



# Enum-like class

class ControllerType:
    cube = "cube"
    circle = "circle"


class LinkMode:
    additive = "additive"
    overriding = "overriding"
    condition = "condition"
    scaling = "scaling"



class NodesUtility:
    @classmethod
    def getNodeByName(cls, name):
        matchingList = pm.ls(name)
        if len(matchingList) > 0:
            return matchingList[0]
        else:
            return None

    @classmethod
    def isJoint(cls, node):
        if pm.objectType(node) == "joint":
            return True

    @classmethod
    def isCurve(cls, node):
        if pm.objectType(node) == "nurbsCurve":
            return True

    allChildren = []

    @classmethod
    def getNextChild(cls, rootObj, depthFirst = True):
        childrenList = rootObj.getChildren()

        if len(childrenList) > 0:
            # remove the 1st child if it is a Shape
            if childrenList[0][-5:] == 'Shape':
                del childrenList[0]

            #if width goes first, then add all the children into the list first
            if not depthFirst:
                cls.allChildren.extend(childrenList)

            for c in childrenList:
                #if depth goes first, then only add the first child in the remaining children list in the chain
                if depthFirst:
                    cls.allChildren.append(c)

                    cls.getNextChild(c, depthFirst)

    @classmethod
    def getAllChildren(cls, rootObj, depthFirst = True):
        cls.allChildren = []
        cls.getNextChild(rootObj, depthFirst)

        return cls.allChildren

    @classmethod
    def getWholeHierarchy(cls, rootObj, depthFirst = True):
        cls.allChildren = []
        cls.getNextChild(rootObj, depthFirst)

        hierarchy = [rootObj]
        hierarchy.extend(cls.allChildren)

        return hierarchy

    # node contain the full hierarchy path
    @classmethod
    def getNameFromNode(cls, node):
        return node.split('|')[-1]

    @classmethod
    def getShapeFromNode(cls, node):
        return pm.ls(node + 'Shape')[0]

    @classmethod
    def addSuffixToNameSegment(cls, nodeName, suffix, segmentIndex):
        nameArr = nodeName.split('_')
        newName = ''

        for i in range(0, len(nameArr)):
            if i == segmentIndex:
                newName += nameArr[i] + suffix + '_'

            elif i < len(nameArr) - 1:
                newName += nameArr[i] + '_'

            else:
                newName += nameArr[i]

        return newName

    @classmethod
    def getPrefix(cls, nodeName):
        nodeName = cls.getNameFromNode(nodeName)
        prefix = nodeName.split('_')[0]
        return prefix

    @classmethod
    def removePrefix(cls, nodeName):
        nodeName = cls.getNameFromNode(nodeName)
        nameList = nodeName.split('_')
        newName = ''

        for i in range(1, len(nameList)):
            if i < len(nameList) - 1:
                newName += nameList[i] + '_'
            else:
                newName += nameList[i]

        return newName

    @classmethod
    def swapSuffix(cls, suffix, node = None, nodeName = None):
        name = ""
        if node:
            name = cls.getNameFromNode(node)
        elif nodeName:
            name = nodeName

        nameList = name.split('_')
        newName = ''

        for i in range(0, len(nameList)):
            if i < len(nameList) - 1:
                newName += nameList[i] + '_'
            else:
                newName += suffix

        return newName

    @classmethod
    def mapVal(cls, mapNodeName, inputAttr, inputRange, outputRange, mappingKeys, interpType = 1):
        mapNode = gen.shadingNode('remapValue', asUtility = True, name = mapNodeName + '_UTL')

        # the shoulder rotate is inversing from the arm?
        #TODO: i might want to unify the rotation of shoulder and arm later
        gen.setAttr(mapNode.inputMin, inputRange[0])
        gen.setAttr(mapNode.outputMin, outputRange[0])
        gen.setAttr(mapNode.inputMax, inputRange[1])
        gen.setAttr(mapNode.outputMax, outputRange[1])

        for i in range(0, len(mappingKeys)):
            keyPos = mappingKeys[i][0]
            keyVal = mappingKeys[i][1]

            gen.setAttr(mapNode.value[i].value_Position, keyPos)
            gen.setAttr(mapNode.value[i].value_FloatValue, keyVal)
            gen.setAttr(mapNode.value[i].value_Interp, interpType)

        inputAttr.connect(mapNode.inputValue)

        return mapNode

    @classmethod
    def setLocalSpace(cls, offsetVector, referenceNode):
        referenceSpace = referenceNode.getMatrix(worldSpace=True)

        nodeXF = dt.Matrix()
        nodeXF.translate = offsetVector
        nodeXF = nodeXF * referenceSpace

        return nodeXF

class XFUtility:
    @classmethod
    def alignAll(cls, curNode, targetNode):
        curNode.setMatrix(targetNode.getMatrix(worldSpace=True), worldSpace = True)

    @classmethod
    def alignTranslation(cls, curNode, targetNode):
        srcTranslation = targetNode.getTranslation(worldSpace = True)
        curNode.setTranslation(srcTranslation, worldSpace = True)

    @classmethod
    def zeroTransformAttribute(cls, joint):
        joint.setAttr('translateX', 0)
        joint.setAttr('translateY', 0)
        joint.setAttr('translateZ', 0)
        joint.setAttr('translateZ', 0)
        joint.setAttr('rotateX', 0)
        joint.setAttr('rotateY', 0)
        joint.setAttr('rotateZ', 0)
        joint.setAttr('rotateZ', 0)
        joint.setAttr('scaleX', 1)
        joint.setAttr('scaleY', 1)
        joint.setAttr('scaleZ', 1)

    @classmethod
    def zeroJointOrientation(cls, joint):
        joint.setAttr('jointOrientX', 0)
        joint.setAttr('jointOrientY', 0)
        joint.setAttr('jointOrientZ', 0)

    @classmethod
    def scaleShape(cls, node, scaleFactor):
        pm.setAttr(node + 'Shape.localScaleX', scaleFactor)
        pm.setAttr(node + 'Shape.localScaleY', scaleFactor)
        pm.setAttr(node + 'Shape.localScaleZ', scaleFactor)

    @classmethod
    def freezeTransform(cls, node):
        pm.makeIdentity(node, apply = True)

    @classmethod
    def freezeRotation(cls, node):
        pm.makeIdentity(node, apply = True, rotate = True)

    @classmethod
    def alignPivot2Translation(cls, curNode, targetNode):
        pivot = targetNode.getTranslation(worldSpace = True)
        pm.xform(curNode, worldSpace = True, piv = pivot)

    @classmethod
    def alignPivot2TranslationXF(cls, curNode, targetTransform):
        pivot = targetTransform.translate
        pm.xform(curNode, worldSpace = True, piv = pivot)

    @classmethod
    def alignObjToPath(cls, obj, pathObject, percentage, index, deletePathConstraint = True, followPath = True):
        hyperNodeName = 'hyperNode' + obj + str(index)


        anim.pathAnimation(obj, curve = pathObject, bank = followPath, followAxis = 'y',
                           name = hyperNodeName, fractionMode = True,
                           upAxis = 'z', worldUpType = 'normal', worldUpVector = (0,1,0))

        if deletePathConstraint:
            pathValNodes = pm.ls('*_uValue')
            pm.delete(pathValNodes)
            pm.ls(hyperNodeName)[0].setAttr('u', percentage)


        return ls(hyperNodeName)[0]

    @classmethod
    def getJointChainSpace(cls, limbRoot, limbEnd, includingTranslation = False):
        limbRootPos = limbRoot.getTranslation(worldSpace = True)
        limbEndPos = limbEnd.getTranslation(worldSpace = True)

        limbPlaneTan = limbEndPos - limbRootPos
        limbPlaneTan.normalize()

        limbRootSpace = limbRoot.getMatrix(worldSpace = True)[0]
        limbRootX = dt.Vector(limbRootSpace[0], limbRootSpace[1], limbRootSpace[2])
        limbRootX.normalize()

        limbPlaneBinorm = cross(limbRootX, limbPlaneTan)
        limbPlaneBinorm.normal()

        limbPlaneNorm = cross(limbPlaneTan, limbPlaneBinorm)
        limbPlaneNorm.normal()

        jointChainSpace = dt.Matrix(limbPlaneNorm,limbPlaneTan, limbPlaneBinorm)
        if includingTranslation:
            jointChainSpace.translate = dt.Vector()

        return jointChainSpace

    @classmethod
    def alignRotation(cls, curNode, srcNode):
        srcNodeRotSpace = srcNode.getMatrix(worldSpace = True)
        srcNodeRotSpace.translate = curNode.getTranslation(worldSpace=True)
        curNode.setMatrix(srcNodeRotSpace, worldSpace=True)


class XMLUtility:
    def __init__(self):
        return

    @classmethod
    def encodeColorString(cls, color):
        return str(color.GetR()) + ',' + str(color.GetG()) + ',' + str(color.GetB())

    @classmethod
    def decodeColorString(cls, colorString):
        colorStrList = colorString.split(',')
        colorValue = mp.Color(float(colorStrList[0]), float(colorStrList[1]), float(colorStrList[2]))
        return colorValue

    @classmethod
    def encodeBoneSize(cls, bone):
        return str(bone.BaseObject.ParameterBlock.Length.Value) + ',' + \
               str(bone.BaseObject.ParameterBlock.Width.Value) + ',' + \
               str(bone.BaseObject.ParameterBlock.Height.Value)

    @classmethod
    def decodeBoneSize(cls, boneSizeString):
        boneSizeStrList = boneSizeString.split(',')
        length = float(boneSizeStrList[0])
        width = float(boneSizeStrList[1])
        height = float(boneSizeStrList[2])
        return length, width, height

    @classmethod
    def encodeMatrixString(cls, matrix):
        matrixString = str(matrix[0][0]) + ' ' + str(matrix[0][1]) + ' ' + str(matrix[0][2]) + ' ' + str(matrix[0][3]) + ' ; ' + \
                       str(matrix[1][0]) + ' ' + str(matrix[1][1]) + ' ' + str(matrix[1][2]) + ' ' + str(matrix[1][3]) + ' ; ' + \
                       str(matrix[2][0]) + ' ' + str(matrix[2][1]) + ' ' + str(matrix[2][2]) + ' ' + str(matrix[2][3]) + ' ; ' + \
                       str(matrix[3][0]) + ' ' + str(matrix[3][1]) + ' ' + str(matrix[3][2]) + ' ' + str(matrix[3][3])

        return matrixString

    @classmethod
    def decodeMatrixString(cls, matrixString):
        matrixStringSplit = matrixString.split('; ')

        l = []

        for item in matrixStringSplit:
            subl = []
            itemSplit = item.split(' ')
            for n in range(4):
                subl.append(float(itemSplit[n]))
            l.append(subl)

        matrixValue = datatypes.Matrix(l)

        return matrixValue

#
# toDel = pm.ls('FR_*')
# pm.delete(toDel)
#
# class Main:
#     facial = 0
#
#     def __init__(self):
#         self.facial = Facial()
#
# app = Main()
#
# # app.facial.saveXML()
# app.facial.loadXML()
#

