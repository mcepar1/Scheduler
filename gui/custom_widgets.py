# -*- coding: Cp1250 -*-

"""
This file contains reusable widgets, that have no implementation in the wx framework. 
"""
import wx
import custom_events
from gui import wx_extensions

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
      
    
    sizer = wx.StaticBoxSizer (wx.StaticBox(self, wx.ID_ANY, self.GetLabel ( )), wx.VERTICAL)
    for radio in self.radio_buttons:
      sizer.Add (radio, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
      
    self.SetSizerAndFit (sizer)
    self.set_selectable (selectable)
    
  def set_selectable (self, elements):
    """
    Set the elements, that can be selected and selects the first. Fires the appropriate event. If the 
    list contains unknown elements, nothing gets deleted or updated.
      elements: a list, that contains elements, that are allowed to be selected
    """
    for i, element in enumerate (self.elements):
      if element in elements:
        self.radio_buttons[i].Enable ( )
      else:
        self.radio_buttons[i].SetValue (False)
        self.radio_buttons[i].Disable ( )
        
    #select the first possible radio
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
    
    if self.GetLabel ( ) == '' or self.GetLabel ( ) == 'panel':
      sizer = wx.BoxSizer (wx.HORIZONTAL)
    else:
      sizer = wx.StaticBoxSizer (wx.StaticBox (self, wx.ID_ANY, self.GetLabel ( )), wx.HORIZONTAL)
    sizer.Add (self.months, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
    sizer.Add (self.years,  0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT)
    
    self.SetSizerAndFit (sizer)
    
  def get_selected_date (self):
    """
    Returns a datetime.date object, that represents the selected combination.
      @return: a datetime.date object
    """
    return self.months.get_value ( ).replace (year = int (self.years.GetItems ( )[self.years.GetSelection ( )]))

    