#!/env/python
# -*- coding:utf-8 -*-

# pyview
# Main Window GUI
"""Main Window GUI for the pyview image viewer"""

import sys
from PyQt4 import QtGui, QtCore
from ui.Ui_MainWindow import Ui_MainWindow

# Main Window class

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):

	# Initializes the class
	def __init__(self):
		# Initialize UI
		print("Initializing main window")
		QtGui.QMainWindow.__init__(self)
		self.setupUi(self)

	# Quit button was clicked
	@QtCore.pyqtSignature("")
	def on_action_Quit_triggered(self):
		print("Closing main window.")
		self.close()
		return

	# Overrides the default behavior for the window close event
	def closeEvent(self, event):
		reply = QtGui.QMessageBox.question(self, 
				self.tr("Closing ..."),
				self.tr("Are you sure you want to quit?"),
				QtGui.QMessageBox.Yes,
				QtGui.QMessageBox.No
				)
		if reply == QtGui.QMessageBox.Yes:
			event.accept()
		else:
			event.ignore()
		return

# Testing

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec_())
