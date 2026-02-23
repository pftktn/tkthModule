import maya.cmds as cmds
import maya.api.OpenMaya as OpenMaya
import maya.api.OpenMayaAnim as OpenMayaAnim

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


class pullDownBifrostUtility(base.pullDownBase) : 
  def __init__(self, inMenu, inItmLst, inCore) : 
    super().__init__(inMenu, inItmLst, inCore)
    bfLst = self.filterByTypeIdList(self.bifrostTypeIdList)
    if len(bfLst) < 1 : raise Exception()

    subMenu = self.menu.addMenu(u'bifrost utility')
    act = subMenu.addAction(u'create rigging')
    act.triggered.connect(self.create_rigging)
    act = subMenu.addAction(u'fix zero port')
    act.triggered.connect(self.fixZeroPort)


  def ioPortList(self, inBfNd, inNd, input=True) : 
    tpNm = cmds.vnnNode(inBfNd, inNd, queryTypeName=True)
    if tpNm != u'' : return None
    
    ndLst = inNd.split(u'/')
    if input : 
      if ndLst[-1].startswith(u'input') == False : return None
    else : 
      if ndLst[-1].startswith(u'output') == False : return None

    try : 
      lst = cmds.vnnCompound(inBfNd, inNd, listPorts=True)
      return None
    except : 
      pass
    portLst = None
    try : 
      portLst = cmds.vnnNode(inBfNd, inNd, listPorts=True)
    except : 
      return None
    lst = list()
    if portLst is not None : 
      for prt in portLst : 
        ndPrt = prt.split(u'.')
        ndPrt.pop(0)
        lst.append(u'.'.join(ndPrt))
    return lst

  def isTemplateModule(self, inBfNd, inNd) : 
    try :
      prtLst = cmds.vnnCompound(inBfNd, inNd, listPorts=True)
      tmpPrtLst = [ 
        ( u'inputs', u'Rigging::Module::Inputs' ),
        ( u'parents', u'array<Rigging::Module::Outputs>' ),
        ( u'name', u'string' ),
        ( u'state', u'int' ),
        ( u'display_pins', u'bool' ),
        ( u'display_controls', u'bool' ),
        ( u'display_joints', u'bool' ),
        ( u'display_transforms', u'bool' ),
        ( u'axes_shape', u'Geometry::StrandShapes' ),
        ( u'axes_scale', u'float' ),
        ( u'profile_evaluation', u'bool' ),
        ( u'edit_mode', u'bool' )
      ]
      for prtTp in tmpPrtLst : 
        ( prt, tp ) = prtTp
        if prt not in prtLst : 
          print((prt, prtLst))
          return False
        curTp = cmds.vnnNode(inBfNd, inNd, queryPortDataType=prt)
        if curTp != tp : 
          print((prt, tp, curTp))
          return False
    except : 
      return False
    return True


  def getIOTemplateNode(self, inBfNd) : 
    ndLst = cmds.vnnCompound(inBfNd, u'/', listNodes=True)
    inputNd = None
    outputNd = None
    templateNd = None
    for nd in ndLst : 
      if inputNd is not None and outputNd is not None and templateNd is not None : break
      
      ndPth = u'/' + nd
      lst = self.ioPortList(inBfNd, ndPth, input=True)
      if lst is not None : 
        inputNd = ( ndPth, lst )
        continue
      lst = self.ioPortList(inBfNd, ndPth, input=False)
      if lst is not None : 
        outputNd = ( ndPth, lst )
        continue
      if self.isTemplateModule(inBfNd, ndPth) : 
        templateNd = ndPth
        continue

    return ( inputNd, outputNd, templateNd )


  def getBifrostRIG(self, inBfNd, inAttr) : 
    rootLst = list()
    for trfAttr in [ u'control_transforms', u'joint_transforms' ] : 
      # trfAttrNm = u'.'.join([inAttr, u'animation', trfAttr])
      trfAttrNm = u'_'.join([inAttr, u'animation', trfAttr])
      attrLst = cmds.attributeQuery(trfAttrNm, node=inBfNd, listChildren=True)
      chAttrLst = list()
      for attr in attrLst : 
        lst = attr.split(u'.')
        chAttrLst.append(lst[-1])

      idxLst = cmds.getAttr(inBfNd + u'.' + trfAttrNm, multiIndices=True)
      for idx in idxLst : 
        # trfAttrElmNm = plugName(inBfNd, [inAttr, u'animation', (trfAttr, idx)])
        trfAttrElmNm = plugName(inBfNd, (trfAttrNm, idx))
        que = list()
        for chAttr in chAttrLst : 
          lst = cmds.listConnections(trfAttrElmNm + u'.' + chAttr, source=False, destination=True, skipConversionNodes=True)
          if lst is not None : que.extend(lst)

        cnt = 1024
        while len(que) > 0 and cnt > 0 : 
          cnt = cnt - 1
          nd = que.pop(0)
          if cmds.objectType(nd, isAType=u'transform') : 
            rtNd = getRoot(nd)
            if rtNd not in rootLst : rootLst.append(rtNd)
            continue
          dstLst = cmds.listConnections(nd, source=False, destination=True, skipConversionNodes=True)
          if dstLst is not None : 
            for dst in dstLst : 
              if dst not in que : que.append(dst)
    if len(rootLst) == 0 : return None
    return rootLst[0]
  

  def create_rigging(self) : 
    opnUndChk = False
    bfLst = self.filterByTypeIdList(self.__bifrostTypeIdList)
    try :
      cmds.undoInfo(openChunk=True, chunkName=u'create bifrost rigging')
      opnUndChk = True

      bfRigLst = list()
      for itm in bfLst :
        ndNm = itm.itemUniqueName
        ( inputNd, outputNd, templateNd ) = self.getIOTemplateNode(ndNm)
        if inputNd is None or outputNd is None or templateNd is None : continue

        outputPrtNm = u'outputs'
        for prt in outputNd[1] : 
          tp = cmds.vnnNode(ndNm, outputNd[0], queryPortDataType=prt)
          if tp == u'Rigging::Module::Outputs' : 
            bfRIGNd = self.getBifrostRIG(ndNm, prt)
            if bfRIGNd is not None : cmds.delete(bfRIGNd)
            #try : 
            #  cmds.vnnConnect(ndNm, templateNd + u'.outputs', outputNd[0] + u'.' + prt, disconnect=True)
            #except : pass
            # cmds.vnnNode(ndNm, outputNd[0], deletePort=prt)
            # melStr = u'vnnNode -deletePort \"' + prt + u'\" \"' + ndNm + u'\" \"' + outputNd[0] + u'\";'
            melStr = u'vnnCompound \"' + ndNm + u'\" \"/\" -deletePort \"' + prt + u'\";'
            self.logMessage(melStr)
            mel.eval(melStr)
            outputPrtNm = prt

        inputPrtNm = u'inputs'
        for prt in inputNd[1] : 
          tp = cmds.vnnNode(ndNm, inputNd[0], queryPortDataType=prt)
          if tp == u'Rigging::Module::Inputs' : 
            #try : 
            #  cmds.vnnConnect(ndNm, inputNd[0] + u'.' + prt, templateNd + u'.inputs', disconnect=True)
            #except : pass
            #cmds.vnnNode(ndNm, inputNd[0], deletePort=prt)
            # melStr = u'vnnNode -deletePort \"' + prt + u'\" \"' + ndNm + u'\" \"' + inputNd[0] + u'\";'
            melStr = u'vnnCompound \"' + ndNm + u'\" \"/\" -deletePort \"' + prt + u'\";'
            self.logMessage(melStr)
            mel.eval(melStr)
            inputPrtNm = prt
        
        try : 
          prtValLst = cmds.vnnNode(ndNm, templateNd, queryPortDefaultValues=u'inputs')
          prtValStr = str(prtValLst.pop(0))
          for prtVal in prtValLst : 
            prtValStr = prtValStr + u', ' + str(prtVal)

          prtValStr = u'{' + prtValStr + u'}'
          melStr = u''
          melStr = melStr + u'vnnPort \"' + ndNm + u'\" \"' + templateNd + u'.inputs' + u'\" 0 1 -set 16;\n'
          melStr = melStr + u'vnnNode \"' + ndNm + u'\" \"' + inputNd[0] + u'\" -createOutputPort \"' + inputPrtNm + u'\" \"Rigging::Module::Inputs\" -portValues \"' + prtValStr + u'\";\n'
          melStr = melStr + u'vnnConnect \"' + ndNm + u'\" \".' + inputPrtNm + u'\" \"' + templateNd + u'.inputs' + u'\" -copyMetaData;\n'
          melStr = melStr + u'vnnPort \"' + ndNm + u'\" \"' + templateNd + u'.inputs' + u'\" 0 1 -clear 16;\n'
          self.logMessage(melStr)
          mel.eval(melStr)

          melStr = u''
          melStr = melStr + u'vnnPort \"' + ndNm + u'\" \"' + templateNd + u'.outputs' + u'\" 1 1 -set 16;\n'
          melStr = melStr + u'vnnNode \"' + ndNm + u'\" \"' + outputNd[0] + u'\" -createInputPort \"' + outputPrtNm + u'\" \"Rigging::Module::Outputs\";\n'
          melStr = melStr + u'vnnConnect \"' + ndNm + u'\" \"' + templateNd + u'.outputs' + u'\" \".' + outputPrtNm + u'\";\n'
          melStr = melStr + u'vnnPort \"' + ndNm + u'\" \"' + templateNd + u'.outputs' + u'\" 1 1 -clear 16;\n'
          self.logMessage(melStr)
          mel.eval(melStr)
        except : continue

        bfRigLst.append(u'\"' + ndNm + u'\"')
        '''
        cmds.select(ndNm, replace=True)
        melStr = u''
        melStr = melStr + u'python(\"import bifrostRigging\\nbifrostRigging.createRigFromModules()\\n\");\n'
        self.core.logMessage(melStr)
        mel.eval(melStr)
        '''
      
      if len(bfRigLst) > 0 : 
        melStr = u''
        melStr = melStr + u'bifrostRigging'
        melStr = melStr + u' -createControls 1'
        melStr = melStr + u' -createJoints 1'
        melStr = melStr + u' -createRig 1'
        melStr = melStr + u' -flattenControls 0'
        melStr = melStr + u' -flattenJoints 0'
        melStr = melStr + u' -moduleTerminals 0'
        melStr = melStr + u' -optimizeModules 0'
        melStr = melStr + u' -setupMethod \"native\"'
        melStr = melStr + u' -syncedContainer 0'
        melStr = melStr + u' ' + u' '.join(bfRigLst)
        self.logMessage(melStr)
        mel.eval(melStr)
    finally :
      if opnUndChk : cmds.undoInfo(closeChunk=True)
      self.core.core.reloadContent()


  def fixZeroPort(self) : 
    opnUndChk = False
    bfLst = self.filterByTypeIdList(self.__bifrostTypeIdList)
    try :
      #cmds.undoInfo(openChunk=True, chunkName=u'fix bifrost zero port')
      #opnUndChk = True

      for itm in bfLst :
        ndNm = itm.itemUniqueName
        bfNdLst = cmds.vnnCompound(ndNm, u'/', listNodes=True)
        while len(bfNdLst) > 0 : 
          bfNd = bfNdLst.pop(0)
          isCmp = False
          try : 
            isRef = cmds.vnnCompound(ndNm, u'/' + bfNd, queryIsReferenced=True)
            isCmp = True
            if isRef == False : 
              chBfNdLst = cmds.vnnCompound(ndNm, u'/' + bfNd, listNodes=True)
              for chBfNd in chBfNdLst : bfNdLst.append(bfNd + u'/' + chBfNd)
          except : 
            pass

          if isCmp : 
            prtLst = cmds.vnnCompound(ndNm, u'/' + bfNd, listPorts=True, inputPort=True)
            if prtLst is not None : 
              for prt in prtLst : 
                cnnLst = cmds.vnnCompound(ndNm, u'/' + bfNd, listNodes=True, connectedTo=prt, connectedToOutput=True)
                print(bfNd + u'.' + prt + u':O:' + str(cnnLst))
                cnnLst = cmds.vnnCompound(ndNm, u'/' + bfNd, listNodes=True, connectedTo=prt, connectedToInput=True)
                print(bfNd + u'.' + prt + u':I:' + str(cnnLst))
                cnnLst = cmds.vnnNode(ndNm, u'/' + bfNd, listConnectedNodes=True, connectedTo=prt)
                print(bfNd + u'.' + prt + u':ND:' + str(cnnLst))
            # print(bfNd + u':compound:' + str(prtLst))
          else : 
            prtLst = cmds.vnnNode(ndNm, u'/' + bfNd, listPorts=True, inputPort=True)
            print(bfNd + u':node:' + str(prtLst))
    finally :
      if opnUndChk : cmds.undoInfo(closeChunk=True)
      self.core.core.reloadContent()
