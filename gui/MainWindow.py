# -*- coding:utf-8 -*-
# pyview
# Main Window GUI
"""
Main Window GUI for the pyview image viewer
"""

import sys, math
from PyQt4 import QtGui, QtCore
from ui.Ui_MainWindow import Ui_MainWindow
from PictureFrame import PictureFrame
from ImageHelper import ImageHelper

# Main Window class

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
	"""
	This class represents the main window of the image viewer
	"""

	# Initializes the class
	def __init__(self):
		# Initialize UI
		QtGui.QMainWindow.__init__(self)
		
		# Set classes
		self.imageHelper = ImageHelper()
		self.image = None			# The ImageHelper instance
		self.qimage = None			# The Qt image copy
		self.frameRegion = None
		self.imheight = 0
		self.imwidth = 0
		self.sourceRect = QtCore.QRect(0,0,0,0)
		self.targetRect = QtCore.QRect(0,0,0,0)
				
		# Setup UI
		self.setupUi(self)
		self.setupKeyboardHooks()
		
		# Weird hack ...
		# First, a central widget
		# That widget will get a grid layout layout
		# That will hold the painting area, as well as the scrollbars
		
		# 1.) Create the central widget
		central = QtGui.QWidget()
		central.setBackgroundRole(QtGui.QPalette.Dark)
		self.setCentralWidget(central)
		
		# 2.) Add the layout
		layout = QtGui.QGridLayout()
		layout.setMargin(0)			# Set a zero margin so it fills the frame
		layout.setSpacing(0)		# -"- spacing for similar reasons
		central.setLayout(layout)
				
		# 3.) Create the picture frame
		self.pictureFrame = PictureFrame(self)
		self.pictureFrame.setVisible(False)
		
		# 4.) Add the picture frame to the grid
		layout.addWidget(self.pictureFrame, 0, 0)

		# 5.) Create the scrollbars
		self.vscroll = QtGui.QScrollBar(QtCore.Qt.Vertical)
		self.vscroll.setPageStep(200)
		layout.addWidget(self.vscroll, 0, 1)
		self.hscroll = QtGui.QScrollBar(QtCore.Qt.Horizontal)
		self.hscroll.setPageStep(200)
		layout.addWidget(self.hscroll, 1, 0)
		
		# 5.5) Connect the sliders
		self.connect(self.vscroll, QtCore.SIGNAL("valueChanged(int)"), self.scrollBarSlided)
		self.connect(self.hscroll, QtCore.SIGNAL("valueChanged(int)"), self.scrollBarSlided)
		
		# Scrollbars	
		self.enableHorizontalScrollBar(False)
		self.enableVerticalScrollBar(False)

		# Finally, add the PictureFrame to the Scrollarea		
		self.pictureFrame.setVisible(True)
		
		# Refresh
		self.refreshViewport()
		
		# Create statusbar widgets
		self.positionLabel = QtGui.QLabel()
		self.statusBar().addPermanentWidget(self.positionLabel)
		self.colorLabel = QtGui.QLabel()
		self.statusBar().addPermanentWidget(self.colorLabel)

		# Set options
		self.setAskOnExit(False)
		self.setFileDialogDirectory(None)
		self.setImageAreaBackgroundColor("#909090")
		
		return

	# Enables or disables the horizontal scrollbar
	def enableHorizontalScrollBar(self, enabled):
		"""Enables or disables the horizontal scrollbar"""
		self.hscroll.setVisible(enabled)

	# Enables or disables the vertica scrollbar
	def enableVerticalScrollBar(self, enabled):
		"""Enables or disables the vertical scrollbar"""
		self.vscroll.setVisible(enabled)
		
	# Gets the hscroll value
	def getHorizontalScrollBarValue(self):
		"""Gets the value of the horizontal scrollbar"""
		if self.hscroll.isVisible():
			return self.hscroll.value()
		return 0
		
	# Gets the vscroll value
	def getVerticalScrollBarValue(self):
		"""Gets the value of the vertical scrollbar"""
		if self.vscroll.isVisible():
			return self.vscroll.value()
		return 0

	# Keyboard hooks

	# Initialize keyboard shortcuts
	def setupKeyboardHooks(self):
		"""Initializes the keyboard shortcuts"""

		# Set secondary "quit" shortcut
		shortcut = QtGui.QShortcut(
			QtGui.QKeySequence( self.tr("Ctrl+Q", "File|Quit")),
			self
			)
		self.connect(shortcut, QtCore.SIGNAL("activated()"), self.on_actionFileQuit_triggered)
		shortcut = QtGui.QShortcut(
			QtGui.QKeySequence( self.tr("Q", "File|Quit")),
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
		
		self.bgColor = QtGui.QColor(color)
		self.bgbrush = QtGui.QBrush(self.bgColor)
		self.pictureFrame.forceRepaint()
				
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
		self.emit(QtCore.SIGNAL("openFileStarted(char*)"), filepath)
		return

	# Notifies the system that the loading of a file has finished
	def __onOpenFileFinished(self, filepath, successful = True):
		"""Notifies the system that the loading of a file has finished"""
		# Emit signal
		self.emit(QtCore.SIGNAL("openFileFinished(char*, bool)"), str(filepath), successful)
		# Sanity check
		if not successful:
			return
		# Display statistics
		width, height = self.image.getSize()
		self.statusBar().showMessage(str(width) + "x" + str(height))
		# Display image
		self.pictureFrame.forceRepaint()
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
		pilimage = self.imageHelper.createImage()
		pilimage.loadImageFromFile(filepath)
		if not pilimage:
			self.__onOpenFileFinished(filepath, False)
			return False
		self.image = pilimage
		self.imwidth, self.imheight = pilimage.getsize()

		# Convert image to Qt QImage
		if not self.updateQImage():
			self.qimage = None
			self.__onOpenFileFinished(filepath, False)
			return False

		# Region set scrollbars
		self.updateScrollbarSizeFromImage()

		# Return
		print("Done loading image")
		self.__onOpenFileFinished(filepath, True)
		return True

	# Updates the local QImage copy
	def updateQImage(self):
		"""Updates the QImage copy"""
		if not self.image:
			self.qimage = None
			return None
			
		qimage = self.image.convertToQtImage()
		self.qimage = qimage
		
		# Refresh the viewport
		self.refreshViewport()
		
		return qimage

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
		
	# Scrollbar value has changed, so refresh the viewports
	def scrollBarSlided(self, value):
		self.calculateViewport()
		self.pictureFrame.forceRepaint()
		return
		
	def calculateViewport(self):
		"""Calculates the visible area of the image"""
		
		# Get the display frame size
		sourceRect = self.pictureFrame.rect()
		
		# Offset the rectangle
		leftOffset = self.getHorizontalScrollBarValue()
		topOffset = self.getVerticalScrollBarValue()		
		sourceRect.adjust(leftOffset, topOffset, leftOffset, topOffset)
		
		# Adjust the height of the source rect,
		# if necessary
		if sourceRect.width() > self.imwidth:
			sourceRect.setWidth(self.imwidth)
		if sourceRect.height() > self.imheight:
			sourceRect.setHeight(self.imheight)
		
		# Create the target rect
		targetRect = self.pictureFrame.rect()
		if targetRect.width() > self.imwidth:
			targetRect.setWidth(self.imwidth)
		if targetRect.height() > self.imheight:
			targetRect.setHeight(self.imheight)

		# Calculate the clipping regions			
		self.targetRegion = QtGui.QRegion( targetRect )
		
		# Set it
		self.sourceRect = sourceRect
		self.targetRect = targetRect
		return
	
	def updateScrollbarSizeFromImage(self):
		"""
		Sets the max values of the scrollbars according to 
		the image's size
		"""
		if not self.image:
			return
		
		# Calculate the possible sizes
		# If either of these values is lte 0, the scrollbar
		# may be hidden
		height = self.imheight - self.pictureFrame.height()
		width = self.imwidth - self.pictureFrame.width()
		
		# Set height scrollbar
		if height > 0:
			self.vscroll.setVisible(True)
			self.vscroll.setMinimum(0)
			self.vscroll.setMaximum(height)
			self.vscroll.setPageStep(4*self.imheight/5)
		else:
			self.vscroll.setVisible(False)
		
		# Set width scrollbar
		if width > 0:
			self.hscroll.setVisible(True)
			self.hscroll.setMinimum(0)
			self.hscroll.setMaximum(width)
			self.hscroll.setPageStep(4*self.imwidth/5)
		else:
			self.hscroll.setVisible(False)
		
		return
	
	def refreshViewport(self):
		"""Refreshes the viewport"""
		self.frameRegion = QtGui.QRegion( self.pictureFrame.rect() )
	
		self.calculateViewport()
		self.updateScrollbarSizeFromImage()
		self.calculateViewport()
		self.pictureFrame.forceRepaint()
		return
	
	# Resize event
	def resizeEvent(self, event):
		return
	
	def resizeHook(self, frame):
		self.refreshViewport()
		return
	
	# Gets the color
	def getColor(self, x, y):
		"""
		Gets the color at the given coordinates.
		x,y is relative to the source rect.
		The result is a RGB tuple
		"""
		# Sanity check
		if (x >= self.imwidth) or (x < 0):
			return None
		if (y >= self.imheight) or (y < 0):
			return None
		return self.image.getPixel(x, y)
		
	# Gets the color
	def getColorHex(self, x, y):
		"""
		Gets the color at the given coordinates.
		x,y is relative to the source rect.
		The result is a web (hex) color representation.
		"""
		color = self.getColor(x, y)
		if not color:
			return None
		value = "#%02X"%color[0]+"%02X"%color[1]+"%02X"%color[2]
		return value
	
	# Painting hook
	def paintHook(self, frame, painter):
		"""This function will be called from within the picture frame"""

		pictureClipRegion = self.frameRegion.intersected( self.targetRegion )
		backgroundClipRegion = self.frameRegion.xored( self.targetRegion )
		
		# Fill the background	
		if self.qimage:
			painter.setClipRegion( backgroundClipRegion )
		painter.fillRect( frame.rect(), self.bgbrush )
			
		# Draw the image
		if self.qimage:
			painter.setClipRegion( pictureClipRegion )
			painter.drawImage(self.targetRect, self.qimage, self.sourceRect )
			pass
		
		return
		
	def mouseMoveHook(self, event):
		# Get the mouse position
		x = event.x() + self.sourceRect.left()
		y = event.y() + self.sourceRect.top()
		
		# Set the position
		if (x < self.imwidth) and (x > 0) and (y < self.imheight) and (y > 0):
			self.positionLabel.setText( str(x) + "x" + str(y))
			self.positionLabel.setVisible(True)
		else:
			self.positionLabel.setVisible(False)
		
		# Get and set the color
		color = self.getColorHex(x, y)
		if color:
			self.colorLabel.setText(color)
			self.colorLabel.setVisible(True)
		else:
			self.colorLabel.setVisible(False)
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
