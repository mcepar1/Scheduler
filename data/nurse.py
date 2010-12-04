# -*- coding: utf-8 -*-

import cPickle as pickle
import os

from utils import time_conversion

class Nurse:

  HEADERS = ["MAT. STEV.", "IME", "PRIIMEK", "ROJSTNI DAN"]

  def __init__(self, work_id, name, surname, birthday, titles=None, roles=None, employment_type=None, workplaces=None):
    """
    This is the constructor.
      work_id: is the unique work id
      name: is the nurse's name
      surname: is the nurse's surname
      birthday: is the nurse's birthday
      titles: is a set of all the nurse's titles
      roles: is dictionary that maps workplaces a set of roles that the has at the
             workplace
      employment_type: is the employment type of the nurse
      workplaces: a sequence of workplaces, in which the nurse works
    """
    
    self.work_id = work_id 
    self.name = name
    self.surname = surname
    self.birthday = birthday
    
    if titles:
      self.titles = titles
    else:
      self.titles = set()
      
    if roles:
      self.roles = roles
    else:
      self.roles = dict()
    
    # tells if the night turnuses are scheduled in packages
    self.packet_night_turnuses = False
    
    # this field should never be changed directly
    # use set_employment_type instead
    if employment_type:
      self.set_employment_type(employment_type)
    else:
      # very rare case
      from data import employment_type
      
      try:
        self.employment_type = employment_type.load().employment_types[1]
      except:
        try:
          self.employment_type = employment_type.load().employment_types[0]
        except:
          raise Exception('V aplikaciji ni vrst zaposlitve.')
    
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
    
    # maps a date to a two tuple (turnus, worspace)
    # if a entry exists in this dict, it will be pre-scheduled    
    self.predefined = {}
      
    
  def as_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    return [self.work_id, self.name, self.surname, time_conversion.date_to_string(self.birthday)]
  
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
      
    self.remove_predefined(date)  
    self.forbidden_turnuses[date].add(turnus)
    
  def remove_invalid_turnus(self, date, turnus):
    """
    Removes a turnus form a list of forbidden turnuses
      date: is the date that does no allow the turnus
      turnus: is the invalid turnus
    """
    
    self.forbidden_turnuses[date].remove(turnus)
      
    if date in self.vacations:
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
    
    del self.vacations[date]
    self.forbidden_turnuses[date] = set()
      
    
  def add_workplace(self, workplace):
    """Adds a workplace to the nurse."""
    self.workplaces.add(workplace)
    self.roles[workplace] = set ()
    
  def remove_workplace(self, workplace):
    """Removes a workplace from the nurse"""
    self.workplaces.remove(workplace)
    # removing an unadded workplace should not be possible
    del self.roles[workplace]
    
    # do not forget to clean the predefined entries
    for date in self.predefined.keys():
      if self.predefined[date][1] == workplace:
        self.remove_predefined(date)

  def add_title(self, title):
    """Adds a title to the nurse."""
    self.titles.add(title)
    
  def remove_title(self, title):
    """Removes a title from the nurse."""
    # removing an un-added title should not be possible 
    self.titles.remove(title)
    
  def add_role(self, workplace, role):
    """Adds a role to the nurse"""
    self.roles[workplace].add(role)
    
  def remove_role(self, workplace, role):
    """Removes a role from the nurse."""
    # removing an un-added role should not be possible
    self.roles[workplace].remove(role)
    
  def add_predefined(self, date, turnus, workplace, role):
    """
    Adds a predefined date in the schedule.
      date: the date that will be added
      turnus: the turnus, that will be added
      workplace: the workplace, that will be added
      role: the role that will be added
    """
    self.predefined[date] = (turnus, workplace, role)
    
  def remove_predefined(self, date):
    """
    Removes the predefined date, if necessary.
      date: the date that will be removed
    """
    if date in self.predefined:
      del self.predefined[date]
      
  def is_predefined(self, date):
    """
    Checks, if the date is predefined.
      return: true, if predefined, false otherwise
    """
    return date in self.predefined

      
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
  
  def is_turnus_forbidden(self, turnus, date):
    """
    Checks, if the turnus is allowed for the specific date.
      turnus: is the checked turnus
      date: is the date checked
      return: true, if the turnus isn't allowed, false otherwise
    """
    
    if turnus not in self.allowed_turnuses:
      return True
    
    if date not in self.forbidden_turnuses:
      return False
    
    if turnus in self.forbidden_turnuses[date]:
      return True
    
    return False
    
    
  def __str__(self):
    return self.name + " " + self.surname
  
  def __hash__(self):
    return hash(str(self))
    
  def __eq__(self, other):
    return self.__cmp__(other) == 0
    
  def __cmp__(self, other):
    try:
      if self.work_id == other.work_id:
        if self.surname == other.surname:
          if self.name == other.name:
            return cmp (self.birthday, other.birthday)
          else:
            return cmp(self.name, other.name)
        else:
          return cmp(self.surname, other.surname)
      else:
        return cmp (self.work_id, other.work_id)
    
    
    except:
      return - 1
    
    
class NurseContainer:
  """Contains methods, that deal with multiple instances of the Nurse
  class at once (loading, saving, representing as a table, ...)"""
  
  FILES_DIR = os.path.join("persistence", "data")
  FILE_NAME = "nurses.dat"

  def __init__(self, nurses_list=None):
    """This is the constructor
    nurses_list: a list (or set) that contains instances of the Nurse class"""
    
    self.nurses = []
    
    if nurses_list:
      self.add_all(nurses_list)
      
  def add_all(self, nurses_list):
    """Adds all the elements of the nurses_list into the container
      nurses_list: a list that contains  instances of the Nurse class"""
      
    for nurse in nurses_list:
      for existing_nurse in self.nurses:
        if nurse.work_id == existing_nurse.work_id:
          raise Exception('Oseba z maticno stevilko ' + str(nurse.work_id) + ' ze obstaja.')
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
    
