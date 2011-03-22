# -*- coding: Cp1250 -*-

"""
This is the core scheduling module.
"""
import random
import datetime

from utils import holiday
from scheduler import schedule_utils

class CoreModule:
  
  def __init__(self, mapper, workers, date, logger):
    """
    The default constructor. Only the parameters listed bellow are used, the rest are 
    discarded.
      @param mapper: a mapper object
      @param workers: the workers object
      @param date: a datetime.date object, that has the correct month and year
      @logger: a logger
    """
    
    self.mapper  = mapper
    self.workers = workers
    self.date    = date
    self.log     = logger
    
  
  def perform_task (self, overtime=False):
    """
    Schedules.
      @param overtime: determines, if the persons are allowed to work in overtime. Default is False
    """
  
    #for each date and workplace go through each allowed turnus and add 
    #one employee, until reaching the point, where the overtime is needed
    #or enough workers are working in a turnus
    scheduled = True
    
    while (scheduled):
      #start with workplaces
      scheduling_units = self.mapper.get_scheduling_units ( )
      random.shuffle (list (scheduling_units))
      
      scheduled = False
      for scheduling_unit in scheduling_units:
        for date in self.workers.get_dates ( ):
          scheduled = scheduled | self.__schedule_scheduling_unit (scheduling_unit, date, self.mapper.get_all_people ( ), overtime)
          
  def __schedule_scheduling_unit (self, scheduling_unit, date, people=[], overtime=False):
    """
    Schedules a single person into the scheduling unit.
      @param scheduling_unit: a data object
      @param date: a datetime.date object
      @param people: a list of data objects
      @param overtime: determines, if the persons are allowed to work in overtime. Default is False
      @return: True, if at least one person was scheduled, False otherwise
    """

    turnuses = list (scheduling_unit.get_allowed_turnuses ( ))    
    random.shuffle(turnuses)

    
    scheduled = False
    for turnus in turnuses:
      #if there are enough workers, schedule none
      if schedule_utils.get_alerady_scheduled_by_type (self.mapper, scheduling_unit, turnus.types, date) < self.workers.get_workers_by_type (date, scheduling_unit, turnus):
        heuritsitc_people = schedule_utils.get_heuristic_sorted_people (people & self.mapper.get_scheduling_unit_people (scheduling_unit) & self.mapper.get_turnus_people (turnus), date)
        while (len(heuritsitc_people) > 0):
          person = heuritsitc_people.pop(0)
          if self.__schedule_person(scheduling_unit, turnus, date, person, overtime):
            scheduled = scheduled | True
            break
          else:
            scheduled = scheduled | False
      else:
        scheduled = scheduled | False
        
    return scheduled
  
  def __schedule_person(self, scheduling_unit, turnus, date, person, overtime):
    """
    Tries to schedule the person.
      @param scheduling_unit: a data object
      @param turnus: a data object
      @param date: a datetime.date object
      @param person: a data object
      @param overtime: determines, if the persons are allowed to work in overtime. Default is False
      @return: True, if the person was scheduled, False otherwise
    """
    
    if self.__is_valid_move(scheduling_unit, turnus, date, person, overtime):
      person.schedule_turnus (date, turnus, scheduling_unit)
      
      #block the previous and next days, if it was the night turnus
      if turnus.code[0] == 'N' and not person.is_blocked(date - datetime.timedelta(days=1), turnus):
        person.add_invalid_turnus(date - datetime.timedelta(days=1), turnus)
        person.add_invalid_turnus(date + datetime.timedelta(days=1), turnus)
        
      
      # the is valid move has taken care of any potential violations, so that you
      # can just schedule turnuses
      if person.packet_night_turnuses and turnus.code[0] == 'N':
        next_date = date + datetime.timedelta(days=1)
        person.schedule_turnus (next_date, turnus, scheduling_unit)
        #if it is Saturday, schedule one more
        if next_date.weekday() == 5:
          next_date += datetime.timedelta(days=1)
          #find the workfree night turnus
          night_turnus = None
          for temp_turnus in self.mapper.get_turnuses (scheduling_unit, person):
            if temp_turnus.holiday and temp_turnus.code[0] == 'N':
              night_turnus = temp_turnus
              break
          else:
            raise Exception ('Napaka pri dodajanju osebe z zdruzenimi nocnimi turnusi.')
          person.schedule_turnus(next_date, night_turnus, scheduling_unit)
          if turnus.code[0] == 'N' and not person.is_blocked(next_date + datetime.timedelta(days=1), turnus):
            person.add_invalid_turnus(next_date + datetime.timedelta(days=1), turnus)
        else:
          if turnus.code[0] == 'N' and not person.is_blocked(next_date + datetime.timedelta(days=1), turnus):
            person.add_invalid_turnus(next_date + datetime.timedelta(days=1), turnus)
      
      if holiday.is_workfree(date):
        schedule_utils.add_free_day (person, date)
      return True
    else:
      return False

  def __is_valid_move(self, scheduling_unit, turnus, date, person, overtime, depth=0, check_turnuses=[]):
    """
    Checks, if the person is allowed to work, on the combination of attributes.
      @param scheduling_unit: a data object
      @param turnus: a data object
      @param date: a datetime.date object
      @param person: a data object
      @param overtime: determines, if the persons are allowed to work in overtime
      @param depth: depth of the recursion. Never set this parameter when calling the method 
             form the outside
      @param check_turnuses: is a list of turnuses. This list contains turnuses that were 
                             checked in the previous recursions. They are needed for calculating
                             the potential overtime. Never set this parameter when calling the
                             method from the outside.
      @return: True, if the move is valid, False otherwise
    """
    
    
    if not schedule_utils.is_valid_move  (scheduling_unit, turnus, date, person, overtime):
      return False     
      
      # if the workplace has the special rule: work in the afternoon, if the next
      # day is a work free day and you will work the next day, and you won't work
      # the next day, work in the morning or not at all
      if scheduling_unit.has_holiday_rule ( ):
        if holiday.is_workfree(date):
          prev_date = date - datetime.timedelta(days=1)
          prev_turnus = person.get_turnus(prev_date) 
          if prev_turnus:
            # all afternoon codes start with P
            # all double shift codes start with C
            # TODO: document this
            if prev_turnus.code[0] != 'P' or prev_turnus.code[0] != 'C':
              return False
          else:
            return False
        else:
          next_date = date + datetime.timedelta(days=1)
          if holiday.is_workfree(next_date):
            # this bottom condition is enough, because the dates are added ascending
            if not person.is_free_day(next_date):
              return False
    
    # if the person schedules night turnuses in packages: 
    #  (Monday + Tuesday)
    #  (Tuesday + Wednesday)
    #  (Wednesday + Thursday)
    #  (Friday + Saturday + Sunday)
    if person.packet_night_turnuses and turnus.code[0] == 'N':
      if depth == 0 and (date.weekday() == 0 or date.weekday() == 2 or date.weekday() == 4):
        return self.__is_valid_move(scheduling_unit, turnus, date + datetime.timedelta(days=1), person, overtime, depth + 1, check_turnuses + [turnus])
      #if this is the second day in the packet continue validation only if it is a Saturday
      elif depth == 1 and date.weekday() == 5:
        # TODO: allow only one holiday turnus per shift type (document this)
        sunday_night_turnus = None
        for alternative_turnus in self.mapper.get_turnuses (scheduling_unit, person):
          if alternative_turnus.holiday and alternative_turnus.code[0] == 'N':
            sunday_night_turnus = alternative_turnus
            break
        else:
          return False
        
        return self.__is_valid_move(scheduling_unit, sunday_night_turnus, date + datetime.timedelta(days=1), person, overtime, depth + 1, check_turnuses + [turnus])
      #Thursday to Friday combination does not exist
      elif depth == 1 and date.weekday() == 4:
        return False
      elif depth == 1:
        return True
      elif depth == 2:
        return True
      
      else:
        return False
        
              
    return True