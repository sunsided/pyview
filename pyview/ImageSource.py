# -*- coding: utf-8 -*-
#
# Disable pylint spaces/tabs warning
# pylint: disable-msg=W0312
# pylint: disable-msg=W0511

class ImageSource:
	"""Aufzählungen der Bildquellen"""
	def __init__(self):
		pass
	UNKNOWN = 0
	LOCALFILE = 1
	REMOTEFILE = 2
