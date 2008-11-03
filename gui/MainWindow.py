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
from PictureFrame import PictureFrame

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

		# Set background frame
		self.setCentralWidget(self.backgroundFrame)
		self.setImageAreaBackgroundColor("#909090")

		# Set widgets
		self.pictureFrame = PictureFrame()
		#self.gridLayout.addWidget(self.pictureFrame, 0, 0)

		# Set options
		self.setAskOnExit(False)
		return

	# Options

	# Sets the background color
	def setImageAreaBackgroundColor(self, color):
		"""
		Sets the background color of the image area.
		The color is a string with a hex RGB color code,
		i.e. "#FF0000" for red
		"""
		self.backgroundFrame.setAutoFillBackground(True)
		self.backgroundFrame.setBackgroundRole(
				QtGui.QPalette.Window
				)
		self.backgroundFrame.palette().setColor(
				QtGui.QPalette.Background,
				QtGui.QColor(color)
				)		
		return

	# Sets whether a dialog box shall be shown when the
	# window is about to close
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

	# Repaint action was triggered
	@QtCore.pyqtSignature("")
	def on_action_Repaint_triggered(self):
		print("Repaint action triggered")
		self.pictureFrame.repaint(self.pictureFrame.rect())
		return

	# Paints the widget
	def pictureFramePaintEvent(self, event):
		# The event is a QPaintEvent
		print("paint")
		return

# Testing

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	window = MainWindow()
	window.centerWindow()
	window.show()
	sys.exit(app.exec_())
