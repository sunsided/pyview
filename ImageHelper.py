# -*- coding:utf-8 -*-
# pyview
# Picture operation helper
"""
Helper functions for image handling
"""

import sys
import Image
from PyQt4 import QtGui, QtCore

class ImageHelper():
		
	# Loads an image from a file and returns a
	# PIL Image
	def loadImageFromFile(self, filepath):
		"""Loads an image from a file and returns a PIL image"""
		image = Image.open(str(filepath))
		return image
		
	# Converts a PIL image to a Qt image
	# Kudos to: http://mail.python.org/pipermail/image-sig/2004-September/002908.html
	def convertPILImageToQtImage(self, pilImage, encoder="jpeg", mode="RGB"):
		"""
		Converts a PIL image to a Qt image.
		Optional parameters "encoder" and "mode" determine which method will
		be used to convert the images.
		The function either returns a QImage or None, in case of an error
		"""
		
		# Convert the PIL image to a string
		PILstring = pilImage.convert(mode).tostring(encoder, mode)
		if( not PILstring ): return None
		
		# Convert the string to a QImage
		image = QtGui.QImage()
		image.loadFromData(QtCore.QByteArray(PILstring))
		
		# Return the image
		return image

