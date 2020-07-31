from maya import OpenMayaUI as omui
from PySide2 import QtGui, QtCore, QtWidgets, QtUiTools
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtUiTools import *
from PySide2.QtWidgets import *
from shiboken2 import wrapInstance

import sys
import AnimationTransfer

def getMayaWin():
	mayaWinPtr = omui.MQtUtil.mainWindow( )
	mayaWin = wrapInstance( long( mayaWinPtr ), QWidget )


def loadUI( path ):
	loader = QUiLoader()
	uiFile = QFile( path )
	
	dirIconShapes = ""
	buff = None
	
	if uiFile.exists():
		dirIconShapes = path
		uiFile.open( QFile.ReadOnly )
		
		buff = QByteArray( uiFile.readAll() )
		uiFile.close()
	else:
		print "UI file missing! Exiting..."
		exit(-1)
		
	fixXML( path, buff )
	qbuff = QBuffer()
	qbuff.open( QBuffer.ReadOnly | QBuffer.WriteOnly )
	qbuff.write( buff )
	qbuff.seek( 0 )
	ui = loader.load( qbuff, parentWidget = getMayaWin() )
	ui.path = path
	
	return ui


def fixXML( path, qbyteArray ):
	# first replace forward slashes for backslashes
	if path[-1] != '/':
		path += '/'
	path = path.replace( "/", "\\" )
	
	# construct whole new path with <pixmap> at the begining
	tempArr = QByteArray( "<pixmap>" + path + "\\" )
	
	# search for the word <pixmap>
	lastPos = qbyteArray.indexOf( "<pixmap>", 0 )
	while lastPos != -1:
		qbyteArray.replace( lastPos, len( "<pixmap>" ), tempArr )
		lastPos = qbyteArray.indexOf( "<pixmap>", lastPos + 1 )
	return


class UIController:
	def __init__( self, ui ):
		# Connect each signal to it's slot one by one
		ui.transferButton.clicked.connect(self.transferButtonClicked)
		ui.loadFromSelectionButton.clicked.connect(self.getRoots)
		ui.targetDeleteButton.clicked.connect(self.deleteTargetSelection)
		ui.targetUpButton.clicked.connect(self.moveUpTarget)
		ui.targetDownButton.clicked.connect(self.moveDownTarget)
		ui.sourceDeleteButton.clicked.connect(self.deleteSourceSelection)
		ui.sourceUpButton.clicked.connect(self.moveUpSource)
		ui.sourceDownButton.clicked.connect(self.moveDownSource)

		ui.sourceRootWindow.returnPressed.connect(self.fillSourceList)
		ui.targetRootWindow.returnPressed.connect(self.fillTargetList)
		
		self.ui = ui
		ui.setWindowFlags( Qt.WindowStaysOnTopHint )
		ui.show()
		
	def deleteSourceSelection(self):
		self.ui.sourceList.takeItem(self.ui.sourceList.currentRow())

	def deleteTargetSelection(self):
		self.ui.targetList.takeItem(self.ui.targetList.currentRow())

	def moveUpSource(self):
		selectedRow = self.ui.sourceList.currentRow()
		selectedItem = self.ui.sourceList.takeItem(selectedRow)
		self.ui.sourceList.insertItem(selectedRow-1, selectedItem)
		self.ui.sourceList.setCurrentRow(selectedRow-1)

	def moveDownSource(self):
		selectedRow = self.ui.sourceList.currentRow()
		selectedItem = self.ui.sourceList.takeItem(selectedRow)
		self.ui.sourceList.insertItem(selectedRow + 1, selectedItem)
		self.ui.sourceList.setCurrentRow(selectedRow + 1)

	def moveUpTarget(self):
		selectedRow = self.ui.targetList.currentRow()
		selectedItem = self.ui.targetList.takeItem(selectedRow)
		self.ui.targetList.insertItem(selectedRow-1, selectedItem)
		self.ui.targetList.setCurrentRow(selectedRow-1)

	def moveDownTarget(self):
		selectedRow = self.ui.targetList.currentRow()
		selectedItem = self.ui.targetList.takeItem(selectedRow)
		self.ui.targetList.insertItem(selectedRow + 1, selectedItem)
		self.ui.targetList.setCurrentRow(selectedRow + 1)

	def fillTargetList(self):
		targetList = AnimationTransfer.getJointList(str(self.ui.targetRootWindow.text()))
		for items in targetList:
			item = QListWidgetItem(str(items))
			self.ui.targetList.addItem(item)

	def fillSourceList(self):
		sourceList = AnimationTransfer.getJointList(str(self.ui.sourceRootWindow.text()))
		for items in sourceList:
			item = QListWidgetItem(str(items))
			self.ui.sourceList.addItem(item)

	def getRoots(self):
		roots = AnimationTransfer.getRoot()
		self.ui.sourceRootWindow.setText(str(roots[0]))
		self.ui.targetRootWindow.setText(str(roots[1]))
		self.fillTargetList()
		self.fillSourceList()

	def transferButtonClicked(self):
		sourceList = [self.ui.sourceList.item(i).text() for i in range(self.ui.sourceList.count())]
		targetList = [self.ui.targetList.item(i).text() for i in range(self.ui.targetList.count())]
		AnimationTransfer.transfer(sourceList, targetList)
		print "# Animation Transfer Done! #"