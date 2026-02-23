import maya.cmds as cmds
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


class pullDownParent(base.pullDownBase) : 
  def __init__(self, inMenu, inItmLst, inCore) : 
    super().__init__(inMenu, inItmLst, inCore)
    trnLst = self.filterByHasFnList([OpenMaya.MFn.kTransform])
    if len(trnLst) < 1 : raise Exception()

    subMenu = self.menu.addMenu(u'parent')
    if len(trnLst) > 1 : 
      act = subMenu.addAction(u'relative')
      act.triggered.connect(self.set_parentRelative)
      act = subMenu.addAction(u'absolute')
      act.triggered.connect(self.set_parentAbsolute)
    act = subMenu.addAction(u'to world')
    act.triggered.connect(self.set_parentToWorld)

  def set_parent(self, relative=True) :
    opnChnk = False
    chLst = self.filterByHasFnList([OpenMaya.MFn.kTransform])
    newPrtItm = chLst.pop(0)
    try :
      newPrtNm = newPrtItm.itemUniqueName
      cmds.undoInfo(chunkName=u'pullDownParent.set_parent:relative=' + str(relative), openChunk=True)
      opnChnk = True
      ndLst = list()
      absolute = not relative
      for chItm in chLst :
        try :
          chNm = chItm.itemUniqueName
          lst = cmds.parent(chNm, newPrtNm, relative=relative, absolute=absolute)
          if lst is not None : ndLst.extend(lst)
          self.logMessage(u'parent -relative ' + chNm + newPrtNm)
          prtItm = chItm.parent()
          if prtItm is None :
            idx = self.core.indexOfTopLevelItem(chItm)
            self.core.takeTopLevelItem(idx)
          else :
            chIdx = prtItm.indexOfChild(chItm)
            prtItm.takeChild(chIdx)
        except Exception as e :
          self.logMessage(str(e))

      self.core.updateItem(newPrtItm)
      if len(ndLst) > 0 : 
        cmds.select(ndLst, replace=True)
        self.core.setSelectedBySelectionList()
    finally :
      if opnChnk : cmds.undoInfo(closeChunk=True)

  def set_parentRelative(self) : self.set_parent(relative=True)
  def set_parentAbsolute(self) : self.set_parent(relative=False)

  def set_parentToWorld(self) :
    opnChnk = False
    chLst = self.filterByHasFnList([OpenMaya.MFn.kTransform])
    try :
      cmds.undoInfo(chunkName=u'pullDownParent.set_parentToWorld', openChunk=True)
      opnChnk = True
      ndLst = list()
      for chItm in chLst :
        try :
          chNm = chItm.itemUniqueName
          lst = cmds.parent(chNm, world=True)
          if lst is not None : ndLst.extend(lst)
          self.logMessage(u'parent -world ' + chNm)
          newChNm = getFullName(lst[0])

          prtItm = chItm.parent()
          if prtItm is None :
            idx = self.core.indexOfTopLevelItem(chItm)
            self.core.takeTopLevelItem(idx)
          else :
            chIdx = prtItm.indexOfChild(chItm)
            prtItm.takeChild(chIdx)
          
          dgp = getMDagPathByName(newChNm)
          itm = item.itemMDagPath(dgp)
          idx = self.core.getRootMDagPathItemCount()
          self.core.insertTopLevelItem(idx, itm)
        except Exception as e :
          self.logMessage(str(e))
      if len(ndLst) > 0 : 
        cmds.select(ndLst, replace=True)
        self.core.setSelectedBySelectionList()
    finally :
      if opnChnk : cmds.undoInfo(closeChunk=True)

