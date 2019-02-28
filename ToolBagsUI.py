import sys
from PySide2.QtWidgets import *
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
import os
rootDic = 'E:\Pojects\Eve\Rigging\RiggingTool'
sys.path.append(rootDic)
import vertexColor
reload(vertexColor)
import mirrorSelectedPos
reload(mirrorSelectedPos)
# import rootDirectory

pNetrualPose = "NeturalPoseBackupShape"

class ToolBag(MayaQWidgetBaseMixin, QWidget):
# widget declaration
    qBtnSaveVC = 0
    qBtnLoadVC = 0
    qBtnComposeModel = 0
    qComboVCList = 0
    qLayoutSaveVC = 0
    qGrpLoadVC = 0
    qGrpVC = 0
    qLayoutVC = 0
    qGrpMirror = 0
    qLayoutMirror = 0
    qBtnMirror = 0
    qLayoutMain = 0
# widget declaration end

    def __init__(self, *args, **kwargs):
        super(ToolBag, self).__init__(*args, **kwargs)
        self.createUI()
        self.connectFunction()

    def createUI(self):
        self.qLayoutMain = QBoxLayout(QBoxLayout.TopToBottom)

        self.qGrpVC = QGroupBox('Vertex Color Functions:')
        self.qLayoutVC = QVBoxLayout()
        self.qBtnSaveVC = QPushButton("Save Vertex Color")
        self.qLayoutVC.addWidget(self.qBtnSaveVC)
        self.qGrpLoadVC = QGroupBox('Load Vertex Color to Neutral Pose')
        self.qLayoutSaveVC = QVBoxLayout()
        self.qBtnLoadVC = QPushButton("Load Vertex Color")
        self.qComboVCList = QComboBox()
        self.qLayoutSaveVC.addWidget(self.qBtnLoadVC)
        self.qLayoutSaveVC.addWidget(self.qComboVCList)
        self.qGrpLoadVC.setLayout(self.qLayoutSaveVC)
        self.qLayoutVC.addWidget(self.qGrpLoadVC)
        self.qBtnComposeModel = QPushButton("Compose New Pose from selected")
        self.qLayoutVC.addWidget(self.qBtnComposeModel)
        self.qGrpVC.setLayout(self.qLayoutVC)
        self.qLayoutMain.addWidget(self.qGrpVC)

        self.qGrpMirror = QGroupBox('Mirror Function:')
        self.qLayoutMirror = QVBoxLayout()
        self.qBtnMirror = QPushButton("Mirror selected Pose")
        self.qLayoutMirror.addWidget(self.qBtnMirror)
        self.qGrpMirror.setLayout(self.qLayoutMirror)
        self.qLayoutMain.addWidget(self.qGrpMirror)

        self.qLayoutMain.addStretch()
        self.setLayout(self.qLayoutMain)
        self.setWindowTitle("Tool Bags")
        self.initWidgets()

    def connectFunction(self):
        self.qBtnSaveVC.clicked.connect(self.onClickSaveVertexColor)
        self.qBtnLoadVC.clicked.connect(self.onClickLoadVertexColor)
        self.qBtnComposeModel.clicked.connect(self.onClickCompose)
        self.qBtnMirror.clicked.connect(self.onClickBtnMirror)

    def initWidgets(self):
        self.refreshColorPlanComboBox(None)

# ********************* event handler ***********************

    def onClickSaveVertexColor(self):
        gui = QWidget()
        text, ok = QInputDialog.getText(gui, "Save color plan", "Input the name of the Vertex Color plan:")
        if ok and text:
            vertexColor.saveVColor(text, pNetrualPose, rootDic)
            self.refreshColorPlanComboBox(text)

    def onClickLoadVertexColor(self):
        poseName = self.qComboVCList.currentText()
        vertexColor.loadVColor(poseName, pNetrualPose, rootDic)
        self.refreshColorPlanComboBox(poseName)

    def onClickCompose(self):
        vertexColor.compose()

    def onClickBtnMirror(self):
        mirrorSelectedPos.mirrorSelected(rootDic)

    def refreshColorPlanComboBox(self, txt):
        self.qComboVCList.clear()
        for file in os.listdir(rootDic + "/data/vcol"):
            if file.endswith(".vcol"):
                self.qComboVCList.addItem(file.split('.')[0])
        if txt:
            self.qComboVCList.setCurrentText(txt)

# ********************* main function below ***********************

def main():
    windowUI = ToolBag()
    windowUI.show()
    windowUI.setMinimumWidth(250)
    windowUI.setMinimumHeight(250)
    return windowUI


if __name__ == '__main__':
    main()
