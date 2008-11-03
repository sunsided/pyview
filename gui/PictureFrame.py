#!/env/python
# -*- coding:utf-8 -*-

# pyview
# Qt Picture Frame Widget
"""
Qt Picture Frame widget
"""

import sys
from PyQt4 import QtGui, QtCore

# Main Window class

class PictureFrame(QtGui.QFrame):
	"""
	This class represents a picture frame
	"""

	# Initializes the class
	def __init__(self):
		# Initialize
		print("Initializing main window")
		QtGui.QFrame.__init__(self)
		return

	# Quit button was clicked
	def paintEvent(self, event):
		print("PictureFrame paint event triggered.")
		# Obtain painter
		painter = QtGui.QPainter(self)

		# Obtain brush and fill frame
		color = QtGui.QColor("#FF0000")
		brush = QtGui.QBrush(color)
		painter.fillRect(self.rect(), brush)
		return

	# Paints the widget
	def forceRepaint(self):
		"""Forces a repaint of the PictureFrame"""
		# Force repaint
		self.repaint(self.rect())
		return

