# -*- coding: Cp1250 -*-

import wx
import wx_extensions

import global_vars
        
class TurnusTypePanel(wx.Panel):
  """This class represents the turnus types."""
  
  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.turnus = None
    
    sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), "Vrste turnusov"), wx.VERTICAL)
    
    #set the turnus types
    self.turnus_types = []
    for turnus_type in global_vars.get_turnus_types ( ).get_all ( ):
      self.turnus_types.append(wx_extensions.LinkedCheckBox(turnus_type, self, wx.NewId(), str(turnus_type)))
      self.Bind(wx.EVT_CHECKBOX, self.__turnus_type_edited, self.turnus_types[-1])
      sizer.Add(self.turnus_types[-1], 0, wx.ALIGN_LEFT | wx.ALIGN_TOP | wx.EXPAND)
    

    #set the initial turnus types  
    self.__set_permissions ()
    
    
    self.SetSizerAndFit(sizer)
    
  def set_unit (self, turnus):
    self.turnus = turnus
    self.__set_permissions ()
    
  def __turnus_type_edited (self, event):
    
    if event.IsChecked():
      # remove the turnus from restrictions
      self.turnus.add_type(event.GetEventObject().element)
    else:
      # add the restriction
      self.turnus.remove_type(event.GetEventObject().element)
      
        
    
    
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
        
        
