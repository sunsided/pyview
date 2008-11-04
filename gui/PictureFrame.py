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
		print("Initializing main window")
		QtGui.QFrame.__init__(self, parent)
		
		# Set variables
		self.image = None
				
		# Create scrollbars
		self.verticalScrollBar = QtGui.QScrollBar(self)
		self.verticalScrollBar.setOrientation(QtCore.Qt.Vertical)
		self.horizontalScrollBar = QtGui.QScrollBar(self)
		self.horizontalScrollBar.setOrientation(QtCore.Qt.Horizontal)
		self.scrollBarSize = 15
		
		# Set scrollbars
		self.__enableVerticalScrollBar(False)
		self.__enableHorizontalScrollBar(False)
		
		# Set stretch mode
		self.setStretchMode(2)
		
		return

	# Sets the stretch mode
	def setStretchMode(self, mode):
		"""
		Sets the image stretching mode.
		0 = Do not stretch
		1 = Stretch to fit
		2 = Stretch to fit vertically
		3 = Stretch to fit horizontally
		"""
		self.stretchMode = mode
		
		# Repaint
		self.calculateSizesAndUpdateScrollbars()
		self.forceRepaint()
		
		return

	# Gives the frame a qimage to display
	def takeImage(self, qimage):
		"""
		Gives the PictureFrame a qimage to display.
		No further processing of the image will be done, except for 
		alignment and scaling (if any)
		"""
		
		# Set image
		self.image = qimage
		
		# Get full source rect
		self.sourceRect = QtCore.QRectF(0, 0, 
						self.image.size().width(), 
						self.image.size().height()
					)
		
		# Repaint
		self.calculateSizesAndUpdateScrollbars()
		self.forceRepaint()
		return

	# Sets the background color
	def setBackgroundColor(self, color, alpha=255):
		"""
		Sets the color to be used for the background whenever the image
		is too small to fill the viewport.
		The alpha parameter defines the transparency of the color, 0 being
		invisible, 255 being opaque.
		"""
		self.bgColor = QtGui.QColor(color)
		self.bgColor.setAlpha(alpha)
		return

	# Refreshes the scrollbars
	def updateScrollBars(self):
		"""Updates the scrollbar sizes and positions"""
		
		# The right scrollbar
		left = self.width() - self.verticalScrollBar.width()
		top = 0
		width = self.scrollBarSize
		height = self.height()
		if self.horizontalScrollBarEnabled:
			height -= self.horizontalScrollBar.height()
		self.verticalScrollBar.setGeometry( left, top, width, height )
		
		# The bottom scrollbar
		left = 0
		top = self.height() - self.horizontalScrollBar.height()
		width = self.width()
		if self.verticalScrollBarEnabled:
			width -= self.verticalScrollBar.width()
		height = self.scrollBarSize
		self.horizontalScrollBar.setGeometry( left, top, width, height )

		return

	# Enables the horizontal scroll bar
	def __enableHorizontalScrollBar(self, enabled, update=False):
		"""
		Enables or disables the horizontal scroll bar
		"""
		self.horizontalScrollBarEnabled = enabled
		self.horizontalScrollBar.setVisible(enabled)
		if update:
			self.updateScrollBars()
		return
		
	# Enables the vertical scroll bar
	def __enableVerticalScrollBar(self, enabled, update=False):
		"""
		Enables or disables the vertical scroll bar
		"""
		self.verticalScrollBarEnabled = enabled
		self.verticalScrollBar.setVisible(enabled)
		if update:
			self.updateScrollBars()
		return
		
	# Calculates the viewport size
	def __calculateViewport(self, includeScrollbars=False):
		"""Calculates the viewport size"""
		# Get new dimensions
		height = self.height()
		if includeScrollbars and self.horizontalScrollBarEnabled:
			height -= self.horizontalScrollBar.height()
		width = self.width()
		if includeScrollbars and self.verticalScrollBarEnabled:
			width -= self.verticalScrollBar.width()

		# Set new viewport size
		viewport = QtCore.QRect( 0.0, 0.0, width, height )
		viewportF = QtCore.QRectF( 0.0, 0.0, width, height )
		
		return viewport, viewportF

	# Called when the frame got resized
	def resizeEvent(self, event):
		self.calculateSizesAndUpdateScrollbars()
		self.forceRepaint()
		return

	# Calculate the target rectangle for the painting function
	def __calculateTargetRect(self, viewport):
		"""Calculates the target rectangle for the painting functions"""
		
		if not self.image:
			return self.rect()
		
		# Default for "size to fit"
		targetRect = QtCore.QRectF( 
			0, 0,
			viewport.width(), viewport.height()
			)
		
		# Get sizes
		imageHeight = self.image.height()
		imageWidth = self.image.width()
		
		# Dispatch
		if self.stretchMode == 2: # size to fit vert
			# Get new width
			width = viewport.height() * imageWidth / imageHeight
			# Get new left
			left = ( viewport.width() - width ) / 2.0
			# Set
			targetRect = QtCore.QRectF( left, 0, width, viewport.height() )
		
		return targetRect
		
	# Calculates viewport and target sizes
	# Updates the scrollbars if necessary
	def calculateSizesAndUpdateScrollbars(self):
		"""Calculates the bounds for the painting function."""	
		
		# Calculate the space needed by the picture.
		# If necessary, take into account the window size.
		# This will be called the target rect.
		targetRect = self.__calculateTargetRect(self.rect())
		
		# Assume we can use the whole window's space.
		# We will call this visible space the viewport.
		viewport, viewportF = self.__calculateViewport(False)
		
		# Then, see if any of the target rect's borders
		# are outside of the window's borders.
		targetRectHeightClipped = False
		if targetRect.bottom() > viewport.height():
			targetRectHeightClipped = True

		targetRectWidthClipped = False			
		if targetRect.right() > viewport.width():
			targetRectWidthClipped = True
		
		# If so, enable the appropriate scrollbar that would fix this.
		# Subtract the size of the scrollbar from the viewport.
		if targetRectWidthClipped:
			self.__enableHorizontalScrollBar(True, False)
			viewport, viewportF = self.__calculateViewport(True)
		else:
			self.__enableHorizontalScrollBar(False, False)
			
		if targetRectHeightClipped:
			self.__enableVerticalScrollBar(True, False)
			viewport, viewportF = self.__calculateViewport(True)
		else:
			self.__enableVerticalScrollBar(False, False)
		
		# Test if either of the both scrollbars is enabled
		if (targetRectWidthClipped or targetRectHeightClipped):

			# But if both are enabled, we are already partly done here
			if not (targetRectWidthClipped and targetRectHeightClipped):
		
				# Now that the viewport is getting smaller, check
				# if the target rect is clipped.
				# If so, enable the other scrollbar to compensate.
				if targetRectWidthClipped:
					if targetRect.bottom() > viewport.height():
						self.__enableVerticalScrollBar(True, False)
				else: # check the other scrollbar
					if targetRect.right() > viewport.width():
						self.__enableHorizontalScrollBar(True, False)

		# Update the scrollbars
		self.updateScrollBars()			

		# Now set rectangles
		self.viewport = viewport
		self.viewportF = viewportF
		self.targetRect = targetRect

		return


	# Control needs to paint itself
	def paintEvent(self, event):
		# Obtain painter
		painter = QtGui.QPainter(self)

		# Get the painting rectangle
		viewport = self.viewportF

		# Clip to viewport		
		region = QtGui.QRegion(self.viewport)
		painter.setClipRegion(region)
		
		# Obtain brush and fill background
		# Do not paint background if "size to fit" mode is enabled
		if self.stretchMode != 1:
			# TODO: Clip paint operation against the actual image size
			color = QtGui.QColor(self.bgColor)
			brush = QtGui.QBrush(color)
			painter.fillRect(viewport, brush)

		
		color = QtGui.QColor(self.bgColor)
		brush = QtGui.QBrush(color)
		painter.fillRect(self.rect(), brush)
					
		# Paint
		if self.image:
			painter.drawImage(self.targetRect, self.image, self.sourceRect)
		
		return

	# Paints the widget
	def forceRepaint(self):
		"""Forces a repaint of the PictureFrame"""
		# Force repaint
		self.repaint(self.viewport)
		return

