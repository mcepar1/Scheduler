# -*- coding: Cp1250 -*-
import random

from utils import calendar_utils

class PreSchedulerModule:
  def __init__(self, mapper, workers, date, logger):
    """
    The default constructor. Only the parameters listed bellow are used, the rest are 
    discarded.
      @param mapper: a mapper object
      @param date: a datetime.date object, that has the correct month and year
    """
    
    self.people = mapper.get_all_people ( )
    self.date = date
    self.already_prescheduled = False
    
  def perform_task(self, overtime=False):
    """Schedules all the predefined constraints. Ignores the parameter."""
    if not self.already_prescheduled:
      self.__pre_schedule_free_weekends ( )
      self.already_prescheduled = True
  
  def __pre_schedule_free_weekends(self):
    """Adds a free weekend, to every person."""
    
    weekends = calendar_utils.get_weekends (self.date)
    random.shuffle (weekends)
    
    people = []
    for person in self.people:
      # it would be an error to add two free weekends to a person
      # TODO: check this
      if not self.__has_vacation (person, weekends):
        people.append (person)
    
    # is responsible for evening out the weekends
    evener = []
    for weekend in weekends:
      evener.append ([weekend, 0])
        
    for person in people:
      for weekend_frequency in evener:
        if self.__add_free_weekend (person, weekend_frequency[0]):
          weekend_frequency[1] += 1
          break
      else:
        raise Exception ('Nisem mogel dodati prostega vikenda')
      
      evener = sorted (evener, lambda e1, e2: cmp(e1[1], e2[1]))
        
      
  def __has_vacation(self, person, weekends):
    """
    Checks if that person has a full vacation weekend.
      person: is the person, that is checked
      weekends: a list of weekends
      return: true, if the person has a vacation
    """
    
    for weekend in weekends:
      if person.is_vacation (weekend[0]) and person.is_vacation (weekend[1]):
        return True
      
    return False
  
  def __add_free_weekend(self, person, weekend):
    """
    Adds a free weekend to a person.
      person: is the person, that will have the free weekend
      weekends: a list of weekends
    """
    
    if person.is_free_day(weekend[0]) and person.is_free_day(weekend[1]):
      if not person.is_scheduled(weekend[0]):
        person.add_free_day(weekend[0])
          
      if not person.is_scheduled(weekend[1]):
        person.add_free_day(weekend[1])
          
      return True
        
    return False
      
      
      
      
      
      
