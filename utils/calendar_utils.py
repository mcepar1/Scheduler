# -*- coding: Cp1250 -*-

"""
This class contains various functions, that simplify the calculating dates. 
"""
import calendar
import datetime

import holiday

# create a calendar with Monday as the first day of the week
__cal = calendar.Calendar (0)
__months = ['Januar', 'Februar', 'Marec', 'April', 'Maj', 'Junij', 'Julij', 'Avgust', 'September', 'Oktober', 'November', 'December']

def get_month_names ( ):
  """
  Returns a date-ordered list of all the month names.
    @return: an ordered list of strings
  """
  return __months

def get_month_name (month):
  """
  Returns the name of the month.
    @param month: a 1 based index of the month
    @return: the month's name
  """
  return __months[month - 1]

def get_month_index (month):
  """
  Returns a 1 based index of the month.
    @param month: the month's name (index)
    @return: an integer
  """
  month = month[0].upper ( ) + month[1:].lower ( )
  return __months.index (month)

def get_py_month_name (date):
  """
  Returns the name of the month.
    @param date: a datetime.date object
    @return: the month's name 
  """
  return get_month_name (date.month)

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

def get_pre_workfree_dates (date):
  """
  Returns a sorted list of work days, that are followed by a workfree date. The pre_workfree dates are all
   in the same month as the specified date.
   @param date: is a datetime.date object, that contains the desired month and year
   @return: a sorted list of datetime.date objects
  """
  this_month_workdays = set (get_workdays (date))
  pre_work_free_dates = []
  for workdate in this_month_workdays:
    if holiday.is_workfree (workdate + datetime.timedelta (days = 1)):
      pre_work_free_dates.append (workdate)
      
  return sorted (pre_work_free_dates)

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

def get_weekends (date):
  """
  Returns a list of two-tuples, that contain datetime.date objects (Saturday and Sunday). Returns only 
  the weekends that have the Saturday in the current month.
  @param date: a datetiem.date object
  @return: a list of ordered 2-tuples that contain datetime.date objects.  
  """
  weekends = []
  
  for date in get_same_month_dates (date):
    if date.weekday() == 5:
      weekends.append ((date, date + datetime.timedelta (days=1)))
        
  return weekends
  
  
  
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
