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
	"""Helper class"""

	# Creates an image
	def createImage(self):
		"""Creates a new image object"""
		return ImageObject()

class ImageObject():

	def __init__(self):
		self.image = None
		return

	# Loads an image from a file
	def loadImageFromFile(self, filepath):
		"""Loads an image from a file and returns a PIL image"""
		self.image = Image.open(str(filepath))
		return

	# Converts a PIL image to a Qt image
	# Kudos to: http://mail.python.org/pipermail/image-sig/2004-September/002908.html
	def convertToQtImage(self, encoder="jpeg", mode="RGB"):
		"""
		Converts a PIL image to a Qt image.
		Optional parameters "encoder" and "mode" determine which method will
		be used to convert the images.
		The function either returns a QImage or None, in case of an error
		"""

		# Convert the PIL image to a string
		PILstring = self.image.convert(mode).tostring(encoder, mode)
		if( not PILstring ): return None

		# Convert the string to a QImage
		qimage = QtGui.QImage()
		qimage.loadFromData(QtCore.QByteArray(PILstring))

		# Return the image
		return qimage

