import wx

import os
LOG = os.path.join("persistence", "log", "log.txt")
def reset_log ():
  file = open(LOG, 'w')
  file.write('START\n')
  file.flush()
  file.close()
  
def set_path ():
  #Append the root to the path
  import sys
  sys.path.append ('..')
  
reset_log()
set_path ()

import locale
locale.setlocale(locale.LC_ALL,"")

from gui import gui

app = wx.App(redirect=True, filename=LOG)
window = gui.MainWindow()
app.MainLoop()
