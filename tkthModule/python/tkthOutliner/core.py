import pathlib
import json
import math
import time

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
from common.qtUtil import * 
from common.jsonUtil import *

import common.qtBase as qtBase

from tkthOutliner.tabOutliner import *
from tkthOutliner.tabConnect import *
from tkthOutliner.tabLog import *


def logMessage(inWgt:QtWidgets.QWidget, inMsg) : 
  wgt = inWgt
  while wgt is not None and type(wgt) != mainWindow : 
    try : 
      wgt = wgt.parent()
    except : 
      pass
  if wgt is not None : wgt.tabLog.logMessage(inMsg)


class mainWindow(qtBase.tkhkMainWindowSimple) : 
  __tabOutliner = None
  @property
  def tabOutliner(self) : return self.__tabOutliner
  __tabConnect = None
  @property
  def tabConnect(self) : return self.__tabConnect
  __tabLog = None
  @property
  def tabLog(self) : return self.__tabLog
  __tabList = None
  
  def __init__(self, parent=None, *args, **kwargs) : 
    super(mainWindow, self).__init__(parent=parent, *args, **kwargs)
    self.setupUI()

    self.currentChanged_tab(0)
    self.tabWidget.currentChanged.connect(self.currentChanged_tab)

    self.show()
    self.addMayaCallback()
    # self.addJobList(u'addTimerCallback', OpenMaya.MTimerMessage.addTimerCallback(1.0, mainWindow.timerCallback, clientData=self))

  def reloadContent(self) : 
    if self.__tabList is not None : 
      for tab in self.__tabList : 
        tab.reloadContent()
  
  def currentChanged_tab(self, inIdx) : 
    sbBar = self.statusBar()
    if sbBar is not None : sbBar.clearMessage()

    if self.__tabList is not None : 
      currTab = self.tabWidget.currentWidget()
      tabName = currTab.objectName()

      for tab in self.__tabList : 
        if tab.objectName() == tabName : tab.activate()
        else : tab.deactivate()

  def addMayaCallback(self) :
    self.removeMayaCallback()
    msgLst = list()
    msgLst.append(OpenMaya.MSceneMessage.kAfterCreateReferenceAndRecordEdits)
    msgLst.append(OpenMaya.MSceneMessage.kAfterImportReference)
    msgLst.append(OpenMaya.MSceneMessage.kAfterImport)
    msgLst.append(OpenMaya.MSceneMessage.kAfterLoadReferenceAndRecordEdits)
    msgLst.append(OpenMaya.MSceneMessage.kAfterNew)
    msgLst.append(OpenMaya.MSceneMessage.kAfterOpen)
    msgLst.append(OpenMaya.MSceneMessage.kAfterRemoveReference)
    msgLst.append(OpenMaya.MSceneMessage.kAfterUnloadReference)
    for msg in msgLst :
      self.addJobList(str(msg), OpenMaya.MSceneMessage.addCallback(msg, mainWindow.afterFileCallback, clientData=self))
    
    msgLst = list()
    msgLst.append(OpenMaya.MSceneMessage.kBeforeCreateReferenceAndRecordEdits)
    msgLst.append(OpenMaya.MSceneMessage.kBeforeCreateReference)
    msgLst.append(OpenMaya.MSceneMessage.kBeforeImport)
    msgLst.append(OpenMaya.MSceneMessage.kBeforeImportReference)
    msgLst.append(OpenMaya.MSceneMessage.kBeforeLoadReference)
    msgLst.append(OpenMaya.MSceneMessage.kBeforeNew)
    msgLst.append(OpenMaya.MSceneMessage.kBeforeOpen)
    msgLst.append(OpenMaya.MSceneMessage.kBeforeReference)
    msgLst.append(OpenMaya.MSceneMessage.kBeforeRemoveReference)
    msgLst.append(OpenMaya.MSceneMessage.kBeforeUnloadReference)
    for msg in msgLst :
      self.addJobList(str(msg), OpenMaya.MSceneMessage.addCallback(msg, mainWindow.beforeFileCallback, clientData=self))
    
    msgLst = list()
    msgLst.append(OpenMaya.MSceneMessage.kAfterExport)
    msgLst.append(OpenMaya.MSceneMessage.kAfterExportReference)
    msgLst.append(OpenMaya.MSceneMessage.kAfterSave)
    for msg in msgLst :
      self.addJobList(str(msg), OpenMaya.MSceneMessage.addCallback(msg, mainWindow.afterSaveExportCallback, clientData=self))

    msgLst = list()
    msgLst.append(OpenMaya.MSceneMessage.kBeforeExport)
    msgLst.append(OpenMaya.MSceneMessage.kBeforeExportReference)
    msgLst.append(OpenMaya.MSceneMessage.kBeforeSave)
    for msg in msgLst :
      self.addJobList(str(msg), OpenMaya.MSceneMessage.addCallback(msg, mainWindow.beforeSaveExportCallback, clientData=self))
    
    mainWindow.addNodeChangeCallback(self)
  
  @staticmethod
  def afterSaveExportCallback(userData) : userData.addNodeChangeCallback(userData)
  @staticmethod
  def beforeSaveExportCallback(userData) : userData.removeNodeChangeCallback(userData)
  
  @staticmethod
  def afterFileCallback(userData) : 
    userData.removeNodeChangeCallback(userData)
    userData.reloadContent()
    userData.addNodeChangeCallback(userData)

  @staticmethod
  def beforeFileCallback(userData) : 
    userData.removeNodeChangeCallback(userData)

  @staticmethod
  def addNodeChangeCallback(userData) : 
    userData.addJobList(u'addNodeAddedCallback', OpenMaya.MDGMessage.addNodeAddedCallback(mainWindow.nodeAddedCallback, u'dependNode', clientData=userData))
    userData.addJobList(u'addNodeRemovedCallback', OpenMaya.MDGMessage.addNodeRemovedCallback(mainWindow.nodeRemovedCallback, u'dependNode', clientData=userData))
    userData.addJobList(u'addNameChangedCallback', OpenMaya.MNodeMessage.addNameChangedCallback(OpenMaya.MObject.kNullObj, mainWindow.nameChangedCallback, clientData=userData))
    userData.addJobList(u'addParentAddedCallback', OpenMaya.MDagMessage.addParentAddedCallback(mainWindow.parentAddedCallback, clientData=userData))

  @staticmethod
  def removeNodeChangeCallback(userData) : 
    userData.timerCallback_addTime = None
    userData.timerCallback_lastTime = None
    userData.nodeChangedList = None
    userData.removeMayaCallback(messageList=[u'addNodeAddedCallback', u'addNodeRemovedCallback', u'addNameChangedCallback', u'addParentAddedCallback', u'addTimerCallback'])

  enNodeAdded = 0
  enNodeRemoved = 1
  enNodeRenamed = 2
  enNodeParentAdded = 3
  timerCallback_addTime = None
  timerCallback_lastTime = None
  nodeChangedList = None
  @staticmethod
  def nodeAddedCallback(inNd, inUD) : 
    # self.addJobList(u'addTimerCallback', OpenMaya.MTimerMessage.addTimerCallback(1.0, mainWindow.timerCallback, clientData=self))
    fn = OpenMaya.MFnDependencyNode(inNd)
    uuid = UniqueMayaUUID(fn)
    if inUD.timerCallback_addTime is None : 
      inUD.timerCallback_addTime = time.time()
      inUD.timerCallback_lastTime = inUD.timerCallback_addTime
      inUD.addJobList(u'addTimerCallback', OpenMaya.MTimerMessage.addTimerCallback(1.0, mainWindow.timerCallback, clientData=inUD))
      inUD.nodeChangedList = [ ( mainWindow.enNodeAdded, (uuid, inNd) ) ]
    elif inUD.nodeChangedList is not None : 
      inUD.timerCallback_lastTime = time.time()
      inUD.nodeChangedList.append(( mainWindow.enNodeAdded, (uuid, inNd) ))

  @staticmethod
  def nodeRemovedCallback(inNd, inUD) : 
    fn = OpenMaya.MFnDependencyNode(inNd)
    uuid = UniqueMayaUUID(fn)
    if inUD.timerCallback_addTime is None : 
      inUD.timerCallback_addTime = time.time()
      inUD.timerCallback_lastTime = inUD.timerCallback_addTime
      inUD.addJobList(u'addTimerCallback', OpenMaya.MTimerMessage.addTimerCallback(1.0, mainWindow.timerCallback, clientData=inUD))
      inUD.nodeChangedList = [ ( mainWindow.enNodeRemoved, uuid ) ]
    elif inUD.nodeChangedList is not None : 
      inUD.timerCallback_lastTime = time.time()
      for idx, nd in enumerate(inUD.nodeChangedList) :
        if nd[0] == mainWindow.enNodeAdded and nd[1][0] == uuid : 
          inUD.nodeChangedList.pop(idx)
          return
      inUD.nodeChangedList.append(( mainWindow.enNodeRemoved, uuid ))
  
  @staticmethod
  def nameChangedCallback(inNd, inStr, inUD) : 
    '''
    print(u'nameChangedCallback:' + str(inNd) + u':' + str(inStr) + u':' + str(inUD))
    fn = OpenMaya.MFnDependencyNode(inNd)
    print(fn.absoluteName())
    '''
    fn = OpenMaya.MFnDependencyNode(inNd)
    uuid = UniqueMayaUUID(fn)
    newNm = fn.absoluteName()
    if inUD.timerCallback_addTime is None : 
      inUD.timerCallback_addTime = time.time()
      inUD.timerCallback_lastTime = inUD.timerCallback_addTime
      inUD.addJobList(u'addTimerCallback', OpenMaya.MTimerMessage.addTimerCallback(1.0, mainWindow.timerCallback, clientData=inUD))
      inUD.nodeChangedList = [ ( mainWindow.enNodeRenamed, (uuid, newNm) ) ]
    elif inUD.nodeChangedList is not None : 
      inUD.timerCallback_lastTime = time.time()
      inUD.nodeChangedList.append(( mainWindow.enNodeRenamed, (uuid, newNm) ))

  @staticmethod
  def parentAddedCallback(inCh, inPrt, inUD) :  # SDK Documentでは、typedef void(* 	MMessageParentChildFunction) (MDagMessage::DagMessage msgType, MDagPath &child, MDagPath &parent, void *clientData)
    fnCh = OpenMaya.MFnDagNode(inCh)
    uuidCh = UniqueMayaUUID(fnCh)
    uuidPrt = None
    if inPrt.length() > 0 : 
      fnPrt = OpenMaya.MFnDagNode(inPrt)
      uuidPrt = UniqueMayaUUID(fnPrt)
    if inUD.timerCallback_addTime is None : 
      inUD.timerCallback_addTime = time.time()
      inUD.timerCallback_lastTime = inUD.timerCallback_addTime
      inUD.addJobList(u'addTimerCallback', OpenMaya.MTimerMessage.addTimerCallback(1.0, mainWindow.timerCallback, clientData=inUD))
      inUD.nodeChangedList = [ ( mainWindow.enNodeParentAdded, (uuidCh, uuidPrt) ) ]
    elif inUD.nodeChangedList is not None : 
      inUD.timerCallback_lastTime = time.time()
      inUD.nodeChangedList.append(( mainWindow.enNodeParentAdded, (uuidCh, uuidPrt) ))

  @staticmethod
  def timerCallback(inUD, elaspsedT, lastT) : # SDK Documentでは、typedef void(* MElapsedTimeFunction) (float elapsedTime, float lastTime, void *clientData)
    # print(u'timerCallback:' + str(inUD.timerCallback_addTime))
    if inUD.timerCallback_addTime is None : return
    if inUD.timerCallback_addTime != inUD.timerCallback_lastTime : 
      inUD.timerCallback_addTime = inUD.timerCallback_lastTime
      return
    inUD.removeMayaCallback(messageList=[u'addTimerCallback'])

    nodeChangedList = inUD.nodeChangedList
    inUD.timerCallback_addTime = None
    inUD.timerCallback_lastTime = None
    inUD.nodeChangedList = None
    # fnRefList = getMFnReferenceList()

    for nd in nodeChangedList : 
      if nd[0] == mainWindow.enNodeAdded : 
        try : 
          fn = OpenMaya.MFnDagNode(nd[1][1])
          # uuid = UniqueMayaUUID(fn, fnRefList=fnRefList)
          itm = inUD.tabOutliner.treeWidget.findByUUID(nd[1][0])
          if itm is None : 
            dgp = fn.getPath()
            inUD.tabOutliner.treeWidget.addMDagPath(dgp)
          else : 
            logMessage(inUD, u'NodeAdded:exist itemMDagPath:' + fn.fullPathName() + u':' + str(itm))
          continue
        except : 
          pass
        try : 
          fn = OpenMaya.MFnDependencyNode(nd[1][1])
          # uuid = UniqueMayaUUID(fn, fnRefList=fnRefList)
          itm = inUD.tabOutliner.treeWidget.findByUUID(nd[1][0])
          if itm is None : 
            inUD.tabOutliner.treeWidget.addMObject(nd[1][1])
          else : 
            logMessage(inUD, u'NodeAdded:exist itemMObject:' + fn.absoluteName() + u':' + str(itm))
          continue
        except : 
          pass
      elif nd[0] == mainWindow.enNodeRemoved : 
        itm = inUD.tabOutliner.treeWidget.findByUUID(nd[1])
        if itm is None : 
          logMessage(inUD, u'NodeRemoved:not exist item:' + str((nd[1])))
          continue
        prtItm = itm.parent()
        if prtItm is None : 
          itmIdx = inUD.tabOutliner.treeWidget.indexOfTopLevelItem(itm)
          if itmIdx >= 0 : inUD.tabOutliner.treeWidget.takeTopLevelItem(itmIdx)
        else : 
          chIdx = prtItm.indexOfChild(itm)
          if chIdx >= 0 : prtItm.takeChild(chIdx)
      elif nd[0] == mainWindow.enNodeRenamed : 
        (uuid, newNm) = nd[1]
        itm = inUD.tabOutliner.treeWidget.findByUUID(uuid)
        if itm is None : 
          logMessage(inUD, u'NodeRenamed:not exist item:' + str((uuid, newNm)))
          continue
        if itm.itemType == item.itemBase.enMDagPath : 
          itm.setText(0, newNm[1:])
        elif itm.itemType == item.itemBase.enMObject : 
          itm.setText(0, newNm)
      elif nd[0] == mainWindow.enNodeParentAdded : 
        (uuidCh, uuidPrt) = nd[1]
        chItm = inUD.tabOutliner.treeWidget.findByUUID(uuidCh)
        if chItm is None : 
          logMessage(inUD, u'NodeParentAdded:not exist child item:' + str((uuidCh, uuidPrt)))
          continue
        prtItm = chItm.parent()
        if prtItm is not None : 
          chIdx = prtItm.indexOfChild(chItm)
          prtItm.takeChild(chIdx)
        else : 
          topIdx = inUD.tabOutliner.treeWidget.indexOfTopLevelItem(chItm)
          inUD.tabOutliner.treeWidget.takeTopLevelItem(topIdx)

        if uuidPrt is not None : 
          prtItm = inUD.tabOutliner.treeWidget.findByUUID(uuidPrt)
          if prtItm is None : 
            logMessage(inUD, u'NodeParentAdded:not exist parent item:' + str((uuidCh, uuidPrt)))
            continue
          prtItm.addChild(chItm)
        else : 
          inUD.tabOutliner.treeWidget.insertTopLevelItemBySorted(chItm)

  
  __jobList = None
  def addJobList(self, inMsg, inId) : 
    if self.__jobList is None : self.__jobList = list()
    self.__jobList.append((inMsg, inId))
    logMessage(self, u'addCallback:' + str((len(self.__jobList), inMsg, inId)))

  def removeMayaCallback(self, messageList=None) :
    if self.__jobList is not None : 
      if messageList is None : 
        for jobMsgId in self.__jobList : 
          OpenMaya.MMessage.removeCallback(jobMsgId[1])
          logMessage(self, u'removeCallback:' + str(jobMsgId))
        self.__jobList = list()
      else : 
        for msg in messageList : 
          for idx, jobMsgId in enumerate(self.__jobList) : 
            if jobMsgId[0] == msg : 
              OpenMaya.MMessage.removeCallback(jobMsgId[1])
              logMessage(self, u'removeCallback:' + str(jobMsgId))
              self.__jobList.pop(idx)
              break

  def closeEvent(self, event):
    self.removeMayaCallback()
    return super().closeEvent(event)

  # def logMessage(self, inMsg) : self.tabLog.logMessage(inMsg)

  def setupUI(self) : 
    self.setObjectName(uniqueWidgetName(u'tkthOutliner'))
    self.resize(480, 800)
    self.centralwidget_root = QtWidgets.QWidget(self)
    self.centralwidget_root.setObjectName(u'centralwidget_root')
    self.verticalLayout_root = QtWidgets.QVBoxLayout(self.centralwidget_root)
    self.verticalLayout_root.setObjectName(u'verticalLayout_root')
    self.tabWidget = QtWidgets.QTabWidget(self.centralwidget_root)
    self.tabWidget.setObjectName(u'tabWidget')
    self.verticalLayout_root.addWidget(self.tabWidget)

    self.__tabList = list()
    self.__tabOutliner = tabOutliner(self)
    self.__tabList.append(self.tabOutliner)
    self.__tabConnect = tabConnect(self)
    self.__tabList.append(self.tabConnect)
    self.__tabLog = tabLog(self)
    self.__tabList.append(self.tabLog)

    self.setCentralWidget(self.centralwidget_root)
    self.statusbar = QtWidgets.QStatusBar(self)
    self.statusbar.setObjectName(u"statusbar")
    self.setStatusBar(self.statusbar)

    self.menuBar = QtWidgets.QMenuBar(self)
    self.menuBar.setObjectName(u"menuBar")
    self.menuBar.setGeometry(QtCore.QRect(0, 0, 480, 21))
    self.setMenuBar(self.menuBar)

    QtCore.QMetaObject.connectSlotsByName(self)
    self.setWindowTitle(u"tkthOutliner")
    self.tabWidget.setCurrentIndex(0)

