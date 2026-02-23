# -*- coding: utf-8 -*-
'''
APIを使った関数群

author : Takeharu TANIMURA <tanie@kk.iij4u.or.jp>
'''

import re

import maya.api.OpenMaya as OpenMaya


import tkthmaya.common.cmdsUtil


def  getMObjectName(inObj) :
  if inObj.isNull() : return None

  try :
    fn = OpenMaya.MFnDagNode(inObj)
    return fn.fullPathName()
  except :
    pass

  try :
    fn = OpenMaya.MFnAttribute(inObj)
    return fn.name()
  except :
    pass

  try :
    fn = OpenMaya.MFnDependencyNode(inObj)
    return fn.name()
  except :
    pass

  return None


def  getMDagPathName(inDag) :
  try :
    fn = OpenMaya.MFnDagNode(inDag)
    return fn.fullPathName()
  except :
    return None


def  getMPlugName(inPlg) :
  if inPlg.isNull : return None
  else : return inPlg.partialName(includeNodeName=True, includeNonMandatoryIndices=False, includeInstancedIndices=True, useAlias=False, useFullAttributePath=True, useLongNames=True)


def  getMObjectByName(inNm) :
  try :
    sl = OpenMaya.MSelectionList()
    sl.add(inNm)
    itr = OpenMaya.MItSelectionList(sl)
    while itr.isDone() == False :
      try :
        if itr.itemType() == OpenMaya.MItSelectionList.kDNselectionItem :
          return itr.getDependNode()
        if itr.itemType() == OpenMaya.MItSelectionList.kDagSelectionItem :
          return itr.getDagPath().node()
      except :
        pass
      finally :
        itr.next()
  except :
    pass
  return None


def  getMDagPathByName(inNm) :
  try :
    sl = OpenMaya.MSelectionList()
    sl.add(inNm)
    itr = OpenMaya.MItSelectionList(sl)
    while itr.isDone() == False :
      try :
        if itr.itemType() == OpenMaya.MItSelectionList.kDagSelectionItem :
          return itr.getDagPath()
      except :
        pass
      finally :
        itr.next()
  except :
    pass
  return None


def  getMPlugByName(inNm) :
  try :
    sl = OpenMaya.MSelectionList()
    sl.add(inNm)
    itr = OpenMaya.MItSelectionList(sl)
    idx = 0
    while itr.isDone() == False :
      try :
        if itr.itemType() == OpenMaya.MItSelectionList.kPlugSelectionItem :
          # SDK:MItSelectionItemに配列アトリビュートの要素を正常に取得できない不具合がある
          plg = sl.getPlug(idx)
          if plg.isElement and re.search(u'\\[\\d+\\]$', inNm) is None : return plg.array()
          else : return plg
      except :
        pass
      finally :
        itr.next()
        idx += 1
  except :
    pass
  return None

def getMPlugAttributeName(inPlg, cutUnderlineNumber=False) :
  if inPlg.isNull : return None
  fn = OpenMaya.MFnAttribute(inPlg.attribute())
  nm = fn.name
  if cutUnderlineNumber : 
    mObj = re.search(u'(_\\d+)$', nm)
    if mObj is not None : 
      ( sIdx, eIdx ) = mObj.span()
      nm = nm[:sIdx]
  return nm


def getMObjectByType(inFnType) : 
  lst = list()
  itr = OpenMaya.MItDependencyNodes(inFnType)
  while itr.isDone() == False : 
    try : 
      lst.append(itr.thisNode())
    finally : 
      itr.next()
  return lst    


def getMFnReferenceList() : 
  refObjLst = getMObjectByType(OpenMaya.MFn.kReference)
  fnRefList = list()
  for refObj in refObjLst :
    fnRefList.append(OpenMaya.MFnReference(refObj))
  return fnRefList


def getUniqueUUID(inFn, fnRefList=None) : 
  uuidTpl = [ inFn.uuid() ]
  if inFn.isFromReferencedFile : 
    if fnRefList is None : 
      fnRefList = getMFnReferenceList()
    for fnRef in fnRefList : 
      try :
        if fnRef.containsNodeExactly(inFn.object()) : 
          uuidTpl.extend(getUniqueUUID(fnRef, fnRefList=fnRefList))
          break
      except :
        pass
        # print((fnRef.absoluteName(), inFn.absoluteName(), inFn.object()))
  return uuidTpl


class UniqueMayaUUID(object) : 
  __uuidList = None
  @property
  def uuidList(self) : return self.__uuidList
  
  def __init__(self, inFn, fnRefList=None) : self.__uuidList = getUniqueUUID(inFn, fnRefList=fnRefList)

  def __eq__(self, inOther) : 
    cnt = len(self.__uuidList)
    if len(inOther.__uuidList) != cnt : return False
    for idx in range(cnt) : 
      if self.__uuidList[idx] == inOther.__uuidList[idx] : 
        pass
      else : 
        return False
    return True

  def __str__(self) : 
    s = u''
    for uuid in self.__uuidList : 
      s = s + u'.' + uuid.asString()
    return s
  

def getMMatrixValue(inPlg) :
  mobj = inPlg.asMObject()
  fn = OpenMaya.MFnMatrixData(mobj)
  return OpenMaya.MMatrix(fn.matrix())
  

def getMMatrixRawValue(inApiMtx) :
  lst = [0.0]*16
  idx = 0
  for row in range(4) :
    for col in range(4) :
      lst[idx] = inApiMtx.getElement(row, col)
      idx = idx + 1
  return lst


def findMPlugSource(inPlg, inFnType, stopFnType=None) :
  que = list()
  plgLst = inPlg.connectedTo(True, False)
  if plgLst is None or len(plgLst) == 0 :
    return None
  que.append(plgLst[0])

  loopLmt = 1024
  while len(que) > 0 :
    if loopLmt <= 0 :
      break
    loopLmt = loopLmt - 1

    curPlg = que.pop(0)
    curObj = curPlg.node()
    if curObj.hasFn(inFnType) :
      return curPlg
    if stopFnType is not None and curObj.hasFn(stopFnType) :
      continue

    if curPlg.isDestination == False :
      plgLst = curPlg.connectedTo(True, False)
      if plgLst is not None and len(plgLst) == 1 :
        que.insert(0, plgLst[0])
    
    fn = OpenMaya.MFnDependencyNode(curObj)
    plgLst = fn.getConnections()
    for plg in plgLst :
      if plg.isDestination == False : continue
      srcPlgLst = plg.connectedTo(True, False)
      if srcPlgLst is not None : que.extend(srcPlgLst)

  return None


def getConstraintTargetList(inDGP) :
  fn = OpenMaya.MFnDagNode(inDGP)
  tgtPlg = fn.findPlug(u'target', True)
  logIdxLst = tgtPlg.getExistingArrayAttributeIndices()
  tgtDgpLst = list()
  for logIdx in logIdxLst :
    tgtElmPlg = tgtPlg.elementByLogicalIndex(logIdx)
    chCnt = tgtElmPlg.numChildren()
    for chIdx in range(chCnt) :
      try :
        chPlg = tgtElmPlg.child(chIdx)
        srcPlg = chPlg.source()
        if srcPlg is None or srcPlg.isNull : continue
        srcFn = OpenMaya.MFnDagNode(srcPlg.node())
        srcDgp = srcFn.getPath()
        if srcDgp is not None : 
          tgtDgpLst.append(srcDgp)
          break
      except :
        pass
  return tgtDgpLst


def getConstraintUpVector(inDGP) :
  if inDGP.hasFn(OpenMaya.MFn.kAimConstraint) == False : return None
  fn = OpenMaya.MFnDagNode(inDGP)
  wumPlg = fn.findPlug(u'worldUpMatrix', True)
  srcPlg = wumPlg.source()
  if srcPlg is None or srcPlg.isNull : return None
  srcFn = OpenMaya.MFnDagNode(srcPlg.node())
  return srcFn.getPath()

# array     : 0x20000
# compound  : 0x10000
#
# numCh-1   : 0x0x000
#
# float     : 0x00200
# int       : 0x00100
# object    : 0x00800
# string    : 0x00400
enATInvalid        = 0x00000
enATBool           = 0x00101
enATLong           = 0x00102
enATShort          = 0x00103
enATByte           = 0x00104
enATChar           = 0x00105
enATEnum           = 0x00106
enATFloat          = 0x00207
enATDouble         = 0x00208
enATDoubleAngle    = 0x00209
enATDoubleLinear   = 0x0020a
enATString         = 0x0040b
enATStringArray    = 0x2040c
enATCompound       = 0x1000d
enATMessage        = 0x0000e
enATTime           = 0x0020f
enATMatrix         = 0x00210
enATFltMatrix      = 0x00211
enATReflectanceRGB = 0x12212
enATReflectance    = 0x00213
enATSpectrumRGB    = 0x12214
enATSpectrum       = 0x00215
enATFloat2         = 0x11216
enATFloat3         = 0x12217
enATDouble2        = 0x11218
enATDouble3        = 0x12219
enATLong2          = 0x1111a
enATLong3          = 0x1211b
enATShort2         = 0x1111c
enATShort3         = 0x1211d
enATDoubleArray    = 0x2011e
enATFloatArray     = 0x2011f
enATInt32Array     = 0x20120
enATVectorArray    = 0x22121
enATNurbsCurve     = 0x00822
enATNurbsSurface   = 0x00823
enATMesh           = 0x00824
enATLattice        = 0x00825
enATPointArray     = 0x22226
enATMatrixArray    = 0x20227
enATDouble4        = 0x13228
enATAddr           = 0x00129
enATBifrostPortIn  = 0x000fe
enATBifrostPortOut = 0x000ff
enATBifrostRiggingModuleInputs  = 0x10801
enATBifrostRiggingModuleOutputs = 0x10802


def isConnectable(inSrc, inDst) :
  if isBifrostPortType(inSrc) and getBiflostType(inDst) is not None : return True
  if isBifrostPortType(inDst) and getBiflostType(inSrc) is not None : return True

  if inSrc == inDst : return True
  if isArrayType(inSrc) or isArrayType(inDst) : return False
  if isNumericValueType(inSrc) and isNumericValueType(inDst) :
    if inSrc == enATMatrix or inSrc == enATFltMatrix :
      if inDst == enATMatrix or inDst == enATFltMatrix : return True
      else : return False
    elif inDst == enATMatrix or inDst == enATFltMatrix : return False

    if hasChildValueType(inSrc) or hasChildValueType(inDst) :
      if inSrc == enATFloat2 or inSrc == enATDouble2 or inSrc == enATLong2 or inSrc == enATShort2 :
        if inDst == enATFloat2 or inDst == enATDouble2 or inDst == enATLong2 or inDst == enATShort2 : return True
        else : return False

      if inSrc == enATFloat3 or inSrc == enATDouble3 or inSrc == enATLong3 or inSrc == enATShort3 :
        if inDst == enATFloat3 or inDst == enATDouble3 or inDst == enATLong3 or inDst == enATShort3 : return True
        else : return False

      if inSrc == enATDouble4 and inDst == enATDouble4 : return True

      if inSrc == enATReflectanceRGB or inSrc == enATSpectrumRGB : 
        if inDst == enATReflectanceRGB or inDst == enATSpectrumRGB : return True
        else : return False

      if inSrc == enATReflectance or inSrc == enATSpectrum :
        if inDst == enATReflectance or inDst == enATSpectrum : return True
        else : return False

      return False

    return True
  if isArrayType(inSrc) == False and inDst == enATMessage : return True
  return False


def isBifrostPortType(inT) : 
  if inT == enATBifrostPortIn or inT == enATBifrostPortOut : return True
  else : return False

def isNumericValueType(inT) :
  if inT & 0x00300 != 0 : return True
  else : return False

def isFloatValueType(inT) :
  if inT & 0x00200 != 0 : return True
  else : return False

def isIntegerValueType(inT) :
  if inT & 0x00100 != 0 : return True
  else : return False

def isStringValueType(inT) : 
  if inT & 0x00400 != 0 : return True
  else : return False

def isObjectValueType(inT) : 
  if inT & 0x00800 != 0 : return True
  else : return False

def hasChildValueType(inT) :
  if inT & 0x10000 != 0 : return True
  else : return False

def isArrayType(inT) :
  if inT & 0x20000 != 0 : return True
  else : return False

def numberOfChildValue(inT) : 
  n = ( inT & 0x0f000 ) >> 12
  return n + 1

def getPlugValueType(inPlg) :
  attrObj = inPlg.attribute()
  try :
    fn = OpenMaya.MFnEnumAttribute(attrObj)
    minV = fn.getMin()
    maxV = fn.getMax()
    for v in range(minV, maxV) :
      try :
        s = fn.fieldName(v)
        if s is not None and len(s) > 0 : 
          return enATEnum
      except :
        pass
  except : pass

  try :
    fn = OpenMaya.MFnMatrixAttribute(attrObj)
    v = fn.default
    dh = inPlg.asMDataHandle()
    v = dh.asMatrix()
    return enATMatrix
  except : pass

  try :
    fn = OpenMaya.MFnUnitAttribute(attrObj)
    ut = fn.unitType()
    if ut == OpenMaya.MFnUnitAttribute.kAngle : return enATDoubleAngle
    if ut == OpenMaya.MFnUnitAttribute.kDistance : return enATDoubleLinear
    if ut == OpenMaya.MFnUnitAttribute.kTime : return enATTime
    return enATInvalid
  except : pass

  try :
    fn = OpenMaya.MFnNumericAttribute(attrObj)
    nt = fn.numericType()
    if nt == OpenMaya.MFnNumericData.kInt64 : return enATLong
    if nt == OpenMaya.MFnNumericData.k2Double : return enATDouble2
    if nt == OpenMaya.MFnNumericData.k2Float : return enATFloat2
    if nt == OpenMaya.MFnNumericData.k2Long : return enATLong2
    if nt == OpenMaya.MFnNumericData.k2Short : return enATShort2
    if nt == OpenMaya.MFnNumericData.k3Double : return enATDouble3
    if nt == OpenMaya.MFnNumericData.k3Float : return enATFloat3
    if nt == OpenMaya.MFnNumericData.k3Long : return enATLong3
    if nt == OpenMaya.MFnNumericData.k3Short : return enATShort3
    if nt == OpenMaya.MFnNumericData.k4Double : return enATDouble4
    if nt == OpenMaya.MFnNumericData.kAddr : return enATAddr
    if nt == OpenMaya.MFnNumericData.kBoolean : return enATBool
    if nt == OpenMaya.MFnNumericData.kByte : return enATByte
    if nt == OpenMaya.MFnNumericData.kChar : return enATChar
    if nt == OpenMaya.MFnNumericData.kDouble : return enATDouble
    if nt == OpenMaya.MFnNumericData.kFloat : return enATFloat
    if nt == OpenMaya.MFnNumericData.kLong : return enATLong
    if nt == OpenMaya.MFnNumericData.kShort : return enATShort
  except : pass

  try :
    fn = OpenMaya.MFnTypedAttribute(attrObj)
    at = fn.attrType()
    if at == OpenMaya.MFnData.kFloatArray : return enATFloatArray
    if at == OpenMaya.MFnData.kMatrixArray : return enATMatrixArray
    if at == OpenMaya.MFnData.kDoubleArray : return enATDoubleArray
    if at == OpenMaya.MFnData.kIntArray : return enATInt32Array
    if at == OpenMaya.MFnData.kLattice : return enATLattice
    if at == OpenMaya.MFnData.kMesh : return enATMesh
    if at == OpenMaya.MFnData.kNurbsCurve : return enATNurbsCurve
    if at == OpenMaya.MFnData.kNurbsSurface : return enATNurbsSurface
    if at == OpenMaya.MFnData.kPointArray : return enATPointArray
    if at == OpenMaya.MFnData.kString : return enATString
    if at == OpenMaya.MFnData.kStringArray : return enATStringArray
    if at == OpenMaya.MFnData.kVectorArray : return enATVectorArray
    if at == OpenMaya.MFnData.kMatrix : return enATMatrix
  except : pass

  if inPlg.isCompound : 
    # test Rigging::Module::Outputs or Rigging::Module::Inputs
    #if isBifrost_RiggingModuleInputs(inPlg) : return enATBifrostRiggingModuleInputs
    #if isBifrost_RiggingModuleOutputs(inPlg) : return enATBifrostRiggingModuleOutputs
    return enATCompound

  try :
    fn = OpenMaya.MFnMessageAttribute(attrObj)
    tmp = fn.name
    return enATMessage
  except : pass

  return enATInvalid

def isBifrost_RiggingModuleOutputs(inPlg) : 
  if inPlg.isCompound == False : return False
  if inPlg.isArray : return False
  setupPlg = None
  animationPlg = None
  internalPlg = None
  plgNm = getMPlugAttributeName(inPlg, cutUnderlineNumber=True)
  chCnt = inPlg.numChildren()
  for chIdx in range(chCnt) : 
    chPlg = inPlg.child(chIdx)
    if chPlg.isCompound == False : continue
    chNm = getMPlugAttributeName(chPlg)
    if chNm == plgNm + u'_setup' or chNm == u'setup' : setupPlg = chPlg
    elif chNm == plgNm + u'_animation' or chNm == u'animation' : animationPlg = chPlg
    elif chNm == plgNm + u'_internal' or chNm == u'internal' : internalPlg = chPlg
  if setupPlg is None or animationPlg is None or internalPlg is None : return False
  
  # check setup
  controlsPlg = None
  jointsPlg = None
  plgNm = getMPlugAttributeName(setupPlg, cutUnderlineNumber=True)
  chCnt = setupPlg.numChildren()
  for chIdx in range(chCnt) : 
    chPlg = setupPlg.child(chIdx)
    chNm = getMPlugAttributeName(chPlg)
    if chPlg.isCompound : 
      if chNm == plgNm + u'_controls' or chNm == u'controls' : controlsPlg = chPlg
      elif chNm == plgNm + u'_joints' or chNm == u'joints' : jointsPlg = chPlg
  if controlsPlg is None or jointsPlg is None : return False
  # check setup_controls
  namesPlg = None
  pathsPlg = None
  tagsPlg = None
  transformConfigsPlg = None
  shapesPlg = None
  attributeDescriptionsPlg = None
  attributeDataPlg = None
  plgNm = getMPlugAttributeName(controlsPlg, cutUnderlineNumber=True)
  chCnt = controlsPlg.numChildren()
  for chIdx in range(chCnt) : 
    chPlg = controlsPlg.child(chIdx)
    chNm = getMPlugAttributeName(chPlg)
    valTp = getPlugValueType(chPlg)
    if chPlg.isArray : 
      if chNm == plgNm + u'_names' or chNm == u'names' : 
        if valTp == enATString : namesPlg = chPlg
      elif chNm == plgNm + u'_paths' or chNm == u'paths' : 
        if valTp == enATString : pathsPlg = chPlg
      elif chNm == plgNm + u'_tags' or chNm == u'tags' :
        if valTp == enATCompound : tagsPlg = chPlg
      elif chNm == plgNm + u'_transform_configs' or chNm == u'transform_configs' :
        if valTp == enATCompound : transformConfigsPlg = chPlg
      elif chNm == plgNm + u'_shapes' or chNm == u'shapes' : 
        if valTp == enATCompound : shapesPlg = chPlg
      elif chNm == plgNm + u'_attribute_descriptions' or chNm == u'attribute_descriptions' : 
        if valTp == enATCompound : attributeDescriptionsPlg = chPlg
    elif chPlg.isCompound : 
      if chNm == plgNm + u'_attribute_data' or chNm == u'attribute_data' : attributeDataPlg = chPlg
  if namesPlg is None or pathsPlg is None or tagsPlg is None or transformConfigsPlg is None or shapesPlg is None or attributeDescriptionsPlg is None or attributeDataPlg is None : return False
  # check setup_joints
  namesPlg = None
  pathsPlg = None
  tagsPlg = None
  transformConfigsPlg = None
  colorsPlg = None
  radiusesPlg = None
  plgNm = getMPlugAttributeName(jointsPlg, cutUnderlineNumber=True)
  chCnt = jointsPlg.numChildren()
  for chIdx in range(chCnt) : 
    chPlg = jointsPlg.child(chIdx)
    chNm = getMPlugAttributeName(chPlg)
    valTp = getPlugValueType(chPlg)
    if chPlg.isArray == False : continue
    if chNm == plgNm + u'_names' or chNm == u'names' :
      if valTp == enATString : namesPlg = chPlg
    elif chNm == plgNm + u'_paths' or chNm == u'paths' :
      if valTp == enATString : pathsPlg = chPlg
    elif chNm == plgNm + u'_tags' or chNm == u'tags' : 
      if valTp == enATCompound : tagsPlg = chPlg
    elif chNm == plgNm + u'_transform_configs' or chNm == u'transform_configs' :
      if valTp == enATCompound : transformConfigsPlg = chPlg
    elif chNm == plgNm + u'_colors' or chNm == u'colors' :
      if valTp == enATFloat3 : colorsPlg = chPlg
    elif chNm == plgNm + u'_radiuses' or chNm == u'radiuses' :
      if valTp == enATFloat : radiusesPlg = chPlg
  if namesPlg is None or pathsPlg is None or tagsPlg is None or transformConfigsPlg is None or colorsPlg is None or radiusesPlg is None : return False

  # check animation
  controlTransformsPlg = None
  jointTransformsPlg = None
  plgNm = getMPlugAttributeName(animationPlg, cutUnderlineNumber=True)
  chCnt = animationPlg.numChildren()
  for chIdx in range(chCnt) : 
    chPlg = animationPlg.child(chIdx)
    chNm = getMPlugAttributeName(chPlg)
    if chPlg.isArray == False : continue
    if chPlg.isCompound == False : continue
    if chNm == plgNm + u'_control_transforms' or chNm == u'control_transforms' : controlTransformsPlg = chPlg
    elif chNm == plgNm + u'_joint_transforms' or chNm == u'joint_transforms' : jointTransformsPlg = chPlg
  if controlTransformsPlg is None or jointTransformsPlg is None : return False

  # check internal
  namePlg = None
  moduleIdPlg = None
  setupHashPlg = None
  setupDirtyPlg = None
  plgNm = getMPlugAttributeName(internalPlg)
  chCnt = internalPlg.numChildren()
  for chIdx in range(chCnt) : 
    chPlg = internalPlg.child(chIdx)
    chNm = getMPlugAttributeName(chPlg)
    valTp = getPlugValueType(chPlg)
    if chNm == plgNm + u'_name' or chNm == u'name' :
      if valTp == enATString: namePlg = chPlg
    elif chNm == plgNm + u'_module_id' or chNm == u'module_id' :
      if valTp == enATLong : moduleIdPlg = chPlg
    elif chNm == plgNm + u'_setup_hash' or chNm == u'setup_hash' : 
      if valTp == enATLong : setupHashPlg = chPlg
    elif chNm == plgNm + u'_setup_dirty' or chNm == u'setup_dirty' :
      if valTp == enATBool : setupDirtyPlg = chPlg
  if namePlg is None or moduleIdPlg is None or setupHashPlg is None or setupDirtyPlg is None : return False

  return True


def isBifrost_RiggingModuleInputs(inPlg) : 
  if inPlg.isCompound == False : return False

  return False


def getPlugValue(inPlg, valueType=None) :
  if valueType is None : valueType = getPlugValueType(inPlg)
  if inPlg.isArray : 
    lst = []
    elmCnt = inPlg.evaluateNumElements()
    for elmIdx in range(elmCnt) : 
      elmPlg = inPlg.elementByPhysicalIndex(elmIdx)
      lst.append(getPlugValue(elmPlg, valueType=valueType))
    return lst

  if valueType == enATBool : return inPlg.asBool()
  elif valueType == enATLong : return inPlg.asInt()
  elif valueType == enATShort or valueType == enATEnum : return inPlg.asShort()
  elif valueType == enATByte or valueType == enATChar : return inPlg.asChar()
  elif valueType == enATFloat : return inPlg.asFloat()
  elif valueType == enATDouble : return inPlg.asDouble()
  elif valueType == enATDoubleAngle : return inPlg.asMAngle().asDegrees()
  elif valueType == enATDoubleLinear : return inPlg.asMDistance().asCentimeters()
  elif valueType == enATString : return inPlg.asString()
  elif valueType == enATTime : return inPlg.asMTime().asUnits(OpenMaya.MTime.uiUnit())
  elif valueType == enATMatrix or valueType == enATFltMatrix : return getMMatrixValue(inPlg)
  elif valueType == enATFloat2 : return inPlg.asMDataHandle().asFloat2()
  elif valueType == enATFloat3 : return inPlg.asMDataHandle().asFloat3()
  elif valueType == enATDouble2 : return inPlg.asMDataHandle().asDouble2()
  elif valueType == enATDouble3 : return inPlg.asMDataHandle().asDouble3()
  elif valueType == enATLong2 : return inPlg.asMDataHandle().asInt2()
  elif valueType == enATLong3 : return inPlg.asMDataHandle().asInt3()
  elif valueType == enATShort2 : return inPlg.asMDataHandle().asShort2()
  elif valueType == enATShort3 : return inPlg.asMDataHandle().asShort3()
  elif valueType == enATDouble4 : return inPlg.asMDataHandle().asDouble4()
  '''
  enATStringArray    = 0x2200b
  enATCompound       = 0x1000c
  enATMessage        = 0x0000d
  enATReflectanceRGB = 0x10211
  enATReflectance    = 0x00212
  enATSpectrumRGB    = 0x10213
  enATSpectrum       = 0x00214
  enATDoubleArray    = 0x2011d
  enATFloatArray     = 0x2011e
  enATInt32Array     = 0x2011f
  enATVectorArray    = 0x20120
  enATNurbsCurve     = 0x00021
  enATNurbsSurface   = 0x00022
  enATMesh           = 0x00023
  enATLattice        = 0x00024
  enATPointArray     = 0x20225
  enATMatrixArray    = 0x20226
  enATAddr           = 0x00128
  '''
  return None


def getValueTypeString(inT) :
  if inT == enATInvalid : return u'invalid'
  if inT == enATBool : return u'bool'
  if inT == enATLong : return u'long'
  if inT == enATShort : return u'short'
  if inT == enATByte : return u'byte'
  if inT == enATChar : return u'char'
  if inT == enATEnum : return u'enum'
  if inT == enATFloat : return u'float'
  if inT == enATDouble : return u'double'
  if inT == enATDoubleAngle : return u'doubleAngle'
  if inT == enATDoubleLinear : return u'doubleLinear'
  if inT == enATString : return u'string'
  if inT == enATStringArray : return u'stringArray'
  if inT == enATCompound : return u'compound'
  if inT == enATMessage : return u'message'
  if inT == enATTime : return u'time'
  if inT == enATMatrix : return u'matrix'
  if inT == enATFltMatrix : return u'fltMatrix'
  if inT == enATReflectanceRGB : return u'reflectanceRGB'
  if inT == enATReflectance : return u'reflectance'
  if inT == enATSpectrumRGB : return u'spectrumRGB'
  if inT == enATSpectrum : return u'spectrum'
  if inT == enATFloat2 : return u'float2'
  if inT == enATFloat3 : return u'float3'
  if inT == enATDouble2 : return u'double2'
  if inT == enATDouble3 : return u'double3'
  if inT == enATLong2 : return u'long2'
  if inT == enATLong3 : return u'long3'
  if inT == enATShort2 : return u'short2'
  if inT == enATShort3 : return u'short3'
  if inT == enATDoubleArray : return u'doubleArray'
  if inT == enATFloatArray : return u'floatArray'
  if inT == enATInt32Array : return u'int32Array'
  if inT == enATVectorArray : return u'vectorArray'
  if inT == enATNurbsCurve : return u'nurbsCurve'
  if inT == enATNurbsSurface : return u'nurbsSurface'
  if inT == enATMesh : return u'mesh'
  if inT == enATLattice : return u'lattice'
  if inT == enATPointArray : return u'pointArray'
  if inT == enATMatrixArray : return u'matrixArray'
  if inT == enATDouble4 : return u'double4'
  if inT == enATAddr : return u'addr'
  return u'unknown'


def getBiflostType(inT) : 
  if inT == enATBool : return u'bool'
  elif inT == enATLong : return u'int'
  elif inT == enATShort : return u'short'
  elif inT == enATByte : return u'uchar'
  elif inT == enATChar : return u'char'
  elif inT == enATEnum : return u'short'
  elif inT == enATFloat : return u'float'
  elif inT == enATDouble : return u'double'
  elif inT == enATDoubleAngle : return u'double'
  elif inT == enATDoubleLinear : return u'double'
  elif inT == enATString : return u'string'
  elif inT == enATTime : return u'double'
  elif inT == enATMatrix : return u'Math::double4x4'
  elif inT == enATFltMatrix : return u'Math::float4x4'
  elif inT == enATFloat2 : return u'Math::float2'
  elif inT == enATFloat3 : return u'Math::float3'
  elif inT == enATDouble2 : return u'Math::double2'
  elif inT == enATDouble3 : return u'Math::double3'
  elif inT == enATDouble4 : return u'Math::double4'
  elif inT == enATLong2 : return u'Math::int2'
  elif inT == enATLong3 : return u'Math::int3'
  elif inT == enATShort2 : return u'Math::short2'
  elif inT == enATShort3 : return u'Math::short3'
  elif inT == enATMesh : return u'Amino::Object'
  elif inT == enATBifrostRiggingModuleOutputs : return u'Rigging::Module::Outputs'
  else : return None

