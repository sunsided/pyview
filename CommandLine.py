# -*- coding:utf-8 -*-
# pyview
# Command Line Argument Parser
"""
pyview Command Line Argument Parser
"""

import sys, os
from PyQt4.QtCore import QCoreApplication
from optparse import OptionParser

class CommandLine():

	# Initializes the command line argument parser		
	def __init__(self, version):
		# Initialize and parse options
		self.cmdLineOptions = None
		self.cmdLineArgs = None
		self.__buildParser(version)
		return
	
	# Translates a string
	def tr(self, string):
		"""Helper function to translate a string for the Command Line Options help display"""
		translated = QCoreApplication.translate("Command Line Options", string)
		return str(translated)
		
	# Build the parser
	def __buildParser(self, version):
		"""Creates the command line options parser"""
		# http://docs.python.org/lib/module-optparse.html
		# http://optik.sourceforge.net/doc/1.5/tutorial.html
		# http://optik.sourceforge.net/doc/1.5/reference.html

		# Translation scope
		scope = "Command Line Arguments"

		# Some strings
		versionString = version.APPNAME + " v" + version.APPVERSION
		usageString = "%prog " + self.tr("[Options] [Filename]")
		descString = self.tr(version.DESCRIPTION)
		
		# Parser erstellen
		cmdOptParser = OptionParser(usage = usageString, 
									version = versionString,
									description = descString)
		
		# Define the options
		cmdOptParser.add_option("-d", "--directory", dest="initialDirectory", default=None,
								help=self.tr("start in DIRECTORY. If an image is loaded through the command line, the directory of the image is used instead"), 
								metavar="DIRECTORY")
		
		# Parse and store in self.cmdLineOptions
		(self.cmdLineOptions, self.cmdLineArgs)	= cmdOptParser.parse_args()	
		
		# Check for file arguments
		self.cmdLineOptions.initialFile = None
		count = len(self.cmdLineArgs)
		if count >= 1:
			filename = self.cmdLineArgs[0]
			if os.path.isfile(filename):
				print("Starting with file argument: " + filename)
				self.cmdLineOptions.initialFile = os.path.abspath(filename)
			else:
				cmdOptParser.error(
					self.tr("Filename argument was invalid. Not a file:") + 
					" " + filename
				)
				
		# Check directory argument
		if self.cmdLineOptions.initialDirectory != None:
			if not os.path.isdir(self.cmdLineOptions.initialDirectory):
				cmdOptParser.error(
					self.tr("Invalid startup directory given. Not a directory:") + 
					" " + self.cmdLineOptions.initialDirectory
				)
		
		return
	
	# Returns the parsed options class
	def getOptions(self):
		"""
		Returns the command line options class.
		"""
		return self.cmdLineOptions
	
	# Return the command line arguments
	def getArgumentVector(self):
		"""
		Gets the command line argument vector after parsing has been done.
		This is usually a list of file arguments.
		"""
		return self.cmdLineArgs

