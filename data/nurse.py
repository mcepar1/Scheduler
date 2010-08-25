# -*- coding: utf-8 -*-

import cPickle as pickle
import os

class Nurse:

  HEADERS = ["IME", "PRIIMEK", "NAZIV", "ROJSTNI DAN"]

  def __init__(self, name, surname, title, birthday, employment_type=None, workplaces=None):
    """
    This is the constructor.
      name: is the nurse's name
      surname: is the nurse's surname
      title: is the nurse's title
      birthday: is the nurse's birthday
      employment_type: is the employment type of the nurse
    """
     
    self.name = name
    self.surname = surname
    self.title = title
    self.birthday = birthday
    
    # this field should never be changed directly
    # use set_employment_type instead
    if employment_type:
      self.set_employment_type(employment_type)
    else:
      # very rare case
      from data import employment_type
      self.employment_type = employment_type.load().employment_types[0]
    
    # contains all turnuses, that the person can use  
    self.allowed_turnuses = self.employment_type.allowed_turnuses
    
    # this dictionary maps dates to a set of turnuses
    # if a date maps to a set that contains a turnus,
    # the turnus is considered to be an invalid move
    self.forbidden_turnuses = {}
    
    # almost identical to forbidden_turnuses
    self.vacations = {}
    
    # on which workplaces the nurse works
    self.workplaces = set ()
    if workplaces:
      for workplace in workplaces:
        self.add_workplace(workplace)
      
    
  def as_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    return [self.name, self.surname, self.title, self.birthday]
  
  def add_allowed_turnus(self, turnus):
    """
    Adds a new turnus, to the turnuses, that the person can work.
      turnus: is the new allowed turnus
    """
    self.allowed_turnuses.add(turnus)
    
  def remove_allowed_turnus(self, turnus):
    """
    Removes a turnus, from the allowed turnuses.
      turnus: the turnus, that will be removed
    """
    self.allowed_turnuses.remove(turnus)
    
  def add_invalid_turnus(self, date, turnus):
    """
    Adds a turnus to a list of forbidden turnuses
      date: is the date that does not allow the turnus
      turnus: is the invalid turnus
    """
    
    
    if date not in self.forbidden_turnuses:
      self.forbidden_turnuses[date] = set()
      
    self.forbidden_turnuses[date].add(turnus)
    
  def remove_invalid_turnus(self, date, turnus):
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
      
    if date in self.vacations:
      # TODO assuming only one vacation per day
      del self.vacations[date]
      
    
    
  def add_vacation(self, date, vacation):
    """
    Adds a vacation to the vacation list
      date: is the date, that the nurse will be on vacation
      vacation: is the vacation instance
    """
    
    self.forbidden_turnuses[date] = set(self.get_allowed_turnuses())
    
    self.vacations[date] = set([vacation])
    
    
  def remove_vacation(self, date, vacation):
    """
    Removes a vacation from the list.
      date: is the date of the vacation
      vacation: is the type of the vacation
    """
    try:
      # Assuming that only one vacation per day is possible
      # TODO: check if this is true
      del self.vacations[date]
      self.forbidden_turnuses[date] = set()
      
    except KeyError as e:
      # this should not be possible
      # pass
      # TODO: check if this holds
      raise e
    
  def add_workplace(self, workplace):
    """Adds a workplace to the nurse."""
    self.workplaces.add(workplace)
    
  def remove_workplace(self, workplace):
    """Removes a workplace from the nurse"""
    self.workplaces.remove(workplace)
      
  def set_employment_type(self, employment_type):
    """
    Set's the nurse's employment type.
      employment_type: is the employment type of this nurse
    """
    self.employment_type = employment_type
    self.allowed_turnuses = self.employment_type.allowed_turnuses
      
  def get_allowed_turnuses(self):
    """
    Returns a list of turnuses, that this nurse can attain.
      return: a list of Turnus objects
    """
  
    return self.allowed_turnuses
    
    
  def __str__(self):
    return self.name + " " + self.surname
    
  def __eq__(self, other):
    return self.__cmp__(other) == 0
    
  def __cmp__(self, other):
    try:
      if self.surname == other.surname:
        if self.name == other.name:
          if self.title == other.title:
            return cmp (self.birthday, other.birthday)
          else:
            return cmp(self.title, other.title)
        else:
          return cmp(self.name, other.name)
      else:
        return cmp(self.surname, other.surname)
    
    
    except:
      return - 1
    
    
class NurseContainer:
  """Contains methods, that deal with multiple instences of the Nurse
  class at once (loading, saving, representing as a table, ...)"""
  
  FILES_DIR = os.path.join("data", "persistence")
  FILE_NAME = "nurses.dat"

  def __init__(self, nurses_list=None):
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
    pickle.dump(self.nurses, file(os.path.join(NurseContainer.FILES_DIR, NurseContainer.FILE_NAME), 'wb'))
    
  def load(self):
    """Loads the contens from the external file. The current state is LOST!!!!"""
    self.nurses = pickle.load(file(os.path.join(NurseContainer.FILES_DIR, NurseContainer.FILE_NAME), 'rb'))
    
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
    
def load():
  """
  Loads and returns a container instance.
  """
  el = NurseContainer()
  try:
    el.load()
  except Exception as e:
    print e
    pass
  return el
    
