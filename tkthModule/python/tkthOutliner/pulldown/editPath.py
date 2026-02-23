import pathlib

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


class pullDownEditPath(base.pullDownBase) : 
  def __init__(self, inMenu, inItmLst, inCore) : 
    super().__init__(inMenu, inItmLst, inCore)
    plgLst = self.filterByHasFnList([OpenMaya.MFn.kPluginDependNode])
    refLst = self.filterByHasFnList([OpenMaya.MFn.kReference])
    if len(refLst) + len(plgLst) != 1 : raise Exception()
    if len(refLst) == 1 :
      act = self.menu.addAction(u'edit path')
      act.triggered.connect(self.editPath)
    if len(plgLst) == 1 :
      act = self.menu.addAction(u'check path')
      act.triggered.connect(self.checkPath)

  def editPath(self) :
    refLst = self.filterByHasFnList([OpenMaya.MFn.kReference])
    refNd = refLst[0].itemUniqueName
    refPth = pathlib.Path(cmds.referenceQuery(refNd, filename=True))
    retVal = QtWidgets.QFileDialog.getOpenFileName(parent=self.core, caption=u'select file', dir=refPth.parent.as_posix(), filter=u'original (' + refPth.name + u');;scene file (*.mb *.ma *.fbx);;all (*.*)')
    if retVal is not None and len(retVal[0]) > 0 : 
      newPth = pathlib.Path(retVal[0])
      if newPth.as_posix() != refPth.as_posix() :
        cmds.file(newPth.as_posix(), loadReference=refNd, prompt=False)

  def checkPath(self) : 
    plgLst = self.filterByHasFnList([OpenMaya.MFn.kPluginDependNode])
    fn = plgLst[0].getMFn()
    if fn is None : return
    pth = fn.pluginName
    if pth is None or len(pth) == 0 : return
    plgPth = pathlib.Path(pth)
    QtWidgets.QFileDialog.getOpenFileName(parent=self.core, caption=u'check path', dir=plgPth.parent.as_posix(), filter=u'original (' + plgPth.name + u');;all (*.*)')
  
