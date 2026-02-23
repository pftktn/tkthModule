# -*- coding: utf-8 -*-
'''
MayaのDrawing OverridesのColor indexに対応。
'''

import maya.api.OpenMaya as OpenMaya

try :
  import PySide6.QtGui as QtGui
except :
  import PySide2.QtGui as QtGui



class qtDrawingOverridesColor(QtGui.QColor) : 
  # 色の名前の数値のリスト
  mayaDOColorList = [
    [ u'gray', [120, 120, 120] ],
    [ u'black', [0, 0, 0] ],
    [ u'dark gray', [64, 64, 64] ], 
    [ u'light gray', [153, 153, 153] ],
    [ u'dark red', [155, 0, 40] ],
    [ u'dark blue', [0, 4, 96] ],
    [ u'blue', [0, 0, 255] ],
    [ u'dark green', [0, 70, 25] ],
    [ u'dark magenta', [38, 0, 67] ],
    [ u'magenta', [200, 0, 200]],
    [ u'brown', [138, 72, 51]],
    [ u'dark brown', [63, 35, 31]],
    [ u'dark orange', [153, 38, 0]],
    [ u'red', [255, 0, 0]],
    [ u'green', [0, 255, 0]],
    [ u'dark navy', [0, 65, 153]],
    [ u'white', [255, 255, 255] ],
    [ u'yellow', [255, 255, 0]],
    [ u'sky blue', [100, 220, 255]],
    [ u'emerald green', [67, 255, 163]],
    [ u'rose', [255, 176, 176]],
    [ u'light orange', [228, 172, 121]],
    [ u'light yellow', [255, 255, 99]],
    [ u'dark emerald', [0, 153, 84]],
    [ u'tang', [161, 106, 48]],
    [ u'gold', [158, 161, 48]],
    [ u'grass', [104, 161, 48]],
    [ u'dark blue green', [48, 161, 93]],
    [ u'blue green', [48, 161, 161]],
    [ u'blue gray', [48, 103, 161]],
    [ u'purple', [111, 48, 161]],
    [ u'pink', [161, 48, 106]]
  ]
  enMayaDOGray = 0
  enMayaDOBlack = 1
  enMayaDODarkGray = 2
  enMayaDOLightGray = 3
  enMayaDODarkRed = 4
  enMayaDODarkBlue = 5
  enMayaDOBlue = 6
  enMayaDODarkGreen = 7
  enMayaDODarkMagenta = 8
  enMayaDOMagenta = 9
  enMayaDOBrown = 10
  enMayaDODarkBrown = 11
  enMayaDODarkOrange = 12
  enMayaDORed = 13
  enMayaDOGreen = 14
  enMayaDODarkNavy = 15
  enMayaDOWhite = 16
  enMayaDOYellow = 17
  enMayaDOSkyBlue = 18
  enMayaDOEmeraldGreen = 19
  enMayaDORose = 20
  enMayaDOLightOrange = 21
  enMayaDOLightYellow = 22
  enMayaDODarkEmerald = 23
  enMayaDOTang = 24
  enMayaDOGold = 25
  enMayaDOGrass = 26
  enMayaDODarkBlueGreen = 27
  enMayaDOBlueGreen = 28
  enMayaDOBlueGray = 29
  enMayaDOPurple =30
  enMayaDOPink =31

  '''
  def __init__(self, inNm, alpha=255) : 
    rgb = [127,127,127]
    for col in qtDrawingOverridesColor.mayaDOColorList : 
      if col[0] == inNm : 
        rgb = col[1]
        break
    super(__class__, self).__init__(rgb[0], rgb[1], rgb[2], alpha)

  def __init__(self, inIdx, alpha=255) : 
    super(__class__, self).__init__(qtDrawingOverridesColor.mayaDOColorList[inIdx][1][0], qtDrawingOverridesColor.mayaDOColorList[inIdx][2][0], qtDrawingOverridesColor.mayaDOColorList[inIdx][3][0], alpha)
  '''

  def __init__(self, inFn, rgba=None) : 
    if rgba is None : rgba = [255, 255, 255, 255]
    plg = inFn.findPlug(u'overrideEnabled', True)
    if plg.asBool() :
      plg = inFn.findPlug(u'overrideRGBColors', True)
      if plg.asBool() :
        for idx, rgbChar in enumerate([u'R', u'G', u'B']) : 
          plgRGB = inFn.findPlug(u'overrideColor' + rgbChar, True)
          rgba[idx] = int(plgRGB.asFloat() * 255.0)
          if rgba[idx] < 0 : rgba[idx] = 0
          elif rgba[idx] > 255 : rgba[idx] = 255
      else :
        plgIdx = inFn.findPlug(u'overrideColor', True)
        idx = 0
        dh = None
        try :
          dh = plgIdx.asMDataHandle()
          idx = dh.asUChar()
        finally :
          if dh is not None : plgIdx.destructHandle(dh)
        rgba[0] = qtDrawingOverridesColor.mayaDOColorList[idx][1][0]
        rgba[1] = qtDrawingOverridesColor.mayaDOColorList[idx][1][1]
        rgba[2] = qtDrawingOverridesColor.mayaDOColorList[idx][1][2]
    super(__class__, self).__init__(rgba[0], rgba[1], rgba[2], rgba[3])
