# -*- coding: utf-8 -*-
import datetime
from utils import time_conversion

class HolidayDate:

  def __init__(self, date, is_holiday):
  
    self.date = date
    self.is_holiday = is_holiday
    

  def __str__(self):
    return time_conversion.date_to_string(self.date) + " - Holiday: " + str(self.is_holiday)
    
  def __hash__(self):
    return hash(self.date) + hash(self.is_holiday)
    
  def __eq__(self,other):
    return self.__cmp__(other) == 0
    
  def __cmp__(self,other):
    try:
      if self.date == other.date:
        return 0
      else:
        return cmp(self.date, other.date)
    
    except:
      return -1
