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


class pullDownChangeRotateOrder(base.pullDownBase) : 
  def __init__(self, inMenu, inItmLst, inCore) : 
    super().__init__(inMenu, inItmLst, inCore)
    trfLst = self.filterByHasFnList([OpenMaya.MFn.kTransform])
    if len(trfLst) < 1 : raise Exception()

    subMenu = self.menu.addMenu(u'change rotateOrder')
    act = subMenu.addAction(u'xyz')
    act.triggered.connect(self.change_rotOrdToXYZ)
    act = subMenu.addAction(u'yzx')
    act.triggered.connect(self.change_rotOrdToYZX)
    act = subMenu.addAction(u'zxy')
    act.triggered.connect(self.change_rotOrdToZXY)
    act = subMenu.addAction(u'xzy')
    act.triggered.connect(self.change_rotOrdToXZY)
    act = subMenu.addAction(u'yxz')
    act.triggered.connect(self.change_rotOrdToYXZ)
    act = subMenu.addAction(u'zyx')
    act.triggered.connect(self.change_rotOrdToZYX)

  def change_rotOrdTo(self, inRotOrd) : 
    opnUndChk = False
    trfItmLst = self.filterByItemType(item.itemBase.enMDagPath)
    try :
      chkLckLst = [ u'rotate', u'rotateX', u'rotateY', u'rotateZ', u'rotateOrder' ]
      for itm in trfItmLst :
        ndNm = itm.itemUniqueName
        lcked = False
        for plg in chkLckLst :
          if cmds.getAttr(plugName(ndNm, plg), lock=True) :
            lcked = True
            break
        if lcked : 
          self.logMessage(u'skip rotate locked:' + ndNm)
          continue
        rotOrd = cmds.getAttr(plugName(ndNm, u'rotateOrder'))
        if rotOrd == inRotOrd : 
          self.logMessage(u'skip same rotateOrder:' + ndNm)
          continue

        if opnUndChk == False :
          cmds.undoInfo(chunkName=u'chaneRotateOrder', openChunk=True)
          opnUndChk = True
        
        [xyz] = cmds.getAttr(plugName(ndNm, u'rotate'))
        eul = OpenMaya.MEulerRotation(xyz[0]*math.pi/180.0, xyz[1]*math.pi/180.0, xyz[2]*math.pi/180.0, rotOrd)
        eul.reorderIt(inRotOrd)
        xyz = [ eul.x*180.0/math.pi, eul.y*180.0/math.pi, eul.z*180.0/math.pi ]
        cmds.setAttr(plugName(ndNm, u'rotate'), xyz[0], xyz[1], xyz[2], type=u'double3')
        cmds.setAttr(plugName(ndNm, u'rotateOrder'), inRotOrd)
        self.logMessage(u'setAttr ' + plugName(itm.itemName, u'rotate') + u' ' + str(xyz))
        self.logMessage(u'setAttr ' + plugName(itm.itemName, u'rotateOrder') + u' ' + str(inRotOrd))
    finally :
      if opnUndChk : cmds.undoInfo(closeChunk=True)

  def change_rotOrdToXYZ(self) : self.change_rotOrdTo(OpenMaya.MEulerRotation.kXYZ)

  def change_rotOrdToYZX(self) : self.change_rotOrdTo(OpenMaya.MEulerRotation.kYZX)

  def change_rotOrdToZXY(self) : self.change_rotOrdTo(OpenMaya.MEulerRotation.kZXY)
  
  def change_rotOrdToXZY(self) : self.change_rotOrdTo(OpenMaya.MEulerRotation.kXZY)
  
  def change_rotOrdToYXZ(self) : self.change_rotOrdTo(OpenMaya.MEulerRotation.kYXZ)

  def change_rotOrdToZYX(self) : self.change_rotOrdTo(OpenMaya.MEulerRotation.kZYX)

