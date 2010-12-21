# -*- coding: utf-8 -*-
from global_vars import turnuses
from utils import holiday, time_conversion

import calendar
import datetime
import random

class FillHours:
  
  def __init__(self, people, workplaces, turnuses, date, logger):
      """
      The default constructor. Only the parameters listed bellow are used, the rest are 
      discarded.
        people: a sequence of people, that will be pre-scheduled
        workplace: a sequence of scheduler workplaces
        date: an instance of the datetime.date object, that has the correct month and year
      """
      
      self.people = people
      self.workplaces = workplaces
      self.date   = date
      
  def perform_task(self, overtime=False):
    """Schedules."""
    
    people = list (self.people)
    random.shuffle (people)
        
    for person in people:
      if person.get_monthly_hours_difference (self.date) > 0:
        # fill hours
        self.__fill_person(person)
      
  def __fill_person (self, person):
    """
    Schedules the person, until the person has overtime.
    person: the person, that will be sheduled
    """
    
    scheduled = True
    while person.get_monthly_hours_difference (self.date) > 0 and scheduled:
      scheduled = False
      #schedule person
      schedule_pairs = self.__get_emptiest (person)
      dates = [datetime.date(day=day, month=self.date.month, year=self.date.year) for day in self.__get_days()]
      for date in dates:
        for workplace, role in schedule_pairs:
          for turnus in self.__get_possible_turnuses(workplace, role, date, person):
            if self.__is_valid_move(workplace, role, turnus, date, person, True):
              person.schedule_turnus (date, turnus, workplace, role)
              
              #block the previous day, if it was the night turnus
              prev_date = date - datetime.timedelta(days=1)
              if turnus.code[0] == 'N' and not person.is_blocked(prev_date, turnus):
                person.add_invalid_turnus(prev_date, turnus)
                
              # the is valid move has taken care of any potential violations, so that you
              # can just schedule turnuses
              if person.packet_night_turnuses and turnus.code[0] == 'N':
                next_date = date + datetime.timedelta(days=1)
                person.schedule_turnus (next_date, turnus, workplace, role)
                #if it is Saturday, schedule one more
                if next_date.weekday() == 5:
                  next_date += datetime.timedelta(days=1)
                  #find the workfree night turnus
                  night_turnus = None
                  for temp_turnus in turnuses.turnuses:
                    if temp_turnus.holiday and temp_turnus.code[0] == 'N':
                      night_turnus = temp_turnus
                      break
                  else:
                    raise Exception ('Napaka pri dodajanju osebe z zdruzenimi nocnimi turnusi.')
                  person.schedule_turnus(next_date, night_turnus, workplace, role)
                  if turnus.code[0] == 'N' and not person.is_blocked(next_date + datetime.timedelta(days=1), turnus):
                    person.add_invalid_turnus(next_date + datetime.timedelta(days=1), turnus)
                else:
                  if turnus.code[0] == 'N' and not person.is_blocked(next_date + datetime.timedelta(days=1), turnus):
                    person.add_invalid_turnus(next_date + datetime.timedelta(days=1), turnus)        
              
              if holiday.is_workfree(date):
                self.__add_free_day(person, date)
              scheduled = True
              if person.get_monthly_hours_difference (self.date) <= 0:
                return
            else:
              scheduled = False
              if person.get_monthly_hours_difference (self.date) <= 0:
                return
      
      
  def __get_emptiest (self, person):
    """
    Return a sorted list of 2-tuples. The first element of the tuple is a workplace,
    the second is a role. The list is ascending. The first element is the workplace - 
    role pair that lacks the most nurses, the second lacks the second most nurses.
    It also sorts pairs with sufficient nurses.
      return: a sorted list of 2-tuples
    """
    trios = []
    for workplace in person.roles:
      for role in person.roles[workplace]:
        #transform into a scheduler workplace
        for workplace_ in self.workplaces:
          if workplace == workplace_:
            workplace = workplace_
            break
        else:
          raise Exception ('Workplace error')
        
        trios.append((workplace, role, self.__calculate_emptiness(workplace, role)))
        
    trios.sort(key=lambda trio: trio[2])
    
    pairs = []
    for trio in trios:
      pairs.append((trio[0], trio[1]))
    
    return pairs
        
  def __calculate_emptiness (self, workplace, role):
    """
    Return the total number of missing (positive) or missing (negative) workers 
    for the whole month.
      workplace: the (data) workplace for which the workers will be calculated
      role: is the role for which the workers will be calculated
      return: the difference in workers
    """
    
    # get the correct scheduler workplace
    for workplace_ in self.workplaces:
      if workplace == workplace_:
        workplace = workplace_
        break
    else:
      raise Exception ('Workplace error')
    
    difference = 0
    
    dates = [datetime.date(day=day, month=self.date.month, year=self.date.year) for day in self.__get_days()]
    for date in dates:
      for person in self.people:
        for turnus in turnuses.turnuses:
          if person.is_scheduled_exact(workplace, role, turnus, date):
            difference += 1
    
    workers = workplace.get_workers(date)[role]
    needed = 0
    for turnus in workers:
      needed += workers[turnus]
               
    difference -= needed
    return difference
  
  def __get_possible_turnuses (self, workplace, role, date, person):
    """
    Gets all the possible turnuses, that a person can fill. The possible turnuses
    include those, that at least 1 worker for the specified parameter.
      workplace: is the workplace to be filled
      role: is the role to be filled
      date: is the date to be filled
      person: is the person that will be filled
      return: a randomly sorted list of turnuses
    """
    
    types = workplace.get_workers(date)[role].keys()
    turnus_candidates = workplace.allowed_turnuses & person.allowed_turnuses
    turnus_list = set ()
    for turnus in turnus_candidates:
      for type in turnus.types: 
        if type in types and workplace.get_workers(date)[role][type] > 0:
          turnus_list.add(turnus)
    
    turnus_list = list (turnus_list)
    random.shuffle(turnus_list)
    return turnus_list
  
  def __is_valid_move(self, workplace, role, turnus, date, person, overtime, depth=0, check_turnuses=[]):
    """
    Checks, if the person is allowed to work, on the combination of attributes.
      workplace: is the workplace checked
      role: is the role checked
      turnus: is the turnus checked
      date: is the date checked
      person: is the person checked
      overtime: if the overtime is allowed for the person
      depth: depth of the recursion. Never set this parameter when calling the method 
            form the outside
      check_turnuses: is a list of turnuses. This list contains turnuses that were 
                      checked in the previous recursions. They are needed for calculating
                      the potential overtime. Never set this parameter when calling the
                      method from the outside.
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
      for prev_turnus in check_turnuses:
        duration += time_conversion.timedelta_to_hours(prev_turnus.duration)
      
      if mh - duration < 0:
        return False
      if wh - duration < 0:
        return False
      
    if holiday.is_workfree(date):
      # check if this a turnus, that can be scheduled in a workfree day
      if not turnus.holiday:
        return False
      
      #check for free days
      #check previous week
      week = self.__get_previous_week(date)
      for date_ in week:
        if person.is_free_day(date_):
          break
      else:
        #if there was no free day the previous week, perhaps there is in the next
        week = self.__get_next_week(date)
        for date_ in week:
          if person.is_free_day(date_):
            break
        else:
          # no free day was found
          return False
      
      # if the workplace has the special rule: work in the afternoon, if the next
      # day is a work free day and you will work the next day, and you won't work
      # the next day, work in the morning or not at all
      if workplace.holiday_rule:
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
        return self.__is_valid_move(workplace, role, turnus, date + datetime.timedelta(days=1), person, overtime, depth + 1, check_turnuses + [turnus])
      #if this is the second day in the packet continue validation only if it is a Saturday
      elif depth == 1 and date.weekday() == 5:
        # TODO: allow only one holiday turnus per shift type (document this)
        sunday_night_turnus = None
        for alternative_turnus in turnuses.turnuses:
          if alternative_turnus.holiday and alternative_turnus.code[0] == 'N':
            sunday_night_turnus = alternative_turnus
            break
        else:
          return False
        
        return self.__is_valid_move(workplace, role, sunday_night_turnus, date + datetime.timedelta(days=1), person, overtime, depth + 1, check_turnuses + [turnus])
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
    
    
        
      
    
        