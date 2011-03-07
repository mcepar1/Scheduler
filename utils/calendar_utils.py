# -*- coding: Cp1250 -*-

"""
This class contains various functions, that simplify the calculating dates. 
"""
import calendar
import datetime

import holiday

# create a calendar with Monday as the first day of the week
__cal = calendar.Calendar (0)

def get_same_month_dates(date):
  """
  Returns a sorted list of dates that are in the same month as the specified date. Does not overflow weeks.
    date: a datetime.date object
    return: a sorted list of dates
  """
  
  dates = []
  for d in __cal.itermonthdates(date.year, date.month):
    dates.append (d)
      
  
  while dates[0].month  != date.month:
    del dates[0]
  while dates[-1].month != date.month:
    del dates[-1]
  
  return dates

def get_workfree_dates (date):
  """
  Returns a sorted list of work free dates, that are in the same month as the specified date. It does not
  overflow weeks.
    date: a datetime.date object
    return: a sorted list of dates
  """
  all_dates      = get_same_month_dates (date)
  workfree_dates = []
  
  for date in all_dates:
    if  holiday.is_workfree (date):
      workfree_dates.append (date)
      
  return workfree_dates

def get_workdays (date):
  """
  Returns a sorted list of work dates, that are in the same month as the specified date. It does not
  overflow weeks.
    date: a datetime.date object
    return a sorted list of dates
  """
  return sorted (set (get_same_month_dates (date)) - set (get_workfree_dates (date)))

def get_previous_month (date):
  """
  Returns a date that belongs to the previous month. Correctly handles December and January.
    date: a datetime.date object
    return: a datetime.date object
  """
  new_date = datetime.date (date.year, date.month, 1) - datetime.timedelta (days = 1)
  new_date = datetime.date (new_date.year, new_date.month, 1)
  return new_date

def get_next_month (date):
  """
  Return a date that belongs to the next month. Correctly handles December an January.
    date: a datetime.date object
    return a datetime.date object
  """
  new_date = datetime.date (date.year, date.month, 25) + datetime.timedelta (days = 14)
  new_date = datetime.date (new_date.year, new_date.month, 1)
  return new_date
  
  
  
def get_week(date):
  """
  Returns the week in which the date is located.
    date: instance of the datetime.date class
    return: a list of dates
  """
  
  for week in calendar.Calendar().monthdatescalendar(year=date.year, month=date.month):
    if date in week:
      return week
  else:
    raise Exception('Date week error')
  
def get_next_week(date):
  """
  Returns all dates in the week after the week in which the date is located.
    date: instance of the datetime.date class
    return: a list of dates
  """
    
  return get_week(date + datetime.timedelta(days=7))

def get_previous_week(date):
  """
  Returns all dates in the week after the week in which the date is located.
    date: instance of the datetime.date class
    return: a list of dates
  """
    
  return get_week(date + datetime.timedelta(days= -7))  
