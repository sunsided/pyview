#!/usr/bin/env python
# -*- coding:utf-8 -*-

# pyview Image Viewer
# Main entry point

import sys
from PyQt4 import QtGui, QtCore
from gui.MainWindow import MainWindow
from CommandLine import CommandLine
from FolderHelper import FolderHelper
import Version
import ImageFormats

# Translates a string
def tr(string):
	"""
	This helper function is used to translates strings in the pyview scope.
	"""
	translated = QtCore.QCoreApplication.translate("pyview", string)
	return str(translated)

# Version
class LocalizedVersion:
	APPNAME		= Version.APPNAME
	APPTITLE    = tr("Image Viewer")
	APPVERSION  = Version.APPVERSION
	DESCRIPTION = tr(Version.DESCRIPTION)
	
# Main Entry point
def main():
	"""The pyview main entry point"""

	global folderHelper, window

	# Build command line parser
	cmdLine = CommandLine(LocalizedVersion())
	options = cmdLine.getOptions()

	# Load image format plugins
	ImageFormats.loadImageFormatPlugins()

	# Get initial directory
	folderHelper = FolderHelper(options)
	folderHelper.setLastOpenedFile(options.initialFile)
	startDir = folderHelper.getFileDialogInitialDirectory()

	# Get and configure App object
	app = QtGui.QApplication(sys.argv)
	#QtGui.QApplication.setStyle(QtGui.QStyleFactory.create("Cleanlooks"))

	# Create and set window
	window = MainWindow()
	window.setFileDialogDirectory(startDir)
	window.centerWindow()
	
	# Connections
	window.connect(window, QtCore.SIGNAL("openFileFinished(char*, bool)"), onFileLoaded)
	
	# Show the window
	window.show()

	# Load initial file
	if options.initialFile:
		window.openFile(options.initialFile)

	# Start the application
	return app.exec_()
	

# Callback to set the dialog startup path whenever an image is loaded
def onFileLoaded(filepath, success):
	"""
	Is invoked through the event system and sets the
	startup path for file dialogs whenever and image was loaded
	"""
	global folderHelper, window
	
	# Set the last path
	folderHelper.setLastOpenedFile(filepath)
	
	# Get and set the new path
	path = folderHelper.getFileDialogInitialDirectory()
	window.setFileDialogDirectory(path)
	
	return

# System entry point

if __name__ == "__main__":

	# Spank me
	sys.exit(main())

