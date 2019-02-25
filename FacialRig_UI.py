import sys


from PySide2.QtCore import *
from PySide2.QtWidgets import *
from functools import partial

import pymel.core as pm
import re
rootDicionary = 'D:\\OneDrive\\ToyLabsP4v\\FacialRig\\Maya\\Main'
sys.path.append(rootDicionary)


import RigBuilder as rb

reload(rb)

from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

class WidgetHierarchyTree(MayaQWidgetBaseMixin, QWidget):

    cbOverrideMode = 0
    spnPoseValue = 0

    cbPoseFilterBySample = 0
    cbSampleFilterBySampleGroup = 0
    cbJointFilterByPose = 0

    btnInitialPose = 0
    btnSaveRig = 0
    btnLoadRig = 0
    btnApplyJointRig = 0
    btnApplyBlendshapeRig = 0
    btnAddPose = 0
    btnRemovePose = 0

    btnSavePose = 0

    etNewSampleName = 0
    btnNewSample = 0
    btnAddSampleToGroup = 0
    btnAddPoseToSample = 0
    lvSampleList = 0
    lvSampleGroupList = 0

    btnIncludeJoint = 0
    btnExcludeJoint = 0
    lvPoseList = 0
    etPoseSearch = 0
    etSampleSearch = 0
    facial = 0
    poseInEdit = 0

    pickStandardPose = 0
    mirrorPose = 0

    def __init__(self, *args, **kwargs):
        super(WidgetHierarchyTree, self).__init__(*args, **kwargs)
        self.facial = rb.Facial()
        self.createUI()
        self.connectFunction()
        self.refreshPoseList()
        self.refreshSampleGroupList()
        self.refreshSampleList()




    def createUI(self):
        # Destroy this widget when closed.
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        treeViewWidth = 120
        treeViewWidthMax = 160
        listWidth = 200
        listWidthMax = 300

        lyRoot = QHBoxLayout()
        lyMain = QVBoxLayout()
        lySamples = QVBoxLayout()
        lyPose = QVBoxLayout()
        lyJoint = QVBoxLayout()
        lyTool =  QVBoxLayout()


        self.cbOverrideMode = QCheckBox("Overriding Mode")
        self.cbPoseFilterBySample = QCheckBox("By Sample")
        self.cbSampleFilterBySampleGroup = QCheckBox("By Sample Group")
        self.spnPoseValue = QDoubleSpinBox ()
        self.spnPoseValue.setValue(1.0)
        self.spnPoseValue.setSingleStep(0.1)
        self.spnPoseValue.setMaximum(1.0)
        self.spnPoseValue.setMinimum(-1.0)
        self.btnSaveRig = QPushButton("Save Rig")
        self.btnLoadRig = QPushButton("Load Rig")
        self.btnApplyJointRig = QPushButton("Apply Joint Rig")
        self.btnApplyBlendshapeRig = QPushButton("Apply Blendshape Rig")


        self.btnInitialPose = QPushButton("Initial Pose")
        self.btnAddPose = QPushButton("Add New Pose")
        self.btnRemovePose = QPushButton("Remove Pose")
        self.lvPoseList = QListWidget()
        self.etPoseSearch = QTextEdit("")
        self.etPoseSearch.setFixedHeight(32)
        self.etSampleSearch = QTextEdit("")
        self.etSampleSearch.setFixedHeight(32)
        self.btnIncludeJoint = QPushButton("Include Joint")
        self.btnExcludeJoint = QPushButton("Exclude Joint")

        self.btnEditPose = QPushButton("Edit")
        self.btnApplyPoseEdit = QPushButton("Apply")
        self.btnCancelPoseEdit = QPushButton("Cancel")

        self.lvPoseJointList = QListWidget()

        self.lvSampleList = QListWidget()
        self.lvSampleGroupList = QListWidget()

        self.etNewSampleName = QTextEdit("NewSample")
        self.etNewSampleName.setFixedHeight(32)

        self.btnNewSample = QPushButton("New Sample")
        self.btnAddSampleToGroup = QPushButton("Add To Group")
        self.btnAddPoseToSample = QPushButton("Add Pose To Sample")

        self.lvAttributeList = QListWidget()
        self.lvControllerList = QListWidget()

        self.pickStandardPose = QPushButton("Pick Standard Pose")
        self.mirrorPose = QPushButton("Mirror Picked Pose")

        lyPoseManage = QHBoxLayout()
        lyPoseManage.addWidget(self.cbOverrideMode)
        lyPoseManage.addWidget(self.cbPoseFilterBySample)
        lyPoseManage.addWidget(self.spnPoseValue)

        lySampleManage = QHBoxLayout()
        lySampleManage.addWidget(self.etSampleSearch)
        lySampleManage.addWidget(self.cbSampleFilterBySampleGroup)
        
        lySaveLoad = QVBoxLayout()
        lySaveLoad.addWidget(self.btnApplyJointRig)
        lySaveLoad.addWidget(self.btnApplyBlendshapeRig)
        lySaveLoad.addWidget(self.btnSaveRig)

        lyMain.addLayout(lySaveLoad)

        lySamples.addWidget(self.etNewSampleName)
        lySamples.addWidget(self.btnNewSample)
        lySamples.addWidget(self.btnAddSampleToGroup)
        lySamples.addWidget(self.btnAddPoseToSample)
        lySamples.addWidget(self.lvSampleGroupList)
        lySamples.addLayout(lySampleManage)
        lySamples.addWidget(self.lvSampleList)


        lyPose.addWidget(self.btnAddPose)
        lyPose.addWidget(self.btnRemovePose)
        lyPose.addWidget(self.btnEditPose)
        lyPose.addWidget(self.btnApplyPoseEdit)
        lyPose.addWidget(self.btnCancelPoseEdit)

        lyJoint.addWidget(self.btnIncludeJoint)
        lyJoint.addWidget(self.btnExcludeJoint)
        lyJoint.addWidget(self.lvPoseJointList)
        lyMain.addLayout(lyJoint)


        lyPose.addWidget(self.btnInitialPose)
        lyPose.addLayout(lyPoseManage)
        lyPose.addWidget(self.etPoseSearch)
        lyPose.addWidget(self.lvPoseList)
# useful tools to deal with the poses
        lyTool.addWidget(self.pickStandardPose)
        lyTool.addWidget(self.mirrorPose)


        lyRoot.addLayout(lyMain)
        lyRoot.addLayout(lyPose)
        lyRoot.addLayout(lySamples)
        lyRoot.addLayout(lyTool)


        self.setLayout(lyRoot)

        self.setWindowTitle("Facial Rig Builder")

        # self.setMinimumWidth(listWidth + treeViewWidth)
        # self.setMaximumWidth(listWidthMax + treeViewWidthMax)


    def connectFunction(self):
        self.btnSaveRig.clicked.connect(self.saveXML)
        self.btnLoadRig.clicked.connect(self.loadXML)
        self.btnApplyJointRig.clicked.connect(self.applyJointRig)
        self.btnApplyBlendshapeRig.clicked.connect(self.applyBlendshapeRig)
        self.btnEditPose.clicked.connect(self.gotoEditPose)
        self.etPoseSearch.textChanged.connect(self.refreshPoseList)
        self.btnApplyPoseEdit.clicked.connect(self.applyPoseEdit)
        self.btnIncludeJoint.clicked.connect(self.includeJoint)
        self.lvPoseJointList.itemSelectionChanged.connect(self.onPoseJointListSelectionChange)
        self.lvPoseList.itemSelectionChanged.connect(self.onPoseListSelectionChange)
        self.lvSampleGroupList.itemSelectionChanged.connect(self.onSampleGroupListSelectionChange)
        self.lvSampleList.itemSelectionChanged.connect(self.onSampleListSelectionChange)
        self.cbOverrideMode.stateChanged.connect(self.setOverridingMode)
        self.spnPoseValue.valueChanged.connect(self.setPoseValue)
        self.cbSampleFilterBySampleGroup.stateChanged.connect(self.setSampleFilterBySampleGroup)
        self.cbPoseFilterBySample.stateChanged.connect(self.setPoseFilterBySample)
        self.btnInitialPose.clicked.connect(self.gotoInitialPose)

        self.btnNewSample.clicked.connect(self.createSample)
        self.btnAddSampleToGroup.clicked.connect(self.addSampleToGroup)
        self.btnAddPoseToSample.clicked.connect(self.addPoseToSample)


    def createSample(self):
        if not self.lvSampleGroupList.currentItem():
            print 'ERROR: please select a sample group to create a sample'
            return

        sampleName = self.etNewSampleName.toPlainText()
        sampleGroupName = self.lvSampleGroupList.currentItem().text()
        self.facial.samplerManager.createNewSample(sampleName, sampleGroupName)

        sampleGroup = self.facial.samplerManager.getSampleGroupByName(sampleGroupName)
        self.refreshSampleList(sampleGroup)



    def addSampleToGroup(self):
        self.facial.samplerManager.addSampleToGroup()
        return


    def addPoseToSample(self):
        poseListItem = self.lvPoseList.currentItem()

        if not poseListItem:
            return

        poseName = poseListItem.text()
        pose = self.facial.poseManager.getPoseByName(poseName)

        sampleName = self.lvSampleList.currentItem().text()
        sample = self.facial.samplerManager.getSampleByName(sampleName)

        value = self.spnPoseValue.value()
        mode = "Absolute"
        sample.addLinkedPose(pose, value, mode)

        self.refreshPoseList()

    def loadXML(self):
        # self.facial.loadXML()
        # self.refreshPoseList()
        # self.refreshSampleGroupList()
        #
        self.facial.reconstructSampler()
        self.refreshSampleGroupList()

    def applyJointRig(self):
        self.facial.reconstructSampler("Joint")

    def applyBlendshapeRig(self):
        self.facial.reconstructSampler("Blendshape")

    def saveXML(self):
        self.facial.saveXML()

    def gotoEditPose(self):
        poseName = self.lvPoseList.currentItem().text()
        self.poseInEdit = poseName
        self.facial.poseManager.editPose(poseName)
        self.lvPoseList.setEnabled(False)

    def applyPoseEdit(self):
        self.facial.poseManager.applyPoseEditByName(self.poseInEdit)
        self.lvPoseList.setEnabled(True)

        return

    def includeJoint(self):
        jointList = pm.ls(selection = True)
        poseName = self.lvPoseList.currentItem().text()
        if len(jointList) > 0:
            self.facial.poseManager.includeJointsToPose(poseName, jointList)
        self.refreshPoseJointList()

    def setPoseFilterBySample(self):
        self.refreshPoseList()

    def setSampleFilterBySampleGroup(self):
        self.refreshSampleList()

    def setPoseValue(self):
        poseItem = self.lvPoseList.currentItem()
        sampleItem = self.lvSampleList.currentItem()

        if poseItem and sampleItem:
            poseName = poseItem.text()
            sampleName = sampleItem.text()

            pose = self.facial.poseManager.getPoseByName(poseName)
            sample = self.facial.samplerManager.getSampleByName(sampleName)

            sample.updateValueOutNode(pose.name, self.spnPoseValue.value())

    def setOverridingMode(self):
        poseName = self.lvPoseList.currentItem().text()
        onOff = self.cbOverrideMode.isChecked()
        self.facial.jointManager.togglePoseOverrding(poseName, onOff)

    def onPoseJointListSelectionChange(self):
        jointName = self.lvPoseJointList.currentItem().text()
        pm.select(self.facial.jointManager.getJointByName(jointName).node)

    def onPoseListSelectionChange(self):
        self.refreshPoseJointList()

        if self.cbOverrideMode.isChecked():
            poseName = self.lvPoseList.currentItem().text()
            self.facial.jointManager.togglePoseOverrding(poseName, True)

    def onSampleGroupListSelectionChange(self):
        sampleGroupName = self.lvSampleGroupList.currentItem().text()
        sampleGroup = self.facial.samplerManager.getSampleGroupByName(sampleGroupName)
        pm.select(sampleGroup.node)
        self.refreshSampleList(sampleGroup = sampleGroup)

    def onSampleListSelectionChange(self):
        sampleName = self.lvSampleList.currentItem().text()
        sample = self.facial.samplerManager.getSampleByName(sampleName)
        pm.select(sample.node)
        self.refreshPoseList()

    def refreshSampleList(self, sampleGroup = None):
        self.lvSampleList.clear()
        sampleNameList = []
        if sampleGroup and self.cbSampleFilterBySampleGroup.isChecked():
            for sample in sampleGroup.sampleList:
                sampleNameList.append(sample.name)
        else:
            for sampleGroup in self.facial.samplerManager.sampleGroupList:
                for sample in sampleGroup.sampleList:
                    sampleNameList.append(sample.name)

        filters = self.etSampleSearch.toPlainText().split(' ')
        sampleNameList = self.filterList(sampleNameList, filters)

        for name in sampleNameList:
            QListWidgetItem(name, self.lvSampleList)

    def refreshSampleGroupList(self):
        self.lvSampleGroupList.clear()
        for sampleGroup in self.facial.samplerManager.sampleGroupList:
            QListWidgetItem(sampleGroup.name, self.lvSampleGroupList)

    def refreshPoseList(self):
        self.lvPoseList.clear()
        if self.cbPoseFilterBySample.isChecked() and self.lvSampleList.currentItem():
            sampleName = self.lvSampleList.currentItem().text()
            sample = self.facial.samplerManager.getSampleByName(sampleName)
            poseList = sample.linkedPoseList
        else:
            poseList = self.facial.poseManager.allPoseList

        if len(poseList) > 0:
            poseNameList = []
            for pose in poseList:
                poseNameList.append(pose.name)

            filters = self.etPoseSearch.toPlainText().split(' ')
            poseNameList = self.filterList(poseNameList, filters)
            poseNameList.sort()

            for p in poseNameList:
                QListWidgetItem(p, self.lvPoseList)

    def filterList(self, sourceList, filters):
        sourceListFiltered = []
        for src in sourceList:
            if filters != [u'']:
                for f in filters:
                    if len(f.strip()) == 0:
                        continue
                    p = re.compile('.*' + f.lower().strip() + '.*')
                    if p.match(src.lower()):
                        sourceListFiltered.append(src)
            else:
                sourceListFiltered.append(src)

        sourceListFiltered = list(set(sourceListFiltered))

        return sourceListFiltered

    def refreshPoseJointList(self):
        self.lvPoseJointList.clear()

        poseName = self.lvPoseList.currentItem().text()
        pose = self.facial.poseManager.getPoseByName(poseName)

        for jnt in pose.jointList:
            QListWidgetItem(jnt.name, self.lvPoseJointList)


    def gotoInitialPose(self):
        self.cbOverrideMode.setChecked(False)
        # self.facial.jointManager.togglePoseOverrding(False)

    def savePose(self):
        self.facial.savePose()

def main():
    windowUI = WidgetHierarchyTree()
    windowUI.show()
    windowUI.setMaximumWidth(1000)
    windowUI.setMinimumWidth(1000)
    windowUI.setMinimumHeight(600)


    return windowUI


if __name__ == '__main__':
    main()
