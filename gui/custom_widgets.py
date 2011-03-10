# -*- coding: Cp1250 -*-

"""
This file contains reusable widgets, that have no implementation in the wx framework. 
"""
import wx
import custom_events
from gui import wx_extensions, utils_gui

"""
This class is used to select the workplace - role pair.
"""    
class ScheduleUnitSelector(wx.Panel):
  def __init__ (self, scheduling_units, *args, **kwargs):
    """
    The default constructor.
      @param scheduling_units: a data container instance
    """
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.scheduling_units   = scheduling_units
    
    self.workplace_selector = CustomRadioBox (self.scheduling_units.get_workplaces ( ), self, wx.ID_ANY, name='Delovišča', selectable=self.scheduling_units.get_workplaces ( ))
    self.role_selector      = CustomRadioBox (self.scheduling_units.get_roles ( ),      self, wx.ID_ANY, name='Vloge')
    
    self.Bind(custom_events.EVT_UPDATED, self.__synchronize_workplace, self.workplace_selector)
    self.Bind(custom_events.EVT_UPDATED, self.__synchronize_role,      self.role_selector)
    
    
    if utils_gui.has_name (self):
      sizer = wx.StaticBoxSizer (wx.StaticBox (self, wx.ID_ANY, self.GetLabel ( )), wx.HORIZONTAL)
    else:  
      sizer = wx.BoxSizer (wx.HORIZONTAL)
    sizer.Add (self.workplace_selector, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    sizer.Add (self.role_selector,      0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    self.SetSizerAndFit (sizer)
    
    
  def __synchronize_workplace (self, event):
    """
    Keeps the role elements in sync with the selected workplace and continues the event propagation.
    """
    workplace = self.workplace_selector.get_selected ( )
    self.role_selector.set_selectable (self.scheduling_units.get_roles (workplace))
      
    wx.PostEvent (self.GetEventHandler ( ), custom_events.UpdateEvent (self.GetId ( )))
    
  def __synchronize_role (self, event):
    """
    Propagates the event.
    """
    wx.PostEvent (self.GetEventHandler ( ), custom_events.UpdateEvent (self.GetId ( )))
    
  def get_selection (self):
    """
    Returns the selected scheduling unit.
      @return: a a data object
    """
    workplace = self.workplace_selector.get_selected ( )
    role      = self.role_selector.get_selected ( )
    
    return self.scheduling_units.get_scheduling_unit (workplace, role)

"""
This class behaves the same way as normal wxRadioBox.
It handles the data objects internally.    
"""
class CustomRadioBox (wx.Panel):
  
  def __init__ (self, elements, *args, **kwargs):
    """
    The default constructor.
      elements: a list of elements, that will be displayed by this widget
      selectable: a list, that contains all elements, that can be selected. Default value is an empty list.
    """
    
    self.elements      = elements
    self.radio_buttons = []
    
    selectable = []
    if 'selectable' in kwargs:
      selectable = kwargs['selectable']
      del kwargs['selectable']
    
    wx.Panel.__init__(self, *args, **kwargs)
    
    
    for element in self.elements:      
      button = wx.RadioButton (self, wx.NewId ( ), str (element))
      self.radio_buttons.append (button)
    
    
    for radio in self.radio_buttons:
      self.Bind(wx.EVT_RADIOBUTTON, self.__selected, radio)
      
    if utils_gui.has_name (self):
      sizer = wx.StaticBoxSizer (wx.StaticBox(self, wx.ID_ANY, self.GetLabel ( )), wx.VERTICAL)
    else:
      sizer = wx.BoxSizer (wx.VERTICAL)
    for radio in self.radio_buttons:
      sizer.Add (radio, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
      
    self.SetSizerAndFit (sizer)
    self.set_selectable (selectable, False)
    
  def set_selectable (self, elements, select_first=True):
    """
    Set the elements, that can be selected and selects the first. Fires the appropriate event. If the 
    list contains unknown elements, nothing gets deleted or updated.
      @param elements: a list, that contains elements, that are allowed to be selected
      @param select_first: if true, the first element will be selected, no element will be selected otherwise
    """
    for i, element in enumerate (self.elements):
      if element in elements:
        self.radio_buttons[i].Enable ( )
      else:
        self.radio_buttons[i].SetValue (False)
        self.radio_buttons[i].Disable ( )
        
    #select the first possible radio
    if select_first:
      for radio_button in self.radio_buttons:
        if radio_button.IsEnabled ( ):
          radio_button.SetValue (True)
          self.__selected (None)
          break
    
    
  def get_selected (self):
    """
    Return the selected element.
      return: the selected element object or None, if there is no selection.
    """
    for i, radio in enumerate (self.radio_buttons):
      if radio.GetValue ( ):
        return self.elements[i]
    return None
  
  def __selected(self, event):
    """
    Event listener for the radio buttons. Fires an update event.
    """
    wx.PostEvent (self.GetEventHandler ( ), custom_events.UpdateEvent (self.GetId ( )))
    

"""
This widget is used for selecting dates, when the day is not important.
"""    
class MonthYearSelector (wx.Panel):
  
  def __init__ (self, *args, **kwargs):
    """
    The default constructor.
    """
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.months = wx_extensions.MonthChoice (self, wx.ID_ANY)
    self.years  = wx.Choice (self, wx.ID_ANY)
    
    year = self.months.get_value ( ).year
    self.years.SetItems ([str (year - 1), str (year), str (year + 1)])
    self.years.Select (1)
    
      
    if utils_gui.has_name (self):
      sizer = wx.StaticBoxSizer (wx.StaticBox (self, wx.ID_ANY, self.GetLabel ( )), wx.HORIZONTAL)
    else:
      sizer = wx.BoxSizer (wx.HORIZONTAL)
    sizer.Add (self.months, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
    sizer.Add (self.years,  0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT)
    
    self.SetSizerAndFit (sizer)
    
  def get_selected_date (self):
    """
    Returns a datetime.date object, that represents the selected combination.
      @return: a datetime.date object
    """
    return self.months.get_value ( ).replace (year = int (self.years.GetItems ( )[self.years.GetSelection ( )]))

    