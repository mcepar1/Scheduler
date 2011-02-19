# -*- coding: Cp1250 -*-

import wx
from global_vars import employment_types

class EmploymentTypePanel(wx.Panel):
  
  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    sizer = wx.BoxSizer(wx.VERTICAL)
    
    self.grid = wx.grid.Grid(self, -1)
    self.fill_grid()
    
    sizer.Add(self.grid,1,wx.ALIGN_LEFT)
    
    self.SetSizerAndFit(sizer)
    
  def fill_grid(self):
    table = employment_types.as_table()
    headers = table['header']
    rows = table['items']
    
    self.grid.CreateGrid(len(rows),len(headers))
      
    for i in range(len(headers)):
      self.grid.SetColLabelValue(i, headers[i])
      
    for i in range(len(rows)):
      for j in range(len(rows[i])):
        self.grid.SetCellValue(i, j, rows[i][j])
        
    self.grid.AutoSize()
