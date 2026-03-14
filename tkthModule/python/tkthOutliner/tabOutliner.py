import pathlib

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

from tkthOutliner.core import *

import tkthOutliner.item as item

from tkthOutliner.pulldown.viewText import *
from tkthOutliner.pulldown.bifrostUtility import *
from tkthOutliner.pulldown.createConstraint import *
from tkthOutliner.pulldown.renameNode import *
from tkthOutliner.pulldown.reload import *
from tkthOutliner.pulldown.deleteNode import *
from tkthOutliner.pulldown.createNode import *
from tkthOutliner.pulldown.disconnect import *
from tkthOutliner.pulldown.parentNode import *
from tkthOutliner.pulldown.editPath import *
from tkthOutliner.pulldown.transform import *
from tkthOutliner.pulldown.sets import *

import tkthOutliner.tabCommon as tabCommon


class treeWidgetOutliner(QtWidgets.QTreeWidget) : 
  __core = None
  @property
  def core(self) : return self.__core
  
  # def logMessage(self, inMsg) : 
  #   if self.core is not None : self.core.logMessage(inMsg)

  def __init__(self, core, parent, objectName) : 
    super().__init__(parent)
    self.__core = core

    qtreewidgetitem = QtWidgets.QTreeWidgetItem()
    qtreewidgetitem.setText(0, u'1')
    self.setHeaderItem(qtreewidgetitem)
    self.setObjectName(objectName)
    self.setLineWidth(2)
    self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
    self.setProperty(u'showDropIndicator', False)
    self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
    self.header().setVisible(False)

    self.setIndentation(10)
    self.itemSelectionChanged.connect(self.itemSelectionChanged_treeWidgetOutliner)
    self.itemExpanded.connect(self.itemExpanded_treeWidgetOutliner)
    self.itemDoubleClicked.connect(self.itemDoubleClicked_treeWidgetOutliner)
    self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    self.customContextMenuRequested.connect(self.customContextMenuRequested_treeWidgetOutliner)

  __uuidListSize = 2048
  __uuidList = None
  def getUUIDTableIndex(self, inUniqueUUID) : 
    if inUniqueUUID is None : return None
    hashVal = hash(str(inUniqueUUID))
    return hashVal % self.__uuidListSize
  
  def addUUIDTable(self, inItm:item.itemBase) : 
    if self.__uuidList is None : self.__uuidList = [None] * self.__uuidListSize
    cnt = 0
    que = [ inItm ]
    while len(que) > 0 : 
      itm = que.pop(0)
      chCnt = itm.childCount()
      for chIdx in range(chCnt) : 
        chItm = itm.child(chIdx)
        if chItm.itemType == item.itemBase.enMDagPath or chItm.itemType == item.itemBase.enMObject or chItm.itemType == item.itemBase.enMObjectFolder or chItm.itemType == item.itemBase.enShapeFolder : que.append(chItm)
      uuid = itm.uniqueUUID
      if uuid is None : continue
      tblIdx = self.getUUIDTableIndex(uuid)
      if tblIdx is None : continue
      cnt = cnt + 1
      if self.__uuidList[tblIdx] is None : 
        self.__uuidList[tblIdx] = [ itm ]
      else : 
        notExist = True
        for tmpItm in self.__uuidList[tblIdx] : 
          if tmpItm.uniqueUUID == uuid : 
            notExist = False
            break
        if notExist : self.__uuidList[tblIdx].append( itm )
    return cnt
  
  def deleteUUIDTable(self, inItm:item.itemBase) : 
    if self.__uuidList is None : return 0
    cnt = 0
    que = [ inItm ]
    while len(que) > 0 : 
      itm = que.pop(0)
      chCnt = itm.childCount()
      for chIdx in range(chCnt) : 
        chItm = itm.child(chIdx)
        if chItm.itemType == item.itemBase.enMDagPath or chItm.itemType == item.itemBase.enMObject or chItm.itemType == item.itemBase.enMObjectFolder or chItm.itemType == item.itemBase.enShapeFolder : que.append(chItm)
      uuid = itm.uniqueUUID
      if uuid is None : continue
      tblIdx = self.getUUIDTableIndex(uuid)
      if tblIdx is None : continue
      if self.__uuidList[tblIdx] is None : continue
      for idx, tmpItm in enumerate(self.__uuidList[tblIdx]) : 
        if tmpItm.uniqueUUID == uuid : 
          self.__uuidList[tblIdx].pop(idx)
          cnt = cnt + 1
          break
    return cnt

  def findByUUID(self, inUUID) : 
    if self.__uuidList is None : return None
    tblIdx = self.getUUIDTableIndex(inUUID)
    if tblIdx is None : return None
    if self.__uuidList[tblIdx] is None : return None
    for itm in self.__uuidList[tblIdx] : 
      if itm.uniqueUUID == inUUID : 
        return itm
    return None

  def findMObjectFolder(self, inMObj, mfnType=None, typeId=None) : 
    fldItm = None
    cnt = self.topLevelItemCount()
    for idx in range(cnt) : 
      itm = self.topLevelItem(idx)
      if itm.itemType != item.itemBase.enMObjectFolder : continue
      if itm.isThisFolder(inMObj, mfnType=mfnType, typeId=typeId) : 
        fldItm = itm
        break
      if itm.isSubFolder(inMObj, mfnType=mfnType) : 
        fldItm = itm
        break
    if fldItm is None : return None

    que = [ fldItm ]
    while len(que) > 0 : 
      fldItm = que.pop(0)
      chCnt = fldItm.childCount()
      for chIdx in range(chCnt) : 
        chItm = fldItm.child(chIdx)
        if chItm.itemType == item.itemBase.enMObjectFolder : 
          if chItm.isThisFolder(inMObj, mfnType=mfnType, typeId=typeId) : 
            que.append(chItm)
          elif chItm.isSubFolder(inMObj, mfnType=mfnType) : 
            que.append(chItm)
            break
        elif chItm.itemType == item.itemBase.enMObject : 
          break
    
    return fldItm

  def insertTopLevelItemBySorted(self, inItm, startIndex=0) : 
    itmNm = inItm.itemName
    chCnt = self.topLevelItemCount()
    chIdx = startIndex
    while chIdx < chCnt : 
      try : 
        chItm = self.topLevelItem(chIdx)
        chItmNm = chItm.itemName
        if chItmNm[0] == u'<' and chItmNm[-1] == u'>' : continue
        if inItm.itemType < chItm.itemType : 
          self.insertTopLevelItem(chIdx, inItm)
          return chIdx
        if inItm.itemType == chItm.itemType and itmNm < chItmNm : 
          self.insertTopLevelItem(chIdx, inItm)
          return chIdx
      finally : 
        chIdx = chIdx + 1
    self.addTopLevelItem(inItm)
    return chCnt

  def addTopLevelItem(self, item) :
    self.addUUIDTable(item)
    return super().addTopLevelItem(item)
  def addTopLevelItems(self, items) :
    for itm in items : self.addUUIDTable(itm)
    return super().addTopLevelItems(items)
  def insertTopLevelItem(self, index, item) :
    self.addUUIDTable(item)
    return super().insertTopLevelItem(index, item)
  def insertTopLevelItems(self, index, items) :
    for itm in items : self.addUUIDTable(itm)
    return super().insertTopLevelItems(index, items)
  def takeTopLevelItem(self, index) :
    itm = self.topLevelItem(index)
    self.deleteUUIDTable(itm)
    return super().takeTopLevelItem(index)
  def clear(self) :
    self.__uuidList = None
    return super().clear()

  def activate(self) : 
    self.currentItemChanged.connect(self.currentItemChanged_treeWidgetOutliner)

  def deactivate(self) : 
    try : self.currentItemChanged.disconnect(self.currentItemChanged_treeWidgetOutliner)
    except : pass

  __expandList = None
  def updateExpandedList(self, que=None) : 
    self.__expandList = list()
    if que is None : 
      que = list()
      cnt = self.topLevelItemCount()
      for idx in range(cnt) : 
        itm = self.topLevelItem(idx)
        if itm.itemType != item.itemBase.enMDagPath and itm.itemType != item.itemBase.enMObject and itm.itemType != item.itemBase.enMObjectFolder : continue
        if itm.isExpanded() : que.append(itm)
    while len(que) > 0 : 
      itm = que.pop(0)
      chExpanded = False
      chCnt = itm.childCount()
      for chIdx in range(chCnt) : 
        chItm = itm.child(chIdx)
        if chItm.itemType != item.itemBase.enMDagPath and itm.itemType != item.itemBase.enMObject and itm.itemType != item.itemBase.enMObjectFolder : continue
        if chItm.isExpanded() : 
          que.append(chItm)
          chExpanded = True
      if chExpanded == False : 
        self.__expandList.append(itm.itemPath())

  def applyExpandedList(self) : 
    if self.__expandList is None : return
    for itmPth in self.__expandList : 
      itm = self.findByItemPath(itmPth)
      while itm is not None : 
        if itm.isExpanded() : break
        itm.setExpanded(True)
        itm = itm.parent()
    self.__expandList = None

  __apiTypeFolderList = None
  def loadAPITypeFolderList(self) : 
    self.__apiTypeFolderList = loadJSON(pathlib.Path(__file__).parent.as_posix() + u'/apitype.json')
    for apTp in self.__apiTypeFolderList : 
      apTp.append(None)
      if type(apTp[1]) == list : 
        for subApTp in apTp[1] : 
          subApTp.append(None)
  
  def addMObjectFolderItem(self, inMObjFldItm, inMObj) : 
    if inMObj is None : 
      self.__apiTypeFolderList.append([ inMObjFldItm.text(0), inMObjFldItm.mfnType, inMObjFldItm ])
      self.insertTopLevelItemBySorted(inMObjFldItm)
      return
    added = False
    for apTp in self.__apiTypeFolderList : 
      if type(apTp[1]) == list : 
        for subApTp in apTp[1] : 
          if inMObj.hasFn(subApTp[1]) : 
            if apTp[2] is None : 
              mfnTpLst = list()
              for tmp in apTp[1] : mfnTpLst.append(tmp[1])
              itm = item.itemMObjectFolder(apTp[0], mfnTypeList=mfnTpLst)
              apTp[2] = itm
              self.insertTopLevelItemBySorted(itm)
            added = True
            apTp[2].addChild(inMObjFldItm)
            subApTp[2] = inMObjFldItm
            break
      else : 
        if inMObj.hasFn(apTp[1]) : 
          if apTp[2] is None : 
            itm = item.itemMObjectFolder(apTp[0], mfnType=apTp[1])
            apTp[2] = itm
            self.insertTopLevelItemBySorted(itm)
          added = True
          apTp[2].addChild(inMObjFldItm)
      if added : break
    if added == False :
      self.__apiTypeFolderList.append([ inMObjFldItm.text(0), inMObj.apiType(), inMObjFldItm ])
      self.insertTopLevelItemBySorted(inMObjFldItm)

  __itemList = None
  __itemIndex = None
  def addNext(self, inItm) : 
    itmPth = inItm.itemPath()
    if self.__itemList is None : 
      self.__itemList = [ itmPth ]
      self.__itemIndex = 0
    else : 
      self.__itemList = self.__itemList[:self.__itemIndex+1]
      self.__itemList.append(itmPth)
      self.__itemIndex = self.__itemIndex + 1

  def setNextItem(self) : 
    if self.__itemList is None or len(self.__itemList) == self.__itemIndex + 1 : 
      return None
    self.__itemIndex = self.__itemIndex + 1
    itm = self.findByItemPath(self.__itemList[self.__itemIndex])
    if itm is not None : self.setCurrentAndScrollToItem(itm)
    return itm

  def setBackItem(self) : 
    if self.__itemList is None or self.__itemIndex == 0 : 
      return None
    self.__itemIndex = self.__itemIndex - 1
    itm = self.findByItemPath(self.__itemList[self.__itemIndex])
    if itm is not None : self.setCurrentAndScrollToItem(itm)
    return itm

  def updateContent(self) : 
    self.updateExpandedList()
    self.__itemList = None
    self.__itemIndex = None
    
    self.clear()
    self.loadAPITypeFolderList()
    ( dgpLst, mobjDct ) = self.getAll()
    self.applyExpandedList()


  def getAll(self) : 
    dgpLst = list()
    mobjDct = dict()
    fnRefList = getMFnReferenceList()

    itr = OpenMaya.MItDependencyNodes()
    while itr.isDone() == False : 
      try : 
        mobj = itr.thisNode()
        try : 
          fn = OpenMaya.MFnDagNode(mobj)
          dgp = fn.getPath()
          if dgp.length() == 0 : continue
          self.addMDagPath(dgp, fnRefList=fnRefList, checkExists=False)
          # itm = item.itemMDagPath(dgp, fnRefList=fnRefList)
          # dgpLst.append([dgp, itm])
        except : 
          self.addMObject(mobj, fnRefList=fnRefList, checkExists=False)
      finally : 
        itr.next()

    return ( dgpLst, mobjDct )

  def addMDagPath(self, inDgp, fnRefList=None, checkExists=True) : 
    fn = OpenMaya.MFnDagNode(inDgp)
    '''
    if self.topLevelItemCount() == 0 : return None
    itm = self.topLevelItem(0)
    mdgpItm = itm.findMDagPath(inDgp)
    '''
    if checkExists : 
      mdgpItm = self.findByUUID(UniqueMayaUUID(fn, fnRefList=fnRefList))
      if mdgpItm is not None : 
        self.updateItem_MDagPath(mdgpItm)
        return mdgpItm
    
    mdgpItm = item.itemMDagPath(inDgp, fnRefList=fnRefList)
    if inDgp.length() == 1 : 
      self.insertTopLevelItemBySorted(mdgpItm)
      # self.updateItem(mdgpItm)
    else : 
      prtDgp = OpenMaya.MDagPath(inDgp)
      prtDgp.pop()
      fnPrt = OpenMaya.MFnDagNode(prtDgp)
      prtItm = self.findByUUID(UniqueMayaUUID(fnPrt))
      if prtItm is None : 
        logMessage(self.parent(), u'not exist parent item:' + inDgp.fullPathName())
        self.insertTopLevelItemBySorted(mdgpItm)
        return None
      else : 
        prtItm.insertChildBySorted(mdgpItm)
        # self.updateItem(prtItm)
    
    return mdgpItm

  def addMObject(self, inMObj, fnRefList=None, checkExists=True) : 
    fn = OpenMaya.MFnDependencyNode(inMObj)
    '''
    if self.topLevelItemCount() == 0 : return None
    itm = self.topLevelItem(0)
    mobjItm = itm.findMObject(inMObj)
    '''
    if checkExists : 
      mobjItm = self.findByUUID(UniqueMayaUUID(fn, fnRefList=fnRefList))
      if mobjItm is not None : 
        self.updateItem_MObject(mobjItm)
        return mobjItm
    
    fldItm = self.findMObjectFolder(inMObj)
    mobjItm = item.itemMObject(inMObj, fnRefList=fnRefList)
    apiTp = inMObj.apiType()
    tpId = fn.typeId
    if fldItm is None : 
      if apiTp == OpenMaya.MFn.kPluginDependNode : 
        depPlgItm = item.itemMObjectFolder(u'kPluginDependNode', mfnType=apiTp)
        self.addMObjectFolderItem(depPlgItm, None)
        fldItm = item.itemMObjectFolder(fn.typeName, typeId=tpId)
      else : 
        fldItm = item.itemMObjectFolder(inMObj.apiTypeStr, mfnType=apiTp)
      fldItm.addChildSorted(mobjItm)
      self.addMObjectFolderItem(fldItm, inMObj)
    else : 
      if apiTp == OpenMaya.MFn.kPluginDependNode : 
        if fldItm.typeId is None or fldItm.typeId != tpId : 
          subFldItm = item.itemMObjectFolder(fn.typeName, typeId=tpId)
          subFldItm.addChildSorted(mobjItm)
          fldItm.addChild(subFldItm)
          fldItm = subFldItm
        else : 
          fldItm.addChild(mobjItm)
      else : 
        if fldItm.mfnType is None or fldItm.mfnType != apiTp : 
          subFldItm = item.itemMObjectFolder(inMObj.apiTypeStr, mfnType=apiTp)
          subFldItm.addChildSorted(mobjItm)
          self.addMObjectFolderItem(subFldItm, inMObj)
          fldItm = subFldItm
        else : 
          fldItm.addChildSorted(mobjItm)

    return mobjItm

  def deleteMDagPath(self, inDgp) : 
    if self.topLevelItemCount() == 0 : return None
    itm = self.topLevelItem(0)
    mdgpItm = itm.findMDagPath(inDgp)
    print(u'deleteMDagPath:' + str(mdgpItm))
    if mdgpItm is not None : self.deleteItem(mdgpItm)

  def deleteMObject(self, inMObj) : 
    if self.topLevelItemCount() == 0 : return None
    itm = self.topLevelItem(0)
    mobjItm = itm.findMObject(inMObj)
    print(u'deleteMObject:' + str(mobjItm))
    if mobjItm is not None : self.deleteItem(mobjItm)

  def deleteItem(self, inItm) : 
    print(u'deleteItem:' + str(inItm))
    prtItm = inItm.parent()
    if prtItm is not None : 
      chIdx = prtItm.indexOfChild(inItm)
      prtItm.takeChild(chIdx)
    else : 
      topIdx = self.indexOfTopLevelItem(inItm)
      self.takeTopLevelItem(topIdx)


  def updateItem(self, inItm) : 
    if inItm.itemType == item.itemBase.enMObjectFolder :
      self.updateContent()
    elif inItm.itemType == item.itemBase.enMDagPath : 
      return self.updateItem_MDagPath(inItm)
    elif inItm.itemType == item.itemBase.enShapeFolder :
      self.updateItem_MDagPath(inItm.parent())
    elif inItm.itemType == item.itemBase.enMObject :
      return self.updateItem_MObject(inItm)
    elif inItm.itemType == item.itemBase.enConnection :
      self.updateItem(inItm.parent())
    elif inItm.itemType == item.itemBase.enSourceFolder or inItm.itemType == item.itemBase.enDestinationFolder : 
      inItm.parent().updateConnection()
    return None


  def updateItem_MObject(self, inItm) : 
    prtItm = inItm.parent()
    chIdx = prtItm.indexOfChild(inItm)
    prtItm.takeChild(chIdx)
    mobj = inItm.getObject()
    if mobj is None : 
      logMessage(self.parent(), u'updateItem_MDagPath:not exist:' + inItm.itemUniqueName)
      return None
    itm = item.itemMObject(mobj)
    prtItm.insertChild(chIdx, itm)
    return itm


  def updateItem_MDagPath(self, inItm) : 
    chIdx = None
    topIdx = None
    prtItm = inItm.parent()
    if prtItm is not None : 
      self.updateExpandedList(que=[ prtItm ])
      chIdx = prtItm.indexOfChild(inItm)
      prtItm.takeChild(chIdx)
    else : 
      self.updateExpandedList(que=[ inItm ])
      topIdx = self.indexOfTopLevelItem(inItm)
      self.takeTopLevelItem(topIdx)
    dgp = inItm.getObject()
    if dgp is None : 
      logMessage(self.parent(), u'updateItem_MDagPath:not exist:' + inItm.itemUniqueName)
      return None
    itm = item.itemMDagPath(dgp)
    if prtItm is not None : 
      prtItm.insertChild(chIdx, itm)
    else : 
      self.insertTopLevelItem(topIdx, itm)
    
    if dgp.node().hasFn(OpenMaya.MFn.kTransform) : 
      que = []
      chCnt = dgp.childCount()
      for chIdx in range(chCnt) : 
        chDgp = OpenMaya.MDagPath(dgp)
        chDgp.push(dgp.child(chIdx))
        que.append((itm, chDgp))
      
      while len(que) > 0 : 
        (prtItm, chDgp) = que.pop(0)
        chItm = item.itemMDagPath(chDgp)
        if chDgp.node().hasFn(OpenMaya.MFn.kTransform) : 
          prtItm.addChild(chItm)
          chCnt = chDgp.childCount()
          for chIdx in range(chCnt) : 
            chChDgp = OpenMaya.MDagPath(chDgp)
            chChDgp.push(chDgp.child(chIdx))
            que.append((chItm, chChDgp))
        else : 
          prtItm.addShape(chItm)

    self.applyExpandedList()
    return itm

  def getRootMDagPathItemCount(self) : 
    cnt = self.topLevelItemCount()
    for idx in range(cnt) : 
      itm = self.topLevelItem(idx)
      if itm.itemType != item.itemBase.enMDagPath : return idx
    return cnt

  # __selectByScript = False
  def setCurrentAndScrollToItem(self, inItm) : 
    # if inItm.flags() & QtCore.Qt.ItemFlag.ItemIsSelectable == QtCore.Qt.ItemFlag.ItemIsSelectable : 
    #   self.__selectByScript = True
    prtItm = inItm.parent()
    while prtItm is not None : 
      if prtItm.isExpanded() == False : prtItm.setExpanded(True)
      prtItm = prtItm.parent()
    self.setCurrentItem(inItm)
    self.scrollToItem(inItm)
    
  def setSelectedBySelectionList(self, selectionList=None) : 
    if self.topLevelItemCount() == 0 : return None
    if selectionList is None : selectionList = OpenMaya.MGlobal.getActiveSelectionList()
    itr = OpenMaya.MItSelectionList(selectionList)
    topItm = self.topLevelItem(0)
    curItm = None
    selItmLst = list()
    while itr.isDone() == False :
      try :
        if itr.itemType() == OpenMaya.MItSelectionList.kDNselectionItem :
          fn = OpenMaya.MFnDependencyNode(itr.getDependNode())
          selItm = self.findByUUID(UniqueMayaUUID(fn))
          # selItm = topItm.findMObject(itr.getDependNode())
          if selItm is not None : 
            curItm = selItm
            selItmLst.append(selItm)
        if itr.itemType() == OpenMaya.MItSelectionList.kDagSelectionItem :
          fn = OpenMaya.MFnDagNode(itr.getDagPath())
          selItm = self.findByUUID(UniqueMayaUUID(fn))
          # selItm = topItm.findMDagPath(itr.getDagPath())
          if selItm is not None : 
            curItm = selItm
            selItmLst.append(selItm)
      except :
        pass
      finally :
        itr.next()
    for selItm in selItmLst : selItm.setSelected(True)
    if curItm is not None : self.setCurrentAndScrollToItem(curItm)
    return curItm


  def findByItemPath(self, inItmPth) : 
    chCnt = self.topLevelItemCount()
    if chCnt == 0 : return None
    lst = list(inItmPth)
    nm = lst.pop(0)
    itm = None
    for chIdx in range(chCnt) : 
      chItm = self.topLevelItem(chIdx)
      if chItm.text(0) == nm : 
        itm = chItm
        break
    if itm is None : return None

    for nm in lst : 
      prtItm = itm
      itm = None
      chCnt = prtItm.childCount()
      for chIdx in range(chCnt) : 
        chItm = prtItm.child(chIdx)
        if chItm.text(0) == nm : 
          itm = chItm
          break
      if itm is None : return None

    return itm

  def itemSelectionChanged_treeWidgetOutliner(self) : 
    # if self.__selectByScript : 
    #   self.__selectByScript = False
    #   return
    
    modCtrlShft = QtGui.QGuiApplication.queryKeyboardModifiers() & (QtCore.Qt.ShiftModifier|QtCore.Qt.ControlModifier)
    selItmLst = self.selectedItems()
    if selItmLst is None or len(selItmLst) == 0 :
      if modCtrlShft == QtCore.Qt.NoModifier : cmds.select(clear=True)
      return
    opnChnk = False
    try : 
      for selItm in selItmLst : 
        if selItm.itemType == item.itemBase.enMObject or selItm.itemType == item.itemBase.enMDagPath or selItm.itemType == item.itemBase.enConnection : 
          if cmds.objExists(selItm.itemUniqueName) : 
            if opnChnk == False : 
              cmds.undoInfo(openChunk=True, chunkName=u'selectByOutliner')
              opnChnk = True
              if modCtrlShft == QtCore.Qt.NoModifier : 
                cmds.select(clear=True)
                logMessage(self.parent(), u'select -clear')
            cmds.select(selItm.itemUniqueName, add=True)
            logMessage(self.parent(), u'select -add ' + str(selItm.itemUniqueName))
            self.core.tabConnect.addNode(selItm.itemUniqueName)
    finally : 
      if opnChnk : cmds.undoInfo(closeChunk=True)

  def itemExpanded_treeWidgetOutliner(self, inCurr) : 
    disconncted = False
    try : 
      if inCurr is None : return
      self.itemExpanded.disconnect(self.itemExpanded_treeWidgetOutliner)
      disconncted = True
      mod = QtGui.QGuiApplication.queryKeyboardModifiers()
      expDep = 0
      if mod & QtCore.Qt.ShiftModifier == QtCore.Qt.ShiftModifier : expDep = expDep + 10
      if mod & QtCore.Qt.ControlModifier == QtCore.Qt.ControlModifier : expDep = expDep + 5
      inCurr.expanded(depth=expDep)
    finally : 
      if disconncted : self.itemExpanded.connect(self.itemExpanded_treeWidgetOutliner)

  def itemDoubleClicked_treeWidgetOutliner(self, inItm, inCol) : 
    if inItm is not None : 
      inItm.doubleClicked(inCol)

  def currentItemChanged_treeWidgetOutliner(self, inCurr, inPrev) : 
    sbBar = self.core.statusBar()
    if sbBar is not None : 
      sbMsg = None
      if inCurr is not None : 
        sbMsg = inCurr.getStatusBarMessage()
        inCurr.setCurrent()
      if sbMsg is None : 
        sbBar.clearMessage()
      else : 
        sbBar.showMessage(sbMsg)

  __actObjList = None
  def customContextMenuRequested_treeWidgetOutliner(self, inPnt) :
    itmLst = list()
    selLst = self.selectedItems()
    if selLst is not None : 
      for sel in selLst : 
        itmLst.append(sel)
    if len(itmLst) == 0 : itmLst.append(self.currentItem())

    self.__actObjList = []
    menu = QtWidgets.QMenu(self)

    try :
      actObj = pullDownViewText(menu, itmLst, self)
      self.__actObjList.append(actObj)
    except : pass
    try :
      actObj = pullDownTransform(menu, itmLst, self)
      self.__actObjList.append(actObj)
    except : pass
    try :
      actObj = pullDownParent(menu, itmLst, self)
      self.__actObjList.append(actObj)
    except : pass
    try :
      actObj = pullDownCreateNode(menu, itmLst, self)
      self.__actObjList.append(actObj)
    except : pass
    try :
      actObj = pullDownEditPath(menu, itmLst, self)
      self.__actObjList.append(actObj)
    except : pass
    try :
      actObj = pullDownSets(menu, itmLst, self)
      self.__actObjList.append(actObj)
    except : pass
    try :
      actObj = pullDownRename(menu, itmLst, self)
      self.__actObjList.append(actObj)
    except : pass
    try :
      actObj = pullDownDelete(menu, itmLst, self)
      self.__actObjList.append(actObj)
    except : pass
    try :
      actObj = pullDownDisconnect(menu, itmLst, self)
      self.__actObjList.append(actObj)
    except : pass
    try :
      actObj = pullDownBifrostUtility(menu, itmLst, self)
      self.__actObjList.append(actObj)
    except : pass
    try :
      actObj = pullDownReload(menu, itmLst, self)
      self.__actObjList.append(actObj)
    except : pass
    try :
      actObj = pullDownAllReload(menu, itmLst, self)
      self.__actObjList.append(actObj)
    except : pass

    if len(self.__actObjList) > 0 : 
      if getPysideMajorVersion() >= 6 : 
        menu.exec(self.mapToGlobal(inPnt))
      else : 
        menu.exec_(self.mapToGlobal(inPnt))




class tabOutliner(tabCommon.tabCommon) : 
  __treeWidget:treeWidgetOutliner = None
  @property
  def treeWidget(self) : return self.__treeWidget
  
  __lineEdit_findName:QtWidgets.QLineEdit = None
  @property
  def lineEdit_findName(self) : return self.__lineEdit_findName
  __pushButton_findNext:QtWidgets.QPushButton = None
  @property
  def pushButton_findNext(self) : return self.__pushButton_findNext

  __pushButton_outlinerBack:QtWidgets.QPushButton = None
  @property
  def pushButton_outlinerBack(self) : return self.__pushButton_outlinerBack
  __pushButton_outlinerNext:QtWidgets.QPushButton = None
  @property
  def pushButton_outlinerNext(self) : return self.__pushButton_outlinerNext
  __pushButton_outlinerSelected:QtWidgets.QPushButton = None
  @property
  def pushButton_outlinerSelected(self) : return self.__pushButton_outlinerSelected
  
  def setupUI(self) : 
    self.verticalLayout_outliner = QtWidgets.QVBoxLayout(self)
    self.verticalLayout_outliner.setObjectName(u"verticalLayout_outliner")

    self.horizontalLayout_outlinerFind = QtWidgets.QHBoxLayout()
    self.horizontalLayout_outlinerFind.setObjectName(u"horizontalLayout_outlinerFind")

    self.__lineEdit_findName = QtWidgets.QLineEdit(self)
    self.__lineEdit_findName.setObjectName(u"lineEdit_findName")
    self.horizontalLayout_outlinerFind.addWidget(self.lineEdit_findName)

    self.__pushButton_findNext = QtWidgets.QPushButton(self)
    self.__pushButton_findNext.setObjectName(u"pushButton_findNext")
    self.pushButton_findNext.setText(u'find')
    self.horizontalLayout_outlinerFind.addWidget(self.pushButton_findNext)

    self.__pushButton_outlinerBack = QtWidgets.QPushButton(self)
    self.__pushButton_outlinerBack.setObjectName(u"pushButton_outlinerBack")
    self.pushButton_outlinerBack.setText(u'back')
    self.horizontalLayout_outlinerFind.addWidget(self.pushButton_outlinerBack)

    self.__pushButton_outlinerNext = QtWidgets.QPushButton(self)
    self.__pushButton_outlinerNext.setObjectName(u"pushButton_outlinerNext")
    self.pushButton_outlinerNext.setText(u'next')
    self.horizontalLayout_outlinerFind.addWidget(self.pushButton_outlinerNext)

    self.__pushButton_outlinerSelected = QtWidgets.QPushButton(self)
    self.__pushButton_outlinerSelected.setObjectName(u"pushButton_outlinerSelected")
    self.pushButton_outlinerSelected.setText(u'selected')
    self.horizontalLayout_outlinerFind.addWidget(self.pushButton_outlinerSelected)

    self.verticalLayout_outliner.addLayout(self.horizontalLayout_outlinerFind)

    self.__treeWidget = treeWidgetOutliner(self.core, self, u'treeWidget_outliner')

    self.verticalLayout_outliner.addWidget(self.treeWidget)
    tabIdx = self.core.tabWidget.addTab(self, u'outliner')
    self.core.tabWidget.setTabText(tabIdx, u'outliner')

  
  def __init__(self, core=None) : 
    super().__init__(core=core, objectName=u'tab_outliner')
    self.setupUI()

    self.pushButton_findNext.clicked.connect(self.clicked_findNext)
    self.lineEdit_findName.editingFinished.connect(self.clicked_findNext)
    self.pushButton_outlinerBack.clicked.connect(self.clicked_outlinerBack)
    self.pushButton_outlinerNext.clicked.connect(self.clicked_outlinerNext)
    self.pushButton_outlinerSelected.clicked.connect(self.clicked_outlinerSelected)
    
    self.treeWidget.updateContent()


  def reloadContent(self) : 
    #self.updateExpandedList()
    self.treeWidget.updateContent()
    #self.applyExpandedList()

  def activate(self) : 
    self.treeWidget.activate()

  def deactivate(self) : 
    try : self.treeWidget.deactivate()
    except : pass
    
  def clicked_outlinerSelected(self) : self.treeWidget.setSelectedBySelectionList()
  
  def clicked_findNext(self) : 
    itm = self.treeWidget.currentItem()
    if itm is None : itm = self.treeWidget.topLevelItem(0)
    else : itm = itm.nextItem()
    if itm is None : 
      msg = u'not exist nextItem'
      QtWidgets.QMessageBox.question(self, msg, msg, buttons=QtWidgets.QMessageBox.StandardButton.Ok)
      return
    
    s = self.lineEdit_findName.text()
    if s is None or len(s) == 0 : return
    nextItm = itm.findItemByText(s, isEntityType=True)
    if nextItm is not None : 
      self.treeWidget.addNext(nextItm)
      self.treeWidget.setCurrentAndScrollToItem(nextItm)
    else :
      msg = u'not exist:' + s
      QtWidgets.QMessageBox.question(self, msg, msg, buttons=QtWidgets.QMessageBox.StandardButton.Ok)

  
  def clicked_outlinerNext(self) : self.treeWidget.setNextItem()

  def clicked_outlinerBack(self) : self.treeWidget.setBackItem()

