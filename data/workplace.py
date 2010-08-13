# -*- coding: utf-8 -*-

import cPickle as pickle
import os

class Workplace:
  
  HEADERS = ["OZNAKA"]
  
  def __init__(self, label):
    """
    This is the default constructor
      label: the name of this workplace
    """
    
    self.label = label
    
    # if the turnus is located in the set, the workplace does not allow that turnus
    self.forbidden_turnuses = set ( )
    
  def as_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    
    return [self.label]
    
  def add_invalid_turnus (self, turnus):
    """
    Adds a turnus to the forbidden turnuses.
      turnus: is the new forbidden turnus
    """
    self.forbidden_turnuses.add (turnus)
    
  def remove_invalid_turnus (self,turnus):
    """
    Removes a turnus from the forbidden turnuses.
      turnus: the turnus, that will be allowed
    """
    self.forbidden_turnuses.remove (turnus)
    
  def __str__(self):
    return self.label
    
  def __hash__(self):
    return hash(str(self))
    
  def __eq__(self,other):
    return self.__cmp__(other) == 0
    
  def __cmp__(self,other):
    try:
      if self.label == other.label:
        return 0
      else:
        return cmp(self.label, other.label)
    
    except:
      return -1
      
class WorkplaceContainer:
  """Contains methods, that deal with multiple instences of the workplace
  class at once (loading, saving, representing as a table, ...)"""
  
  FILES_DIR = os.path.join("data","persistence")
  FILE_NAME = "workplace.dat"
  
  def __init__(self, workplace_list = None):
    """
    This is the constructor
      vacation_list: a list (or set) that contains instances of the vacation class
    """
    
    self.workplaces = []
    
    if workplace_list:
      self.add_all(workplace_list)
      
  def add_all(self, workplace_list):
    """
    Adds all the elements of the workplace_list into the container.
      workplace_list: a list that contains  instances of the vacation class
    """
      
    for workplace in workplace_list:
        self.workplaces.append(workplace)
  
  def save(self):
    """Saves the current state into an external file."""
    pickle.dump(self.workplaces, file(os.path.join(WorkplaceContainer.FILES_DIR, WorkplaceContainer.FILE_NAME),'wb'))
    
  def load(self):
    """Loads the contens from the external file. The current state is LOST!!!!"""
    self.workplaces = pickle.load(file(os.path.join(WorkplaceContainer.FILES_DIR, WorkplaceContainer.FILE_NAME),'rb'))
    
  def as_table(self):
    """Returns a table-like representation of self.
      return: a dictionary with two string keys:
        header: a list that contains headers of the table:
        items: a list of lists. The external list represents rows and the intrenal one represents columns within a single row."""
        
    
    rows_list = []
    for workplace in self.workplaces:
      rows_list.append(workplace.as_list())
    
    table = {}
    table['header'] = Workplace.HEADERS  
    table['items'] = rows_list
   
    return table
    
  def get_element(self, index):
    """Returns the nurse at the specified index.
      index: index of the nurse
    """
    
    # TODO: verify, that the self.workplaces and the GUI table always match indexes
    return self.workplaces[index]
    
  def __str__(self):
    return ", ".join([str(workplace) for workplace in self.workplaces])
    
def load():
  """
  Loads and returns a container instance.
  """
  el = WorkplaceContainer()
  el.load()
  return el
    
    
