# -*- coding: Cp1250 -*-
"""
This file contains the classes and methods, that act as bridges between all application's layers.
"""
import workers
import locations
import person_scheduler
import schedule_container
import person as person_module

from data import general, scheduling_unit
from utils import calendar_utils, time_conversion

import os
import copy
import datetime
import cPickle as pickle

def __exists (date):
  """
  Checks, if the saved schedule for the date exists.
    @param date: a datetime.date object
    @return: True, if exists, False otherwise
  """
  return __load_single (locations.get_file_path (date)) != None

def __load_single (path):
  """
  Loads and returns an existing scheduler, as specified by the path.
    @param path: a string
    @return: a proxy object, if the load was successful, None otherwise.
  """
  try:
    return pickle.load (file (path, 'rb'))
  except:
    return None
  
def __is_before (date1, date2):
  """
  Checks if the date1 is before date2, by the time stamp values of the files, that they represent.
    @param date1: a datetime.date object
    @param date2: a datetime.date object
    @return: True, if date1 is before date2, False, if the date2 is before date1
  """
  timestamp1 = datetime.datetime.fromtimestamp (os.path.getmtime (locations.get_file_path (date1)))
  timestamp2 = datetime.datetime.fromtimestamp (os.path.getmtime (locations.get_file_path (date2)))
  return timestamp1 < timestamp2

def __merge (proxy1, proxy2, date, merging_dates, all_dates):
  """
  Merges the two proxies into a new one. The people from the proxy1 override the ones proxy2, if their 
  schedules intersect.
    @param proxy1: a proxy object
    @param proxy2: a proxy object
    @param merging_dates: a list of dates in which the peoples schedule intersect.
    @param all_dates: a list of all valid dates
    @param date: a datetime.date object, that defines the scheduling object
    
    @return: a proxy object
  """
  people           = None
  schedule_units   = None
  turnus_types     = None
  workers          = None
  proxy            = None
  
  schedule_units, turnus_types, workers = __merge_common (proxy1, proxy2, date)
  people                                = __merge_people (proxy1.get_people ( ), proxy2.get_people ( ), date, merging_dates, all_dates)
  
  proxy = DataToSchedule (date, general.DataContainer ('', general.DataClass), schedule_units, turnus_types)
  proxy.set_people  (people)
  proxy.set_workers (workers)
  
  return proxy

def __merge_common (proxy1, proxy2, date):
  """
  Merges the base elements of the two proxies.
    @param proxy1: the first proxy object
    @param proxy2: the second proxy object
    @param date: the datetime.date object, that defines the new proxy' s scheduling date
    @return: 2 data containers and a workers object (scheduling units, turnus types and workers in the 
             specified order)
  """
  workers          = None
  scheduling_units = sorted (set (proxy1.get_scheduling_units ( )) | set (proxy2.get_scheduling_units ( )))
  turnus_types     = sorted (set (proxy1.get_turnus_types ( ))     | set (proxy2.get_turnus_types ( )))
  
  if proxy1.get_date ( ) == date:
    workers = proxy1.get_workers ( )  
  else:
    workers = proxy2.get_workers ( )
    
  scheduling_units = scheduling_unit.SchedulingUnitContainer ('', scheduling_units[0].__class__, scheduling_units)
  turnus_types     = general.DataContainer ('', turnus_types[0].__class__,     turnus_types)
  
  return scheduling_units, turnus_types, workers  
  
def __merge_people (people1, people2, date, merging_dates, all_dates):
  """
  Merges the two people lists according to the merging dates. When considering the merging dates, the first
  list of people takes priority, the rest in the rest of dates the second one takes priority.
    @param people1: a list of people
    @param people2: a list of people
    @param date: a datetime.date object, that defines the scheduling date
    @param merging_dates: a list of dates in which the peoples schedule intersect.
    @param all_dates: a list of all valid dates
    @return: a schedule container object
  """
  
  people = set ( )
  for person in set (people1) | set (people2):
    new_person = person_module.Nurse (person)
    if new_person in people2:
      new_person.overwrite (people2[people2.index (new_person)], all_dates)
    elif new_person in people1:
      new_person.overwrite (people1[people1.index (new_person)], all_dates)
      
    if new_person in people1 and new_person in people2:
      new_person.overwrite (people1[people1.index (new_person)], merging_dates)
      
    people.add (new_person)
      
  return schedule_container.ScheduleContainer (date, sorted (people))
      
  

def save (proxy, overwrite=False):
  """
  Saves the person scheduler. It does not overwrite an existing scheduler, unless told to do so.
    @param proxy: a proxy object
    @param overwrite: a boolean. Default value is set to False.
    @return: True, if the save was successful, False otherwise. 
  """
  save_object = proxy
  if overwrite:
    pickle.dump (save_object, file (locations.get_file_path (proxy.get_date ( )), 'wb'))
    return True
  elif not overwrite and os.path.exists (locations.get_file_path (proxy.get_date ( ))):
    return False
  else:
    pickle.dump (save_object, file (locations.get_file_path (proxy.get_date ( )), 'wb'))
    return True
  
def load (date):
  """
  Loads and returns an existing scheduler, as specified by the date. The scheduler is correctly merged with
  the previous and the next month. The merging priority is defined by the file's time stamp.
    @date:   a datetime.date object
    @return: a proxy object, if the load was successful, None otherwise.
  """
  
  prev_date = calendar_utils.get_previous_month (date)
  next_date = calendar_utils.get_next_month     (date)
  
  all_dates = sorted (set (calendar_utils.get_same_month_dates (prev_date)) | \
                      set (calendar_utils.get_same_month_dates (date))      | \
                      set (calendar_utils.get_same_month_dates (next_date))
                     )
  
  if __exists (date):
    curr_proxy = __load_single (locations.get_file_path (date))
    temp_proxy = None
  
    if __exists (prev_date):
      
      merging_dates = calendar_utils.get_same_month_dates (prev_date)
      prev_proxy = __load_single (locations.get_file_path (prev_date))
      
      if __is_before (prev_date, date):
        temp_proxy = __merge (prev_proxy, curr_proxy, curr_proxy.get_date ( ), merging_dates, all_dates)
      else:
        temp_proxy = __merge (curr_proxy, prev_proxy, curr_proxy.get_date ( ), merging_dates, all_dates)
    else:
      temp_proxy = curr_proxy
        
        
    if __exists (next_date):
      merging_dates = calendar_utils.get_same_month_dates (next_date)
      next_proxy = __load_single (locations.get_file_path (next_date))
      
      if __is_before (date, next_date):
        temp_proxy = __merge (next_proxy, temp_proxy, date, merging_dates, all_dates)
      else:
        temp_proxy = __merge (temp_proxy, next_proxy, date, merging_dates, all_dates)

    return temp_proxy
  else:
    return None

def get_saved_schedules ( ):
  """
  Returns a list of saved schedules.
    @return: a list 3-tuples. The first value is the month's name, the second value is the year and the third
             is the modification datetime.
  """
  schedules = []
  for path in locations.get_files ( ):
    month, year = os.path.split(path)[1].split('.')[0].split ('_')
    modified    = datetime.datetime.fromtimestamp (os.path.getmtime (path))
    schedules.append ((calendar_utils.get_month_name (int (month)), year, time_conversion.time_to_string (modified) + \
                                                                          ' ' + \
                                                                          time_conversion.date_to_string (modified)))
  schedules.sort (key=lambda x: x[2], reverse=True)
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
    self.persons        = self.__create_data_people (persons)
    self.schedule_units = schedule_units
    self.turnus_types   = turnus_types
    self.workers        = workers.Workers(get_schedule_dates (self.date), self.schedule_units.get_all ( ), self.turnus_types.get_all ( ))
    
  def get_date (self):
    """
    Returns the scheduling date. Day is not important.
      @return: a datetime.dat object
    """ 
    return self.date 
    
  def get_workers (self):
    """
    Returns the schedule workers.
      @return: a schedule Workers object
    """
    return self.workers
  
  def set_workers (self, workers):
    """
    Sets the workers.
      @param workers: a workers object
    """
    self.workers = workers
  
  def get_scheduling_units_container (self):
    """
    Returns a list of schedule units.
      @return: a data container
    """
    return self.schedule_units
  
  def get_scheduling_units (self):
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
    
  def get_scheduler (self):
    """
    Returns the scheduler object.
      @return: a person scheduler
    """
    ps = person_scheduler.PersonScheduler(self.__get_persons ( ), 
                                          self.__get_scheduling_units ( ), 
                                          self.get_date ( ),
                                          self.get_workers ( ))
    return ps
  
  def get_people (self):
    """
    Returns a list of people.
      @return: a list of people
    """
    return self.__get_persons ( )
  
  def set_people (self, people):
    """
    Sets the people, that are represented by this proxy object.
      @param people: a data container object
    """
    self.persons = people
    
  def __get_persons (self):
    """
    Returns a list of all data persons.
      @return: a list of data objects
    """
    return copy.deepcopy (self.persons.get_all ( ))
  
  def __get_scheduling_units (self):
    """
    Returns a list of all scheduling units.
      @return: a list of data objects
    """
    return self.schedule_units.get_all ( )   
  
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
    