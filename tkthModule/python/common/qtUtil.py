# -*- coding: utf-8 -*-
'''
PySide関連の雑多な関数

author : Takeharu TANIMURA <tanie@kk.iij4u.or.jp>
'''

import pathlib
import json
import re

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


import maya.cmds as cmds
import maya.mel as mel



def uniqueWidgetName(inBaseName) :
  maxIdx = 0
  wgtLst = cmds.lsUI(dumpWidgets=True, long=True)
  if wgtLst is not None :
    ptnStr = u'^' + inBaseName + u'(\\d+)$'
    for wgt in wgtLst : 
      rObj = re.match(ptnStr, wgt)
      if rObj is not None and rObj.group(1) is not None :
        idx = int(rObj.group(1))
        if idx > maxIdx : maxIdx = idx
  return inBaseName + str(maxIdx + 1)


def cleanupQtWidget(inUniqueName) :
  scrStr = u''
  scrStr = scrStr + u'\"{ string $wgt[] = \\`lsUI -dumpWidgets\\`; if (stringArrayFind(\\"'
  scrStr = scrStr + inUniqueName
  scrStr = scrStr + u'\\", 0, $wgt) >= 0) deleteUI \\"'
  scrStr = scrStr + inUniqueName
  scrStr = scrStr + u'\\"; }\"'
  mel.eval(u'evalDeferred -lowestPriority ' + scrStr)


def getQtWidget(inUniqueName) :
  lst = list()
  wgtLst = cmds.lsUI(dumpWidgets=True, long=True)
  if wgtLst is not None :
    unqLen = len(inUniqueName) + 1
    ptnStr = inUniqueName + u'|'
    for wgt in wgtLst :
      if wgt == inUniqueName :
        lst.append(wgt)
      elif wgt[:unqLen] == ptnStr :
        lst.append(wgt)
  return lst


def getPysideVersion() :
  v = QtCore.__version__
  if v is None : return None
  lst = v.split(u'.')
  if len(lst) > 2 : return ( int(lst[0]), int(lst[1]), int(lst[2]) )
  else : return None

def getPysideMajorVersion() :
  v = getPysideVersion()
  if v is None : return 0
  else : return v[0]

