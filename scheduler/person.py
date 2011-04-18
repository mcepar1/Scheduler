# -*- coding: Cp1250 -*-

from data import nurse, turnus, vacation

from utils.time_conversion import timedelta_to_hours
from utils.holiday import is_holiday
from utils import calendar_utils
from scheduler import constants

import datetime
import math

class Nurse (nurse.Nurse):
  
  FREE_DAY_SIGN = 'This is a free day'

  def __init__(self, data_nurse):
    """
    The default constructor
      data_nurse: an instance of the data.nurse.Nurse class
    """
      
    nurse.Nurse.__init__(self, data_nurse.work_id, data_nurse.name, data_nurse.surname, data_nurse.birthday, data_nurse.titles, data_nurse.employment_type)
    
    self.scheduling_units_map = data_nurse.scheduling_units_map
    self.week_morning = data_nurse.week_morning
    self.packet_night_turnuses = data_nurse.packet_night_turnuses
    
    # if a turnus is not allowed to be scheduled (maps dates to a set of turnuses)
    self.forbidden_turnuses = {}
    
    #this field maps a date to the turnus
    self.scheduled_turnus = {}
    #this field maps a date to the scheduling_unit
    self.scheduled_scheduling_unit = {}
    
  def add_dates (self, dates):
    """
    Adds a new month into this scheduler.
      @param dates: a list of datetime.date objects
    """

    for date in dates:
      if date not in self.scheduled_turnus and date not in self.scheduled_scheduling_unit:
        self.scheduled_turnus[date] = ''
        self.scheduled_scheduling_unit[date] = ''
        
  def get_dates (self):
    """
    Returns all the dates of this nurse.
      @return: an list sorted list of dates.
    """
    return sorted (set (self.scheduled_scheduling_unit.keys ( )) | set (self.scheduled_turnus.keys ( )))
        
    
  def schedule_turnus (self, date, turnus, scheduling_unit):
    """
    Schedules a new turnus.
      @param date: is the date of the turnus
      @param turnus: is the turnus
      @param scheduling_unit: is the scheduling unit. An empty string if none.
    """
    
    
    if self.scheduled_turnus[date] or self.scheduled_scheduling_unit[date]:
      raise Exception("Trying to override an already scheduled date")
        
    
    self.scheduled_turnus[date]          = turnus
    self.scheduled_scheduling_unit[date] = scheduling_unit
    
  def is_blocked (self, date, turnus):
    """
    Checks, if the following can be scheduled for the specific date.
      date: is the date that we want to insert
      turnus: is the turnus that we want to schedule
      return: true, if it is blocked, false otherwise
    """
    
    if self.is_scheduled(date):
      return True
    else:
      prev_date = date - datetime.timedelta(days=1)
      next_date = date + datetime.timedelta(days=1)
      if self.is_free_day(prev_date) and self.is_free_day(next_date):
        return False
      else:
        if not self.is_free_day(prev_date):
          prev_turnus = self.scheduled_turnus[prev_date]
          #calculate blocking next free date
          instance = datetime.datetime (year=prev_date.year, month=prev_date.month, day=prev_date.day)
          prev_turnus_start = instance.combine (prev_date, prev_turnus.start)
          prev_turnus_end   = prev_turnus_start + prev_turnus.duration
          next_allowed      = prev_turnus_end   + prev_turnus.blockade
            
          current_start = instance.combine(date, turnus.start)
          if next_allowed < current_start:
            return False
        if self.__can_be_scheduled (next_date):
          #check if there is a hard-coded date in the next-date
          if self.scheduled_turnus[next_date]:
            next_turnus = self.scheduled_turnus[next_date]
            next_start = instance.combine(next_date, next_turnus.start)
          else:
            next_start = datetime.datetime(day=1, month=1, year=3000)
            
          instance = datetime.datetime(year=date.year, month=date.month, day=date.day)
          this_turnus_start =  instance.combine(date, turnus.start)
          this_turnus_end   =  this_turnus_start + turnus.duration
          next_allowed      =  this_turnus_end   + turnus.blockade
                     
          
          if next_allowed > next_start:
            return False
    
    return True
    
    
  def is_scheduled (self, date):
    """
    Checks if the date is already scheduled. The date is considered scheduled, if it
    has a turnus, a vacation or a specifically marked free day.
      date: the date checked
      return: true, if scheduled, false otherwise
    """
    
    if self.scheduled_turnus[date] or self.scheduled_scheduling_unit[date]:
      return True
    else:
      return False
    
    
  def is_scheduled_exact (self, scheduling_unit, turnus, date):
    """
    Checks if the combination is scheduled.
      @param scheduling_unit: is the scheduling unit, that is checked
      @param turnus: is the turnus that is checked
      @param date: is date for against the turnus, workplace and role are checked
      @return: true if they are scheduled, false otherwise
    """
        
    return self.scheduled_turnus[date] == turnus and self.scheduled_scheduling_unit[date] == scheduling_unit
    
  def add_free_day (self, date):
    """
    Adds a free day in the schedule. This is not a vacation! This is the a legal 
    requirement.
      date: is the date of the free day
    """
    
    if self.scheduled_turnus[date] or self.scheduled_scheduling_unit[date]:
      raise Exception('Ta dan ne more biti prost')
      
    self.scheduled_turnus[date] = Nurse.FREE_DAY_SIGN
    
  def is_vacation (self, date):
    """
    Checks if the date is a vacation.
      date: is the date being checked
      return: true, if the date is a vacation, false otherwise
    """
    
    if date in self.scheduled_turnus:
      return isinstance(self.scheduled_turnus[date], vacation.Vacation)
    else:
      return False
    
  def is_free_day (self, date):
    """
    Checks if the date is a free day. A free day is: a vacation, a specifically
    marked free day, a yet unscheduled date or the persons birthday.
      date: is the date checked
      return: true, if the day is free, false otherwise
    """
    if date == self.birthday:
      return True
    elif date in self.scheduled_turnus or date in self.scheduled_scheduling_unit:
      if  not isinstance(self.scheduled_turnus[date], turnus.Turnus):
        return True
      else:
        return False
    else:
      return True
    
    
  def get_turnus_dispersion (self):
    """Calculates and returns the entropy of the turnuses."""
    
    raw_data = {}
    total_turnuses = 0.0
    entropy = 0.0
    
    for turnus in self.allowed_turnuses:
      raw_data[turnus] = 0.0
      
    for _, turnus in self.scheduled_turnus.items():
      # check if it is a turnus or a vacation
      if turnus in raw_data:
        raw_data[turnus] += 1.0
        total_turnuses += 1.0
    
    if total_turnuses == 0:
      #no turnuses - no dispersion
      return 0.0    
    
    for _, occuernces in raw_data.items():
      p = occuernces / total_turnuses
      if p:    
        entropy += (-1.0 * p * math.log(p, 2))
      else:
        entropy += 0.0
      
    return entropy
  
  def get_scheduling_unit_dispersion (self):
    """Calculates and returns the entropy of the scheduling units."""
    
    raw_data               = {}
    total_scheduling_units = 0.0
    entropy                = 0.0
    
    for scheduling_unit in self.scheduling_units_map:
      raw_data[scheduling_unit] = 0.0
      
    for scheduling_unit in self.scheduled_scheduling_unit.items ( ):
      if scheduling_unit in raw_data:
        raw_data[scheduling_unit] += 1.0
        total_scheduling_units += 1.0
        
    if total_scheduling_units == 0:
      #no scheduling units - no dispersion
      return 0.0
    
    for _, occuernces in raw_data.items():
      p = occuernces / total_scheduling_units
      if p:    
        entropy += (-1.0 * p * math.log(p, 2))
      else:
        entropy += 0.0
      
    return entropy
  
  def get_weekly_hours_difference(self, date):
    """
    Returns the difference in the current week hours, versus 
    the minimum week hours. If the difference is negative, the person is working
    overtime.
      date: an instance of the datetime.date class
      return: a number
    """
    current_hours = datetime.timedelta()
    week = calendar_utils.get_week (date)
    for date_ in week:
      if self.scheduled_turnus[date_]:
        if isinstance(self.scheduled_turnus[date_], turnus.Turnus):
          current_hours += self.scheduled_turnus[date_].duration
        elif isinstance(self.scheduled_turnus[date_], vacation.Vacation):
          current_hours += self.scheduled_turnus[date_].duration
        elif is_holiday(date_) and date_.weekday() != 6:
          current_hours += constants.HOLIDAY_HOURS
      elif is_holiday(date_) and date_.weekday() != 6:
          current_hours += constants.HOLIDAY_HOURS
          
    
    current_hours = timedelta_to_hours(current_hours)
    
    return self.employment_type.weekly_hours - current_hours
  
  def get_monthly_hours_difference(self, date):
    """
    Returns the difference in the current month hours, versus
    the minimum month hours. If the difference is negative, the person is working
    overtime.
      date: an instance of the datetime.date class
      return: a number
    """
    #TODO: remember months in the employment type
    current_hours = datetime.timedelta ( )
    for date_ in calendar_utils.get_same_month_dates (date):
      if self.scheduled_turnus[date_]:
        if isinstance(self.scheduled_turnus[date_], turnus.Turnus):
          current_hours += self.scheduled_turnus[date_].duration
        elif isinstance(self.scheduled_turnus[date_], vacation.Vacation):
          current_hours += self.scheduled_turnus[date_].duration
        elif is_holiday(date_) and date_.weekday() != 6:
          current_hours += constants.HOLIDAY_HOURS
      elif is_holiday(date_) and date_.weekday() != 6:
          current_hours += constants.HOLIDAY_HOURS
      
      
    current_hours = timedelta_to_hours(current_hours)
    
    return self.employment_type.monthly_hours - current_hours

  
  
  def get_turnus (self, date, scheduling_unit=None):
    """
    Return the turnus at the specified date. If the scheduling unit is specified, the person must also work in
    there.
      @param date: a datetime.date object
      @param scheduling_unit: a data object, default is None
      @return: a turnus, if exists, None otherwise
    """
    if isinstance(self.scheduled_turnus[date], turnus.Turnus):
      if scheduling_unit and self.scheduled_scheduling_unit[date] == scheduling_unit:
        return self.scheduled_turnus[date]
      elif not scheduling_unit:
        return self.scheduled_turnus[date]
      else:
        return None
    else:
      return None

  def get_scheduled_raw (self, date):
    """
    Returns the scheduled object at the specified date.
      @return: a 2-tuple:
                the first index has the vacation/turnus
                the second index has the schedule_unit
                both may contain None, if no valid entry exsists
    """
    turnus        = self.scheduled_turnus[date]
    schedule_unit = self.scheduled_scheduling_unit[date]
    
    if not (turnus and turnus != Nurse.FREE_DAY_SIGN):
      turnus = None
    if not schedule_unit:
      schedule_unit = None
    return (turnus, schedule_unit)
  
  def get_scheduled (self, date):
    """
    Returns a tuple, that represents the scheduled object.
      return: a 3-tuple of strings, the first string is the turnus/vacation, the second
              is the workplace, the third is the role
    """
    
    if date not in self.scheduled_turnus or date not in self.scheduled_scheduling_unit:
      raise Exception ('Tega dneva ni bilo v razvrscanju')
    else:
      if self.scheduled_turnus[date]:
        if self.scheduled_turnus[date] == Nurse.FREE_DAY_SIGN:
          return ('', str(self.scheduled_scheduling_unit[date]), '')
        else:
          return (str(self.scheduled_turnus[date]), str(self.scheduled_scheduling_unit[date]), '')
      else:
        return (str(self.scheduled_turnus[date]), str(self.scheduled_scheduling_unit[date]), '')
      
  def get_schedule (self, dates):
    """
    Returns this nurses schedule, for the specified dates.
      @param dates: a list of datetime.date object
      @return: a list of @see: get_scheduled results, ordered in the same way as the dates parameter. 
    """
    schedule = []
    for date in dates:
      try:
        sch = self.get_scheduled (date)
        schedule.append (str (sch[0]) + '\n' + str (sch[1]))
      except:
        schedule.append (('\n'))
    return schedule
  
  def get_schedule_compact (self, dates):
    """
    Returns this nurses compact schedule (only turnus and vacation code), for the specified dates.
      @param dates: a list of datetime.date object
      @return: a list of @see: get_scheduled_results, ordered in the same way as the dates parameter.
    """
    schedule = []
    for date in dates:
      if self.get_turnus (date):
        schedule.append (self.get_turnus (date).code)
      elif self.__get_vacation (date):
        schedule.append (self.__get_vacation (date).code)
      else:
        schedule.append ('')
    return schedule
  
  def get_colors (self, dates):
    """
    Returns a list of scheduling units' background colors. The list of colors matches the dates parameter.
    The default color is white (if there is no scheduling unit.
      @return: a list of RGB tuples.
    """
    colors = []
    for date in dates:
      if self.scheduled_scheduling_unit[date]:
        colors.append (self.scheduled_scheduling_unit[date].get_color ( ))
      else:
        colors.append ((255,255,255))
    return colors
      
    
  def clear_date(self, date):
    """
    Clears whatever was scheduled in the schedule.
      date: the date that will be cleared
    """
    
    if date not in self.scheduled_turnus or date not in self.scheduled_scheduling_unit:
      raise Exception ('Datuma ni bilo mogoce odstraniti.')
    
    self.scheduled_turnus[date] = ''
    self.scheduled_scheduling_unit[date] = ''
    
    
  def is_turnus_forbidden (self, date, turnus):
    """
    Checks if the turnus is allowed to be scheduled for the specified date.
      @param date: a datetime.date object
      @param turnus: a data object
      @return: False, if it is not allowed, True otherwise
    """
    if date in self.forbidden_turnuses:
      return turnus in self.forbidden_turnuses[date]
    else:
      return False
  
  def add_invalid_turnus (self, date, turnus):
    """
    Disallows the turnus for the specified date.
      @param date: a datetime.date object
      @param turnus: a data object
    """
    if date not in self.forbidden_turnuses:
      self.forbidden_turnuses[date] = set ( )
    self.forbidden_turnuses[date].add (turnus)
  
  def remove_invalid_turnus (self, date, turnus):
    """
    Removes the restricted turnus for the specified date
      @param date: a datetime.date object
      @param turnus: a data object
    """
    if date in self.forbidden_turnuses:
      if turnus in self.forbidden_turnuses[date]:
        self.forbidden_turnuses[date].remove (turnus)
        if not self.forbidden_turnuses[date]:
          del self.forbidden_turnuses[date]
          
  def get_month_clone (self, date):
    """
    Returns a copy of this person, but the date fields contain only dates from the given month.
      @param date: a datetime.date object, with the correct month and year
      @return: a schedule nurse object
    """
    dates = calendar_utils.get_same_month_dates (date)
    clone = Nurse (self)
    
    for date in dates:
      if date in self.forbidden_turnuses:
        clone.forbidden_turnuses[date] = self.forbidden_turnuses[date]
      
      clone.scheduled_turnus[date]          = self.scheduled_turnus[date]
      clone.scheduled_scheduling_unit[date] = self.scheduled_scheduling_unit[date]
      
    return clone
  
  def merge (self, person):
    """
    Merges the person into this one. All the date fields that may appear in both persons are 
    overwritten by the given person.
      @param person: an object of this class
    """
    
    for date in person.forbidden_turnuses:
      self.forbidden_turnuses[date] = person.forbidden_turnuses[date]
      
    for date in person.scheduled_turnus:
      self.scheduled_turnus[date]          = person.scheduled_turnus[date]
      self.scheduled_scheduling_unit[date] = person.scheduled_scheduling_unit[date]
      
      
    

  def __get_vacation (self, date):
    """
    Returns the vacation at the selected date.
      @param date: a datetime.date object
      @return: a data object, None if there is no vacation at the specified date.
    """
    if isinstance(self.scheduled_turnus[date], vacation.Vacation):
      return self.scheduled_turnus[date]
    else:
      return None
    

  def __can_be_scheduled (self, date):
    """
    Check, if is possible, that a turnus can be scheduled that day.
      date: is the date checked
      return: true, if the day can support a turnus, false otherwise
    """
    if date == self.birthday:
      return False
    else:
      return not self.is_scheduled(date)
      
