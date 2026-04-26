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

from common.qtUtil import * 
from common.qtColor import * 
from common.apiUtil import * 
from common.cmdsUtil import *

from tkthOutliner.core import *


class itemBase(QtWidgets.QTreeWidgetItem) : 
  #def logMessage(self, inMsg) : 
  #  try : 
  #    coreObj = self.getCoreObject()
  #    if coreObj is not None : coreObj.logMessage(inMsg)
  #  except : pass
  
  enInvalid = -1
  enMDagPath = 0
  enMObject = 1
  enMObjectFolder = 2
  enShapeFolder = 3
  enConnection = 4
  enSourceFolder = 5
  enDestinationFolder = 6
  __itemType = None
  @property
  def itemType(self) : return self.__itemType

  @property
  def isEntityType(self) : return self.__itemType == itemBase.enMDagPath or self.__itemType == itemBase.enMObject 

  @property
  def itemName(self) : 
    lst = self.text(0).split(u' ')
    return lst[0]

  def findChildByName(self, inNm, itemType=None) : 
    chCnt = self.childCount()
    for chIdx in range(chCnt) : 
      chWgt = self.child(chIdx)
      if itemType is not None and chWgt.itemType != itemType : continue
      if chWgt.itemName == inNm : return chWgt
    return None
  def findChildByType(self, inTp) : 
    chCnt = self.childCount()
    for chIdx in range(chCnt) : 
      chWgt = self.child(chIdx)
      if chWgt.itemType == inTp : return chWgt
    return None
    
  def insertChildBySorted(self, inItm) : 
    itmNm = inItm.itemName
    chCnt = self.childCount()
    for chIdx in range(chCnt) : 
      chItm = self.child(chIdx)
      chItmNm = chItm.itemName
      if chItmNm[0] == u'<' and chItmNm[-1] == u'>' : continue
      if itmNm < chItmNm : 
        self.insertChild(chIdx, inItm)
        return chIdx
    self.addChild(inItm)
    return chCnt
    
  __itemUniqueName = None
  @property
  def itemUniqueName(self) : return self.__itemUniqueName
  @itemUniqueName.setter
  def itemUniqueName(self, inV) : 
    if self.itemType != itemBase.enMDagPath and self.itemType != itemBase.enMObject : return
    self.__itemUniqueName = inV
    self.setText(0, getShortNameWithNamespace(self.__itemUniqueName))

  __mfnType = None
  @property
  def mfnType(self) : return self.__mfnType

  __isDagNode = False
  @property
  def isDagNode(self) : return self.__isDagNode

  def __init__(self, itemType=None, itemFlags=QtCore.Qt.ItemFlag.ItemIsEnabled, isDagNode=False, itemUniqueName=None, itemName=None, mfnType=None):
    super(__class__, self).__init__()
    if itemType is None : self.__itemType = itemBase.enInvalid
    else : self.__itemType = itemType
    self.setText(0, itemName)
    self.setFlags(itemFlags)
    self.__isDagNode = isDagNode
    self.__itemUniqueName = itemUniqueName
    self.__mfnType = mfnType
    
  def updateItemName(self, inMObj) : 
    fn = OpenMaya.MFnDependencyNode(inMObj)
    nm = fn.absoluteName()
    if self.itemType == itemBase.enMDagPath : 
      self.setText(0, nm[1:])
    elif self.itemType == itemBase.enMObject : 
      self.setText(0, nm)

    
  def addUUIDTable(self, child) : 
    treeWgt = self.treeWidget()
    if treeWgt is None : return False
    treeWgt.addUUIDTable(child)
    return True

  def deleteUUIDTable(self, child) : 
    treeWgt = self.treeWidget()
    if treeWgt is None : return False
    treeWgt.deleteUUIDTable(child)
    return True

  def addChildSorted(self, child) : 
    chCnt = self.childCount()
    if chCnt > 0 : 
      chTxt = child.text(0)
      for chIdx in range(chCnt) : 
        if chTxt < self.child(chIdx).text(0) : 
          return self.insertChild(chIdx, child)
    return self.addChild(child)

  def addChild(self, child) :
    self.addUUIDTable(child)
    return super().addChild(child)
  def addChildren(self, children):
    for itm in children : 
      self.addUUIDTable(itm)
    return super().addChildren(children)
  def insertChild(self, index, child):
    self.addUUIDTable(child)
    return super().insertChild(index, child)
  def insertChildren(self, index, children):
    for itm in children : 
      self.addUUIDTable(itm)
    return super().insertChildren(index, children)
  def takeChild(self, index):
    itm = self.child(index)
    if itm is not None : self.deleteUUIDTable(itm)
    return super().takeChild(index)
  def takeChildren(self):
    chCnt = self.childCount()
    for chIdx in range(chCnt) : 
      itm = self.child(chIdx)
      if itm is not None : self.deleteUUIDTable(itm)
    return super().takeChildren()
    
  def getObject(self) : 
    if self.itemUniqueName is None : return None    
    if self.mfnType is None : return None
    if self.isDagNode : return getMDagPathByName(self.itemUniqueName)
    else : return getMObjectByName(self.itemUniqueName)
    
  def getMFn(self) : 
    obj = self.getObject()
    if obj is not None : 
      if type(obj) == OpenMaya.MDagPath : 
        if obj.hasFn(OpenMaya.MFn.kTransform) : 
          try : 
            fn = OpenMaya.MFnDagNode(obj)
            return fn
          except : pass
        else : 
          try : 
            fn = OpenMaya.MFnDependencyNode(obj.node())
            return fn
          except : pass

      try : 
        fn = OpenMaya.MFnDependencyNode(obj)
        return fn
      except : pass
    return None
    
  __uniqueUUID = None
  @property
  def uniqueUUID(self) : return self.__uniqueUUID
  
  def setUniqueUUID(self, fn=None, fnRefList=None) : 
    if fn is None : 
      fn = self.getMFn()
      if fn is None : return None
    self.__uniqueUUID = UniqueMayaUUID(fn, fnRefList=fnRefList)
    return self.__uniqueUUID
    
  def getStatusBarMessage(self) : return self.itemUniqueName
  def addStatusBarMessageByMFn(self, inFn) : 
    s = u''
    if inFn.isDefaultNode : s = s + u' defaultNode'
    if inFn.isFromReferencedFile : s = s + u' reference'
    if inFn.isLocked : s = s + u' locked'
    if inFn.isShared : s = s + u' shared'
    s = s + u' type=' + str((hex(inFn.typeId.id()), inFn.typeName))
    return s

  def expanded(self, depth=0) : 
    self.updateConnection()
    if depth > 0 : 
      chCnt = self.childCount()
      for chIdx in range(chCnt) : 
        chItm = self.child(chIdx)
        # print((chItm, chItm.itemType, chItm.isExpanded()))
        if chItm.itemType == itemBase.enMDagPath : 
          if chItm.isExpanded() == False : chItm.setExpanded(True)
          chItm.expanded(depth=depth - 1)
    
  def setCurrent(self) : 
    self.updateConnection()
  def doubleClicked(self, inColumn) : pass

  def updateConnection(self) : 
    if self.isEntityType == False : return
    mobj = getMObjectByName(self.itemUniqueName)
    if mobj is None : 
      fldItm = self.sourceFolder
      if fldItm is not None : self.removeChild(fldItm)
      fldItm = self.destinationFolder
      if fldItm is not None : self.removeChild(fldItm)
      return
    fn = OpenMaya.MFnDependencyNode(mobj)
    plgLst = fn.getConnections()

    fldItm = self.sourceFolder
    if fldItm is not None : fldItm.takeChildren()
    fldItm = self.destinationFolder
    if fldItm is not None : fldItm.takeChildren()

    srcExist = False
    dstExist = False
    if plgLst is not None : 
      for plg in plgLst : 
        srcPlg = plg.source()
        if srcPlg is not None and srcPlg.isNull == False : 
          srcExist = True
          self.addSource(plg, srcPlg)
        dstPlgLst = plg.destinations()
        if dstPlgLst is not None : 
          for dstPlg in dstPlgLst : 
            dstExist = True
            self.addDestination(plg, dstPlg)
    if srcExist == False : 
      fldItm = self.sourceFolder
      if fldItm is not None : self.removeChild(fldItm)
    if dstExist == False : 
      fldItm = self.destinationFolder
      if fldItm is not None : self.removeChild(fldItm)

  @property
  def sourceFolder(self) : return self.findChildByType(itemBase.enSourceFolder)
  def createSourceFolder(self) : 
    fldItm = self.sourceFolder
    if fldItm is not None : return fldItm
    fldItm = itemSourceFolder()
    self.insertChild(0, fldItm)
    return fldItm
  def addSource(self, inPlg, inTgtPlg) : 
    fldItm = self.createSourceFolder()
    itm = itemConnection(inPlg, inTgtPlg, targetIsSource=True, depth=0)
    fldItm.addChild(itm)
    return itm
  
  @property
  def destinationFolder(self) : return self.findChildByType(itemBase.enDestinationFolder)
  def createDestinationFolder(self) : 
    fldItm = self.destinationFolder
    if fldItm is not None : return fldItm
    fldItm = itemDestinationFolder()
    idx = 0
    if self.sourceFolder is not None : idx = idx + 1
    self.insertChild(idx, fldItm)
    return fldItm
  def addDestination(self, inPlg, inTgtPlg) : 
    fldItm = self.createDestinationFolder()
    itm = itemConnection(inPlg, inTgtPlg, targetIsSource=False, depth=0)
    fldItm.addChild(itm)
    return itm

  def findEntityItem(self, inObj) : 
    try : 
      fn = OpenMaya.MFnDagNode(inObj)
      return self.findMDagPath(fn.getPath())
    except : 
      return self.findMObject(inObj)

  def findMDagPathByName(self, inName) : 
    dgp = getMDagPathByName(inName)
    if dgp is None : return None
    return self.findMDagPath(dgp)
  
  def findMDagPath(self, inDgp) : 
    fp = inDgp.fullPathName()
    snLst = fp.split(u'|')
    sn = snLst.pop(0)
    if sn == u'' : sn = snLst.pop(0)
    snItm = None
    cnt = self.treeWidget().topLevelItemCount()
    for idx in range(cnt) : 
      itm = self.treeWidget().topLevelItem(idx)
      if itm.itemType != itemBase.enMDagPath : continue
      if itm.itemName == sn : 
        snItm = itm
        break
    if snItm is None : 
      logMessage(self.treeWidget(), u'not found:' + str(sn))
      return None

    for sn in snLst : 
      curItm = snItm
      snItm = None

      shpFldItm = curItm.shapeFolder
      if shpFldItm is not None : 
        chCnt = shpFldItm.childCount()
        for chIdx in range(chCnt) : 
          chItm = shpFldItm.child(chIdx)
          if chItm.itemType != itemBase.enMDagPath : continue
          if chItm.itemName == sn : 
            snItm = chItm
            break
        if snItm is not None : continue

      chCnt = curItm.childCount()
      for chIdx in range(chCnt) : 
        chItm = curItm.child(chIdx)
        if chItm.itemType != itemBase.enMDagPath : continue
        if chItm.itemName == sn : 
          snItm = chItm
          break
      if snItm is None : 
        logMessage(self.treeWidget(), u'not found:' + str(sn))
        return None
    
    return snItm

  def findMObjectByName(self, inName) :
    mobj = getMObjectByName(inName)
    if mobj is None : return None
    return self.findMObject(mobj)

  def findMObject(self, inMObj) :
    fldItm = None
    cnt = self.treeWidget().topLevelItemCount()
    for idx in range(cnt) : 
      itm = self.treeWidget().topLevelItem(idx)
      if itm.itemType != itemBase.enMObjectFolder : continue
      if itm.isThisFolder(inMObj) : 
        fldItm = itm
        break
      if itm.isSubFolder(inMObj) : 
        fldItm = itm
        break
    if fldItm is None : return None

    que = [ fldItm ]
    fn = OpenMaya.MFnDependencyNode(inMObj)
    nm = fn.absoluteName()
    while len(que) > 0 : 
      curItm = que.pop(0)
      chCnt = curItm.childCount()
      for chIdx in range(chCnt) : 
        chItm = curItm.child(chIdx)
        if chItm.itemType == itemBase.enMObjectFolder : 
          if chItm.isThisFolder(inMObj) : 
            que.append(chItm)
          elif chItm.isSubFolder(inMObj) : 
            que.append(chItm)
            break
        elif chItm.itemType == itemBase.enMObject : 
          if chItm.itemName == nm : 
            return chItm
    
    return None

  def findMObjectFolder(self, inMObj, mfnType=None, typeId=None) : 
    fldItm = None
    cnt = self.treeWidget().topLevelItemCount()
    for idx in range(cnt) : 
      itm = self.treeWidget().topLevelItem(idx)
      if itm.itemType != itemBase.enMObjectFolder : continue
      if itm.isThisFolder(inMObj, mfnType=mfnType, typeId=typeId) : 
        fldItm = itm
        break
      if itm.isSubFolder(inMObj, mfnType=mfnType) : 
        fldItm = itm
        break
    if fldItm is None : return None

    que = [ fldItm ]
    while len(que) > 0 : 
      fldItm = que.pop(0)
      chCnt = fldItm.childCount()
      for chIdx in range(chCnt) : 
        chItm = fldItm.child(chIdx)
        if chItm.itemType == itemBase.enMObjectFolder : 
          if chItm.isThisFolder(inMObj, mfnType=mfnType, typeId=typeId) : 
            que.append(chItm)
          elif chItm.isSubFolder(inMObj, mfnType=mfnType) : 
            que.append(chItm)
            break
        elif chItm.itemType == itemBase.enMObject : 
          break
    
    return fldItm

  def getCoreObject(self) : 
    treeWgt = self.treeWidget()
    if treeWgt is None : return None
    prt = treeWgt.parent()
    while prt is not None : 
      if prt.objectName().startswith(u'tkthOutliner') : 
        return prt
      prt = prt.parent()
    return None

  def itemPath(self, column=0) : 
    prtItm = self.parent()
    if prtItm is None : return [ self.text(column) ]
    prtPth = prtItm.itemPath(column=column)
    prtPth.append(self.text(column))
    return prtPth

  def nextItem(self, skipIndex=None) : 
    if skipIndex is not None : idx = skipIndex
    else : idx = 0
    chCnt = self.childCount()
    if idx < chCnt : return self.child(idx)
    
    prtItm = self.parent()
    if prtItm is None : 
      treeWgt = self.treeWidget()
      idx = treeWgt.indexOfTopLevelItem(self) + 1
      cnt = treeWgt.topLevelItemCount()
      if idx < cnt : return treeWgt.topLevelItem(idx)
      else : return None
    else : 
      idx = prtItm.indexOfChild(self) + 1
      return prtItm.nextItem(skipIndex=idx)

  def findItemByText(self, inStr, isEntityType=False) : 
    nextItm = self
    while nextItm is not None : 
      if isEntityType == False or isEntityType == nextItm.isEntityType : 
        try : 
          strIdx = nextItm.text(0).index(inStr)
          return nextItm
        except : pass
      nextItm = nextItm.nextItem()
    
    return None


class itemMObjectFolder(itemBase) : 
  __mfnTypeList = None
  @property
  def mfnTypeList(self) : return self.__mfnTypeList
  __typeId = None
  @property
  def typeId(self) : return self.__typeId
  
  def __init__(self, itemName, mfnTypeList=None, mfnType=None, typeId=None):
    super(__class__, self).__init__(itemFlags=QtCore.Qt.ItemFlag.ItemIsEnabled, itemType=itemBase.enMObjectFolder, mfnType=mfnType, itemName=itemName)
    self.__mfnTypeList = mfnTypeList
    self.__typeId = typeId
    fnt = self.font(0)
    fnt.setBold(True)
    self.setFont(0, fnt)
    if self.mfnTypeList is not None : 
      self.setForeground(0, QtGui.QBrush(qtDrawingOverridesColor(None, colorIndex=qtDrawingOverridesColor.enMayaDODarkBlueGreen)))
    elif self.mfnType is not None : 
      self.setForeground(0, QtGui.QBrush(qtDrawingOverridesColor(None, colorIndex=qtDrawingOverridesColor.enMayaDOBlueGreen)))
    else : 
      self.setForeground(0, QtGui.QBrush(qtDrawingOverridesColor(None, colorIndex=qtDrawingOverridesColor.enMayaDOGreen)))
  
  def isThisFolder(self, inMObj, mfnType=None, typeId=None) : 
    if self.mfnType is not None : 
      '''
      if self.mfnType == OpenMaya.MFn.kDependencyNode : 
        if inMObj.apiType() == OpenMaya.MFn.kDependencyNode : 
          return True
        else : 
          return False
      '''
      if inMObj is not None : 
        if inMObj.apiType() == self.mfnType : return True
        else : return False
      elif mfnType is not None : 
        if mfnType == self.mfnType : return True
    if self.typeId is not None : 
      if inMObj is not None : 
        fn = OpenMaya.MFnDependencyNode(inMObj)
        if fn.typeId == self.typeId : return True
        else : return False
      elif typeId is not None : 
        if typeId == self.mfnType : return True
    return False
  
  def isSubFolder(self, inMObj, mfnType=None) : 
    if self.mfnType is not None : 
      if self.mfnType == OpenMaya.MFn.kDependencyNode : 
        if inMObj.apiType() == OpenMaya.MFn.kDependencyNode : 
          return True
        else : 
          return False
    if self.__mfnTypeList is not None : 
      if inMObj is not None : 
        for mfnType in self.__mfnTypeList : 
          if inMObj.hasFn(mfnType) : 
            return True
      elif mfnType is not None : 
        if mfnType in self.__mfnTypeList : 
          return True
    return False

  def getFirstMObject(self) : 
    chCnt = self.childCount()
    for chIdx in range(chCnt) : 
      chWgt = self.child(chIdx)
      if chWgt.isEntityType : 
        mobj = chWgt.getObject()
        if mobj is not None : return mobj
      elif chWgt.itemType == itemBase.enMObjectFolder : 
        mobj = chWgt.getFirstMObject()
        if mobj is not None : return mobj
    return None

  def getStatusBarMessage(self):
    if self.mfnType is not None : return u'fnType=' + str(self.mfnType)
    if self.typeId is not None : return u'typeId=' + str(self.typeId)
    if self.mfnTypeList is not None : 
      s = u' '
      for ft in self.mfnTypeList : 
        s = s + str(ft) + u','
      s = u'fnType=[' + s[:-1] + u']'
      return s
    return super().getStatusBarMessage()


class itemMDagPath(itemBase) : 
  @property
  def shapeFolder(self) : return self.findChildByType(itemBase.enShapeFolder)
  def createShapeFolder(self) : 
    shpFldItm = self.shapeFolder
    if shpFldItm is not None : return shpFldItm
    shpFldItm = itemShapeFolder()
    idx = 0
    if self.sourceFolder is not None : idx = idx + 1
    if self.destinationFolder is not None : idx = idx + 1
    self.insertChild(idx, shpFldItm)
    return shpFldItm
  def addShape(self, itm) : 
    shpFldItm = self.createShapeFolder()
    shpFldItm.addChild(itm)
    return shpFldItm

  def constraintTargetLabel(self, inFn:OpenMaya.MFnDagNode) : 
    if inFn.getPath().hasFn(OpenMaya.MFn.kConstraint) == False : return u''
    s = u''
    try :
      tgtLst = list()
      tgtArrPlg = inFn.findPlug(u'target', True)
      elmCnt = tgtArrPlg.evaluateNumElements()
      for elmIdx in range(elmCnt) : 
        tgtPlg = tgtArrPlg.elementByPhysicalIndex(elmIdx)
        chCnt = tgtPlg.numChildren()
        for chIdx in range(chCnt) : 
          chPlg = tgtPlg.child(chIdx)
          lst = chPlg.name().split(u'.')
          nm = lst[-1]
          if nm == u'targetParentMatrix' : 
            srcPlg = chPlg.source()
            if srcPlg is not None and srcPlg.isNull == False : 
              try : 
                srcFn = OpenMaya.MFnDagNode(srcPlg.node())
                lst = srcFn.fullPathName().split(u'|')
                tgtLst.append(lst[-1])
              except : 
                pass
      if len(tgtLst) == 1 : s = s + u' target=' + tgtLst[0]
      elif len(tgtLst) > 1 : 
        tgtStr = u''
        for tgt in tgtLst : tgtStr = tgtStr + u',' + tgt
        s = s + u' target=' + tgtStr[1:]
      if inFn.getPath().hasFn(OpenMaya.MFn.kAimConstraint) : 
        wupPlg = inFn.findPlug(u'worldUpMatrix', True)
        srcPlg = wupPlg.source()
        if srcPlg is not None and srcPlg.isNull == False : 
          try : 
            srcFn = OpenMaya.MFnDagNode(srcPlg.node())
            lst = srcFn.fullPathName().split(u'|')
            s = s + u' up=' + lst[-1]
          except : 
            pass
    except : pass
    return s

  def __init__(self, dagPath, fnRefList=None):
    fn = OpenMaya.MFnDagNode(dagPath)
    fullPath = fn.fullPathName()
    lst = fullPath.split(u'|')
    itmNm = lst[-1] + self.constraintTargetLabel(fn)
    super(__class__, self).__init__(itemFlags=QtCore.Qt.ItemFlag.ItemIsEnabled|QtCore.Qt.ItemFlag.ItemIsSelectable, itemType=itemBase.enMDagPath, isDagNode=True, itemName=itmNm, itemUniqueName=fullPath, mfnType=dagPath.node().apiType())
    self.setUniqueUUID(fn=fn, fnRefList=fnRefList)
    plgLst = fn.getConnections()
    if plgLst is not None and len(plgLst) > 0 : 
      self.createSourceFolder()
      self.createDestinationFolder()
    self.updateColor()

  def updateColor(self) : 
    fn = self.getMFn()
    if fn is not None : 
      try : 
        col = qtDrawingOverridesColor(fn)
        self.setForeground(0, QtGui.QBrush(col))
      except : 
        pass
    shpFldItm = self.shapeFolder
    if shpFldItm is not None : 
      chCnt = shpFldItm.childCount()
      for chIdx in range(chCnt) : 
        itm = shpFldItm.child(chIdx)
        if itm.itemType == itemBase.enMDagPath : itm.updateColor()

  def getStatusBarMessage(self):
    dgp = self.getObject()
    if dgp is None : return super().getStatusBarMessage()
    s = u'MDagPath type=' + str(dgp.apiType())
    if dgp.length() > 1 : 
      dgp.pop()
      fp = dgp.fullPathName()
      lst = fp.split(u'|')
      s = s + u' parent=' + lst[-1]
    s = s + self.addStatusBarMessageByMFn(self.getMFn())
    return s

  def getWorldMatrix(self) :
    dgp = self.getObject()
    if dgp is None : return None
    fn = OpenMaya.MFnDagNode(dgp)
    wmPlg = fn.findPlug(u'worldMatrix', True)
    wmElmPlg = wmPlg.elementByLogicalIndex(0)
    v = wmElmPlg.asMObject()
    mtxFn = OpenMaya.MFnMatrixData(v)
    return mtxFn.matrix()

  def getParentInverseMatrix(self) :
    dgp = self.getObject()
    if dgp is None : return None
    fn = OpenMaya.MFnDagNode(dgp)
    wmPlg = fn.findPlug(u'parentInverseMatrix', True)
    wmElmPlg = wmPlg.elementByLogicalIndex(0)
    v = wmElmPlg.asMObject()
    mtxFn = OpenMaya.MFnMatrixData(v)
    return mtxFn.matrix()



class itemShapeFolder(itemBase) : 
  def __init__(self):
    super(__class__, self).__init__(itemFlags=QtCore.Qt.ItemFlag.ItemIsEnabled, itemType=itemBase.enShapeFolder, itemName=u'<shape>')

class itemSourceFolder(itemBase) : 
  def __init__(self):
    super(__class__, self).__init__(itemFlags=QtCore.Qt.ItemFlag.ItemIsEnabled, itemType=itemBase.enSourceFolder, itemName=u'<source>')

class itemDestinationFolder(itemBase) : 
  def __init__(self):
    super(__class__, self).__init__(itemFlags=QtCore.Qt.ItemFlag.ItemIsEnabled, itemType=itemBase.enDestinationFolder, itemName=u'<destination>')


class itemMObject(itemBase) : 
  def __init__(self, mobject, fnRefList=None):
    fn = OpenMaya.MFnDependencyNode(mobject)
    nm = fn.absoluteName()
    super(__class__, self).__init__(itemFlags=QtCore.Qt.ItemFlag.ItemIsEnabled|QtCore.Qt.ItemFlag.ItemIsSelectable, itemType=itemBase.enMObject, itemUniqueName=nm, itemName=nm, mfnType=mobject.apiType())
    self.setUniqueUUID(fn=fn, fnRefList=fnRefList)
    plgLst = fn.getConnections()
    if plgLst is not None and len(plgLst) > 0 : 
      self.createSourceFolder()
      self.createDestinationFolder()


  def getStatusBarMessage(self):
    mobj = self.getObject()
    if mobj is None : return super().getStatusBarMessage()
    s = u'MObject type=' + str(mobj.apiType()) + self.addStatusBarMessageByMFn(self.getMFn())
    return s

class itemConnection(itemBase) : 
  __plugName = None
  __plugPath = None
  @property
  def plugPath(self) : return self.__plugPath
  
  __targetPlugName = None
  __targetPlugPath = None
  @property
  def targetPlugPath(self) : return self.__targetPlugPath
  
  __targetIsSource = False
  @property
  def targetIsSource(self) : return self.__targetIsSource

  def __init__(self, plug, targetPlug, targetIsSource=False, depth=100):
    self.__plugPath = plug.name()
    self.__targetPlugPath = targetPlug.name()
    self.__targetIsSource = targetIsSource

    self.__plugName = plug.partialName(includeNodeName=False, includeNonMandatoryIndices=True, includeInstancedIndices=False, useAlias=False, useFullAttributePath=False, useLongNames=True)
    tgtObj = targetPlug.node()
    self.__targetPlugName = targetPlug.partialName(includeNodeName=False, includeNonMandatoryIndices=True, includeInstancedIndices=False, useAlias=False, useFullAttributePath=False, useLongNames=True)
    if tgtObj.hasFn(OpenMaya.MFn.kDagNode) : 
      fn = OpenMaya.MFnDagNode(tgtObj)
      unqNm = fn.fullPathName()
      lst = unqNm.split(u'|')
      nm = lst[-1]
      dgNd = True
    else : 
      fn = OpenMaya.MFnDependencyNode(tgtObj)
      unqNm = fn.absoluteName()
      nm = unqNm
      dgNd = False
    nm = nm + u'.' + self.__targetPlugName + u' <' + self.__plugName + u'>'
    super(__class__, self).__init__(itemFlags=QtCore.Qt.ItemFlag.ItemIsEnabled|QtCore.Qt.ItemFlag.ItemIsSelectable, itemType=itemBase.enConnection, isDagNode=dgNd, itemUniqueName=unqNm, itemName=nm, mfnType=tgtObj.apiType())
    if depth < 5 : self.addSubTargetPlug(targetPlug, depth=depth + 1)
  
  def addSubTargetPlug(self, targetPlug, depth=100) : 
    chkPlgLst = list()
    targetNode = targetPlug.node()
    fn = OpenMaya.MFnDependencyNode(targetNode)
    if self.targetIsSource : 
      if targetNode.hasFn(OpenMaya.MFn.kDecomposeMatrix) : 
        chkPlgLst.append(fn.findPlug(u'inputMatrix', True))
      elif targetNode.hasFn(OpenMaya.MFn.kMatrixMult) : 
        chkPlgLst.append(fn.findPlug(u'matrixIn', True))
      elif fn.typeId.id() == 0x58000302 : # inverseMatrix
        chkPlgLst.append(fn.findPlug(u'inputMatrix', True))
      elif targetNode.hasFn(OpenMaya.MFn.kMatrixWtAdd) : 
        chkPlgLst.append(fn.findPlug(u'wtMatrix', True))
      for chkPlg in chkPlgLst : 
        chkSrcPlg = chkPlg.source()
        if chkSrcPlg is not None and chkSrcPlg.isNull == False : 
          chkSrcItm = itemConnection(targetPlug, chkSrcPlg, targetIsSource=self.targetIsSource, depth=depth+1)
          self.addChild(chkSrcItm)
        if chkPlg.isArray : 
          logIdxLst = chkPlg.getExistingArrayAttributeIndices()
          for logIdx in logIdxLst : 
            elmPlg = chkPlg.elementByLogicalIndex(logIdx)
            chkSrcPlg = elmPlg.source()
            if chkSrcPlg is not None and chkSrcPlg.isNull == False : 
              chkSrcItm = itemConnection(targetPlug, chkSrcPlg, targetIsSource=self.targetIsSource, depth=depth+1)
              self.addChild(chkSrcItm)
            if elmPlg.isCompound : 
              chCnt = elmPlg.numChildren()
              for chIdx in range(chCnt) : 
                elmChPlg = elmPlg.child(chIdx)
                chkSrcPlg = elmChPlg.source()
                if chkSrcPlg is not None and chkSrcPlg.isNull == False : 
                  chkSrcItm = itemConnection(targetPlug, chkSrcPlg, targetIsSource=self.targetIsSource, depth=depth+1)
                  self.addChild(chkSrcItm)

    else : 
      if targetNode.hasFn(OpenMaya.MFn.kComposeMatrix) : 
        chkPlgLst.append(fn.findPlug(u'outputMatrix', True))
      elif targetNode.hasFn(OpenMaya.MFn.kDecomposeMatrix) : 
        chkPlgLst.append(fn.findPlug(u'outputTranslate', True))
        chkPlgLst.append(fn.findPlug(u'outputRotate', True))
        chkPlgLst.append(fn.findPlug(u'outputScale', True))
        chkPlgLst.append(fn.findPlug(u'outputShear', True))
        chkPlgLst.append(fn.findPlug(u'outputQuat', True))
      elif targetNode.hasFn(OpenMaya.MFn.kMatrixMult) : 
        chkPlgLst.append(fn.findPlug(u'matrixSum', True))
      elif fn.typeId.id() == 0x58000302 : # inverseMatrix
        chkPlgLst.append(fn.findPlug(u'outputMatrix', True))
      elif targetNode.hasFn(OpenMaya.MFn.kMatrixWtAdd) : 
        chkPlgLst.append(fn.findPlug(u'matrixSum', True))
      for chkPlg in chkPlgLst : 
        chkDstPlgLst = chkPlg.destinations()
        if chkDstPlgLst is not None : 
          for chkDstPlg in chkDstPlgLst : 
            chkDstItm = itemConnection(targetPlug, chkDstPlg, targetIsSource=self.targetIsSource, depth=depth+1)
            self.addChild(chkDstItm)
        if chkPlg.isArray : 
          logIdxLst = chkPlg.getExistingArrayAttributeIndices()
          for logIdx in logIdxLst : 
            elmPlg = chkPlg.elementByLogicalIndex(logIdx)
            elmDstPlgLst = elmPlg.destinations()
            if elmDstPlgLst is not None : 
              for elmDstPlg in elmDstPlgLst : 
                elmDstItm = itemConnection(targetPlug, elmDstPlg, targetIsSource=self.targetIsSource, depth=depth+1)
                self.addChild(elmDstItm)
            if elmPlg.isCompound : 
              chCnt = elmPlg.numChildren()
              for chIdx in range(chCnt) : 
                elmChPlg = elmPlg.child(chIdx)
                elmChDstPlgLst = elmChPlg.destinations()
                if elmChDstPlgLst is not None : 
                  for elmChDstPlg in elmChDstPlgLst : 
                    elmChDstItm = itemConnection(targetPlug, elmChDstPlg, targetIsSource=self.targetIsSource, depth=depth+1)
                    self.addChild(elmChDstItm)

  
  def doubleClicked(self, inColumn) : 
    itm = None
    if self.isDagNode : 
      itm = self.findMDagPathByName(self.itemUniqueName)
      #print(self.itemUniqueName + u':dag:' + str(itm))
    else : 
      itm = self.findMObjectByName(self.itemUniqueName)
      #print(self.itemUniqueName + u':dep:' + str(itm))
    if itm is not None : 
      self.treeWidget().setCurrentAndScrollToItem(itm)
      self.treeWidget().addNext(self)
      self.treeWidget().addNext(itm)
    else : 
      logMessage(self.treeWidget(), u'not found:' + str((self.itemUniqueName, self.isDagNode)))

  def getStatusBarMessage(self):
    plg = getMPlugByName(self.plugPath)
    if plg is None : 
      txt = u'null'
    else : 
      txt = getValueTypeString(getPlugValueType(plg))
    txt = txt + u' : '
    plg = getMPlugByName(self.targetPlugPath)
    if plg is None : 
      txt = txt + u'null'
    else : 
      txt = txt + getValueTypeString(getPlugValueType(plg))
    return txt

