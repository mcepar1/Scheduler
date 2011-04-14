# -*- coding: Cp1250 -*-

from data import locations, general
from utils import translate

class SchedulingUnit (general.DataClass):
  
  HEADERS = ["DELOVIŠČE", "VLOGA"]
  
  def __init__ (self, workplace, role):
    """
    The default constructor.
      @param workplace: a data object
      @param role: a data object
    """
    general.DataClass.__init__ (self)
    
    self.workplace = workplace
    self.role      = role
    
    #A RGB color. Needed for coloring the background in the schedule output.
    self.__color     = (255, 255, 255)
    
    # if the turnus is located in the set, the workplace allows that turnus
    self.allowed_turnuses = set ()
    
  def as_data_list(self):
    """
    Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable.
    """
    
    return [self.workplace, self.role]
    
  def as_list(self):
    """
    Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable.
    """
    
    return [translate (self.workplace), translate (self.role)]
  
  def synchronize_data(self, *args):
    """
    This is used to keep the instances of the subclasses consistent. This method updates every internal
    attribute of the class, so that the matching objects are forced into the data structure. Look at the
    data model for more details. 
    """
    for data in args:
      if data == self.workplace:
        self.workplace = data
      if data == self.role:
        self.role = data
      if data in self.allowed_turnuses:
        self.remove_allowed_turnus (data)
        self.add_allowed_turnus (data)
        
  def add_allowed_turnus (self, turnus):
    """
    Adds a turnus to the allowed turnuses.
      turnus: is the new allowed turnus
    """
    self.allowed_turnuses.add (turnus)
    
  def remove_allowed_turnus (self, turnus):
    """
    Removes a turnus from the allowed turnuses.
      turnus: the turnus, that will be allowed
    """
    self.allowed_turnuses.remove (turnus)
    
  def is_allowed_turnus (self, turnus):
    """
    Checks, if it is possible to schedule the turnus into this workplace.
      @param turnus: the a data object
      @return true, if it possible, false otherwise
    """
    return turnus in self.allowed_turnuses
  
  def get_turnus_types (self):
    """
    Returns a list of all the contained turnus types.
      @return: a set of turnus types
    """
    
    turnus_types = set ( )
    for turnus in self.allowed_turnuses:
      turnus_types |= turnus.types
      
    return sorted (turnus_types)
  
  def get_workplace (self):
    """
    Returns this unit's workplace.
      @return: a data object
    """
    return self.workplace
  
  def has_workplace (self, workplace):
    """
    Checks, if the scheduling unit has the specific workplace.
      @param workplace: a data object
      @return: true if it has, false otherwise
    """
    return workplace == self.workplace
  
  def get_role (self):
    """
    Returns this unit's role.
      @return: a data object
    """
    return self.role

  def has_role (self, role):
    """
    Checks, if the scheduling unit has the specific role.
      @param role: a data object
      @return: true if it has, false otherwise
    """
    return role == self.role
  
  def get_allowed_turnuses (self):
    """
    Returns a list of all turnuses.
      @return: a set of data objects
    """
    return self.allowed_turnuses
  
  def has_holiday_rule (self):
    """
    Checks if the scheduling unit's workplace has the holiday rule.
      @return: True if it has, False otherwise
    """
    return self.get_workplace ( ).has_holiday_rule ( )
  
  def get_color (self):
    """
    Returns the scheduling unit's color.
      @return: a RGB tuple (3-tuple)
    """
    return self.__color
  
  def set_color (self, color):
    """
    Sets the scheduling unit's color.
      @param color: a RGB tuple (3-tuple)
    """
    self.__color = color
  
  def __str__ (self):
    return str (self.workplace) + ' - ' + str (self.role)
    
  def __hash__ (self):
    return hash (str(self))
    
  def __eq__ (self, other):
    return self.__cmp__(other) == 0
  
  def __cmp__ (self, other):
    try:
      if not cmp (self.workplace, other.workplace):
        return cmp (self.role, other.role)
      else:
        return cmp (self.workplace, other.workplace)  
    except:
      return - 1

"""
This class adds some utility methods to the standard Data class.
"""
class SchedulingUnitContainer (general.DataContainer):
      
  def get_workplaces (self):
    """
    Returns an ordered list of workplaces.
      @return: an ordered list of data objects
    """
    workplaces = []
    for unit in self.elements:
      if unit.get_workplace ( ) not in workplaces:
        workplaces.append (unit.get_workplace ( ))
    return workplaces
  
  def get_roles (self, workplace=None):
    """
    Returns an ordered list of roles.
      @param workplace: returns only the roles associated with this workplace (data object), if given
      @return: an ordered list of data objects
    """
    roles = []
    if workplace:
      for unit in self.elements:
        if unit.get_role ( ) not in roles and unit.get_workplace ( ) == workplace:
          roles.append (unit.get_role ( ))
    else:
      for unit in self.elements:
        if unit.get_role ( ) not in roles:
          roles.append (unit.get_role ( ))
    return roles
  
  def get_scheduling_unit (self, workplace, role):
    """
    Returns the scheduling unit, that is represented by the two parameters.
      @param workplace: a workplace data object
      @param role: a role data object
      @return: a scheduling unit data object, None if there is no match
    """
    for unit in self.elements:
      if unit.has_workplace (workplace) and unit.has_role (role):
        return unit
    return None
    
def load ( ):
  """
  Loads and returns a container instance.
  """
  return general.load (locations.SCHEDULE_UNIT_DATA, SchedulingUnit, container_class=SchedulingUnitContainer)

