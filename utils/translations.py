# -*- coding: Cp1250 -*-

"""
This class has some useful function for translating variable values.
"""
from utils import time_conversion

__class_names      = ['EmploymentType',   'Nurse',             'Role', 'SchedulingUnit',         'Title', 'TurnusType',    'Turnus', 'Vacation', 'Workplace']
__translated_names = ['Vrsta zaposlitve', 'Medicinska sestra', 'Vloga', 'Par vloga - delovi��e', 'Naziv', 'Vrsta turnusa', 'Turnus', 'Dopust',   'Delovi��e']

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
  string = str (timedelta)[0:-3]
  # add leading zero, if necessary
  if len (string)==4:
    string = '0' + string 
  return string

def translate_string(string):
  """
  Translates string variable into slovenian language.
    return: an unicode object
  """
  if string in __class_names:
    return __translated_names[__class_names.index(string)]
  else:
    return str (string)

def translate_boolean(boolean):
  """
  Translates a boolean variable into the slovenian language.
    return: an unicode object
  """
  if isinstance(boolean, bool):
    return u'Da' if boolean else  u'Ne'
  else:
    raise Exception('Trying to translate a non-boolean variable')
    