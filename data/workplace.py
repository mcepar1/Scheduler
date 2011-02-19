# -*- coding: Cp1250 -*-

import cPickle as pickle
import os

class Workplace:
  
  HEADERS = ["OZNAKA", "DELAJ POPOLDNE PRED PRAZNIKOM"]
  
  def __init__(self, label, holiday_rule):
    """
    This is the default constructor
      label: the name of this workplace
      holiday_rule: is a boolean that tells the scheduler, if the workplace 
                    should follow the spacial scheduling rule (if works on a work 
                    free day, then it must work the afternoon before (can violate
                    any other restriction)
    """
    
    self.label = label
    self.holiday_rule = holiday_rule
    
    # which roles can nurses assume in the workplace
    self.roles = set()
    
    # if the turnus is located in the set, the workplace allows that turnus
    self.allowed_turnuses = set ()
    
  def as_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    
    return [self.label, str(self.holiday_rule)]
    
  def add_allowed_turnus (self, turnus):
    """
    Adds a turnus to the allowed turnuses.
      turnus: is the new allowed turnus
    """
    self.allowed_turnuses.add (turnus)
    
  def remove_allowed_turnus (self, turnus):
    """
    Removes a turnus from the allowed turnuses.
      turnus: the turnus, that will be allowed
    """
    self.allowed_turnuses.remove (turnus)
    
  def add_role (self, role):
    """
    Adds a role to the workplace.
      role: is the role that will be added
    """
    self.roles.add(role)
    
  def remove_role (self, role):
    """
    Removes the role from the workplace
      role: the role that will be removed
    """
    # removing an un-added role should not be possible
    self.roles.remove(role)
    
  def __str__(self):
    return self.label
    
  def __hash__(self):
    return hash(str(self))
    
  def __eq__(self, other):
    return self.__cmp__(other) == 0
    
  def __cmp__(self, other):
    try:
      if self.label == other.label:
        return 0
      else:
        return cmp(self.label, other.label)
    
    except:
      return - 1
      
class WorkplaceContainer:
  """Contains methods, that deal with multiple instences of the workplace
  class at once (loading, saving, representing as a table, ...)"""
  
  FILES_DIR = os.path.join("persistence", "data")
  FILE_NAME = "workplace.dat"
  
  def __init__(self, workplace_list=None):
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
    pickle.dump(self.workplaces, file(os.path.join(WorkplaceContainer.FILES_DIR, WorkplaceContainer.FILE_NAME), 'wb'))
    
  def load(self):
    """Loads the contens from the external file. The current state is LOST!!!!"""
    self.workplaces = pickle.load(file(os.path.join(WorkplaceContainer.FILES_DIR, WorkplaceContainer.FILE_NAME), 'rb'))
    
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
  try:
    el.load()
  except Exception as e:
    print e
  return el
    
    
