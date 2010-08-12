# -*- coding: utf-8 -*-

import datetime

import wx
import wx.calendar
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
  def __init__(self,element,*args,**kwargs):
    wx.CheckBox.__init__(self,*args,**kwargs)
    
    self.element = element
    
    
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
    
    self.Bind(wx.calendar.EVT_CALENDAR_MONTH, self.__set_holidays,self)
    self.Bind(wx.calendar.EVT_CALENDAR_YEAR, self.__set_holidays,self)
    self.__set_holidays(None)
        
  def __set_holidays(self, event):
    """Colors the holidays"""
    
    for day in self.__get_holidays(year = self.PyGetDate().year)[self.PyGetDate().month]:
      self.SetHoliday(day)
      
  def __get_holidays(self, year = datetime.date.today().year):
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
    easter_monday = easter+datetime.timedelta(days = 1)
    
    holidays[easter.month].append(easter.day)
    holidays[easter_monday.month].append(easter_monday.day)
    
    return holidays
      
  def GetDateObject (self):
    """
    Returns a custom date object.
      return: a HolidayDate instance
    """
    
    date = self.PyGetDate ( )
    
    # a national holiday or a Sunday
    is_holiday = (date.strftime("%w") == 0) or date.day in self.__get_holidays()[date.month]
    
    return HolidayDate(date, is_holiday)
    
    
    
    
