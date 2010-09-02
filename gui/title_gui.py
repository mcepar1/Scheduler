# -*- coding: utf-8 -*-

import wx
import wx.grid

from global_vars import titles


class TitlePanel(wx.Panel):
  def __init__(self,parent):
    wx.Panel.__init__(self, parent)
    
    sizer = wx.BoxSizer(wx.VERTICAL)
    
    grid = wx.grid.Grid(self, -1)
    self.fill_grid(grid)
    
    sizer.Add(grid,1,wx.ALIGN_LEFT)
    
    self.SetSizerAndFit(sizer)
    
  def fill_grid(self, grid):
      
    table = titles.as_table()
    headers = table['header']
    rows = table['items']
    
    grid.CreateGrid(len(rows),len(headers))
      
    for i in range(len(headers)):
      grid.SetColLabelValue(i, headers[i])
      
    for i in range(len(rows)):
      for j in range(len(rows[i])):
        grid.SetCellValue(i, j, rows[i][j])
        
    grid.AutoSize()
    
