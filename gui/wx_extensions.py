# -*- coding: utf-8 -*-

from utils import holiday

import datetime
import calendar

import wx
import wx.calendar
import wx.lib.intctrl



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
    
    next_month = datetime.date(day=28, month=datetime.date.today().month, year=datetime.date.today().year) + datetime.timedelta(days=10)
    self.SetSelection(next_month.month - 1)
    
  def get_value(self):
    """
    Returns an instance of the datetime.date, with current year, the selected
    month and the first day in the month.
      return: a datetime.date instance
    """
    #return MonthChoice.MONTHS[self.GetCurrentSelection()]
    return datetime.date(day=1, month=self.GetCurrentSelection() + 1, year=int(datetime.date.today().year))

"""
This class behaves the same way as as a normal wxChoice.
The only difference is that it handles workplaces 
internally.
"""  
class WorkplaceChoice(wx.Choice):
  def __init__(self, workplaces, *args, **kwargs):
    self.workplaces = sorted(workplaces)
    
    kwargs['choices'] = [str(workplace) for workplace in self.workplaces]
    wx.Choice.__init__(self, *args, **kwargs)
    
  def get_value(self):
    """Returns the selected instance of the workspace class"""
    if self.workplaces:
      return self.workplaces[self.GetCurrentSelection()]
    else:
      return 'Ni delovisc'
    
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

                      
  def __init__(self, *args, **kwargs):
  
    wx.calendar.CalendarCtrl.__init__(self, *args, **kwargs)
    
    self.Bind(wx.calendar.EVT_CALENDAR_MONTH, self.__set_holidays, self)
    self.Bind(wx.calendar.EVT_CALENDAR_YEAR, self.__set_holidays, self)
    
    next_month = datetime.date(day=28, month=datetime.date.today().month, year=datetime.date.today().year) + datetime.timedelta(days=10)
    self.PySetDate(next_month.replace(day=1))
    self.__set_holidays(None)
        
  def __set_holidays(self, event):
    """Colors the holidays"""
    
    for date in self.__get_dates():
      if holiday.is_workfree(date):
        self.SetHoliday(date.day)
      else:
        self.ResetAttr(date.day)
      
    
  def __get_dates(self):
    """Returns a sorted list of days for the current date and month."""
    current_date = self.PyGetDate()
    dates = []
    for day in calendar.Calendar().itermonthdays(current_date.year, current_date.month):
      if day:
        dates.append(datetime.date(day=day, month=current_date.month, year=current_date.year))
              
    dates.sort()
    
    return dates
    
    
    
