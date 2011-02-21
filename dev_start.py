from gui import gui

import wx

import os

LOG = os.path.join("persistence", "log", "log.txt")
def reset_log ():
  file = open(LOG, 'w')
  file.write('START\n')
  file.flush()
  file.close()
  
reset_log()
app = wx.App(redirect=False)
window = gui.MainWindow()
app.MainLoop()
