# -*- coding: Cp1250 -*-
"""
This file contains the classes and methods, that act as bridges between all application's layers.
"""
import workers
import locations
import person_scheduler
import person as person_module

from utils import calendar_utils

import os
import cPickle as pickle

def save (person_scheduler, overwrite=False):
  """
  Saves the person scheduler. It does not overwrite an existing scheduler, unless told to do so.
    @param person_scheduler: a person_scheduler object
    @param overwrite: a boolean. Default value is set to False.
    @return: True, if the save was successful, False otherwise. 
  """
  if overwrite:
    pickle.dump (person_scheduler, file (locations.get_file_path (person_scheduler.get_date ( )), 'wb'))
    return True
  elif not overwrite and os.path.exists (locations.get_file_path (person_scheduler.get_date ( ))):
    return False
  else:
    pickle.dump (person_scheduler, file (locations.get_file_path (person_scheduler.get_date ( )), 'wb'))
    return True
  
def load (date):
  """
  Loads and returns an existing scheduler, as specified by the date.
    @date:   a datetime.date object
    @return: a person scheduler object, if the load was successful, None otherwise.
  """
  try:
    return pickle.load (file (locations.get_file_path (date), 'rb'))
  except:
    return None

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
  
  def __init__ (self, load, date, persons, schedule_units, turnus_types):
    """
    The default constructor.
      @param load:           the boolean, that tells, if we are trying to load an existing schedule or creating a new one
      @param date:           the datetime.date object, that represents the scheduling date (day is not important)
      @param persons:        the data container object, that contains persons
      @param schedule_units: the data container object, that contains workplaces
      @param turnus_types:   the data container object, that contains turnus types
    """
    
    self.load           = load
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
  
  def get_scheduling_units_container (self):
    """
    Returns a list of schedule units.
      @return: a data container
    """
    return self.schedule_units

  def get_turnus_types (self):
    """
    Returns a list of turnus types.
      @return: a list of data objects
    """
    return self.turnus_types.get_all ( )
  
  def save (self, person_scheduler, overwrite):
    """
    Saves the target person scheduler.
      @param person_scheduler: a person scheduler object
      @param overwrite: a boolean, that defines if we are allowed to overwrite an existing file. If it set 
             to True, we can overwrite.
      @return: True, if the save was successful, False otherwise
    """
    return save  (person_scheduler, overwrite)
    
  def get_scheduler (self):
    """
    Returns the scheduler object.
      @return: a person scheduler
    """
    if self.load:
      ps = load (self.__get_date ( ))
    else:
      ps = person_scheduler.PersonScheduler(self.__get_persons ( ), 
                                            self.__get_scheduling_units ( ), 
                                            self.__get_date ( ),
                                            self.get_workers ( ))
    return ps
    
  def __get_persons (self):
    """
    Returns a list of all data persons.
      @return: a list of data objects
    """
    return self.__create_data_people (self.persons).get_all ( )
  
  def __get_scheduling_units (self):
    """
    Returns a list of all scheduling units.
      @return: a list of data objects
    """
    return self.schedule_units.get_all ( )
  
  def __get_date (self):
    """
    Returns the scheduling date. Day is not important.
      @return: a datetime.dat object
    """ 
    return self.date    
  
  def __get_date_string (self):
    """
    Returns the scheduling date, that this class handles:
      @return: a string
    """
    return calendar_utils.get_py_month_name (self.date) + ' ' + str (self.date.year)
  
  def __create_data_people (self, people):
    """
    Returns a data container, with the scheduler's data model people.
      @param people: a data container object
      @return: a data container object
    """
    scheduler_people = []
    dates = calendar_utils.get_same_month_dates (calendar_utils.get_previous_month (self.date)) + \
            calendar_utils.get_same_month_dates (self.date) + \
            calendar_utils.get_same_month_dates (calendar_utils.get_next_month (self.date))
    for person in people.get_all ( ):
      scheduler_people.append (person_module.Nurse (person))
      scheduler_people[-1].add_dates (dates)
    
    from data import general, nurse
    return general.DataContainer ('', nurse.Nurse, elements_list=scheduler_people)
  
  def __str__ (self):
    return self.__get_date_string ( )
    