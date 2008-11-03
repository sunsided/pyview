#!/env/python
# -*- coding:utf-8 -*-

# pyview
# Qt Picture Frame Widget
"""
Qt Picture Frame widget
"""

import sys
from PyQt4 import QtGui, QtCore

# Picture Frame class

class PictureFrame(QtGui.QFrame):
	"""
	This class represents a picture frame
	"""

	# Initializes the class
	def __init__(self, parent):
		# Initialize
		print("Initializing main window")
		QtGui.QFrame.__init__(self, parent)
		
		# Create scrollbars
		self.verticalScrollBar = QtGui.QScrollBar(self)
		self.verticalScrollBar.setOrientation(QtCore.Qt.Vertical)
		self.enableVerticalScrollBar(True)
		self.horizontalScrollBar = QtGui.QScrollBar(self)
		self.horizontalScrollBar.setOrientation(QtCore.Qt.Horizontal)
		self.enableHorizontalScrollBar(True)
		self.updateScrollBars()
		
		return

	# Refreshes the scrollbars
	def updateScrollBars(self):
		"""Updates the scrollbar sizes and positions"""
		
		# The right scrollbar
		left = self.width() - self.verticalScrollBar.width()
		top = 0
		width = self.verticalScrollBar.width()	
		height = self.height()
		if self.horizontalScrollBarEnabled:
			height -= self.horizontalScrollBar.height()
		self.verticalScrollBar.setGeometry( left, top, width, height )
		
		# The bottom scrollbar
		left = 0
		top = self.height() - self.horizontalScrollBar.height()
		width = self.width()
		if self.verticalScrollBarEnabled:
			width -=self.verticalScrollBar.width()
		height = self.horizontalScrollBar.height()
		self.horizontalScrollBar.setGeometry( left, top, width, height )
		return

	# Enables the horizontal scroll bar
	def enableHorizontalScrollBar(self, enabled):
		"""
		Enables or disables the horizontal scroll bar
		"""
		self.horizontalScrollBarEnabled = enabled
		self.horizontalScrollBar.setVisible(enabled)
		return
		
	# Enables the vertical scroll bar
	def enableVerticalScrollBar(self, enabled):
		"""
		Enables or disables the vertical scroll bar
		"""
		self.verticalScrollBarEnabled = enabled
		self.verticalScrollBar.setVisible(enabled)
		return

	# Called when the frame got resized
	def resizeEvent(self, event):
		print("PictureFrame resized")
		self.updateScrollBars()
		return

	# Quit button was clicked
	def paintEvent(self, event):
		print("PictureFrame paint event triggered.")
		# Obtain painter
		painter = QtGui.QPainter(self)

		# TODO: The painting region depends from the fact whether the scollbars are enabled or not

		# Obtain brush and fill frame
		color1 = QtGui.QColor("#FF0000")
		color2 = QtGui.QColor("#FF00FF")
		gradient = QtGui.QLinearGradient(
			QtCore.QPointF(self.x(), self.y()),
			QtCore.QPointF(self.width(), self.height())
			)
		gradient.setColorAt(0, color1)
		gradient.setColorAt(1, color2)
		brush = QtGui.QBrush(gradient)
		painter.fillRect(self.rect(), brush)
		return

	# Paints the widget
	def forceRepaint(self):
		"""Forces a repaint of the PictureFrame"""
		# Force repaint
		self.repaint(self.rect())
		return

