# -*- coding: utf-8 -*-
#
# Disable pylint spaces/tabs warning
# pylint: disable-msg=W0312
# pylint: disable-msg=W0511

import Image
from PyQt4.QtGui import QWidget, QPainter, QPalette, QSizePolicy, QImage
from PyQt4.QtCore import SIGNAL, QSize, QByteArray

class DisplayArea(QWidget):
	"""Arthur-Basierte DisplayArea"""
	# Member
	image = None
	firstImage = True
	imageSize = QSize(0, 0)
	zoomFactor = 1.0
	
	# Konstanten
	MAX_ZOOM = 10.0
	MIN_ZOOM = 0.1
	ZOOM_STEP = 0.1
	
	def __init__(self, parent=None):
		"""Initialisiert die Klasse"""
		QWidget.__init__(self, parent)
		
		self.setBackgroundRole(QPalette.Base)
		self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
		
		# Variablen setzen
		self.PILimage = None
		self.image = QImage()

	def __del__(self):
		self.PILimage = None
		if( self.image ):
			self.image.__del__()

	def isOpenGL(self):
		"""Gibt an, ob diese DisplayArea OpenGL nutzt"""
		return False

	def loadFromFile(self, filename):
		"""Öffnet ein Bild, dessen Dateiname bekannt ist"""
		# load an image using PIL, first read it
		self.PILimage  = Image.open(filename)
		return self.__PIL2Qt()

	def __PIL2Qt(self, encoder="jpeg", mode="RGB"):
		"""Wandelt ein Bild der PIL in ein QImage um"""	
		# http://mail.python.org/pipermail/image-sig/2004-September/002908.html
		PILstring = self.PILimage.convert(mode).tostring(encoder, mode)
		if( not PILstring ): return False
		
		self.imageSize = QSize( self.PILimage.size[0], self.PILimage.size[1] )
		self.setMinimumSize( self.imageSize.width()*self.zoomFactor, self.imageSize.height()*self.zoomFactor )
		retval = self.image.loadFromData(QByteArray(PILstring))
		self.repaint()
		return retval

	def paintEvent(self, event):
		"""Zeichnet das Bild erneut"""
		if(self.image == None): return
		painter = QPainter(self)
		
		# Nicht über den Rand malen
		painter.setClipping(True)
		painter.setClipRect(self.rect())
		
		# X-Offset
		offset_x = 0
		zoomed_width = self.imageSize.width()*self.zoomFactor
		
		# Nur beim Verkleinern zentrieren
		if( self.width() > zoomed_width ):
			offset_x = (self.width() - zoomed_width) / 2
		
		# Y-Offset
		offset_y = 0
		zoomed_height = self.imageSize.height()*self.zoomFactor
		
		# Nur beim Verkleinern zentrieren
		if( self.height() > zoomed_height ):
			offset_y = (self.height() - zoomed_height) / 2
		
		painter.save()
		painter.translate(offset_x, offset_y)
		painter.scale(self.zoomFactor, self.zoomFactor)
		
		#exposedRect = painter.matrix().inverted()[0].mapRect(event.rect()).adjusted(-1, -1, 1, 1)
		painter.drawImage(0,0,self.image)
		#painter.drawImage(exposedRect, self.image, exposedRect)
		#painter.drawImage(self.parent().rect(), self.image, exposedRect)
		painter.restore()

	def setZoomFactor(self, factor):
		"""Setzt den Zoom-Faktor des Bildes"""
		if( self.zoomFactor == factor ): return
		
		self.zoomFactor = factor
		self.emit(SIGNAL("zoomFactorChanged(float)"), factor)
		
		w = self.imageSize.width() * self.zoomFactor
		h = self.imageSize.height() * self.zoomFactor
		self.setMinimumSize(w, h)
		self.resize(w, h)
		
		self.repaint()
#		
#		self.adjustScrollBar(QScrollArea(self.parent()).horizontalScrollBar(), factor)
#		self.adjustScrollBar(QScrollArea(self.parent()).verticalScrollBar(), factor)
#
#	def adjustScrollBar(self, scrollbar, factor):
#		print scrollbar.value(), scrollbar.pageStep()
#	
#		scrollbar.setValue(int(factor*scrollbar.value()) + ((factor-1) * scrollbar.pageStep()/2))
	
	def zoomIn(self):
		"""Zoomt um einen festen Betrag ein"""
		newZoomFactor = self.zoomFactor + self.ZOOM_STEP
		if( newZoomFactor >= self.MAX_ZOOM ):
			newZoomFactor = self.MAX_ZOOM
		self.setZoomFactor(newZoomFactor)

	def zoomOut(self):
		"""Zoomt um einen festen Betrag aus"""
		newZoomFactor = self.zoomFactor - self.ZOOM_STEP
		if( newZoomFactor <= self.MIN_ZOOM ):
			newZoomFactor = self.MIN_ZOOM
		self.setZoomFactor(newZoomFactor)

	def zoomFull(self):
		"""Setzt den Zoom auf 100%"""
		self.setZoomFactor(1.0)
