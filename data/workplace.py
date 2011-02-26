# -*- coding: Cp1250 -*-

from data  import general, locations
from utils import translate

import locale

class Workplace (general.DataClass):
  
  HEADERS = ["OZNAKA", "DELAJ POPOLDNE PRED PRAZNIKOM"]
  
  def __init__(self, label, holiday_rule):
    """
    This is the default constructor
      label: the name of this workplace
      holiday_rule: is a boolean that tells the scheduler, if the workplace 
                    should follow the special scheduling rule (if works on a work 
                    free day, then it must work the afternoon before (can violate
                    any other restriction)
    """
    
    self.label = label
    self.holiday_rule = holiday_rule
    
    # which roles can nurses assume in the workplace
    self.roles = set()
    
    # if the turnus is located in the set, the workplace allows that turnus
    self.allowed_turnuses = set ()
    
  def as_data_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    
    return [self.label, self.holiday_rule]
    
  def as_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    
    return [translate (self.label), translate (self.holiday_rule)]
    
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
    
  def synchronize_data(self, *args):
    """
    This is used to keep the instances of the subclasses consistent. This method updates every internal
    attribute of the class, so that the matching objects are forced into the data structure. Look at the
    data model for more details. 
    """
    for data in args:
      if data in self.allowed_turnuses:
        self.remove_allowed_turnus(data)
        self.add_allowed_turnus(data)
      if data in self.roles:
        self.remove_role(data)
        self.add_role(data)
    
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
      

def load():
  """
  Loads and returns a container instance.
  """
  el = general.DataContainer(locations.WORKPLACE_DATA, Workplace.HEADERS)
  try:
    el.load()
  except Exception as e:
    print e
  return el
    
    
