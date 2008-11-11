# -*- coding:utf-8 -*-
# pyview
# Default image format plugin
"""
Default/base image format plugin
"""

import sys, os
import Image

class ImageFormatPlugin(object):

	def __init__(self):
		return
		
	# Gets a list of the subclasses
	def getPlugins(self):
		"""
		Returns a list of all classes inherting from ImageFormatPlugin
		"""
		return ImageFormatPlugin.__subclasses__()

	# Returns the PIL version number	
	def getPILVersion(self):
		"""
		Returns the PIL version number
		"""
		return Image.VERSION
		
	################### OVERRIDE THE FOLLOWING ################################
	
	# Gets a list of supported formats
	def supportedFormats(self):
		"""
		Returns a list of supported image formats.

		The return value is a list of tuples:
		[
			(Name, Extensions, CanRead, CanWrite, Mimetype),
			...
		]
		"""
		return None

	# Loads an image from the given path
	def loadImage(self, filepath):
		"""
		Loads the image at the given path and returns a PIL image object.
		"""
		return None
		
	# Saves the given image to the given file
	def saveImage(self, image, filepath, format=None):
		"""
		Saves the given image (PIL image object) to the given path.
		"""
		return False

