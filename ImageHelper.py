# -*- coding:utf-8 -*-
# pyview
# Picture operation helper
"""
Helper functions for image handling
"""

import sys
import Image

class ImageHelper():
		
	# Loads an image from a file and returns a
	# PIL Image
	def loadImageFromFile(filepath):
		"""Loads an image from a file and returns a PIL image"""
		image = Image.open(filepath)
		return image
		
	# Converts a PIL image to a Qt image
	# Kudos to: http://mail.python.org/pipermail/image-sig/2004-September/002908.html
	def convertPILImageToQtImage(pilImage, encoder="jpeg", mode="RGB"):
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
		imageSize = QSize( pilImage.size[0], pilImage.size[1] )
		image = QImage()
		image.loadFromData(QByteArray(PILstring))
		
		# Return the image
		return image

