# -*- coding: Cp1250 -*-

import wx
import wx_extensions
from Scheduler.global_vars import workplaces, turnuses, roles
from Scheduler.gui.common import GenericTablePanel

class WorkplacePanel(GenericTablePanel):
  
  def __init__(self, parent):
    GenericTablePanel.__init__(self, workplaces, parent, edit_panel=EditWorkplacePanel)
        
class EditWorkplacePanel(wx.Panel):
  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    sizer = wx.BoxSizer(wx.VERTICAL)
    
    self.turnuses = TurnusPanel (self, wx.NewId())
    self.roles    = RolePanel   (self, wx.NewId())
    
    sizer.Add(self.turnuses, 0, wx.ALIGN_LEFT | wx.ALIGN_TOP | wx.EXPAND)
    sizer.Add(self.roles,    0, wx.ALIGN_LEFT | wx.ALIGN_TOP | wx.EXPAND)
    
    self.SetSizerAndFit (sizer)
    self.set_unit(None)
    
  def set_unit (self, workplace):
    self.turnuses.set_unit(workplace)
    self.roles.set_unit(workplace)

        
class TurnusPanel(wx.Panel):
  """This class represents the turnuses."""
  
  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.workplace = None
    
    
    sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), "Turnusi"), wx.VERTICAL)
    
    #set the turnuses
    self.turnuses = []
    for turnus in turnuses.get_all ( ):
      self.turnuses.append(wx_extensions.LinkedCheckBox(turnus, self, wx.NewId(), str(turnus)))
      self.Bind(wx.EVT_CHECKBOX, self.__turnus_edited, self.turnuses[-1])
      sizer.Add(self.turnuses[-1], 1, wx.ALIGN_LEFT | wx.ALIGN_TOP | wx.EXPAND)
    

    #set the initial turnuses  
    self.__set_permissions ()
    
    #topSizer.Add(turnusSizer, 0, wx.ALIGN_RIGHT)
    
    self.SetSizerAndFit(sizer)
    
  def set_unit (self, workplace):
    self.workplace = workplace
    self.__set_permissions ()
    
  def __turnus_edited (self, event):
    
    if event.IsChecked():
      # remove the turnus from restrictions
      self.workplace.add_allowed_turnus(event.GetEventObject().element)
    else:
      # add the restriction
      self.workplace.remove_allowed_turnus(event.GetEventObject().element)
      
          
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
        turnus.SetValue (False)
        turnus.Disable ( )
        
class RolePanel(wx.Panel):
  
  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.workplace = None
    
    sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), "Vloge"), wx.VERTICAL)
    
    #set the roles
    self.roles = []
    for role in roles.get_all ( ):
      self.roles.append(wx_extensions.LinkedCheckBox(role, self, wx.NewId(), str(role)))
      self.Bind(wx.EVT_CHECKBOX, self.__role_edited, self.roles[-1])
      sizer.Add(self.roles[-1], 0, wx.ALIGN_LEFT | wx.ALIGN_TOP | wx.EXPAND)
    

    #set the initial roles
    self.__set_permissions ()
    
    self.SetSizerAndFit(sizer)
    
  def set_unit (self, workplace):
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
        role.SetValue (False)
        role.Disable ( )
      
