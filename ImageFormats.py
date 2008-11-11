# -*- coding:utf-8 -*-
# pyview
# Image format helper
#
# Kudos: http://lucumr.pocoo.org/blogarchive/python-plugin-system
"""
Helper functions for image formats
"""

import sys
from plugins.formats.ImageFormatPlugin import ImageFormatPlugin

# Loads the plugins
def loadImageFormatPlugins():
	"""
	Loads all known image format plugins
	"""
	addPluginPath( "plugins/formats/" )
	plugins = ImageFormatPlugin().getPlugins()
	print(plugins)
	
def addPluginPath(path):
	"""
	Adds a directory to the search path.
	"""
	path = str(path)
	if not path in sys.path:
		sys.path.insert(0, path)
	return

	
	
if __name__=="__main__":
	loadImageFormatPlugins()
