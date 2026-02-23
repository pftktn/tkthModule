# -*- coding: utf-8 -*-
'''
JSONファイルの入出力関数

author : Takeharu TANIMURA <tanie@kk.iij4u.or.jp>
'''

import pathlib
import json





def isImmediateType(inTp) : 
  if inTp != int and inTp != float and inTp != str and inTp != bool : return False
  else : return True

def isImmediateList(inLst) : 
  for elm in inLst :
    if isImmediateType(type(elm)) == False : return False
  return True


def loadJSON(inPth) :
  jsPth = pathlib.Path(inPth)
  if jsPth.is_file() == False : return None

  fObj = None
  try :
    fObj = jsPth.open(mode=u'r')
    jsStr = u''
    while True : 
      ln = fObj.readline()
      if ln == u'' : break
      jsStr = jsStr + ln
    fObj.close()
    fObj = None
    
    return json.loads(jsStr)
  finally :
    if fObj is not None : 
      fObj.close()
      fObj = None


def saveJSON_dict(inFObj, inDct, nest=u'', indent=u'\t', elementCount=10) : 
  kLst = list(inDct.keys())
  kCnt = len(kLst)
  if kCnt == 0 : 
    inFObj.write(nest + u'{}')
  else :
    elmNest = nest + indent
    inFObj.write(nest + u'{\n' + elmNest + json.dumps(kLst[0]) + u' : ')
    tp = type(inDct[kLst[0]])
    if isImmediateType(tp) : 
      inFObj.write(json.dumps(inDct[kLst[0]]))
    elif tp == list : 
      inFObj.write(u'\n')
      saveJSON_list(inFObj, inDct[kLst[0]], nest=elmNest + indent, indent=indent, elementCount=elementCount)
    elif tp == dict : 
      inFObj.write(u'\n')
      saveJSON_dict(inFObj, inDct[kLst[0]], nest=elmNest + indent, indent=indent, elementCount=elementCount)
    
    idx = 1
    while idx < kCnt : 
      try : 
        inFObj.write(u',\n' + elmNest + json.dumps(kLst[idx]) + u' : ')
        tp = type(inDct[kLst[idx]])
        if isImmediateType(tp) : 
          inFObj.write(json.dumps(inDct[kLst[idx]]))
        elif tp == list : 
          inFObj.write(u'\n')
          saveJSON_list(inFObj, inDct[kLst[idx]], nest=elmNest + indent, indent=indent, elementCount=elementCount)
        elif tp == dict : 
          inFObj.write(u'\n')
          saveJSON_dict(inFObj, inDct[kLst[idx]], nest=elmNest + indent, indent=indent, elementCount=elementCount)
      finally :
        idx = idx + 1
    inFObj.write(u'\n' + nest + u'}')


def saveJSON_list(inFObj, inLst, nest=u'', indent=u'\t', elementCount=10) : 
  cnt = len(inLst)
  if cnt == 0 : 
    inFObj.write(nest + u'[]')
  elif isImmediateList(inLst) : 
    if cnt < elementCount : 
      inFObj.write(nest + json.dumps(inLst))
    else : 
      elmNest = nest + indent
      inFObj.write(nest + u'[\n' + elmNest)
      inFObj.write(json.dumps(inLst[0]))
      idx = 1
      while idx < cnt : 
        try : 
          if idx % elementCount == 0 : 
            inFObj.write(u',\n' + elmNest)
          else : 
            inFObj.write(u', ')
          inFObj.write(json.dumps(inLst[idx]))
        finally :
          idx = idx + 1
      inFObj.write(u'\n' + nest + u']')
  else : 
    elmNest = nest + indent
    inFObj.write(nest + u'[\n')
    tp = type(inLst[0])
    if isImmediateType(tp) : 
      inFObj.write(elmNest + json.dumps(inLst[0]))
    elif tp == list : 
      saveJSON_list(inFObj, inLst[0], nest=elmNest, indent=indent, elementCount=elementCount)
    elif tp == dict : 
      saveJSON_dict(inFObj, inLst[0], nest=elmNest, indent=indent, elementCount=elementCount)

    idx = 1
    while idx < cnt : 
      try : 
        inFObj.write(u',\n')
        tp = type(inLst[idx])
        if isImmediateType(tp) : 
          inFObj.write(elmNest + json.dumps(inLst[idx]))
        elif tp == list : 
          saveJSON_list(inFObj, inLst[idx], nest=elmNest, indent=indent, elementCount=elementCount)
        elif tp == dict : 
          saveJSON_dict(inFObj, inLst[idx], nest=elmNest, indent=indent, elementCount=elementCount)
      finally :
        idx = idx + 1
    inFObj.write(u'\n' + nest + u']')
    

def saveJSON(inPth, inObj, indent=u'\t', elementCount=10) :
  fObj = None
  try : 
    fObj = open(inPth, mode=u'w')
    tp = type(inObj)
    if isImmediateType(tp) : 
      fObj.write(json.dumps(inObj))
    elif tp == list : 
      saveJSON_list(fObj, inObj, indent=indent, elementCount=elementCount)
    elif tp == dict : 
      saveJSON_dict(fObj, inObj, indent=indent, elementCount=elementCount)
  finally :
    fObj.close()

