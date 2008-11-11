#!/usr/bin/env python
# -*- coding:utf-8 -*-

# pyview Image Viewer
# Main entry point

import sys
from PyQt4 import QtGui, QtCore
from gui.MainWindow import MainWindow
from CommandLine import CommandLine
from FolderHelper import FolderHelper
from ImageHelper import ImageHelper

# Translates a string
def tr(string):
	"""
	This helper function is used to translates strings in the pyview scope.
	"""
	translated = QtCore.QCoreApplication.translate("pyview", string)
	return str(translated)

# Version
class Version:
	APPNAME     = tr("pyview Image Viewer")
	APPVERSION  = "0.1 development"
	DESCRIPTION = tr("A simple image viewer that wants to be like IrfanView")

# Main Entry point
def main():

	# Build command line parser
	cmdLine = CommandLine(Version())
	options = cmdLine.getOptions()

	# Get initial directory
	folderHelper = FolderHelper(options)
	folderHelper.setLastOpenedFile(options.initialFile)
	startDir = folderHelper.getFileDialogInitialDirectory()

	# Create image helper class
	imageHelper = ImageHelper()

	# Get and configure App object
	app = QtGui.QApplication(sys.argv)
	#QtGui.QApplication.setStyle(QtGui.QStyleFactory.create("Cleanlooks"))

	# Create and set window
	window = MainWindow(imageHelper, folderHelper)
	window.setFileDialogDirectory(startDir)
	window.centerWindow()
	window.show()

	# Load initial file
	if options.initialFile:
		window.openFile(options.initialFile)

	# Start the application
	return app.exec_()

# System entry point

if __name__ == "__main__":

	# Spank me
	sys.exit(main())

