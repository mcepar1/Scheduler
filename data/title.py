# -*- coding: Cp1250 -*-

from Scheduler.data  import general, locations
from Scheduler.utils import translate

class Title:
  
  HEADERS = ["NAZIV"]
  
  def __init__(self, label):
    
    self.label = label
    
  def as_data_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    return [self.label]
    
  def as_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    return [translate (self.label)]
    
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
    
def load():
  """
  Loads and returns a container instance.
  """
  el = general.Container(locations.TITLE_DATA, Title.HEADERS)
  try:
    el.load()
  except Exception as e:
    print e
    
  return el
  