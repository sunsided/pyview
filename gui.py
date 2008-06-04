#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Kudos:
#		http://www.webappers.com/2008/02/12/webappers-released-free-web-application-icons-set/
#		http://lists.kde.org/?l=pykde&m=114235100819012&w=2

import sys, os, Image
from threading import Thread
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from optparse import OptionParser

class DisplayArea(QLabel):
	# Member
	image = None
	firstImage = True

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
	
		if( self.firstImage == True ):
			self.firstImage = False
			size = QSize( self.PILimage.size[0], self.PILimage.size[1] )
			self.setSize(size)
		
		return self.image.loadFromData(QByteArray(PILstring))
		
	def paintEvent(self, Event):
		"""Zeichnet das Bild erneut"""
		painter = QPainter(self)

		if(self.image == None): return

		# Hole Skalierung
		# TODO: Division durch 0 testen
		scale_x = float(self.size().width()) / self.image.size().width()
		scale_y = float(self.size().height()) / self.image.size().height()	
		painter.scale(scale_x, scale_y)
		
		painter.drawImage(0, 0, self.image)
		
	def setSize(self, size, sizey=None):
		"""Setzt Größe des Anzeigeelementes"""
		if( sizey != None):
			size = QSize(size, sizey)
		self.resize(size)
		return
		
	def setFullSize(self):
		"""Setzt Größe des Anzeigeelementes auf die Größe des Bildes"""
		self.resize(self.image.size())
		return

class ImageSource:
	Unknown = 0
	LocalFile = 1
	RemoteFile = 2

class ApplicationWindow(QMainWindow):
	# Kontanten
	APPNAME = "Bildbetrachter"
	APPVERSION = "0.1"

	# Membervariablen
	lastOpenedFile = None
	isFullScreen = False
	askBeforeClosing = False
	loadedFromCommandLine = False
	
	# Objekte
	scrollArea = None
	displayArea = None
	cmdLineOptions = None
	cmdLineArgs = []
	tempFiles = []
	
	def __init__(self, parent=None):
		"""Initialisiert das Anwendungsfenster"""
		QMainWindow.__init__(self, parent)

		# Kommandozeilenoptionen, Teil 1
		self.buildCmdLineParser()

		# Fensterstatus setzen
		self.setWindowTitle(self.APPNAME)
		self.setWindowIcon(QIcon("icons/icon.gif"))
		self.resize(640, 480)
		self.center()
		self.statusBar()

		# Vollbildmodus switchen
		if( self.cmdLineOptions.fullScreen ):
			self.toggleFullScreen()
		
		# Drag&Drop initialisieren
		self.setAcceptDrops(True)
		self.__class__.dragEnterEvent = self.dragEnterEvent
		self.__class__.dropEvent = self.dragDropEvent
			
		# Das Display-Widget
		self.displayArea = DisplayArea()
		
		# Scroll Area
		self.scrollArea = QScrollArea(self)
		self.scrollArea.setBackgroundRole(QPalette.Dark)
		self.scrollArea.setWidget(self.displayArea)
		self.setCentralWidget(self.scrollArea)

		# Menü erstellen
		self.buildMenu()
		
		# Weitere Hooks
		self.connect(self, SIGNAL("imageLoaded(bool)"), self.notifyFileLoaded)
		self.connect(self, SIGNAL("imageLoading(bool, int, bool)"), self.notifyFileLoading)
		
		print "initializer done"
		
	def buildMenu(self):
		"""Erstellt die Menüleiste und setzt die Shortcuts"""
		
		# Menüzeile
		# http://zetcode.com/tutorials/pyqt4/menusandtoolbars/
		# http://lists.trolltech.com/qt-interest/2007-07/thread00771-0.html
		menuBar = self.menuBar()
		
		# Menüeintrag zum Laden eines Bildes
		menuFileOpen = QAction(QIcon("icons/Load.png"), "&Laden ...", self)
		menuFileOpen.setShortcut("O")
		menuFileOpen.setStatusTip("Eine Bilddatei laden")
		self.connect(menuFileOpen, SIGNAL("triggered()"), self.openImageDialog)
		
		# Menüeintrag zum Laden eines Bildes
		menuFileReopen = QAction(QIcon("icons/Load.png"), "&Erneut laden", self)
		menuFileReopen.setShortcut("SHIFT+R")
		menuFileReopen.setStatusTip("Letzte Bilddatei erneut laden")
		menuFileReopen.setEnabled(False)
		self.connect(menuFileReopen, SIGNAL("triggered()"), self.reOpenImage)
		self.connect(self, SIGNAL("imageLoaded(bool)"), menuFileReopen, SLOT("setEnabled(bool)"))
		
		# Menüeintrag zum Beenden
		menuFileExit = QAction(QIcon("icons/exit.gif"), "&Beenden", self)
		menuFileExit.setShortcut("ESC")
		menuFileExit.setStatusTip("Beendet das Programm")
		self.connect(menuFileExit, SIGNAL("triggered()"), SLOT("close()"))
		
		# Dateimenü
		file = menuBar.addMenu("&Datei")	
		self.addAction(menuFileOpen)
		file.addAction(menuFileOpen)
		self.addAction(menuFileReopen)
		file.addAction(menuFileReopen)
		file.addSeparator()
		self.addAction(menuFileExit)
		file.addAction(menuFileExit)
		
		# Vollbild-Menüeintrag
		menuViewFullScreen = QAction(QIcon("icons/Loading.png"), "&Vollbild", self)
		menuViewFullScreen.setShortcut("RETURN")
		menuViewFullScreen.setStatusTip("Wechselt in den Vollbildmodus")
		menuViewFullScreen.setCheckable(True)
		menuViewFullScreen.setChecked(bool(self.cmdLineOptions.fullScreen))
		menuViewFullScreen.connect(menuViewFullScreen, SIGNAL("triggered()"), self.toggleFullScreen)
		
		# Anzeigemodi
		menuViewWindowToImageSize = QAction("Fenster ans Bild anpassen (1:1, empfo&hlen)", self)
		menuViewWindowToImageSize.setCheckable(True)
		menuViewWindowToImageSize.setProperty("tag", QVariant("WindowToImageSize"))
		menuViewWindowToImageSize.setStatusTip(u"Passt das Fenster an die Bildgröße an")
		
		menuViewSizeToFit = QAction("Bild ans Fenster anpa&ssen", self)
		menuViewSizeToFit.setCheckable(True)
		menuViewSizeToFit.setProperty("tag", QVariant("SizeToFit"))
		menuViewSizeToFit.setStatusTip(u"Passt das Bild an die Fenstergröße an")

		menuViewSizeLargeToFit = QAction(u"Nur große Bilder ans Fenster anpa&ssen", self)
		menuViewSizeLargeToFit.setCheckable(True)
		menuViewSizeLargeToFit.setProperty("tag", QVariant("SizeLargeToFit"))
		menuViewSizeLargeToFit.setStatusTip(u"Passt das Bild an die Fenstergröße an")
		
		menuViewFitToScreen = QAction("Fenster/Bild an Bildschirm anpassen", self)
		menuViewFitToScreen.setCheckable(True)
		menuViewFitToScreen.setShortcut("F")
		menuViewFitToScreen.setProperty("tag", QVariant("FitToScreen"))
		menuViewFitToScreen.setStatusTip(u"Passt Fenster und Bild an die Bildschirmgröße an")
		
		menuViewFitLargeToScreen = QAction(u"Nur große Bilder an Bildschirm anpassen", self)
		menuViewFitLargeToScreen.setCheckable(True)
		menuViewFitLargeToScreen.setProperty("tag", QVariant("FitLargeToScreen"))
		menuViewFitLargeToScreen.setStatusTip(u"Passt große Bilder an die Bildschirmgröße an")
		
		menuViewFitToScreenWidth = QAction("Bilder an Bildschirmbreite anpassen", self)
		menuViewFitToScreenWidth.setCheckable(True)
		menuViewWindowToImageSize.setProperty("tag", QVariant("FitToScreenWidth"))
		menuViewFitToScreenWidth.setStatusTip("Passt Bilder an die Bildschirmbreite an")
		
		menuViewFitToScreenHeight = QAction(u"Bilder an Bildschirmhöhe anpassen", self)
		menuViewFitToScreenHeight.setCheckable(True)
		menuViewFitToScreenHeight.setProperty("tag", QVariant("FitToScreenHeight"))
		menuViewFitToScreenHeight.setStatusTip(u"Passt Bilder an die Bildschirmhöhe an")
		
		menuViewNoFit = QAction(u"Keine A&npassung durchführen", self)
		menuViewNoFit.setCheckable(True)
		menuViewNoFit.setProperty("tag", QVariant("NoFit"))
		menuViewNoFit.setStatusTip("Bilder werden nicht angepasst")
		
		# Ansichtsmenü
		view = menuBar.addMenu("&Ansicht")
		self.addAction(menuViewFullScreen)
		view.addAction(menuViewFullScreen)
		
		# Anzeige-OptionsMenü
		viewOptionsWindowed = view.addMenu("&Anzeige-Optionen (Fenstermodus)")
		viewOptionsWindowedGroup = QActionGroup(self)
		viewOptionsWindowedGroup.addAction(menuViewWindowToImageSize)
		viewOptionsWindowedGroup.addAction(menuViewSizeToFit)
		viewOptionsWindowedGroup.addAction(menuViewSizeLargeToFit)
		#viewOptionsWindowedGroup.addSeparator()
		# self.addAction(menuViewFitToScreen)
		viewOptionsWindowedGroup.addAction(menuViewFitToScreen)
		viewOptionsWindowedGroup.addAction(menuViewFitLargeToScreen)
		#viewOptionsWindowedGroup.addSeparator()
		viewOptionsWindowedGroup.addAction(menuViewFitToScreenWidth)
		viewOptionsWindowedGroup.addAction(menuViewFitToScreenHeight)
		viewOptionsWindowedGroup.addAction(menuViewNoFit)
		viewOptionsWindowedGroup.connect(viewOptionsWindowedGroup, SIGNAL("triggered(QAction*)"), self.trigger)
		viewOptionsWindowed.addActions(viewOptionsWindowedGroup.actions())
	
	def trigger(self, action):
		print "Selected Menu: " + action.property("tag").toString()
	
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
	
	def notifyFileLoading(self, loading, source, success):
		"""Wird gerufen, wenn eine Datei geladen wird"""
		if( source == 0 or source == 1 ):
			if( loading ):
				print "Loading file ..."
				self.setStatusTip("Lade Datei ...")
			else:
				if( success ):
					print "Done loading of file."
					self.setStatusTip("Laden von Datei abgeschlossen.")
				else:
					print "Canceled loading of file."
					self.setStatusTip("Laden von Datei abgebrochen.")
		else:
			if( loading ):
				print "Loading remote file..."
				self.setStatusTip("Lade entfernte Datei ...")
			else:
				if( success ):
					print "Done loading remote file."
					self.setStatusTip("Laden von entfernter Datei abgeschlossen.")
				else:
					print "Canceled loading remote file."
					self.setStatusTip("Laden von entfernter Datei abgebrochen.")
	
	def notifyFileLoaded(self):
		"""Wird gerufen, wenn eine Datei geladen wurde"""	
		print "File loaded."
		self.setStatusTip("Datei geladen.")
		
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
		filters << "Bilder (*.jpg *.gif *.png *.xpm)"
		filters << "Alle Dateien (*)"
		
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
			self.loadImageFromFile(fileName)

	def reOpenImage(self):
		"""Öffnet das zuletzt geöffnete Bild erneut"""
	
		if( self.lastOpenedFile == None ):
			print "Could not open last image: No known last image."
			return
		self.loadImageFromFile(self.lastOpenedFile)

	def loadImageFromFile(self, fileName):
		"""Lädt ein Bild, dessen Pfad bekannt ist"""
		self.emit(SIGNAL("imageLoading(bool,int,bool)"), True, ImageSource.LocalFile, False)
		return self.internalLoadImageFromFile(fileName, ImageSource.LocalFile)
			
	def internalLoadImageFromFile(self, fileName, source):
		"""Lädt ein Bild, dessen Pfad bekannt ist"""

		success = False
		try:
			success = self.displayArea.loadFromFile(str(fileName))
			self.displayArea.repaint()
			self.lastOpenedFile = fileName
			self.emit(SIGNAL("imageLoaded(bool)"), True)
			return True
		except:
			print "Could not load image: ", sys.exc_info()
			return False
		finally:
			self.emit(SIGNAL("imageLoading(bool,int,bool)"), False, int(source), success)
	
	def canHandleMimeType(self, mimetype):
		"""Testet, ob eine Datei eines bestimmten Mime-Typs geladen werden kann"""
		# TODO: Sinnvolle Implementierung auf Basis tatsächlich möglicher Dinge
		mimetype = str(mimetype).lower()
		if( mimetype.startswith("image/")): return True
		if( mimetype.startswith("application/octet-stream") ): return True
		return False
	
	def loadImageFromWeb(self, url):
		"""Lädt ein Bild aus dem Netz"""
		self.emit(SIGNAL("imageLoading(bool,int,bool)"), True, ImageSource.RemoteFile, False)
		
		# TODO: Testen, ob die Datei evtl. bereits heruntergeladen wurde (Temporärdateicache)
		
		# http://docs.python.org/lib/module-urllib2.html
		import urllib2, tempfile
		image = None; tempFile = None; tempFileName = None; success = False
		try:
			self.emit(SIGNAL("downloadingFile(bool)"), True)

			# Verbindung herstellen		
			url = str(url)
			image = urllib2.urlopen(str(url))
			
			# Get image info
			info = image.info()
			
			# Mime-Typ testen
			if( info.has_key("Content-Type") ):
				mime = info["Content-Type"]
				if not self.canHandleMimeType(str(mime)):
					print "Unsupported MIME type: ", mime
					
					self.emit(SIGNAL("imageLoading(bool,int,bool)"), False, ImageSource.RemoteFile, False)
					return False
			
			# TODO: Nachfragen, bevor ein großes Bild heruntergeladen wird
			if( info.has_key("Content-Length") ):
				size = info["Content-Length"]
				print "Remote content size: ", size
			
			# Create temp file
			(tempFile, tempFileName) = tempfile.mkstemp(".fromweb", "iview-")
			tempFile = open(tempFileName, "wb")
		
			# Copy web stream to disk (in chunks)
			while True:
				data = image.read(1024)
				if( data ):
					tempFile.write(data)
				else:
					break
					
		except urllib2.URLError:
			# TODO: Testen, ob die URL ungültig ist (404 oder so)
			print "Problem beim Laden der URL: Netzwerk- oder Serverfehler: ", sys.exc_info()
			return False
		except:
			print "Fehler beim Speichern des Bildes: ", sys.exc_info()
			return False
		finally:
			if(image): image.close()		
			if(tempFile): tempFile.close()		
			self.emit(SIGNAL("downloadingFile(bool)"), False)
		# TODO: Weitere Exceptions abgreifen
		
		# Temporäre Datei merken, um sie zum Programmende zu löschen
		self.tempFiles.append( (tempFileName, url) )
		
		# Bild laden
		if( tempFileName ):
			success = self.internalLoadImageFromFile( tempFileName, ImageSource.RemoteFile )
		
		return True

	def closeEvent(self, event):
		"""Wird gerufen, wenn die Anwendung geschlossen werden soll"""

		if( self.askBeforeClosing ):
			reply = QMessageBox.question(self, "Programm beenden", "Sind Sie sicher?", QMessageBox.Yes, QMessageBox.No)
	
			if reply == QMessageBox.Yes:
				event.accept()
			else:
				event.ignore()
				return
		
		# Aufräumen
		if( self.cmdLineOptions.tempClean ): self.deleteTempFiles()

	def center(self):
		"""Zentriert die Anwendung auf dem Bildschirm"""
	
		screen = QDesktopWidget().screenGeometry()
		size =  self.geometry()
		self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
		
	def setFitToWindow(self, state):
		"""Schaltet die verschiedenen Ansichtsmodi des Bildes durch"""
	
		print "setFitToWindow called: " + str(state)
		if( state == False):
			self.scrollArea.setWidgetResizable(False)
			#self.displayArea.resize(self.displayArea.image.size())
			self.displayArea.adjustSize()
		else:
			self.scrollArea.setWidgetResizable(True)
	
	def dragEnterEvent(self, event):
		"""Handhabt DragEnter-Events"""
		#if event.mimeData().hasImage() == True:
		if event.mimeData().hasUrls() == True:
			urllist = event.mimeData().urls()
			for url in urllist:
				#print "  URL: " + url.toString()
				fileName = url.toLocalFile()
				if( fileName != "" ):
					event.acceptProposedAction()
				else:
					# TODO: Weiteres testen, ob das hier eine Web-URL ist
					event.acceptProposedAction()
	
	def dragDropEvent(self, event):
		"""Handhabt Drop-Events"""
		if event.mimeData().hasUrls() == True:
			urllist = event.mimeData().urls()
			for url in urllist:
				#print "  URL: " + url.toString()
				fileName = url.toLocalFile()
				if( fileName != "" ):
					event.acceptProposedAction()
					self.loadImageFromFile(fileName)
				else:
					# TODO: Weiteres testen, ob das hier eine Web-URL ist
					# TODO: Evtl. direkt auf den Programmcache zugreifen, wenn möglich
					event.acceptProposedAction()
					self.loadImageFromWeb(url.toString())
		
	def buildCmdLineParser(self):
		"""Erstellt den Kommandozeilenoptionsparser"""
		# http://docs.python.org/lib/module-optparse.html
		# http://optik.sourceforge.net/doc/1.5/tutorial.html
		# http://optik.sourceforge.net/doc/1.5/reference.html

		versionString = self.APPNAME + " v" + self.APPVERSION
		usageString = "%prog [Optionen] [Dateiname]"
		descString = "Ein einfacher Bildbetrachter im Stil von IrfanView"
		
		# Parser erstellen
		cmdOptParser = OptionParser(usage = usageString, 
									version = versionString,
									description = descString)
		
		# Optionen definieren
		cmdOptParser.add_option("-f", "--fullscreen", dest="fullScreen", 
								action="store_true", default=False,
								help="start in fullscreen mode")
		cmdOptParser.add_option("--no-tempclean", dest="tempClean", 
								action="store_false", default=True,
								help="don't delete cached files when exiting")
		
		# Parsen
		(self.cmdLineOptions, self.cmdLineArgs)	= cmdOptParser.parse_args()	
		return self.cmdLineArgs
		
	def loadInitialImage(self):
		"""Lädt das Bild von der Kommandozeile"""
	
		# Kommandozeilenoptionen, Teil 2
		if( not self.loadedFromCommandLine ):
			self.loadedFromCommandLine = True
			self.internalOpenFileFromCmdLine()
		
	def internalOpenFileFromCmdLine(self):
		"""Holt den Bildpfad von der Kommandozeile"""
		if( len(self.cmdLineArgs) > 0 ):
			print "Loading file from command line"
			param = self.cmdLineArgs[0]
			url = QUrl(param)
			if( url.isEmpty() ): return
			localFile = url.toLocalFile()
			if( localFile ):
				self.loadImageFromFile( localFile )
			else:
				self.loadImageFromWeb( url.toString() )
				
	def deleteTempFiles(self):
		"""Löscht alle geöffneten temporären Dateien"""
		if( len(self.tempFiles) == 0): return
		print "Deleting temporary files"
		for tmpFile in self.tempFiles:
			try:
				os.remove(tmpFile[0])
			except:
				continue
				
	class ImageLoader(Thread):
		def __init__(self, displayArea):
			self.displayArea = displayArea
			Thread.__init__(self)
		
		def setSource(self, source):
			pass
		
		def run(self):
			pass



# Die Anwendung nur starten, wenn die Source nicht als Modul geladen wird
if( __name__ == "__main__" ):
	app = QApplication(sys.argv)

	# Siehe: http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/qtranslator.html
	translator = QTranslator()
	translator.load("qt_de", "/usr/share/qt4/translations")
	app.installTranslator(translator)

	form = ApplicationWindow()
	form.show()
	form.update()
	
	form.loadInitialImage()

	sys.exit(app.exec_())

