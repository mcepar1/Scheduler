# -*- coding: Cp1250 -*-

"""
This files contains logic for coordinating the scheduling process.
"""
from utils import time_conversion
from scheduler import schedule_utils, modules, schedule_container

import log

"""
This class binds all the scheduling modules and coordinates their execution.
"""
class PersonScheduler:
  
  """
  Contains the modules, that are used after the scheduling phase.
  """
  CLEAN_UP = [modules.FillHours]#modules.WeekMorning, 
  
  """
  Contains the modules, that will be used in this scheduler.
  The order is important!
  """    
  MODULES = [modules.PreSchedulerModule, modules.HolidayRuleModule, modules.CoreModule]

  def __init__(self, people, scheduling_units, date, workers, log = log.DummyLog ( )):
    """
    The default constructor.
      @param people: a list of data objects
      @param scheduling_units: a list of data objects
      @param date: a datetime.date object, that represents the scheduling date (day is not important)
      @param workers: an object, that contains information, about how many people must work at any given
        date, scheduling unit and turnus
      @param log: a logger object (optional).
    """
    
    self.__log = log
    
    self.__log.send_message('Ustvarjam razvrscevalnik ...')
    
    if not people:
      raise Exception('Ni nobene osebe za razvrscanje')    
    
    self.__date             = date
    self.__workers          = workers
    
    #set various maps, for the ease of access
    self.__mapper           = schedule_utils.Mapper (people, scheduling_units)


  def schedule(self):
    """
    Schedules.
    """
    
    # initialize modules
    active_modules   = []
    clean_up_modules = []
    for module in PersonScheduler.MODULES:
      active_modules.append   (module (self.__mapper, self.__workers, self.__date, self.__log))
    for module in PersonScheduler.CLEAN_UP:
      clean_up_modules.append (module (self.__mapper, self.__workers, self.__date, self.__log))
      
      
    
    self.__log.send_message('Prva faza razvrščanja ...')
    #invoke the plugins
    for module in active_modules:
      module.perform_task (overtime=False) 
    
          
    self.__log.send_message('Druga faza razvrščanja ...')
    #repeat the process for the part-time employees
    
    #invoke the plugins
    for module in active_modules:
      module.perform_task (overtime=False)
    
    
    self.__log.send_message('Tretja faza razvrščanja ...')
    #finally add all the people, including the ones with the overtime
    
    
    #invoke the plugins
    for module in active_modules:
      module.perform_task (overtime=True)
    
          

    self.__log.send_message('Zadnja faza razvrščanja ...')
    for module in clean_up_modules:
      module.perform_task (overtime=True)
      
  def get_date (self):
    """
    Returns this scheduler's date.
      @return: a datetime.date object
    """    
    return self.__date
  
  def set_log (self, log):
    """
    Sets this scheduler's logger.
    """
    self.__log = log
  
  
  def get_result (self):
    """
    Returns the schedule's result.
      @return: a schedule container object
    """
    return schedule_container.ScheduleContainer (self.get_date ( ), self.__mapper.get_all_people ( ))
  
  
  def get_workplace_matrix(self):
    """
    @deperecated: there are no more workplaces
    Returns a dictionary, that maps workplaces to roles and roles to a schedule matrix, 
    that contains only persons and turnuses, that were scheduled into this role - 
    workplace pair.
    """
    map = {}
    
    headers = ['Oseba']
    for date in self.__workers.get_dates ( ):
      headers.append(time_conversion.date_to_string(date))
    
    for scheduling_unit in self.__mapper.get_scheduling_units ( ):
      map[scheduling_unit] = [headers] 
      people = []
      for person in self.__mapper.get_scheduling_unit_people (scheduling_unit):
        people.append(person)
      
      for person in people:
        person_schedule = [person.get_academic_name ( )]
        for date in self.__workers.get_dates ( ):
            turnus = person.get_turnus(date, scheduling_unit)
            if turnus:
              person_schedule.append(turnus.code[0])
            else:
              person_schedule.append('')
        map[scheduling_unit].append(person_schedule)
    
    return map
          
  def get_workplace_warnings(self):
    """
    @deprecated: no more workplaces
    Returns workplace warnings.
      returns: a nested dictionary that maps workplaces to roles, roles to turnuses, 
               turnuses to dates and dates to warning messages
    """
    temp = {}
    
    for scheduling_unit in sorted (self.__mapper.get_scheduling_units ( )):
      for date in self.__workers.get_dates ( ):
        turnus_types = scheduling_unit.get_turnus_types ( )
        for turnus_type in sorted(turnus_types):
          needed = self.__workers.get_workers (date, scheduling_unit, turnus_type)
          scheduled = schedule_utils.get_alerady_scheduled_by_type (self.__mapper, scheduling_unit, [turnus_type], date)
          if scheduled < needed or scheduled > needed:
            if scheduling_unit not in temp:
              temp[scheduling_unit] = {}
            if turnus_type not in temp[scheduling_unit]:
              temp[scheduling_unit][turnus_type] = {}
            
            if scheduled < needed:
              temp[scheduling_unit][turnus_type][date] = 'Premalo:' + str(needed - scheduled)
            elif scheduled > needed:
              temp[scheduling_unit][turnus_type][date] = 'Preveč:' + str(scheduled - needed)
    
    return temp
  
