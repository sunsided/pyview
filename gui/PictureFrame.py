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
		self.horizontalScrollBar = QtGui.QScrollBar(self)
		self.horizontalScrollBar.setOrientation(QtCore.Qt.Horizontal)
		# Set scrollbars
		self.enableVerticalScrollBar(True, False)
		self.enableHorizontalScrollBar(True, False)
		self.updateScrollBars()
		
		return

	# Gives the frame a qimage to display
	def takeImage(self, qimage):
		"""
		Gives the PictureFrame a qimage to display.
		No further processing of the image will be done, except for 
		alignment and scaling (if any)
		"""
		self.image = qimage
		self.forceRepaint()
		return

	# Sets the background color
	def setBackgroundColor(self, color):
		"""Sets the color to be used for the background whenever the image
		is too small to fill the viewport"""
		self.bgColor = QtGui.QColor(color)
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
		
		# Calculate the new viewport size
		self.calculateViewport()
		self.forceRepaint()
		return

	# Enables the horizontal scroll bar
	def enableHorizontalScrollBar(self, enabled, update=True):
		"""
		Enables or disables the horizontal scroll bar
		"""
		self.horizontalScrollBarEnabled = enabled
		self.horizontalScrollBar.setVisible(enabled)
		if update:
			self.updateScrollBars()
		return
		
	# Enables the vertical scroll bar
	def enableVerticalScrollBar(self, enabled, update=True):
		"""
		Enables or disables the vertical scroll bar
		"""
		self.verticalScrollBarEnabled = enabled
		self.verticalScrollBar.setVisible(enabled)
		if update:
			self.updateScrollBars()
		return
		
	# Calculates the viewport size
	def calculateViewport(self):
		"""Calculates the viewport size"""
		# Get new dimensions
		height = self.height()
		if self.horizontalScrollBarEnabled:
			height -= self.horizontalScrollBar.height()
		width = self.width()
		if self.verticalScrollBarEnabled:
			width -= self.verticalScrollBar.width()

		# Set new viewport size
		self.viewport = QtCore.QRect( 0, 0, width, height )
		self.viewportF = QtCore.QRectF( 0, 0, width, height )
		return

	# Called when the frame got resized
	def resizeEvent(self, event):
		self.updateScrollBars()
		self.calculateViewport()
		return

	# Control needs to paint itself
	def paintEvent(self, event):
		# Obtain painter
		painter = QtGui.QPainter(self)

		# Get the painting rectangle
		viewport = self.viewportF
		
		# DEBUG: Obtain brush and fill frame
		color1 = QtGui.QColor("#FF0000")
		color2 = QtGui.QColor("#FF00FF")
		gradient = QtGui.QLinearGradient(
			QtCore.QPointF(self.x(), self.y()),
			QtCore.QPointF(self.width(), self.height())
			)
		gradient.setColorAt(0, color1)
		gradient.setColorAt(1, color2)
		brush = QtGui.QBrush(gradient)
		painter.fillRect(viewport, brush)
		
		# Paint the image
		targetRect = viewport
		sourceRect = QtCore.QRectF(0, 0, self.image.size().width(), self.image.size().height())
		painter.drawImage(targetRect, self.image, sourceRect)
		
		return

	# Paints the widget
	def forceRepaint(self):
		"""Forces a repaint of the PictureFrame"""
		# Force repaint
		self.repaint(self.viewport)
		return

