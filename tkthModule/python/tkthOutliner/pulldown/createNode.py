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


class pullDownCreateNode(base.pullDownBase) : 
  def __init__(self, inMenu, inItmLst, inCore) : 
    super().__init__(inMenu, inItmLst, inCore)
    trfLst = self.filterByHasFnList([OpenMaya.MFn.kTransform])
    if len(trfLst) > 0 :
      subMenu = self.menu.addMenu(u'create child')
      act = subMenu.addAction(u'locator')
      act.triggered.connect(self.addChild_locator)
      act = subMenu.addAction(u'group')
      act.triggered.connect(self.addChild_group)
      act = subMenu.addAction(u'joint')
      act.triggered.connect(self.addChild_joint)

      subMenu = self.menu.addMenu(u'create matrix')
      act = subMenu.addAction(u'decompose worldMatrix')
      act.triggered.connect(self.addDecompose_worldMatrix)
      act = subMenu.addAction(u'compose localMatrix')
      act.triggered.connect(self.addCompose_localMatrix)
      act = subMenu.addAction(u'quaternion')
      act.triggered.connect(self.addQuaternion)

      jntLst = self.filterByHasFnList([OpenMaya.MFn.kJoint])
      if len(jntLst) == 2 :
        act = self.menu.addAction(u'create ikHandle')
        act.triggered.connect(self.add_ikHandle)
    else : 
      subMenu = self.menu.addMenu(u'create root')
      act = subMenu.addAction(u'locator')
      act.triggered.connect(self.addRoot_locator)
      act = subMenu.addAction(u'group')
      act.triggered.connect(self.addRoot_group)
      act = subMenu.addAction(u'joint')
      act.triggered.connect(self.addRoot_joint)
    

  def addChild_locator(self) : 
    opnChnk = False
    try :
      trfLst = self.filterByHasFnList([OpenMaya.MFn.kTransform])
      nmHint = getShortName(trfLst[0].itemUniqueName)
      ( nm, sts ) = QtWidgets.QInputDialog.getText(self.core, u'create locator', u'name', text=nmHint)
      if nm is None or len(nm) == 0 or sts == False : return
      cmds.undoInfo(chunkName=u'pullDownAddNode.addChild_locator', openChunk=True)
      opnChnk = True
      ndLst = list()
      for itm in trfLst :
        nd = createLocator(itm.itemUniqueName, nm)
        ndLst.append(nd[0])
        self.core.updateItem(itm)
      if len(ndLst) > 0 : 
        cmds.select(ndLst, replace=True)
        self.core.setSelectedBySelectionList()
    finally :
      if opnChnk : cmds.undoInfo(closeChunk=True)

  def addChild_group(self) :
    opnChnk = False
    try :
      trfLst = self.filterByHasFnList([OpenMaya.MFn.kTransform])
      nmHint = getShortName(trfLst[0].itemUniqueName)
      ( nm, sts ) = QtWidgets.QInputDialog.getText(self.core, u'create group', u'name', text=nmHint)
      if nm is None or len(nm) == 0 or sts == False : return
      cmds.undoInfo(chunkName=u'pullDownAddNode.addChild_group', openChunk=True)
      opnChnk = True
      ndLst = list()
      for itm in trfLst :
        nd = createTransform(itm.itemUniqueName, nm)
        ndLst.append(nd[0])
        self.core.updateItem(itm)
      if len(ndLst) > 0 : 
        cmds.select(ndLst, replace=True)
        self.core.setSelectedBySelectionList()
    finally :
      if opnChnk : cmds.undoInfo(closeChunk=True)

  def addChild_joint(self) :
    opnChnk = False
    try :
      trfLst = self.filterByHasFnList([OpenMaya.MFn.kTransform])
      nmHint = getShortName(trfLst[0].itemUniqueName)
      ( nm, sts ) = QtWidgets.QInputDialog.getText(self.core, u'create joint', u'name', text=nmHint)
      if nm is None or len(nm) == 0 or sts == False : return
      cmds.undoInfo(chunkName=u'pullDownAddNode.addChild_joint', openChunk=True)
      opnChnk = True
      ndLst = list()
      for itm in trfLst :
        jnt = createJoint(itm.itemUniqueName, nm)
        ndLst.append(jnt[0])
        self.core.updateItem(itm)
      if len(ndLst) > 0 : 
        cmds.select(ndLst, replace=True)
        self.core.setSelectedBySelectionList()
    finally :
      if opnChnk : cmds.undoInfo(closeChunk=True)

  def addRoot_locator(self) :
    opnChnk = False
    try :
      ( nm, sts ) = QtWidgets.QInputDialog.getText(self.core, u'create root locator', u'name', text=u'root')
      if nm is None or len(nm) == 0 or sts == False : return
      cmds.undoInfo(chunkName=u'pullDownAddNode.addRoot_locator', openChunk=True)
      opnChnk = True
      ndNm = createLocator(None, nm)
      dgp = getMDagPathByName(ndNm[0])
      itm = item.itemMDagPath(dgp)
      idx = self.core.getRootMDagPathItemCount()
      self.core.insertTopLevelItem(idx, itm)
      self.core.updateItem(itm)
      cmds.select(ndNm[0], replace=True)
      self.core.setSelectedBySelectionList()
    finally :
      if opnChnk : cmds.undoInfo(closeChunk=True)

  def addRoot_group(self) :
    opnChnk = False
    try :
      ( nm, sts ) = QtWidgets.QInputDialog.getText(self.core, u'create root group', u'name', text=u'root')
      if nm is None or len(nm) == 0 or sts == False : return
      cmds.undoInfo(chunkName=u'pullDownAddNode.addRoot_group', openChunk=True)
      opnChnk = True
      ndNm = createTransform(None, nm)
      dgp = getMDagPathByName(ndNm[0])
      itm = item.itemMDagPath(dgp)
      idx = self.core.getRootMDagPathItemCount()
      self.core.insertTopLevelItem(idx, itm)
      self.core.updateItem(itm)
      cmds.select(ndNm[0], replace=True)
      self.core.setSelectedBySelectionList()
    finally :
      if opnChnk : cmds.undoInfo(closeChunk=True)

  def addRoot_joint(self) :
    opnChnk = False
    try :
      ( nm, sts ) = QtWidgets.QInputDialog.getText(self.core, u'create root joint', u'name', text=u'j_root')
      if nm is None or len(nm) == 0 or sts == False : return
      cmds.undoInfo(chunkName=u'pullDownAddNode.addRoot_joint', openChunk=True)
      opnChnk = True
      ndNm = createJoint(None, nm)
      dgp = getMDagPathByName(ndNm[0])
      itm = item.itemMDagPath(dgp)
      idx = self.core.getRootMDagPathItemCount()
      self.core.insertTopLevelItem(idx, itm)
      self.core.updateItem(itm)
      cmds.select(ndNm[0], replace=True)
      self.core.setSelectedBySelectionList()
    finally :
      if opnChnk : cmds.undoInfo(closeChunk=True)

  def add_ikHandle(self) :
    opnChnk = False
    try :
      jntLst = self.filterByHasFnList([OpenMaya.MFn.kJoint])
      startJntNdNm = jntLst[0].itemUniqueName
      endJntNdNm = jntLst[1].itemUniqueName
      endJntSn = getShortName(endJntNdNm)
      cmds.undoInfo(chunkName=u'pullDownAddNode.add_ikHandle', openChunk=True)
      opnChnk = True
      pfx = u'ikh_'
      lst = cmds.ikHandle(startJoint=startJntNdNm, endEffector=endJntNdNm, name=pfx + endJntSn)
      ikEfNd = getFullName(lst[0])
      dgp = getMDagPathByName(ikEfNd)
      itm = item.itemMDagPath(dgp)
      idx = self.core.getRootMDagPathItemCount()
      self.core.insertTopLevelItem(idx, itm)
      if len(lst) == 2 : 
        pfx = u'eff_'
        cmds.rename(lst[1], pfx + endJntSn)
        jntLst[0].updateConnection()
        self.core.updateItem(jntLst[0])
      cmds.select(lst[0], replace=True)
      self.core.setSelectedBySelectionList()
    finally :
      if opnChnk : cmds.undoInfo(closeChunk=True)

  def addDecompose_worldMatrix(self) : 
    opnChnk = False
    try :
      trfLst = self.filterByHasFnList([OpenMaya.MFn.kTransform])
      cmds.undoInfo(chunkName=u'pullDownAddNode.addDecompose_worldMatrix', openChunk=True)
      opnChnk = True
      for itm in trfLst :
        ndNm = itm.itemUniqueName
        sn = getShortName(ndNm)
        dcMtxNd = cmds.createNode(u'decomposeMatrix', name=u'decomposeMatrix_' + sn + u'_wm', skipSelect=True)
        cmds.connectAttr(plugName(ndNm, (u'worldMatrix', 0)), plugName(dcMtxNd, u'inputMatrix'), force=True)
        mobj = getMObjectByName(dcMtxNd)
        self.core.addMObject(mobj)
        itm.updateConnection()
    finally :
      if opnChnk : cmds.undoInfo(closeChunk=True)


  def addCompose_localMatrix(self) : 
    opnChnk = False
    try :
      trfLst = self.filterByHasFnList([OpenMaya.MFn.kTransform])
      if cmds.pluginInfo(u'quatNodes', query=True, loaded=True) == False : cmds.loadPlugin(u'quatNodes')
      cmds.undoInfo(chunkName=u'pullDownAddNode.addCompose_localMatrix', openChunk=True)
      opnChnk = True
      for itm in trfLst :
        ndNm = itm.itemUniqueName
        sn = getShortName(ndNm)
        mobjLst = list()
        cmMtx = cmds.createNode(u'composeMatrix', name=u'composeMatrix_' + sn + u'_lm', skipSelect=True)
        mobjLst.append(getMObjectByName(cmMtx))
        cmds.connectAttr(plugName(ndNm, u'translate'), plugName(cmMtx, u'inputTranslate'), force=True)
        cmds.connectAttr(plugName(ndNm, u'shear'), plugName(cmMtx, u'inputShear'), force=True)
        cmds.connectAttr(plugName(ndNm, u'scale'), plugName(cmMtx, u'inputScale'), force=True)
        if cmds.objectType(ndNm, isAType=u'joint') : 
          eulQtJo = cmds.createNode(u'eulerToQuat', name=u'eulerToQuat_' + sn + u'_jo', skipSelect=True)
          mobjLst.append(getMObjectByName(eulQtJo))
          cmds.connectAttr(plugName(ndNm, u'jointOrient'), plugName(eulQtJo, u'inputRotate'), force=True)
          eulQtRo = cmds.createNode(u'eulerToQuat', name=u'eulerToQuat_' + sn + u'_ro', skipSelect=True)
          mobjLst.append(getMObjectByName(eulQtRo))
          cmds.connectAttr(plugName(ndNm, u'rotate'), plugName(eulQtRo, u'inputRotate'), force=True)
          cmds.connectAttr(plugName(ndNm, u'rotateOrder'), plugName(eulQtRo, u'inputRotateOrder'), force=True)
          qtPrd = cmds.createNode(u'quatProd', name=u'quatProd_' + sn + u'_joro', skipSelect=True)
          mobjLst.append(getMObjectByName(qtPrd))
          cmds.connectAttr(plugName(eulQtRo, u'outputQuat'), plugName(qtPrd, u'input1Quat'), force=True)
          cmds.connectAttr(plugName(eulQtJo, u'outputQuat'), plugName(qtPrd, u'input2Quat'), force=True)
          cmds.connectAttr(plugName(qtPrd, u'outputQuat'), plugName(cmMtx, u'inputQuat'), force=True)
          cmds.setAttr(plugName(cmMtx, u'useEulerRotation'), False)
        else :
          cmds.connectAttr(plugName(ndNm, u'rotateOrder'), plugName(cmMtx, u'inputRotateOrder'), force=True)
          cmds.connectAttr(plugName(ndNm, u'rotate'), plugName(cmMtx, u'inputRotate'), force=True)
          cmds.setAttr(plugName(cmMtx, u'useEulerRotation'), True)
        for mobj in mobjLst : self.core.addMObject(mobj)
        itm.updateConnection()
    finally :
      if opnChnk : cmds.undoInfo(closeChunk=True)

  def addQuaternion(self) :
    opnChnk = False
    try :
      trfLst = self.filterByHasFnList([OpenMaya.MFn.kTransform])
      if cmds.pluginInfo(u'quatNodes', query=True, loaded=True) == False : cmds.loadPlugin(u'quatNodes')
      cmds.undoInfo(chunkName=u'pullDownAddNode.addQuaternion', openChunk=True)
      opnChnk = True
      for itm in trfLst :
        ndNm = itm.itemUniqueName
        sn = getShortName(ndNm)
        mobjLst = list()
        eulQtRo = cmds.createNode(u'eulerToQuat', name=u'eulerToQuat_' + sn + u'_ro', skipSelect=True)
        mobjLst.append(getMObjectByName(eulQtRo))
        cmds.connectAttr(plugName(ndNm, u'rotate'), plugName(eulQtRo, u'inputRotate'), force=True)
        cmds.connectAttr(plugName(ndNm, u'rotateOrder'), plugName(eulQtRo, u'inputRotateOrder'), force=True)
        if cmds.objectType(ndNm, isAType=u'joint')  : 
          eulQtJo = cmds.createNode(u'eulerToQuat', name=u'eulerToQuat_' + sn + u'_jo', skipSelect=True)
          mobjLst.append(getMObjectByName(eulQtJo))
          cmds.connectAttr(plugName(ndNm, u'jointOrient'), plugName(eulQtJo, u'inputRotate'), force=True)
          qtPrd = cmds.createNode(u'quatProd', name=u'quatProd_' + sn + u'_joro', skipSelect=True)
          mobjLst.append(getMObjectByName(qtPrd))
          cmds.connectAttr(plugName(eulQtRo, u'outputQuat'), plugName(qtPrd, u'input1Quat'), force=True)
          cmds.connectAttr(plugName(eulQtJo, u'outputQuat'), plugName(qtPrd, u'input2Quat'), force=True)
        for mobj in mobjLst : self.core.addMObject(mobj)
        itm.updateConnection()
    finally :
      if opnChnk : cmds.undoInfo(closeChunk=True)
