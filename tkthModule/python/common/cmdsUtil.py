# -*- coding: utf-8 -*-
'''
雑多な関数

author : Takeharu TANIMURA <tanie@kk.iij4u.or.jp>
'''

import re

import maya.cmds as cmds
import maya.mel as mel


def getFullName(inNm) :
  '''
  getFullName(uniqName) : fullPath
  '''
  if cmds.objExists(inNm) :
    evalStr = u'longNameOf(\"' + inNm + u'\")'
    return mel.eval(evalStr)
  else :
    return None

def getUniqueShortName(inNm) :
  '''
  getUniqueShortName(fullPath) : unique Name
  '''
  if cmds.objExists(inNm) :
    evalStr = u'shortNameOf(\"' + inNm + u'\")'
    return mel.eval(evalStr)
  else :
    return None


def getShortNameWithNamespace(inNm) :
  '''
  getShortNameWithNamespace(objName) : shortest name(not unique) with namespace
  '''
  lst = inNm.split(u'|')
  return lst[-1]


def getShortName(inNm) :
  '''
  getShortName(objName) : shortest name(not unique)
  '''
  nsNm = getShortNameWithNamespace(inNm)
  lst = nsNm.split(u':')
  return lst[-1]


def findChild(inRoot, inName) :
  '''
  findChild(parentNode, name) : fullpath node name or None
  '''
  que = [ inRoot ]
  queCnt = 1
  while queCnt > 0 :
    nd = que.pop(0)
    queCnt = queCnt - 1
    sn = getShortName(nd)
    if sn == inName : 
      return nd

    chLst = cmds.listRelatives(nd, children=True, fullPath=True)
    if chLst is None : continue
    for ch in chLst :
      if cmds.objectType(ch, isAType=u'transform') == False :
        continue
      que.append(ch)
      queCnt = queCnt + 1
  return None

def getTransformTree(inRoot) :
  '''
  getTransformTree(root) : all children list
  '''
  trfLst = [ getFullName(inRoot) ]
  que = [ inRoot ]
  queCnt = 1
  while queCnt > 0 :
    trf = que.pop(0)
    queCnt = queCnt - 1
    chLst = cmds.listRelatives(trf, children=True, fullPath=True)
    if chLst is None : continue
    for ch in chLst :
      if cmds.objectType(ch, isAType=u'transform') :
        que.append(ch)
        queCnt = queCnt + 1
        trfLst.append(ch)
  return trfLst

def getTransformDict(inRoot) :
  '''
  getTransformDict(root) : all children dict()
  '''
  ndLst = getTransformTree(inRoot)
  dct = dict()
  for nd in ndLst :
    sn = getShortName(nd)
    if sn in dct :
      cmds.warning(u'SKIP:' + sn + u':' + nd + u':' + dct[sn])
    else :
      dct[sn] = nd
  return dct

def plugName(inNd, inAttrLst) :
  '''
  plugName(nodeName, attrNameLst) : str. plug name
  '''
  if type(inAttrLst) == str : return inNd + u'.' + inAttrLst
  if type(inAttrLst) == tuple : return inNd + u'.' + inAttrLst[0] + u'[' + str(inAttrLst[1]) + u']'
  plgNm = inNd
  for attr in inAttrLst :
    if type(attr) == tuple or type(attr) == list :
      plgNm = plgNm + u'.' + attr[0] + u'[' + str(attr[1]) + u']'
    else :
      plgNm = plgNm + u'.' + attr
  return plgNm


def getShortPlugName(inPlg) : 
  '''
  getShortPlugName(plugName) : short plugName with namespace
  '''
  try : 
    idx = inPlg.index(u'.')
    nd = inPlg[:idx]
    plg = inPlg[idx:]
  except : 
    return inPlg
  return getShortNameWithNamespace(nd) + plg


def getNodePlug(inPlg) :
  '''
  getPlugNode(plugName) : ( nodeName, plugNameList )
  '''
  lst = inPlg.split(u'.')
  if len(lst) < 2 : return None
  nd = lst.pop(0)
  plgLst = list()
  for plgNm in lst :
    mtchObj = re.match(u'^(.+)\\[(\\d+)\\]$', plgNm)
    if mtchObj is not None :
      plg = mtchObj.group(1)
      idx = int(mtchObj.group(2))
      plgLst.append([plg, idx])
    else :
      plgLst.append(plgNm)
  return ( nd, plgLst )


def getRoot(inNd) :
  '''
  getRoot(nodeName) : str. transform root name
  '''
  nd = getFullName(inNd)
  lst = nd.split(u'|')
  return u'|' + lst[1]

def addConstraint(inNode, offsetParentMatrix=None, pointConstraint=None, orientConstraint=None, parentConstraint=None, aimUpConstraint=None, aimVector=[1.0, 0.0, 0.0], upVector=[0.0, 1.0, 0.0]) :
  '''
  addConstraint(nodeName, offsetParentMatrix=None, pointConstraint=None, orientConstraint=None, parentConstraint=None, aimUpConstraint=None, aimVector=[1.0, 0.0, 0.0], upVector=[0.0, 1.0, 0.0]) : [constraintNodeName]
  '''
  chLst = cmds.listRelatives(inNode, children=True, fullPath=True)
  if chLst is None : chLst = []
  cns = [ ]
  if offsetParentMatrix is not None :
    dstPlg = plugName(inNode, u'offsetParentMatrix')
    disconnectSource(dstPlg)
    cmds.connectAttr(offsetParentMatrix, dstPlg, force=True)
  if pointConstraint is not None :
    for idx, ch in enumerate(chLst) : 
      if cmds.objectType(ch, isAType=u'pointConstraint') : 
        cmds.delete(chLst.pop(idx))
        break
    cns.extend(cmds.pointConstraint(pointConstraint, inNode, name=getShortName(inNode) + u'_pointConstraint'))
  if orientConstraint is not None :
    for idx, ch in enumerate(chLst) : 
      if cmds.objectType(ch, isAType=u'orientConstraint') : 
        cmds.delete(chLst.pop(idx))
        break
    cns.extend(cmds.orientConstraint(orientConstraint, inNode, name=getShortName(inNode) + u'_orientConstraint'))
  if parentConstraint is not None :
    for idx, ch in enumerate(chLst) : 
      if cmds.objectType(ch, isAType=u'parentConstraint') : 
        cmds.delete(chLst.pop(idx))
        break
    cns.extend(cmds.parentConstraint(parentConstraint, inNode, name=getShortName(inNode) + u'_parentConstraint'))
  if aimUpConstraint is not None :
    for idx, ch in enumerate(chLst) : 
      if cmds.objectType(ch, isAType=u'aimConstraint') : 
        cmds.delete(chLst.pop(idx))
        break
    cns.extend(cmds.aimConstraint(aimUpConstraint[0], inNode, name=getShortName(inNode) + u'_aimConstraint', worldUpObject=aimUpConstraint[1], worldUpType=u'object', aimVector=aimVector, upVector=upVector))
  return cns

def copyTransform(inSrc, inDst, copyTranslate=True, copyRotate=True, copyScale=True, copyJointOrient=True, copyPreferredAngle=True) : 
  if copyTranslate :
    try : 
      xyz = cmds.getAttr(plugName(inSrc, u'translate'))
      cmds.setAttr(plugName(inDst, u'translate'), xyz[0][0], xyz[0][1], xyz[0][2], type=u'double3')
    except : pass
  if copyRotate :
    try : 
      xyz = cmds.getAttr(plugName(inSrc, u'rotate'))
      cmds.setAttr(plugName(inDst, u'rotate'), xyz[0][0], xyz[0][1], xyz[0][2], type=u'double3')
      rotOrd = cmds.getAttr(plugName(inSrc, u'rotateOrder'))
      cmds.setAttr(plugName(inDst, u'rotateOrder'), rotOrd)
    except : pass
  if copyScale :
    try : 
      xyz = cmds.getAttr(plugName(inSrc, u'scale'))
      cmds.setAttr(plugName(inDst, u'scale'), xyz[0][0], xyz[0][1], xyz[0][2], type=u'double3')
    except : pass
  if cmds.objectType(inSrc, isAType=u'joint') and cmds.objectType(inDst, isAType=u'joint') : 
    if copyJointOrient :
      try : 
        xyz = cmds.getAttr(plugName(inSrc, u'jointOrient'))
        cmds.setAttr(plugName(inDst, u'jointOrient'), xyz[0][0], xyz[0][1], xyz[0][2], type=u'double3')
      except : pass
    if copyPreferredAngle :
      try : 
        xyz = cmds.getAttr(plugName(inSrc, u'preferredAngle'))
        cmds.setAttr(plugName(inDst, u'preferredAngle'), xyz[0][0], xyz[0][1], xyz[0][2], type=u'double3')
      except : pass


def createTransform(inParent, inName, copySource=None, copyTranslate=True, copyRotate=True, copyScale=True, offsetParentMatrix=None, pointConstraint=None, orientConstraint=None, parentConstraint=None, aimUpConstraint=None) :
  '''
  createTransform(parentNodeName, name, copySource=None, copyTranslate=True, copyRotate=True, copyScale=True, offsetParentMatrix=None, pointConstraint=None, orientConstraint=None, parentConstraint=None, aimUpConstraint=None) : [nodeName, constraintList]
  '''
  nd = None
  if inParent is not None : 
    nd = cmds.group(empty=True, parent=inParent, relative=True, name=inName)
  else :
    nd = cmds.group(empty=True, relative=True, name=inName)
  nd = [ getFullName(nd) ]
  if copySource is not None :
    copyTransform(copySource, nd[0], copyTranslate=copyTranslate, copyRotate=copyRotate, copyScale=copyScale)
  nd.extend(addConstraint(nd[0], offsetParentMatrix=offsetParentMatrix, pointConstraint=pointConstraint, orientConstraint=orientConstraint, parentConstraint=parentConstraint, aimUpConstraint=aimUpConstraint))
  return nd

def createJoint(inParent, inName, copySource=None, copyTranslate=True, copyRotate=True, copyScale=True, copyJointOrient=True, copyPreferredAngle=True, offsetParentMatrix=None, pointConstraint=None, orientConstraint=None, parentConstraint=None, aimUpConstraint=None) :
  '''
  createJoint(parentNodeName, name, inHintJnt, offsetParentMatrix=None, pointConstraint=None, orientConstraint=None, parentConstraint=None, aimUpConstraint=None) : [nodeName, constraintList]
  '''
  if inParent is not None :
    cmds.select(inParent, replace=True)
  else :
    cmds.select(clear=True)
  jnt = [ getFullName(cmds.joint(name=inName)) ]
  if copySource is not None :
    copyTransform(copySource, jnt[0], copyTranslate=copyTranslate, copyRotate=copyRotate, copyScale=copyScale, copyJointOrient=copyJointOrient, copyPreferredAngle=copyPreferredAngle)
  jnt.extend(addConstraint(jnt[0], offsetParentMatrix=offsetParentMatrix, pointConstraint=pointConstraint, orientConstraint=orientConstraint, parentConstraint=parentConstraint, aimUpConstraint=aimUpConstraint))
  return jnt


def createLocator(inParent, inName, copySource=None, copyTranslate=True, copyRotate=True, copyScale=True, offsetParentMatrix=None, pointConstraint=None, orientConstraint=None, parentConstraint=None, aimUpConstraint=None) :
  '''
  createLocator(parentNodeName, name, offsetParentMatrix=None, pointConstraint=None, orientConstraint=None, parentConstraint=None, aimUpConstraint=None) : [nodeName, constraintList]
  '''
  nd = None
  if inParent is not None : 
    lst = cmds.spaceLocator(absolute=True, name=inName)
    lst = cmds.parent(lst[0], inParent, relative=True)
    nd = [ getFullName(cmds.rename(lst[0], inName)) ]
  else :
    lst = cmds.spaceLocator(absolute=True, name=inName)
    nd = [ getFullName(lst[0]) ]
  if copySource is not None :
    copyTransform(copySource, nd[0], copyTranslate=copyTranslate, copyRotate=copyRotate, copyScale=copyScale)
  nd.extend(addConstraint(nd[0], offsetParentMatrix=offsetParentMatrix, pointConstraint=pointConstraint, orientConstraint=orientConstraint, parentConstraint=parentConstraint, aimUpConstraint=aimUpConstraint))
  return nd


def getChildByType(inNode, inType) :
  chLst = cmds.listRelatives(inNode, children=True, fullPath=True)
  if chLst is None : return None
  for ch in chLst :
    if cmds.objectType(ch, isAType=inType) :
      return ch
  return None


def hasSource(inPlg) :
  src = cmds.listConnections(inPlg, source=True, destination=False)
  if src is not None and len(src) > 0 : return True
  else : return False


def unlockAttribute(inPlg) :
  lck = cmds.getAttr(inPlg, lock=True)
  if lck : cmds.setAttr(inPlg, lock=False)


def lockAttribute(inPlg) :
  lck = cmds.getAttr(inPlg, lock=True)
  if lck == False : cmds.setAttr(inPlg, lock=True)


def lockSRT(inNd, translate=None, rotate=None, rotateOrder=True, scale=True, shear=True, rotateAxis=True) :
  if translate is not None :
    if type(translate) == bool : xyzVal = [translate] * 3
    else : xyzVal = translate
    for xyz, val in zip([u'X', u'Y', u'Z'], xyzVal) :
      cmds.setAttr(plugName(inNd, u'translate' + xyz), lock=val)
  if rotate is not None :
    if type(rotate) == bool : xyzVal = [rotate] * 3
    else : xyzVal = rotate
    for xyz, val in zip([u'X', u'Y', u'Z'], xyzVal) :
      cmds.setAttr(plugName(inNd, u'rotate' + xyz), lock=val)
  if rotateOrder is not None :
    cmds.setAttr(plugName(inNd, u'rotateOrder'), lock=rotateOrder)
  if scale is not None :
    if type(scale) == bool : xyzVal = [scale] * 3
    else : xyzVal = scale
    for xyz, val in zip([u'X', u'Y', u'Z'], xyzVal) :
      cmds.setAttr(plugName(inNd, u'scale' + xyz), lock=val)
  if shear is not None :
    if type(shear) == bool : xyzVal = [shear] * 3
    else : xyzVal = shear
    for xyz, val in zip([u'XY', u'XZ', u'YZ'], xyzVal) :
      cmds.setAttr(plugName(inNd, u'shear' + xyz), lock=val)
  if rotateAxis is not None :
    if type(rotateAxis) == bool : xyzVal = [rotateAxis] * 3
    else : xyzVal = rotateAxis
    for xyz, val in zip([u'X', u'Y', u'Z'], xyzVal) :
      cmds.setAttr(plugName(inNd, u'rotateAxis' + xyz), lock=val)



def findSource(inPlug, inType, inStopType, plug=False) :
  cnt = 36
  que = []
  que.append(inPlug)
  queCnt = 1
  while queCnt > 0 : 
    if cnt == 0 : break
    cnt = cnt - 1
    plg = que.pop(0)
    queCnt = queCnt - 1
    lstSrc = cmds.listConnections(plg, source=True, destination=False, plugs=True, skipConversionNodes=True)
    if lstSrc is None or len(lstSrc) == 0 : continue
    for src in lstSrc : 
      ndPlg = src.split(u'.')
      if cmds.objectType(ndPlg[0], isAType=inType) : 
        if plug : 
          return src
        else :
          return ndPlg[0]
      if inStopType is None : 
        que.append(src)
        que.append(ndPlg[0])
        queCnt = queCnt + 2
      else :
        if cmds.objectType(ndPlg[0], isAType=inStopType) : 
          pass
        else :
          que.append(src)
          que.append(ndPlg[0])
          queCnt = queCnt + 2
  return None


def disconnectSource(inPlg) :
  src = cmds.listConnections(inPlg, source=True, destination=False, plugs=True)
  if src is None or len(src) == 0 : return None
  cmds.disconnectAttr(src[0], inPlg)
  return src[0]


def addedAssemblies(inOldAsmLst) :
  asmLst = cmds.ls(assemblies=True, long=True)
  if asmLst is None : return None
  addedAsmLst = list()
  for asm in asmLst :
    if asm not in inOldAsmLst :
      addedAsmLst.append(asm)
  return addedAsmLst


def loadPluginList(inLst) :
  for plg in inLst :
    try :
      if cmds.pluginInfo(plg, query=True, loaded=True) == False : cmds.loadPlugin(plg)
    except : pass


