# -*- coding: Cp1250 -*-

from Scheduler.utils import time_conversion, translate
from Scheduler.data  import general, locations

class Nurse:

  HEADERS = ["MAT. ŠTEV.", "IME", "PRIIMEK", "ROJSTNI DAN"]

  def __init__(self, work_id, name, surname, birthday, titles=None, roles=None, employment_type=None, workplaces=None):
    """
    This is the constructor.
      work_id: is the unique work id
      name: is the nurse's name
      surname: is the nurse's surname
      birthday: is the nurse's birthday
      titles: is a list of two lists. The first list contains the prefix titles, the second list contains suffix
              titles. Both are ordered.
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
      self.titles = [[],[]]
      
    if roles:
      self.roles = roles
    else:
      self.roles = dict()
    
    # tells if the night turnuses are scheduled in packages
    self.packet_night_turnuses = False
    
    # tells if the nurse only works in weekedays and morning shifts
    self.week_morning = False
    
    # this field should never be changed directly
    # use set_employment_type instead
    if employment_type:
      self.set_employment_type(employment_type)
    else:
      # very rare case
      from Scheduler.data import employment_type
      
      try:
        self.employment_type = employment_type.load().get_all ( )[1]
      except:
        try:
          self.employment_type = employment_type.load().get_all ( )[0]
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
      
  
  def as_data_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    return [self.work_id, self.name, self.surname, self.birthday]
    
  def as_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    return [translate (self.work_id), translate (self.name), translate (self.surname), translate (self.birthday)]
  
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
    
    if date in self.forbidden_turnuses:
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

  def get_titles(self):
    """
    Returns two lists. The first is an ordered list of prefix titles, the second is an ordered list of suffix
    titles.
    return: two lists
    """
    
    return self.titles[0], self.titles[1]
  
  def set_titles(self, prefixes, suffixes):
    """
    Sets the person's titles.
      prefixes: an ordered list of prefix titles
      suffixes: an ordered list of suffix titles
    """
    self.titles[0] = prefixes
    self.titles[1] = suffixes 
    
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
    
  def get_academic_name(self):
    """
    Returns an unicode object, representing the person's full academic name
    """
    prefixes_t, suffixes_t = self.get_titles ( )
    prefixes_s = []
    suffixes_s = []
    for title in prefixes_t:
      prefixes_s.append(unicode (title))
    for title in suffixes_t:
      suffixes_s.append(unicode (title))
      
    return unicode (u', '.join(prefixes_s) + u' ' + unicode (self) + u' ' + ', '.join(suffixes_s))
    
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
    
def load():
  """
  Loads and returns a container instance.
  """
  el = general.Container(locations.NURSES_DATA, Nurse.HEADERS)
  try:
    el.load()
  except Exception as e:
    print e
    pass
  return el
    
