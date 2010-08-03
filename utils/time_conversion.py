# -*- coding: utf-8 -*-
"""This script contaions methods that ease the conversion beetween the time and string objects"""

import datetime

TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%d. %m. %Y"

def time_to_string(time):
  """Convert a time object into a string HH:MM representation"""
  return time.strftime(TIME_FORMAT)
  
def string_to_time(string):
  """Converts a string formatted like HH:MM into a time object"""
  try:
    date = datetime.datetime.strptime(string, TIME_FORMAT)
    return = datetime.time(hour = date.hour, minute = date.minute)
  except Exception as e:
    raise Exception(u"Čas mora biti oblike " + TIME_FORMAT + ". Ura je lahko 0-23, minute pa 0-59")

    
