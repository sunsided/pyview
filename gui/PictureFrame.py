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
		QtGui.QFrame.__init__(self, parent)	
		self.owner = parent
		return

	# Control needs to paint itself
	def paintEvent(self, event):
		
		paint = QtGui.QPainter()
		paint.begin(self)
		
		# Dispatch to owner
		self.owner.paintHook(self, paint)
		
		paint.end()
		return

