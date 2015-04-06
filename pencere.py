# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'testchroot.ui'
#
# Created: Mon Apr  6 01:38:01 2015
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Pencere(object):
    def setupUi(self, Pencere):
        Pencere.setObjectName(_fromUtf8("Pencere"))
        Pencere.resize(729, 504)
        self.centralwidget = QtGui.QWidget(Pencere)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.containerList = QtGui.QComboBox(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.containerList.sizePolicy().hasHeightForWidth())
        self.containerList.setSizePolicy(sizePolicy)
        self.containerList.setMinimumSize(QtCore.QSize(150, 0))
        self.containerList.setObjectName(_fromUtf8("containerList"))
        self.horizontalLayout_3.addWidget(self.containerList)
        self.cmdLine = QtGui.QLineEdit(self.centralwidget)
        self.cmdLine.setMaximumSize(QtCore.QSize(633, 16777215))
        self.cmdLine.setObjectName(_fromUtf8("cmdLine"))
        self.horizontalLayout_3.addWidget(self.cmdLine)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.containerInfo = QtGui.QPlainTextEdit(self.centralwidget)
        self.containerInfo.setObjectName(_fromUtf8("containerInfo"))
        self.horizontalLayout_2.addWidget(self.containerInfo)
        self.terminalOutput = QtGui.QPlainTextEdit(self.centralwidget)
        self.terminalOutput.setObjectName(_fromUtf8("terminalOutput"))
        self.horizontalLayout_2.addWidget(self.terminalOutput)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        Pencere.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(Pencere)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        Pencere.setStatusBar(self.statusbar)

        self.retranslateUi(Pencere)
        QtCore.QObject.connect(self.cmdLine, QtCore.SIGNAL(_fromUtf8("returnPressed()")), Pencere.command)
        QtCore.QObject.connect(self.containerList, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(QString)")), Pencere.setInfo)
        QtCore.QMetaObject.connectSlotsByName(Pencere)

    def retranslateUi(self, Pencere):
        Pencere.setWindowTitle(_translate("Pencere", "MainWindow", None))

