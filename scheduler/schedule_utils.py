# -*- coding: Cp1250 -*-

"""
This file contains functions, that are used throughout the scheduling process.
"""
from utils import time_conversion, holiday
import weights

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

def is_valid_move (workplace, role, turnus, date, person, overtime):
  """
  Checks, if the person is allowed to work, on the combination of attributes.
    workplace: is the workplace checked
    role: is the role checked
    turnus: is the turnus checked
    date: is the date checked
    person: is the person checked
    overtime: if the overtime is allowed for the person
  """
  if turnus not in person.allowed_turnuses:
    return False
  
  if person.is_turnus_forbidden(turnus, date):
    return False
  
  if person.is_blocked(date, turnus):
    return False
  
  if holiday.is_workfree(date):
    # check if this a turnus, that can be scheduled in a workfree day
    if not turnus.holiday:
      return False
  else:
    if not turnus.workday:
      return False
  
  
  #check the role
  if role not in workplace.roles or workplace not in person.roles or role not in person.roles[workplace]:
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
  

def __get_heuristic_score(person, date):
  """
  Returns a value. The higher the value, the worst choice the person is.
    person: is the person, that will have the score computed
    date: is the date, that we want scheduled
    return: a float
  """
  
  month_hours          = -1 * person.get_monthly_hours_difference(date)
  week_hours           = -1 * person.get_weekly_hours_difference(date)
  turnus_dispersion    = person.get_turnus_dispersion()
  workplace_dispersion = person.get_workplace_dispersion()
  
  return weights.MONTH_HOURS * month_hours + weights.WEEK_HOURS * week_hours + weights.TURNUS_DISPERSION * turnus_dispersion + weights.WORKPLACE_DISPERSION * workplace_dispersion
  
