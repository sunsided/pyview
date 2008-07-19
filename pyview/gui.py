# -*- coding: utf-8 -*-
#
# Kudos:
#		http://www.webappers.com/2008/02/12/webappers-released-free-web-application-icons-set/
#		http://lists.kde.org/?l=pykde&m=114235100819012&w=2
#
# Disable pylint spaces/tabs warning
# pylint: disable-msg=W0312
# pylint: disable-msg=W0511

import sys, os, Image
from threading import Thread
from PyQt4.QtGui import QApplication, QMessageBox, QMainWindow, QWidget, QPainter, QPalette, \
						QSizePolicy, QImage, QIcon, QScrollArea, QActionGroup, QAction, QFileDialog, \
						QMessageBox, QDesktopWidget
from PyQt4.QtCore import SIGNAL, SLOT, QTranslator, QVariant, QUrl, QStringList, QSize, QByteArray
from PyQt4.QtOpenGL import QGLFormat, QGLWidget
from optparse import OptionParser

class DisplayArea(QWidget):
	"""Arthur-Basierte DisplayArea"""
	# Member
	image = None
	firstImage = True
	imageSize = QSize(0, 0)
	zoomFactor = 1.0
	
	# Konstanten
	MAX_ZOOM = 10.0
	MIN_ZOOM = 0.1
	ZOOM_STEP = 0.1
	
	def __init__(self, parent=None):
		"""Initialisiert die Klasse"""
		QWidget.__init__(self, parent)
		
		self.setBackgroundRole(QPalette.Base)
		self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
		
		# Variablen setzen
		self.PILimage = None
		self.image = QImage()

	def __del__(self):
		self.PILimage = None
		if( self.image ):
			self.image.__del__()

	def isOpenGL(self):
		"""Gibt an, ob diese DisplayArea OpenGL nutzt"""
		return False

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
		
		self.imageSize = QSize( self.PILimage.size[0], self.PILimage.size[1] )
		self.setMinimumSize( self.imageSize.width()*self.zoomFactor, self.imageSize.height()*self.zoomFactor )
		retval = self.image.loadFromData(QByteArray(PILstring))
		self.repaint()
		return retval

	def paintEvent(self, event):
		"""Zeichnet das Bild erneut"""
		if(self.image == None): return
		painter = QPainter(self)
		
		# Nicht über den Rand malen
		painter.setClipping(True)
		painter.setClipRect(self.rect())
		
		# X-Offset
		offset_x = 0
		zoomed_width = self.imageSize.width()*self.zoomFactor
		
		# Nur beim Verkleinern zentrieren
		if( self.width() > zoomed_width ):
			offset_x = (self.width() - zoomed_width) / 2
		
		# Y-Offset
		offset_y = 0
		zoomed_height = self.imageSize.height()*self.zoomFactor
		
		# Nur beim Verkleinern zentrieren
		if( self.height() > zoomed_height ):
			offset_y = (self.height() - zoomed_height) / 2
		
		painter.save()
		painter.translate(offset_x, offset_y)
		painter.scale(self.zoomFactor, self.zoomFactor)
		
		#exposedRect = painter.matrix().inverted()[0].mapRect(event.rect()).adjusted(-1, -1, 1, 1)
		painter.drawImage(0,0,self.image)
		#painter.drawImage(exposedRect, self.image, exposedRect)
		#painter.drawImage(self.parent().rect(), self.image, exposedRect)
		painter.restore()

	def setZoomFactor(self, factor):
		"""Setzt den Zoom-Faktor des Bildes"""
		if( self.zoomFactor == factor ): return
		
		self.zoomFactor = factor
		self.emit(SIGNAL("zoomFactorChanged(float)"), factor)
		
		w = self.imageSize.width() * self.zoomFactor
		h = self.imageSize.height() * self.zoomFactor
		self.setMinimumSize(w, h)
		self.resize(w, h)
		
		self.repaint()
#		
#		self.adjustScrollBar(QScrollArea(self.parent()).horizontalScrollBar(), factor)
#		self.adjustScrollBar(QScrollArea(self.parent()).verticalScrollBar(), factor)
#
#	def adjustScrollBar(self, scrollbar, factor):
#		print scrollbar.value(), scrollbar.pageStep()
#	
#		scrollbar.setValue(int(factor*scrollbar.value()) + ((factor-1) * scrollbar.pageStep()/2))
	
	def zoomIn(self):
		"""Zoomt um einen festen Betrag ein"""
		newZoomFactor = self.zoomFactor + self.ZOOM_STEP
		if( newZoomFactor >= self.MAX_ZOOM ):
			newZoomFactor = self.MAX_ZOOM
		self.setZoomFactor(newZoomFactor)

	def zoomOut(self):
		"""Zoomt um einen festen Betrag aus"""
		newZoomFactor = self.zoomFactor - self.ZOOM_STEP
		if( newZoomFactor <= self.MIN_ZOOM ):
			newZoomFactor = self.MIN_ZOOM
		self.setZoomFactor(newZoomFactor)

	def zoomFull(self):
		"""Setzt den Zoom auf 100%"""
		self.setZoomFactor(1.0)



class GLDisplayArea(QGLWidget, DisplayArea):
	"""OpenGL-Basierte DisplayArea"""
	
	def __init__(self, parent=None):
		"""Initialisiert die Klasse"""
		QGLWidget.__init__(self, parent)
		DisplayArea.__init__(self, parent)
	
	def isOpenGL(self):
		"""Gibt an, ob diese DisplayArea OpenGL nutzt"""
		return True



class ImageSource:
	"""Aufzählungen der Bildquellen"""
	def __init__(self):
		pass
	UNKNOWN = 0
	LOCALFILE = 1
	REMOTEFILE = 2



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
		#self.__class__.dragEnterEvent = self.dragEnterEvent
		self.__class__.dropEvent = self.dragDropEvent
			
		# Das Display-Widget
		openGLsupport = QGLFormat.hasOpenGL()
		if( self.cmdLineOptions.openGL and openGLsupport):
			print "Using OpenGL engine."
			self.displayArea = GLDisplayArea() #DisplayArea()
		else:
			if( openGLsupport ):
				print "Not using OpenGL engine."
			else:
				print "Not using OpenGL engine: OpenGL rendering not supported."
			self.displayArea = DisplayArea()
		
		# Scroll Area
		self.scrollArea = QScrollArea(self)
		# TODO: Benutzerdefinierte Farbe
		self.scrollArea.setBackgroundRole(QPalette.Dark)
		#self.scrollArea.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
		#self.scrollArea.setWidgetResizable(True)
		self.scrollArea.setWidget(self.displayArea)
		self.setCentralWidget(self.scrollArea)

		# Menü erstellen
		self.buildMenu()
		
		# Weitere Hooks
		self.connect(self, SIGNAL("imageLoaded(bool)"), self.notifyFileLoaded)
		self.connect(self, SIGNAL("imageLoading(bool, int, bool)"), self.notifyFileLoading)
		self.connect(self.scrollArea.verticalScrollBar(), SIGNAL("valueChanged(int)"), self.imageAreaScrolled)
		self.connect(self.scrollArea.verticalScrollBar(), SIGNAL("valueChanged(int)"), self.imageAreaScrolled)
		
	def imageAreaScrolled(self, value):
		self.displayArea.repaint()
		
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
		
		menuViewZoomIn = QAction(u"Ver&größern", self)
		menuViewZoomIn.setShortcut("+")
		menuViewZoomIn.setStatusTip(u"Vergrößert die Ansicht")
		menuViewZoomIn.connect(menuViewZoomIn, SIGNAL("triggered()"), self.displayArea.zoomIn)

		menuViewZoomOut = QAction(u"Ver&kleinern", self)
		menuViewZoomOut.setShortcut("-")
		menuViewZoomOut.setStatusTip(u"Verkleinert die Ansicht")
		menuViewZoomOut.connect(menuViewZoomOut, SIGNAL("triggered()"), self.displayArea.zoomOut)

		menuViewZoomFull = QAction(u"&Originalgröße", self)
		menuViewZoomFull.setShortcut("STRG+H")
		menuViewZoomFull.setStatusTip("Zoomt die Ansicht auf 100%")
		menuViewZoomFull.connect(menuViewZoomFull, SIGNAL("triggered()"), self.displayArea.zoomFull)
		
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
	
		view.addSeparator()
		self.addAction(menuViewZoomIn)
		view.addAction(menuViewZoomIn)
		self.addAction(menuViewZoomOut)
		view.addAction(menuViewZoomOut)
		self.addAction(menuViewZoomFull)
		view.addAction(menuViewZoomFull)
	
	def trigger(self, action):
		print "Selected Menu: " + action.property("tag").toString()
	
	def resizeEvent(self, event):
		self.displayArea.update()
	
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
	
	def notifyFileLoaded(self, state):
		"""Wird gerufen, wenn eine Datei geladen wurde"""	
		print "File loaded."
		if not state: return
		filename = os.path.basename(str(self.lastOpenedFile))
		self.setWindowTitle(filename + " - " + self.APPNAME)
		self.setStatusTip("Datei geladen.")
		
	def getUserHomeDir(self):
		"""Holt das Home-Verzeichnis des aktuellen Nutzers"""
		# TODO: Windows-sicher machen
		return str(os.environ.get('HOME'))

	def getStartDir(self):
		"""Liefert das Startverzeichnis der Anwendung, wie es über die 
		Kommandozeile gesetzt wurde"""
		startDir = str(self.cmdLineOptions.directory)
		if( os.path.isdir(startDir) ):
			startDir = os.path.normpath(startDir)
		else:
			startDir = os.path.dirname(startDir)
		return str(startDir)

	def getUserPicturesDir(self):
		"""Holt den Pfad des Benutzer-Bilderverzeichnisses"""
		# http://win32com.goermezer.de/content/view/191/188/
		# http://www.blueskyonmars.com/2005/08/05/finding-a-users-my-documents-folder-on-windows/
		# TODO: Erweitern auf Windows, MacOS, ...
		user_home_dir = self.getUserHomeDir()
		conf_home = user_home_dir + "/.config"
		if os.environ.has_key("XDG_CONFIG_HOME"):
			conf_home = os.environ["XDG_CONFIG_HOME"]
		
		userdirs_path = str(conf_home + "/user-dirs.dirs")
		if os.path.exists(userdirs_path) and os.path.isfile(userdirs_path):
			userdirs_file = open(userdirs_path, "r")
			lines = userdirs_file.readlines()
			userdirs_file.close()
			for line in lines:
				if line.startswith("XDG_PICTURES_DIR"):
					pictures_dir = line.split("=", 1)[1].strip()
					if( pictures_dir.startswith("\"")):
						pictures_dir = pictures_dir[1:-1]
					pictures_dir = pictures_dir.replace("$HOME", user_home_dir)
					pictures_dir = pictures_dir.replace("~/", user_home_dir + "/")
					return str(pictures_dir)
		return None

	def openImageDialog(self):
		"""Zeigt den \"Bild Laden\"-Dialog an"""
	
		# Startverzeichnis holen
		startDir = self.getStartDir()
		if not startDir:
			startDir = self.getUserPicturesDir()
		if not startDir:
			startDir = self.getUserHomeDir()
		if( self.lastOpenedFile != None and not self.isTempFile(self.lastOpenedFile) ):
			startDir = os.path.dirname(str(self.lastOpenedFile))
		
		# Dateifilter definieren
		# TODO: Sinnvolle Lösung finden, in aller Regel durch eine Liste bekannter Typen
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
		self.emit(SIGNAL("imageLoading(bool,int,bool)"), True, ImageSource.LOCALFILE, False)
		return self.internalLoadImageFromFile(fileName, ImageSource.LOCALFILE)
			
	def internalLoadImageFromFile(self, fileName, source):
		"""Lädt ein Bild, dessen Pfad bekannt ist"""

		success = False
		try:
			success = self.displayArea.loadFromFile(str(fileName))
			#self.displayArea.update()
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
		self.emit(SIGNAL("imageLoading(bool,int,bool)"), True, ImageSource.REMOTEFILE, False)
		
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
					
					self.emit(SIGNAL("imageLoading(bool,int,bool)"), False, ImageSource.REMOTEFILE, False)
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
			success = self.internalLoadImageFromFile( tempFileName, ImageSource.REMOTEFILE )
		
		return True

	def isTempFile(self, fileName):
		"""Teste, ob eine Datei eine Temporärdatei ist"""
		if( len(self.tempFiles) == 0): return False
		# TODO: Auf Dictionary umstellen
		for tmpFile in self.tempFiles:
			if( tmpFile[0] == fileName ): return True
		return False

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
		cmdOptParser.add_option("-d", "--directory", dest="directory", default=None,
								help="start in DIRECTORY. If an image is loaded through the command line, the directory of the image is used instead", 
								metavar="DIRECTORY")
		cmdOptParser.add_option("--no-opengl", dest="openGL", 
								action="store_false", default=True,
								help="don't use the OpenGL render engine'")

		
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
