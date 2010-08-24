# -*- coding: utf-8 -*-
from scheduler import person

import datetime
import cPickle as pickle
import os


class NurseScheduler:
  FILES_DIR = os.path.join("scheduler","persistence", "nurses")

  def __init__(self, nurses, date, morning_shift, afternoon_shift, night_shift, double_shift):
    """
    The default constructor.
      nurses: a list of all the nurses, that will be scheduled
      date: is the starting date of the scheduling
      moring_shift: is the number of nurses, that will be working the morning shift
      afternoon_shift: is the number of nurses, that will be working the afternoon shift
      night_shift: is the number of nurses, that will be working the night shift
      double shift: is the number of nurses, that will be working the double shift
    """
  
    self.nurses = []
    for nurse in nurses:
      self.nurses.append(person.Nurse(nurse))
      self.nurses[-1].add_month (date)
    self.__get_previous_month(date)
    
    
    self.date = date
    self.morning_shift = morning_shift
    self.afternoon_shift = afternoon_shift
    self.night_shift = night_shift
    self.double_shift = double_shift
    
    
    
  def __get_previous_month(self, date):
    """
    This reloads the previously scheduled month into the application.
      date: is the current schedule date
    """
    
    prev_date = datetime.date(day = 1, month = date.month, year = date.year) - datetime.timedelta (days = 1) 
    filename = str(prev_date.month) + '_' + str(prev_date.year) + '.dat'
    
    old_nurses = pickle.load(file(os.path.join(NurseScheduler.FILES_DIR, filename),'rb'))
    
    for nurse in self.nurses:
      for old_nurse in old_nurses:
        if nurse == old_nurse:
          #we can always do that, because the past is always right
          nurse.scheduled.update(old_nurse.scheduled)
    
    
  def __save(self):
    """Saves the schedule"""
    
    filename = str(self.date.month) + '_' + str(self.date.year) + '.dat'
    pickle.dump(self.nurses, file(os.path.join(NurseScheduler.FILES_DIR, filename),'wb'))
       