# -*- coding: Cp1250 -*-

import wx

class SchedulerPanel(wx.Panel):
  def __init__(self, workplaces, roles, turnus_types, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.workplaces   = workplaces
    self.roles        = roles
    self.turnus_types = turnus_types
    
    button = wx.Button(self, wx.ID_APPLY, 'Prikaži')
    self.Bind(wx.EVT_BUTTON, self.__show, button)
    
  def __show (self, event):
    from schedule import main_window
    
    f = main_window.MainWindow  (self.workplaces, self.roles, self.turnus_types, self)
    f.Show ( )