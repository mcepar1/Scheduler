# -*- coding: utf-8 -*-

import datetime
import dateutil.easter

# fill these dates out for the present year
# some could change with another year
# {month: list of holiday dates in month}
# TODO: export into an external, easy to edit file
HOLIDAYS = {
              1: [1, 2], # novo leto
              2: [8], # Slovenski kulturni praznik
              3: [],
              4: [27], # dan boja proti okupatorju
              5: [1, 2, 31], # praznik dela, Binkošti
              6: [25], # dan državnosti
              7: [],
              8: [15], # Marijino vnebovzetje
              9: [],
              10: [5,31], # dan reformacije
              11: [1], # dan spomina na mrtve
              12: [25, 26] # božič, dan samostojnosti
            }

def __get_holidays(self, year=datetime.date.today().year):
    """
    Returns a dict in the same format as HOLIDAYS, only with the correct easter and easter mondays dates.
    """
    # create a hard copy
    holidays = {}
    for month in HOLIDAYS:
      holidays[month] = []
      for day in HOLIDAYS[month]:
        holidays[month].append(day)
    
    easter = dateutil.easter.easter(year)
    easter_monday = easter + datetime.timedelta(days=1)
    
    holidays[easter.month].append(easter.day)
    holidays[easter_monday.month].append(easter_monday.day)
    
    return holidays
  
def is_holiday(date):
  """
  Checks if the date is a holiday.
    date: an instance of the datetime.date class
    return: true, if the date is a holiday, false otherwise
  """
  
  return date.day in __get_holidays(date.year)[date.month]

def is_workfree(date):
  """
  Checks if the date is a work free day.
    date: an instance of the datetime.date class
    return: true, if the date is a work free day, false otherwise
  """
  
  return date.weekday() == 6 or is_holiday(date)

