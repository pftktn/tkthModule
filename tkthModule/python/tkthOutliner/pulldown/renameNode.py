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


class pullDownRename(base.pullDownBase) : 
  def __init__(self, inMenu, inItmLst, inCore) : 
    super().__init__(inMenu, inItmLst, inCore)
    dgpLst = self.filterByItemType(item.itemBase.enMDagPath)
    mobjLst = self.filterByItemType(item.itemBase.enMObject)
    if len(dgpLst) + len(mobjLst) != 1 : raise Exception()
    act = self.menu.addAction(u'rename')
    act.triggered.connect(self.executeRename)

  def executeRename(self) : 
    itm = None
    lst = self.filterByItemType(item.itemBase.enMDagPath)
    if len(lst) == 0 : 
      lst = self.filterByItemType(item.itemBase.enMObject)
    itm = lst[0]
    ndNm = itm.itemUniqueName
    sn = getShortName(ndNm)
    ( nm, sts ) = QtWidgets.QInputDialog.getText(self.core, u'new name', u'name', text=sn)
    if nm is None or len(nm) == 0 or nm == sn or sts == False : return
    try :
      newNm = cmds.rename(ndNm, nm)
      itm.itemUniqueName = getFullName(newNm)
      self.core.updateItem(itm)
    except Exception as e :
      self.logMessage(str(e))

