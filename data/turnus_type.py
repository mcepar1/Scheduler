# -*- coding: Cp1250 -*-

import cPickle as pickle
import os

class TurnusType:
  
  HEADERS = ["VRSTE TURNUSOV"]
  
  def __init__(self, label):
    
    self.label = label
    
  def as_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    return [self.label]
    
  def __str__(self):
    return self.label
    
  def __hash__(self):
    return hash(str(self))
    
  def __eq__(self, other):
    return self.__cmp__(other) == 0
    
  def __cmp__(self, other):
    try:
      return cmp(self.label, other.label)
    except:
      return - 1
    
class TurnusTypeContainer:
  """Contains methods, that deal with multiple instances of the TurnusType
  class at once (loading, saving, representing as a table, ...)"""
  
  FILES_DIR = os.path.join("persistence", "data")
  FILE_NAME = "turnus_types.dat"
  
  def __init__(self, turnus_types_list=None):
    """This is the constructor
    turnus_types_list: a list (or set) that contains instances of the TurnusType class"""
    
    self.turnus_types = []
    
    if turnus_types_list:
      self.add_all(turnus_types_list)
        
  def add_all(self, turnus_types_list):
    """Adds all the elements of the turnus_types_list into the container
      turnus_types_list: a list that contains  instances of the TurnusType class"""
      
    for turnus_type in turnus_types_list:
        self.turnus_types.append(turnus_type)
  
  def save(self):
    """Saves the current state into an external file."""
    pickle.dump(self.turnus_types, file(os.path.join(TurnusTypeContainer.FILES_DIR, TurnusTypeContainer.FILE_NAME), 'wb'))
    
  def load(self):
    """Loads the contens from the external file. The current state is LOST!!!!"""
    self.turnus_types = pickle.load(file(os.path.join(TurnusTypeContainer.FILES_DIR, TurnusTypeContainer.FILE_NAME), 'rb'))
    
  def as_table(self):
    """Returns a table-like representation of self.
      return: a dictionary with two string keys:
        header: a list that contains headers of the table:
        items: a list of lists. The external list represents rows and the internal one represents columns within a single row."""
        
    
    rows_list = []
    for turnus_type in self.turnus_types:
      rows_list.append(turnus_type.as_list())
    
    table = {}
    table['header'] = TurnusType.HEADERS  
    table['items'] = rows_list
   
    return table
    
  def __str__(self):
    return ", ".join([str(turnus_type) for turnus_type in self.turnus_types])
    
def load():
  """
  Loads and returns a container instance.
  """
  el = TurnusTypeContainer()
  try:
    el.load()
  except Exception as e:
    print e
    
  return el
  