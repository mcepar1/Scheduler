# -*- coding: Cp1250 -*-

from data  import general, locations
from utils import translate

import locale

class Workplace (general.DataClass):
  
  HEADERS = ["OZNAKA"]
  
  def __init__(self, label, holiday_rule=False):
    """
    This is the default constructor
      label: the name of this workplace
      holiday_rule: is a boolean that tells the scheduler, if the workplace 
                    should follow the special scheduling rule (if works on a work 
                    free day, then it must work the afternoon before (can violate
                    any other restriction). Default value is False.
    """
    general.DataClass.__init__ (self)
    
    self.label = label
    self.holiday_rule = holiday_rule
     
    
  def as_data_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    
    return [self.label]
    
  def as_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    
    return [translate (self.label)]
  
  def has_holiday_rule (self):
    """
    Checks, if the workplace has the holiday rule.
      @return: True if it has, False otherwise
    """
    return self.holiday_rule
  
  def set_holiday_rule (self, holiday_rule):
    """
    Sets the workplace's holiday rule.
      @param holiday_rule: a boolean
    """
    self.holiday_rule = holiday_rule
    
  def __str__(self):
    return self.label
    
  def __hash__(self):
    return hash(str(self))
    
  def __eq__(self, other):
    return self.__cmp__(other) == 0
    
  def __cmp__(self, other):
    try:
      if  not locale.strcoll (self.label, other.label):
        return 0
      else:
        return locale.strcoll (self.label, other.label)
    
    except:
      return - 1
      

def load ( ):
  """
  Loads and returns a container instance.
  """
  return general.load (locations.WORKPLACE_DATA, Workplace)
    
    
