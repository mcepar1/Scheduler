# -*- coding: Cp1250 -*-
"""
This file contains the proxy between the GUI and the schedule workers.
"""
from utils import calendar_utils

"""
The proxy class. The responsibility to manage dates is handled outside the scope of this class.
"""
class Workers:
  
  def __init__(self, dates, schedule_units, turnus_types):
    """
    The default constructor.
      @param dates: a list of datetime.date objects
      @param schedule_units: a list of data objects
      @param turnus_types: a list data objects
    """
    
    self.all_dates     = dates
    self.holiday_dates = set ( )
    self.manual_dates  = {}
    
    for date in self.all_dates:
      for holiday in calendar_utils.get_workfree_dates (date):
        if holiday <= self.all_dates[-1]:
          self.holiday_dates.add (holiday)
    self.holiday_dates = sorted (self.holiday_dates)
    
    self.work_day_workers = {}
    self.holiday_workers  = {}
    self.manual_workers   = {}
    
    self.__build_dict(self.work_day_workers, dates, schedule_units, turnus_types)
    self.__build_dict(self.holiday_workers,  dates, schedule_units, turnus_types)
    self.__build_dict(self.manual_workers,   dates, schedule_units, turnus_types)
    
    self.__build_manual(dates, schedule_units)
    

  def add_worday_dates (self, schedule_unit, turnus_type, workers):
    """
    Adds a work day date into the container.
      @param schedule_unit: a data object
      @param turnus_type: a data object
      @param workers: the number of workers
    """
    for date in self.all_dates:
      self.work_day_workers[date][schedule_unit][turnus_type] = workers
    
  def add_holiday_dates (self, schedule_unit, turnus_type, workers):
    """
    Adds a holiday date into the container.
      @param schedule_unit: a data object
      @param turnus_type: a data object
      @param workers: the number of workers
    """
    for date in self.holiday_dates:
      self.holiday_workers[date][schedule_unit][turnus_type] = workers
    
  def add_manual_date (self, date, schedule_unit, turnus_type_workers):
    """
    Adds a holiday date into the container.
      @param date: a datetime.date object
      @param schedule_unit: a data object
      @param turnus_type_workers: a map that maps turnus types (data objects) into the number of workers
    """
    for turnus_type in turnus_type_workers:
      self.manual_workers[date][schedule_unit][turnus_type] = turnus_type_workers[turnus_type]
    self.manual_dates[date][schedule_unit] = True
    
  def remove_manual_date (self, date, schedule_unit):
    """
    Removes a manually added  date from the container.
      @param date: a list of datetime.date objects
      @param schedule_unit: a data object
    """
    for turnus_type in self.manual_workers[date][schedule_unit]:
      self.manual_workers[date][schedule_unit][turnus_type] = 0
    self.manual_dates[date][schedule_unit] = False
    
  def is_date_manual (self, date, schedule_unit):
    """
    Checks, if the specified date was tampered manually.
      @param schedule_unit: a data object
      @return: true, if it was, false otherwise
    """
    return  self.manual_dates[date][schedule_unit]

  def get_range (self):
    """
    Returns the minimum and maximum date, that is valid for this workers object.
      @return: a 2-tuple: the first element is the minimum datetime.date object, the second is the maximum
        datetime.date object
    """
    return (min (self.all_dates), max (self.all_dates))
  
  def get_dates (self):
    """
    Returns an ordered list of all valid dates for this object.
      @return: an ordered list of datetime.date objects
    """
    return sorted (self.all_dates)
  
  def get_workers (self, date, schedule_unit, turnus_type):
    """
    Return the amount of workers for the specified parameters.
      @param date: a datetime.date object
      @param schedule_unit: a data object
      @param turnus_type: a data object
      @return: the number of workers
    """
    return self.get_manual_date_workers (schedule_unit, turnus_type, date)
  
  def get_manual_date_workers (self, schedule_unit, turnus_type, date):
    """
    Gets the amount of workers at the given date. 
      @param schedule_unit: a data object
      @param turnus_type: a data object
      @param date: a datetime.date object
      @return: the amount of workers in the specified data
    """
    if self.manual_workers[date][schedule_unit][turnus_type]:
      return self.manual_workers[date][schedule_unit][turnus_type]
    elif date in self.holiday_dates:
      return self.holiday_workers[date][schedule_unit][turnus_type]
    else:
      return self.work_day_workers[date][schedule_unit][turnus_type]
    
  
  def get_workday_workers (self, schedule_unit, turnus_type):
    """
    Returns the amount of work day workers for the specified data.
      @param schedule_unit: a data object
      @param turnus_type: a data object
      @return: the amount of workers in the specified data
    """
    for date in self.all_dates:
      return self.work_day_workers[date][schedule_unit][turnus_type]
      
  
  def get_holiday_workers (self, schedule_unit, turnus_type):
    """
    Returns the amount of holiday workers for the specified data.
      @param schedule_unit: a data object
      @param turnus_type: a data object
      @return: the amount of workers in the specified data
    """
    for date in self.holiday_dates:    
      return self.holiday_workers[date][schedule_unit][turnus_type]
    
  def get_workers_by_type (self, date, scheduling_unit, turnus):
    """
    Returns the amount of workers for the specified turnus, date and scheduling unit.
    The final amount is defined as the maximum value of turnus types.
      @param date: a datetiem.date object.
      @param scheduling_unit: a data object
      @param turnus: a data object
    """
    workers = set ([0])
    for turnus_type in turnus.types:
      workers.add (self.get_workers (date, scheduling_unit, turnus_type))
    return max (workers)
    
  
  def __build_dict (self, dict, dates, schedule_units, turnus_types, value = 0):
    """
    Creates the map.
      @param dates: a list of datetime.date objects
      @param schedule_units: a list of data objects
      @param turnus_types: a list of data objects
      @param value: the value that will be assigned to all of the elements. The default value is 0.
    """
    for date in dates:
      dict[date] = {}
      for schedule_unit in schedule_units:
        dict[date][schedule_unit] = {}
        for turnus_type in turnus_types:
          dict[date][schedule_unit][turnus_type] = value
            
  def __build_manual (self, dates, schedule_units, value=False):
    """
    Construct a map, that memorizes, which dates have been manually edited.
      @param dates: a list of datetime.date objects
      @param schedule_units: a list of data objects
      value: the value that will be assigned to all of the elements. The default value is false.
    """
    for date in dates:
      self.manual_dates[date] = {}
      for schedule_unit in schedule_units:
        self.manual_dates[date][schedule_unit] = value

