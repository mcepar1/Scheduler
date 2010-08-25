# -*- coding: utf-8 -*-

import datetime

import wx
import wx.calendar
import wx.lib.intctrl
import dateutil.easter


from data.date import HolidayDate

"""
This class behaves the same way as a normal wxCheckBox.
The only difference is that is also has an attribute
element.
Element is an instance, that is beeing manipulated by
this CheckBox.
"""
class LinkedCheckBox(wx.CheckBox):
  def __init__(self, element, *args, **kwargs):
    wx.CheckBox.__init__(self, *args, **kwargs)
    
    self.element = element

"""
This class is a wx.Choice, with predefined choices.
The hard-coded choices are months of the year.
"""    
class MonthChoice(wx.Choice):
  MONTHS = [
              'Januar',
              'Februar',
              'Marec',
              'April',
              'Maj',
              'Junij',
              'Julij',
              'Avgust',
              'September',
              'Oktober',
              'November',
              'December'
           ]

  def __init__(self, *args, **kwargs):
    kwargs['choices'] = MonthChoice.MONTHS
    wx.Choice.__init__(self, *args, **kwargs)
    
    self.SetSelection(datetime.date.today().month - 1)
    
  def get_value(self):
    """
    Returns an instance of the datetime.date, with current year, the selected
    month and the first day in the month.
      return: a datetime.date instance
    """
    #return MonthChoice.MONTHS[self.GetCurrentSelection()]
    return datetime.date(day = 1, month = self.GetCurrentSelection() + 1, year = int(datetime.date.today().year))

"""
This class behaves the same way as as a normal wxChoice.
The only difference is that it handles workplaces 
internally.
"""  
class WorkplaceChoice(wx.Choice):
  def __init__(self, workplaces, *args, **kwargs):
    self.workplaces = workplaces
    
    kwargs['choices'] = [str(workplace) for workplace in self.workplaces]
    wx.Choice.__init__(self, *args, **kwargs)
    
  def get_value(self):
    """Returns the selected instance of the workspace class"""
    return self.workplaces[self.GetCurrentSelection()]
    
"""
This class behaves the same way as as a normal wxIntCtrl.
The only difference is that it handles employment
types internally.
"""
class LinkedIntCtrl(wx.lib.intctrl.IntCtrl):
  
  def __init__(self, employment_type, *args, **kwargs):
    """
    The default constructor.
      employment_type: is an instance of the EmploymentType, that this control will manage.
    """
    wx.lib.intctrl.IntCtrl.__init__(self, *args, **kwargs)
    
    self.employment_type = employment_type
    
    self.Bind(wx.lib.intctrl.EVT_INT, self.__set_monthly_hours, self)
    
  def __set_monthly_hours(self, event):
    """Event listener for the value."""
    self.employment_type.monthly_hours = self.GetValue()

class LinkedSpinCtr(wx.SpinCtrl):
  def __init__(self, turnus, *args, **kwargs):
    wx.SpinCtrl.__init__(self, *args, **kwargs)
    
    self.element = turnus

"""
This class behaves the same way as a normal wxComboBox.
The only difference is that it handles employment 
types internally.
"""    
class LinkedComboBox(wx.ComboBox):
  
  def __init__(self, *args, **kwargs):
    """The default constructor."""
  
    #TODO clean the imports
    from global_vars import employment_types
    
    wx.ComboBox.__init__(self, *args, **kwargs)
    self.employment_types = employment_types.employment_types
    
    self.Clear()
    for employment_type in self.employment_types:
      self.Append(str(employment_type))
      
    self.Disable()
    
    
  def set_selection(self, person):
    """
    Sets the selection.
      person: is an instance of either the Nurse or Doctor class
    """
    
    if person:
      self.Enable()
      self.SetStringSelection(str(person.employment_type))
    else:
      self.Disable()
        
  def get_selected_type(self):
    """
    Return the selected employement type if any.
      return: an employement type if a valid emplyement type was
              selected, None otherwise.
    """
    
    if self.employment_types:
      for employment_type in self.employment_types:
        if employment_type.label == self.GetValue():
          return employment_type
    else:
      return None
    
"""
This class behaves the same way as a normal wxCalendar.
It recognizes Slovenian holidays, and does not consider
Saturday as a weekend.
It has additional methods and returns a custom wrapper
around the python date object.
"""
class EnhancedCalendar(wx.calendar.CalendarCtrl):

  # fill these dates out for the present year
  # some could change with another year
  # {month: list of holiday dates in month}
  # TODO: export into an external, easy to edit file
  HOLIDAYS = {
                1: [1, 2], # novo leto
                2: [8], # Slovenski kulturni praznik
                3: [],
                4: [27], # dan boja proti okupatorju
                5: [1, 2, 31], # praznik dela, Binkošti
                6: [25], # dan državnosti
                7: [],
                8: [15], # Marijino vnebovzetje
                9: [],
                10: [31], # dan reformacije
                11: [1], # dan spomina na mrtve
                12: [25, 26] # božič, dan samostojnosti
              }
              
              
  def __init__(self, *args, **kwargs):
  
    wx.calendar.CalendarCtrl.__init__(self, *args, **kwargs)
    
    self.Bind(wx.calendar.EVT_CALENDAR_MONTH, self.__set_holidays, self)
    self.Bind(wx.calendar.EVT_CALENDAR_YEAR, self.__set_holidays, self)
    self.__set_holidays(None)
        
  def __set_holidays(self, event):
    """Colors the holidays"""
    
    for day in self.__get_holidays(year=self.PyGetDate().year)[self.PyGetDate().month]:
      self.SetHoliday(day)
      
  def __get_holidays(self, year=datetime.date.today().year):
    """
    Returns a dict in the same format as HOLIDAYS, only with the correct EASTER and easter mondays dates.
    """
    # create a hard copy
    holidays = {}
    for month in EnhancedCalendar.HOLIDAYS:
      holidays[month] = []
      for day in EnhancedCalendar.HOLIDAYS[month]:
        holidays[month].append(day)
    
    easter = dateutil.easter.easter(year)
    easter_monday = easter + datetime.timedelta(days=1)
    
    holidays[easter.month].append(easter.day)
    holidays[easter_monday.month].append(easter_monday.day)
    
    return holidays
      
  def GetDateObject (self):
    """
    Returns a custom date object.
      return: a HolidayDate instance
    """
    
    date = self.PyGetDate ()
    
    # a national holiday or a Sunday
    is_holiday = (date.strftime("%w") == 0) or date.day in self.__get_holidays()[date.month]
    
    return HolidayDate(date, is_holiday)
    
    
    
    
