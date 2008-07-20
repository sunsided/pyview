# -*- coding: utf-8 -*-
#
# Disable pylint spaces/tabs warning
# pylint: disable-msg=W0312
# pylint: disable-msg=W0511

from threading import Thread

class ImageLoader(Thread):
	"""Helper class for asynchronous image loading"""
	
	def __init__(self, displayArea):
		self.displayArea = displayArea
		Thread.__init__(self)
	
	def setSource(self, source):
		pass
		
	def run(self):
		pass

