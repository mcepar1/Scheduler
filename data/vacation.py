# -*- coding: Cp1250 -*-

import datetime

from data  import general, locations
from utils import translate

import locale

class Vacation (general.DataClass):
  
  HEADERS = ["OZNAKA", "VRSTA DOPUSTA", "OBRAČUNAN ČAS"]
  
  def __init__(self, code, label, duration):
    """
    This is the constructor.
      code: is the code of the vacation (X, L, T, ...)
      label: is the label of the vacation (drĹľavni praznik, ...)
      duration: is the number of hours, as if the person was working
    """
      
    self.code = code
    self.label = label
    self.start = datetime.time(hour = 0, minute = 0)
    self.end = datetime.time(hour = 23, minute = 59)
    self.blockade = datetime.timedelta()
    self.duration = duration
    
  def as_data_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    return [self.code, self.label, self.duration]
      
  def as_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    return [translate (self.code), translate (self.label), translate (self.duration)]
    
  def __str__(self):
    return self.code + " - " + self.label
    
  def __hash__(self):
    return hash(str(self))
    
  def __eq__(self, other):
    return self.__cmp__(other) == 0
    
  def __cmp__(self, other):
    try:
      if not locale.strcoll (self.code, other.code):
        if not locale.strcoll (self.label, other.label):
          return 0
        else:
          return locale.strcoll (self.label, other.label)
      else:
        return locale.strcoll (self.code, other.code)
    
    
    except:
      return - 1
    
def load():
  """
  Loads and returns a container instance.
  """
  el = general.DataContainer(locations.VACATION_DATA, Vacation.HEADERS)
  try:
    el.load()
  except Exception as e:
    print e
    
  return el
      
  
    
