# -*- coding: utf-8 -*-

import wx
import wx_extensions

class SchedulerPanel(wx.Panel):
  def __init__(self,*args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    main_sizer = wx.BoxSizer(wx.VERTICAL)
    
    self.month_picker = wx_extensions.MonthChoice(self,wx.NewId())
    main_sizer.Add(self.month_picker,0,wx.ALIGN_TOP|wx.ALIGN_LEFT)
    
    self.shift_control = ShiftControl(self,wx.NewId())
    
    main_sizer.Add(self.shift_control,0,wx.ALIGN_TOP|wx.ALIGN_LEFT)
    
    self.SetSizerAndFit(main_sizer)
    
class ShiftControl(wx.Panel):
  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    shift_sizer = wx.StaticBoxSizer(wx.StaticBox(self,wx.NewId(),"Stevilo zaposlenih v izmeni"),wx.VERTICAL)
    
    
    sub_sizer = wx.GridSizer(rows = 0, cols = 2)
    sub_sizer.Add(wx.StaticText(self,wx.NewId(),"Dopoldanski turnus: "), 0, wx.ALIGN_LEFT)
    self.morning = wx.SpinCtrl(self, wx.NewId(),style = wx.SP_VERTICAL)
    self.morning.SetRange(1, 100)
    self.morning.SetValue(1)
    sub_sizer.Add(self.morning,0,wx.ALIGN_TOP|wx.ALIGN_LEFT)
    
    
    sub_sizer.Add(wx.StaticText(self,wx.NewId(),"Popoldanski turnus: "), 0, wx.ALIGN_LEFT)
    self.afternoon = wx.SpinCtrl(self, wx.NewId(),style = wx.SP_VERTICAL)
    self.afternoon.SetRange(1, 100)
    self.afternoon.SetValue(1)
    sub_sizer.Add(self.afternoon,0,wx.ALIGN_TOP|wx.ALIGN_LEFT)
    
    sub_sizer.Add(wx.StaticText(self,wx.NewId(),"Nocni turnus: "), 0, wx.ALIGN_LEFT)
    self.night = wx.SpinCtrl(self, wx.NewId(),style = wx.SP_VERTICAL)
    self.night.SetRange(1, 100)
    self.night.SetValue(1)
    sub_sizer.Add(self.night,0,wx.ALIGN_TOP|wx.ALIGN_LEFT)
    
    shift_sizer.Add(sub_sizer,0,wx.ALIGN_TOP|wx.ALIGN_LEFT)
    
    self.SetSizerAndFit(shift_sizer)
    
