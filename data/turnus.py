# -*- coding: Cp1250 -*-

from data  import general, locations
from utils import translate

import locale

class Turnus (general.DataClass):
  
  HEADERS = ["OZNAKA", "TIP DELA", "ZAČETEK", "KONEC", "TRAJANJE", "BLOKADA", "NA PROST DAN"]
  
  def __init__(self, code, label, start, end, duration, blockade, holiday, types=None):
    """
    This is the constructor.
      code: is the code of the turnus (D,P,N, ...)
      label: is the label of the turnus (eno izmensko, ...)
      start: is the starting time
      end: is the ending time
      duration: is the length of the shift (start - end)
      blockade: how long after the end of the shift, the person cannot perform tasks
      holiday: if true, the turnus can be scheduled on a holiday
      types: a list of turnus types, that this turnus belongs to
    """
  
  
    self.code = code
    self.label = label
    self.start = start
    self.end = end
    self.duration = duration
    self.blockade = blockade    
    self.holiday = holiday
    
    self.types = set()
    if not types:
      # a very rare case
      self.__gues_types()
    else:
      self.types = types
  
  def as_data_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    return [self.code, self.label, self.start, self.end, self.duration, self.blockade, self.holiday]
    
  def as_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    return [translate (self.code), translate (self.label), translate (self.start), translate (self.end), translate (self.duration), translate (self.blockade), translate (self.holiday)]
  
  def add_type(self, type):
    """Adds a type to the set of turnus types."""
    self.types.add(type)
    
  def remove_type(self, type):
    """Removes a type from the set of turnus types."""
    self.types.remove(type)
    
  def has_type(self, type):
    """
    Checks, it the turnus is of the specified type.
      type: a turnus_type object
      return: true, if the turnus is of the type, false otherwise
    """
    return type in self.types
    
  def synchronize_data(self, *args):
    """
    This is used to keep the instances of the subclasses consistent. This method updates every internal
    attribute of the class, so that the matching objects are forced into the data structure. Look at the
    data model for more details. 
    """
    for data in args:
      if data in self.types:
        self.remove_type(data)
        self.add_type(data)
  
  def __gues_types(self):
    """Tries to guess into which types does this turnus belong into"""
    import global_vars
    turnus_types = global_vars.get_turnus_types ( ).get_all ( )
    # if it is empty, try to reload the container
    # only when inputing initial data
    if not turnus_types:
      import turnus_type
      turnus_types = turnus_type.load ( ).get_all ( )
    
    
    #first get all the capital letters from the turnus code
    #TODO: document this
    chars = set()
    for char in self.code:
      if char.isalpha() and char.isupper():
        chars.add(char)
        
    #now we check if they match with the types first letter
    for char in chars:
      for type in global_vars.get_turnus_types ( ).get_all ( ):
        if char == str(type)[0].upper():
          self.types.add(type)
          
    
  def __str__(self):
    return self.code + " - " + self.label
    
  def __hash__(self):
    return hash(str(self))
    
  def __eq__(self, other):
    return self.__cmp__(other) == 0
    
  def __cmp__(self, other):
    try:
      if not locale.strcoll (self.code, other.code):
        if not locale.strcoll (self.label, other.label):
          if self.start == other.start:
            if self.end == other.end:
              return 0
            else:
              return cmp(self.end, other.end)
          else:
            return cmp(self.start, other.start)
        else:
          return locale.strcoll (self.label, other.label)
      else:
        return locale.strcoll (self.code, other.code)
    
    
    except:
      return - 1
    
class TurnusContainer (general.DataContainer):
  
  def get_by_type(self, type, workplace=None):
    """
    Returns a set of turnuses, that belong to a specific type.
      type: is the turnus type
      workplace: if this attribute is given, the method return all the turnuses
                 that belong to the specific type and are allowed for the workplace
      return: a set of turnuses
    """
    turnuses = set()
    for turnus in self.elements:
      if type in turnus.types:
        turnuses.add(turnus)
    
    if workplace:
      return turnuses & workplace.allowed_turnuses
    else:    
      return turnuses
    
  def __str__(self):
    return ", ".join([str(turnus) for turnus in self.turnuses])
    
def load ( ):
  """
  Loads and returns a container instance.
  """
  return general.load (locations.TURNUS_DATA, Turnus, container_class=TurnusContainer)
  
    
