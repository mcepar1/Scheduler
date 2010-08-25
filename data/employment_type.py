# -*- coding: utf-8 -*-

import cPickle as pickle
import os

"""
This file contains the employment types.
"""
class EmploymentType:

  HEADERS = ["VRSTA", "URE NA TEDEN", "NADURE"]

  def __init__(self, label, weekly_hours, has_overtime, monthly_hours = 0, allowed_turnuses=[]):
    """
    The default constructor
      label: is the label of the employment type
      weekly_hours: is the minimum required work time per week
      has_overtime: true, if it allows overtime, false otherwise
      monthly_hours: is the minimum required work time per month
      allowed_turnuses: a list of turnuses, that a parson can have
    """
    
    self.label = label
    self.weekly_hours = weekly_hours
    self.has_overtime = has_overtime
    self.monthly_hours = monthly_hours
    
    self.allowed_turnuses = set(allowed_turnuses)
    
  def as_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    return [str(self.label), str(self.weekly_hours), str(self.has_overtime)]
    
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
      if self.label == other.label:
        if self.weekly_hours == other.weekly_hours:
          return cmp (self.has_overtime, other.has_overtime)
        else:
          return cmp(self.weekly_hours, other.weekly_hours)
      else:
        return cmp(self.label, other.label)
    
    
    except:
      return - 1
      
class EmploymentTypeContainer:
  """Contains methods, that deal with multiple instences of the employmentType
  class at once (loading, saving, representing as a table, ...)"""
  
  FILES_DIR = os.path.join("data", "persistence")
  FILE_NAME = "employment_type.dat"
  
  def __init__(self, employment_type_list=None):
    """
    This is the constructor
      employment_type: a list (or set) that contains instances of the EmploymentType class.
    """
    
    self.employment_types = []
    
    if employment_type_list:
      self.add_all(employment_type_list)
        
  def add_all(self, employment_type_list):
    """
    Adds all the elements of the employment_type_list into the container
      employment_type_list: a list that contains  instances of the EmploymentType class.
    """
      
    for employment_type in employment_type_list:
        self.employment_types.append(employment_type)
  
  def save(self):
    """Saves the current state into an external file."""
    pickle.dump(self.employment_types, file(os.path.join(EmploymentTypeContainer.FILES_DIR, EmploymentTypeContainer.FILE_NAME), 'wb'))
    
  def load(self):
    """Loads the contens from the external file. The current state is LOST!!!!"""
    self.employment_types = pickle.load(file(os.path.join(EmploymentTypeContainer.FILES_DIR, EmploymentTypeContainer.FILE_NAME), 'rb'))
    
  def as_table(self):
    """
    Returns a table-like representation of self.
      return: a dictionary with two string keys:
        header: a list that contains headers of the table:
        items: a list of lists. The external list represents rows and the intrenal one represents columns within a single row.
    """
        
    
    rows_list = []
    for employment_type in self.employment_types:
      rows_list.append(employment_type.as_list())
    
    table = {}
    table['header'] = EmploymentType.HEADERS  
    table['items'] = rows_list
   
    return table
    
  def __str__(self):
    return ", ".join([str(employment_type) for employment_type in self.employment_types])
    
def load():
  """
  Loads and returns a container instance.
  """
  el = EmploymentTypeContainer()
  try:
    el.load()
  except Exception as e:
    print e
    pass
  return el


