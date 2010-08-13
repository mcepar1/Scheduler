# -*- coding: utf-8 -*-

import cPickle as pickle
import os

class Vacation:
  
  HEADERS = ["OZNAKA", "VRSTA DOPUSTA"]
  
  def __init__(self, code, label):
    """
    This is the constructor.
      code: is the code of the vacation (X, L, T, ...)
      label: is the label of the vacation (državni praznik, ...)
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
    
class VacationContainer:
  """Contains methods, that deal with multiple instences of the vacation
  class at once (loading, saving, representing as a table, ...)"""
  
  FILES_DIR = os.path.join("data","persistence")
  FILE_NAME = "vacation.dat"
  
  def __init__(self, vacation_list = None):
    """This is the constructor
    vacation_list: a list (or set) that contains instances of the vacation class"""
    
    self.vacations = []
    
    if vacation_list:
      self.add_all(vacation_list)
        
  def add_all(self, vacation_list):
    """Adds all the elements of the vacation_list into the container
      vacation_list: a list that contains  instances of the vacation class"""
      
    for vacation in vacation_list:
        self.vacations.append(vacation)
  
  def save(self):
    """Saves the current state into an external file."""
    pickle.dump(self.vacations, file(os.path.join(VacationContainer.FILES_DIR, VacationContainer.FILE_NAME),'wb'))
    
  def load(self):
    """Loads the contens from the external file. The current state is LOST!!!!"""
    self.vacations = pickle.load(file(os.path.join(VacationContainer.FILES_DIR, VacationContainer.FILE_NAME),'rb'))
    
  def as_table(self):
    """Returns a table-like representation of self.
      return: a dictionary with two string keys:
        header: a list that contains headers of the table:
        items: a list of lists. The external list represents rows and the intrenal one represents columns within a single row."""
        
    
    rows_list = []
    for vacation in self.vacations:
      rows_list.append(vacation.as_list())
    
    table = {}
    table['header'] = Vacation.HEADERS  
    table['items'] = rows_list
   
    return table
    
  def __str__(self):
    return ", ".join([str(vacation) for vacation in self.vacations])
    
def load():
  """
  Loads and returns a container instance.
  """
  el = VacationContainer()
  el.load()
  return el
    
