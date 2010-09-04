# -*- coding: utf-8 -*-

import cPickle as pickle
import os

class Turnus:
  
  HEADERS = ["OZNAKA", "TIP DELA", "ZACETEK", "KONEC", "TRAJANJE", "BLOKADA", "NA PROST DAN"]
  
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
      for type in turnus_types.turnus_types:
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
    
class TurnusContainer:
  """Contains methods, that deal with multiple instences of the Turnus
  class at once (loading, saving, representing as a table, ...)"""
  
  FILES_DIR = os.path.join("persistence", "data")
  FILE_NAME = "turnus.dat"
  
  def __init__(self, turnus_list=None):
    """This is the constructor
    turnus_list: a list (or set) that contains instances of the Turnus class"""
    
    self.turnuses = []
    
    if turnus_list:
      self.add_all(turnus_list)
        
  def add_all(self, turnus_list):
    """Adds all the elements of the turnus_list into the container
      turnus_list: a list that contains  instances of the Turnus class"""
      
    for turnus in turnus_list:
        self.turnuses.append(turnus)
  
  def save(self):
    """Saves the current state into an external file."""
    pickle.dump(self.turnuses, file(os.path.join(TurnusContainer.FILES_DIR, TurnusContainer.FILE_NAME), 'wb'))
    
  def load(self):
    """Loads the contens from the external file. The current state is LOST!!!!"""
    self.turnuses = pickle.load(file(os.path.join(TurnusContainer.FILES_DIR, TurnusContainer.FILE_NAME), 'rb'))
    
  def as_table(self):
    """Returns a table-like representation of self.
      return: a dictionary with two string keys:
        header: a list that contains headers of the table:
        items: a list of lists. The external list represents rows and the intrenal one represents columns within a single row."""
        
    
    rows_list = []
    for turnus in self.turnuses:
      rows_list.append(turnus.as_list())
    
    table = {}
    table['header'] = Turnus.HEADERS  
    table['items'] = rows_list
   
    return table
  
  def get_element(self, index):
    """Returns the turnus at the specified index.
      index: index of the turnus
    """
    
    # TODO: verify, that the self.workplaces and the GUI table always match indexes
    return self.turnuses[index]
  
  def get_by_type(self, type, workplace=None):
    """
    Returns a set of turnuses, that belong to a specific type.
      type: is the turnus type
      workplace: if this attribute is given, the method return all the turnuses
                 that belong to the specific type and are allowed for the workplace
      return: a set of turnuses
    """
    turnuses = set()
    for turnus in self.turnuses:
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
  el = TurnusContainer()
  try:
    el.load()
  except Exception as e:
    print e
    pass
  return el
  
    
