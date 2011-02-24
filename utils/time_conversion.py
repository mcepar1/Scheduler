# -*- coding: Cp1250 -*-

"""This script contaions methods that ease the conversion beetween the time and string objects"""

import datetime

TIME_FORMAT     = "%H:%M"
DATE_FORMAT     = "%d.%m.%Y"
DATETIME_FORMAT = "%H:%M %d.%m.%Y"

def time_to_string(time):
  """Convert a time object into a string HH:MM representation"""
  return str (time.strftime(TIME_FORMAT))
  
def string_to_time(string):
  """Converts a string formatted like HH:MM into a time object"""
  try:
    date = datetime.datetime.strptime(string, TIME_FORMAT)
    return datetime.time(hour=date.hour, minute=date.minute)
  except Exception as e:
    print e
    raise Exception(u"Cas mora biti oblike " + TIME_FORMAT + ". Ura je lahko 0-23, minute pa 0-59")

def date_to_string (date):
  """Convert a date object into human readable date"""
  return str (date.strftime (DATE_FORMAT))

def string_to_date (string):
  """Converts string into date object"""
  try:
    date = datetime.datetime.strptime(string, DATE_FORMAT)
    return datetime.date(day=date.day, month=date.month, year=date.year)
  except:
    raise Exception('Datum mora biti oblike ' + DATE_FORMAT + '.')

def timedelta_to_hours (timedelta):
  """Returns an hour representation of the timedelta object"""
  
  return ((timedelta.microseconds + (timedelta.seconds + timedelta.days * 24 * 3600) * 10 ** 6) / 10 ** 6) / 3600.0

def time_to_timedelta(time):
  """Converts a time object into a timedelta"""
  return datetime.timedelta(hours=time.hour, minutes=time.minute, seconds=time.second, microseconds=time.microsecond)

def datetime_to_string (datetime):
  """Converts a datetime object into a string."""
  return str (datetime.strftime (DATETIME_FORMAT))
