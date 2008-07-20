# -*- coding: utf-8 -*-
#
# Disable pylint spaces/tabs warning
# pylint: disable-msg=W0312
# pylint: disable-msg=W0511

from PyQt4.QtOpenGL import QGLWidget
from DisplayArea import DisplayArea

class GLDisplayArea(QGLWidget, DisplayArea):
	"""OpenGL-Basierte DisplayArea"""
	
	def __init__(self, parent=None):
		"""Initialisiert die Klasse"""
		QGLWidget.__init__(self, parent)
		DisplayArea.__init__(self, parent)
	
	def isOpenGL(self):
		"""Gibt an, ob diese DisplayArea OpenGL nutzt"""
		return True
