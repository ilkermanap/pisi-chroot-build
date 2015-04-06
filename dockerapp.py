import sys
from PyQt4 import QtCore, QtGui
from pencere import Ui_Pencere
from dockermodule import *

class MyWin(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Pencere()
        self.ui.setupUi(self)
        self.docker = DockerModule()
        for repos in self.docker.images.keys():
            self.ui.containerList.addItem(repos)

    def setInfo(self):
        selected = str(self.ui.containerList.currentText())
        self.ui.containerInfo.setPlainText(self.docker.images[selected].info())

    def stopAndClear(self):
        print "stopandclear clicked"
        pass

    def command(self):
        s =  str(self.ui.cmdLine.text().toLatin1())
        selected = str(self.ui.containerList.currentText())
        self.ui.terminalOutput.setPlainText(self.docker.images[selected].runCommand(s))

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())

