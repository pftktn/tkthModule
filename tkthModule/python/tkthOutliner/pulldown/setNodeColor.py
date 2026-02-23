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
from common.qtColor import *

import tkthOutliner.item as item

import tkthOutliner.pulldown.base as base


class setNodeColor(object) : 
  __index = None
  __rgb = None
  __rgbF = None
  __itemList = None
  def __init__(self, inIndex, inRGB, inItemList) : 
    self.__index = inIndex
    self.__rgb = list(inRGB)
    self.__rgbF = [0.0] * 3
    for idx in range(3) : 
      self.__rgbF[idx] = float(self.__rgb[idx]) / 255.0
      if self.__rgbF[idx] > 1.0 : self.__rgbF[idx] = 1.0
    self.__itemList = list(inItemList)
  
  def execute(self) : 
    try : 
      cmds.undoInfo(chunkName=u'setNodeColor', openChunk=True)
      for itm in self.__itemList : 
        try : 
          ndLst = [ itm.itemUniqueName ]
          shpLst = cmds.listRelatives(ndLst[0], fullPath=True, shapes=True)
          if shpLst is not None : ndLst.extend(shpLst)
          for nd in ndLst : 
            try : 
              cmds.setAttr(plugName(nd, u'useOutlinerColor'), True)
              cmds.setAttr(plugName(nd, u'outlinerColor'), self.__rgbF[0], self.__rgbF[1], self.__rgbF[2], type=u'float3')
            except : 
              cmds.warning(u'set error:' + plugName(nd, u'outlinerColor'))
            try : 
              cmds.setAttr(plugName(nd, u'overrideEnabled'), True)
              cmds.setAttr(plugName(nd, u'overrideRGBColors'), False)
              cmds.setAttr(plugName(nd, u'overrideColor'), self.__index)
            except : 
              cmds.warning(u'set error:' + plugName(nd, u'overrideColor'))
          itm.updateColor()
        except : 
          cmds.warning(u'listRelatives error:' + ndLst[0])
    finally : 
      cmds.undoInfo(closeChunk=True)


class pullDownSetNodeColor(base.pullDownBase) : 
  __actSetNodeColorList = None
  
  def __init__(self, inMenu, inItmLst, inCore) : 
    super().__init__(inMenu, inItmLst, inCore)
    trfLst = self.filterByItemType(item.itemBase.enMDagPath)
    if len(trfLst) < 1 : raise Exception()

    subMenu = self.menu.addMenu(u'set color')
    redMenu = subMenu.addMenu(u'red')
    greenMenu = subMenu.addMenu(u'green')
    blueMenu = subMenu.addMenu(u'blue')
    grayMenu = subMenu.addMenu(u'gray')
    
    self.__actSetNodeColorList = list()
    for idx, col in enumerate(qtDrawingOverridesColor.mayaDOColorList) : 
      # [ u'gray', [120, 120, 120] ]
      rgb = col[1]
      ctr = (rgb[0] + rgb[1] + rgb[2]) / 3
      dff = math.fabs(rgb[0] - ctr) + math.fabs(rgb[1] - ctr) + math.fabs(rgb[2] - ctr)
      if dff < 10.0 : 
        colMenu = grayMenu
      elif rgb[0] >= rgb[1] and rgb[0] >= rgb[2] : 
        colMenu = redMenu
      elif rgb[1] >= rgb[0] and rgb[1] >= rgb[2] : 
        colMenu = greenMenu
      else : 
        colMenu = blueMenu
      
      pxmp = QtGui.QPixmap(8,8)
      pxmp.fill(QtGui.QColor(rgb[0], rgb[1], rgb[2]))
      icn = QtGui.QIcon(pxmp)
      act = colMenu.addAction(icn, col[0])
      self.__actSetNodeColorList.append(setNodeColor(idx, rgb, trfLst))
      act.triggered.connect(self.__actSetNodeColorList[-1].execute)
