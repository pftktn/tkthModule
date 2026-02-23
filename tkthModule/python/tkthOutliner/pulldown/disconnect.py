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


class pullDownDisconnect(base.pullDownBase) : 
  def __init__(self, inMenu, inItmLst, inCore) : 
    super().__init__(inMenu, inItmLst, inCore)
    cnnLst = self.filterByItemType(item.itemBase.enConnection)
    if len(cnnLst) == 0 : raise Exception()
    act = self.menu.addAction(u'disconnect')
    act.triggered.connect(self.executeDisconnect)

  def executeDisconnect(self) : 
    opnChnk = False
    try :
      cnnLst = self.filterByItemType(item.itemBase.enConnection)
      cmds.undoInfo(chunkName=u'pullDownDisconnect.disconnect', openChunk=True)
      opnChnk = True
      updItmLst = list()
      for cnn in cnnLst : 
        srcPlg = None
        dstPlg = None
        if cnn.targetIsSource : 
          srcPlg = cnn.targetPlugPath
          dstPlg = cnn.plugPath
        else :
          dstPlg = cnn.targetPlugPath
          srcPlg = cnn.plugPath

        cmds.disconnectAttr(srcPlg, dstPlg)
        self.logMessage(u'disconnectAttr ' + srcPlg + u' ' + dstPlg)

        prtItm = cnn.parent()
        if prtItm is not None : 
          prtItm = prtItm.parent()
          if prtItm is not None : updItmLst.append(prtItm)

        tgtPlg = getMPlugByName(cnn.targetPlugPath)
        if tgtPlg is not None and tgtPlg.isNull == False : 
          tgtItm = cnn.findEntityItem(tgtPlg.node())
          if tgtItm is not None : updItmLst.append(tgtItm)

      for updItm in updItmLst : updItm.updateConnection()
    finally :
      if opnChnk : cmds.undoInfo(closeChunk=True)

  
