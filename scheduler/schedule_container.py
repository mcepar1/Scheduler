# -*- coding: Cp1250 -*-

"""
This file contains a container class, that is similar to the data containers.
"""
import person 

from data import general
from utils import time_conversion, calendar_utils



"""
The container class.
"""
class ScheduleContainer (general.DataContainer):
  
  def __init__ (self, date, elements_list=None):
    """
    The default constructor.
      @param date: a datetime.date object, that defines the schedule's year and month
      @param elements_list: a sequence of elements.
    """
    general.DataContainer.__init__ (self, '', person.Nurse, elements_list)
    
    self.date      = date
    self.compact   = True
    self.full_span = False
    
  def save (self):
    """
    @deprecated: not needed. 
    """
    pass
  
  def load (self):
    """
    @deprecated: not needed.
    """
    pass
  
  def set_compact (self, compact):
    """
    Sets the type of the view, that will be displayed.
      @param compact: a boolean that defines the view. Compact view if True, full view if False.
    """
    self.compact = compact
    
  def is_compact (self):
    """
    Checks, if this container is set to the compact view mode.
      @return: True, if it compact, False otherwise.
    """
    return self.compact
  
  def set_span (self, full):
    """
    Sets the date range of the view. Span can be set to full (the neighbouring months) or normal (only the
    main scheduling month).
      @param full: a boolean that sets the span. True if full span, False otherwise. 
    """
    self.full_span = full
    
  def is_full_span (self):
    """
    Checks, if this container is set to the full span view mode.
      @return: True, if it is full, False otherwise.
    """
    return self.full_span
    
  
  def as_table(self, filter=False):
    """
    Returns a table-like representation of self.
      @param filter: determines, if the output should be filtered. The default value is set to false.
      @return: a dictionary with two string keys:
        header: a list that contains headers of the table;
        titles: a list of row names
        items:  a list of lists. The external list represents rows and the internal one represents columns within a single row.
    """
        
    dates     = self.__get_dates ( )
    rows_list = []
    overtimes = self.__get_overtime ( )
    
    headers = [str (date.day) for date in dates] if self.compact else [time_conversion.date_to_string (date) for date in dates]
    headers.append ('NADURE')
    headers.append ('NEPLAČANE URE')
    
    for element in self.get_filtered( ):
      row = element.get_schedule_compact (dates) if self.compact else element.get_schedule (dates)
      row.append (overtimes[element])
      row.append (str (element.get_unpaid_hours ( )))
      
      rows_list.append (row)
    
    
    table = {}
    table['header'] = headers
    table['titles'] = [str (element) for element in self.get_filtered ( )]
    table['items']  = rows_list
   
    return table
  
  def get_colors (self):
    """
    Returns a list of lists of colors.
      @return: a double list. The inner list represent columns, the outer rows. Each item in the inner
               list is a RGB tuple.
    """
    dates = self.__get_dates ( )
    rows  = []
    
    for element in self.get_filtered ( ):
      rows.append (element.get_colors (dates))
      
    return rows
  
  def get_people (self, indexes):
    """
    Returns a list of people at the specified indexes.
      @param indexes: a list of integers
      @return: a list schedule persons
    """
    people = []
    for i, person in enumerate (self.get_filtered ( )):
      if i in indexes:
        people.append (person)
    return people
  
  def get_dates (self, indexes):
    """
    Returns a list of date at the specified indexes.
      @param indexes: a list of integers
      @return: a list of dates
    """
    dates = []
    for i, date in enumerate (self.__get_dates ( )):
      if i in indexes:
        dates.append (date)
    return dates
  
  def get_exportable (self):
    """
    Returns a dictionary, that maps scheduling units to a schedule matrix, 
    that contains only persons and turnuses, that were scheduled into scheduling unit.
    """
    map = {}
    
    headers = ['Oseba']
    for date in calendar_utils.get_same_month_dates (self.date):
      headers.append(time_conversion.date_to_string(date))
    
    scheduling_units = set ( )
    for person in self.get_all ( ):
      for scheduling_unit in person.get_scheduling_units ( ):
        scheduling_units.add (scheduling_unit)
    
    for scheduling_unit in sorted (scheduling_units):
      map[scheduling_unit] = [headers] 
      people = []
      for person in self.get_all ( ):
        if person.has_scheduling_unit (scheduling_unit):
          people.append(person)
      
      for person in people:
        person_schedule = [person.get_academic_name ( )]
        for date in calendar_utils.get_same_month_dates (self.date):
            turnus = person.get_turnus(date, scheduling_unit)
            if turnus:
              person_schedule.append(turnus.code[0])
            else:
              person_schedule.append('')
        map[scheduling_unit].append(person_schedule)
    
    return map
  
  def __get_overtime (self):
    """
    Returns the overtime value for each person.
      @return: a map that maps elements to overtime.
    """
    overtime = {}
    for nurse in self.get_filtered ( ):
      overtime[nurse] = str (-1 * nurse.get_monthly_hours_difference (self.date))
    return overtime
  
  def __get_dates (self):
    """
    Returns a sorted list of all dates, contained by all nurses.
      @return: an ordered list of datetime.date objects
    """
    if self.full_span:
      dates = set ( )
      for nurse in self.elements:
        for date in nurse.get_dates ( ):
          dates.add (date)
      return sorted (dates)
    else:
      return calendar_utils.get_same_month_dates (self.date)
      
    
    