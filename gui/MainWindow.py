#!/env/python
# -*- coding:utf-8 -*-

# pyview
# Main Window GUI
"""
Main Window GUI for the pyview image viewer
"""

import sys
from PyQt4 import QtGui, QtCore
from ui.Ui_MainWindow import Ui_MainWindow

# Main Window class

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
	"""
	This class represents the main window of the image viewer
	"""

	# Initializes the class
	def __init__(self):
		# Initialize UI
		print("Initializing main window")
		QtGui.QMainWindow.__init__(self)
		self.setupUi(self)

		# Set options
		self.setAskOnExit(False)
		return

	# Options
	def setAskOnExit(self, enabled):
		"""
		If enabled, the user will be asked if the window
		is about to close. If disabled, the window will close
		without further intervention
		"""
		self.AskOnExit = enabled
		return

	# Center the window on the screen
	def centerWindow(self):
		"""Centers the window on the screen"""
		print("Centering window on screen")
		# Get desktop size
		desktop = QtGui.QApplication.desktop()
		screenWidth = desktop.width()
		screenHeight = desktop.height()
		# Get window size
		windowSize = self.size()
		width = windowSize.width()
		height = windowSize.height()
		# Calculate new position
		x = (screenWidth-width) / 2
		y = (screenHeight-height) / 2
		# Set position
		self.move(x, y)
		return

	# Quit button was clicked
	@QtCore.pyqtSignature("")
	def on_action_Quit_triggered(self):
		print("Closing main window.")
		self.close()
		return

	# Overrides the default behavior for the window close event
	def closeEvent(self, event):
		# Check if asking is enabled
		if not self.AskOnExit:
			return

		# Ask
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
	window.centerWindow()
	window.show()
	sys.exit(app.exec_())
