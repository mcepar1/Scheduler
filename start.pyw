from gui import gui

import wx

import os
import locale

LOG = os.path.join("persistence", "log", "log.txt")
def reset_log ():
  file = open(LOG, 'w')
  file.write('START\n')
  file.flush()
  file.close()
  
reset_log()

locale.setlocale(locale.LC_ALL,"")

app = wx.App(redirect=True, filename=LOG)
window = gui.MainWindow()
app.MainLoop()
