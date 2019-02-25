from PySide2.QtWidgets import QApplication,QMainWindow,QTabWidget,QWidget, QInputDialog
from PySide2.QtWidgets import QMessageBox,QFileDialog,QErrorMessage
from PySide2 import QtCore, QtGui, QtWidgets
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

class Ui_Dialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(Ui_Dialog, self).__init__(parent)
        self.p = parent
        self.setupUi(self)

    def setupUi(self, Dialog1):
        Dialog1.setObjectName("Dialog1")
        Dialog1.resize(333, 173)

class MainWindow(MayaQWidgetBaseMixin, QWidget) :

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.resize(100,100)
        self.pb = QPushButton('push button!')
        lyRoot = QVBoxLayout()
        lyRoot.addWidget(self.pb)
        self.setLayout(lyRoot)
        self.pb.clicked.connect(self.btnClicked)

    def btnClicked(self):
        # ui = Ui_Dialog(self)
        # ui.show()
        gui = QWidget()
        text, ok = QInputDialog.getText(gui, "ABC", "DDD")
        print(text)
        print(ok)
        gui.show()

if __name__ == "__main__":
    ui = MainWindow()
    ui.show()