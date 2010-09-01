# -*- coding: utf-8 -*-

from data import workplace as data_model

class Workplace(data_model.Workplace):
  
  def __init__(self, data_workplace):
    data_model.Workplace.__init__(self, data_workplace.label, data_workplace.holiday_rule)
    
    self.allowed_turnuses = data_workplace.allowed_turnuses
    
    self.workers = {}
    self.date_workers = {}
    for turnus in self.allowed_turnuses:
      self.workers[turnus] = 0
      
  def add_allowed_turnus (self, turnus):
    """
    Adds a turnus to the allowed turnuses.
      turnus: is the new allowed turnus
    """
    self.allowed_turnuses.add (turnus)
    self.workers[turnus] = 0
    
  def remove_allowed_turnus (self, turnus):
    """
    Removes a turnus from the allowed turnuses.
      turnus: the turnus, that will be allowed
    """
    self.allowed_turnuses.remove (turnus)
    del self.workers[turnus]
    
  def set_worker(self, turnus, workers, date=None):
    """
    Sets the number of persons, that will work in the specified turnus.
      turnus: is the turnus
      workers: is the number of workers
      date: if given, it set's the only for the specified date. The dated number of
            workers always takes priority.
    """
    
    if turnus in self.allowed_turnuses:
      if date:
        if date not in self.date_workers:
          self.date_workers[date] = {}
        self.date_workers[date][turnus] = workers
      else:      
        self.workers[turnus] = workers
    # because date specific adding does not have any filtering, it may try to
    # and workers for an invalid turnus, but the number of workers will be 0
    elif workers != 0:
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

