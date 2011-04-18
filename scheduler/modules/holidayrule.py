# -*- coding: Cp1250 -*-

"""
This plugin is responsible for properly scheduling the special holiday rule
workplaces and three day night turnus packet.
"""
from utils import holiday, calendar_utils
from data import turnus_type
from scheduler import schedule_utils

import datetime
import random

"""
The main plug-in class.
"""
class HolidayRuleModule:
  
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
    
  def perform_task(self, overtime=False):
    """Schedules."""
        
    if overtime:
      people = self.mapper.get_no_overtime_people ( )
    else:
      people = self.mapper.get_all_people ( )
    
    self.__preschedule_packet_night_turnuses (people, overtime)  
    self.__preschedule_workfree_days (people, overtime)
     
     

  def __preschedule_workfree_days(self, people, overtime=False):
    """
    Schedules the special holidays rule workplaces outside the normal scheduling
    procedure.
      people: a sequence of people, that will be scheduled
      overtime: allows, people to go into overtime (if true)
    """
    #This is not included in the prescheduler, because it is not prescheduled.
    #It is scheduled automatically, only outside the normal scheduling scope.
    
    dates = calendar_utils.get_pre_workfree_dates (self.date)
    
    scheduling_units = []
    for scheduling_unit in self.mapper.get_scheduling_units ( ):
      if scheduling_unit.has_holiday_rule ( ):
        scheduling_units.append (scheduling_unit)
        
    
    random.shuffle (scheduling_units)  
    for scheduling_unit in scheduling_units:
      
      pre_holiday_turnuses = []
      for turnus in self.mapper.get_turnuses (scheduling_unit):
        if turnus_type.TurnusType('Popoldanski') in turnus.types:
          pre_holiday_turnuses.append(turnus)
        if turnus_type.TurnusType('Celodnevni') in turnus.types:
          pre_holiday_turnuses.append(turnus)
          
      holiday_turnuses = []
      for turnus in self.mapper.get_turnuses (scheduling_unit):
        if turnus.holiday and turnus_type.TurnusType('Celodnevni') in turnus.types:
          holiday_turnuses.append(turnus)
      
      for pre_holiday_date in dates:
        holiday_date = pre_holiday_date + datetime.timedelta(days=1)
        
        random.shuffle (pre_holiday_turnuses)
        random.shuffle (holiday_turnuses)
        for pre_holiday_turnus in pre_holiday_turnuses:
          for holiday_turnus in holiday_turnuses:
            
            pre_holiday_workers = self.workers.get_workers_by_type (pre_holiday_date, scheduling_unit, pre_holiday_turnus)
            holiday_workers     = self.workers.get_workers_by_type (holiday_date,     scheduling_unit, holiday_turnus)
            
            scheduled = True
            
            while (schedule_utils.get_alerady_scheduled_by_type (self.mapper, scheduling_unit, pre_holiday_turnus.types, pre_holiday_date) < pre_holiday_workers) \
            and   (schedule_utils.get_alerady_scheduled_by_type (self.mapper, scheduling_unit, holiday_turnus.types,     holiday_date)     < holiday_workers) \
            and scheduled:
            
              scheduled = False
            
              #does not take into account both days
              heuristic_people = schedule_utils.get_heuristic_sorted_people (people & self.mapper.get_scheduling_unit_people (scheduling_unit) & self.mapper.get_turnus_people (holiday_turnus), holiday_date)
              
              for person in heuristic_people:
                if \
                self.__is_valid_move_preschedule (scheduling_unit, pre_holiday_turnus, pre_holiday_date, person, overtime) \
                and \
                self.__is_valid_move_preschedule (scheduling_unit, holiday_turnus, holiday_date, person, overtime):
                  person.schedule_turnus (pre_holiday_date, pre_holiday_turnus, scheduling_unit)
                  person.schedule_turnus (holiday_date,     holiday_turnus,     scheduling_unit)
                  scheduled = True
                  break
                
  def __preschedule_packet_night_turnuses(self, people, overtime):
    """Schedules the Friday-Saturday-Sunday night turnus package"""
    
    packet_people = set ( )
    for person in people:
      if person.packet_night_turnuses:
        packet_people.add(person)
          
    scheduling_units = self.mapper.get_scheduling_units ( )
    random.shuffle (list (scheduling_units))
        
    date_packs = self.__get_friday_saturday_sunday_dates ( )
    random.shuffle (date_packs)
    
      
    for scheduling_unit in scheduling_units:
      
      pre_holiday_night_turnuses = []
      holiday_night_turnuses     = []
      for turnus in self.mapper.get_turnuses (scheduling_unit=scheduling_unit):
        if turnus_type.TurnusType('Nočni') in turnus.types: #TODO: document hard-coded
          if turnus.holiday:
            holiday_night_turnuses.append(turnus)
          elif turnus.workday:
            pre_holiday_night_turnuses.append(turnus)
      
      for date_pack in date_packs:
        
        random.shuffle(pre_holiday_night_turnuses)
        random.shuffle(holiday_night_turnuses)
        
        for pre_holiday_night_turnus in pre_holiday_night_turnuses:
          for holiday_night_turnus in holiday_night_turnuses:
            
            workers = [self.workers.get_workers_by_type (date_pack[0], scheduling_unit, pre_holiday_night_turnus), 
                       self.workers.get_workers_by_type (date_pack[1], scheduling_unit, pre_holiday_night_turnus), 
                       self.workers.get_workers_by_type (date_pack[2], scheduling_unit, holiday_night_turnus)]
            
            scheduled = True
            
            while (schedule_utils.get_alerady_scheduled_by_type (self.mapper, scheduling_unit, pre_holiday_night_turnus.types, date_pack[0]) < workers[0]) \
            and   (schedule_utils.get_alerady_scheduled_by_type (self.mapper, scheduling_unit, pre_holiday_night_turnus.types, date_pack[1]) < workers[1]) \
            and   (schedule_utils.get_alerady_scheduled_by_type (self.mapper, scheduling_unit, holiday_night_turnus.types,     date_pack[2]) < workers[2]) \
            and   scheduled:
            
              scheduled = False
            
              #does not take into account all days
              heuristic_people = schedule_utils.get_heuristic_sorted_people (packet_people & self.mapper.get_scheduling_unit_people (scheduling_unit) & self.mapper.get_turnus_people (turnus), date_pack[2])
              
              for person in heuristic_people:
                if self.__is_valid_move_preschedule_packet(scheduling_unit, pre_holiday_night_turnus, date_pack[0], person, overtime):
                  person.schedule_turnus(date_pack[0], pre_holiday_night_turnus, scheduling_unit)
                  if not person.is_blocked (date_pack[0] - datetime.timedelta(days=1), pre_holiday_night_turnus):
                    person.add_invalid_turnus(date_pack[0] - datetime.timedelta(days=1),pre_holiday_night_turnus)
                  
                  if self.__is_valid_move_preschedule_packet(scheduling_unit, pre_holiday_night_turnus, date_pack[1], person, overtime):
                    person.schedule_turnus(date_pack[1], pre_holiday_night_turnus, scheduling_unit)
                    
                    if self.__is_valid_move_preschedule_packet(scheduling_unit, holiday_night_turnus, date_pack[2], person, overtime):
                      person.schedule_turnus(date_pack[2], holiday_night_turnus, scheduling_unit)
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
        
      
      
  def __is_valid_move_preschedule(self, scheduling_unit, turnus, date, person, overtime):
    """
    Checks, if the person is allowed to work, on the combination of attributes. This function
    is identical to the is_valid_move function. The only difference is that it does not
    check the holiday workplace rule.
      scheduling_unit: is the scheduling unit checked
      turnus: is the turnus checked
      date: is the date checked
      person: is the person checked
      overtime: if the overtime is allowed for the person
    """
    
    #the special property of the holiday rule is, that it can ignore the if turnuses overlap
    if not schedule_utils.is_valid_move (scheduling_unit, turnus, date, person, overtime):
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
  
  def __is_valid_move_preschedule_packet(self, scheduling_unit, turnus, date, person, overtime, depth=0, check_turnuses=[]):
    """
    Checks, if the person is allowed to work, on the combination of attributes. This function
    is identical to the is_valid_move_preschedule function. The only difference is that 
    it does not check for night turnus packets.
      scheduling_unit: is the scheduling unit checked
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
    
    if not schedule_utils.is_valid_move (scheduling_unit, turnus, date, person, overtime):
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
  
  def __can_continue_scheduling (self, scheduled_types, workers):
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
  
  
  def __get_friday_saturday_sunday_dates(self):
    """Returns a sorted list of 3-tuples (Friday, Saturday, Sunday) for the scheduling date"""
    dates = []
    for date in calendar_utils.get_same_month_dates (self.date):
      if date.weekday ( ) == 4:
        dates.append ((date, date + datetime.timedelta (days=1), date + datetime.timedelta (days=2)))
          
    return dates
    
