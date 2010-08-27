# -*- coding: utf-8 -*-
from scheduler import person
from scheduler import workplace as workplace_module
from scheduler import weights
from global_vars import employment_types, turnuses as all_turnuses, workplaces as all_workplaces
from utils import time_conversion, holiday

import random
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
    for workplace in all_workplaces.workplaces:
      self.workplace_nurses[workplace] = set()
    
    for workplace in self.workplaces:
      self.workplace_nurses[workplace] = set()
      for nurse in self.nurses:
        if workplace in nurse.workplaces:
          self.workplace_nurses[workplace].add(nurse)
        
    #maps employment types to nurses
    self.employment_type_nurses = {}
    for employment_type in employment_types.employment_types:
      self.employment_type_nurses[employment_type] = set ()
    
    for nurse in self.nurses:
      if nurse.employment_type not in self.employment_type_nurses:
        self.employment_type_nurses[nurse.employment_type] = set()
      self.employment_type_nurses[nurse.employment_type].add(nurse)
      
    #maps turnuses to nurses
    self.turnus_nurses = {}
    for turnus in all_turnuses.turnuses:
      self.turnus_nurses[turnus] = set ()
    
    for nurse in self.nurses:
      for turnus in nurse.allowed_turnuses:
        if turnus not in self.turnus_nurses:
          self.turnus_nurses[turnus] = set()
        self.turnus_nurses[turnus].add(nurse)
      
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
    dates = [datetime.date(day=day, month=self.date.month, year=self.date.year) for day in self.__get_days()]
    
    
    nurses = set()
    for employment_type in self.employment_type_nurses:
      #exclude the part time employees
      if employment_type != employment_types.employment_types[1]:
        nurses = nurses | self.employment_type_nurses[employment_type]
    
    # for each date and workplace go through each allowed turnus and add 
    # one employee, until reaching the point, where the overtime is needed
    # or enough workers are working in a turnus
    scheduled = True
    while (scheduled):
      #start with workplaces
      random.shuffle(self.workplaces)
      
      scheduled = False
      for workplace in self.workplaces:
        for date in dates:
          scheduled = scheduled | self.__schedule_workplace(workplace, date, nurses, overtime=False)
          
    self.__debug_print()
    
  def __schedule_workplace(self, workplace, date, nurses=[], overtime=False):
    """
    Schedules a single nurse into each allowed workplace's turnus.
      workplace: the workplace, that will be scheduled
      date: the date for which the scheduling will occur
      nurses: a collection of nurses to chose form, default value is an empty list
      overtime: allow scheduling nurses with overtime, default value is false
      return: false, if no nurse was scheduled, true if at least one nurse was scheduled
    """
    
    workers = workplace.get_workers()
    turnuses = workers.keys()
    random.shuffle(turnuses)

    
    scheduled = False
    
    #always start with the night shift, because it requires the nurse, to be scheduled
    #across multiple days
    if all_turnuses.turnuses[3] in turnuses:
      turnuses.remove(all_turnuses.turnuses[3])
      
      #if there are enough workers, schedule none
      if self.__get_already_scheduled(workplace, all_turnuses.turnuses[3], date) < workers[all_turnuses.turnuses[3]]:        
        heuritsitc_nurses = self.__get_heuristic_sorted_nurses(nurses & self.workplace_nurses[workplace] & self.turnus_nurses[all_turnuses.turnuses[3]] , date)
        while (len(heuritsitc_nurses) > 0):
          nurse = heuritsitc_nurses.pop(0)
          if self.__schedule_nurse(workplace, all_turnuses.turnuses[3], date, nurse, overtime):
            scheduled = scheduled | True
            break
          else:
            scheduled = scheduled | False 
      else:
        scheduled = scheduled | False
      
      
    for turnus in turnuses:
      #if there are enough workers, schedule none
      if self.__get_already_scheduled(workplace, turnus, date) < workers[turnus]:
        heuritsitc_nurses = self.__get_heuristic_sorted_nurses(nurses & self.workplace_nurses[workplace] & self.turnus_nurses[turnus] , date)
        while (len(heuritsitc_nurses) > 0):
          nurse = heuritsitc_nurses.pop(0)
          if self.__schedule_nurse(workplace, turnus, date, nurse, overtime):
            scheduled = scheduled | True
            break
          else:
            scheduled = scheduled | False
      else:
        scheduled = scheduled | False
        
    return scheduled
      
  def __schedule_nurse(self, workplace, turnus, date, nurse, overtime):
    """
    Tries to schedule the nurse.
      workplace: is the workplace, that we want scheduled
      turnus: is the turnus, that we want scheduled
      date: is the turnus, that we want scheduled
      nurse: is the nurse, that we want scheduled
      overtime: if true, overtime is allowed
      return: true: if the nurse was scheduled, false otherwise
    """
    
    if self.__is_valid_move(workplace, turnus, date, nurse, overtime):
      nurse.schedule_turnus (date, turnus, workplace)
      if holiday.is_workfree(date):
        self.__add_free_day(nurse, date)
      return True
    else:
      return False
    

  def __is_valid_move(self, workplace, turnus, date, nurse, overtime, depth=0):
    """
    Checks, if the nurse is allowed to work, on the combination of attributes.
      workplace: is the workplace checked
      turnus: is the turnus checked
      date: is the date checked
      nurse: is the nurse checked
      overtime: if the overtime is allowed for the nurse
      depth: depth of the recursion. Never set this paramter when calling the method 
            form the outside
    """
    
    
    if nurse.is_scheduled(date):
      return False
    
    if turnus not in nurse.allowed_turnuses:
      return False
    
    if nurse.is_turnus_forbidden(turnus, date):
      return False
    
    if not overtime:
      mh = nurse.get_monthly_hours_difference(date)
      wh = nurse.get_weekly_hours_difference(date)
      
      duration = time_conversion.timedelta_to_hours(turnus.duration)
      
      if mh - duration < 0:
        return False
      if wh - duration < 0:
        return False
      
    if holiday.is_workfree(date):
      #check previous week
      week = self.__get_previous_week(date)
      for date_ in week:
        if nurse.is_free_day(date_):
          break
      else:
        #if there was no free day the previous week, perhaps there is in the next
        week = self.__get_next_week(date)
        for date_ in week:
          if nurse.is_free_day(date_):
            break
        else:
          # no free day was found
          return False
      
      
        
    #if it is the night shift check the next days
    #if turnus == all_turnuses.turnuses[3]:
      #if it is not Saturday or Sunday, one additional day is enough
    #  if date.weekday() < 5 and depth < 1:
    #    return self.__is_valid_move(workplace, turnus, date + datetime.timedelta(days=1), nurse, overtime, depth + 1)
      #if it is Saturday, check Sunday
    #  if date.weekday() == 5 and depth == 1:
    #    return self.__is_valid_move(workplace, turnus, date + datetime.timedelta(days=1), nurse, overtime, depth + 1)
      #if it Sunday, no lookahead is required
    
          
    return True
  
  def __add_free_day(self, nurse, date):
    """
    Adds a free day to the nurse, if necessary. See the person.Nurse.is_free_day_for 
    details.
      nurse: the nurse that needs a free day
      date: is the date that contains the week in which the nurse worked on a work
            free day
    """
    
    #check previous week
    week = self.__get_previous_week(date)
    for date_ in week:
      if nurse.is_free_day(date_):
        return
    else:
      #if there was no free day the previous week, perhaps there is in the next
      week = self.__get_next_week(date)
      free_day = []
      for date_ in week:
        if nurse.is_free_day(date_):
          free_day.append(date_)
      
      if free_day:
        # add a random not yet scheduled day as a free day
        nurse.add_free_day(random.choice(free_day))
      else:
        raise Exception('Nisem mogel dodati prostega dneva.')

  def __get_heuristic_sorted_nurses(self, nurses, date):
    """
    Returns a sorted list of nurses, according to their heuristic score.
      nurses: the list of nurses, to be sorted
      date: the date that we want scheduled
      return: a list of nurses
    """
    
    temp = {}
    result = []
    
    for nurse in nurses:
      heuristic_score = self.__get_heuristic_score(nurse, date)
      if heuristic_score not in temp:
        temp[heuristic_score] = []
      temp[heuristic_score].append(nurse)
      
    for heuristic_score in sorted(temp.keys()):
      result += temp[heuristic_score]
      
    return result
    
  
  def __get_heuristic_score(self, nurse, date):
    """
    Returns a value. The higher the value, the worst choice the person is.
      nurse: is the person, that will have the score computed
      date: is the date, that we want scheduled
      return: a float
    """
    
    month_hours = -1 * nurse.get_monthly_hours_difference(date)
    week_hours = -1 * nurse.get_weekly_hours_difference(date)
    turnus_dispersion = nurse.get_turnus_dispersion()
    workplace_dispersion = nurse.get_workplace_dispersion()
    
    return weights.MONTH_HOURS * month_hours + weights.WEEK_HOURS * week_hours + weights.TURNUS_DISPERSION * turnus_dispersion + weights.WORKPLACE_DISPERSION * workplace_dispersion
  
  
  def __get_already_scheduled(self, workplace, turnus, date):
    """
    Returns the number of currently scheduled persons, for the specific turnus, 
    date and workplace.
      workplace: is the workplace
      turnus: is the turnus
      date: is the date
      return: the number of nurses
    """
    
    number = 0
    for nurse in self.nurses:
      if nurse.is_scheduled_exact(workplace, turnus, date):
        number += 1
    
    return number
    
  def __get_scheduled_nurses(self, date):
    """
    Returns a set of nurses, that are already scheduled.
      date: is the date that is checked
      return: a set
    """
    
    scheduled = set()
    for nurse in self.nurses:
      if nurse.is_scheduled(date):
        scheduled.add(nurse)
    
    return scheduled
  
  
  def __get_days(self):
    """Returns a sorted list of days for the scheduling date"""
    days = []
    for day in calendar.Calendar().itermonthdays(self.date.year, self.date.month):
      if day:
        days.append(day)
        
    days.sort()
    
    return days
  
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
  
  def __get_next_week(self, date):
    """
    Returns all dates in the week after the week in which the date is located.
      date: instance of the datetime.date class
      return: a list of dates
    """
      
    return self.__get_week(date + datetime.timedelta(days=7))
  
  def __get_previous_week(self, date):
    """
    Returns all dates in the week after the week in which the date is located.
      date: instance of the datetime.date class
      return: a list of dates
    """
      
    return self.__get_week(date + datetime.timedelta(days= -7))
  
  def __debug_print(self):
    min_date = datetime.date(day=1, month=self.date.month, year=self.date.year)
    
    for nurse in self.nurses:
      print str(nurse)
      schedule = nurse.get_schedule()
      for date in sorted(schedule.keys()):
        if date >= min_date:
          print '\tDate: ' + str(date)
          print '\t\t Turnus: ' + str(schedule[date][0])
          print '\t\t Workplace: ' + str(schedule[date][1])
      print ''
