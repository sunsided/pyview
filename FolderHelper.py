# -*- coding:utf-8 -*-
# pyview
# Folders helper
"""
Helper functions for file/folder handling
"""

import sys, os

class FolderHelper():

	def __init__(self, commandLineArgs):
		"""
		Initializes the folder helper and sets the command line arguments
		class as created by the CommandLine helper class
		"""
		self.cmdLineOptions = commandLineArgs
		self.lastOpenedFile = None
		return

	# Gets the user's home directory
	def getUserHomeDir(self):
		"""Gets the user's home directory"""
		# TODO: Make this Windows safe
		return str(os.environ.get('HOME'))

	# Gets the user's "pictures" folder
	def getUserPicturesDir(self):
		"""Gets the user's Pictures folder"""
		# http://win32com.goermezer.de/content/view/191/188/
		# http://www.blueskyonmars.com/2005/08/05/finding-a-users-my-documents-folder-on-windows/
		# TODO: Extend this for Windows, MacOS ...
		user_home_dir = self.getUserHomeDir()
		conf_home = user_home_dir + "/.config"
		if os.environ.has_key("XDG_CONFIG_HOME"):
			conf_home = os.environ["XDG_CONFIG_HOME"]
	
		userdirs_path = str(conf_home + "/user-dirs.dirs")
		if os.path.exists(userdirs_path) and os.path.isfile(userdirs_path):
			userdirs_file = open(userdirs_path, "r")
			lines = userdirs_file.readlines()
			userdirs_file.close()
			for line in lines:
				if line.startswith("XDG_PICTURES_DIR"):
					pictures_dir = line.split("=", 1)[1].strip()
					if( pictures_dir.startswith("\"")):
						pictures_dir = pictures_dir[1:-1]
					pictures_dir = pictures_dir.replace("$HOME", user_home_dir)
					pictures_dir = pictures_dir.replace("~/", user_home_dir + "/")
					return str(pictures_dir)
		return None

	# Sets the last opened file
	def setLastOpenedFile(self, filepath):
		"""Sets the path of the last opened file"""
		filepath = str(filepath)
		if os.path.isfile(filepath):
			self.lastOpenedFile = filepath
		return
		
	# Gets the application's startup directory
	def getStartDir(self):
		"""Gets the directory from which pyview was started"""
		startDir = str(self.cmdLineOptions.initialDirectory)
		if( os.path.isdir(startDir) ):
			startDir = os.path.normpath(startDir)
		else:
			startDir = os.path.dirname(startDir)
		return str(startDir)

	# Gets the start directory for the file|open dialog
	def getFileDialogInitialDirectory(self):
		"""Gets the initial directory for a file|open dialog"""
		# Startverzeichnis holen
		startDir = None
		if self.lastOpenedFile != None:
			startDir = os.path.dirname(str(self.lastOpenedFile))
		if not startDir:
			startDir = self.getStartDir()
		if not startDir:
			startDir = self.getUserPicturesDir()
		if not startDir:
			startDir = self.getUserHomeDir()
		return startDir

