# -*- coding: utf-8 -*-
from global_vars import turnuses
from data import workplace as data_model

class Workplace(data_model.Workplace):
  
  def __init__(self, data_workplace):
    data_model.Workplace.__init__(self, data_workplace.label, data_workplace.holiday_rule)
    
    self.allowed_turnuses = data_workplace.allowed_turnuses
    
    self.workers = {}
    self.date_workers = {}
    
    allowed_types = set()
    for turnus in self.allowed_turnuses:
      for type in turnus.types:
        allowed_types.add(type)
        
    for type in allowed_types:
      self.workers[type] = 0
      
  def add_allowed_turnus (self, turnus):
    """
    Adds a turnus to the allowed turnuses.
      turnus: is the new allowed turnus
    """
    self.allowed_turnuses.add (turnus)
    
    if type not in self.workers:
      self.workers[type] = 0
    
  def remove_allowed_turnus (self, turnus):
    """
    Removes a turnus from the allowed turnuses.
      turnus: the turnus, that will be allowed
    """
    self.allowed_turnuses.remove (turnus)
    
    #find out if this was the last turnus of its type
    #if it was delete it
    types = turnus.types
    for type in types:
      if not turnuses.get_by_type(type, self):
        del self.workers[type]
      
    
  def set_worker(self, role, turnus_type, workers, date=None):
    """
    Sets the number of persons, that will work in the specified turnus_type.
      role: is the role for which the workers will be set
      turnus_type: is the turnus
      workers: is the number of workers
      date: if given, it set's the only for the specified date. The dated number of
            workers always takes priority.
    """
    
    #discover, if there is a turnus of the specified type
    for turnus in self.allowed_turnuses:
      if turnus_type in turnus.types:
        if date:
          if date not in self.date_workers:
            self.date_workers[date] = {}
          if role not in self.date_workers[date]:
            self.date_workers[date][role] = {}
          self.date_workers[date][role][turnus_type] = workers
        else:
          self.workers[turnus_type] = workers
          
        break
    # because date specific adding does not have any filtering, it may try to
    # and workers for an invalid turnus, but the number of workers will be 0
    else:
      if workers != 0:
        raise Exception('To delovisce nima izbranega turnusa')
    
        
    
  def get_workers(self, date):
    """Returns workers for the specified date."""
    
    if date not in self.date_workers:
      return self.workers
    else:
      workers = {}
      workers.update(self.workers)
      workers.update(self.date_workers[date])
      return workers

