# -*- coding: Cp1250 -*-

import wx
import wx.grid
from person_gui import PersonPanel
from Scheduler.global_vars import nurses

class NursePanel(wx.Panel):
  
  def __init__(self,parent):
    wx.Panel.__init__(self, parent)
    
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    
    self.grid = wx.grid.Grid(self, wx.NewId())
    self.fill_grid()
    
    sizer.Add(self.grid,1,wx.CENTER | wx.EXPAND)
    
    self.person = PersonPanel(self)
    sizer.Add(self.person,0,wx.ALIGN_LEFT | wx.LEFT, 4)
    
    self.SetSizerAndFit(sizer)
    
    # add event listeners
    self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.nurse_selected, self.grid)
    
  def fill_grid(self):
    table = nurses.as_table()
    headers = table['header']
    rows = table['items']
    
    self.grid.CreateGrid(len(rows),len(headers))
      
    for i in range(len(headers)):
      self.grid.SetColLabelValue(i, headers[i])
      
    for i in range(len(rows)):
      for j in range(len(rows[i])):
        self.grid.SetCellValue(i, j, rows[i][j])
        
    self.grid.AutoSize()
    
  def nurse_selected(self, event):
    if event.GetCol()==-1:
      if event.GetRow() < 0:
        self.person.set_person(None)
        self.grid.ClearSelection()
      else:
        self.grid.SelectRow(event.GetRow())
        self.person.set_person(nurses.get_element(event.GetRow()))
        
      
