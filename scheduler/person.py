from data import nurse

import datetime

class Nurse (nurse.Nurse):

  def __init__(self,data_nurse):
    """
    The default constructor
      data_nurse: an instance of the data.nurse.Nurse class
    """
      
    nurse.Nurse.__init__(self,data_nurse.name, data_nurse.surname, data_nurse.employment_type)
    
    self.forbidden_turnuses = data_nurse.forbidden_turnuses
    self.vacations = data_nurse.vacations
    
    #this field maps a date to the turnus
    self.scheduled = {}
    
    self.monthly_hours = 0
    self.weekly_hours = 0
    
  def add_month (self,date):
    """
    Adds a new month into this scheduler.
      date: is the any datetime.date instance with the correct year or month
    """
    
    try:
      for day in range (1,32):
        self.scheduled[datetime.date(day = day, month = date.month, year = date.year)] = ''
    except:
      pass
        
    
  def add_turnus (self,date,turnus):
    """
    Schedules a new turnus.
      date: is the date of the turnus
      turnis: is the turnus  
    """
      
    if self.scheduled[date]:
      raise Exception("Trying to override an already scheduled date")
      
    #if monday
    if date.weekday() == 0:
      self.weekly_hours = 0
      
    #if new month
    if date not in self.scheduled:
      self.add_month (date)
      self.monthly_hours = 0
        
    self.weekly_hours += (turnus.start-turnus.end)
    self.monthly_hours += (turnus.start-turnus.end)
    
    self.scheduled[date]=turnus
      
      
