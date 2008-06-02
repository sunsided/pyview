#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore

class MyForm(QtGui.QWidget):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)

		self.resize(250, 150)
		self.setWindowTitle('Testanwendung')
		self.setWindowIcon(QtGui.QIcon('icons/icon.gif'))
		self.center()

		QtGui.QToolTip.setFont(QtGui.QFont('OldEnglish', 10))
		quit = QtGui.QPushButton(u"Schließen", self)
		quit.setGeometry(10, 10, 60, 35)
		quit.setToolTip("Das Fenster nach <b>Oblivion</b> schicken")

		self.connect(	quit, QtCore.SIGNAL('clicked()'), 
						self, QtCore.SLOT('close()'))

	def closeEvent(self, event):
		reply = QtGui.QMessageBox.question(self, 'Programm beenden',
			"Sind Sie sicher?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

		if reply == QtGui.QMessageBox.Yes:
			event.accept()
		else:
			event.ignore()

	def center(self):
		screen = QtGui.QDesktopWidget().screenGeometry()
		size =  self.geometry()
		self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)


app = QtGui.QApplication(sys.argv)

# Siehe: http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/qtranslator.html
translator = QtCore.QTranslator()
translator.load("qt_de", "/usr/share/qt4/translations")
app.installTranslator(translator)

form = MyForm()
form.show()

sys.exit(app.exec_())

