# -*- coding: utf-8 -*-
'''
bifrostを使った関数群

author : Takeharu TANIMURA <tanie@kk.iij4u.or.jp>
'''

import maya.cmds as cmds

# u'bool'
# u'int'
# u'short'
# u'uchar'
# u'char'
# u'short'
# u'float'
# u'double'
# u'double'
# u'double'
# u'string'
# u'double'
# u'Math::double4x4'
# u'Math::float4x4'
# u'Math::float2'
# u'Math::float3'
# u'Math::double2'
# u'Math::double3'
# u'Math::double4'
# u'Math::int2'
# u'Math::int3'
# u'Math::short2'
# u'Math::short3'
# u'Amino::Object'
# u'Rigging::Module::Outputs'


def createInputPort(inNode, inName, inType, nodePath=u'/input', sourcePlug=None) : 
  curPortLst = cmds.vnnNode(inNode, nodePath, listPorts=True)
  if curPortLst is None : curPortLst = []
  cmds.vnnNode(inNode, nodePath, createOutputPort=[inName, inType])
  newPortLst = cmds.vnnNode(inNode, nodePath, listPorts=True)
  newPortLst.reverse()
  newPort = None
  for pt in newPortLst : 
    if pt in curPortLst : 
      pass
    else :
      newPort = pt
      try : 
        idx = newPort.index(u'.')
        newPort = newPort[idx+1:]
        if sourcePlug is not None : cmds.connectAttr(sourcePlug, inNode + u'.' + newPort, force=True)
      except : 
        pass
      break
  return newPort


def createOutputPort(inNode, inName, inType, nodePath=u'/output', destinationPlugList=None) :
  curPortLst = cmds.vnnNode(inNode, nodePath, listPorts=True)
  if curPortLst is None : curPortLst = []
  cmds.vnnNode(inNode, nodePath, createInputPort=[inName, inType])
  newPortLst = cmds.vnnNode(inNode, nodePath, listPorts=True)
  newPortLst.reverse()
  for pt in newPortLst : 
    if pt in curPortLst :
      pass
    else :
      newPort = pt
      try : 
        idx = newPort.index(u'.')
        newPort = newPort[idx+1:]
        if destinationPlugList is not None : 
          for dstPlg in destinationPlugList : 
            cmds.connectAttr(inNode + u'.' + newPort, dstPlg, force=True)
      except : 
        pass
      break
  return newPort


def createConstantNode(inNode, inPath, inType) : 
  lst = cmds.vnnCompound(inNode, inPath, addNode=u'BifrostGraph,Core::Constants,' + inType)
  if lst is None or len(lst) == 0 : return None
  ndPath = inPath + lst[0]
  if inType == u'Math::double4x4' or inType == u'Math::float4x4' : 
    cmds.vnnNode(inNode, ndPath, setPortDefaultValues=[u'value', u'{1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1}'])
  elif inType == u'Math::double4' or inType == u'Math::float4' : 
    cmds.vnnNode(inNode, ndPath, setPortDefaultValues=[u'value', u'{0,0,0,1}'])
  return ndPath


def addBifrostNode(inNode, inPath, inType, name=None) : 
  lst = cmds.vnnCompound(inNode, inPath, addNode=inType)
  if lst is None or len(lst) == 0 : return None
  ndPath = inPath + lst[0]
  setDoubleDefault(inNode, ndPath)
  if name is not None : 
    lst = cmds.vnnCompound(inNode, inPath, renameNode=[lst[0], name])
    ndPath = inPath + lst[0]
  return ndPath


def setDoubleDefault(inNode, inPath) : 
  tp = cmds.vnnNode(inNode, inPath, queryTypeName=True)
  if tp == u'BifrostGraph,Core::Math,SRT_to_matrix' : 
    try : 
      cmds.vnnNode(inNode, inPath, setPortDataType=[u'scale', u'Math::double3'])
    except : 
      try : 
        cmds.vnnNode(inNode, inPath, setPortDataType=[u'quaternion', u'Math::double4'])
      except : 
        cmds.vnnNode(inNode, inPath, setPortDataType=[u'translate', u'Math::double3'])
    try : cmds.vnnNode(inNode, inPath, setPortDefaultValues=[u'scale', u'{1,1,1}'])
    except : pass
    try : cmds.vnnNode(inNode, inPath, setPortDefaultValues=[u'quaternion', u'{0,0,0,1}'])
    except : pass
  elif tp == u'BifrostGraph,Core::Math,matrix_to_SRT' : 
    try : cmds.vnnNode(inNode, inPath, setPortDataType=[u'transform', u'Math::double4x4'])
    except : pass
    try : cmds.vnnNode(inNode, inPath, setPortDefaultValues=[u'transform', u'{1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1}'])
    except : pass


def setCompoundInputDefault(inNode, inPath) : 
  ptLst = cmds.vnnCompound(inNode, inPath, listPorts=True, inputPort=True)
  if ptLst is None or len(ptLst) == 0 : return
  for pt in ptLst : 
    tp = cmds.vnnCompound(inNode, inPath, queryPortDataType=pt)
    if tp == u'Math::double4x4' or tp == u'Math::float4x4' : 
      cmds.vnnNode(inNode, inPath, setPortDefaultValues=[pt, u'{1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1}'])
    elif tp == u'Math::double4' or tp == u'Math::float4' : 
      cmds.vnnNode(inNode, inPath, setPortDefaultValues=[pt, u'{0,0,0,1}'])
