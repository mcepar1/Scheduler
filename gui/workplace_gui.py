# -*- coding: Cp1250 -*-

import wx
import wx_extensions
from global_vars import workplaces, turnuses, roles, nurses

class WorkplacePanel(wx.Panel):
  
  def __init__(self, parent):
    wx.Panel.__init__(self, parent)
    
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    
    self.grid = wx.grid.Grid(self, wx.NewId())
    self.fill_grid()
    
    panelSizer = wx.BoxSizer(wx.VERTICAL)
    
    sizer.Add(self.grid, 1, wx.CENTER | wx.EXPAND)
    
    self.turnuses = TurnusPanel(self)
    panelSizer.Add(self.turnuses, 0, wx.ALIGN_LEFT | wx.LEFT, 4)
    
    self.roles = RolePanel(self)
    panelSizer.Add(self.roles, 0, wx.ALIGN_LEFT | wx.LEFT, 4)
    
    sizer.Add(panelSizer, 0, wx.ALIGN_LEFT)
    
    self.SetSizerAndFit(sizer)
    
    # add event listeners
    self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.workplace_selected, self.grid)
    
  def fill_grid(self):
    table = workplaces.as_table()
    headers = table['header']
    rows = table['items']
    
    self.grid.CreateGrid(len(rows), len(headers))
      
    for i in range(len(headers)):
      self.grid.SetColLabelValue(i, headers[i])
      
    for i in range(len(rows)):
      for j in range(len(rows[i])):
        self.grid.SetCellValue(i, j, rows[i][j])
        
    self.grid.AutoSize()
    
  def workplace_selected(self, event):
    if event.GetCol() == -1:
      if event.GetRow() < 0:
        self.turnuses.set_workplace(None)
        self.roles.set_workplace(None)
        self.grid.ClearSelection()
      else:
        self.grid.SelectRow(event.GetRow())
        self.turnuses.set_workplace(workplaces.get_element(event.GetRow()))
        self.roles.set_workplace(workplaces.get_element(event.GetRow()))

        
class TurnusPanel(wx.Panel):
  """This class represents the turnuses."""
  
  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.workplace = None
    
    topSizer = wx.BoxSizer(wx.HORIZONTAL)
    
    turnusSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), "Turnusi"), wx.VERTICAL)
    
    #set the turnuses
    self.turnuses = []
    for turnus in turnuses.turnuses:
      self.turnuses.append(wx_extensions.LinkedCheckBox(turnus, self, wx.NewId(), str(turnus)))
      self.Bind(wx.EVT_CHECKBOX, self.__turnus_edited, self.turnuses[-1])
      turnusSizer.Add(self.turnuses[-1], 0, wx.ALIGN_LEFT)
    

    #set the initial turnuses  
    self.__set_permissions ()
    
    topSizer.Add(turnusSizer, 0, wx.ALIGN_RIGHT)
    
    self.SetSizerAndFit(topSizer)
    
  def set_workplace (self, workplace):
    self.workplace = workplace
    self.__set_permissions ()
    
  def __turnus_edited (self, event):
    
    if event.IsChecked():
      # remove the turnus from restrictions
      self.workplace.add_allowed_turnus(event.GetEventObject().element)
    else:
      # add the restriction
      self.workplace.remove_allowed_turnus(event.GetEventObject().element)
         
    #update every single person - needed for synchronization
    for nurse in nurses.nurses:
      if self.workplace in nurse.workplaces:
        nurse.remove_workplace(self.workplace)
        nurse.add_workplace(self.workplace)
      
        
    
    
  def __set_permissions (self):
    """Checks and unchecks the checker according to the current state."""
    
    if self.workplace:
      for turnus in self.turnuses:
        turnus.Enable ()
        if turnus.element in self.workplace.allowed_turnuses:
          turnus.SetValue (True)
        else:
          turnus.SetValue (False)
    else:
      for turnus in self.turnuses:
        turnus.Disable ()
        
class RolePanel(wx.Panel):
  
  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.workplace = None
        
    topSizer = wx.BoxSizer(wx.HORIZONTAL)
    
    roleSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), "Vloge"), wx.VERTICAL)
    
    #set the roles
    self.roles = []
    for role in roles.roles:
      self.roles.append(wx_extensions.LinkedCheckBox(role, self, wx.NewId(), str(role)))
      self.Bind(wx.EVT_CHECKBOX, self.__role_edited, self.roles[-1])
      roleSizer.Add(self.roles[-1], 0, wx.ALIGN_LEFT)
    

    #set the initial roles
    self.__set_permissions ()
    
    topSizer.Add(roleSizer, 0, wx.ALIGN_RIGHT)
    
    self.SetSizerAndFit(topSizer)
    
  def set_workplace (self, workplace):
    self.workplace = workplace
    self.__set_permissions ()
    
  def __role_edited (self, event):
    
    if event.IsChecked():
      # add a role
      self.workplace.add_role(event.GetEventObject().element)
    else:
      # remove a role
      self.workplace.remove_role(event.GetEventObject().element)
      
  def __set_permissions (self):
    """Checks and unchecks the checker according to the current state."""
    
    if self.workplace:
      for role in self.roles:
        role.Enable ()
        if role.element in self.workplace.roles:
          role.SetValue (True)
        else:
          role.SetValue (False)
    else:
      for role in self.roles:
        role.Disable ()
      
