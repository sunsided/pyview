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
	def __init__(self, imageHelper):
		# Initialize UI
		print("Initializing main window")
		QtGui.QMainWindow.__init__(self)
		self.setupUi(self)
		self.setupKeyboardHooks()

		# Set classes
		self.imageHelper = imageHelper

		# Set picture frame
		self.pictureFrame = PictureFrame(self)
		self.setCentralWidget(self.pictureFrame)
		self.setImageAreaBackgroundColor("#909090")

		# Set options
		self.setAskOnExit(False)
		self.setFileDialogDirectory(None)
		return

	# Keyboard hooks
	
	# Initialize keyboard shortcuts
	def setupKeyboardHooks(self):
		"""Initializes the keyboard shortcuts"""
		print("Initializing keyboard shortcuts")
		
		# Set secondary "quit" shortcut
		shortcut = QtGui.QShortcut(
			QtGui.QKeySequence( self.tr("Ctrl+Q", "File|Quit")), 
			self
			)
		self.connect(shortcut, QtCore.SIGNAL("activated()"), self.on_actionFileQuit_triggered)
		
		# Set secondary "open" shortcut
		shortcut = QtGui.QShortcut(
			QtGui.QKeySequence( self.tr("Ctrl+O", "File|Open")), 
			self
			)
		self.connect(shortcut, QtCore.SIGNAL("activated()"), self.on_actionFileOpen_triggered)
		return

	# Options

	# Sets the background color
	def setImageAreaBackgroundColor(self, color):
		"""
		Sets the background color of the image area.
		The color is a string with a hex RGB color code,
		i.e. "#FF0000" for red
		"""
		self.pictureFrame.setAutoFillBackground(True)
		self.pictureFrame.setBackgroundRole(
				QtGui.QPalette.Window
				)
		self.pictureFrame.setBackgroundColor( color )
		return
		
	# Sets the initial directory for file dialogs
	def setFileDialogDirectory(self, directory):
		"""Sets the initial directory for file dialogs"""
		self.fileDialogDirectory = directory
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

	# Convenience functions

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

	# Scrollbars
	
	# Checks for the right scrollbar
	def isVerticalScrollbarNeeded(self):
		"""
		Determines whether the vertical (right) scrollbar is currently
		needed or not.
		"""
		# TODO: Implement
		return False
	
	# Checks for the bottom scrollbar
	def isHorizontalScrollbarNeeded(self):
		"""
		Determines whether the horizontal (bottom) scrollbar is currently
		needed or not.
		"""
		# TODO: Implement
		return False

	# Menu handling

	# File|Open was selected
	@QtCore.pyqtSignature("")
	def on_actionFileOpen_triggered(self):
		self.openFileWithDialog()
		return

	# File|Close was clicked
	@QtCore.pyqtSignature("")
	def on_actionFileQuit_triggered(self):
		self.close()
		return
		
	# Repaint action was triggered
	@QtCore.pyqtSignature("")
	def on_actionDebugRepaint_triggered(self):
		self.pictureFrame.forceRepaint()
		return

	# File handling
	
	# Shows the file open dialog and eventually opens the file
	def openFileWithDialog(self):
		"""
		Shows the "File Open" dialog and eventually opens the file.
		Returns True if the user clicked "OK" and False otherwise.
		"""
				
		# Define file filters
		# TODO: Extend this list to every supported type
		filters = QtCore.QStringList()
		filters << self.tr("Pictures", "File dialog") + " (*.jpg *.gif *.png *.xpm)"
		filters << self.tr("All files", "File dialog") + " (*)"
		
		# Create the dialog
		dialog = QtGui.QFileDialog(self)
		dialog.setFileMode(QtGui.QFileDialog.ExistingFile)
		dialog.setViewMode(QtGui.QFileDialog.Detail)
		dialog.setFilters(filters)
		if self.fileDialogDirectory != None:
			dialog.setDirectory(self.fileDialogDirectory)
		
		# Show the dialog
		if( dialog.exec_() ):
			# Get the filename
			fileNames = dialog.selectedFiles()
			fileName = fileNames[0]
			# Open the file
			self.openFile(fileName)
			return True
		
		return False
	
	# Notifies the system that the loading of a file has started
	def __onOpenFileStarted(self, filepath):
		"""Notifies the system that the loading of a file has started"""
		# Emit signal
		self.emit(QtCore.SIGNAL("openFileStarted(string)"), filepath)
		return
	
	# Notifies the system that the loading of a file has finished
	def __onOpenFileFinished(self, filepath, successful = True):
		"""Notifies the system that the loading of a file has finished"""
		# Emit signal
		self.emit(QtCore.SIGNAL("openFileFinished(string, bool)"), filepath, successful)
		# Display image
		self.pictureFrame.takeImage(self.qimage)
		return
	
	# Opens the specified file
	def openFile(self, filepath):
		"""Opens the specified file"""
		# Open the file
		self.__openFileSync(filepath)
		return
		
	# Opens a file synchronously
	def __openFileSync(self, filepath):
		"""
		Synchronously opens the file.
		The function will block until the image is loaded.
		"""

		# Notify
		print("Synchronously loading image: " + filepath)
		self.__onOpenFileStarted(filepath)
		
		# Load image using PIL
		pilimage = self.imageHelper.loadImageFromFile(filepath)
		if not pilimage:
			self.__onOpenFileFinished(filepath, False)
			return False
		self.pilimage = pilimage
		
		# Convert image to Qt QImage
		qimage = self.imageHelper.convertPILImageToQtImage(pilimage)
		if not qimage:
			self.__onOpenFileFinished(filepath, False)
			return False
		self.qimage = qimage
		
		# Return
		print("Done loading image")
		self.__onOpenFileFinished(filepath, True)
		return True

	# General event handling

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

	# Handles the resize event
	def resizeEvent(self, event):
		# TODO: Disable picture frame update	
		# TODO: Rescale image and repaint frame, if necessary
		# TODO: Enable picture frame update
		return

# Testing

if __name__ == "__main__":
	# Init app and get style
	app = QtGui.QApplication(sys.argv)
	#QtGui.QApplication.setStyle(QtGui.QStyleFactory.create("Cleanlooks"))
	# Create and set window
	window = MainWindow()
	window.centerWindow()
	window.show()
	# Loop
	sys.exit(app.exec_())
