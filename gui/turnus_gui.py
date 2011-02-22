# -*- coding: Cp1250 -*-

import wx
import wx.grid
import wx_extensions

from global_vars import turnuses, turnus_types, nurses

class TurnusPanel(wx.Panel):
  def __init__(self, parent):
    wx.Panel.__init__(self, parent)
    
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    
    self.grid = wx.grid.Grid(self, -1)
    self.fill_grid()
    sizer.Add(self.grid, 1, wx.ALIGN_LEFT)
    
    self.types = TurnusTypePanel(self)
    sizer.Add(self.types, 0, wx.ALIGN_LEFT | wx.LEFT, 4)
    
    self.SetSizerAndFit(sizer)
    
    # add event listeners
    self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.turnus_selected, self.grid)
    
  def fill_grid(self):
      
    table = turnuses.as_table()
    headers = table['header']
    rows = table['items']
    
    self.grid.CreateGrid(len(rows), len(headers))
      
    for i in range(len(headers)):
      self.grid.SetColLabelValue(i, headers[i])
      
    for i in range(len(rows)):
      for j in range(len(rows[i])):
        self.grid.SetCellValue(i, j, rows[i][j])
        
    self.grid.AutoSize()
    
  def turnus_selected(self, event):
    if event.GetCol() == -1:
      if event.GetRow() < 0:
        self.types.set_turnus(None)
        self.grid.ClearSelection()
      else:
        self.grid.SelectRow(event.GetRow())
        self.types.set_turnus(turnuses.get_element(event.GetRow()))
    
    
class TurnusTypePanel(wx.Panel):
  """This class represents the turnus types."""
  
  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.turnus = None
    
    topSizer = wx.BoxSizer(wx.HORIZONTAL)
    
    turnusSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), "Vrste turnusov"), wx.VERTICAL)
    
    #set the turnus types
    self.turnus_types = []
    for turnus_type in turnus_types.get_all ( ):
      self.turnus_types.append(wx_extensions.LinkedCheckBox(turnus_type, self, wx.NewId(), str(turnus_type)))
      self.Bind(wx.EVT_CHECKBOX, self.__turnus_type_edited, self.turnus_types[-1])
      turnusSizer.Add(self.turnus_types[-1], 0, wx.ALIGN_LEFT)
    

    #set the initial turnus types  
    self.__set_permissions ()
    
    topSizer.Add(turnusSizer, 0, wx.ALIGN_RIGHT)
    
    self.SetSizerAndFit(topSizer)
    
  def set_turnus (self, turnus):
    self.turnus = turnus
    self.__set_permissions ()
    
  def __turnus_type_edited (self, event):
    
    if event.IsChecked():
      # remove the turnus from restrictions
      self.turnus.add_type(event.GetEventObject().element)
    else:
      # add the restriction
      self.turnus.remove_type(event.GetEventObject().element)
         
    #update every single person - needed for synchronization
    for nurse in nurses.get_all ( ):
      if self.turnus in nurse.allowed_turnuses:
        nurse.remove_allowed_turnus(self.turnus)
        nurse.add_allowed_turnus(self.turnus)
      
        
    
    
  def __set_permissions (self):
    """Checks and unchecks the checker according to the current state."""
    
    if self.turnus:
      for type in self.turnus_types:
        type.Enable ()
        if type.element in self.turnus.types:
          type.SetValue (True)
        else:
          type.SetValue (False)
    else:
      for type in self.turnus_types:
        type.Disable ()
        
        
