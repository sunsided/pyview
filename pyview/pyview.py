#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Disable pylint spaces/tabs warning
# pylint: disable-msg=W0312
# pylint: disable-msg=W0511

import sys
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QTranslator
from mainwin import ApplicationWindow

def main():
	"""pyview main entry point"""
	
	# Create a new Qt application
	app = QApplication(sys.argv)

	# localize Qt
	# Siehe: http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/qtranslator.html
	translator = QTranslator()
	translator.load("qt_de", "/usr/share/qt4/translations")
	app.installTranslator(translator)

	# Create main application window
	form = ApplicationWindow()
	form.show()
	form.update()
	
	# Load any images from the command line
	form.loadInitialImage()

	# fire the application loop
	return app.exec_()


# If the script is called directly, run the main function
if( __name__ == "__main__" ):
	sys.exit(main())

