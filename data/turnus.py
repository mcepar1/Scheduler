# -*- coding: Cp1250 -*-

from Scheduler.data  import general, locations

class Turnus:
  
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
    
  def as_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    return [self.code, self.label, self.start.strftime("%H:%M"), self.end.strftime("%H:%M"), str(self.duration), str(self.blockade), str(self.holiday)]
  
  def add_type(self, type):
    """Adds a type to the set of turnus types."""
    self.types.add(type)
    
  def remove_type(self, type):
    """Removes a type from the set of turnus types."""
    self.types.remove(type)
  
  def __gues_types(self):
    """Tries to guess into which types does this turnus belong into"""
    from global_vars import turnus_types
    
    #first get all the capital letters from the turnus code
    #TODO: document this
    chars = set()
    for char in self.code:
      if char.isalpha() and char.isupper():
        chars.add(char)
        
    #now we check if they match with the types first letter
    for char in chars:
      for type in turnus_types.get_all ( ):
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
      if self.code == other.code:
        if self.label == other.label:
          if self.start == other.start:
            if self.end == other.end:
              return 0
            else:
              return cmp(self.end, other.end)
          else:
            return cmp(self.start, other.start)
        else:
          return cmp(self.label, other.label)
      else:
        return cmp(self.code, other.code)
    
    
    except:
      return - 1
    
class TurnusContainer (general.Container):
  
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
    
def load():
  """
  Loads and returns a container instance.
  """
  el = TurnusContainer (locations.TURNUS_DATA, Turnus.HEADERS)
  try:
    el.load()
  except Exception as e:
    print e
    pass
  return el
  
    
