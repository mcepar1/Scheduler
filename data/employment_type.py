# -*- coding: Cp1250 -*-

from Scheduler.data  import general, locations
from Scheduler.utils import translate

import locale

"""
This file contains the employment types.
"""
class EmploymentType:

  HEADERS = ["VRSTA", "URE NA TEDEN", "NADURE"]

  def __init__(self, label, weekly_hours, has_overtime, allowed_turnuses=[], monthly_hours=0):
    """
    The default constructor
      label: is the label of the employment type
      weekly_hours: is the minimum required work time per week
      has_overtime: true, if it allows overtime, false otherwise
      allowed_turnuses: a list of turnuses, that a parson can have
      monthly_hours: is the minimum required work time per month
    """
    
    self.label = label
    self.weekly_hours = weekly_hours
    self.has_overtime = has_overtime
    self.monthly_hours = monthly_hours
    
    self.allowed_turnuses = set(allowed_turnuses)
    
  def as_data_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    return [self.label, self.weekly_hours, self.has_overtime]
    
  def as_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    return [translate (self.label), translate (self.weekly_hours), translate (self.has_overtime)]
    
  def __str__(self):
    return self.label
    
  def __hash__(self):
    return hash(str(self))
    
  def __eq__(self, other):
    return self.__cmp__(other) == 0
    
  def __cmp__(self, other):
    #Monthly hours attribute is excluded, because this 
    #attribute varies form month to month
    try:
      if  not locale.strcoll(self.label, other.label):
        if self.weekly_hours == other.weekly_hours:
          return cmp (self.has_overtime, other.has_overtime)
        else:
          return cmp(self.weekly_hours, other.weekly_hours)
      else:
        return locale.strcoll(self.label, other.label)
    
    
    except:
      return - 1
    
def load():
  """
  Loads and returns a container instance.
  """
  el = general.Container(locations.EMPLOYMENT_TYPE_DATA, EmploymentType.HEADERS)
  try:
    el.load()
  except Exception as e:
    print e
    pass
  return el


