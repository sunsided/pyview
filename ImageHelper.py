# -*- coding:utf-8 -*-
# pyview
# Picture operation helper
"""
Helper functions for image handling
"""

import sys
from PIL import Image, ImagePalette
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

	def pilimage(self):
		"""Returns the image representation"""
		return self.image
		
	def getsize(self):
		"""
		Returns the dimensions of the image as a tuple {width, height}
		"""
		return self.image.size

	def getPixel(self, x, y):
		"""Gets the pixel at x,y as a 3-tuple"""
		
		# TODO: convert indexed colors to RGB
		value = self.image.getpixel((x, y))
		value = self.convertColorToRGB(value)
		
		return value

	# Converts a color to RGB
	def convertColorToRGB(self, color):
		"""Converts a color to RGB"""
		
		# Get the image mode
		mode = self.image.mode

		# If the color is in RGBA mode, skip the alpha
		if mode == "RGBA":
			return color[0:3]
			
		# If the color is RGB, return it
		if mode == "RGB":
			return color

		# Paletted
		if mode == "P":
			value = self.lut[color]
			return value

		# Grayscale
		if mode == "L":
			return color,color,color

		# Bitmaps
		if mode == "1":
			if color==1:
				return 255,255,255
			else:
				return 0,0,0
		
		# Return something
		return None

	# Loads an image from a file
	def loadImageFromFile(self, filepath):
		"""Loads an image from a file and returns a PIL image"""
		image = Image.open(str(filepath))	
		
		# If it is a pallete image, loat the LUT
		if image.mode == "P":
			lut = image.resize((256, 1))
			lut.putdata(range(256))
			lut = lut.convert("RGB").getdata() 
			self.lut = lut
		else:
			self.lut = None
		
		# Set the image and return
		self.image = image
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
		
	# Gets the image's dimensions
	def getSize(self):
		"""Gets the dimensions of the loaded image"""
		return self.image.size
