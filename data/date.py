# -*- coding: utf-8 -*-
import datetime

class HolidayDate (datetime.date):

  def __init__(*args, is_holiday = True, **kwargs):
    datetime.date.__init__(self, *args, **kwargs)
    self.is_holiday = is_holiday
