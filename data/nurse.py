# -*- coding: utf-8 -*-

import cPickle as pickle
import os

class Nurse:

  HEADERS = ["IME", "PRIIMEK"]

  def __init__(self,name,surname):
    """This is the constructor.
      name: is the nurse's name
      surname: is the nurse's surname
     """
     
    self.name = name
    self.surname = surname
    
    # this dictionary maps sates to a set of turnuses
    # if a date maps to a set that contains a turnus,
    # the turnus is considered to be an invalid move
    self.forbidden_turnuses = {}
    
    # almost identical to forbidden_turnuses
    self.vacations = {}
    
  def as_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    return [self.name, self.surname]
    
  def add_invalid_turnus(self,date,turnus):
    """
    Adds a turnus to a list of forbidden turnuses
      date: is the date that does not allow the turnus
      turnus: is the invalid turnus
    """
    
    
    if date not in self.forbidden_turnuses:
      self.forbidden_turnuses[date] = set()
      
    self.forbidden_turnuses[date].add(turnus)
    
  def remove_invalid_turnus(self,date,turnus):
    """
    Removes a turnus form a list of forbidden turnuses
      date: is the date that does no allow the turnus
      turnus: is the invalid turnus
    """
    try:
      self.forbidden_turnuses[date].remove(turnus)
    except KeyError as e:
      # this should not be possible
      # pass
      # TODO: check if this holds
      raise e
      
    
    
  def add_vacation(self,date,vacation):
    """
    Adds a vacation to the vacation list
      date: is the date, that the nurse will be on vacation
      vacation: is the vacation instance
    """
    
    # TODO: synchronize with the forbidden_turnuses
    
    if date in self.vacations:
      # TODO: check if this holds
      raise Exception("Več kot dve vrsti dopusta na isti dan?")
      
    self.vacations[date] = set([vacation])
    
    
  def remove_vacation(self,date,vacation):
    """
    Removes a vacation from the list.
      date: is the date of the vacation
      vacation: is the type of the vacation
    """
    try:
      # Assuming that only one vacation per day is possible
      # TODO: check if this is true
      del self.vacations[date]
    except KeyError as e:
      # this should not be possible
      # pass
      # TODO: check if this holds
      raise e
    
    
  def __str__(self):
    return self.name + " " + self.surname
    
  def __eq__(self,other):
    return self.__cmp__(other) == 0
    
  def __cmp__(self,other):
    try:
      if self.surname == other.surname:
        if self.name == other.name:
          return 0
        else:
          return cmp(self.name, other.name)
      else:
        return cmp(self.surname, other.surname)
    
    
    except:
      return -1
    
    
class NurseContainer:
  """Contains methods, that deal with multiple instences of the Nurse
  class at once (loading, saving, representing as a table, ...)"""
  
  FILES_DIR = os.path.join("data","persistence")
  FILE_NAME = "nurses.dat"

  def __init__(self, nurses_list = None):
    """This is the constructor
    nurses_list: a list (or set) that contains instances of the Nurse class"""
    
    self.nurses = []
    
    if nurses_list:
      self.add_all(self, nurses_list)
      
  def add_all(self, nurses_list):
    """Adds all the elements of the nurses_list into the container
      nurses_list: a list that contains  instances of the Nurse class"""
      
    for nurse in nurses_list:
      self.nurses.append(nurse)
 
  def save(self):
    """Saves the current state into an external file."""
    pickle.dump(self.nurses, file(os.path.join(NurseContainer.FILES_DIR, NurseContainer.FILE_NAME),'wb'))
    
  def load(self):
    """Loads the contens from the external file. The current state is LOST!!!!"""
    self.nurses = pickle.load(file(os.path.join(NurseContainer.FILES_DIR, NurseContainer.FILE_NAME),'rb'))
    
  def as_table(self):
    """Returns a table-like representation of self.
      return: a dictionary with two string keys:
        header: a list that contains headers of the table:
        items: a list of lists. The external list represents rows and the intrenal one represents columns within a single row."""
        
    
    rows_list = []
    for nurse in self.nurses:
      rows_list.append(nurse.as_list())
    
    table = {}
    table['header'] = Nurse.HEADERS  
    table['items'] = rows_list
   
    return table
    
  def get_element(self, index):
    """Returns the nurse at the specified index.
      index: index of the nurse
    """
    
    # TODO: verify, that the self.nurses and the GUI table always match indexes
    return self.nurses[index]
    
  def __str__(self):
    return ", ".join([str(nurse) for nurse in self.nurses])
    
