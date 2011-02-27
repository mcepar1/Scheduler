# -*- coding: Cp1250 -*-
import wx

import os
LOG = os.path.join("persistence", "log", "log.txt")
def reset_log ():
  file = open(LOG, 'w')
  file.write('START\n')
  file.flush()
  file.close()
  
def set_encoding ():
  import sys
  reload (sys)
  sys.setdefaultencoding('Cp1250')
  
reset_log()
set_encoding()

import locale
locale.setlocale(locale.LC_ALL, '')

import gui
app = wx.App(redirect=False)
gui.start ( )
app.MainLoop ( )
