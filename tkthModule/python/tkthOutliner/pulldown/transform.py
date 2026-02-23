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


from tkthOutliner.pulldown.changeRotateOrder import *
from tkthOutliner.pulldown.copySRT import *
from tkthOutliner.pulldown.jointOrient import *
from tkthOutliner.pulldown.createConstraint import *
from tkthOutliner.pulldown.parentNode import *
from tkthOutliner.pulldown.setNodeColor import *


class pullDownTransform(base.pullDownBase) : 
  __pullDownChangeRotateOrder = None
  __pullDownCopySRT = None
  __pullDownJointOrient = None
  __pullDownCreateConstraint = None
  __pullDownParent = None
  __pullDownSetNodeColor = None
  
  def __init__(self, inMenu, inItmLst, inCore) : 
    super().__init__(inMenu, inItmLst, inCore)
    trfLst = self.filterByItemType(item.itemBase.enMDagPath)
    if len(trfLst) == 0 : raise Exception()

    subMenu = self.menu.addMenu(u'transform')
    try :
      self.__pullDownChangeRotateOrder = pullDownChangeRotateOrder(subMenu, inItmLst, inCore)
    except : pass
    try :
      self.__pullDownCopySRT = pullDownCopySRT(subMenu, inItmLst, inCore)
    except : pass
    try :
      self.__pullDownJointOrient = pullDownJointOrient(subMenu, inItmLst, inCore)
    except : pass
    try :
      self.__pullDownCreateConstraint = pullDownCreateConstraint(subMenu, inItmLst, inCore)
    except : pass
    try :
      self.__pullDownParent = pullDownParent(subMenu, inItmLst, inCore)
    except : pass
    try :
      self.__pullDownSetNodeColor = pullDownSetNodeColor(subMenu, inItmLst, inCore)
    except : pass

