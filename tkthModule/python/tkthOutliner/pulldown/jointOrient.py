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


class pullDownJointOrient(base.pullDownBase) : 
  def __init__(self, inMenu, inItmLst, inCore) : 
    super().__init__(inMenu, inItmLst, inCore)
    jntLst = self.filterByHasFnList([OpenMaya.MFn.kJoint])
    if len(jntLst) < 1 : raise Exception()
    act = self.menu.addAction(u'rotate to jointOrient')
    act.triggered.connect(self.rotateToJointOrient)
    act = self.menu.addAction(u'jointOrient to rotate')
    act.triggered.connect(self.jointOrientToRotate)

  def rotateToJointOrient(self) :
    jntLst = self.filterByHasFnList([OpenMaya.MFn.kJoint])
    for itm in jntLst :
      try : 
        jnt = itm.itemUniqueName
        attrLocked = False
        for attr in [ u'rotate', u'jointOrient' ] :
          if cmds.getAttr(plugName(jnt, attr), lock=True) : 
            attrLocked = True
            break
          for xyz in [ u'X', u'Y', u'Z' ] :
            if cmds.getAttr(plugName(jnt, attr + xyz), lock=True) : 
              attrLocked = True
              break
          if attrLocked : break
        if attrLocked :
          self.logMessage(u'rotate or jointOrient locked:' + jnt)
          continue
        
        [xyz] = cmds.getAttr(plugName(jnt, u'rotate'))
        rotOrd = cmds.getAttr(plugName(jnt, u'rotateOrder'))
        eul = OpenMaya.MEulerRotation(xyz[0]*math.pi/180.0, xyz[1]*math.pi/180.0, xyz[2]*math.pi/180.0, rotOrd)
        qt = eul.asQuaternion()
        [xyz] = cmds.getAttr(plugName(jnt, u'jointOrient'))
        eul = OpenMaya.MEulerRotation(xyz[0]*math.pi/180.0, xyz[1]*math.pi/180.0, xyz[2]*math.pi/180.0, OpenMaya.MEulerRotation.kXYZ)
        qt = qt * eul.asQuaternion()
        eul = qt.asEulerRotation()
        if eul.order != OpenMaya.MEulerRotation.kXYZ : eul.reorderIt(OpenMaya.MEulerRotation.kXYZ)
        cmds.setAttr(plugName(jnt, u'rotate'), 0.0, 0.0, 0.0, type=u'double3')
        cmds.setAttr(plugName(jnt, u'jointOrient'), eul.x*180.0/math.pi, eul.y*180.0/math.pi, eul.z*180.0/math.pi, type=u'double3')
      except Exception as e :
        self.logMessage(str(e))

  def jointOrientToRotate(self) :
    jntLst = self.filterByHasFnList([OpenMaya.MFn.kJoint])
    for itm in jntLst :
      try : 
        jnt = itm.itemUniqueName
        attrLocked = False
        for attr in [ u'rotate', u'jointOrient' ] :
          if cmds.getAttr(plugName(jnt, attr), lock=True) : 
            attrLocked = True
            break
          for xyz in [ u'X', u'Y', u'Z' ] :
            if cmds.getAttr(plugName(jnt, attr + xyz), lock=True) : 
              attrLocked = True
              break
          if attrLocked : break
        if attrLocked :
          self.logMessage(u'rotate or jointOrient locked:' + jnt)
          continue
        
        [xyz] = cmds.getAttr(plugName(jnt, u'rotate'))
        rotOrd = cmds.getAttr(plugName(jnt, u'rotateOrder'))
        eul = OpenMaya.MEulerRotation(xyz[0]*math.pi/180.0, xyz[1]*math.pi/180.0, xyz[2]*math.pi/180.0, rotOrd)
        qt = eul.asQuaternion()
        [xyz] = cmds.getAttr(plugName(jnt, u'jointOrient'))
        eul = OpenMaya.MEulerRotation(xyz[0]*math.pi/180.0, xyz[1]*math.pi/180.0, xyz[2]*math.pi/180.0, OpenMaya.MEulerRotation.kXYZ)
        qt = qt * eul.asQuaternion()
        eul = qt.asEulerRotation()
        if eul.order != rotOrd : eul.reorderIt(rotOrd)
        cmds.setAttr(plugName(jnt, u'rotate'), eul.x*180.0/math.pi, eul.y*180.0/math.pi, eul.z*180.0/math.pi, type=u'double3')
        cmds.setAttr(plugName(jnt, u'jointOrient'), 0.0, 0.0, 0.0, type=u'double3')
      except Exception as e :
        self.logMessage(str(e))

