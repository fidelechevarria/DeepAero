# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui/mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# pyuic5 -x gui/mainwindow.ui -o gui/mainwindow.py
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.showMaximized()
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName("menubar")
        self.menuIdentify = QtWidgets.QMenu(self.menubar)
        self.menuIdentify.setObjectName("menuIdentify")
        self.menuSimulate = QtWidgets.QMenu(self.menubar)
        self.menuSimulate.setObjectName("menuSimulate")
        self.menuTrain = QtWidgets.QMenu(self.menubar)
        self.menuTrain.setObjectName("menuTrain")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuIdentify.menuAction())
        self.menubar.addAction(self.menuSimulate.menuAction())
        self.menubar.addAction(self.menuTrain.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuIdentify.setTitle(_translate("MainWindow", "Identify"))
        self.menuSimulate.setTitle(_translate("MainWindow", "Simulate"))
        self.menuTrain.setTitle(_translate("MainWindow", "Train"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

