# -*- coding: Cp1250 -*-

from data  import general, locations
from utils import translate

import locale

"""
This file contains the employment types.
"""
class EmploymentType (general.DataClass):

  HEADERS = ["VRSTA", "URE NA TEDEN"]

  def __init__(self, label, weekly_hours, comment = '', monthly_hours=0):
    """
    The default constructor
      label: is the label of the employment type
      weekly_hours: is the minimum required work time per week
      comment: @see: general.DataClass
      monthly_hours: is the minimum required work time per month
    """
    general.DataClass.__init__ (self, comment)
    
    self.label = label
    self.weekly_hours    = weekly_hours
    self.monthly_hours   = monthly_hours
    
    
  def as_data_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    return [self.label, self.weekly_hours]
    
  def as_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    return [translate (self.label), translate (self.weekly_hours)]
    
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
        return cmp (self.weekly_hours, other.weekly_hours)
      else:
        return locale.strcoll(self.label, other.label)
    
    
    except:
      return - 1
    
def load ( ):
  """
  Loads and returns a container instance.
  """
  return general.load (locations.EMPLOYMENT_TYPE_DATA, EmploymentType)


