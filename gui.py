#!/usr/bin/python

import sys
from PyQt4 import QtGui

class Icon(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Icon')
        self.setWindowIcon(QtGui.QIcon('icons/icon.gif'))

	self.setToolTip('This is a <b>QWidget</b> widget')
        QtGui.QToolTip.setFont(QtGui.QFont('OldEnglish', 10))



app = QtGui.QApplication(sys.argv)

widget = QtGui.QWidget()
#widget.resize(250, 150)
#widget.setWindowTitle('Hallo, Welt')
#widget.show()

icon = Icon()
icon.show()


sys.exit(app.exec_())

