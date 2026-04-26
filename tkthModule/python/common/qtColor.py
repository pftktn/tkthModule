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
  #mayaDOGray = qtDrawingOverridesColor(None, rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDOGray])
  enMayaDOBlack = 1
  #mayaDOBlack = qtDrawingOverridesColor(None, rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDOBlack])
  enMayaDODarkGray = 2
  #mayaDODarkGray = qtDrawingOverridesColor(None, rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDODarkGray])
  enMayaDOLightGray = 3
  #mayaDOLightGray = qtDrawingOverridesColor(None, rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDOLightGray])
  enMayaDODarkRed = 4
  #mayaDODarkRed = qtDrawingOverridesColor(None, rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDODarkRed])
  enMayaDODarkBlue = 5
  #mayaDODarkBlue = qtDrawingOverridesColor(None, rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDODarkBlue])
  enMayaDOBlue = 6
  #mayaDOBlue = qtDrawingOverridesColor(None, rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDOBlue])
  enMayaDODarkGreen = 7
  #mayaDO = qtDrawingOverridesColor(rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDO])
  enMayaDODarkMagenta = 8
  #mayaDO = qtDrawingOverridesColor(rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDO])
  enMayaDOMagenta = 9
  #mayaDO = qtDrawingOverridesColor(rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDO])
  enMayaDOBrown = 10
  #mayaDO = qtDrawingOverridesColor(rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDO])
  enMayaDODarkBrown = 11
  #mayaDO = qtDrawingOverridesColor(rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDO])
  enMayaDODarkOrange = 12
  #mayaDO = qtDrawingOverridesColor(rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDO])
  enMayaDORed = 13
  #mayaDO = qtDrawingOverridesColor(rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDO])
  enMayaDOGreen = 14
  #mayaDO = qtDrawingOverridesColor(rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDO])
  enMayaDODarkNavy = 15
  #mayaDO = qtDrawingOverridesColor(rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDO])
  enMayaDOWhite = 16
  #mayaDO = qtDrawingOverridesColor(rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDO])
  enMayaDOYellow = 17
  #mayaDO = qtDrawingOverridesColor(rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDO])
  enMayaDOSkyBlue = 18
  #mayaDO = qtDrawingOverridesColor(rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDO])
  enMayaDOEmeraldGreen = 19
  #mayaDO = qtDrawingOverridesColor(rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDO])
  enMayaDORose = 20
  #mayaDO = qtDrawingOverridesColor(rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDO])
  enMayaDOLightOrange = 21
  #mayaDO = qtDrawingOverridesColor(rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDO])
  enMayaDOLightYellow = 22
  #mayaDO = qtDrawingOverridesColor(rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDO])
  enMayaDODarkEmerald = 23
  #mayaDO = qtDrawingOverridesColor(rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDO])
  enMayaDOTang = 24
  #mayaDO = qtDrawingOverridesColor(rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDO])
  enMayaDOGold = 25
  #mayaDO = qtDrawingOverridesColor(rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDO])
  enMayaDOGrass = 26
  #mayaDO = qtDrawingOverridesColor(rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDO])
  enMayaDODarkBlueGreen = 27
  #mayaDO = qtDrawingOverridesColor(rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDO])
  enMayaDOBlueGreen = 28
  #mayaDO = qtDrawingOverridesColor(rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDO])
  enMayaDOBlueGray = 29
  #mayaDO = qtDrawingOverridesColor(rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDO])
  enMayaDOPurple = 30
  #mayaDO = qtDrawingOverridesColor(rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDO])
  enMayaDOPink = 31
  #mayaDO = qtDrawingOverridesColor(rgba=qtDrawingOverridesColor.mayaDOColorList[qtDrawingOverridesColor.enMayaDO])

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

  def __init__(self, inFn, rgba=None, colorIndex=None) : 
    if colorIndex is not None : 
      rgba = list(qtDrawingOverridesColor.mayaDOColorList[colorIndex][1])
      rgba.append(255)
    elif rgba is None : rgba = [255, 255, 255, 255]

    if inFn is not None : 
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
