# -*- coding:utf-8 -*-
# pyview
# Image format helper
#
# Kudos: http://lucumr.pocoo.org/blogarchive/python-plugin-system
#        http://pytute.blogspot.com/2007/04/python-plugin-system.html
"""
Helper functions for image formats
"""

import sys, os

# The list of loaded plugin classes
plugins = None

# The list of plugin instances
__instances = []
#__instanceMap = {}

def getFormatPlugins():
	"""
	Gets the list of format plugin instances
	"""
	return loadImageFormatPlugins()

# Loads the plugins
def loadImageFormatPlugins():
	"""
	Loads all known image format plugins.
	Returns a list of all loaded image format plugin instances.
	"""
	global plugins
	
	# Once we've loaded the plugins, return the cached object
	if plugins:
		return __instances
	
	# Load plugins from the application location
	plugins = addPlugins( "plugins/formats/", plugins )
		
	# TODO Load plugins from the user's homedir
	# This should be cross platform, ideally
	#plugins = addPlugins( "~/.pyview/plugins/formats/", plugins )
	
	# TODO Load plugins from a system wide location
	# This should be cross platform, ideally
	#plugins = addPlugins( "/usr/local/etc/pyview/plugins/formats/", plugins )

	# Instanciate the plugins
	loadInstances()

	print(str(len(__instances)) + " format plugin(s) loaded")
	return __instances

# Instanciate the classesplugins
def loadInstances():
	"""
	Takes the list of known plugin classes and instances each of them.
	Then it returns a list of these instances.
	The list is also set globally.
	"""

	global plugins, __instances
	for plugin in plugins:
		if not plugin in __instances:
			instance = plugin()
			__instances.append(instance)
			#__instanceMap[plugin] = instance
			
	return __instances

def addPlugins(path, fallback = None):
	"""
	Adds a directory to the search path.
	Returns a list of all loaded plugin classes or the value 
	of the "fallback" parameter.
	"""
	
	# Get the path
	pluginpath = os.path.abspath(str(path))
	if not os.path.isdir(pluginpath):
		return fallback
	
	# Scan for files
	pluginfiles = [fname[:-3] for fname in os.listdir(pluginpath) if fname.endswith(".py") and fname != "ImageFormatPlugin.py" and not fname.startswith("__init__")]
	
	# Add path to the search path
	if not pluginpath in sys.path:
		sys.path.append(pluginpath)
	
	# Import the modules	
	imported_modules = [__import__(filename) for filename in pluginfiles]
	if len(imported_modules) == 0:
		return fallback

	# Get the list of imported classes
	plugins = getattr(imported_modules[0], "ImageFormatPlugin").__subclasses__()
	return plugins
	
	
	
if __name__=="__main__":
	loadImageFormatPlugins()

