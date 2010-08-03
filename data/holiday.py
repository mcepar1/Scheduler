# -*- coding: utf-8 -*-

import cPickle as pickle
import os

class Holiday:
  
  HEADERS = ["OZNAKA", "VRSTA DOPUSTA"]
  
  def __init__(self, code, label):
    """
    This is the constructor.
      code: is the code of the holiday (X, L, T, ...)
      label: is the label of the holiday (državni praznik, ...)
    """
      
    self.code = code
    self.label = label
      
  def as_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    return [self.code, self.label]
    
  def __str__(self):
    return self.code + " - " + self.label
    
  def __hash__(self):
    return hash(str(self))
    
  def __eq__(self,other):
    return self.__cmp__(other) == 0
    
  def __cmp__(self,other):
    try:
      if self.code == other.code:
        if self.label == other.label:
          return 0
        else:
          return cmp(self.label, other.label)
      else:
        return cmp(self.code, other.code)
    
    
    except:
      return -1
    
class HolidayContainer:
  """Contains methods, that deal with multiple instences of the Holiday
  class at once (loading, saving, representing as a table, ...)"""
  
  FILES_DIR = os.path.join("data","persistence")
  FILE_NAME = "holiday.dat"
  
  def __init__(self, holiday_list = None):
    """This is the constructor
    holiday_list: a list (or set) that contains instances of the Holiday class"""
    
    self.holidays = []
    
    if holiday_list:
      self.add_all(holiday_list)
        
  def add_all(self, holiday_list):
    """Adds all the elements of the holiday_list into the container
      holiday_list: a list that contains  instances of the Holiday class"""
      
    for holiday in holiday_list:
        self.holidays.append(holiday)
  
  def save(self):
    """Saves the current state into an external file."""
    pickle.dump(self.holidays, file(os.path.join(HolidayContainer.FILES_DIR, HolidayContainer.FILE_NAME),'wb'))
    
  def load(self):
    """Loads the contens from the external file. The current state is LOST!!!!"""
    self.holidays = pickle.load(file(os.path.join(HolidayContainer.FILES_DIR, HolidayContainer.FILE_NAME),'rb'))
    
  def as_table(self):
    """Returns a table-like representation of self.
      return: a dictionary with two string keys:
        header: a list that contains headers of the table:
        items: a list of lists. The external list represents rows and the intrenal one represents columns within a single row."""
        
    
    rows_list = []
    for holiday in self.holidays:
      rows_list.append(holiday.as_list())
    
    table = {}
    table['header'] = Holiday.HEADERS  
    table['items'] = rows_list
   
    return table
    
  def __str__(self):
    return ", ".join([str(holiday) for holiday in self.holidays])
    
