# -*- coding: Cp1250 -*-

import wx
import os

from gui.main_window import make_icon
from scheduler_gui import SchedulerPanel

"""
This class represents the Main window for the entire scheduling process.
"""
class MainWindow(wx.Frame):

  TITLE     = 'Razvrščanje'
  PARENT    = None
  ICON_PATH = os.path.join ('persistence', 'gui', 'clock.png')

  def __init__(self, workplaces, roles, turnus_types, parent):
    wx.Frame.__init__(self, parent, title = MainWindow.TITLE, style = wx.DEFAULT_FRAME_STYLE)
    
    self.sizer = wx.BoxSizer(wx.VERTICAL)
    
    notebook = wx.Notebook(self)
    notebook.AddPage(SchedulerPanel(workplaces, roles, turnus_types, notebook), "Urnik")
    
    self.sizer.Add(notebook,1,wx.ALIGN_LEFT | wx.EXPAND)
    
    self.SetSizer(self.sizer)
    self.SetAutoLayout(1)
    self.sizer.Fit(self)
    self.SetIcon(make_icon(wx.Image(name = MainWindow.ICON_PATH)))
