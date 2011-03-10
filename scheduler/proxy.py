# -*- coding: Cp1250 -*-
"""
This file contains the classes and methods, that act as bridges between all application's layers.
"""
import workers
import locations

from utils import calendar_utils


def get_saved_schedules ( ):
  """
  Returns a list of saved schedules.
    @return: a list 2-tuples. The first value is the month's name, the second value is the year.
  """
  schedules = []
  for file in locations.FILES:
    month, year = file.split('.')[0].split ('_')
    schedules.append ((calendar_utils.get_month_name (int (month)), year))
  return schedules
    

def get_schedule_dates (date):
  """
  Return an ordered list of all dates, that the scheduler can reach for the given date.
    @param date: a datetime.date object. The day is not important
    @return: an ordered list of datetime.date objects
  """
  this_month_dates = calendar_utils.get_same_month_dates (date)
  
  # handles the cases that are needed for packet nights and holiday
  next_month_dates = calendar_utils.get_same_month_dates (calendar_utils.get_next_month (date))
  if this_month_dates[-1].weekday ( ) == 4:
    this_month_dates += next_month_dates[0:2]
  elif this_month_dates[-1].weekday ( ) == 0:
    this_month_dates.append (next_month_dates[0])
  elif this_month_dates[-1].weekday ( ) == 2:
    this_month_dates.append (next_month_dates[0])
  elif this_month_dates[-1].weekday ( ) == 5:
    this_month_dates.append (next_month_dates[0])
  
  return this_month_dates

"""
This class is a bridge between the data model, the GUI and the scheduling logic.
"""
class DataToSchedule:
  
  def __init__ (self, date, persons, schedule_units, turnus_types):
    """
    The default constructor.
      @param date:           the datetime.date object, that represents the scheduling date (day is not important)
      @param persons:        the data container object, that contains persons
      @param schedule_units: the data container object, that contains workplaces
      @param turnus_types:   the data container object, that contains turnus types
    """
    
    self.date           = date
    self.persons        = persons
    self.schedule_units = schedule_units
    self.turnus_types   = turnus_types
    self.workers        = workers.Workers(get_schedule_dates (self.date), self.schedule_units.get_all ( ), self.turnus_types.get_all ( ))
    
  def get_workers (self):
    """
    Returns the schedule workers.
      @return: a schedule Workers object
    """
    return self.workers
  
  def get_schedule_units_container (self):
    """
    Returns a list of schedule units.
      @return: a data container
    """
    return self.schedule_units
  
  def get_schedule_units (self):
    """
    Returns a list of schedule units.
      @return: a list of data objects
    """
    return self.schedule_units.get_all ( )

  def get_turnus_types (self):
    """
    Returns a list of turnus types.
      @return: a list of data objects
    """
    return self.turnus_types.get_all ( )
  
  def __get_date_string (self):
    """
    Returns the scheduling date, that this class handles:
      @return: a string
    """
    return calendar_utils.get_py_month_name (self.date) + ' ' + str (self.date.year)
  
  def __str__ (self):
    return self.__get_date_string ( )
    