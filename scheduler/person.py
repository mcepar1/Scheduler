from data import nurse

import calendar
import datetime
import math

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
      
      next_month = datetime.date(day = 28, month = date.month, year = date.year) + datetime.timedelta(days = 8)
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

    for day in self.__get_days(date):
      date_ = datetime.date (day = day, month = date.month, year = date.year)
      
      if date_ not in self.scheduled_turnus and date_ not in self.scheduled_workplace:
        self.scheduled_turnus[date_] = ''
        self.scheduled_workplace[date_] = ''
  
        
    
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
        
    
    for _, occuernces in raw_data.items():
      p = occuernces / total_turnuses
      if p:    
        entropy += (-1.0 * p * math.log(p, 2))
      else:
        entropy += 0.0
      
    return entropy
  
  def get_workspace_dispersion(self):
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
        
    
    for _, occuernces in raw_data.items():
      p = occuernces / total_workspaces
      if p:    
        entropy += (-1.0 * p * math.log(p, 2))
      else:
        entropy += 0.0
      
    return entropy
  
  def get_weekly_hours_difference(self):
    """Returns the difference in the current week hours, versus 
    the minimum week hours. If the difference is negative, the person is working
    overtime"""
    pass
  
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
    
      
    
      
