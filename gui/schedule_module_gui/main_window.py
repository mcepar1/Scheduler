# -*- coding: Cp1250 -*-

import wx

import os


from gui import custom_events, wx_extensions
from gui.utils_gui import make_icon
from scheduler_gui import SchedulerPanel


"""
This class represents the Main window for the entire scheduling process.
"""
class MainWindow(wx.Frame):

  TITLE     = 'Razpored'
  PARENT    = None
  ICON_PATH = os.path.join ('persistence', 'gui', 'clock.png')

  def __init__(self, proxy, parent):
    wx.Frame.__init__(self, parent, title = MainWindow.TITLE + ': ' + str (proxy), style = wx.DEFAULT_FRAME_STYLE)
    
    self.generated_results = 0
    
    
    self.notebook = wx_extensions.EnhancedAUINotebook (self, wx.ID_ANY)
    self.notebook.AddPage(SchedulerPanel(proxy, self.notebook, wx.ID_NEW), "Turnusi")
    
    self.Bind(custom_events.EVT_TB_START, self.__start, id=wx.ID_NEW)
    
    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(self.notebook, 1, wx.ALIGN_LEFT | wx.EXPAND)
    
    self.SetSizerAndFit (sizer)
    self.SetIcon(make_icon(wx.Image(name = MainWindow.ICON_PATH)))
    
    
  def __start (self, event):
    #TODO: rewrite the whole procedure.
    self.generated_results += 1
    import result_gui_new
    page = result_gui_new.Result(event.proxy, self.notebook, wx.NewId())
    self.notebook.AddPage(page, 'Razpored ' + str (self.generated_results), True)
    page.start ( )
    
