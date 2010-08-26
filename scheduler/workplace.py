# -*- coding: utf-8 -*-

from data import workplace as data_model

class Workplace(data_model.Workplace):
  
  def __init__(self, data_workplace):
    data_model.Workplace.__init__(self, data_workplace.label)
    
    self.allowed_turnuses = data_workplace.allowed_turnuses
    
    self.workers = {}
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
    
  def set_worker(self, turnus, workers):
    """
    Sets the number of persons, that will work in the specified turnus.
      turnus: is the turnus
      workers: is the number of workers
    """
    
    if turnus in self.allowed_turnuses and turnus in self.workers:
      self.workers[turnus] = workers
    else:
      raise Exception('To delovisce nima izbranega turnusa')
    
  def get_workers(self):
    """Returns self.workes."""
    
    return self.workers

