# -*- coding: utf-8 -*-

import wx
import wx.grid

class Result(wx.Frame):
  def __init__(self, scheduler, *args, **kwargs):
    wx.Frame.__init__(self, *args, **kwargs)
    
    self.scheduler = scheduler
    
    sizer = wx.BoxSizer(wx.VERTICAL)
    self.grid = wx.grid.Grid(self, wx.NewId())
    self.fill_grid()
    
    sizer.Add(self.grid,1,wx.CENTER | wx.EXPAND)
    
    self.SetSizerAndFit(sizer)
    
  def fill_grid(self):
    table = self.scheduler.get_schedule_matrix()
    headers = table[0]
    rows = table[1:]
    
    self.grid.CreateGrid(len(rows),len(headers))
      
    for i in range(len(headers)):
      self.grid.SetColLabelValue(i, headers[i])
      
    for i in range(len(rows)):
      for j in range(len(rows[i])):
        self.grid.SetCellValue(i, j, rows[i][j])
        
    self.grid.AutoSize()