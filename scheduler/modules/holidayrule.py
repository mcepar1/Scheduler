# -*- coding: Cp1250 -*-

"""
This plugin is responsible for properly scheduling the special holiday rule
workplaces and three day night turnus packet.
"""
from utils import holiday, calendar_utils
from data import turnus_type
from scheduler import schedule_utils

import global_vars

import datetime
import random

"""
The main plug-in class.
"""
class HolidayRulePlugin:
  
  def __init__(self, people, workplaces, turnuses, date, logger):
    """
    The default constructor. Only the parameters listed bellow are used, the rest are 
    discarded.
      people: a sequence of people, that will be pre-scheduled
      date: an instance of the datetime.date object, that has the correct month and year
    """
    
    self.people = people
    self.workplaces = workplaces
    self.turnuses = turnuses
    self.date = date
    self.log = logger
    
    #maps workplaces to people
    self.workplace_people = {}
    for workplace in self.workplaces:
      self.workplace_people[workplace] = set()
    
    for workplace in self.workplaces:
      self.workplace_people[workplace] = set()
      for person in self.people:
        if workplace in person.workplaces:
          self.workplace_people[workplace].add(person)
    
    #maps turnuses to people
    self.turnus_people = {}
    for turnus in self.turnuses:
      self.turnus_people[turnus] = set ()
    
    for person in self.people:
      for turnus in person.allowed_turnuses:
        if turnus not in self.turnus_people:
          self.turnus_people[turnus] = set()
        self.turnus_people[turnus].add(person)
        
    #determine the people without overtime
    self.no_overtime_people = set()
    for person in self.people:
      if not person.employment_type.has_overtime:
        self.no_overtime_people.add(person)
    
    # maps roles to people    
    self.role_people = {}
    for person in self.people:
      for workplace in person.roles:
        for role in person.roles[workplace]:
          if role not in self.role_people:
            self.role_people[role] = set()
          self.role_people[role].add (person)
    
  def perform_task(self, overtime=False):
    """Schedules."""
        
    if overtime:
      people = set(self.people) - self.no_overtime_people
    else:
      people = set(self.people)
    
    self.__preschedule_packet_night_turnuses(people, overtime)  
    self.__preschedule_workfree_days(people, overtime)
     
     

  def __preschedule_workfree_days(self, people, overtime=False):
    """
    Schedules the special holidays rule workplaces outside the normal scheduling
    procedure.
      people: a sequence of people, that will be scheduled
      overtime: allows, people to go into overtime (if true)
    """
    #This is not included in the prescheduler, because it is not prescheduled.
    #It is scheduled automatically, only outside the normal scheduling scope.
    
    dates = calendar_utils.get_workfree_dates (self.date)
    
    workplaces = []
    for workplace in self.workplaces:
      if workplace.holiday_rule:
        workplaces.append(workplace)
        
    pre_holiday_turnuses = []
    for turnus in self.turnuses:
      if turnus_type.TurnusType('Popoldanski') in turnus.types:
        pre_holiday_turnuses.append(turnus)
      if turnus_type.TurnusType('Celodnevni') in turnus.types:
        pre_holiday_turnuses.append(turnus)
        
    holiday_turnuses = []
    for turnus in self.turnuses:
      if turnus.holiday:
        holiday_turnuses.append(turnus)
    
    random.shuffle(workplaces)  
    for workplace in workplaces:
      for holiday_date in dates:
        pre_holiday_date = holiday_date - datetime.timedelta(days=1)
        
        pre_holiday_workers = workplace.get_workers(pre_holiday_date)
        holiday_workers = workplace.get_workers(holiday_date)
        
        roles = list(set(pre_holiday_workers.keys()) & set(holiday_workers.keys()))
        
        random.shuffle(pre_holiday_turnuses)
        random.shuffle(holiday_turnuses)
        random.shuffle(roles)
        for role in roles:
          for pre_holiday_turnus in pre_holiday_turnuses:
            for holiday_turnus in holiday_turnuses:
              
              # there is no guarantee that a workplace will have all holiday and preholdiay turnuses
              if not (set (pre_holiday_turnus.types) & set (pre_holiday_workers[role])):
                continue
              if not (set (holiday_turnus.types) & set (holiday_workers[role])):
                continue
              
              scheduled = True
              
              while self.__can_continue_scheduling(self.__get_alerady_scheduled_by_type(workplace, role, pre_holiday_turnus.types, pre_holiday_date), pre_holiday_workers[role]) \
              and   self.__can_continue_scheduling(self.__get_alerady_scheduled_by_type(workplace, role, holiday_turnus.types, holiday_date), holiday_workers[role]) \
              and scheduled:
              
                scheduled = False
              
                #does not take into account both days
                heuristic_people = schedule_utils.get_heuristic_sorted_people(people & self.workplace_people[workplace] & self.turnus_people[holiday_turnus] & self.role_people[role], holiday_date)
                
                for person in heuristic_people:
                  if \
                  self.__is_valid_move_preschedule(workplace, role, pre_holiday_turnus, pre_holiday_date, person, overtime) \
                  and \
                  self.__is_valid_move_preschedule(workplace, role, holiday_turnus, holiday_date, person, overtime):
                    person.schedule_turnus(pre_holiday_date, pre_holiday_turnus, workplace, role)
                    person.schedule_turnus(holiday_date, holiday_turnus, workplace, role)
                    scheduled = True
                    break
                
  def __preschedule_packet_night_turnuses(self, people, overtime):
    """Schedules the Friday-Saturday-Sunday night turnus package"""
    
    packet_people = set()
    for person in people:
      if person.packet_night_turnuses:
        packet_people.add(person)
        
    pre_holiday_night_turnuses = []
    holiday_night_turnuses = []
    for turnus in self.turnuses:
      if turnus_type.TurnusType('Nočni') in turnus.types:
        if turnus.holiday:
          holiday_night_turnuses.append(turnus)
        else:
          pre_holiday_night_turnuses.append(turnus)
          
    workplaces = []
    for workplace in self.workplaces:
      if workplace.holiday_rule:
        workplaces.append(workplace)
        
    date_packs = self.__get_friday_saturday_sunday_dates()
    random.shuffle(date_packs)
    
    random.shuffle(workplaces)  
    for workplace in workplaces:
      for date_pack in date_packs:
        
        workers = [workplace.get_workers(date_pack[0]), workplace.get_workers(date_pack[1]), workplace.get_workers(date_pack[2])]
        roles = list(set(workers[0].keys()) & set(workers[1].keys()) & set(workers[2].keys()))
        
        random.shuffle(roles)
        random.shuffle(pre_holiday_night_turnuses)
        random.shuffle(holiday_night_turnuses)
        
        for role in roles:
          for pre_holiday_night_turnus in pre_holiday_night_turnuses:
            for holiday_night_turnus in holiday_night_turnuses:
              
              # there is no guarantee that a workplace will have all holiday and preholdiay turnuses
              if not (set (pre_holiday_night_turnus.types) & set (workers[0][role])):
                continue
              if not (set (pre_holiday_night_turnus.types) & set (workers[1][role])):
                continue
              if not (set (holiday_night_turnus.types) & set (workers[2][role])):
                continue
              
              scheduled = True
              
              while self.__can_continue_scheduling(self.__get_alerady_scheduled_by_type(workplace, role, pre_holiday_night_turnus.types, date_pack[0]), workers[0][role]) \
              and   self.__can_continue_scheduling(self.__get_alerady_scheduled_by_type(workplace, role, pre_holiday_night_turnus.types, date_pack[1]), workers[1][role]) \
              and   self.__can_continue_scheduling(self.__get_alerady_scheduled_by_type(workplace, role, holiday_night_turnus.types, date_pack[2]), workers[2][role]) \
              and   scheduled:
              
                scheduled = False
              
                #does not take into account all days
                heuristic_people = schedule_utils.get_heuristic_sorted_people(packet_people & self.workplace_people[workplace] & self.turnus_people[holiday_night_turnus] & self.role_people[role], date_pack[2])
                
                for person in heuristic_people:
                  if self.__is_valid_move_preschedule_packet(workplace, role, pre_holiday_night_turnus, date_pack[0], person, overtime):
                    person.schedule_turnus(date_pack[0], pre_holiday_night_turnus, workplace, role)
                    if not person.is_blocked (date_pack[0] - datetime.timedelta(days=1), pre_holiday_night_turnus):
                      person.add_invalid_turnus(date_pack[0] - datetime.timedelta(days=1),pre_holiday_night_turnus)
                    
                    if self.__is_valid_move_preschedule_packet(workplace, role, pre_holiday_night_turnus, date_pack[1], person, overtime):
                      person.schedule_turnus(date_pack[1], pre_holiday_night_turnus, workplace, role)
                      
                      if self.__is_valid_move_preschedule_packet(workplace, role, holiday_night_turnus, date_pack[2], person, overtime):
                        person.schedule_turnus(date_pack[2], holiday_night_turnus, workplace, role)
                        scheduled = True
                        
                        if not person.is_blocked (date_pack[2] + datetime.timedelta(days=1), pre_holiday_night_turnus):
                          person.add_invalid_turnus(date_pack[2] + datetime.timedelta(days=1),pre_holiday_night_turnus)
                        break
                        
                      else:
                        person.clear_date(date_pack[0])
                        person.clear_date(date_pack[1])
                        
                        person.remove_invalid_turnus(date_pack[2] + datetime.timedelta(days=1),pre_holiday_night_turnus)
                      
                    else:
                      person.clear_date(date_pack[0])
                      person.remove_invalid_turnus(date_pack[0] - datetime.timedelta(days=1),pre_holiday_night_turnus)
        
      
      
  def __is_valid_move_preschedule(self, workplace, role, turnus, date, person, overtime):
    """
    Checks, if the person is allowed to work, on the combination of attributes. This function
    is identical to the is_valid_move function. The only difference is that it does not
    check the holiday workplace rule.
      workplace: is the workplace checked
      role: is the role checked
      turnus: is the turnus checked
      date: is the date checked
      person: is the person checked
      overtime: if the overtime is allowed for the person
    """
    
    if not schedule_utils.is_valid_move (workplace, role, turnus, date, person, overtime):
      return False
      
    if holiday.is_workfree(date):      
      #check for free days
      #check previous week
      week = calendar_utils.get_previous_week(date)
      for date_ in week:
        if person.is_free_day(date_):
          break
      else:
        #if there was no free day the previous week, perhaps there is in the next
        week = calendar_utils.get_next_week(date)
        for date_ in week:
          if person.is_free_day(date_):
            break
        else:
          # no free day was found
          return False
      
        
              
    return True
  
  def __is_valid_move_preschedule_packet(self, workplace, role, turnus, date, person, overtime, depth=0, check_turnuses=[]):
    """
    Checks, if the person is allowed to work, on the combination of attributes. This function
    is identical to the is_valid_move_preschedule function. The only difference is that 
    it does not check for night turnus packets.
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
    
    if not schedule_utils.is_valid_move (workplace, role, turnus, date, person, overtime):
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
        
              
    return True
  
  def __can_continue_scheduling(self, scheduled_types, workers):
    """
    Checks, if the workplace has enough people working at it, to be considered
    full.
      scheduled_types: a dictionary, that maps turnus types to the number of 
                       currently scheduled turnuses of that type
      workers: a dictionary, that maps turnus types to the number of required
               scheduled turnuses of that type
      return: true, if there aren't enough people working, false otherwise
    """
    
    for type in scheduled_types:
      if scheduled_types[type] < workers[type]:
        return True
    
    return False
  
  def __get_alerady_scheduled_by_type(self, workplace, role, types, date):
    """
    Return the number of currently scheduled people for the specific types
    date and workplace
      workplace: is the workplace
      role: is the role
      types: is the sequence of types
      date: is the date
      return: a dictionary, that maps types to the number of scheduled turnuses
              for each type
    """
    
    map = {}
    
    for type in types:
      turnuses = global_vars.get_turnuses ( ).get_by_type(type, workplace)
      map[type] = 0
      for turnus in turnuses:
        map[type] += self.__get_already_scheduled(workplace, role, turnus, date)
      
    return map
  
  def __get_already_scheduled(self, workplace, role, turnus, date):
    """
    Returns the number of currently scheduled people, for the specific turnus, 
    date and workplace.
      workplace: is the workplace
      role: is the role
      turnus: is the turnus
      date: is the date
      return: the number of people
    """
    
    number = 0
    for person in self.people:
      if person.is_scheduled_exact(workplace, role, turnus, date):
        number += 1
    
    return number
  
  def __get_friday_saturday_sunday_dates(self):
    """Returns a sorted list of 3-tuples (Friday, Saturday, Sunday) for the scheduling date"""
    dates = []
    for date in calendar_utils.get_same_month_dates (self.date):
      if date.weekday ( ) == 4:
        dates.append ((date, date + datetime.timedelta (days=1), date + datetime.timedelta (days=2)))
          
    return dates
    
