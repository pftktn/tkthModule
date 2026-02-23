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

from common.apiUtil import *
from common.cmdsUtil import *
from common.qtUtil import * 

import tkthOutliner.tabCommon as tabCommon


class tabLog(tabCommon.tabCommon) : 
  __plainTextEdit_log:QtWidgets.QPlainTextEdit = None
  @property
  def plainTextEdit_log(self) : return self.__plainTextEdit_log

  withPrint = False

  __tabActive = False
  __messageCountMax = 1024
  __messageList = None
  def logMessage(self, inMsg) : 
    if len(self.__messageList) > self.__messageCountMax : 
      self.__messageList = self.__messageList[self.__messageCountMax//4:]
      if self.__tabActive : 
        self.plainTextEdit_log.clear()
        txt = u''
        for msg in self.__messageList : 
          txt = txt + u'\n' + msg
        self.plainTextEdit_log.setPlainText(txt[1:])
    self.__messageList.append(inMsg)
    if self.withPrint : print(inMsg)
    if self.__tabActive : self.plainTextEdit_log.appendPlainText(inMsg)

  def activate(self) : 
    self.__tabActive = True
    txt = u''
    for msg in self.__messageList : 
      txt = txt + u'\n' + msg
    self.plainTextEdit_log.setPlainText(txt[1:])

  def deactivate(self) : 
    self.__tabActive = False
    self.plainTextEdit_log.clear()

  def setupUI(self) : 
    self.verticalLayout_log = QtWidgets.QVBoxLayout(self)
    self.verticalLayout_log.setObjectName(u"verticalLayout_log")
    self.__plainTextEdit_log = QtWidgets.QPlainTextEdit(self)
    self.__plainTextEdit_log.setObjectName(u"plainTextEdit_log")
    self.plainTextEdit_log.setUndoRedoEnabled(False)
    self.plainTextEdit_log.setReadOnly(True)

    self.verticalLayout_log.addWidget(self.plainTextEdit_log)

    tabIdx = self.core.tabWidget.addTab(self, u"log")
    self.core.tabWidget.setTabText(tabIdx, u'log')
    self.plainTextEdit_log.clear()
    self.__messageList = list()

  def __init__(self, core=None) : 
    super().__init__(core=core, objectName=u'tab_log')
    self.setupUI()
    self.__tabActive = False
