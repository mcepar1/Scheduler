# -*- coding: Cp1250 -*-

"""
This files contains logic for coordinating the scheduling process.
"""
from utils import time_conversion
from scheduler import schedule_utils, modules

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

  def __init__(self, people, scheduling_units, date, workers, log=log.DummyLog()):
    """
    The default constructor.
      @param people: a list of data objects
      @param scheduling_units: a list of data objects
      @param date: a datetime.date object, that represents the scheduling date (day is not important)
      @param workers: an object, that contains information, about how many people must work at any given
        date, scheduling unit and turnus
      @param log: the logger (optional)
    """
    
    self.log = log
    
    self.log.send_message('Ustvarjam razvrscevalnik ...')
    
    if not people:
      raise Exception('Ni nobene osebe za razvrscanje')    
    
    self.people           = people
    self.scheduling_units = scheduling_units
    self.date             = date
    self.workers          = workers
    
    #set various maps, for the ease of access
    self.mapper           = schedule_utils.Mapper (self.people, self.scheduling_units)
    
        
    
    self.active_modules   = []
    self.clean_up_modules = []

    for module in PersonScheduler.MODULES:
      self.active_modules.append (module (self.mapper, self.workers, self.date, self.log))
    for module in PersonScheduler.CLEAN_UP:
      self.clean_up_modules.append (module (self.mapper, self.workers, self.date, self.log))   
    
          

  def schedule(self):
    
    self.log.send_message('Prva faza razvrščanja ...')
    #invoke the plugins
    for plugin in self.active_modules:
      plugin.perform_task (overtime=False) 
    
          
    self.log.send_message('Druga faza razvrščanja ...')
    #repeat the process for the part-time employees
    
    #invoke the plugins
    for plugin in self.active_modules:
      plugin.perform_task (overtime=False)
    
    
    self.log.send_message('Tretja faza razvrščanja ...')
    #finally add all the people, including the ones with the overtime
    
    
    #invoke the plugins
    for plugin in self.active_modules:
      plugin.perform_task (overtime=True)
    
          

    self.log.send_message('Zadnja faza razvrščanja ...')
    for plugin in self.clean_up_modules:
      plugin.perform_task (overtime=True)      
  
  
  def get_schedule_matrix (self):
    """
    Returns a matrix, that is close to what the final output might be.
    """
    dates = self.workers.get_dates ( )
    scheduled = {}
    
    for person in self.people:
      scheduled[person] = []
      for date in dates:
        temp = person.get_scheduled(date)
        scheduled[person].append(temp[0] + '\n' + temp[1] + '\n' + temp[2])
        
    headers = ['Oseba']
    for date in dates:
      headers.append(time_conversion.date_to_string(date))
    headers.append('Nadure')
    lines = [headers]
    for person in self.people:
      lines.append([])
      lines[-1].append(str(person))
      lines[-1] += scheduled[person]
      lines[-1].append(str(person.get_monthly_hours_difference(self.date)))
      
    return lines
  
  def get_workplace_matrix(self):
    """
    @deperecated: there are no more workplaces
    Returns a dictionary, that maps workplaces to roles and roles to a schedule matrix, 
    that contains only persons and turnuses, that were scheduled into this role - 
    workplace pair.
    """
    map = {}
    
    headers = ['Oseba']
    for date in self.workers.get_dates ( ):
      headers.append(time_conversion.date_to_string(date))
    
    for scheduling_unit in self.mapper.get_scheduling_units ( ):
      map[scheduling_unit] = [headers] 
      people = []
      for person in self.mapper.get_scheduling_unit_people (scheduling_unit):
        people.append(person)
      
      for person in people:
        person_schedule = [str(person)]
        for date in self.workers.get_dates ( ):
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
    
    for scheduling_unit in sorted (self.scheduling_units):
      for date in self.workers.get_dates ( ):
        turnus_types = scheduling_unit.get_turnus_types ( )
        for turnus_type in sorted(turnus_types):
          needed = self.workers.get_workers (date, scheduling_unit, turnus_type)
          scheduled = schedule_utils.get_alerady_scheduled_by_type (self.mapper, scheduling_unit, [turnus_type], date)
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
