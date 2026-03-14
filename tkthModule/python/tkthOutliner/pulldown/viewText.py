import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as OpenMaya

try :
  import PySide6.QtCore as QtCore
  import PySide6.QtGui as QtGui
  import PySide6.QtWidgets as QtWidgets
  import PySide6.QtUiTools as QtUiTools
  import shiboken6 as shiboken
except :
  import PySide2.QtCore as QtCore
  import PySide2.QtGui as QtGui
  import PySide2.QtWidgets as QtWidgets
  import PySide2.QtUiTools as QtUiTools
  import shiboken2 as shiboken

from common.apiUtil import *
from common.cmdsUtil import *

import tkthOutliner.item as item

import tkthOutliner.pulldown.base as base



class textViewWindow(QtWidgets.QMainWindow) :
  def __init__(self, inParent, inName, inTxt) :
    super(textViewWindow, self).__init__(parent=inParent)
    self.init(inName, inTxt)

  __textView = None
  def init(self, inName, inExp) :
    self.resize(400, 400)
    self.setWindowTitle(inName)
    self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    self.setCentralWidget(QtWidgets.QWidget(self))
    self.__textView = QtWidgets.QPlainTextEdit(self.centralWidget())
    self.__textView.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
    self.__textView.setReadOnly(True)
    self.__textView.clear()
    self.__textView.appendPlainText(inExp)
    self.show()

  margin = 5
  def resizeEvent(self, inEv) : 
    super(textViewWindow, self).resizeEvent(inEv)
    cwRect = self.centralWidget().geometry()
    cwWidth = cwRect.width()
    cwHeight = cwRect.height()
    if cwWidth < 200 : cwWidth = 200
    if cwHeight < 200 : cwHeight = 200
    cwWidth = cwWidth - textViewWindow.margin * 2
    cwBottom = cwHeight - textViewWindow.margin * 2

    self.__textView.setGeometry(textViewWindow.margin, textViewWindow.margin, cwWidth, cwBottom)

  def closeEvent(self, inEvent) : 
    inEvent.accept()



class pullDownViewText(base.pullDownBase) : 
  def __init__(self, inMenu, inItmLst, inCore) : 
    super().__init__(inMenu, inItmLst, inCore)
    bfLst = self.filterByTypeIdList(self.bifrostTypeIdList)
    expLst = self.filterByHasFnList([ OpenMaya.MFn.kExpression ])
    if len(expLst) + len(bfLst) == 0 : raise Exception()
    if len(bfLst) > 0 : 
      act = self.menu.addAction(u'open in bifrost')
      act.triggered.connect(self.openInBifrost)
    act = self.menu.addAction(u'view as text')
    act.triggered.connect(self.viewAsText)
      
  def openInBifrost(self) : 
    mel.eval(u'openBifrostGraphEditorFromSelection;')

  def viewAsText(self) : 
    expItmLst = self.filterByHasFnList([ OpenMaya.MFn.kExpression ])
    cnt = 10
    for expItm in expItmLst :
      try :
        if cnt == 0 : break
        exp = cmds.expression(expItm.itemUniqueName, query=True, string=True)
        textViewWindow(self.core, u'expression:' + expItm.itemUniqueName, exp)
      except Exception as e :
        self.logMessage(str(e))
      finally :
        cnt = cnt - 1

    bfItmLst = self.filterByTypeIdList(self.bifrostTypeIdList)
    for bfItm in bfItmLst :
      try :
        if cnt == 0 : break
        txt = cmds.getAttr(plugName(bfItm.itemUniqueName, u'saveContainerToJSON'))
        textViewWindow(self.core, u'bifrost:' + bfItm.itemUniqueName, txt)
      except Exception as e :
        self.logMessage(str(e))
      finally :
        cnt = cnt - 1

