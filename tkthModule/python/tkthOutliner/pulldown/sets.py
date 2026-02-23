import math

import maya.cmds as cmds
import maya.api.OpenMaya as OpenMaya
import maya.api.OpenMayaAnim as OpenMayaAnim

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


class actionSets(object) : 
  __setsItem = None
  __itemList = None
  
  def __init__(self, inSetsItem, inItemList) : 
    self.__setsItem = inSetsItem
    self.__itemList = list(inItemList)

  
  def addToSets(self) : 
    opnUnd = False
    try : 
      # print(u'addToSets:' + self.__setsItem.itemUniqueName)
      for itm in self.__itemList : 
        if cmds.sets(itm.itemUniqueName, isMember=self.__setsItem.itemUniqueName) : continue
        if opnUnd == False : 
          cmds.undoInfo(chunkName=u'addToSets', openChunk=True)
          opnUnd = True
        cmds.sets(itm.itemUniqueName, edit=True, addElement=self.__setsItem.itemUniqueName)
    finally : 
      if opnUnd : cmds.undoInfo(closeChunk=True)
    

  def deleteFromSets(self) : 
    opnUnd = False
    try : 
      # print(u'deleteFromSets:' + self.__setsItem.itemUniqueName)
      for itm in self.__itemList : 
        if cmds.sets(itm.itemUniqueName, isMember=self.__setsItem.itemUniqueName) == False : continue
        if opnUnd == False : 
          cmds.undoInfo(chunkName=u'deleteFromSets', openChunk=True)
          opnUnd = True
        cmds.sets(itm.itemUniqueName, edit=True, remove=self.__setsItem.itemUniqueName)

    finally : 
      if opnUnd : cmds.undoInfo(closeChunk=True)



class pullDownSets(base.pullDownBase) : 
  __setsFolderItem = None
  __actList = None
  
  def __init__(self, inMenu, inItmLst, inCore) : 
    super().__init__(inMenu, inItmLst, inCore)
    stLst = self.filterByHasFnList([OpenMaya.MFn.kSet])
    itmLst = list()
    itmLst.extend(self.filterByItemType(item.itemBase.enMDagPath))
    itmLst.extend(self.filterByItemType(item.itemBase.enMObject))
    if len(stLst) + len(itmLst) == 0 : raise Exception()

    if len(stLst) > 0 : 
      subMenu = self.menu.addMenu(u'select')
      act = subMenu.addAction(u'dag')
      act.triggered.connect(self.select_dag)
      act = subMenu.addAction(u'dn')
      act.triggered.connect(self.select_dn)
      act = subMenu.addAction(u'all')
      act.triggered.connect(self.select_all)

    if len(itmLst) > 0 : 
      tmpItm = self.core.treeWidget.topLevelItem(0)
      self.__setsFolderItem = tmpItm.findMObjectFolder(None, mfnType=OpenMaya.MFn.kSet)
      if self.__setsFolderItem is not None and self.__setsFolderItem.childCount() > 0 : 
        setsMenu = self.menu.addMenu(u'sets')
        setsAddMenu = setsMenu.addMenu(u'add')
        setsDelMenu = setsMenu.addMenu(u'delete')
        self.__actList = list()
        chCnt = self.__setsFolderItem.childCount()
        for chIdx in range(chCnt) : 
          chItm = self.__setsFolderItem.child(chIdx)
          if chItm.itemType != item.itemBase.enMObject : continue
          self.__actList.append(actionSets(chItm, itmLst))
          act = setsAddMenu.addAction(chItm.itemName)
          act.triggered.connect(self.__actList[-1].addToSets)
          act = setsDelMenu.addAction(chItm.itemName)
          act.triggered.connect(self.__actList[-1].deleteFromSets)


  def select_members(self, dag=False, dn=False) : 
    opnUndChk = False
    stLst = self.filterByHasFnList([OpenMaya.MFn.kSet])
    try : 
      for st in stLst : 
        stNdNm = st.itemUniqueName
        if dag : 
          idxLst = cmds.getAttr(plugName(stNdNm, u'dagSetMembers'), multiIndices=True)
          if idxLst is None : continue
          for idx in idxLst : 
            src = cmds.listConnections(plugName(stNdNm, (u'dagSetMembers', idx)), source=True, destination=False, skipConversionNodes=True)
            if src is None or len(src) == 0 : continue
            if opnUndChk == False : 
              cmds.undoInfo(chunkName=u'select_members', openChunk=True)
              opnUndChk = True
              cmds.select(clear=True)
            cmds.select(src[0], add=True)
        if dn : 
          idxLst = cmds.getAttr(plugName(stNdNm, u'dnSetMembers'), multiIndices=True)
          if idxLst is None : continue
          for idx in idxLst : 
            src = cmds.listConnections(plugName(stNdNm, (u'dnSetMembers', idx)), source=True, destination=False, skipConversionNodes=True)
            if src is None or len(src) == 0 : continue
            if opnUndChk == False : 
              cmds.undoInfo(chunkName=u'select_members', openChunk=True)
              opnUndChk = True
              cmds.select(clear=True)
            cmds.select(src[0], add=True)
    finally :
      if opnUndChk : cmds.undoInfo(closeChunk=True)

  def select_dag(self) : self.select_members(dag=True)
  def select_dn(self) : self.select_members(dn=True)
  def select_all(self) : self.select_members(dag=True, dn=True)

