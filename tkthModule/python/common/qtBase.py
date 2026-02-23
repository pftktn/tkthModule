import pathlib
import json
import math

import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI

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


class tkhkMainWindow(QtWidgets.QMainWindow) : 
  __mayaMainWinPtr = None
  __mayaMainWin = None
  __ui = None
  @property
  def ui(self) : return self.__ui
  
  def __init__(self, uiObject, objectName, parent=None, *args, **kwargs) : 
    if parent is None : 
      self.__mayaMainWinPtr = OpenMayaUI.MQtUtil.mainWindow()
      self.__mayaMainWin = shiboken.wrapInstance(int(self.__mayaMainWinPtr), QtWidgets.QWidget)
      parent = self.__mayaMainWin
    super(tkhkMainWindow, self).__init__(*args, parent=parent, **kwargs)
    self.setWindowFlags(QtCore.Qt.Window)
    self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    self.__ui = uiObject
    self.__ui.setupUi(self, objectName)
    


class tkhkMainWindowSimple(QtWidgets.QMainWindow) : 
  __mayaMainWinPtr = None
  __mayaMainWin = None
  
  def __init__(self, parent=None, *args, **kwargs) : 
    if parent is None : 
      self.__mayaMainWinPtr = OpenMayaUI.MQtUtil.mainWindow()
      self.__mayaMainWin = shiboken.wrapInstance(int(self.__mayaMainWinPtr), QtWidgets.QWidget)
      parent = self.__mayaMainWin
    super(tkhkMainWindowSimple, self).__init__(*args, parent=parent, **kwargs)
    self.setWindowFlags(QtCore.Qt.Window)
    self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    
