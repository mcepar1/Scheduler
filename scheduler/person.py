from Scheduler.data import nurse, doctor, turnus, vacation

from Scheduler.utils.time_conversion import timedelta_to_hours
from Scheduler.utils.holiday import is_holiday
from Scheduler.scheduler import constants

import calendar
import datetime
import math


FREE_DAY_SIGN = 'This is a free day'

class Nurse (nurse.Nurse):

  def __init__(self, data_nurse):
    """
    The default constructor
      data_nurse: an instance of the data.nurse.Nurse class
    """
      
    nurse.Nurse.__init__(self, data_nurse.work_id, data_nurse.name, data_nurse.surname, data_nurse.birthday, data_nurse.titles, data_nurse.roles, data_nurse.employment_type)
    
    self.allowed_turnuses = data_nurse.allowed_turnuses
    self.forbidden_turnuses = data_nurse.forbidden_turnuses
    self.vacations = data_nurse.vacations
    self.workplaces = data_nurse.workplaces
    self.predefined = data_nurse.predefined
    self.week_morning = data_nurse.week_morning
    
    # tells if the night turnuses are scheduled in packages
    self.packet_night_turnuses = data_nurse.packet_night_turnuses
    
    #this field maps a date to the turnus
    self.scheduled_turnus = {}
    #this field maps a date to the workplace
    self.scheduled_workplace = {}
    #this field maps a date to the role
    self.scheduled_role = {}
    
    
    
  def load_previous_month (self, old_nurse, date):
    """
    Loads the already scheduled days back into the person.
      old_nurse: is the instance of this class, from the previous month
      date: is the datetime.date, that contains the previous month and year
    """
    
    next_month = datetime.date(day=28, month=date.month, year=date.year) + datetime.timedelta(days=8)
    self.add_month(date)
    self.add_month(next_month)
    
    if self == old_nurse:
      self.scheduled_turnus.update(old_nurse.scheduled_turnus)
      self.scheduled_workplace.update(old_nurse.scheduled_workplace)
      self.scheduled_role.update(old_nurse.scheduled_role)
      
    else:
      raise Exception('Napaka pri nalaganju prejsnjega meseca.')
    
  def add_month (self, date):
    """
    Adds a new month into this scheduler.
      date: is an datetime.date instance with the correct year or month
    """

    for date_ in self.__get_affected_dates(date):
      if date_ not in self.scheduled_turnus and date_ not in self.scheduled_workplace and date_ not in self.scheduled_role:
        self.scheduled_turnus[date_] = ''
        self.scheduled_workplace[date_] = ''
        self.scheduled_role[date_] = ''
        
  def schedule_constraints(self):
    """Schedules vacations and manually added constraints into the person."""
    self.__synchronize_vacations()
    self.__synchronize_predefined()
  
        
    
  def schedule_turnus (self, date, turnus, workplace, role):
    """
    Schedules a new turnus.
      date: is the date of the turnus
      turnus: is the turnus
      workplace: is the workplace in which the nurse will work
      role: is the role, that the nurse will assume  
    """
    
    #if new month
    if date not in self.scheduled_turnus or date not in self.scheduled_workplace or date not in self.scheduled_role:
      self.add_month (date)
    
    if self.scheduled_turnus[date] or self.scheduled_workplace[date] or self.scheduled_role[date]:
      raise Exception("Trying to override an already scheduled date")
        
    
    self.scheduled_turnus[date] = turnus
    self.scheduled_workplace[date] = workplace
    self.scheduled_role[date] = role
    
  def is_blocked(self, date, turnus):
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
          instance = datetime.datetime(year=prev_date.year, month=prev_date.month, day=prev_date.day)
          prev_turnus_start = instance.combine(prev_date, prev_turnus.start)
          prev_turnus_end = instance.combine(prev_date, prev_turnus.end)
          
          #if it went over midnight
          if prev_turnus_end < prev_turnus_start:
            prev_turnus_end += datetime.timedelta(days=1)
            
          current_start = instance.combine(date, turnus.start)
          if (prev_turnus_end + prev_turnus.blockade) < current_start:
            return False
        if self.can_be_scheduled(next_date):
          #check if there is a hard-coded date in the next-date
          if self.scheduled_turnus[next_date]:
            next_turnus = self.scheduled_turnus[next_date]
            next_start = instance.combine(next_date, next_turnus.start)
          else:
            next_start = datetime.datetime(day=1, month=1, year=3000)
            
          instance = datetime.datetime(year=date.year, month=date.month, day=date.day)
          this_turnus_start = instance.combine(date, turnus.start)
          this_turnus_end = instance.combine(date, turnus.end)
          
          #if it went over midnight
          if this_turnus_end < this_turnus_start:
            this_turnus_end += datetime.timedelta(days=1)
            
          
          if (this_turnus_end + turnus.blockade) < next_start:
            return False
    
    return True
    
    
  def is_scheduled(self, date):
    """
    Checks if the date is already scheduled. The date is considered scheduled, if it
    has a turnus, a vacation or a specifically marked free day.
      date: the date checked
      return: true, if scheduled, false otherwise
    """
    
    if self.scheduled_turnus[date] or self.scheduled_workplace[date] or self.scheduled_role[date]:
      return True
    else:
      return False
    
    
  def is_scheduled_exact(self, workplace, role, turnus, date):
    """
    Checks if the combination is scheduled.
      workplace: is the workplace that is checked
      role: is the role that is checked
      turnus: is the turnus that is checked
      date: is date for against the turnus, workplace and role are checked
      return: true if they are scheduled, false otherwise
    """
        
    return self.scheduled_turnus[date] == turnus and self.scheduled_workplace[date] == workplace and self.scheduled_role[date] == role
    
  def schedule_vacation (self, date, vacation):
    """
    Adds a vacation to the person.
      date: is the date of the vacation
      vacation: is the type of the vacation
    """
    
    #if new month
    if date not in self.scheduled_turnus:
      self.add_month(date)
    
    if self.scheduled_turnus[date]:
      raise Exception ("Trying to override an already scheduled date")

    self.scheduled_turnus[date] = vacation
    self.scheduled_workplace[date] = ''
    self.scheduled_role[date] = ''
    
  def add_free_day(self, date):
    """
    Adds a free day in the schedule. This is not a vacation! This is the a legal 
    requirement.
      date: is the date of the free day
    """
    
    if self.scheduled_turnus[date] or self.scheduled_workplace[date]:
      raise Exception('Ta dan ne more biti prost')
      
    self.scheduled_turnus[date] = FREE_DAY_SIGN
    
  def is_vacation(self, date):
    """
    Checks if the date is a vacation.
      date: is the date being checked
      return: true, if the date is a vacation, false otherwise
    """
    
    if date in self.scheduled_turnus:
      return isinstance(self.scheduled_turnus[date], vacation.Vacation)
    else:
      return False
    
  def is_free_day(self, date):
    """
    Checks if the date is a free day. A free day is: a vacation, a specifically
    marked free day, a yet unscheduled date or the persons birthday.
      date: is the date checked
      return: true, if the day is free, false otherwise
    """
    if date == self.birthday:
      return True
    elif date in self.scheduled_turnus or date in self.scheduled_workplace:
      if  not isinstance(self.scheduled_turnus[date], turnus.Turnus):
        return True
      else:
        return False
    else:
      return True
  
  def can_be_scheduled(self, date):
    """
    Check, if is possible, that a turnus can be scheduled that day.
      date: is the date checked
      return: true, if the day can support a turnus, false otherwise
    """
    if date == self.birthday:
      return False
    else:
      return not self.is_scheduled(date)
    
    
  def get_turnus_dispersion(self):
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
  
  def get_workplace_dispersion(self):
    """Calculates and returns the entropy of the workplaces."""
    
    raw_data = {}
    total_workspaces = 0.0
    entropy = 0.0
    
    for workspace in self.workplaces:
      raw_data[workspace] = 0.0
      
    for _, workspace in self.scheduled_workplace.items():
      if workspace in raw_data:
        raw_data[workspace] += 1.0
        total_workspaces += 1.0
        
    if total_workspaces == 0:
      #no workplaces - no dispersion
      return 0.0
    
    for _, occuernces in raw_data.items():
      p = occuernces / total_workspaces
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
    week = self.__get_week(date)
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
    
    current_hours = datetime.timedelta()
    for day in self.__get_days(date):
      date_ = datetime.date(day=day, month=date.month, year=date.year)
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
  
  def get_turnus(self, date, workplace=None, role=None):
    """
    Return the turnus at the specified date.
      date: is the date of the desired turnus
      workplace: if this paramter is given, the person must also be
                 scheduled in the correct workplace
      role: if this parameter is given, the person must also be 
            scheduled in the correct role
      return: a turnus, if exists, None otherwise
    """
    if isinstance(self.scheduled_turnus[date], turnus.Turnus):
      if workplace and role and self.scheduled_workplace[date] == workplace and self.scheduled_role[date] == role:
        return self.scheduled_turnus[date]
      elif not workplace and role and self.scheduled_role[date] == role:
        return self.scheduled_turnus[date]
      elif not role and workplace and self.scheduled_workplace[date] == workplace:
        return self.scheduled_turnus[date]
      elif not role and not workplace:
        return self.scheduled_turnus[date]
      else:
        return None
    else:
      return None
  
  def get_scheduled(self, date):
    """
    Returns a tuple, that represents the scheduled object.
      return: a 3-tuple of strings, the first string is the turnus/vacation, the second
              is the workplace, the third is the role
    """
    
    if date not in self.scheduled_turnus or date not in self.scheduled_workplace:
      raise Exception ('Tega dneva ni bilo v razvrscanju')
    else:
      if self.scheduled_turnus[date]:
        if self.scheduled_turnus[date] == FREE_DAY_SIGN:
          return ('', str(self.scheduled_workplace[date]), str(self.scheduled_role[date]))
        else:
          return (str(self.scheduled_turnus[date]), str(self.scheduled_workplace[date]), str(self.scheduled_role[date]))
      else:
        return (str(self.scheduled_turnus[date]), str(self.scheduled_workplace[date]), str(self.scheduled_role[date]))
      
  def get_scheduled_dates(self):
    """
    Returns a sorted list of all dates, that are currently scheduled in this object.
    """
    turnus_dates = self.scheduled_turnus.keys()
    workplace_dates = self.scheduled_workplace.keys()
    role_dates = self.scheduled_role.keys()
    
    dates = set(turnus_dates) & set(workplace_dates) & set(role_dates)
    
    if len(dates) != len(turnus_dates) or len(dates) != len(workplace_dates) or len(dates) != len(role_dates):
      raise Exception ('Oseba ima napacno razvrscene turnuse ali delovisca.')
    
    return sorted(dates)
  
  def remove_scheduled_date(self, date):
    """
    Deletes a date from the schedule.
      date: the date that will be deleted
    """ 
    
    if date not in self.scheduled_turnus or date not in self.scheduled_workplace or date not in self.scheduled_role:
      raise Exception ('Datuma ni bilo mogoce odstraniti.')
    
    del self.scheduled_turnus[date]
    del self.scheduled_workplace[date]
    del self.scheduled_role[date]
    
  def clear_date(self, date):
    """
    Clears whatever was scheduled in the schedule.
      date: the date that will be cleared
    """
    
    if date not in self.scheduled_turnus or date not in self.scheduled_workplace or date not in self.scheduled_role:
      raise Exception ('Datuma ni bilo mogoce odstraniti.')
    
    self.scheduled_turnus[date] = ''
    self.scheduled_workplace[date] = ''
    self.scheduled_role[date] = ''
    
    
    
    
      
  def __get_days(self, date):
    """
    Returns a sorted list of days for the scheduling date.
      date: is the datetime.date object, that defines the month and year
      return: a sorted list of integers
    """
    days = []
    for day in calendar.Calendar().itermonthdays(date.year, date.month):
      if day:
        days.append(day)
        
    days.sort()
    
    return days
  
  def __get_affected_dates(self, date):
    """
    Returns all the dates in all the weeks that this month includes.
      date: an instance of datetime.date, that contains the month
      return: a list of dates
    """
    
    dates = []
    for week in calendar.Calendar().monthdatescalendar(year=date.year, month=date.month):
      dates += week
      
    return dates
    
  def __get_week(self, date):
    """
    Returns the week in which the date is located.
      date: instance of the datetime.date class
      return: a list of dates
    """
    
    for week in calendar.Calendar().monthdatescalendar(year=date.year, month=date.month):
      if date in week:
        return week
    else:
      raise Exception('Date week error')
    
  def __synchronize_vacations(self):
    """Schedules all the vacations."""
    
    for date in self.vacations:
      self.schedule_vacation(date, list(self.vacations[date])[0])
      
  def __synchronize_predefined(self):
    """Schedule all the predefined turnuses. The user is always right, so this can break any constraint,
      except one turnus per day.."""
    
    for date in self.predefined:
      self.schedule_turnus(date, self.predefined[date][0], self.predefined[date][1], self.predefined[date][2])
      
      
class Doctor (doctor.Doctor):

  def __init__(self, data_doctor):
    """
    The default constructor
      data_doctor: an instance of the data.doctor.Doctor class
    """
      
    doctor.Doctor.__init__(self, data_doctor.work_id, data_doctor.name, data_doctor.surname, data_doctor.birthday, data_doctor.titles, data_doctor.employment_type)
    
    self.allowed_turnuses = data_doctor.allowed_turnuses
    self.forbidden_turnuses = data_doctor.forbidden_turnuses
    self.vacations = data_doctor.vacations
    self.workplaces = data_doctor.workplaces
    self.predefined = data_doctor.predefined
    
    # tells if the night turnuses are scheduled in packages
    self.packet_night_turnuses = data_doctor.packet_night_turnuses
    
    #this field maps a date to the turnus
    self.scheduled_turnus = {}
    #this field maps a date to the workplace
    self.scheduled_workplace = {}
    
    
    
  def load_previous_month (self, old_doctor, date):
    """
    Loads the already scheduled days back into the person.
      old_doctor: is the instance of this class, from the previous month
      date: is the datetime.date, that contains the previous month and year
    """
    
    next_month = datetime.date(day=28, month=date.month, year=date.year) + datetime.timedelta(days=8)
    self.add_month(date)
    self.add_month(next_month)
    
    if self == old_doctor:
      self.scheduled_turnus.update(old_doctor.scheduled_turnus)
      self.scheduled_workplace.update(old_doctor.scheduled_workplace)
      
    else:
      raise Exception('Napaka pri nalaganju prejsnjega meseca.')
    
  def add_month (self, date):
    """
    Adds a new month into this scheduler.
      date: is an datetime.date instance with the correct year or month
    """

    for date_ in self.__get_affected_dates(date):
      if date_ not in self.scheduled_turnus and date_ not in self.scheduled_workplace:
        self.scheduled_turnus[date_] = ''
        self.scheduled_workplace[date_] = ''
        
  def schedule_constraints(self):
    """Schedules vacations and manually added constraints into the person."""
    self.__synchronize_vacations()
    self.__synchronize_predefined()
  
        
    
  def schedule_turnus (self, date, turnus, workplace):
    """
    Schedules a new turnus.
      date: is the date of the turnus
      turnus: is the turnus
      workplace: is the workplace in which the doctor will work  
    """
      
    if self.scheduled_turnus[date] or self.scheduled_workplace[date]:
      raise Exception("Trying to override an already scheduled date")
      
      
    #if new month
    if date not in self.scheduled_turnus or date not in self.scheduled_workplace:
      self.add_month (date)
        
    
    self.scheduled_turnus[date] = turnus
    self.scheduled_workplace[date] = workplace
    
  def is_blocked(self, date, turnus):
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
          instance = datetime.datetime(year=prev_date.year, month=prev_date.month, day=prev_date.day)
          prev_turnus_start = instance.combine(prev_date, prev_turnus.start)
          prev_turnus_end = instance.combine(prev_date, prev_turnus.end)
          
          #if it went over midnight
          if prev_turnus_end < prev_turnus_start:
            prev_turnus_end += datetime.timedelta(days=1)
            
          current_start = instance.combine(date, turnus.start)
          if (prev_turnus_end + prev_turnus.blockade) < current_start:
            return False
        if self.can_be_scheduled(next_date):
          #check if there is a hard-coded date in the next-date
          next_turnus = self.scheduled_turnus[next_date]
          instance = datetime.datetime(year=date.year, month=date.month, day=date.day)
          this_turnus_start = instance.combine(date, turnus.start)
          this_turnus_end = instance.combine(date, turnus.end)
          
          #if it went over midnight
          if this_turnus_end < this_turnus_start:
            this_turnus_end += datetime.timedelta(days=1)
            
          next_start = instance.combine(next_date, next_turnus.start)
          if (this_turnus_end + turnus.blockade) < next_start:
            return False
    
    return True
    
    
  def is_scheduled(self, date):
    """
    Checks if the date is already scheduled. The date is considered scheduled, if it
    has a turnus, a vacation or a specifically marked free day.
      date: the date checked
      return: true, if scheduled, false otherwise
    """
    
    if self.scheduled_turnus[date] or self.scheduled_workplace[date]:
      return True
    else:
      return False
    
    
  def is_scheduled_exact(self, workplace, turnus, date):
    """
    Checks if the combination is scheduled.
      workplace: is tha workplace that is checked
      turnus: is the turnus that is checked
      date: is date for against the turnus and workplaces are checked
      return: true if they are scheduled, false otherwise
    """
        
    return self.scheduled_turnus[date] == turnus and self.scheduled_workplace[date] == workplace
    
  def schedule_vacation (self, date, vacation):
    """
    Adds a vacation to the person.
      date: is the date of the vacation
      vacation: is the type of the vacation
    """
    
    if self.scheduled_turnus[date]:
      raise Exception ("Trying to override an already scheduled date")
    
    #if new month
    if date not in self.scheduled_turnus:
      self.add_month(date)

    self.scheduled_turnus[date] = vacation
    self.scheduled_workplace[date] = ''
    
  def add_free_day(self, date):
    """
    Adds a free day in the schedule. This is not a vacation! This is a legal 
    requirement.
      date: is the date of the free day
    """
    
    if self.scheduled_turnus[date] or self.scheduled_workplace[date]:
      raise Exception('Ta dan ne more biti prost')
      
    self.scheduled_turnus[date] = FREE_DAY_SIGN
    
  def is_vacation(self, date):
    """
    Checks if the date is a vacation.
      date: is the date being checked
      return: true, if the date is a vacation, flase otherwise
    """
    
    if date in self.scheduled_turnus:
      return isinstance(self.scheduled_turnus[date], vacation.Vacation)
    else:
      return False
    
  def is_free_day(self, date):
    """
    Checks if the date is a free day. A free day is: a vacation, a specifically
    marked free day, a yet unscheduled date or the persons birthday.
      date: is the date checked
      return: true, if the day is free, false otherwise
    """
    if date == self.birthday:
      return True
    elif date in self.scheduled_turnus or date in self.scheduled_workplace:
      if  not isinstance(self.scheduled_turnus[date], turnus.Turnus):
        return True
      else:
        return False
    else:
      return True
    
  def can_be_scheduled(self, date):
    """
    Check, if is possible, that a turnus can be scheduled that day.
      date: is the date checked
      return: true, if the day can support a turnus, false otherwise
    """
    if date == self.birthday:
      return False
    else:
      return not self.is_scheduled(date)
    
    
  def get_turnus_dispersion(self):
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
  
  def get_workplace_dispersion(self):
    """Calculates and returns the entropy of the workplaces."""
    
    raw_data = {}
    total_workspaces = 0.0
    entropy = 0.0
    
    for workspace in self.workplaces:
      raw_data[workspace] = 0.0
      
    for _, workspace in self.scheduled_workplace.items():
      if workspace in raw_data:
        raw_data[workspace] += 1.0
        total_workspaces += 1.0
        
    if total_workspaces == 0:
      #no workplaces - no dispersion
      return 0.0
    
    for _, occuernces in raw_data.items():
      p = occuernces / total_workspaces
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
    week = self.__get_week(date)
    
    for date_ in week:
      if self.scheduled_turnus[date_]:
        if isinstance(self.scheduled_turnus[date_], turnus.Turnus):
          current_hours += self.scheduled_turnus[date_].duration
        if isinstance(self.scheduled_turnus[date_], vacation.Vacation):
          current_hours += self.scheduled_turnus[date_].duration
    
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
    
    current_hours = datetime.timedelta()
    for day in self.__get_days(date):
      date_ = datetime.date(day=day, month=date.month, year=date.year)
      if self.scheduled_turnus[date_]:
        if isinstance(self.scheduled_turnus[date_], turnus.Turnus):
          current_hours += self.scheduled_turnus[date_].duration
        if isinstance(self.scheduled_turnus[date_], vacation.Vacation):
          current_hours += self.scheduled_turnus[date_].duration
        
        
    current_hours = timedelta_to_hours(current_hours)
    
    return self.employment_type.monthly_hours - current_hours
  
  def get_turnus(self, date, workplace=None):
    """
    Return the turnus at the specified date.
      date: is the date of the desired turnus
      workplace: if this paramter is given, the person must also be
                 scheduled in the correct workplace
      return: a turnus, if exists, None otherwise
    """
    if isinstance(self.scheduled_turnus[date], turnus.Turnus):
      if workplace and self.scheduled_workplace[date] == workplace:
        return self.scheduled_turnus[date]
      elif not workplace:
        return self.scheduled_turnus[date]
      else:
        return None
    else:
      return None
  
  def get_scheduled(self, date):
    """
    Returns a tuple, that represents the scheduled object.
      return: a 2-tuple of strings, the first string is the turnus/vacation, the second
              is the workplace
    """
    
    if date not in self.scheduled_turnus or date not in self.scheduled_workplace:
      raise Exception ('Tega dneva ni bilo v razvrscanju')
    else:
      if self.scheduled_turnus[date]:
        if self.scheduled_turnus[date] == FREE_DAY_SIGN:
          return ('', str(self.scheduled_workplace[date]))
        else:
          return (str(self.scheduled_turnus[date]), str(self.scheduled_workplace[date]))
      else:
        return (str(self.scheduled_turnus[date]), str(self.scheduled_workplace[date]))
      
  def get_scheduled_dates(self):
    """
    Returns a sorted list of all dates, that are currently scheduled in this object.
    """
    turnus_dates = self.scheduled_turnus.keys()
    workplace_dates = self.scheduled_workplace.keys()
    
    dates = set(turnus_dates) & set(workplace_dates)
    
    if len(dates) != len(turnus_dates) or len(dates) != len(workplace_dates):
      raise Exception ('Oseba ima napacno razvrscene turnuse ali delovisca.')
    
    return sorted(dates)
  
  def remove_scheduled_date(self, date):
    """
    Deletes a date from the schedule.
      date: the date that will be deleted
    """ 
    
    if date not in self.scheduled_turnus or date not in self.scheduled_workplace:
      raise Exception ('Datuma ni bilo mogoce odstraniti.')
    
    del self.scheduled_turnus[date]
    del self.scheduled_workplace[date]
    
    
    
    
      
  def __get_days(self, date):
    """
    Returns a sorted list of days for the scheduling date.
      date: is the datetime.date object, that defines the month and year
      return: a sorted list of integers
    """
    days = []
    for day in calendar.Calendar().itermonthdays(date.year, date.month):
      if day:
        days.append(day)
        
    days.sort()
    
    return days
  
  def __get_affected_dates(self, date):
    """
    Returns all the dates in all the weeks that this month includes.
      date: an instance of datetime.date, that contains the month
      return: a list of dates
    """
    
    dates = []
    for week in calendar.Calendar().monthdatescalendar(year=date.year, month=date.month):
      dates += week
      
    return dates
    
  def __get_week(self, date):
    """
    Returns the week in which the date is located.
      date: instance of the datetime.date class
      return: a list of dates
    """
    
    for week in calendar.Calendar().monthdatescalendar(year=date.year, month=date.month):
      if date in week:
        return week
    else:
      raise Exception('Date week error')
    
  def __synchronize_vacations(self):
    """Schedules all the vacations."""
    
    for date in self.vacations:
      self.schedule_vacation(date, list(self.vacations[date])[0])
      
  def __synchronize_predefined(self):
    """Schedule all the predefined turnuses. The user is always right, so this can break any constraint,
      except one turnus per day.."""
    
    for date in self.predefined:
      self.schedule_turnus(date, self.predefined[date][0], self.predefined[date][1])
  
        
