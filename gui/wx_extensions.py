# -*- coding: utf-8 -*-

import datetime

import wx
import wx.calendar

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
  HOLIDAYS = {
                1: [1],
                2: [13],
                3: [22],
                4: [3],
                5: [29],
                6: [15],
                7: [4, 11],
                8: [4],
                9: [3],
                10: [],
                11: [27, 26],
                12: [24, 25]
              }
              
              
  def __init__(self, *args, **kwargs):
  
    wx.calendar.CalendarCtrl.__init__(self, *args, **kwargs)
    
    self.Bind(wx.calendar.EVT_CALENDAR_MONTH, self.__set_holidays,self)
    self.Bind(wx.calendar.EVT_CALENDAR_YEAR, self.__set_holidays,self)
    self.__set_holidays(None)
        
  def __set_holidays(self, event):
    """Colors the holidays"""
    
    for day in EnhancedCalendar.HOLIDAYS[self.PyGetDate().month]:
      self.SetHoliday(day)
      
  def GetDateObject (self):
    date = self.PyGetDate ( )
    is_holiday = date.day in EnhancedCalendar.HOLIDAYS[date.month]
    
    return HolidayDate(date, is_holiday)
    
    
    
    
