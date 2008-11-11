#!/env/python
# -*- coding:utf-8 -*-

# pyview
# Qt Picture Frame Widget
"""
Qt Picture Frame widget
"""

import sys
from PyQt4 import QtGui, QtCore, Qt

# Picture Frame class

class PictureFrame(QtGui.QFrame):
	"""
	This class represents a picture frame
	"""

	# Initializes the class
	def __init__(self, parent):
		# Initialize
		QtGui.QFrame.__init__(self)	
		
		# Save owner
		self.owner = parent
		
		# Enable mouse tracking
		self.setMouseTracking(True)
		
		# Disable background
		self.setOpaqueMode(True)
				
		return
	
	def setOpaqueMode(self, enabled):
		"""Enables or disables opaque mode"""
		self.isOpaque = enabled
		self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent, enabled)
		self.setAttribute(QtCore.Qt.WA_NoSystemBackground, enabled)
		return
	
	# Forces a repaint
	def forceRepaint(self):
		"""Forces a repaint"""
		self.repaint(self.rect())
		return

	# Mouse was hovered
	def mouseMoveEvent(self, event):
		self.owner.mouseMoveHook(event)
		return

	# Control was resized
	def resizeEvent(self, event):
		self.owner.resizeHook(self)
		return

	# Control needs to paint itself
	def paintEvent(self, event):
		
		paint = QtGui.QPainter()
		paint.begin(self)
		
		# Dispatch to owner
		self.owner.paintHook(self, paint)
		
		paint.end()
		return

