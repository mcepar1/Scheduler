# -*- coding: Cp1250 -*-
"""
This file contains the classes and methods, that act as bridges between all application's layers.
"""
import workers
import locations
import global_vars
import person_scheduler
import schedule_container
import person as person_module

from utils  import calendar_utils, time_conversion

import os
import copy
import datetime
import cPickle as pickle

CREATE_BLANK = 0
CREATE_NEW   = 1
LOAD_EXACT   = 2
LOAD_MERGE   = 3

def __merge_people (curr_people, prev_people, next_people):
  """
  Adds the date dependant fields into the curr_people.
    @param curr_people: a list of data objects
    @param prev_people: a list of data objects
    @param next_people: a list of data objects
    @return: a list of data objects
  """
  for curr_person in curr_people:
    for prev_person in prev_people:
      if curr_person == prev_person:
        curr_person.merge (prev_person)
        break

    for next_person in next_people:
      if curr_person == next_person:
        curr_person.merge (next_person)
        break
      
  return curr_people
  

def __exists (date):
  """
  Checks, if a schedule with the date already exists.
    @param date: a datetime.date object with the correct month and year
    @return: True, if exists, False othewise
  """
  return os.path.exists (locations.get_file_path (date))

def __load_neighbours (curr_state):
  """
  Loads neigbours of the current state, but the schedule of the current state itself is not loaded.
    @param curr_state: a proxy object
    @return: a proxy object
  """  
  prev_date = calendar_utils.get_previous_month (curr_state.get_date ( ))
  next_date = calendar_utils.get_next_month (curr_state.get_date ( ))
  
  prev_proxy = None
  curr_proxy = curr_state
  next_proxy = None
  
  if __exists (prev_date):
    prev_proxy = pickle.load (file (locations.get_file_path (prev_date), 'rb'))
  else:
    prev_proxy = DataToSchedule (prev_date, curr_proxy.get_people_container ( ), curr_proxy.get_scheduling_units_container ( ), curr_proxy.get_turnus_types_container ( ), False)
    
  if __exists (next_date):
    next_proxy = pickle.load (file (locations.get_file_path (next_date), 'rb'))
  else:
    next_proxy = DataToSchedule (next_date, curr_proxy.get_people_container ( ), curr_proxy.get_scheduling_units_container ( ), curr_proxy.get_turnus_types_container ( ), False)
    
  prev_people = prev_proxy.get_people ( )
  curr_people = curr_proxy.get_people ( )
  next_people = next_proxy.get_people ( )
  
  saved_people = __merge_people (curr_people, prev_people, next_people)
  curr_proxy.set_people (schedule_container.ScheduleContainer (curr_proxy.get_date ( ), saved_people))
    
  return curr_proxy

def __load (date, curr_state=None):
  """
  Loads the proxy for the specified date.
    @param date: a datetime.date object with the correct day and month
    @param curr_state: the current state of the application proxy object. If this one is set, all the loaded
                       data will merge into this proxy. Default is set to None.
    @return: a proxy object
  """
  prev_date = calendar_utils.get_previous_month (date)
  curr_date = date
  next_date = calendar_utils.get_next_month (date)
  
  prev_proxy = None
  curr_proxy = pickle.load (file (locations.get_file_path (curr_date), 'rb'))
  next_proxy = None
  
  
  if curr_state:
    temp_people = curr_state.get_people ( )
    load_people = curr_proxy.get_people ( )
    merg_people = __merge_people(temp_people, load_people, [])
    curr_state.set_people (schedule_container.ScheduleContainer (curr_proxy.get_date ( ), merg_people))
    curr_proxy = curr_state
  
  if __exists (prev_date):
    prev_proxy = pickle.load (file (locations.get_file_path (prev_date), 'rb'))
  else:
    prev_proxy = DataToSchedule (prev_date, curr_proxy.get_people_container ( ), curr_proxy.get_scheduling_units_container ( ), curr_proxy.get_turnus_types_container ( ), False)
    
  if __exists (next_date):
    next_proxy = pickle.load (file (locations.get_file_path (next_date), 'rb'))
  else:
    next_proxy = DataToSchedule (next_date, curr_proxy.get_people_container ( ), curr_proxy.get_scheduling_units_container ( ), curr_proxy.get_turnus_types_container ( ), False)
    
  prev_people = prev_proxy.get_people ( )
  curr_people = curr_proxy.get_people ( )
  next_people = next_proxy.get_people ( )
  
  saved_people = __merge_people (curr_people, prev_people, next_people)
  curr_proxy.set_people (schedule_container.ScheduleContainer (curr_proxy.get_date ( ), saved_people))
    
  return curr_proxy
  
def create_proxy (date, type):
  """
  Returns creates and returns a proxy object.
    @param date: a datetime.date object, for which the proxy will be created
    @param type: one of the following constants:
                   CREATE_BLANK: creates a completely new schedule from the current data state
                   CREATE_NEW:   creates a completely new schedule from the current data state, but loads the neighbouring months
                   LOAD_EXACT:   loads a schedule, in the exact state when it was last saved
                   LOAD_MERGE:   loads a schedule, merges it into the current application state and copies the dates 
    @return: a proxy object
  """
  if   type == CREATE_BLANK: 
    return DataToSchedule (date, global_vars.get_nurses ( ), global_vars.get_scheduling_units ( ), global_vars.get_turnus_types ( ))
  elif type == CREATE_NEW:
    return __load_neighbours (DataToSchedule (date, global_vars.get_nurses ( ), global_vars.get_scheduling_units ( ), global_vars.get_turnus_types ( )))
  elif type == LOAD_EXACT:
    return __load (date)
  elif type == LOAD_MERGE:
    return __load (date, DataToSchedule (date, global_vars.get_nurses ( ), global_vars.get_scheduling_units ( ), global_vars.get_turnus_types ( )))
  else:
    raise Exception ('Unsupported creation type')
  

def save (proxy, overwrite=False):
  """
  Saves the proxy. It does not overwrite any file, unless told to do so. 
    @param proxy: a proxy object
    @param overwrite: overwrites any file, if set to True, does not overwrite anything, if set to False
    @return: True if the proxy was saved, False otherwise
  """
  prev_date = calendar_utils.get_previous_month (proxy.get_date ( ))
  curr_date = proxy.get_date ( )
  next_date = calendar_utils.get_next_month (proxy.get_date ( ))
  
  if not overwrite and (__exists (prev_date) or __exists (curr_date) or __exists (next_date)):
    return False
  else:
    prev_proxy = proxy.get_month_clone (prev_date)
    curr_proxy = proxy.get_month_clone (curr_date)
    next_proxy = proxy.get_month_clone (next_date)
    
    pickle.dump (prev_proxy, file (locations.get_file_path (prev_date), 'wb'))
    pickle.dump (curr_proxy, file (locations.get_file_path (curr_date), 'wb'))
    pickle.dump (next_proxy, file (locations.get_file_path (next_date), 'wb'))
    
    return True
  

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
  
  def __init__ (self, date, persons, schedule_units, turnus_types, full_scope=True):
    """
    The default constructor.
      @param date:           the datetime.date object, that represents the scheduling date (day is not important)
      @param persons:        the data container object, that contains persons
      @param schedule_units: the data container object, that contains workplaces
      @param turnus_types:   the data container object, that contains turnus types
      @param full_scope:     a boolean. If set to True, the neighbouring months will also be created (default).
    """
    
    self.date           = date
    self.persons        = self.__create_data_people (persons, full_scope)
    self.schedule_units = schedule_units
    self.turnus_types   = turnus_types
    self.workers        = workers.Workers(get_schedule_dates (self.date), self.schedule_units.get_all ( ), self.turnus_types.get_all ( ))
    
  def get_date (self):
    """
    Returns the scheduling date. Day is not important.
      @return: a datetime.dat object
    """ 
    return self.date
  
  def set_date (self, date):
    """
    Sets the scheduling date.
      @param date: a datetime.date object
    """
    self.date = date
    
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
  
  def get_turnus_types_container (self):
    """
    Returns a list of turnus types.
      @return: a data container
    """
    return self.turnus_types

  def get_turnus_types (self):
    """
    Returns a list of turnus types.
      @return: a list of data objects
    """
    return self.turnus_types.get_all ( )
  
  def get_turnuses (self):
    """
    Returns a list of all turnuses in this proxy object.
      @return: a list of data objects
    """
    turnuses = set ( )
    for schedule_unit in self.schedule_units.get_all ( ):
      turnuses |= set (schedule_unit.get_allowed_turnuses ( ))
      for person in self.persons.get_all ( ):
        turnuses |= set (person.get_allowed_turnuses (schedule_unit))
    return sorted (turnuses)
        
    
  def get_scheduler (self):
    """
    Returns the scheduler object.
      @return: a person scheduler
    """
    ps = person_scheduler.PersonScheduler(self.persons.get_all ( ), 
                                          self.__get_scheduling_units ( ), 
                                          self.get_date ( ),
                                          self.get_workers ( ))
    return ps
  
  def get_people_container (self):
    """
    Return a result container.
      @return: a schedule container object
    """
    return self.persons
  
  def get_people (self):
    """
    Returns a list of people.
      @return: a list of people
    """
    return self.__get_persons ( )
  
  def set_people (self, people):
    """
    Sets the people, that are represented by this proxy object.
      @param people: a schedule container object
    """
    self.persons = people
    
  def get_exportable (self):
    """
    Returns the persons, formated for the exporter.
      @return: a map
    """
    return self.persons.get_exportable ( )
    
  def get_month_clone (self, date):
    """
    Creates a copy of this proxy, but only with the dates associated with the given month.
      @param date: a datetime.date object, with the correct month and year
      @return: a proxy object
    """
    person_container = schedule_container.ScheduleContainer (date)
    proxy            = DataToSchedule (date, person_container, self.get_scheduling_units_container ( ), self.turnus_types)
    
    #create the persons
    for person in self.persons.get_all ( ):
      person_container.add_all ([person.get_month_clone (date)])  
      
    proxy.set_people  (person_container)
    
    if date == self.get_date ( ):
      proxy.set_workers (self.get_workers ( ))
      
    
    return proxy
  
  def merge (self, proxy):
    """
    Merges the proxy into this one. All the date dependant fields that may appear in both proxies are 
    overwritten by the given proxy.
      @param proxy: an object of this class 
    """
    self.date = proxy.date
    
    for schedule_unit in proxy.get_scheduling_units ( ):
      if schedule_unit not in self.get_scheduling_units ( ):
        self.schedule_units.add_all ([schedule_unit])
        
    for turnus_type in proxy.get_turnus_types  ( ):
      if turnus_type not in self.turnus_types.get_all ( ):
        self.turnus_types.add_all ([turnus_type])
    
    self.workers = proxy.get_workers ( )
    
    for person in proxy.get_people ( ):
      if person not in self.get_people ( ):
        self.persons.add_all ([person])
      else:
        for originial_person in self.get_people ( ):
          if originial_person == person:
            originial_person.merge (person)
    
    
    
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
  
  def __create_data_people (self, people, full_scope):
    """
    Returns a data container, with the scheduler's data model people.
      @param people: a data container object
      @param full_scope: a boolean. If set to True, the scheduler people will also have the neighbouring months
                         appended to the list of possible dates.
      @return: a data container object
    """
    scheduler_people = []
    dates            = []
    
    if full_scope:
      dates = calendar_utils.get_same_month_dates (calendar_utils.get_previous_month (self.date)) + \
              calendar_utils.get_same_month_dates (self.date) + \
              calendar_utils.get_same_month_dates (calendar_utils.get_next_month (self.date))
    else:
      dates = calendar_utils.get_same_month_dates (self.date)
      
    for person in people.get_all ( ):
      scheduler_people.append (person_module.Nurse (person))
      scheduler_people[-1].add_dates (dates)
    
    return schedule_container.ScheduleContainer (self.get_date ( ), elements_list=scheduler_people)
  
  def __str__ (self):
    return self.__get_date_string ( )
    