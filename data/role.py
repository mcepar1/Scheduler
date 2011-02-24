# -*- coding: Cp1250 -*-

from Scheduler.data  import general, locations

class Role:
  
  HEADERS = ["VLOGA"]

  def __init__ (self, label):
    """
    This is the constructor.
      label: is the role's label
    """
    
    self.label = label;
    
  def as_data_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    
    return [self.label]
    
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
    
  
def load():
  """
  Loads and returns a container instance.
  """
  el = general.Container(locations.ROLE_DATA, Role.HEADERS)
  try:
    el.load()
  except Exception as e:
    print e
    pass
  return el
