#!/usr/bin/python

import sys
from PyQt4 import QtGui, QtCore

class MyForm(QtGui.QWidget):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)

		self.setGeometry(300, 300, 250, 150)
		self.setWindowTitle('Icon')
		self.setWindowIcon(QtGui.QIcon('icons/icon.gif'))

		QtGui.QToolTip.setFont(QtGui.QFont('OldEnglish', 10))
		quit = QtGui.QPushButton('Close', self)
		quit.setGeometry(10, 10, 60, 35)
		quit.setToolTip('Das Fenster nach <b>Oblivion</b> schicken')

		self.connect(quit, QtCore.SIGNAL('clicked()'), 
				QtGui.qApp, QtCore.SLOT('quit()'))


app = QtGui.QApplication(sys.argv)

form = MyForm()
form.show()

sys.exit(app.exec_())

