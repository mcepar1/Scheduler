# -*- coding: utf-8 -*-
from scheduler import person
from scheduler import workplace as workplace_module

import datetime
import calendar
import cPickle as pickle
import os


class NurseScheduler:
  FILES_DIR = os.path.join("scheduler", "persistence", "nurses")

  def __init__(self, nurses, workplaces, date):
    """
    The default constructor.
      nurses: a list of all the nurses, that will be scheduled
      workplaces: a list of workplaces, that the nurses will be scheduled into
      date: is the starting date of the scheduling
    """
  
    self.nurses = []
    for nurse in nurses:
      if nurse.allowed_turnuses:
        self.nurses.append(person.Nurse(nurse))
        self.nurses[-1].add_month (date)
    self.__get_previous_month(date)
    
    self.workplaces = []
    for workplace_ in workplaces:
      self.workplaces.append(workplace_module.Workplace(workplace_))
    
    
    self.date = date
    
    #set various maps, for the ease of access
    
    #maps workplaces to nurses
    self.workplace_nurses = {}
    for workplace in self.workplaces:
      self.workplace_nurses[workplace] = set()
      for nurse in self.nurses:
        if workplace in nurse.workplaces:
          self.workplace_nurses[workplace].add(nurse)
        
    #maps employment types to nurses
    self.employment_type_nurses = {}
    for nurse in self.nurses:
      if nurse.employment_type not in self.employment_type_nurses:
        self.employment_type_nurses[nurse.employment_type] = set()
      self.employment_type_nurses[nurse.employment_type].add(nurse)
      
    #self.__save()
      
    
    
  def __get_previous_month(self, date):
    """
    This reloads the previously scheduled month into the application.
      date: is the current schedule date
    """
    
    prev_date = datetime.date(day=1, month=date.month, year=date.year) - datetime.timedelta (days=1) 
    filename = str(prev_date.month) + '_' + str(prev_date.year) + '.dat'
    
    old_nurses = pickle.load(file(os.path.join(NurseScheduler.FILES_DIR, filename), 'rb'))
    
    for nurse in self.nurses:
      for old_nurse in old_nurses:
        if nurse == old_nurse:
          #we can always do that, because the past is always right
          nurse.load_previous_month(old_nurse, prev_date)
    
    
  def __save(self):
    """Saves the schedule"""
    
    filename = str(self.date.month) + '_' + str(self.date.year) + '.dat'
    pickle.dump(self.nurses, file(os.path.join(NurseScheduler.FILES_DIR, filename), 'wb'))
       

  def schedule(self):
    days = self.__get_days()
    month = self.date.month
    year = self.date.year
    
    #two iterations: the first schedules normal nurses, the second schedules 
    #part-time nurses
    
    #first iteration
    first_iteration_nurses = set()
    second_iteration_nurses = set()
    for nurse in self.nurses:
      if nurse.employment_type.weekly_hours == 20:
        second_iteration_nurses.add(nurse)
      else:
        first_iteration_nurses.add(nurse)
    
    #start with first day and continue forward
    for day in days:
      date = datetime.date(day = day, month = month, year = year)
      self.__schedule_date(first_iteration_nurses, date)
      
  
  def __schedule_date(self, nurses, date):
    #schedule workplace
    for workplace in self.workplaces:
      self.__schedule_workplace(nurses, date, workplace)
      
      
  def __schedule_workplace(self, nurses, date, workplace):
    nurses = self.workplace_nurses[workplace].intersection(nurses)
    
  
  def __get_heuristic_score(self, nurses):
    pass
  
  def __get_days(self):
    """Returns a sorted list of days for the scheduling date"""
    days = []
    for day in calendar.Calendar().itermonthdays(self.date.year, self.date.month):
      if day:
        days.append(day)
        
    days.sort()
    
    return days