# -*- coding: Cp1250 -*-
"""
This file contains the proxy between the GUI and the schedule workers.
"""
from utils import calendar_utils

"""
The proxy class. The responsibility to manage dates is handled outside the scope of this class.
"""
class Workers:
  
  def __init__(self, dates, workplaces, roles, turnus_types):
    
    self.all_dates     = dates
    self.holiday_dates = set ( )
    self.manual_dates  = {}
    
    for date in dates:
      for holiday in calendar_utils.get_workfree_dates (date):
        self.holiday_dates.add (holiday)
    self.holiday_dates = sorted (self.holiday_dates)
    
    self.work_day_workers = {}
    self.holiday_workers  = {}
    self.manual_workers   = {}
    
    self.__build_dict(self.work_day_workers, dates, workplaces, roles, turnus_types)
    self.__build_dict(self.holiday_workers,  dates, workplaces, roles, turnus_types)
    self.__build_dict(self.manual_workers,   dates, workplaces, roles, turnus_types)
    
    self.__build_manual(dates, workplaces, roles)
    

  def add_worday_dates (self, workplace, role, turnus_type, workers):
    """
    Adds a work day date into the container.
      workplace: a data object
      role: a data object
      turnus_type: a data object
      workers: the number of workers
    """
    for date in self.all_dates:
      self.work_day_workers[date][workplace][role][turnus_type] = workers
    
  def add_holiday_dates (self, workplace, role, turnus_type, workers):
    """
    Adds a holiday date into the container.
      workplace: a data object
      role: a data object
      turnus_type: a data object
      workers: the number of workers
    """
    for date in self.holiday_dates:
      self.holiday_workers[date][workplace][role][turnus_type] = workers
    
  def add_manual_date (self, date, workplace, role, turnus_type_workers):
    """
    Adds a holiday date into the container.
      dates: a datetime.date object
      workplace: a data object
      role: a data object
      turnus_type_workers: a map that maps turnus types (data objects) into the number of workers
    """
    for turnus_type in turnus_type_workers:
      self.manual_workers[date][workplace][role][turnus_type] = turnus_type_workers[turnus_type]
    self.manual_dates[date][workplace][role] = True
    
  def remove_manual_date (self, date, workplace, role):
    """
    Removes a manually added  date from the container.
      dates: a list of datetime.date objects
      workplace: a data object
      role: a data object
    """
    for turnus_type in self.manual_workers[date][workplace][role]:
      self.manual_workers[date][workplace][role][turnus_type] = 0
    self.manual_dates[date][workplace][role] = False
    
  def is_date_manual (self, date, workplace, role):
    """
    Checks, if the specified date was tampered manually.
      return: true, if it was, false otherwise
    """
    return  self.manual_dates[date][workplace][role]

  def get_range (self):
    """
    Returns the minimum and maximum date, that is valid for this workers object.
      return: a 2-tuple: the first element is the minimum datetime.date object, the second is the maximum
        datetime.date object
    """
    return (min (self.all_dates), max (self.all_dates))
    
  def get_all (self):
    """
    Returns all workers, ordered by date priority.
      return: a dictionary, that maps:
        dates to workplaces
        workplaces to roles
        roles to turnus types
        turnus types to the number of workers
    """
    raise Exception ('Implement!')
  
  def get_manual_date_workers (self, workplace, role, turnus_type, date):
    """
    Gets the amount of workers at the given date. 
      workplace: a data object
      role: a data object
      turnus_type: a data object
      date: a datetime.date object
      return: the amount of workers in the specified data
    """
    if self.manual_workers[date][workplace][role][turnus_type]:
      return self.manual_workers[date][workplace][role][turnus_type]
    elif date in self.holiday_dates:
      return self.holiday_workers[date][workplace][role][turnus_type]
    else:
      return self.work_day_workers[date][workplace][role][turnus_type]
    
  
  def get_workday_workers (self, workplace, role, turnus_type):
    """
    Returns the amount of work day workers for the specified data.
      date: a datetime.date object
      workplace: a data object
      role: a data object
      turnus_type: a data object
      return: the amount of workers in the specified data
    """
    for date in self.all_dates:
      return self.work_day_workers[date][workplace][role][turnus_type]
      
  
  def get_holiday_workers (self, workplace, role, turnus_type):
    """
    Returns the amount of holiday workers for the specified data.
      date: a datetime.date object
      workplace: a data object
      role: a data object
      turnus_type: a data object
      return: the amount of workers in the specified data
    """
    for date in self.holiday_dates:    
      return self.holiday_workers[date][workplace][role][turnus_type]
    
  def convert (self, workplace):
    """
    Converts this instance into the current workers-workplace relation.
      return: the map, that maps dates into the roles into the turnus types.
    """
    #TODO: remove this
    map = {}
    for date in self.all_dates:
      map[date] = {}
      for role in self.work_day_workers[date][workplace]:
        map[date][role] = {}
        for turnus_type in self.work_day_workers[date][workplace][role]:
          if self.manual_dates[date][workplace][role]:
            map[date][role][turnus_type] = self.manual_workers[date][workplace][role][turnus_type]
          elif date in self.holiday_dates:
            map[date][role][turnus_type] = self.holiday_workers[date][workplace][role][turnus_type]
          else:
            map[date][role][turnus_type] = self.work_day_workers[date][workplace][role][turnus_type]
            
    return map
    
  
  def __build_dict (self, dict, dates, workplaces, roles, turnus_types, value = 0):
    """
    Creates the map.
      dates: a list of datetime.date objects
      workplaces: a list of data objects
      roles: a list of data objects
      turnus_type: a list of data objects
      value: the value that will be assigned to all of the elements. The default value is 0.
    """
    for date in dates:
      dict[date] = {}
      for workplace in workplaces:
        dict[date][workplace] = {}
        for role in roles:
          dict[date][workplace][role] = {}
          for turnus_type in turnus_types:
            dict[date][workplace][role][turnus_type] = value
            
  def __build_manual (self, dates, workplaces, roles, value=False):
    """
    Construct a map, that memorizes, which dates have been manually edited.
      dates: a list of datetime.date objects
      workplaces: a list of data objects
      roles: a list of data objects
      value: the value that will be assigned to all of the elements. The default value is false.
    """
    for date in dates:
      self.manual_dates[date] = {}
      for workplace in workplaces:
        self.manual_dates[date][workplace] = {}
        for role in roles:
          self.manual_dates[date][workplace][role] = value
            
# A debug level method
def get_workers ( ):
  import datetime
  from utils import calendar_utils
  
  import global_vars
  
  dates = calendar_utils.get_same_month_dates (datetime.date.today ( ))
  dates += calendar_utils.get_same_month_dates (calendar_utils.get_next_month(datetime.date.today ( )))
  
  return Workers (dates, 
                  global_vars.get_workplaces ( ).get_all ( ), 
                  global_vars.get_roles ( ).get_all ( ), 
                  global_vars.get_turnus_types ( ).get_all ( )
                  )

