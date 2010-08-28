from data import nurse, turnus, vacation

from utils.time_conversion import timedelta_to_hours 

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
      
    nurse.Nurse.__init__(self, data_nurse.name, data_nurse.surname, data_nurse.title, data_nurse.birthday, data_nurse.employment_type)
    
    self.forbidden_turnuses = data_nurse.forbidden_turnuses
    self.vacations = data_nurse.vacations
    self.workplaces = data_nurse.workplaces
    self.predefined = data_nurse.predefined
    
    #this field maps a date to the turnus
    self.scheduled_turnus = {}
    #this field maps a date to the workplace
    self.scheduled_workplace = {}
    
    self.monthly_hours = {}
    self.weekly_hours = datetime.timedelta()
    
    
  def load_previous_month (self, old_nurse, date):
    """
    Loads the already scheduled days back into the person.
      old_nurse: is the instance of this class, from the previous month
      date: is the datetime.date, that contains the previous month and year
    """
    if self == old_nurse:
      self.scheduled_turnus.update(old_nurse.scheduled_turnus)
      self.scheduled_workplace.update(old_nurse.scheduled_workplace)
      
      self.weekly_hours = old_nurse.weekly_hours
      
      next_month = datetime.date(day=28, month=date.month, year=date.year) + datetime.timedelta(days=8)
      if next_month in old_nurse.monthly_hours:
        self.monthly_hours[next_month.month] = old_nurse.monthly_hours[next_month.month]
    else:
      raise Exception('Napaka pri nalaganju prejsnjega meseca.')
    
  def add_month (self, date):
    """
    Adds a new month into this scheduler.
      date: is an datetime.date instance with the correct year or month
    """
    if date.month not in self.monthly_hours:
      self.monthly_hours[date.month] = datetime.timedelta()

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
      workplace: is the workplace in which the nurse will work  
    """
      
    if self.scheduled_turnus[date] or self.scheduled_workplace[date]:
      raise Exception("Trying to override an already scheduled date")
      
    #if monday
    if date.weekday() == 0:
      self.weekly_hours = datetime.timedelta()
      
    #if new month
    if date not in self.scheduled_turnus or date not in self.scheduled_workplace:
      self.add_month (date)
        
    self.weekly_hours += turnus.duration
    self.monthly_hours[date.month] += turnus.duration
    
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
      if self.is_free_day(prev_date):
        return False
      else:
        prev_turnus = self.scheduled_turnus[prev_date]
        #calculate blocking next free date
        instance = datetime.datetime(year=prev_date.year, month=prev_date.month, day=prev_date.day)
        prev_turnus_start = instance.combine(prev_date, prev_turnus.start)
        prev_turnus_end = instance.combine(prev_date, prev_turnus.end)
        
        #if it went over midnight
        if prev_turnus_end < prev_turnus_start:
          prev_turnus_end += datetime.timedelta(days=1)
          
        current_start = instance.combine(date, turnus.start)
        return current_start < (prev_turnus_end + prev_turnus.blockade)
    
  def is_scheduled(self, date):
    """
    Checks if the date is already scheduled.
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
    
    if self.scheduled[date]:
      raise Exception ("Trying to override an already scheduled date")
    
    #if new month
    if date not in self.scheduled:
      self.add_month(date)

    self.scheduled_turnus[date] = vacation
    self.scheduled_workplace[date] = ''
    
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
      return: true, if the date is a vacation, flase otherwise
    """
    
    if date in self.scheduled_turnus:
      return isinstance(self.scheduled_turnus[date], vacation.Vacation)
    else:
      return False
    
  def is_free_day(self, date):
    """
    Checks if the date is a free day. A free day is: a vacation, a specificly
    marked free day or a yet unscheduled date,
      date: is the date checked
      return: true, if the day is free, false otherwise
    """
    if date in self.scheduled_turnus or date in self.scheduled_workplace:
      if  not isinstance(self.scheduled_turnus[date], turnus.Turnus):
        return True
      else:
        return False
    else:
      return True
    
    
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
        #TODO: VACATIONS
        if isinstance(self.scheduled_turnus[date_], turnus.Turnus):
          current_hours += self.scheduled_turnus[date_].duration
        elif isinstance(self.scheduled_turnus[date_], vacation.Vacation):
          current_hours += datetime.timedelta(hours=7)
    
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
        #TODO: VACATIONS
        if isinstance(self.scheduled_turnus[date_], turnus.Turnus):
          current_hours += self.scheduled_turnus[date_].duration
        elif isinstance(self.scheduled_turnus[date_], vacation.Vacation):
          current_hours += datetime.timedelta(hours=7)
        
        
    current_hours = timedelta_to_hours(current_hours)
    
    return self.employment_type.monthly_hours - current_hours
  
  def get_schedule_raw(self):
    """
    Returns the nurse's schedule.
    @deprecated: use get_scheduled instead
    """
    schedule = {}
    
    for date in self.scheduled_workplace:
      schedule[date] = (self.scheduled_turnus[date], self.scheduled_workplace[date])
      
    return schedule
  
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
      self.schedule_vacation(date, self.vacations[date])
      
  def __synchronize_predefined(self):
    """Schedule all the predefined turnuses. The user is always right, so this can break any constraint,
      except one turnus per day.."""
    
    for date in self.predefined:
      self.schedule_turnus(date, self.predefined[date][0], self.predefined[date][1])
          
