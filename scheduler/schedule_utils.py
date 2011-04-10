# -*- coding: Cp1250 -*-

"""
This file contains functions, that are used throughout the scheduling process.
"""
from utils import time_conversion, holiday, calendar_utils
import weights
import locations

import random
"""
This class contains various maps, that ease attribute access throughout the scheduling process.
"""
class Mapper:
  
  def __init__ (self, people, scheduling_units):
    """
    The default constructor.
    """
    
    self.people           = people
    self.scheduling_units = scheduling_units
    
    #maps scheduling units to people
    self.scheduling_units_to_people = {}
    for scheduling_unit in self.scheduling_units:
      self.scheduling_units_to_people[scheduling_unit] = set ( )
      for person in self.people:
        if person.has_scheduling_unit (scheduling_unit):
          self.scheduling_units_to_people[scheduling_unit].add (person)
        
    #maps employment types to people
    self.employment_type_people = {}
    for person in self.people:
      if person.employment_type not in self.employment_type_people:
        self.employment_type_people[person.employment_type] = set ( )
      self.employment_type_people[person.employment_type].add (person)
      
    #maps turnuses to people
    self.turnus_people = {}
    for scheduling_unit in self.scheduling_units:
      for turnus in scheduling_unit.get_allowed_turnuses ( ):
        for person in self.people:
          if person.is_turnus_allowed (scheduling_unit, turnus):
            if turnus not in self.turnus_people:
              self.turnus_people[turnus] = set ( )
            self.turnus_people[turnus].add(person)
            
  
  def get_all_people (self):
    """
    Returns a set of all people.
      @return: a set of data objects
    """
    return set (self.people)
  
  def get_overtime_people (self):
    """
    Returns all people, that can work in overtime.
      @return: a set of data objects
    """
    people= set ( )
    for employment_type in self.employment_type_people:
      if employment_type.has_overtime ( ):
        people |= self.employment_type_people[employment_type]
    return people

  def get_no_overtime_people (self):
    """
    Returns all people, that cannot work in overtime.
      @return: a set of data objects
    """
    return set (self.people) - self.get_overtime_people ( )
  
  def get_scheduling_unit_people (self, scheduling_unit):
    """
    Returns a set of all people, that can work in the scheduling unit.
      @param scheduling_unit: a data object
      @return: a set of data objects
    """
    return self.scheduling_units_to_people[scheduling_unit]
  
  def get_turnus_people (self, turnus):
    """
    Returns a set of all people, that can work in the given turnus.
      @param turnus: a data object
      @return: a set of data objects
    """
    return self.turnus_people[turnus]
  
  def get_turnuses (self, scheduling_unit=None, person=None):
    """
    Returns a set of all turnuses, that the person and the scheduling unit can have (intersection). If one of
      the parameters is not given, it only checks the given one.
      @param scheduling_unit: a data object - default is None
      @param person: a data object - default is None
      @return: a set of data objects
    """
    if not scheduling_unit and not person:
      return set ( )
    elif scheduling_unit and person:
      return set (person.get_allowed_turnuses (scheduling_unit)) & set (scheduling_unit.get_allowed_turnuses ( ))
    elif scheduling_unit:
      return set (scheduling_unit.get_allowed_turnuses ( ))
    elif person:
      return set (person.get_allowed_turnuses ( ))
  
  def get_scheduling_units (self):
    """
    Returns a set of all scheduling units, that have at least one person, that can work in them.
      @return: a set of data objects
    """
    return set (self.scheduling_units_to_people.keys ( ))
  
  
  
def remove_schedule (date):
  """
  Permanently deletes a schedule.
    @param date: a datetime.date object. Day parameter is unimportant.
  """
  locations.delete_schedule (date)

def goes_into_overtime (person, date, turnuses):
  """
  Checks if the combined turnuses go into overtime.
    person: the person beeing checked
    date: a datetime.date object
    turnuses: a list of data objects
    return: true, if it goes into overtime, flase otherwise
  """
  mh = person.get_monthly_hours_difference (date)
  wh = person.get_weekly_hours_difference (date)
  
  duration = 0
  for turnus in turnuses:
    duration += time_conversion.timedelta_to_hours (turnus.duration)
  
  if mh - duration < 0:
    return True
  if wh - duration < 0:
    return True
  return False

def is_valid_move (scheduling_unit, turnus, date, person, overtime):
  """
  Checks, if the person is allowed to work, on the combination of attributes.
    @param scheduling_unit: is the scheduling_unit checked
    @param turnus: is the turnus checked
    @param date: is the date checked
    @param person: is the person checked
    @param overtime: if the overtime is allowed for the person
    @return: True, if the move is valid, False otherwise
  """
  if not person.is_turnus_allowed (scheduling_unit, turnus):
    return False
  
  if person.is_turnus_forbidden(date, turnus):
    return False
  
  if person.is_blocked(date, turnus):
    return False
  
  if holiday.is_workfree(date):
    # check if this a turnus, that can be scheduled in a workfree day
    if not turnus.holiday:
      return False
    
    #check for free days
    #check previous week
    week = calendar_utils.get_previous_week( date)
    for date_ in week:
      if person.is_free_day (date_):
        break
    else:
      #if there was no free day the previous week, perhaps there is in the next
      week = calendar_utils.get_next_week (date)
      for date_ in week:
        if person.is_free_day(date_):
          break
      else:
        # no free day was found
        return False
        
  else:
    if not turnus.workday:
      return False
  
  
  #also check the people's employment type
  if not overtime or not person.employment_type.has_overtime:
    return not goes_into_overtime (person, date, [turnus])
  
  return True
  
def get_heuristic_sorted_people(people, date):
  """
  Returns a sorted list of people, according to their heuristic score.
    people: the list of people, to be sorted
    date: the date that we want scheduled
    return: a list of people
  """
  
  temp   = {}
  result = []
  
  for person in people:
    heuristic_score = __get_heuristic_score(person, date)
    if heuristic_score not in temp:
      temp[heuristic_score] = []
    temp[heuristic_score].append(person)
    
  for heuristic_score in sorted(temp.keys ( )):
    result += temp[heuristic_score]
    
  return result

def add_free_day (person, date):
  """
  Adds a free day to the person, if necessary. See the person.Person.is_free_day_for 
  details.
    @param person: a data object
    @param date: a datetime.date object, that contains the week in which the person worked on a work
                 free day
  """
  
  #check previous week
  week = calendar_utils.get_previous_week (date)
  for date_ in week:
    if person.is_free_day(date_):
      return
  else:
    #if there was no free day the previous week, perhaps there is in the next
    week = calendar_utils.get_next_week(date)
    free_day = []
    for date_ in week:
      if person.is_free_day(date_) and not person.is_scheduled(date_):
        free_day.append(date_)
    
    if free_day:
      # add a random not yet scheduled day as a free day
      person.add_free_day (random.choice(free_day))
    else:
      raise Exception('Nisem mogel dodati prostega dneva.')
  

def get_alerady_scheduled_by_type (mapper, scheduling_unit, types, date):
  """
  Return the number of currently scheduled people for the specific types
  date and scheduling_unit.
    @param mapper: a mapper object
    @param scheduling_unit: is the scheduling unit 
    @param types: is the sequence of types
    @param date: is the date
    @return: the minimum amount of scheduled turnuses for any of the given types
  """
  #TODO: remove global vars
  map = {}
  import global_vars
  for type in types:
    turnuses = global_vars.get_turnuses ( ).get_by_type(type, scheduling_unit)
    map[type] = 0
    for turnus in turnuses:
      map[type] += __get_already_scheduled(mapper, scheduling_unit, turnus, date)
    
  return min (map.values ( ))

def __get_heuristic_score(person, date):
  """
  Returns a value. The higher the value, the worst choice the person is.
    person: is the person, that will have the score computed
    date: is the date, that we want scheduled
    return: a float
  """
  
  month_hours          = -1 * person.get_monthly_hours_difference(date)
  week_hours           = -1 * person.get_weekly_hours_difference(date)
  turnus_dispersion    = person.get_turnus_dispersion ( )
  workplace_dispersion = person.get_scheduling_unit_dispersion ( )
  
  return weights.MONTH_HOURS * month_hours + weights.WEEK_HOURS * week_hours + weights.TURNUS_DISPERSION * turnus_dispersion + weights.WORKPLACE_DISPERSION * workplace_dispersion

def __get_already_scheduled (mapper, scheduling_unit, turnus, date):
  """
  Returns the number of currently scheduled people, for the specific turnus, 
  date and scheduling unit.
    @param mapper: a mapper object
    @param scheduling_unit: is the scheduling unit
    @param turnus: is the turnus
    @param date: is the date
    @return: the number of people
  """
  
  number = 0
  for person in mapper.get_all_people ( ):
    if person.is_scheduled_exact(scheduling_unit, turnus, date):
      number += 1
  
  return number
  
