# -*- coding: Cp1250 -*-

"""
This file contains various methods, that are used throughout the GUI.
"""

import wx

def make_icon(img):
  """
  The various platforms have different requirements for the
  icon size...
  """
  if "wxMSW" in wx.PlatformInfo:
    img = img.Scale(16, 16)
  elif "wxGTK" in wx.PlatformInfo:
    img = img.Scale(22, 22)
  # wxMac can be any size upto 128x128, so leave the source img alone....
  icon = wx.IconFromBitmap(img.ConvertToBitmap() )
  return icon
