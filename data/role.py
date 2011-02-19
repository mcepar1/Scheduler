# -*- coding: Cp1250 -*-

import cPickle as pickle
import os

class Role:
  
  HEADERS = ["VLOGA"]

  def __init__ (self, label):
    """
    This is the constructor.
      label: is the role's label
    """
    
    self.label = label;
    
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
      return cmp (self.label, other.label)
    except:
      return - 1
    
class RoleContainer:
  """Contains methods, that deal with multiple instances of the Role
  class at once (loading, saving, representing as a table, ...)"""
  
  FILES_DIR = os.path.join("persistence", "data")
  FILE_NAME = "roles.dat"

  def __init__(self, roles_list=None):
    """This is the constructor
    roles_list: a list (or set) that contains instances of the Role class"""
    
    self.roles = []
    
    if roles_list:
      self.add_all(roles_list)
      
  def add_all(self, roles_list):
    """Adds all the elements of the roles_list into the container
      roles_list: a list that contains  instances of the Role class"""
      
    for role in roles_list:
      for existing_role in self.roles:
        if role == existing_role:
          raise Exception('Vloga ' + str(role) + ' ze obstaja.')
      self.roles.append(role)
 
  def save(self):
    """Saves the current state into an external file."""
    pickle.dump(self.roles, file(os.path.join(RoleContainer.FILES_DIR, RoleContainer.FILE_NAME), 'wb'))
    
  def load(self):
    """Loads the contents from the external file. The current state is LOST!!!!"""
    self.roles = pickle.load(file(os.path.join(RoleContainer.FILES_DIR, RoleContainer.FILE_NAME), 'rb'))
    
  def as_table(self):
    """Returns a table-like representation of self.
      return: a dictionary with two string keys:
        header: a list that contains headers of the table:
        items: a list of lists. The external list represents rows and the intrenal one represents columns within a single row."""
        
    
    rows_list = []
    for role in self.roles:
      rows_list.append(role.as_list())
    
    table = {}
    table['header'] = Role.HEADERS  
    table['items'] = rows_list
   
    return table
    
  def get_element(self, index):
    """Returns the role at the specified index.
      index: index of the role
    """
    
    # TODO: verify, that the self.roles and the GUI table always match indexes
    return self.role[index]
    
  def __str__(self):
    return ", ".join([str(role) for role in self.roles])
  
def load():
  """
  Loads and returns a container instance.
  """
  el = RoleContainer()
  try:
    el.load()
  except Exception as e:
    print e
    pass
  return el
