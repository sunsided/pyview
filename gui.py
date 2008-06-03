#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Kudos:
#		http://www.webappers.com/2008/02/12/webappers-released-free-web-application-icons-set/
#		http://lists.kde.org/?l=pykde&m=114235100819012&w=2

import sys, os, Image
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class QDisplay(QLabel):
	# Member
	image = None

	def __init__(self, parent=None):
		"""Initialisiert die Klasse"""
	
		QWidget.__init__(self, parent)
			
		# Hintergrundfarbe setzen
		self.setAutoFillBackground(True)
		palette = self.palette()
		palette.setColor(QPalette.Background, QColor(32, 32, 32))
		self.setPalette(palette)
		
		# Tweaking
		self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
		self.setScaledContents(True)
		
		# Variablen setzen
		self.image = QImage()
		
	def open(self, filename):
		"""Öffnet ein Bild, dessen Dateiname bekannt ist"""
		
		print("Opening file: " + filename)
		# load an image using PIL, first read it
		self.PILimage  = Image.open(str(filename))		
		print("File opened.")
		self.__PIL2Qt()
		
	def __PIL2Qt(self, encoder="jpeg", mode="RGB"):
		"""Wandelt ein Bild der PIL in ein QImage um"""
	
		print("Converting file ...")
		
		# I have only tested the jpeg encoder, there are others, see
		# http://mail.python.org/pipermail/image-sig/2004-September/002908.html
		PILstring = self.PILimage.convert(mode).tostring(encoder, mode)
		self.image.loadFromData(QByteArray(PILstring))
		self.resize(self.image.size())

		print("File converted and image set.")
		
	def paintEvent(self, Event):
		"""Zeichnet das Bild erneut"""
	
		painter = QPainter(self)
		painter.drawImage(0, 0, self.image)
		
	def setSize(self, size):
		"""Setzt Größe des Anzeigeelementes"""
		return



class MyForm(QMainWindow):
	# Membervariablen
	lastOpenedFile = None
	isFullScreen = False
	
	# Objekte
	scrollArea = None
	displayArea = None
	
	# Menüeinträge
	menuFileReopen = None
	sizeToFit = None

	def __init__(self, parent=None):
		"""Initialisiert das Anwendungsfenster"""
	
		QMainWindow.__init__(self, parent)

		# Fensterstatus setzen
		self.resize(640, 480)
		self.setWindowTitle("Testanwendung")
		self.setWindowIcon(QIcon("icons/icon.gif"))
		self.center()
		self.statusBar().showMessage("Programm gestartet.")
			
		# Das Display-Widget
		self.displayArea = QDisplay()
		
		# Scroll Area
		self.scrollArea = QScrollArea(self)
		self.scrollArea.setBackgroundRole(QPalette.Dark)
		self.scrollArea.setWidget(self.displayArea)
		self.setCentralWidget(self.scrollArea)
		#self.setCentralWidget(self.displayArea)

		# Menüeintrag zum Laden eines Bildes
		open = QAction(QIcon("icons/Load.png"), "&Laden ...", self)
		open.setShortcut("O")
		open.setStatusTip("Eine Bilddatei laden")
		self.connect(open, SIGNAL("triggered()"), self.openImageDialog)
		
		# Menüeintrag zum Laden eines Bildes
		self.menuFileReopen = QAction(QIcon("icons/Load.png"), "&Erneut laden", self)
		self.menuFileReopen.setShortcut("SHIFT+R")
		self.menuFileReopen.setStatusTip("Letzte Bilddatei erneut laden")
		self.menuFileReopen.setEnabled(False)
		self.connect(self.menuFileReopen, SIGNAL("triggered()"), self.reOpenImage)
		
		# Menüeintrag zum Beenden
		exit = QAction(QIcon("icons/exit.gif"), "&Beenden", self)
		# FIXME Wenn ESC benutzt wird, um ein Menü zu schließen, geht der Shortcut flöten
		exit.setShortcut("ESC")
		exit.setStatusTip("Beendet das Programm")
		self.connect(exit, SIGNAL("triggered()"), SLOT("close()"))
		
		# Vollbild-Menüeintrag
		fullScreen = QAction(QIcon("icons/Loading.png"), "&Vollbild", self)
		fullScreen.setShortcut("RETURN")
		fullScreen.setStatusTip("Wechselt in den Vollbildmodus")
		fullScreen.connect(fullScreen, SIGNAL("triggered()"), self.toggleFullScreen)

		# Vollbild-Menüeintrag
		self.sizeToFit = QAction(QIcon("icons/Loading.png"), u"An Fenstergröße &anpassen", self)
		self.sizeToFit.setShortcut("F")
		self.sizeToFit.setCheckable(True)
		self.sizeToFit.setStatusTip(u"Passt das Bild an die Fenstergröße an")
		self.sizeToFit.connect(self.sizeToFit, SIGNAL("triggered()"), self.setFitToWindow)
		
		# Menüzeile
		# http://zetcode.com/tutorials/pyqt4/menusandtoolbars/
		menuBar = self.menuBar()
		
		# Dateimenü
		file = menuBar.addMenu("&Datei")
		file.addAction(open)
		file.addAction(self.menuFileReopen)
		file.addSeparator()
		file.addAction(exit)
		self.addAction(exit) # http://lists.trolltech.com/qt-interest/2007-07/thread00771-0.html
	
		
		# Ansichtsmenü
		view = menuBar.addMenu("&Ansicht")
		view.addAction(self.sizeToFit)
		self.addAction(self.sizeToFit)
		view.addAction(fullScreen)
		self.addAction(fullScreen)

		# Eigene Trigger
		self.connect(self, SIGNAL("imageLoaded"), self.notifyFileLoaded)
	
	def toggleFullScreen(self):
		"""Schaltet zwischen Vollbild und Normalansicht um"""
	
		self.isFullScreen = not self.isFullScreen
		if(self.isFullScreen):
			self.showFullScreen()
			self.menuBar().hide()
			self.statusBar().hide()
		else:
			self.showNormal()
			self.menuBar().show()
			self.statusBar().show()
	
	def notifyFileLoaded(self):
		"""Wird gerufen, wenn eine Datei geladen wurde"""
	
		self.setStatusTip("Datei geladen.")
		if( self.lastOpenedFile != None):
			self.menuFileReopen.setEnabled(True)
		
	def getUserHomeDir(self):
		"""Holt das Home-Verzeichnis des aktuellen Nutzers"""
	
		return str(os.environ.get('HOME'))

	def openImageDialog(self):
		"""Zeigt den \"Bild Laden\"-Dialog an"""
	
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
		"""Öffnet das zuletzt geöffnete Bild erneut"""
	
		if( self.lastOpenedFile == None ):
			return
		self.openImage(self.lastOpenedFile)

	def openImage(self, fileName):
		"""Lädt ein Bild, dessen Pfad bekannt ist"""
	
		self.displayArea.open(str(fileName))
		self.displayArea.repaint()
		self.emit(SIGNAL("imageLoaded"), ())

	def closeEvent(self, event):
		"""Wird gerufen, wenn die Anwendung geschlossen werden soll"""
	
		# TODO Nachfragen, ob das Programm beendet werden soll per Optionen ein- oder ausschalten
		#reply = QMessageBox.question(self, "Programm beenden", "Sind Sie sicher?", QMessageBox.Yes, QMessageBox.No)

		#if reply == QMessageBox.Yes:
		#	event.accept()
		#else:
		#	event.ignore()
		return

	def center(self):
		"""Zentriert die Anwendung auf dem Bildschirm"""
	
		screen = QDesktopWidget().screenGeometry()
		size =  self.geometry()
		self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
		
	def setFitToWindow(self):
		"""Schaltet die verschiedenen Ansichtsmodi des Bildes durch"""
	
		state = self.sizeToFit.isChecked()
		print "setFitToWindow called: " + str(state)
		if( state == False):
			self.scrollArea.setWidgetResizable(False)
			#self.displayArea.resize(self.displayArea.image.size())
			self.displayArea.adjustSize()
		else:
			self.scrollArea.setWidgetResizable(True)



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

