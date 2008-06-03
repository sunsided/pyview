#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Kudos:
#		http://www.webappers.com/2008/02/12/webappers-released-free-web-application-icons-set/
#		http://lists.kde.org/?l=pykde&m=114235100819012&w=2

import sys, os, Image
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class QDisplay(QWidget):
	def __init__(self, parent=None):
		QWidget.__init__(self, parent)
			
		# Hintergrundfarbe setzen
		self.setAutoFillBackground(True)
		palette = self.palette()
		palette.setColor(QPalette.Background, QColor(32, 32, 32))
		self.setPalette(palette)
		
		# Variablen setzen
		self.image = QImage()
		
	def open(self, filename):
		print("Opening file: " + filename)
		
		# load an image using PIL, first read it
		self.PILimage  = Image.open(str(filename))
		
		print("File opened.")
		
		self.__PIL2Qt()
		
	def __PIL2Qt(self, encoder="jpeg", mode="RGB"):
		print("Converting file ...")
		
		# I have only tested the jpeg encoder, there are others, see
		# http://mail.python.org/pipermail/image-sig/2004-September/002908.html
		PILstring = self.PILimage.convert(mode).tostring(encoder, mode)
		self.image.loadFromData(QByteArray(PILstring))
		
		print("File converted and image set.")
		
	def paintEvent(self, Event):
		print("In paint event.")
	
		painter = QPainter(self)
		painter.drawImage(0, 0, self.image)
		
		print("Left paint event.")

class MyForm(QMainWindow):
	# Membervariablen
	lastOpenedFile = None

	def __init__(self, parent=None):
		QMainWindow.__init__(self, parent)

		# Fensterstatus setzen
		self.resize(640, 480)
		self.setWindowTitle("Testanwendung")
		self.setWindowIcon(QIcon("icons/icon.gif"))
		self.center()
		self.statusBar().showMessage("Programm gestartet.")
		
		# Das Display-Widget
		self.displayArea = QDisplay()
		self.setCentralWidget(self.displayArea)

		# Menüeintrag zum Laden eines Bildes
		open = QAction(QIcon("icons/Load.png"), "&Laden ...", self)
		open.setShortcut("O")
		open.setStatusTip("Eine Bilddatei laden")
		self.connect(open, SIGNAL("triggered()"), self.openImageDialog)
		
		# Menüeintrag zum Laden eines Bildes
		reopen = QAction(QIcon("icons/Load.png"), "&Erneut laden", self)
		reopen.setShortcut("SHIFT+R")
		reopen.setStatusTip("Letzte Bilddatei erneut laden")
		self.connect(reopen, SIGNAL("triggered()"), self.reOpenImage)
		
		# Menüeintrag zum Beenden
		exit = QAction(QIcon("icons/exit.gif"), "&Beenden", self)
		exit.setShortcut("ESC")
		exit.setStatusTip("Beendet das Programm")
		self.connect(exit, SIGNAL("triggered()"), SLOT("close()"))
		
		# Menüzeile
		# http://zetcode.com/tutorials/pyqt4/menusandtoolbars/
		menubar = self.menuBar()
		file = menubar.addMenu("&Datei")
		file.addAction(open)
		file.addAction(reopen)
		file.addSeparator()
		file.addAction(exit)

	def getUserHomeDir(self):
		return str(os.environ.get('HOME'))

	def openImageDialog(self):
		# Startverzeichnis holen
		startDir = self.getUserHomeDir()
		if( self.lastOpenedFile != None ):
			startDir = os.path.basename(str(self.lastOpenedFile))
		
		# Dateifilter definieren
		filters = QStringList()
		filters << "Bilder (*.png *.xpm *.jpg)" << "Alle Dateien (*)";
		
		# Dialog anzeigen
		dialog = QFileDialog(self)
		dialog.setFileMode(QFileDialog.ExistingFile)
		dialog.setDirectory(startDir)
		dialog.setFilters(filters)
		dialog.setViewMode(QFileDialog.Detail)
		
		# Wenn OK geklickt wurde, ...
		if( dialog.exec_() ):
			# Dateinamen holen und Datei öffnen
			fileNames = dialog.selectedFiles()
			fileName = fileNames[0]
			self.lastOpenedFile = fileName
			self.openImage(fileName)

	def reOpenImage(self):
		if( self.lastOpenedFile == None ):
			return
		self.openImage(self.lastOpenedFile)

	def openImage(self, fileName):
		self.displayArea.open(str(fileName))
		self.displayArea.repaint()

	def closeEvent(self, event):
		# TODO Nachfragen, ob das Programm beendet werden soll per Optionen ein- oder ausschalten
		#reply = QMessageBox.question(self, "Programm beenden", "Sind Sie sicher?", QMessageBox.Yes, QMessageBox.No)

		#if reply == QMessageBox.Yes:
		#	event.accept()
		#else:
		#	event.ignore()
		return

	def center(self):
		screen = QDesktopWidget().screenGeometry()
		size =  self.geometry()
		self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)


# Die Anwendung nur starten, wenn die Source nicht als Modul geladen wird
if( __name__ == "__main__" ):
	app = QApplication(sys.argv)

	# Siehe: http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/qtranslator.html
	translator = QTranslator()
	translator.load("qt_de", "/usr/share/qt4/translations")
	app.installTranslator(translator)

	form = MyForm()
	form.show()

	sys.exit(app.exec_())

