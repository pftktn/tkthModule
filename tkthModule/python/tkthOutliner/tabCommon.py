import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI

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
from common.qtUtil import * 
from common.jsonUtil import *


class tabCommon(QtWidgets.QWidget) : 
  __core = None
  @property
  def core(self) : return self.__core
  
  def __init__(self, core=None, objectName=None) : 
    super().__init__()
    self.__core = core
    if objectName is not None : self.setObjectName(objectName)

  def reloadContent(self) : pass
  
  def activate(self) : pass
  def deactivate(self) : pass
  
  # def logMessage(self, inMsg) : self.core.logMessage(inMsg)
