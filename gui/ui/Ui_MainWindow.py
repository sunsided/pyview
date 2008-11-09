# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created: Sat Nov  8 16:37:23 2008
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(500, 300)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 500, 22))
        self.menubar.setObjectName("menubar")
        self.menu_File = QtGui.QMenu(self.menubar)
        self.menu_File.setObjectName("menu_File")
        self.menu_Debug = QtGui.QMenu(self.menubar)
        self.menu_Debug.setObjectName("menu_Debug")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionFileQuit = QtGui.QAction(MainWindow)
        self.actionFileQuit.setShortcutContext(QtCore.Qt.ApplicationShortcut)
        self.actionFileQuit.setObjectName("actionFileQuit")
        self.actionDebugRepaint = QtGui.QAction(MainWindow)
        self.actionDebugRepaint.setObjectName("actionDebugRepaint")
        self.actionFileOpen = QtGui.QAction(MainWindow)
        self.actionFileOpen.setObjectName("actionFileOpen")
        self.actionDebugSwitchScrollbars = QtGui.QAction(MainWindow)
        self.actionDebugSwitchScrollbars.setObjectName("actionDebugSwitchScrollbars")
        self.menu_File.addAction(self.actionFileOpen)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.actionFileQuit)
        self.menu_Debug.addAction(self.actionDebugRepaint)
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menu_Debug.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Image Viewer", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_File.setTitle(QtGui.QApplication.translate("MainWindow", "&File", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_Debug.setTitle(QtGui.QApplication.translate("MainWindow", "&Debug", None, QtGui.QApplication.UnicodeUTF8))
        self.actionFileQuit.setText(QtGui.QApplication.translate("MainWindow", "&Quit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionFileQuit.setShortcut(QtGui.QApplication.translate("MainWindow", "Esc", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDebugRepaint.setText(QtGui.QApplication.translate("MainWindow", "Force &repaint", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDebugRepaint.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+D, R", None, QtGui.QApplication.UnicodeUTF8))
        self.actionFileOpen.setText(QtGui.QApplication.translate("MainWindow", "Open ...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionFileOpen.setShortcut(QtGui.QApplication.translate("MainWindow", "O", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDebugSwitchScrollbars.setText(QtGui.QApplication.translate("MainWindow", "Switch Scrollbars", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDebugSwitchScrollbars.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+D, S", None, QtGui.QApplication.UnicodeUTF8))

