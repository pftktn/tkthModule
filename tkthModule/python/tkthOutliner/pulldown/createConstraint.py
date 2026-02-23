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


class pullDownCreateConstraint(base.pullDownBase) : 
  def __init__(self, inMenu, inItmLst, inDlg) : 
    super().__init__(inMenu, inItmLst, inDlg)
    trfLst = self.filterByItemType(item.itemBase.enMDagPath)
    if len(trfLst) < 2 : raise Exception()

    subMenu = self.menu.addMenu(u'constraint')
    act = subMenu.addAction(u'point')
    act.triggered.connect(self.add_point)
    act = subMenu.addAction(u'orient')
    act.triggered.connect(self.add_orient)
    act = subMenu.addAction(u'parent')
    act.triggered.connect(self.add_parent)
    if len(trfLst) >= 3 :
      act = subMenu.addAction(u'aimUp')
      act.triggered.connect(self.add_aimUp)
    dgp = trfLst[-1].getObject()
    if dgp.hasFn(OpenMaya.MFn.kIkHandle) :
      act = subMenu.addAction(u'poleVector')
      act.triggered.connect(self.add_poleVector)
    act = subMenu.addAction(u'scale')
    act.triggered.connect(self.add_scale)


  def add_point(self) : 
    actLst = self.filterByItemType(item.itemBase.enMDagPath)
    pss = actLst.pop(-1)
    pssNd = pss.itemUniqueName
    nm = getShortName(pssNd) + u'_pointConstraint'
    actNdLst = list()
    for act in actLst : actNdLst.append(act.itemUniqueName)
    opnChnk = False
    try :
      cmds.undoInfo(chunkName=u'add pointConstraint', openChunk=True)
      opnChnk = True
      cns = cmds.pointConstraint(actNdLst, pssNd, name=nm, maintainOffset=False)
      msg = u'pointConstraint'
      for act in actLst : 
        self.core.updateItem(act)
        msg = msg + u' ' + act.itemName
      self.core.updateItem(pss)
      self.logMessage(msg + u' ' + pss.itemName)
      if cns is not None and len(cns) > 0 : 
        cmds.select(cns, replace=True)
        self.core.setSelectedBySelectionList()
    except Exception as e :
      self.logMessage(str(e))
    finally : 
      if opnChnk : cmds.undoInfo(closeChunk=True)

  def add_orient(self) : 
    actLst = self.filterByItemType(item.itemBase.enMDagPath)
    pss = actLst.pop(-1)
    pssNd = pss.itemUniqueName
    nm = getShortName(pssNd) + u'_orientConstraint'
    actNdLst = list()
    for act in actLst : actNdLst.append(act.itemUniqueName)
    opnChnk = False
    try :
      cmds.undoInfo(chunkName=u'add orientConstraint', openChunk=True)
      opnChnk = True
      cns = cmds.orientConstraint(actNdLst, pssNd, name=nm, maintainOffset=False)
      cmds.setAttr(plugName(cns[0], u'interpType'), 2)  # shortest
      msg = u'orientConstraint'
      for act in actLst : 
        self.core.updateItem(act)
        msg = msg + u' ' + act.itemName
      self.core.updateItem(pss)
      self.logMessage(msg + u' ' + pss.itemName)
      if cns is not None and len(cns) > 0 : 
        cmds.select(cns, replace=True)
        self.core.setSelectedBySelectionList()
    except Exception as e :
      self.logMessage(str(e))
    finally : 
      if opnChnk : cmds.undoInfo(closeChunk=True)

  def add_parent(self) : 
    actLst = self.filterByItemType(item.itemBase.enMDagPath)
    pss = actLst.pop(-1)
    pssNd = pss.itemUniqueName
    nm = getShortName(pssNd) + u'_parentConstraint'
    actNdLst = list()
    for act in actLst : actNdLst.append(act.itemUniqueName)
    opnChnk = False
    try :
      cmds.undoInfo(chunkName=u'add parentConstraint', openChunk=True)
      opnChnk = True
      cns = cmds.parentConstraint(actNdLst, pssNd, name=nm, maintainOffset=False)
      msg = u'parentConstraint'
      for act in actLst : 
        self.core.updateItem(act)
        msg = msg + u' ' + act.itemName
      self.core.updateItem(pss)
      self.logMessage(msg + u' ' + pss.itemName)
      if cns is not None and len(cns) > 0 : 
        cmds.select(cns, replace=True)
        self.core.setSelectedBySelectionList()
    except Exception as e :
      self.logMessage(str(e))
    finally : 
      if opnChnk : cmds.undoInfo(closeChunk=True)

  def add_aimUp(self) : 
    actLst = self.filterByItemType(item.itemBase.enMDagPath)
    pss = actLst.pop(-1)
    upv = actLst.pop(-1)
    pssNd = pss.itemUniqueName
    upvNd = upv.itemUniqueName
    nm = getShortName(pssNd) + u'_aimConstraint'
    actNdLst = list()
    for act in actLst : actNdLst.append(act.itemUniqueName)
    opnChnk = False
    try :
      cmds.undoInfo(chunkName=u'add aimConstraint', openChunk=True)
      opnChnk = True
      cns = cmds.aimConstraint(actNdLst, pssNd, name=nm, maintainOffset=False, worldUpType=u'object', worldUpObject=upvNd, aimVector=[1.0,0.0,0.0], upVector=[0.0,1.0,0.0])
      msg = u'aimConstraint -worldUpObject ' + upv.itemName
      for act in actLst : 
        self.core.updateItem(act)
        msg = msg + u' ' + act.itemName
      self.core.updateItem(upv)
      self.core.updateItem(pss)
      self.logMessage(msg + u' ' + pss.itemName)
      if cns is not None and len(cns) > 0 : 
        cmds.select(cns, replace=True)
        self.core.setSelectedBySelectionList()
    except Exception as e :
      self.logMessage(str(e))
    finally : 
      if opnChnk : cmds.undoInfo(closeChunk=True)

  def add_poleVector(self) : 
    actLst = self.filterByItemType(item.itemBase.enMDagPath)
    pss = actLst.pop(-1)
    pssNd = pss.itemUniqueName
    nm = getShortName(pssNd) + u'_poleVectorConstraint'
    actNdLst = list()
    opnChnk = False
    try :
      cmds.undoInfo(chunkName=u'add poleVectorConstraint', openChunk=True)
      opnChnk = True
      cns = cmds.poleVectorConstraint(actNdLst, pssNd, name=nm)
      msg = u'poleVectorConstraint'
      for act in actLst : 
        self.core.updateItem(act)
        msg = msg + u' ' + act.itemName
      self.core.updateItem(pss)
      self.logMessage(msg + u' ' + pss.itemName)
      if cns is not None and len(cns) > 0 : 
        cmds.select(cns, replace=True)
        self.core.setSelectedBySelectionList()
    except Exception as e :
      self.logMessage(str(e))
    finally : 
      if opnChnk : cmds.undoInfo(closeChunk=True)

  def add_scale(self) : 
    actLst = self.filterByItemType(item.itemBase.enMDagPath)
    pss = actLst.pop(-1)
    pssNd = pss.itemUniqueName
    nm = getShortName(pssNd) + u'_scaleConstraint'
    actNdLst = list()
    opnChnk = False
    try :
      cmds.undoInfo(chunkName=u'add scaleConstraint', openChunk=True)
      opnChnk = True
      cns = cmds.scaleConstraint(actNdLst, pssNd, name=nm, maintainOffset=False)
      msg = u'scaleConstraint'
      for act in actLst : 
        self.core.updateItem(act)
        msg = msg + u' ' + act.itemName
      self.core.updateItem(pss)
      self.logMessage(msg + u' ' + pss.itemName)
      if cns is not None and len(cns) > 0 : 
        cmds.select(cns, replace=True)
        self.core.setSelectedBySelectionList()
    except Exception as e :
      self.logMessage(str(e))
    finally : 
      if opnChnk : cmds.undoInfo(closeChunk=True)

