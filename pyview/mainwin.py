# -*- coding: utf-8 -*-
#
# Kudos:
#		http://www.webappers.com/2008/02/12/webappers-released-free-web-application-icons-set/
#		http://lists.kde.org/?l=pykde&m=114235100819012&w=2
#
# Disable pylint spaces/tabs warning
# pylint: disable-msg=W0312
# pylint: disable-msg=W0511

import sys, os
from threading import Thread
from PyQt4.QtGui import QMessageBox, QMainWindow, QPalette, \
						QIcon, QScrollArea, QActionGroup, QAction, QFileDialog, \
						QMessageBox, QDesktopWidget
from PyQt4.QtCore import SIGNAL, SLOT, QVariant, QUrl, QStringList, QObject
from PyQt4.QtOpenGL import QGLFormat
from optparse import OptionParser
from DisplayArea import DisplayArea
from GLDisplayArea import GLDisplayArea
from ImageSource import ImageSource


class ApplicationWindow(QMainWindow):
	"""ApplicationWindow
	
	This is pyview's main window."""
	
	# Constants
	APPNAME = None
	APPVERSION = None

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
		
		# Initialize app name and version
		self.APPVERSION = "0.1"
		self.APPNAME = self.tr("Image viewer")
		
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
			print("Using OpenGL engine.")
			self.displayArea = GLDisplayArea() #DisplayArea()
		else:
			if( openGLsupport ):
				print("Not using OpenGL engine.")
			else:
				print("Not using OpenGL engine: OpenGL rendering not supported.")
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
		"""Creates the menus and applies the shortcuts"""
		
		# Menüzeile
		# http://zetcode.com/tutorials/pyqt4/menusandtoolbars/
		# http://lists.trolltech.com/qt-interest/2007-07/thread00771-0.html
		menuBar = self.menuBar()
		
		# Menüeintrag zum Laden eines Bildes
		menuFileOpen = QAction(QIcon("icons/Load.png"), self.tr("&Open ..."), self)
		menuFileOpen.setShortcut(self.tr("O", "File|Open"))
		menuFileOpen.setStatusTip(self.tr("Opens a picture"))
		self.connect(menuFileOpen, SIGNAL("triggered()"), self.openImageDialog)
		
		# Menüeintrag zum Laden eines Bildes
		menuFileReopen = QAction(QIcon("icons/Load.png"), self.tr("&Reload picture"), self)
		menuFileReopen.setShortcut(self.tr("SHIFT+R", "File|Reload"))
		menuFileReopen.setStatusTip(self.tr("Reloads the last opened picture"))
		menuFileReopen.setEnabled(False)
		self.connect(menuFileReopen, SIGNAL("triggered()"), self.reOpenImage)
		self.connect(self, SIGNAL("imageLoaded(bool)"), menuFileReopen, SLOT("setEnabled(bool)"))
		
		# Menüeintrag zum Beenden
		menuFileExit = QAction(QIcon("icons/exit.gif"), self.tr("&Quit"), self)
		menuFileExit.setShortcut(self.tr("ESC", "File|Quit"))
		menuFileExit.setStatusTip(self.tr("Quits the application"))
		self.connect(menuFileExit, SIGNAL("triggered()"), SLOT("close()"))
		
		# Dateimenü
		file = menuBar.addMenu(self.tr("&File"))	
		self.addAction(menuFileOpen)
		file.addAction(menuFileOpen)
		self.addAction(menuFileReopen)
		file.addAction(menuFileReopen)
		file.addSeparator()
		self.addAction(menuFileExit)
		file.addAction(menuFileExit)
		
		# Vollbild-Menüeintrag
		menuViewFullScreen = QAction(QIcon("icons/Loading.png"), self.tr("&Fullscreen"), self)
		menuViewFullScreen.setShortcut(self.tr("RETURN", "View|Fullscreen"))
		menuViewFullScreen.setStatusTip(self.tr("Switches to fullscreen mode"))
		menuViewFullScreen.setCheckable(True)
		menuViewFullScreen.setChecked(bool(self.cmdLineOptions.fullScreen))
		menuViewFullScreen.connect(menuViewFullScreen, SIGNAL("triggered()"), self.toggleFullScreen)
		
		menuViewZoomIn = QAction(self.tr("Zoom &in"), self)
		menuViewZoomIn.setShortcut(self.tr("+", "View|Zoom in"))
		menuViewZoomIn.setStatusTip(self.tr("Zooms in"))
		menuViewZoomIn.connect(menuViewZoomIn, SIGNAL("triggered()"), self.displayArea.zoomIn)

		menuViewZoomOut = QAction(self.tr("Zoom &out"), self)
		menuViewZoomOut.setShortcut(self.tr("-", "View|Zoom out"))
		menuViewZoomOut.setStatusTip(self.tr("Zooms out"))
		menuViewZoomOut.connect(menuViewZoomOut, SIGNAL("triggered()"), self.displayArea.zoomOut)

		menuViewZoomFull = QAction(self.tr("&Original size"), self)
		menuViewZoomFull.setShortcut(self.tr("STRG+H", "View|Sizes"))
		menuViewZoomFull.setStatusTip(self.tr("Zooms the view 100%"))
		menuViewZoomFull.connect(menuViewZoomFull, SIGNAL("triggered()"), self.displayArea.zoomFull)
		
		# Anzeigemodi
		menuViewWindowToImageSize = QAction(self.tr("Scale window to picture (1:1, &recommended)"), self)
		menuViewWindowToImageSize.setCheckable(True)
		menuViewWindowToImageSize.setProperty("tag", QVariant("WindowToImageSize"))
		menuViewWindowToImageSize.setStatusTip(self.tr("Scales the window to fit the image size"))
		
		menuViewSizeToFit = QAction(self.tr("Scale picture to window"), self)
		menuViewSizeToFit.setCheckable(True)
		menuViewSizeToFit.setProperty("tag", QVariant("SizeToFit"))
		menuViewSizeToFit.setStatusTip(self.tr("Scales the picture to fit the window size"))

		menuViewSizeLargeToFit = QAction(self.tr("Scale large images only"), self)
		menuViewSizeLargeToFit.setCheckable(True)
		menuViewSizeLargeToFit.setProperty("tag", QVariant("SizeLargeToFit"))
		menuViewSizeLargeToFit.setStatusTip(self.tr("Only scales large images to fit the window size"))
		
		menuViewFitToScreen = QAction(self.tr("Scale window/picture to fit the screen"), self)
		menuViewFitToScreen.setCheckable(True)
		menuViewFitToScreen.setShortcut("F")
		menuViewFitToScreen.setProperty("tag", QVariant("FitToScreen"))
		menuViewFitToScreen.setStatusTip(self.tr("Scales the window or picture to fit the screen size"))
		
		menuViewFitLargeToScreen = QAction(self.tr("Scale large images to screen only"), self)
		menuViewFitLargeToScreen.setCheckable(True)
		menuViewFitLargeToScreen.setProperty("tag", QVariant("FitLargeToScreen"))
		menuViewFitLargeToScreen.setStatusTip(self.tr("Scales large images to the screen size only"))
		
		menuViewFitToScreenWidth = QAction(self.tr("Scale images to screen width"), self)
		menuViewFitToScreenWidth.setCheckable(True)
		menuViewWindowToImageSize.setProperty("tag", QVariant("FitToScreenWidth"))
		menuViewFitToScreenWidth.setStatusTip(self.tr("Scales the images to fit the screen width"))
		
		menuViewFitToScreenHeight = QAction(self.tr("Scale images to screen height"), self)
		menuViewFitToScreenHeight.setCheckable(True)
		menuViewFitToScreenHeight.setProperty("tag", QVariant("FitToScreenHeight"))
		menuViewFitToScreenHeight.setStatusTip(self.tr("Scales images to fit the screen height"))
		
		menuViewNoFit = QAction(self.tr("Do&n't scale"), self)
		menuViewNoFit.setCheckable(True)
		menuViewNoFit.setProperty("tag", QVariant("NoFit"))
		menuViewNoFit.setStatusTip(self.tr("Images are not scaled"))
		
		# Ansichtsmenü
		view = menuBar.addMenu(self.tr("&View"))
		self.addAction(menuViewFullScreen)
		view.addAction(menuViewFullScreen)
		
		# Anzeige-OptionsMenü
		viewOptionsWindowed = view.addMenu(self.tr("&Display options (Window mode)"))
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
		"""Switches between fullscreen and normal view"""
	
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
		"""Called when a files is about to load"""
		if( source == 0 or source == 1 ):
			if( loading ):
				print "Loading file ..."
				self.setStatusTip(self.tr("Loading file ..."))
			else:
				if( success ):
					print "Done loading of file."
					self.setStatusTip(self.tr("File loaded."))
				else:
					print "Canceled loading of file."
					self.setStatusTip(self.tr("Loading of file canceled."))
		else:
			if( loading ):
				print "Loading remote file..."
				self.setStatusTip(self.tr("Loading remote file ..."))
			else:
				if( success ):
					print "Done loading remote file."
					self.setStatusTip(self.tr("Remote file loaded."))
				else:
					print "Canceled loading remote file."
					self.setStatusTip(self.tr("Loading of remote file canceled."))
	
	def notifyFileLoaded(self, state):
		"""Called when a file is loaded"""	
		print "File loaded."
		if not state: return
		filename = os.path.basename(str(self.lastOpenedFile))
		self.setWindowTitle(filename + " - " + self.APPNAME)
		self.setStatusTip("Datei geladen.")
		
	def getUserHomeDir(self):
		"""Gets the user's home directory"""
		# TODO: Windows-sicher machen
		return str(os.environ.get('HOME'))

	def getStartDir(self):
		"""Gets the directory from which pyview was started"""
		startDir = str(self.cmdLineOptions.directory)
		if( os.path.isdir(startDir) ):
			startDir = os.path.normpath(startDir)
		else:
			startDir = os.path.dirname(startDir)
		return str(startDir)

	def getUserPicturesDir(self):
		"""Gets the user's Pictures folder"""
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
		"""Displays the \"Open Picture\" dialog"""
	
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
		filters << self.tr("Pictures", "File filter") + " (*.jpg *.gif *.png *.xpm)"
		filters << self.tr("All files") + " (*)"
		
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
		"""Reopens the last file"""
	
		if( self.lastOpenedFile == None ):
			print "Could not open last image: No known last image."
			return
		self.loadImageFromFile(self.lastOpenedFile)

	def loadImageFromFile(self, fileName):
		"""Loads a file with a known path"""
		self.emit(SIGNAL("imageLoading(bool,int,bool)"), True, ImageSource.LOCALFILE, False)
		return self.internalLoadImageFromFile(fileName, ImageSource.LOCALFILE)
			
	def internalLoadImageFromFile(self, fileName, source):
		"""Loads a file with a known path.
		This is an internal function."""

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
		"""Tests the mimetype of the file.
		Returns True if the mime type can be handled and false otherwise"""
		# TODO: Sinnvolle Implementierung auf Basis tatsächlich möglicher Dinge
		mimetype = str(mimetype).lower()
		if( mimetype.startswith("image/")): return True
		if( mimetype.startswith("application/octet-stream") ): return True
		return False
	
	def loadImageFromWeb(self, url):
		"""Loads a picture from the web"""
		self.emit(SIGNAL("imageLoading(bool,int,bool)"), True, ImageSource.REMOTEFILE, False)
		
		# TODO: Testen, ob die Datei evtl. bereits heruntergeladen wurde (Temporärdateicache)
		
		# http://docs.python.org/lib/module-urllib2.html
		import urllib2, tempfile
		image = None
		tempFile = None 
		tempFileName = None
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
			self.internalLoadImageFromFile( tempFileName, ImageSource.REMOTEFILE )
		
		return True

	def isTempFile(self, fileName):
		"""Tests if a file is a temporary file"""
		if( len(self.tempFiles) == 0): return False
		# TODO: Auf Dictionary umstellen
		for tmpFile in self.tempFiles:
			if( tmpFile[0] == fileName ): return True
		return False

	def closeEvent(self, event):
		"""Called when the application is about to close"""

		if( self.askBeforeClosing ):
			reply = QMessageBox.question(self, self.tr("Close the program?"), self.tr("Are you sure?"), QMessageBox.Yes, QMessageBox.No)
	
			if reply == QMessageBox.Yes:
				event.accept()
			else:
				event.ignore()
				return
		
		# Aufräumen
		if( self.cmdLineOptions.tempClean ): self.deleteTempFiles()

	def center(self):
		"""Centers the window on the screen"""
	
		screen = QDesktopWidget().screenGeometry()
		size =  self.geometry()
		self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
		
	def setFitToWindow(self, state):
		"""Switches the display modes"""
	
		print "setFitToWindow called: " + str(state)
		if( state == False):
			self.scrollArea.setWidgetResizable(False)
			#self.displayArea.resize(self.displayArea.image.size())
			self.displayArea.adjustSize()
		else:
			self.scrollArea.setWidgetResizable(True)
	
	def dragEnterEvent(self, event):
		"""Drag&Drop event: Element enters the window"""
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
		"""Drag&Drop event: Item has been dropped"""
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
		"""Creates the command line options parser"""
		# http://docs.python.org/lib/module-optparse.html
		# http://optik.sourceforge.net/doc/1.5/tutorial.html
		# http://optik.sourceforge.net/doc/1.5/reference.html

		versionString = self.APPNAME + " v" + self.APPVERSION
		usageString = "%prog [Optionen] [Dateiname]"
		descString = self.tr("A simple picture viewer that wants to be like IrfanView")
		
		# Parser erstellen
		cmdOptParser = OptionParser(usage = usageString, 
									version = versionString,
									description = descString)
		
		# Optionen definieren
		cmdOptParser.add_option("-f", "--fullscreen", dest="fullScreen", 
								action="store_true", default=False,
								help=self.tr("start in fullscreen mode"))
		cmdOptParser.add_option("--no-tempclean", dest="tempClean", 
								action="store_false", default=True,
								help=self.tr("don't delete cached files when exiting"))
		cmdOptParser.add_option("-d", "--directory", dest="directory", default=None,
								help=self.tr("start in DIRECTORY. If an image is loaded through the command line, the directory of the image is used instead"), 
								metavar="DIRECTORY")
		cmdOptParser.add_option("--no-opengl", dest="openGL", 
								action="store_false", default=True,
								help=self.tr("don't use the OpenGL render engine'"))

		
		# Parsen
		(self.cmdLineOptions, self.cmdLineArgs)	= cmdOptParser.parse_args()	
		return self.cmdLineArgs
		
	def loadInitialImage(self):
		"""Loads the picture specified on the command line"""
	
		# Kommandozeilenoptionen, Teil 2
		if( not self.loadedFromCommandLine ):
			self.loadedFromCommandLine = True
			self.internalOpenFileFromCmdLine()
		
	def internalOpenFileFromCmdLine(self):
		"""Gets the path of the picture specified on the command line"""
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
		"""Deletes all registered temporary files"""
		if( len(self.tempFiles) == 0): return
		print "Deleting temporary files"
		for tmpFile in self.tempFiles:
			try:
				os.remove(tmpFile[0])
			except:
				continue
				