# -*- coding: utf-8 -*-
#
# Disable pylint spaces/tabs warning
# pylint: disable-msg=W0312
# pylint: disable-msg=W0511

from PyQt4.QtOpenGL import QGLWidget
from DisplayArea import DisplayArea

class GLDisplayArea(QGLWidget, DisplayArea):
	"""OpenGL based DisplayArea"""
	
	def __init__(self, parent=None):
		"""Initializes the class"""
		QGLWidget.__init__(self, parent)
		DisplayArea.__init__(self, parent)
	
	def isOpenGL(self):
		"""Determines if this class is OpenGL based. Returns true."""
		return True
