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
from common.jsonUtil import *

from tkthOutliner.core import *

import tkthOutliner.tabCommon as tabCommon


class itemPlugBase(QtWidgets.QTreeWidgetItem) : 
  #def logMessage(self, inMsg) : 
  #  try : 
  #    coreObj = self.getCoreObject()
  #    if coreObj is not None : coreObj.logMessage(inMsg)
  #  except : pass

  __plugName = None
  @property
  def plugName(self) : return self.__plugName

  def getMPlug(self) : 
    plg = getMPlugByName(self.plugName)
    if plg is None or plg.isNull : return None
    else : return plg

  @property
  def itemName(self) : return self.text(0)

  __valueType = None
  @property
  def valueType(self) : return self.__valueType

  def setVisibleByName(self, inNm) : 
    v = False
    try : 
      self.text(0).index(inNm)
      v = True
    except : 
      pass
    chCnt = self.childCount()
    if v : 
      self.setVisibleRecurse(True)
      return True
    
    chCnt = self.childCount()
    for chIdx in range(chCnt) : 
      chItm = self.child(chIdx)
      chV = chItm.setVisibleByName(inNm)
      if chV : v = True

    if v : self.setHidden(False)
    else : self.setHidden(True)
    return v

  def setVisibleRecurse(self, inV) : 
    if inV : self.setHidden(False)
    else : self.setHidden(True)
    chCnt = self.childCount()
    for chIdx in range(chCnt) : 
      chItm = self.child(chIdx)
      chItm.setVisibleRecurse(inV)

  def isVisibleRecurse(self) : 
    itm = self
    while itm is not None : 
      if itm.isHidden() : return False
      itm = itm.parent()
    return True

  def setExpandedRecurse(self, inExp) : 
    itm = self.parent()
    while itm is not None : 
      itm.setExpanded(inExp)
      itm = itm.parent()

  def updateConnectable(self, inSrcPlg, inSrcValType) : 
    fnt = self.font(0)
    fnt.setStrikeOut(False)
    fnt.setItalic(False)
    fnt.setBold(False)
    flg = QtCore.Qt.ItemFlag.ItemIsEnabled
    prtExp = curExp = False

    if inSrcPlg is not None and inSrcPlg.isCompound : 
      if isBifrost_RiggingModuleOutputs(inSrcPlg) : 
        inSrcValType = enATBifrostRiggingModuleOutputs
      # if isBifrost_RiggingModuleInputs(inSrcPlg) : 
      #   inSrcValType = enATBifrostRiggingModuleInputs

    plg = self.getMPlug()
    if plg is not None and plg.isArray == False : 
      curSrcPlg = plg.source()
      if curSrcPlg is not None and curSrcPlg.isNull == False : 
        if inSrcPlg is not None and curSrcPlg == inSrcPlg : 
          fnt.setItalic(True)
          fnt.setBold(True)
          prtExp = True
        else : 
          fnt.setItalic(True)
    if inSrcValType is not None : 
      valTp = self.valueType
      if plg is not None and isBifrost_RiggingModuleOutputs(plg) : 
        valTp = enATBifrostRiggingModuleOutputs
      if isConnectable(inSrcValType, valTp) : 
        flg = flg | QtCore.Qt.ItemFlag.ItemIsSelectable
        prtExp = True
      else : 
        fnt.setStrikeOut(True)
      
    self.setFont(0, fnt)
    self.setFlags(flg)
    
    chCnt = self.childCount()
    for chIdx in range(chCnt) : 
      chItm = self.child(chIdx)
      chExp = chItm.updateConnectable(inSrcPlg, inSrcValType)
      if chExp : curExp = chExp

    self.setExpanded(curExp)
    return prtExp

  def __init__(self, plugName=None, valueType=enATInvalid, text=None, itemFlags=QtCore.Qt.ItemFlag.ItemIsEnabled|QtCore.Qt.ItemFlag.ItemIsSelectable):
    super(__class__, self).__init__()
    self.__plugName = plugName
    self.__valueType = valueType
    self.setText(0, text)
    self.setFlags(itemFlags)

  def getStatusBarMessage(self) : return None

  def source(self) : 
    plg = self.getMPlug()
    if plg is None : return None
    srcPlg = plg.source()
    if srcPlg is None or srcPlg.isNull : return None
    else : return srcPlg

  def connect(self, inSrcItm) : return False

  def addPortInput(self, inSrcItm) : return None
  def addPortOutput(self, inDstItm) : return None

  def getCoreObject(self) : 
    prt = self.treeWidget().parent()
    while prt is not None : 
      if prt.objectName().startswith(u'tkthOutliner') : 
        return prt
      prt = prt.parent()
    return None


class itemPlug(itemPlugBase) : 
  def __init__(self, inPlg:OpenMaya.MPlug, itemFlags=QtCore.Qt.ItemFlag.ItemIsEnabled|QtCore.Qt.ItemFlag.ItemIsSelectable):
    plgNm = inPlg.name()
    valTp = getPlugValueType(inPlg)
    lst = plgNm.split(u'.')
    attrNm = lst[-1]
    txt = attrNm + u':' + getValueTypeString(valTp)
    if attrNm in [ u'scale', u'shear', u'rotateAxis', u'rotate', u'rotateOrder', u'translate', u'jointOrient', u'inverseScale', u'offsetParentMatrix', u'worldMatrix', u'matrix', u'bifrostPort' ] : txt = txt + u' #srt'
    super(__class__, self).__init__(plugName=plgNm, valueType=valTp, text=txt, itemFlags=itemFlags)

    if inPlg.isArray : 
      self.setFlags(itemFlags & QtCore.Qt.ItemFlag.ItemIsEnabled)
      try :
        elmItmLst = list()
        lmtCnt = 100
        elmCnt = inPlg.evaluateNumElements()
        for elmIdx in range(elmCnt) : 
          if lmtCnt == 0 : break
          lmtCnt = lmtCnt - 1
          elmPlg = inPlg.elementByPhysicalIndex(elmIdx)
          elmItmLst.append(itemPlug(elmPlg, itemFlags=itemFlags))
      except : 
        elmItmLst = list()
        lmtCnt = 100
        logIdxLst = inPlg.getExistingArrayAttributeIndices()
        for logIdx in logIdxLst : 
          if lmtCnt == 0 : break
          lmtCnt = lmtCnt - 1
          elmPlg = inPlg.elementByLogicalIndex(logIdx)
          elmItmLst.append(itemPlug(elmPlg, itemFlags=itemFlags))
      for elmItm in elmItmLst : self.addChild(elmItm)
    elif inPlg.isCompound : 
      chCnt = inPlg.numChildren()
      for chIdx in range(chCnt) : 
        chPlg = inPlg.child(chIdx)
        chItm = itemPlug(chPlg, itemFlags=itemFlags)
        self.addChild(chItm)

  def getStatusBarMessage(self) : 
    plg = getMPlugByName(self.plugName)
    if plg is None or plg.isNull : return u'null'
    if plg.isArray : 
      elmCnt = plg.evaluateNumElements()
      return u'count=' + str(elmCnt)
    return u'value=' + str(getPlugValue(plg, valueType=self.valueType))

  def connect(self, inSrcItm):
    dstPlg = self.getMPlug()
    srcPlg = inSrcItm.getMPlug()
    curSrcPlg = self.source()
    if curSrcPlg is not None : 
      if curSrcPlg == srcPlg : 
        msg = u'disconnect source:' + self.plugName
        btn = QtWidgets.QMessageBox.question(self.treeWidget(), msg, msg)
        if btn == QtWidgets.QMessageBox.StandardButton.No : return False
        srcPlg = None
      else : 
        msg = u'replace source:' + self.plugName
        btn = QtWidgets.QMessageBox.question(self.treeWidget(), msg, msg)
        if btn == QtWidgets.QMessageBox.StandardButton.No : return False
        # if srcPlg is None and inSrcItm.valueType == enATBifrostPortOut : srcPlg = inSrcItm.addPortOutput(self)

    if srcPlg is not None : 
      try : 
        cmds.undoInfo(chunkName=u'connect', openChunk=True)
        if curSrcPlg is not None : cmds.disconnectAttr(curSrcPlg.name(), dstPlg.name())
        cmds.connectAttr(srcPlg.name(), dstPlg.name(), force=True)
        logMessage(self.treeWidget(), u'connectAttr ' + srcPlg.name() + u' ' + dstPlg.name())
      finally : 
        cmds.undoInfo(closeChunk=True)
    else : 
      if inSrcItm.valueType == enATBifrostPortOut : 
        try : 
          cmds.undoInfo(chunkName=u'connect bifrost output', openChunk=True)
          if curSrcPlg is not None : 
            cmds.disconnectAttr(curSrcPlg.name(), dstPlg.name())
            logMessage(self.treeWidget(), u'disconnectAttr ' + curSrcPlg.name() + u' ' + dstPlg.name())
          srcPlg = inSrcItm.addPortOutput(self)
          if srcPlg is not None : 
            cmds.connectAttr(srcPlg.name(), dstPlg.name(), force=True)
            logMessage(self.treeWidget(), u'connectAttr ' + srcPlg.name() + u' ' + dstPlg.name())
        finally : 
          cmds.undoInfo(closeChunk=True)
      elif curSrcPlg is not None : 
        try : 
          cmds.undoInfo(chunkName=u'disconnect', openChunk=True)
          cmds.disconnectAttr(curSrcPlg.name(), dstPlg.name())
          logMessage(self.treeWidget(), u'disconnectAttr ' + curSrcPlg.name() + u' ' + dstPlg.name())
        finally : 
          cmds.undoInfo(closeChunk=True)
      else : 
        return False

    return True

class itemBifrostPlug(itemPlugBase) : 
  def __init__(self, inObj:OpenMaya.MObject, inIsSource, itemFlags=QtCore.Qt.ItemFlag.ItemIsEnabled|QtCore.Qt.ItemFlag.ItemIsSelectable):
    fn = OpenMaya.MFnDependencyNode(inObj)
    plgNm = fn.absoluteName() + u'.<bifrostPort>'
    txt = u'bifrostPort'
    if inIsSource : 
      valTp = enATBifrostPortOut
      txt = txt + u':output'
    else : 
      valTp = enATBifrostPortIn
      txt = txt + u':input'
    super(__class__, self).__init__(plugName=plgNm, valueType=valTp, text=txt, itemFlags=itemFlags)

  @staticmethod
  def portName(inPlgNm) : 
    lst = inPlgNm.split(u'.')
    nd = getShortName(lst[0])
    attr = lst[-1]
    mtch = re.search(u'\\[\\d+\\]$', attr)
    while mtch is not None : 
      idxLen = len(mtch.group(0))
      attr = attr[:-idxLen]
      mtch = re.search(u'\\[\\d+\\]$', attr)
    return nd + u'_' + attr

  def addPortInput(self, inSrcItm) : 
    newPort = None
    try :
      portTp = getBiflostType(inSrcItm.valueType)
      if portTp is None : 
        srcPlg = inSrcItm.getMPlug()
        if srcPlg is not None and isBifrost_RiggingModuleOutputs(srcPlg) : 
          portTp = getBiflostType(enATBifrostRiggingModuleOutputs)
        if portTp is None : return None
      portNm = itemBifrostPlug.portName(inSrcItm.plugName)
      
      lst = self.plugName.split(u'.')
      ndNm = lst[0]
      oldPortLst = cmds.vnnCompound(ndNm, u'/', inputPort=True, listPorts=True)
      if oldPortLst is None : oldPortLst = []
      cmds.vnnCompound(ndNm, u'/', createInputPort=[portNm, portTp])
      logMessage(self.treeWidget(), u'vnnCompound -createInputPort ' + portNm + u' ' + portTp + u' / ' + ndNm)
      newPortLst = cmds.vnnCompound(ndNm, u'/', inputPort=True, listPorts=True)
      newPortLst.reverse()
      for pt in newPortLst : 
        if pt in oldPortLst :
          pass
        else :
          newPort = pt
          break
    except :
      pass
    if newPort is not None : return getMPlugByName(ndNm + u'.' + newPort)
    else : return None
  
  def addPortOutput(self, inDstItm) : 
    newPort = None
    try :
      portTp = getBiflostType(inDstItm.valueType)
      if portTp is None : return None
      portNm = itemBifrostPlug.portName(inDstItm.plugName)
      
      lst = self.plugName.split(u'.')
      ndNm = lst[0]
      oldPortLst = cmds.vnnCompound(ndNm, u'/', outputPort=True, listPorts=True)
      if oldPortLst is None : oldPortLst = []
      cmds.vnnCompound(ndNm, u'/', createOutputPort=[portNm, portTp])
      logMessage(self.treeWidget(), u'vnnCompound -createOutputPort ' + portNm + u' ' + portTp + u' / ' + ndNm)
      newPortLst = cmds.vnnCompound(ndNm, u'/', outputPort=True, listPorts=True)
      newPortLst.reverse()
      for pt in newPortLst : 
        if pt in oldPortLst :
          pass
        else :
          newPort = pt
          break
    except :
      pass
    if newPort is not None : return getMPlugByName(ndNm + u'.' + newPort)
    else : return None

  def connect(self, inSrcItm):
    srcPlg = inSrcItm.getMPlug()
    if srcPlg is None : return False
    dstPlg = self.addPortInput(inSrcItm)
    if dstPlg is None : return False
    cmds.connectAttr(srcPlg.name(), dstPlg.name(), force=True)
    logMessage(self.treeWidget(), u'connectAttr ' + srcPlg.name() + u' ' + dstPlg.name())
    return True


class tabConnect(tabCommon.tabCommon) : 
  __comboBox_nodeSource:QtWidgets.QComboBox = None
  @property
  def comboBox_nodeSource(self) : return self.__comboBox_nodeSource
  __lineEdit_plugFilterSource:QtWidgets.QLineEdit = None
  @property
  def lineEdit_plugFilterSource(self) : return self.__lineEdit_plugFilterSource
  __pushButton_plugFilter:QtWidgets.QPushButton = None
  @property
  def pushButton_plugFilter(self) : return self.__pushButton_plugFilter
  __treeWidget_plugSource:QtWidgets.QTreeWidget = None
  @property
  def treeWidget_plugSource(self) : return self.__treeWidget_plugSource

  __comboBox_nodeDestination:QtWidgets.QComboBox = None
  @property
  def comboBox_nodeDestination(self) : return self.__comboBox_nodeDestination
  __lineEdit_plugFilterDestination:QtWidgets.QLineEdit = None
  @property
  def lineEdit_plugFilterDestination(self) : return self.__lineEdit_plugFilterDestination
  __pushButton_swapSourceDestination:QtWidgets.QPushButton = None
  @property
  def pushButton_swapSourceDestination(self) : return self.__pushButton_swapSourceDestination
  __treeWidget_plugDestination:QtWidgets.QTreeWidget = None
  @property
  def treeWidget_plugDestination(self) : return self.__treeWidget_plugDestination
  
  def setupUI(self) : 
    self.verticalLayout_connect = QtWidgets.QVBoxLayout(self)
    self.verticalLayout_connect.setObjectName(u"verticalLayout_connect")

    self.horizontalLayout_node = QtWidgets.QHBoxLayout()
    self.horizontalLayout_node.setObjectName(u"horizontalLayout_node")

    self.__comboBox_nodeSource = QtWidgets.QComboBox(self)
    self.__comboBox_nodeSource.setObjectName(u"comboBox_nodeSource")
    self.horizontalLayout_node.addWidget(self.comboBox_nodeSource)

    self.__comboBox_nodeDestination = QtWidgets.QComboBox(self)
    self.__comboBox_nodeDestination.setObjectName(u"comboBox_nodeDestination")
    self.horizontalLayout_node.addWidget(self.comboBox_nodeDestination)

    self.verticalLayout_connect.addLayout(self.horizontalLayout_node)

    self.horizontalLayout_filter = QtWidgets.QHBoxLayout()
    self.horizontalLayout_filter.setObjectName(u"horizontalLayout_filter")

    self.__lineEdit_plugFilterSource = QtWidgets.QLineEdit(self)
    self.__lineEdit_plugFilterSource.setObjectName(u"lineEdit_plugFilterSource")
    self.horizontalLayout_filter.addWidget(self.lineEdit_plugFilterSource)

    self.__pushButton_plugFilter = QtWidgets.QPushButton(self)
    self.__pushButton_plugFilter.setObjectName(u"pushButton_plugFilter")
    self.pushButton_plugFilter.setText(u'filter')
    self.horizontalLayout_filter.addWidget(self.pushButton_plugFilter)

    self.__pushButton_swapSourceDestination = QtWidgets.QPushButton(self)
    self.__pushButton_swapSourceDestination.setObjectName(u"pushButton_swapSourceDestination")
    self.pushButton_swapSourceDestination.setText(u'swap')
    self.horizontalLayout_filter.addWidget(self.pushButton_swapSourceDestination)

    self.__lineEdit_plugFilterDestination = QtWidgets.QLineEdit(self)
    self.__lineEdit_plugFilterDestination.setObjectName(u"lineEdit_plugFilterDestination")
    self.horizontalLayout_filter.addWidget(self.lineEdit_plugFilterDestination)

    self.verticalLayout_connect.addLayout(self.horizontalLayout_filter)

    self.horizontalLayout_plug = QtWidgets.QHBoxLayout()
    self.horizontalLayout_plug.setObjectName(u"horizontalLayout_plug")

    self.__treeWidget_plugSource = QtWidgets.QTreeWidget(self)
    qtreewidgetitem1 = QtWidgets.QTreeWidgetItem()
    qtreewidgetitem1.setText(0, u"1")
    self.treeWidget_plugSource.setHeaderItem(qtreewidgetitem1)
    self.treeWidget_plugSource.setObjectName(u"treeWidget_plugSource")
    self.treeWidget_plugSource.header().setVisible(False)
    self.horizontalLayout_plug.addWidget(self.treeWidget_plugSource)

    self.__treeWidget_plugDestination = QtWidgets.QTreeWidget(self)
    qtreewidgetitem2 = QtWidgets.QTreeWidgetItem()
    qtreewidgetitem2.setText(0, u"1")
    self.treeWidget_plugDestination.setHeaderItem(qtreewidgetitem2)
    self.treeWidget_plugDestination.setObjectName(u"treeWidget_plugDestination")
    self.treeWidget_plugDestination.header().setVisible(False)
    self.horizontalLayout_plug.addWidget(self.treeWidget_plugDestination)

    self.verticalLayout_connect.addLayout(self.horizontalLayout_plug)
    tabIdx = self.core.tabWidget.addTab(self, u"connect")
    self.core.tabWidget.setTabText(tabIdx, u'connect')

  def __init__(self, core=None) : 
    super().__init__(core=core, objectName=u'tab_connect')
    self.setupUI()

    self.treeWidget_plugSource.setIndentation(15)
    self.treeWidget_plugSource.itemSelectionChanged.connect(self.itemSelectionChanged_treeWidget_plugSource)
    self.treeWidget_plugSource.itemExpanded.connect(self.itemExpanded_treeWidget_plugSource)

    self.treeWidget_plugDestination.setIndentation(15)
    self.treeWidget_plugDestination.itemSelectionChanged.connect(self.itemSelectionChanged_treeWidget_plugDestination)
    self.treeWidget_plugDestination.itemExpanded.connect(self.itemExpanded_treeWidget_plugDestination)

    self.comboBox_nodeSource.currentIndexChanged.connect(self.currentIndexChanged_nodeSource)
    self.comboBox_nodeDestination.currentIndexChanged.connect(self.currentIndexChanged_nodeDestination)

    self.pushButton_plugFilter.clicked.connect(self.clicked_plugFilter)
    self.pushButton_swapSourceDestination.clicked.connect(self.clicked_swapSourceDestination)
    self.lineEdit_plugFilterSource.editingFinished.connect(self.editingFinished_plugFilterSource)
    self.lineEdit_plugFilterDestination.editingFinished.connect(self.editingFinished_plugFilterDestination)
    
    self.comboBox_nodeSource.clear()
    self.comboBox_nodeDestination.clear()
    self.treeWidget_plugSource.clear()
    self.treeWidget_plugDestination.clear()

  def checkComboBox(self) : 
    rmIdxLst = list()
    cnt = self.comboBox_nodeSource.count()
    for idx in range(cnt) : 
      itmNdNm = self.comboBox_nodeSource.itemData(idx)
      obj = getMDagPathByName(itmNdNm)
      if obj is None : 
        obj = getMObjectByName(itmNdNm)
        if obj is None : rmIdxLst.append(idx)
    rmIdxLst.reverse()
    for rmIdx in rmIdxLst : 
      self.comboBox_nodeSource.removeItem(rmIdx)
      self.comboBox_nodeDestination.removeItem(rmIdx)

  def reloadContent(self) : 
    self.checkComboBox()

  def activate(self) : 
    self.checkComboBox()
    self.currentIndexChanged_nodeSource(0)
    self.currentIndexChanged_nodeDestination(0)
    self.comboBox_nodeSource.currentIndexChanged.connect(self.currentIndexChanged_nodeSource)
    self.comboBox_nodeDestination.currentIndexChanged.connect(self.currentIndexChanged_nodeDestination)
    self.treeWidget_plugSource.currentItemChanged.connect(self.currentItemChanged_treeWidget_plugSource)
    self.treeWidget_plugDestination.currentItemChanged.connect(self.currentItemChanged_treeWidget_plugDestination)

  def deactivate(self) : 
    try : self.comboBox_nodeSource.currentIndexChanged.disconnect()
    except : pass
    try : self.comboBox_nodeDestination.currentIndexChanged.disconnect()
    except : pass
    try : self.treeWidget_plugSource.currentItemChanged.disconnect()
    except : pass
    try : self.treeWidget_plugDestination.currentItemChanged.disconnect()
    except : pass

    self.treeWidget_plugSource.clear()
    self.treeWidget_plugDestination.clear()

  __comboBox_nodeCountMax = 20
  def addNode(self, inNdNm) : 
    sn = getUniqueShortName(inNdNm)
    cnt = self.comboBox_nodeSource.count()
    for idx in range(cnt) : 
      itmNdNm = self.comboBox_nodeSource.itemData(idx)
      if itmNdNm == inNdNm : 
        self.comboBox_nodeSource.removeItem(idx)
        self.comboBox_nodeDestination.removeItem(idx)
        break

    self.comboBox_nodeSource.addItem(sn, userData=inNdNm)
    self.comboBox_nodeDestination.addItem(sn, userData=inNdNm)
    cnt = self.comboBox_nodeSource.count() - self.__comboBox_nodeCountMax
    if cnt > 0 : 
      for idx in range(cnt) : 
        self.comboBox_nodeSource.removeItem(0)
        self.comboBox_nodeDestination.removeItem(0)
    '''
    self.comboBox_nodeSource.insertItem(0, sn, userData=inNdNm)
    self.comboBox_nodeDestination.insertItem(0, sn, userData=inNdNm)
    cnt = self.comboBox_nodeSource.count() - self.__comboBox_nodeCountMax
    if cnt > 0 : 
      for idx in range(cnt) : 
        self.comboBox_nodeSource.removeItem(self.__comboBox_nodeCountMax)
        self.comboBox_nodeDestination.removeItem(self.__comboBox_nodeCountMax)
    '''
    
  def getFn(self, inComboBox:QtWidgets.QComboBox) : 
    ndNm = inComboBox.currentData()
    obj = getMDagPathByName(ndNm)
    if obj is not None : return OpenMaya.MFnDependencyNode(obj.node())
    obj = getMObjectByName(ndNm)
    if obj is not None : return OpenMaya.MFnDependencyNode(obj)
    return None
    
  def currentIndexChanged_nodeSource(self, inIdx) : 
    if self.comboBox_nodeSource.count() == 0 : 
      self.treeWidget_plugSource.clear()
      return
    fn = self.getFn(self.comboBox_nodeSource)
    if fn is not None : 
      self.updatePlugTree(fn, self.treeWidget_plugSource, source=True)
      self.applyPlugFilter(self.treeWidget_plugSource, self.lineEdit_plugFilterSource)
      

  def currentIndexChanged_nodeDestination(self, inIdx) : 
    if self.comboBox_nodeDestination.count() == 0 : 
      self.treeWidget_plugDestination.clear()
      return
    fn = self.getFn(self.comboBox_nodeDestination)
    if fn is not None : 
      self.updatePlugTree(fn, self.treeWidget_plugDestination, source=False)
      self.applyPlugFilter(self.treeWidget_plugDestination, self.lineEdit_plugFilterDestination)
      self.itemSelectionChanged_treeWidget_plugSource()
   
  def updatePlugTree_SourceDestination(self) : 
    selPlgNm = None
    selLst = self.treeWidget_plugSource.selectedItems()
    if selLst is not None and len(selLst) == 1 : selPlgNm = selLst[0].plugName

    self.treeWidget_plugSource.clear()
    self.treeWidget_plugDestination.clear()

    fn = self.getFn(self.comboBox_nodeSource)
    if fn is not None : 
      self.updatePlugTree(fn, self.treeWidget_plugSource, source=True)
      self.applyPlugFilter(self.treeWidget_plugSource, self.lineEdit_plugFilterSource)
      if selPlgNm is not None : 
        que = []
        cnt = self.treeWidget_plugSource.topLevelItemCount()
        for idx in range(cnt) : que.append(self.treeWidget_plugSource.topLevelItem(idx))
        while len(que) > 0 : 
          itm = que.pop(0)
          if itm.isVisibleRecurse() == False : continue
          if itm.plugName == selPlgNm : 
            itm.setExpandedRecurse(True)
            itm.setSelected(True)
            break
          chCnt = itm.childCount()
          for idx in range(chCnt) : que.append(itm.child(idx))

    fn = self.getFn(self.comboBox_nodeDestination)
    if fn is not None : 
      self.updatePlugTree(fn, self.treeWidget_plugDestination, source=False)
      self.applyPlugFilter(self.treeWidget_plugDestination, self.lineEdit_plugFilterDestination)
      self.itemSelectionChanged_treeWidget_plugSource()


  def updatePlugTree(self, inFn:OpenMaya.MFnDependencyNode, inTreeWidget:QtWidgets.QTreeWidget, source=True) : 
    selLst = inTreeWidget.selectedItems()
    if selLst is None or len(selLst) > 0 : inTreeWidget.clearSelection()
    inTreeWidget.clear()
    if source : 
      itemFlags=QtCore.Qt.ItemFlag.ItemIsEnabled|QtCore.Qt.ItemFlag.ItemIsSelectable
    else : 
      itemFlags=QtCore.Qt.ItemFlag.ItemIsEnabled
    # bifrostGraphShape:0x58000360, bifrostBoard:0x80088
    if inFn.typeId.id() in [ 0x58000360, 0x80088 ] : 
      itmPlg = itemBifrostPlug(inFn.object(), source, itemFlags=itemFlags)
      inTreeWidget.addTopLevelItem(itmPlg)
    attrCnt = inFn.attributeCount()
    for idx in range(attrCnt) : 
      attrIdx = attrCnt - 1 - idx
      attrObj = inFn.attribute(attrIdx)
      plg = inFn.findPlug(attrObj, True)
      if plg.isChild : continue
      itmPlg = itemPlug(plg, itemFlags=itemFlags)
      inTreeWidget.addTopLevelItem(itmPlg)
  

  def currentItemChanged_treeWidget_plugSource(self, inCurr, inPrev) : 
    sbBar = self.core.statusBar()
    if sbBar is not None : 
      sbMsg = None
      if inCurr is not None : 
        sbMsg = inCurr.getStatusBarMessage()
      if sbMsg is None : 
        sbBar.clearMessage()
      else : 
        sbBar.showMessage(sbMsg)

  def currentItemChanged_treeWidget_plugDestination(self, inCurr, inPrev) : 
    pass

  def itemSelectionChanged_treeWidget_plugSource(self) : 
    selLst = self.treeWidget_plugDestination.selectedItems()
    if selLst is not None : 
      for selItm in selLst : 
        selItm.setSelected(False)

    cnt = self.treeWidget_plugDestination.topLevelItemCount()
    for idx in range(cnt) : 
      try : 
        dstItm = self.treeWidget_plugDestination.topLevelItem(idx)
        dstItm.updateConnectable(None, None)
      except : 
        logMessage(self, u'itemSelectionChanged_treeWidget_plugSource:' + str(idx) + u':' + dstItm.text(0) + u':' + str(type(dstItm)))

    selLst = self.treeWidget_plugSource.selectedItems()
    if selLst is None or len(selLst) != 1 : return
    srcItm = selLst[0]
    srcPlg = srcItm.getMPlug()
    for idx in range(cnt) : 
      dstItm = self.treeWidget_plugDestination.topLevelItem(idx)
      dstItm.updateConnectable(srcPlg, srcItm.valueType)

  def itemSelectionChanged_treeWidget_plugDestination(self) : 
    selLst = self.treeWidget_plugDestination.selectedItems()
    if selLst is None or len(selLst) != 1 : return
    # self.treeWidget_plugDestination.clearSelection()
    selLst[0].setSelected(False)
    dstItm = selLst[0]

    selLst = self.treeWidget_plugSource.selectedItems()
    if selLst is None or len(selLst) != 1 : return
    srcItm = selLst[0]

    dstItm.connect(srcItm)

    self.updatePlugTree_SourceDestination()
    '''
    if srcItm.valueType == enATBifrostPortOut or dstItm.valueType == enATBifrostPortIn : 
      self.currentIndexChanged_nodeSource(None)
      self.currentIndexChanged_nodeDestination(None)
    else :
      self.itemSelectionChanged_treeWidget_plugSource()
    '''


  def itemExpanded_treeWidget_plugSource(self, inCurr) : pass
  def itemExpanded_treeWidget_plugDestination(self, inCurr) : pass

  def applyPlugFilter(self, inTreeWidget:QtWidgets.QTreeWidget, inLineEdit:QtWidgets.QLineEdit) :
    cnt = inTreeWidget.topLevelItemCount()
    fltStr = inLineEdit.text()
    if len(fltStr) == 0 : 
      for idx in range(cnt) : 
        itm = inTreeWidget.topLevelItem(idx)
        itm.setVisibleRecurse(True)
    else : 
      for idx in range(cnt) : 
        itm = inTreeWidget.topLevelItem(idx)
        itm.setVisibleByName(fltStr)

  def clicked_plugFilter(self) : 
    self.applyPlugFilter(self.treeWidget_plugSource, self.lineEdit_plugFilterSource)
    self.applyPlugFilter(self.treeWidget_plugDestination, self.lineEdit_plugFilterDestination)

  def clicked_swapSourceDestination(self) : 
    srcIdx = self.comboBox_nodeSource.currentIndex()
    srcFltTxt = self.lineEdit_plugFilterSource.text()
    dstIdx = self.comboBox_nodeDestination.currentIndex()
    dstFltTxt = self.lineEdit_plugFilterDestination.text()
    
    self.lineEdit_plugFilterSource.setText(dstFltTxt)
    self.lineEdit_plugFilterDestination.setText(srcFltTxt)
    self.comboBox_nodeSource.setCurrentIndex(dstIdx)
    self.comboBox_nodeDestination.setCurrentIndex(srcIdx)


  def editingFinished_plugFilterSource(self) : 
    self.applyPlugFilter(self.treeWidget_plugSource, self.lineEdit_plugFilterSource)

  def editingFinished_plugFilterDestination(self) : 
    self.applyPlugFilter(self.treeWidget_plugDestination, self.lineEdit_plugFilterDestination)

