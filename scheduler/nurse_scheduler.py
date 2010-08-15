# -*- coding: utf-8 -*-

import datetime

class NurseScheduler:
  def __init__(self, nurses, date, morning_shift, afternoon_shift, night_shift):
    self.nurses = nurses
    self.date = date
    self.morning_shift = morning_shift
    self.afternoon_shift = afternoon_shift
    self.night_shift = night_shift
    
  def __get_previous_month(self, date):
    prev_date = date - datetime.timedelta(months = 1)
    #load the month somehow
