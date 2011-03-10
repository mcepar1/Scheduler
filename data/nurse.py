# -*- coding: Cp1250 -*-

from utils import translate
from data  import general, locations

import locale

class Nurse (general.DataClass):

  HEADERS = ["MAT. ŠTEV.", "IME", "PRIIMEK", "ROJSTNI DAN"]

  def __init__(self, work_id, name, surname, birthday, titles=None, employment_type=None):
    """
    This is the constructor.
      work_id: is the unique work id
      name: is the nurse's name
      surname: is the nurse's surname
      birthday: is the nurse's birthday
      titles: is a list of two lists. The first list contains the prefix titles, the second list contains suffix
              titles. Both are ordered.
      roles: is dictionary that maps workplaces to a set of roles that the has at the
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
      from data import employment_type
      
      try:
        self.employment_type = employment_type.load().get_all ( )[1]
      except:
        try:
          self.employment_type = employment_type.load().get_all ( )[0]
        except:
          raise Exception('V aplikaciji ni vrst zaposlitve.')
    
    # maps scheduling units, to the turnuses, that are allowed for the scheduling unit  
    self.scheduling_units_map = {}
      
  
  def as_data_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    return [self.work_id, self.name, self.surname, self.birthday]
    
  def as_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    return [translate (self.work_id), translate (self.name), translate (self.surname), translate (self.birthday)]
  
  def add_allowed_turnus(self, scheduling_unit, turnus):
    """
    Adds a new turnus, to the turnuses, that the person can work.
      @param scheduling_unit: the scheduling unit, that the person will work in the specified turnus
      @param turnus: the turnus that the person can work
    """
    if scheduling_unit not in self.scheduling_units_map:
      self.scheduling_units_map[scheduling_unit] = set ( )
    self.scheduling_units_map[scheduling_unit].add (turnus)
    
  def remove_allowed_turnus(self, scheduling_unit, turnus):
    """
    Removes a turnus, from the allowed turnuses.
      @param scheduling_unit: the scheduling unit, that the person will have the turnus removed
      @param turnus: the turnus, that will be removed
    """
    self.scheduling_units_map[scheduling_unit].remove (turnus)
    if not self.scheduling_units_map[scheduling_unit]:
      del self.scheduling_units_map[scheduling_unit]
      
    
  def is_turnus_allowed(self, scheduling_unit, turnus):
    """
    Checks, if the nurse can work in the specified turnus.
      @param scheduling_unit: the scheduling unit, that will be checked
      @param turnus: the turnus, that will be checked
      @return: true if she can, false otherwise
    """
    if scheduling_unit in self.scheduling_units_map:
      return turnus in self.scheduling_units_map[scheduling_unit]
    else:
      return False
    
  def get_allowed_turnuses(self, scheduling_unit):
    """
    Returns a list of turnuses, that this nurse can work in, for the specified scheduling unit.
      @param scheduling_unit: a data object
      @return: a list of Turnus objects
    """
    if scheduling_unit in self.scheduling_units_map:
      return sorted (self.scheduling_units_map[scheduling_unit])
    else:
      return []
    
    
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

      
  def set_employment_type(self, employment_type):
    """
    Set's the nurse's employment type.
      employment_type: is the employment type of this nurse
    """
    self.employment_type = employment_type
    self.allowed_turnuses = self.employment_type.allowed_turnuses
    
  def get_academic_name(self):
    """
    Returns an unicode object, representing the person's full academic name
    """
    prefixes_t, suffixes_t = self.get_titles ( )
    prefixes_s = []
    suffixes_s = []
    for title in prefixes_t:
      prefixes_s.append(str (title))
    for title in suffixes_t:
      suffixes_s.append(str (title))
      
    return str (u', '.join(prefixes_s) + u' ' + unicode (self) + u' ' + ', '.join(suffixes_s))
  
  def synchronize_data(self, *args):
    """
    This is used to keep the instances of the subclasses consistent. This method updates every internal
    attribute of the class, so that the matching objects are forced into the data structure. Look at the
    data model for more details. 
    """
    for data in args:
      #set the titles
      titles_l, titles_r = self.get_titles ( )
      if data in titles_l:
        titles_l[titles_l.index(data)] = data
      if data in titles_r:
        titles_r[titles_r.index(data)] = data
      self.set_titles(titles_l, titles_r)
      
              
      #set the employment type
      if self.employment_type == data:
        self.employment_type = data
        
      #set the scheduling units
      if data in self.scheduling_units_map:
        turnuses = self.scheduling_units_map[data]
        del self.scheduling_units_map[data]
        self.scheduling_units_map[data] = turnuses
        
      #set the turnuses
      for scheduling_unit in self.scheduling_units_map:
        if data in self.scheduling_units_map[scheduling_unit]:
          self.scheduling_units_map[scheduling_unit].remove (data)
          self.scheduling_units_map[scheduling_unit].add    (data)
        
  
  def __str__(self):
    return self.name + " " + self.surname
  
  def __hash__(self):
    return hash(str(self))
    
  def __eq__(self, other):
    return self.__cmp__(other) == 0
    
  def __cmp__(self, other):
    try:
      if not locale.strcoll(self.work_id, other.work_id):
        if not locale.strcoll(self.surname, other.surname):
          if not locale.strcoll(self.name, other.name):
            return cmp (self.birthday, other.birthday)
          else:
            return locale.strcoll (self.surname, other.surname)
        else:
          return locale.strcoll (self.surname, other.surname)
      else:
        return locale.strcoll (self.work_id, other.work_id)
    
    
    except:
      return - 1
    
def load ( ):
  """
  Loads and returns a container instance.
  """
  return general.load (locations.NURSES_DATA, Nurse)
    
