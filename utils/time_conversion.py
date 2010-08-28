# -*- coding: utf-8 -*-
"""This script contaions methods that ease the conversion beetween the time and string objects"""

import datetime

TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%d.%m.%Y"

def time_to_string(time):
  """Convert a time object into a string HH:MM representation"""
  return time.strftime(TIME_FORMAT)
  
def string_to_time(string):
  """Converts a string formatted like HH:MM into a time object"""
  try:
    date = datetime.datetime.strptime(string, TIME_FORMAT)
    return datetime.time(hour = date.hour, minute = date.minute)
  except Exception:
    raise Exception(u"Čas mora biti oblike " + TIME_FORMAT + ". Ura je lahko 0-23, minute pa 0-59")

def date_to_string (date):
  """Convert a date object into human readable date"""
  return date.strftime (DATE_FORMAT)

def string_to_date (string):
  """Converts string into date object"""
  try:
    date = datetime.datetime.strptime(string, DATE_FORMAT)
    return datetime.date(day = date.day, month = date.month, year = date.year)
  except:
    raise Exception('Datum mora biti oblike ' + DATE_FORMAT + '.')

def timedelta_to_hours (timedelta):
  """Returns an hour representation of the timedelta object"""
  
  return ((timedelta.microseconds + (timedelta.seconds + timedelta.days * 24 * 3600) * 10**6) / 10**6) / 3600.0