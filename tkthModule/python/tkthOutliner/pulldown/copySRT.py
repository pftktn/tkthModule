import math

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


class pullDownCopySRT(base.pullDownBase) : 
  def __init__(self, inMenu, inItmLst, inCore) : 
    super().__init__(inMenu, inItmLst, inCore)
    trfLst = self.filterByItemType(item.itemBase.enMDagPath)
    if len(trfLst) < 2 : raise Exception()
    jntLst = self.filterByHasFnList([OpenMaya.MFn.kJoint])

    subMenu = self.menu.addMenu(u'copy SRT')

    localMenu = subMenu.addMenu(u'local')
    act = localMenu.addAction(u'translate')
    act.triggered.connect(self.copy_localTranslate)
    act = localMenu.addAction(u'rotate')
    act.triggered.connect(self.copy_localRotate)
    act = localMenu.addAction(u'rotateOrder')
    act.triggered.connect(self.copy_localRotateOrder)
    act = localMenu.addAction(u'scale')
    act.triggered.connect(self.copy_localScale)
    act = localMenu.addAction(u'shear')
    act.triggered.connect(self.copy_localShear)
    if len(jntLst) > 1 :
      act = localMenu.addAction(u'jointOrient')
      act.triggered.connect(self.copy_jointOrient)
    act = localMenu.addAction(u'transform')
    act.triggered.connect(self.copy_localTransform)

    worldMenu = subMenu.addMenu(u'world')
    act = worldMenu.addAction(u'translate')
    act.triggered.connect(self.copy_worldTranslate)
    act = worldMenu.addAction(u'rotate')
    act.triggered.connect(self.copy_worldRotate)
    act = worldMenu.addAction(u'scale')
    act.triggered.connect(self.copy_worldScale)
    act = worldMenu.addAction(u'shear')
    act.triggered.connect(self.copy_worldShear)
    act = worldMenu.addAction(u'transform')
    act.triggered.connect(self.copy_worldTransform)

  def set_attribute(self, inDst, inAttrLst, inValLst) : 
    dstNm = inDst.itemUniqueName
    for attr, val in zip(inAttrLst, inValLst) : 
      try : 
        plgNm = plugName(dstNm, attr)
        cmds.setAttr(plgNm, val)
        self.logMessage(u'setAttr ' + getShortPlugName(plgNm) + u' ' + str(val))
      except Exception as e :
        self.logMessage(str(e))


  def copy_attribute(self, inSrc, inDstLst, inAttrLst) : 
    srcValLst = list()
    srcNm = inSrc.itemUniqueName
    for attr in inAttrLst : 
      srcValLst.append(cmds.getAttr(plugName(srcNm, attr)))
    for dst in inDstLst : 
      self.set_attribute(dst, inAttrLst, srcValLst)


  def copy_localTranslate(self) :
    opnUndChk = False
    dstLst = self.filterByItemType(item.itemBase.enMDagPath)
    src = dstLst.pop(0)
    try :
      cmds.undoInfo(chunkName=u'copyLocalTranslate', openChunk=True)
      opnUndChk = True
      attrLst = []
      for xyz in [u'X', u'Y', u'Z'] : attrLst.append(u'translate' + xyz)
      self.copy_attribute(src, dstLst, attrLst)
    finally :
      if opnUndChk : cmds.undoInfo(closeChunk=True)

  def copy_rotate(self, inSrc, inDstLst) : 
    srcNm = inSrc.itemUniqueName
    [xyzLst] = cmds.getAttr(plugName(srcNm, u'rotate'))
    srcRotOrd = cmds.getAttr(plugName(srcNm, u'rotateOrder'))
    srcEul = OpenMaya.MEulerRotation(xyzLst[0]*math.pi/180.0, xyzLst[1]*math.pi/180.0, xyzLst[2]*math.pi/180.0, srcRotOrd)
    srcQt = srcEul.asQuaternion()
    if cmds.objectType(srcNm, isAType=u'joint') :
      [joLst] = cmds.getAttr(plugName(srcNm, u'jointOrient'))
      joEul = OpenMaya.MEulerRotation(joLst[0]*math.pi/180.0, joLst[1]*math.pi/180.0, joLst[2]*math.pi/180.0)
      srcQt = srcQt * joEul.asQuaternion()
      srcEul = srcQt.asEulerRotation()
      if srcEul.order != srcRotOrd : srcEul.reorderIt(srcRotOrd)

    attrLst = list()
    for xyz in [u'X', u'Y', u'Z'] : attrLst.append(u'rotate' + xyz)

    for dst in inDstLst : 

      dstNm = dst.itemUniqueName
      dstEul = None
      dstRotOrd = cmds.getAttr(plugName(dstNm, u'rotateOrder'))
      if cmds.objectType(dstNm, isAType=u'joint') :
        [joLst] = cmds.getAttr(plugName(dstNm, u'jointOrient'))
        joEul = OpenMaya.MEulerRotation(joLst[0]*math.pi/180.0, joLst[1]*math.pi/180.0, joLst[2]*math.pi/180.0)
        tmpQt = srcQt * joEul.asQuaternion().inverse()
        dstEul = tmpQt.asEulerRotation()
        if dstEul.order != dstRotOrd : dstEul.reorderIt(dstRotOrd)
      else :
        dstEul = srcEul
        if dstEul.order != dstRotOrd : dstEul = dstEul.reorder(dstRotOrd)
          
      valLst = [dstEul.x*180.0/math.pi, dstEul.y*180.0/math.pi, dstEul.z*180.0/math.pi]
      self.set_attribute(dst, attrLst, valLst)


  def copy_localRotate(self) : 
    opnUndChk = False
    dstLst = self.filterByItemType(item.itemBase.enMDagPath)
    src = dstLst.pop(0)
    try :
      cmds.undoInfo(chunkName=u'copyLocalRotate', openChunk=True)
      opnUndChk = True
      self.copy_rotate(src, dstLst)
    finally :
      if opnUndChk : cmds.undoInfo(closeChunk=True)


  def copy_localRotateOrder(self) :
    opnUndChk = False
    dstLst = self.filterByItemType(item.itemBase.enMDagPath)
    src = dstLst.pop(0)
    try :
      cmds.undoInfo(chunkName=u'copyRotateOrder', openChunk=True)
      opnUndChk = True
      self.copy_attribute(src, dstLst, [u'rotateOrder'])
    finally :
      if opnUndChk : cmds.undoInfo(closeChunk=True)


  def copy_localScale(self) :
    opnUndChk = False
    dstLst = self.filterByItemType(item.itemBase.enMDagPath)
    src = dstLst.pop(0)
    try :
      cmds.undoInfo(chunkName=u'copyLocalScale', openChunk=True)
      opnUndChk = True
      attrLst = []
      for xyz in [u'X', u'Y', u'Z'] : attrLst.append(u'scale' + xyz)
      self.copy_attribute(src, dstLst, attrLst)
    finally :
      if opnUndChk : cmds.undoInfo(closeChunk=True)


  def copy_localShear(self) :
    opnUndChk = False
    dstLst = self.filterByItemType(item.itemBase.enMDagPath)
    src = dstLst.pop(0)
    try :
      cmds.undoInfo(chunkName=u'copyLocalShear', openChunk=True)
      opnUndChk = True
      attrLst = []
      for xyz in [u'XY', u'XZ', u'YZ'] : attrLst.append(u'shear' + xyz)
      self.copy_attribute(src, dstLst, attrLst)
    finally :
      if opnUndChk : cmds.undoInfo(closeChunk=True)


  def copy_jointOrient(self) :
    opnUndChk = False
    dstLst = self.filterByHasFnList([OpenMaya.MFn.kJoint])
    src = dstLst.pop(0)
    try :
      cmds.undoInfo(chunkName=u'copyJointOrient', openChunk=True)
      opnUndChk = True
      attrLst = []
      for xyz in [u'X', u'Y', u'Z'] : attrLst.append(u'jointOrient' + xyz)
      self.copy_attribute(src, dstLst, attrLst)
    finally :
      if opnUndChk : cmds.undoInfo(closeChunk=True)


  def copy_localTransform(self) :
    opnUndChk = False
    dstLst = self.filterByItemType(item.itemBase.enMDagPath)
    src = dstLst.pop(0)
    try :
      cmds.undoInfo(chunkName=u'copyLocalTransform', openChunk=True)
      opnUndChk = True

      attrLst = []
      for xyz in [u'X', u'Y', u'Z'] : attrLst.append(u'translate' + xyz)
      self.copy_attribute(src, dstLst, attrLst)
      attrLst = []
      for xyz in [u'X', u'Y', u'Z'] : attrLst.append(u'scale' + xyz)
      self.copy_attribute(src, dstLst, attrLst)
      attrLst = []
      for xyz in [u'XY', u'XZ', u'YZ'] : attrLst.append(u'shear' + xyz)
      self.copy_attribute(src, dstLst, attrLst)
      self.copy_rotate(src, dstLst)
      
    finally :
      if opnUndChk : cmds.undoInfo(closeChunk=True)


  def copy_worldTranslate(self) :
    opnUndChk = False
    dstLst = self.filterByItemType(item.itemBase.enMDagPath)
    src = dstLst.pop(0)
    try :
      trf = OpenMaya.MTransformationMatrix(src.getWorldMatrix())
      srcPos = OpenMaya.MPoint(trf.translation(OpenMaya.MSpace.kTransform))
    
      attrLst = []
      for xyz in [u'X', u'Y', u'Z'] : attrLst.append(u'translate' + xyz)
    
      cmds.undoInfo(chunkName=u'copyWorldTranslate', openChunk=True)
      for dst in dstLst : 
        dstInvMtx = dst.getParentInverseMatrix()
        dstPos = srcPos * dstInvMtx
        self.set_attribute(dst, attrLst, [dstPos.x, dstPos.y, dstPos.z])
    finally :
      if opnUndChk : cmds.undoInfo(closeChunk=True)


  def copy_worldRotate(self) :
    opnUndChk = False
    dstLst = self.filterByItemType(item.itemBase.enMDagPath)
    src = dstLst.pop(0)
    try :
      trf = OpenMaya.MTransformationMatrix(src.getWorldMatrix())
      srcQt = trf.rotation(asQuaternion=True)

      attrLst = []
      for xyz in [u'X', u'Y', u'Z'] : attrLst.append(u'rotate' + xyz)

      cmds.undoInfo(chunkName=u'copyWorldRotate', openChunk=True)
      opnUndChk = True
      for dst in dstLst : 
        dstNm = dst.itemUniqueName
        dstInvMtx = dst.getParentInverseMatrix()
        trf = OpenMaya.MTransformationMatrix(dstInvMtx)
        dstRotOrd = cmds.getAttr(plugName(dstNm, u'rotateOrder'))
        dstQt = trf.rotation(asQuaternion=True) * srcQt
        dstEul = None
        if cmds.objectType(dstNm, isAType=u'joint') :
          [joLst] = cmds.getAttr(plugName(dstNm, u'jointOrient'))
          joEul = OpenMaya.MEulerRotation(joLst[0]*math.pi/180.0, joLst[1]*math.pi/180.0, joLst[2]*math.pi/180.0)
          dstQt = joEul.asQuaternion().inverse() * dstQt
          dstEul = dstQt.asEulerRotation()
          if dstEul.order != dstRotOrd : dstEul.reorderIt(dstRotOrd)
        else :
          dstEul = dstQt.asEulerRotation()
          if dstEul.order != dstRotOrd : dstEul.reorderIt(dstRotOrd)

        self.set_attribute(dst, attrLst, [dstEul.x, dstEul.y, dstEul.z])
    finally :
      if opnUndChk : cmds.undoInfo(closeChunk=True)


  def copy_worldScale(self) :
    opnUndChk = False
    dstLst = self.filterByItemType(item.itemBase.enMDagPath)
    src = dstLst.pop(0)
    try :
      srcWMtx = src.getWorldMatrix()

      attrLst = []
      for xyz in [u'X', u'Y', u'Z'] : attrLst.append(u'scale' + xyz)

      cmds.undoInfo(chunkName=u'copyWorldScale', openChunk=True)
      opnUndChk = True
      print(u'copy world scale from:' + self.getNodeName(src))
      for dst in dstLst : 
        dstInvMtx = dst.getParentInverseMatrix()
        dstMtx = dstInvMtx * srcWMtx
        trf = OpenMaya.MTransformationMatrix(dstMtx)
        xyz = trf.scale(OpenMaya.MSpace.kTransform)
        self.set_attribute(dst, attrLst, xyz)
    finally :
      if opnUndChk : cmds.undoInfo(closeChunk=True)


  def copy_worldShear(self) :
    opnUndChk = False
    dstLst = self.filterByItemType(item.itemBase.enMDagPath)
    src = dstLst.pop(0)
    try :
      srcWMtx = src.getWorldMatrix()

      attrLst = []
      for xyz in [u'XY', u'XZ', u'YZ'] : attrLst.append(u'shear' + xyz)

      cmds.undoInfo(chunkName=u'copyWorldShear', openChunk=True)
      opnUndChk = True
      for dst in dstLst : 
        dstInvMtx = dst.getParentInverseMatrix()
        dstMtx = dstInvMtx * srcWMtx
        trf = OpenMaya.MTransformationMatrix(dstMtx)
        xyz = trf.shear(OpenMaya.MSpace.kTransform)
        self.set_attribute(dst, attrLst, xyz)
    finally :
      if opnUndChk : cmds.undoInfo(closeChunk=True)


  def copy_worldTransform(self) :
    opnUndChk = False
    dstLst = self.filterByItemType(item.itemBase.enMDagPath)
    src = dstLst.pop(0)
    try :
      srcWMtx = src.getWorldMatrix()

      trnAttrLst = []
      rotAttrLst = []
      sclAttrLst = []
      for xyz in [u'X', u'Y', u'Z'] : 
        trnAttrLst.append(u'translate' + xyz)
        rotAttrLst.append(u'rotate' + xyz)
        sclAttrLst.append(u'scale' + xyz)

      shrAttrLst = []
      for xyz in [u'XY', u'XZ', u'YZ'] : shrAttrLst.append(u'shear' + xyz)

      cmds.undoInfo(chunkName=u'copyWorldTransform', openChunk=True)
      opnUndChk = True
      for dst in dstLst : 
        dstNm = dst.itemUniqueName
        dstInvMtx = dst.getParentInverseMatrix()
        dstMtx = srcWMtx * dstInvMtx
        trf = OpenMaya.MTransformationMatrix(dstMtx)
        dstTrn = trf.translation(OpenMaya.MSpace.kTransform)

        dstRotOrd = cmds.getAttr(plugName(dstNm, u'rotateOrder'))
        dstQt = trf.rotation(asQuaternion=True)
        dstEul = None
        if cmds.objectType(dstNm, isAType=u'joint') :
          [joLst] = cmds.getAttr(plugName(dstNm, u'jointOrient'))
          joEul = OpenMaya.MEulerRotation(joLst[0]*math.pi/180.0, joLst[1]*math.pi/180.0, joLst[2]*math.pi/180.0)
          dstQt = joEul.asQuaternion().inverse() * dstQt
          dstEul = dstQt.asEulerRotation()
          if dstEul.order != dstRotOrd : dstEul.reorderIt(dstRotOrd)
        else :
          dstEul = dstQt.asEulerRotation()
          if dstEul.order != dstRotOrd : dstEul.reorderIt(dstRotOrd)

        dstScl = trf.scale(OpenMaya.MSpace.kTransform)
        dstShr = trf.shear(OpenMaya.MSpace.kTransform)
        
        self.set_attribute(dst, trnAttrLst, [dstTrn.x, dstTrn.y, dstTrn.z])
        self.set_attribute(dst, rotAttrLst, [dstEul.x*180.0/math.pi, dstEul.y*180.0/math.pi, dstEul.z*180.0/math.pi])
        self.set_attribute(dst, sclAttrLst, dstScl)
        self.set_attribute(dst, shrAttrLst, dstShr)
    finally :
      if opnUndChk : cmds.undoInfo(closeChunk=True)

