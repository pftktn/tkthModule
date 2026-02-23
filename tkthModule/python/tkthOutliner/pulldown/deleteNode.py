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


class pullDownDelete(base.pullDownBase) : 
  def __init__(self, inMenu, inItmLst, inCore) : 
    super().__init__(inMenu, inItmLst, inCore)
    dgpLst = self.filterByItemType(item.itemBase.enMDagPath)
    mobjLst = self.filterByItemType(item.itemBase.enMObject)
    if len(dgpLst) + len(mobjLst) == 0 : raise Exception()
    act = self.menu.addAction(u'delete')
    act.triggered.connect(self.executeDelete)

  def executeDelete(self) : 
    opnChk = False
    try : 
      lst = self.filterByItemType(item.itemBase.enMDagPath)
      lst.extend(self.filterByItemType(item.itemBase.enMObject))
      nmInf = u''
      nmLst = []
      for itm in lst : 
        sn = getShortNameWithNamespace(itm.itemUniqueName)
        nmLst.append(itm.itemUniqueName)
        nmInf = nmInf + u',' + sn
      
      if len(nmLst) == 0 : return
      nmInf = nmInf[1:]
      if len(nmInf) > 40 :
        nmInf = u'node(s):' + nmInf[:40] + u'...'
      else :
        nmInf = u'node(s):' + nmInf
      retVal = QtWidgets.QMessageBox.warning(self.core, u'delete selected node(s).', nmInf, buttons=QtWidgets.QMessageBox.Ok|QtWidgets.QMessageBox.Cancel)
      if retVal != QtWidgets.QMessageBox.Ok : return

      cmds.undoInfo(chunkName=u'pullDownDelete.executeDelete', openChunk=True)
      opnChk = True
      for nm in nmLst : 
        try : 
          if cmds.objExists(nm) == False :
            self.logMessage(u'skip not exist:' + nm)
            continue
          cmds.delete(nm)
          self.logMessage(u'delete ' + nm)
        except : 
          self.logMessage(u'failed delete:' + nm)

      for itm in lst : 
        prtItm = itm.parent()
        if prtItm is not None : 
          chIdx = prtItm.indexOfChild(itm)
          prtItm.takeChild(chIdx)
        else : 
          topIdx = self.core.indexOfTopLevelItem(itm)
          self.core.takeTopLevelItem(topIdx)
    finally : 
      if opnChk : cmds.undoInfo(closeChunk=True)
