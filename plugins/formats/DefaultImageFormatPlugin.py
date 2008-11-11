# -*- coding:utf-8 -*-
# pyview
# Default image format plugin
"""
Default/base image format plugin
"""

import sys, os
import Image
from ImageFormatPlugin import ImageFormatPlugin

class DefaultImageFormatPlugin(ImageFormatPlugin):

	# Supported formats, see supportedFormats() function
	formats = [
			("Windows Bitmap", "*.bmp",      True,  True,  None),
			("Windows Cursor", "*.cur",      True,  False, None),
			("DCX", "*.dcx",                 True,  False, None),
			("Epson PostScropt", "*.eps",    False, True,  None),
			("Autodesc Flic", "*.fli *.flc", True,  False, None),
			("FlashPix", "*.fpx",            True,  False, None),
			("GIMP Brush", "*.gbr",          True,  False, None),
			("GD Image", "*.gd",             True,  False, None), # http://www.pythonware.com/library/pil/handbook/format-gd.htm
			("GIF", "*.gif",                 True,  True,  None),
			("Windows Icon", "*.ico",        True,  False, None),
			("IM (IFUNC)", "*.im",           True,  True,  None),
			("Image Tools Image", "*.imt",   True,  False, None),
			("IPTC/NAA Newsphoto", "*.naa",  True,  False, None),
			("JPEG", "*.jpg *.jpeg *.jpe *.jfif", True, True, None),
			#("McIDAS", None, True, False, None),
			("Microsoft Image Composer (MIC)", "*.mic", True, False, None),
			("Windows MSP", "*.msp",         True,  True,  None),
			("PALM pixmap", "*.palm",        False, True,  None),
			("PhotoCD", "*.pcd",             True,  False, None),
			("PCX", "*.pcx",                 True,  True,  None),
			("PDF (Acrobat)", "*.pdf",       False, True,  None),
			("PNG", "*.png",                 True,  True,  None),
			("PIXAR raster image", "*.pxr",  True,  False, None),
			("PPM/PGM/PBM", "*.ppm *.pgm *.ppm", True, True, None),
			("Photoshop PSD", "*.psd",       True,  False, None),
			("SGI", "*.sgi",                 True,  False, None),
			#("SPIDER", None, None),
			("Targa", "*.tga",               True,  False, None),
			("TIFF", "*.tif *.tiff",         True,  True,  None),
			("Quake2 Texture", "*.wal",      True,  False, None),
			("X Bitmap", "*.xbm",            True,  True,  None),
			("X Pixmap", "*.xpm",            True,  False, None),
			("XV Thumbnail", "*.xv",         True,  True,  None),
			]

	def __init__(self):
		ImageFormatPlugin.__init__(self)
		return
	
	# Gets a list of supported formats
	def supportedFormats(self):
		"""
		Returns a list of supported image formats.
		
		The return value is a list of tuples:
		[
			(Name, Extensions, Read, Write, Mimetype),
			...
		]
		"""
		return self.formats
	
	# Loads an image from the given path
	def loadImage(self, filepath):
		"""
		Loads the image at the given path and returns a PIL image object.
		"""
		try:
			image = Image.open(str(filepath))
			print(filepath + ": "+ image.format + " %dx%d" % image.size +" "+ image.mode)
			return image
		except IOError:
			return None
		
	# Saves the given image to the given file
	def saveImage(self, image, filepath, format=None):
		"""
		Saves the given image (PIL image object) to the given path.
		"""
		try:
			if format:
				image.save(str(filepath), format)
			else:
				image.save(str(filepath))
			return True
		except IOError:
			return False



if __name__ == "__main__":
	from ImageFormatPlugin import getPlugins
	print "--> " + str(getPlugins())
