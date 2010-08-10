# -*- coding: utf-8 -*-

import wx
import wx_extensions
from global_vars import workplaces, turnuses

class WorkplacePanel(wx.Panel):
  
  def __init__(self,parent):
    wx.Panel.__init__(self, parent)
    
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    
    self.grid = wx.grid.Grid(self, wx.NewId())
    self.fill_grid()
    
    sizer.Add(self.grid,1,wx.CENTER | wx.EXPAND)
    
    self.person = TurnusPanel(self)
    sizer.Add(self.person,0,wx.ALIGN_LEFT | wx.LEFT, 4)
    
    self.SetSizerAndFit(sizer)
    
    # add event listeners
    self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.workplace_selected, self.grid)
    
  def fill_grid(self):
    table = workplaces.as_table()
    headers = table['header']
    rows = table['items']
    
    self.grid.CreateGrid(len(rows),len(headers))
      
    for i in range(len(headers)):
      self.grid.SetColLabelValue(i, headers[i])
      
    for i in range(len(rows)):
      for j in range(len(rows[i])):
        self.grid.SetCellValue(i, j, rows[i][j])
        
    self.grid.AutoSize()
    
  def workplace_selected(self, event):
    if event.GetCol()==-1:
      if event.GetRow() < 0:
        self.person.set_workplace(None)
        self.grid.ClearSelection()
      else:
        self.grid.SelectRow(event.GetRow())
        self.person.set_workplace(workplaces.get_element(event.GetRow()))

        
class TurnusPanel(wx.Panel):
  """This class represents the turnuses."""
  
  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.workplace = None
    
    topSizer = wx.BoxSizer(wx.HORIZONTAL)
    
    turnusSizer = wx.StaticBoxSizer(wx.StaticBox(self,wx.NewId(),"Turnusi"),wx.VERTICAL)
    
    #set the turnuses
    self.turnuses = []
    for turnus in turnuses.turnuses:
      self.turnuses.append(wx_extensions.LinkedCheckBox(turnus,self,wx.NewId(),str(turnus)))
      self.Bind(wx.EVT_CHECKBOX, self.__turnus_edited, self.turnuses[-1])
      turnusSizer.Add(self.turnuses[-1],0,wx.ALIGN_LEFT)
    

    #set the initial turnuses  
    self.__set_permissions ( )
    
    topSizer.Add(turnusSizer,0,wx.ALIGN_RIGHT)
    
    self.SetSizerAndFit(topSizer)
    
  def set_workplace (self, workplace):
    self.workplace = workplace
    self.__set_permissions ( )
    
  def __turnus_edited (self, event):
    
    if event.IsChecked():
      # remove the turnus from restrictions
      self.workplace.remove_invalid_turnus(event.GetEventObject().element)
    else:
      # add the restriction
      self.workplace.add_invalid_turnus(event.GetEventObject().element)
    
  def __set_permissions (self):
    """Checks and unchecks the checker according ti the current state."""
    
    if self.workplace:
      for turnus in self.turnuses:
        turnus.Enable ( )
        if turnus.element in self.workplace.forbidden_turnuses:
          turnus.SetValue (False)
        else:
          turnus.SetValue (True)
    else:
      for turnus in self.turnuses:
        turnus.Disable ( )
        
        
      
