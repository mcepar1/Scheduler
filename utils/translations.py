"""
This class has some useful function for translating variable values.
"""
from Scheduler.utils import time_conversion

def translate_time (time):
  """
  Translates a time variable into sloveninan language
    time: instance of the datetime.time class
    return: an unicode object
  """
  return time_conversion.time_to_string(time)

def translate_date (date):
  """
  Translates a date variable into the slovenian language.
    date: instance of the datetime.date class
    return: an unicode object
  """
  return time_conversion.date_to_string(date)

def translate_datetime (datetime):
  """
  Translates a date variable into the slovenian language.
    datetime: instance of the datetime.datetime class
    return: an unicode object
  """
  return time_conversion.date_to_string(datetime)

def translate_timedelata (timedelta):
  """
  Translates a timedelta variable into the slovenian language.
    timedelta: instance of the datetime.timedelta class
    return: an unicode object
  """
  # exclude seconds
  return unicode (timedelta)[0:-3]

def translate_string(string):
  """
  Translates string variable into slovenian language.
    return: an unicode object
  """
  return unicode (string)

def translate_boolean(boolean):
  """
  Translates a boolean variable into the slovenian language.
    return: an unicode object
  """
  if isinstance(boolean, bool):
    return u'Da' if boolean else  u'Ne'
  else:
    raise Exception('Trying to translate a non-boolean varible')
    