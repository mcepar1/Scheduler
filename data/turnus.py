# -*- coding: utf-8 -*-

import cPickle as pickle
import os

class Turnus:
  
  HEADERS = ["OZNAKA", "TIP DELA", "ZACETEK", "KONEC", "TRAJANJE", "BLOKADA", "NA PROST DAN"]
  
  def __init__(self,code,label,start,end,duration,blockade, holiday):
    """
    This is the constructor.
      code: is the code of the turnus (D,P,N, ...)
      label: is the label of the turnus (eno izmensko, ...)
      start: is the starting time
      end: is the ending time
      duration: is the length of the shift (start - end)
      blockade: how long after the end of the shift, the person cannot perform tasks
      holiday: if true, the turnus can be scheduled an a holiday
    """
  
  
    self.code = code
    self.label = label
    self.start = start
    self.end = end
    self.duration = duration
    self.blockade = blockade    
    self.holiday = holiday
    
  def as_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    return [self.code, self.label, self.start.strftime("%H:%M"), self.end.strftime("%H:%M"), str(self.duration), str(self.blockade), str(self.holiday)]
    
  def __str__(self):
    return self.code + " - " + self.label
    
  def __hash__(self):
    return hash(str(self))
    
  def __eq__(self,other):
    return self.__cmp__(other) == 0
    
  def __cmp__(self,other):
    try:
      if self.code == other.code:
        if self.label == other.label:
          if self.start == other.start:
            if self.end == other.end:
              return 0
            else:
              return cmp(self.end,other.end)
          else:
            return cmp(self.start,other.start)
        else:
          return cmp(self.name, other.name)
      else:
        return cmp(self.code, other.code)
    
    
    except:
      return -1
    
class TurnusContainer:
  """Contains methods, that deal with multiple instences of the Turnus
  class at once (loading, saving, representing as a table, ...)"""
  
  FILES_DIR = os.path.join("persistence", "data")
  FILE_NAME = "turnus.dat"
  
  def __init__(self, turnus_list = None):
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
    pickle.dump(self.turnuses, file(os.path.join(TurnusContainer.FILES_DIR, TurnusContainer.FILE_NAME),'wb'))
    
  def load(self):
    """Loads the contens from the external file. The current state is LOST!!!!"""
    self.turnuses = pickle.load(file(os.path.join(TurnusContainer.FILES_DIR, TurnusContainer.FILE_NAME),'rb'))
    
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
  
    
