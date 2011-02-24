# -*- coding: Cp1250 -*-

from Scheduler.utils import holiday

import datetime
import calendar

import wx
import wx.grid
import wx.calendar
import wx.lib.intctrl
import wx.lib.newevent



"""
This class behaves the same way as a normal wxCheckBox.
The only difference is that is also has an attribute
element.
Element is an instance, that is beeing manipulated by
this CheckBox.
"""
class LinkedCheckBox(wx.CheckBox):
  def __init__(self, element, *args, **kwargs):
    wx.CheckBox.__init__(self, *args, **kwargs)
    
    self.element = element

"""
This class is a wx.Choice, with predefined choices.
The hard-coded choices are months of the year.
"""    
class MonthChoice(wx.Choice):
  MONTHS = [
              'Januar',
              'Februar',
              'Marec',
              'April',
              'Maj',
              'Junij',
              'Julij',
              'Avgust',
              'September',
              'Oktober',
              'November',
              'December'
           ]

  def __init__(self, *args, **kwargs):
    kwargs['choices'] = MonthChoice.MONTHS
    wx.Choice.__init__(self, *args, **kwargs)
    
    next_month = datetime.date(day=28, month=datetime.date.today().month, year=datetime.date.today().year) + datetime.timedelta(days=10)
    self.SetSelection(next_month.month - 1)
    
  def get_value(self):
    """
    Returns an instance of the datetime.date, with current year, the selected
    month and the first day in the month.
      return: a datetime.date instance
    """
    #return MonthChoice.MONTHS[self.GetCurrentSelection()]
    return datetime.date(day=1, month=self.GetCurrentSelection() + 1, year=int(datetime.date.today().year))

"""
This class behaves the same way as as a normal wxChoice.
The only difference is that it handles elements 
internally.
"""  
class LinkedChoice(wx.Choice):
  def __init__(self, elements, *args, **kwargs):
    """
    Same constructor as the wxChoice. The only difference is that it has on additional
    parameter. It also overrides any existing choices.
      elements: a list of elements that will be displayed in the choice menu.
    """
    self.elements = sorted(elements)
    
    kwargs['choices'] = [str(element) for element in self.elements]
    wx.Choice.__init__(self, *args, **kwargs)
    
  def set_elements(self, elements):
    """Replaces the old choices with the ones specified in the list"""
    if elements:
      self.elements = sorted(elements)
      self.Clear ()
      self.AppendItems ([str(element) for element in self.elements])
      self.Select(0)
    else:
      self.elements = None
      self.Clear()
    
    
    
  def get_value(self):
    """Returns the selected instance of the workspace class"""
    if self.elements:
      return self.elements[self.GetCurrentSelection()]
    else:
      raise Exception ('Ni elmentov!')
    
"""
This class behaves the same way as as a normal wxIntCtrl.
The only difference is that it handles employment
types internally.
"""
class LinkedIntCtrl(wx.lib.intctrl.IntCtrl):
  
  def __init__(self, employment_type, *args, **kwargs):
    """
    The default constructor.
      employment_type: is an instance of the EmploymentType, that this control will manage.
    """
    wx.lib.intctrl.IntCtrl.__init__(self, *args, **kwargs)
    
    self.employment_type = employment_type
    
    self.Bind(wx.lib.intctrl.EVT_INT, self.__set_monthly_hours, self)
    
  def __set_monthly_hours(self, event):
    """Event listener for the value."""
    self.employment_type.monthly_hours = self.GetValue()

class LinkedSpinCtr(wx.SpinCtrl):
  def __init__(self, turnus, *args, **kwargs):
    wx.SpinCtrl.__init__(self, *args, **kwargs)
    
    self.element = turnus

"""
This class behaves the same way as a normal wxComboBox.
The only difference is that it handles employment 
types internally.
"""    
class LinkedComboBox(wx.ComboBox):
  
  def __init__(self, *args, **kwargs):
    """The default constructor."""
  
    #TODO clean the imports
    from Scheduler.global_vars import employment_types
    
    wx.ComboBox.__init__(self, *args, **kwargs)
    self.employment_types = employment_types.get_all ( )
    
    self.Clear()
    for employment_type in self.employment_types:
      self.Append(str(employment_type))
      
    self.Disable()
    
    
  def set_selection(self, person):
    """
    Sets the selection.
      person: is an instance of either the Nurse or Doctor class
    """
    
    if person:
      self.Enable()
      self.SetStringSelection(str(person.employment_type))
    else:
      self.Disable()
        
  def get_selected_type(self):
    """
    Return the selected employement type if any.
      return: an employement type if a valid emplyement type was
              selected, None otherwise.
    """
    
    if self.employment_types:
      for employment_type in self.employment_types:
        if employment_type.label == self.GetValue():
          return employment_type
    else:
      return None
    
"""
This class behaves the same way as a normal wxCalendar.
It recognizes Slovenian holidays, and does not consider
Saturday as a weekend.
It has additional methods and returns a custom wrapper
around the python date object.
"""
class EnhancedCalendar(wx.calendar.CalendarCtrl):

                      
  def __init__(self, *args, **kwargs):
  
    wx.calendar.CalendarCtrl.__init__(self, *args, **kwargs)
    
    self.Bind(wx.calendar.EVT_CALENDAR_MONTH, self.__set_holidays, self)
    self.Bind(wx.calendar.EVT_CALENDAR_YEAR, self.__set_holidays, self)
    
    next_month = datetime.date(day=28, month=datetime.date.today().month, year=datetime.date.today().year) + datetime.timedelta(days=10)
    self.PySetDate(next_month.replace(day=1))
    self.__set_holidays(None)
        
  def __set_holidays(self, event):
    """Colors the holidays"""
    
    for date in self.__get_dates():
      if holiday.is_workfree(date):
        self.SetHoliday(date.day)
      else:
        self.ResetAttr(date.day)
      
    
  def __get_dates(self):
    """Returns a sorted list of days for the current date and month."""
    current_date = self.PyGetDate()
    dates = []
    for day in calendar.Calendar().itermonthdays(current_date.year, current_date.month):
      if day:
        dates.append(datetime.date(day=day, month=current_date.month, year=current_date.year))
              
    dates.sort()
    
    return dates

"""
Custom events to handle the new grid's functionality. 
"""
SelectEvent, EVT_GRID_SELECTED = wx.lib.newevent.NewCommandEvent ( )
    
"""
This class behaves the same way as a normal wxGrid.
It handles data containers, filtering and sorting internally.
"""
class EnhancedGrid (wx.grid.Grid):
  
  def __init__(self, container, *args, **kwargs):
    """
    The default constructor.
      container: an instance of the data container
    """
    wx.grid.Grid.__init__(self, *args, **kwargs)
    
    self.container = container
    self.index_map = {}
    self.sort_ascending = None
    
    self.SetCellHighlightPenWidth(-1) # disables the selected cell's bold border
    self.EnableEditing(False)
    self.__fill_grid()
    
    
    
    self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.__grid_clicked)
    self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.__grid_clicked)
    
  def delete (self):
    """
    Deletes the selected element from the global container.
    """
    if self.IsSelection ( ):
      self.container.delete (self.get_selected_element ( ))
      self.__fill_grid ( )
    
  def save (self):
    """
    Saves the contents of the grid. It always saves the whole grid (including filtered out elements) and
    preserves the sorting state.
    """
    self.container.save ( )
    
  def reload (self):
    """
    Writes the last saved state into the grid.
    """
    self.ClearSelection ( )
    self.container.load ( )
    self.__fill_grid ( )
    
  def search (self, search_list):
    """
    Displays only those entries, that match the search list.
      search_list: a list of strings
    """
    index = None
    if self.IsSelection():
      index = self.container.get_index(self.get_selected_element())
    
    self.container.set_filter(search_list)
    self.__fill_grid ( )
    
    #if there is only one element, select it
    if len (self.index_map) == 1:
      self.__select(-1, 0)
    #if there is an selected element, select it, if it passes the filter
    elif index != None:
      for row in self.index_map:
        if self.index_map[row] == index:
          self.__select(-1, row)
          break
      else:
        self.__select(-1, -1)
    #clear selection, if all else fails
    else:
      self.__select(-1, -1)
      
    
  def get_selected_element (self):
    """
    Returns the currently selected element.
      return: the element instance, None if there is no selection.
    """
    
    if self.IsSelection ( ):
      return self.container.get_element (self.index_map[self.GetSelectedRows( )[0]])
    else:
      return None
    
  def __sort (self, col):
    """
    Sorts and redraws the grid.
    """
    if self.sort_ascending:
      self.sort_ascending = False
    else:
      self.sort_ascending = True
    
    element = None
    if self.IsSelection():
      element = self.get_selected_element ( )
      
    self.container.sort(col, self.sort_ascending)
    self.__fill_grid()
    
    if element:
      for i in self.index_map:
        if self.container.get_element(self.index_map[i]) == element:
          self.__select(-1, i)
          break
      else:
        self.__select(-1, -1)
    else:
      self.__select(-1, -1)
      
    
  def __fill_grid(self):
    """
    Fills the grid, with the container's data.
    """
    
    self.ClearGrid( )
    self.SetTable(None)
      
    table, self.index_map = self.container.as_table_filtered()
    headers = table['header']
    rows = table['items']
    
    self.CreateGrid(len(rows),len(headers))
      
    for i in range(len(headers)):
      self.SetColLabelValue(i, headers[i])
      
    for i in range(len(rows)):
      for j in range(len(rows[i])):
        self.SetCellValue(i, j, rows[i][j])
        
    self.AutoSize ( )
    self.GetParent( ).GetSizer().Layout()
    
    
  def __select (self, col, row):
    if col >=-1:
      if row < 0:
        self.ClearSelection()
      else:
        self.SelectRow(row)
        
    wx.PostEvent(self.GetEventHandler(), SelectEvent(self.GetId()))
    
  def __grid_clicked(self, event):
    """
    Event listener for the cell selection.
    """
    if event.GetRow ( ) == -1:
      self.__sort(event.GetCol ( ))
    else:
      self.__select(event.GetCol ( ), event.GetRow ( ))
      
    