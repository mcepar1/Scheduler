# -*- coding: Cp1250 -*-
"""
This module contains panels, for editing static data.
"""
import wx
import wx.lib.masked
import wx.lib.intctrl
import datetime

from utils import time_conversion

"""
Superclass for the static panels.
"""    
class StaticPanel (wx.Panel):
  
  def __init__ (self, container, *args, **kwargs):
    """
    The default constructor.
      container: a data container object
    """
    wx.Panel.__init__ (self, *args, **kwargs)
    
    self.headers     = self.__pretty_format (container.as_table( )['header'])
    self.attributes  = []
    self.error_label = wx.StaticText(self, wx.ID_ANY)
    self.error_label.SetForegroundColour (wx.RED)
    
    
  def get_attributes (self):
    """
    Return a list of all attributes.
      return: a list, that contains this panel's attribute values.
    """
    raise Exception ('Implement!')
  
  def is_valid (self):
    """
    Checks, if all the input fields have a valid entry. Also sets the error message
      return: true, if it is valid, false otherwise
    """
    raise Exception ('Implement!')
  
  def set_error_msg (self, msg):
    """
    Displays an error message.
    """
    self.error_label.SetLabel (msg)
  
  def _set_attributes (self, attributes):
    """
    Adds the fields to this panel.
    """
    
    self.attributes = attributes
    
    top_sizer       = wx.BoxSizer (wx.VERTICAL)
    panel_sizer     = wx.FlexGridSizer (rows=len(self.headers), cols=2)
    for i, header in enumerate (self.headers):
      panel_sizer.Add (wx.StaticText(self, wx.ID_ANY, header))
      panel_sizer.Add (self.attributes[i], 0, wx.EXPAND)
    
    top_sizer.Add (panel_sizer, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    top_sizer.Add (self.error_label, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    self.SetSizerAndFit (top_sizer)
    
    
  
  def __pretty_format(self, headers):
    """
    Transforms the headers into a nicer format.
    """
    formatted = []
    for header in headers:
      new_header = ''
      for i, c in enumerate (header):
        if i:
          new_header += c.lower ( )
        else:
          new_header += c.upper ( )
      new_header += ':'
      formatted.append(new_header)
    return formatted
        
"""
A panel, that has only text fields.
"""
class TextStaticPanel (StaticPanel):
  def __init__(self, container, *args, **kwargs):
    """
    The default constructor
      container: a data container object
    """
    StaticPanel.__init__(self, container, *args, **kwargs)
    
    for _ in self.headers:
      self.attributes.append (wx.TextCtrl(self, wx.ID_ANY, '', size=(125, -1)))
    self._set_attributes (self.attributes)
    
  def get_attributes (self):
    """
    Return a list of all attributes.
      return: a list, that contains this panel's attribute values.
    """
    atr = []
    for attribute in self.attributes:
      atr.append(attribute.GetValue ( ))
      
    return atr
  
  def is_valid (self):
    """
    Checks, if all the input fields have a valid entry. Also sets the error message
      return: true, if it is valid, false otherwise
    """
    for text in self.get_attributes ( ):
      if not text:
        self.set_error_msg('Vsa tekstovna polja so obvezna.')
        return False
    
    self.set_error_msg('')
    return True

"""
A panel, that mirrors the nurse's static attributes.
"""    
class StaticNursePanel (TextStaticPanel):
  
  def __init__(self, container, *args, **kwargs):
    """
    The default constructor
      container: a data container object
    """
    TextStaticPanel.__init__(self, container, *args, **kwargs)
    
    self.attributes[-1].Destroy ( )
    self.attributes[-1] = wx.GenericDatePickerCtrl(self, wx.ID_ANY, style = wx.DP_DROPDOWN | wx.DP_SHOWCENTURY)
    self._set_attributes(self.attributes)

  def get_attributes(self):
    """
    Return a list of all attributes.
      return: a list, that contains this panel's attribute values.
    """
    attributes = []
    for atr in self.attributes[0:-1]:
      attributes.append (atr.GetValue ( ))
    
    wx_date = self.attributes[-1].GetValue ( )
    attributes.append (datetime.date (day=wx_date.GetDay ( ), month=wx_date.GetMonth ( ) + 1, year=wx_date.GetYear ( )))
    
    return attributes
  
  def is_valid (self):
    """
    Checks, if all the input fields have a valid entry. Also sets the error message
      return: true, if it is valid, false otherwise
    """
    for text in self.get_attributes ( )[0:-1]:
      if not text:
        self.set_error_msg('Vsa tekstovna polja so obvezna.')
        return False
    
    self.set_error_msg('')
    return True
  
"""
A panel, that mirrors the workplaces's static attributes.
""" 
class StaticWorkplacePanel (TextStaticPanel):
  def __init__(self, container, *args, **kwargs):
    """
    The default constructor
      container: a data container object
    """
    TextStaticPanel.__init__(self, container, *args, **kwargs)
    
    self.attributes[-1].Destroy ( )
    self.attributes[-1] = wx.CheckBox (self, wx.ID_ANY)
    self._set_attributes(self.attributes)
    
  def get_attributes(self):
    """
    Return a list of all attributes.
      return: a list, that contains this panel's attribute values.
    """
    attributes = []
    for atr in self.attributes:
      attributes.append (atr.GetValue ( ))
    
    return attributes
  
  def is_valid (self):
    """
    Checks, if all the input fields have a valid entry. Also sets the error message
      return: true, if it is valid, false otherwise
    """
    for text in self.get_attributes ( )[0:-1]:
      if not text:
        self.set_error_msg('Vsa tekstovna polja so obvezna.')
        return False
    
    self.set_error_msg('')
    return True
  
"""
A panel, that mirrors the employment type static attributes.
""" 
class StaticEmploymentTypePanel (StaticPanel):
  def __init__(self, container, *args, **kwargs):
    """
    The default constructor
      container: a data container object
    """
    StaticPanel.__init__(self, container, *args, **kwargs)
    
    self.attributes.append (wx.TextCtrl (self, wx.ID_ANY))
    self.attributes.append (wx.lib.intctrl.IntCtrl (self, wx.ID_ANY, min=0, limited=True, allow_none=False))
    self.attributes.append (wx.CheckBox (self, wx.ID_ANY))
    
    self._set_attributes(self.attributes)
    
  def get_attributes(self):
    """
    Return a list of all attributes.
      return: a list, that contains this panel's attribute values.
    """
    attributes = []
    for atr in self.attributes:
      attributes.append (atr.GetValue ( ))
    
    return attributes
  
  def is_valid (self):
    """
    Checks, if all the input fields have a valid entry. Also sets the error message
      return: true, if it is valid, false otherwise
    """
    if not self.get_attributes ( )[0]:
      self.set_error_msg('Vsa tekstovna polja so obvezna.')
      return False
    
    self.set_error_msg('')
    return True

"""
A panel, that mirrors the turnus static attributes.
"""   
class StaticTurnusPanel (StaticPanel):
  def __init__(self, container, *args, **kwargs):
    """
    The default constructor
      container: a data container object
    """
    StaticPanel.__init__(self, container, *args, **kwargs)
     
    self.attributes.append (wx.TextCtrl (self, wx.ID_ANY))
    self.attributes.append (wx.TextCtrl (self, wx.ID_ANY))
    self.attributes.append (wx.lib.masked.TimeCtrl (self, wx.ID_ANY, format='24HHMM'))
    self.attributes.append (wx.lib.masked.TimeCtrl (self, wx.ID_ANY, format='24HHMM'))
    self.attributes.append (wx.lib.masked.TimeCtrl (self, wx.ID_ANY, format='24HHMM'))
    self.attributes.append (wx.lib.masked.TimeCtrl (self, wx.ID_ANY, format='24HHMM'))
    self.attributes.append (wx.CheckBox (self, wx.ID_ANY))
    self.attributes.append (wx.CheckBox (self, wx.ID_ANY))
    
    self._set_attributes(self.attributes)
    
  def get_attributes(self):
    """
    Return a list of all attributes.
      return: a list, that contains this panel's attribute values.
    """
    attributes = []
    for atr in self.attributes[0:2]:
      attributes.append (atr.GetValue ( ))
    
    for atr in self.attributes[2:4]:
      attributes.append (time_conversion.string_to_time(atr.GetValue ( )))
    for atr in self.attributes[4:-2]:
      attributes.append (time_conversion.time_to_timedelta (time_conversion.string_to_time (atr.GetValue ( ))))
    
    attributes.append (self.attributes[-2].GetValue ( ))
    attributes.append (self.attributes[-1].GetValue ( ))  
    
    return attributes
  
  def is_valid (self):
    """
    Checks, if all the input fields have a valid entry. Also sets the error message
      return: true, if it is valid, false otherwise
    """
    for text in self.get_attributes ( )[0:2]:
      if not text:
        self.set_error_msg('Vsa tekstovna polja so obvezna.')
        return False
    
    self.set_error_msg('')
    return True
  
"""
A panel, that mirrors the vacation's static attributes.
"""   
class StaticVacationPanel (StaticPanel):
  def __init__(self, container, *args, **kwargs):
    """
    The default constructor
      container: a data container object
    """
    StaticPanel.__init__(self, container, *args, **kwargs)
     
    self.attributes.append (wx.TextCtrl (self, wx.ID_ANY))
    self.attributes.append (wx.TextCtrl (self, wx.ID_ANY))
    self.attributes.append (wx.lib.masked.TimeCtrl (self, wx.ID_ANY, format='24HHMM'))
    
    self._set_attributes (self.attributes)
    
  def get_attributes(self):
    """
    Return a list of all attributes.
      return: a list, that contains this panel's attribute values.
    """
    attributes = []
    for atr in self.attributes[0:2]:
      attributes.append (atr.GetValue ( ))
    
    attributes.append (time_conversion.time_to_timedelta (time_conversion.string_to_time (self.attributes[-1].GetValue ( ))))
    
    return attributes
  
  def is_valid (self):
    """
    Checks, if all the input fields have a valid entry. Also sets the error message
      return: true, if it is valid, false otherwise
    """
    for text in self.get_attributes ( )[0:2]:
      if not text:
        self.set_error_msg('Vsa tekstovna polja so obvezna.')
        return False
    
    self.set_error_msg('')
    return True
