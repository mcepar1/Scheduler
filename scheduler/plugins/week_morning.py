# -*- coding: Cp1250 -*-
from Scheduler.data.turnus_type import TurnusType
from Scheduler.utils import holiday, time_conversion

import datetime
import calendar
import random

class WeekMorning:
  def __init__(self, people, workplaces, turnuses, date, logger):
    """
    The default constructor. Only the parameters listed bellow are used, the rest are 
    discarded.
      people: a sequence of people, that will be pre-scheduled
      date: an instance of the datetime.date object, that has the correct month and year
    """
    
    self.people = set()
    for person in people:
      if person.week_morning:
        self.people.add(person)
        
    self.date = date
    
    self.turnus_type = TurnusType('Dopoldanski')
    
    
  def perform_task(self, overtime=False):
    """Schedules all the predefined constraints. Ignores the parameter."""
    for person in self.people:
      self.__schedule_person(person)
      
  def __schedule_person(self, person):
    """Schedules a single person for the whole month."""
    dates = self.__get_dates()
    
    for date in dates:
      workplaces = list(person.roles.keys())
      random.shuffle(workplaces)
      
      for workplace in workplaces:
        roles = list (person.roles[workplace])
        random.shuffle(roles)
        
        for role in roles:
          turnuses = list(person.allowed_turnuses & workplace.allowed_turnuses)
          random.shuffle(turnuses)
          
          for turnus in turnuses:
            if turnus.code[0] == 'D' and self.__is_valid_move(workplace, role, turnus, date, person, True):
              person.schedule_turnus (date, turnus, workplace, role)
          
  
  def __is_valid_move(self, workplace, role, turnus, date, person, overtime):
    """
    Checks, if the person is allowed to work, on the combination of attributes.
      workplace: is the workplace checked
      role: is the role checked
      turnus: is the turnus checked
      date: is the date checked
      person: is the person checked
      overtime: if the overtime is allowed for the person
    """
    
    
    if turnus not in person.allowed_turnuses:
      return False
    
    if person.is_turnus_forbidden(turnus, date):
      return False
    
    if person.is_blocked(date, turnus):
      return False
    
    #block the workfree night turnus, if the day is not workfree
    if turnus.holiday and turnus.code[0] == 'N' and not holiday.is_workfree(date):
      return False
    
    #check the role
    if role not in workplace.roles or workplace not in person.roles or role not in person.roles[workplace]:
      return False
    
    #also check the people's employment type
    if not overtime or not person.employment_type.has_overtime:
      mh = person.get_monthly_hours_difference(date)
      wh = person.get_weekly_hours_difference(date)
      
      duration = time_conversion.timedelta_to_hours(turnus.duration)
      
      if mh - duration < 0:
        return False
      if wh - duration < 0:
        return False  
              
    return True
   
  def __get_dates (self):
    """Returns a sorted list of all valid dates."""
    pre_dates = [datetime.date(day=day, month=self.date.month, year=self.date.year) for day in self.__get_days()]
    dates = []
    
    for date in pre_dates:
      if not holiday.is_weekend(date) and not holiday.is_holiday(date):
        dates.append(date)
    
    return dates
    
    
  def __get_days(self):
    """Returns a sorted list of days for the scheduling date"""
    days = []
    for day in calendar.Calendar().itermonthdays(self.date.year, self.date.month):
      if day:
        days.append(day)
        
    days.sort()
    
    return days