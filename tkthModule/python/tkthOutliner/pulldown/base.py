import maya.api.OpenMaya as OpenMaya
import maya.cmds as cmds


from common.apiUtil import *
from common.cmdsUtil import *

from tkthOutliner.core import *

import tkthOutliner.item as item


class pullDownBase(object) : 
  bifrostTypeIdList = [ 0x58000360, 0x80088 ]
  
  __menu = None
  @property
  def menu(self) : return self.__menu
  __itemList = None
  @property
  def itemList(self) : return self.__itemList

  def logMessage(self, inMsg) : logMessage(self.__menu, inMsg)

  __core = None
  @property
  def core(self) : return self.__core

  def __init__(self, inMenu, inItmLst, inCore) : 
    self.__menu = inMenu
    self.__itemList = list(inItmLst)
    self.__core = inCore


  def filterByHasFnList(self, inMFnList) :
    lst = []
    for itm in self.itemList :
      obj = None
      if itm.itemType == item.itemBase.enMObject or itm.itemType == item.itemBase.enMDagPath : obj = itm.getObject()
      if obj is None : continue
      for mfn in inMFnList : 
        if obj.hasFn(mfn) : 
          lst.append(itm)
          break
    return lst

  def filterByItemType(self, inItmTp) : 
    lst = []
    for itm in self.itemList :
      if itm.itemType == inItmTp : lst.append(itm)
    return lst

  def filterByTypeIdList(self, inTypeIdList) : 
    lst = []
    for itm in self.itemList :
      fn = None
      if itm.itemType == item.itemBase.enMObject or itm.itemType == item.itemBase.enMDagPath : fn = itm.getMFn()
      if fn is None : continue
      itmId = fn.typeId.id()
      if itmId in inTypeIdList : lst.append(itm)
    return lst
