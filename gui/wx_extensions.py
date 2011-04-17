# -*- coding: Cp1250 -*-

from utils import holiday

import datetime

import wx
import wx.grid
import wx.calendar
import wx.lib.agw.aui
import wx.lib.intctrl
import wx.lib.newevent
import wx.lib.mixins.listctrl

from utils import calendar_utils

"""
This class behaves the same way as a normal wxCheckBox.
The only difference is that is also has an attribute
element.
Element is an instance, that is being manipulated by
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

  def __init__(self, *args, **kwargs):
    kwargs['choices'] = calendar_utils.get_month_names ( )
    wx.Choice.__init__(self, *args, **kwargs)
    
    next_month = datetime.date(day=28, month=datetime.date.today().month, year=datetime.date.today().year) + datetime.timedelta(days=10)
    self.SetSelection(next_month.month - 1)
    
  def get_value(self):
    """
    Returns an instance of the datetime.date, with current year, the selected
    month and the first day in the month.
      return: a datetime.date object
    """
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
    
    if self.elements:
      self.Select (0)
    
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
    """Returns the selected object, None if there is no slected object."""
    if self.elements:
      return self.elements[self.GetCurrentSelection()]
    else:
      #raise Exception ('Ni elmentov!')
      return None
    
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
  def __init__(self, element, *args, **kwargs):
    wx.SpinCtrl.__init__(self, *args, **kwargs)
    
    self.element = element
    
"""
This class is the list control, that auto sizes the last column.
"""
class EnhancedListCtrl (wx.ListCtrl, wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin):
  
  def __init__ (self, *args, **kwargs):
    """
    The default constructor.
    """
    wx.ListCtrl.__init__ (self, *args, **kwargs)
    wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin.__init__ (self)
    

"""
This class behaves the same way as a normal wxComboBox.
The only difference is that it handles employment 
types internally.
"""    
class LinkedComboBox(wx.ComboBox):
  
  def __init__(self, *args, **kwargs):
    """The default constructor."""
  
    #TODO clean the imports
    import global_vars
    
    wx.ComboBox.__init__(self, *args, **kwargs)
    self.employment_types = global_vars.get_employment_types ( ).get_all ( )
    
    self.Clear ( )
    for employment_type in self.employment_types:
      self.Append (str (employment_type))
      
    self.Disable ( )
    
    
  def set_selection(self, employment_type):
    """
    Sets the selection.
      person: is an instance of either the Nurse or Doctor class
    """
    
    if employment_type in self.employment_types:
      self.SetStringSelection (str (employment_type))
    else:
      self.Select (-1)
        
  def get_selected_type (self):
    """
    Return the selected employment type if any.
      return: an employment type if a valid employment type was
              selected, None otherwise.
    """
    
    if self.employment_types:
      for employment_type in self.employment_types:
        if employment_type.label == self.GetValue():
          return employment_type
    else:
      return None

"""
This class is the same as the wx.aui.AuiNotebook. It is enhanced in a way, that enables it
to communicate with sizers, for getting the best size.
"""    
class EnhancedAUINotebook(wx.lib.agw.aui.AuiNotebook):
  
  def __init__ (self, *args, **kwargs):
    wx.lib.agw.aui.AuiNotebook.__init__(self, *args, **kwargs)
    
  def DoGetBestSize (self):
    """
    Return an wx.Size object, that represents the best size of this control.
      @return: a wx.Size object
    """
    notebook_size = self.GetBestSize ( ) 
    panel_size    = wx.Size (0, 0) 
    for i in range (self.GetPageCount ( )):
      page_size = self.GetPage (i).GetBestSize ( )
      if page_size.GetWidth ( ) > panel_size.GetWidth ( ):
        panel_size.SetWidth (page_size.GetWidth ( ))
      if page_size.GetHeight ( ) > panel_size.GetHeight ( ):
        panel_size.SetHeight (page_size.GetHeight ( ))
    
    # calculate the best size by summing up the heigth and taking the panels width
    best_size = wx.Size (0, 0)
    best_size.SetWidth  (10 + panel_size.GetWidth  ( ))
    best_size.SetHeight (10 + panel_size.GetHeight ( ) + notebook_size.GetHeight ( ))
        
    return best_size 
    
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
    
    self.Bind(wx.EVT_PAINT, self.__paint)
    
    self.special_days = set ( )
    
  def mark_special_date (self, date):
    """
    Marks the date in special color.
    """
    self.special_days.add (date)
    if date in self.__get_dates ( ) and date in self.special_days:
      attr = wx.calendar.CalendarDateAttr (colText=wx.WHITE, colBack=wx.ColourDatabase ( ).Find ('MAROON'), colBorder=wx.NullColour, font=wx.NullFont, border=wx.calendar.CAL_BORDER_NONE)
      self.SetAttr (date.day, attr)
    else:
      self.__set_holidays (None)
    
  def unmark_special_date (self, date):
    """
    Removes the special color from the date.
    """
    if date in self.special_days:
      self.special_days.remove (date)
      if date in self.__get_dates ( ):
        self.__set_holidays (None)
        
  def __paint (self, event):
    self.__set_holidays (None)
    for date in sorted (self.special_days):
      self.mark_special_date (date)
    event.Skip ( )
    
        
  def __set_holidays(self, event):
    """Colors the holidays"""
    
    for date in self.__get_dates ( ):
      if holiday.is_workfree(date):
        self.SetHoliday(date.day)
      else:
        self.ResetAttr(date.day)
      
    
  def __get_dates(self):
    """
    Returns a sorted list of days for the current date and month.
      @return: an ordered list of datetime.date objects
    """
    return calendar_utils.get_same_month_dates (self.PyGetDate ( ))
  
  def Enable (self, arg=True):
    """
    Overrides the main method.
    """
    if arg:
      self.SetHighlightColours (wx.WHITE, wx.BLUE)
    else:
      self.SetHighlightColours (wx.BLACK, wx.WHITE)
    super(EnhancedCalendar, self).Enable (arg)
    self.Refresh ( )
    
  def Disable (self):
    """
    Overrides the main method.
    """
    self.Enable (False)
    

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
    
    self.SetCellHighlightPenWidth(-1) # disables the selected cell's bold border
    self.EnableEditing(False)
    self.__fill_grid ( )
    
    self.Bind (wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.__grid_clicked)
    self.Bind (wx.grid.EVT_GRID_CELL_LEFT_CLICK,  self.__grid_clicked)
  
  def AutoSize (self):
    """
    Overrides the main method.
    Adds a label sizing ability.
    """
    super (EnhancedGrid, self).AutoSize ( )
    self.__autosize_labels ( )
    
  def Refresh (self):
    """Overrides the default function."""
    self.__fill_grid ( )
    super (EnhancedGrid, self).Refresh ( )
    
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
      search_list: a list of strings. If it is an empty list, all items will be displayed.
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
    
  def select_element (self, element):
    """
    Selects the element, if possible.
      element: a data object, that will be selected
    """
    index = self.container.get_index (element)
    for i in self.index_map:
      if self.index_map[i] == index:
        self.__select(-1, i)
        break
    
  def __sort (self, col):
    """
    Sorts and redraws the grid.
    """    
    element = None
    if self.IsSelection():
      element = self.get_selected_element ( )
      
    self.container.sort(col)
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
      
    table, self.index_map = self.container.as_table_filtered ( )
    headers = table['header']
    rows = table['items']
    
    self.CreateGrid(len(rows),len(headers))
      
    for i in range(len(headers)):
      self.SetColLabelValue(i, headers[i])
      
    for i in range(len(rows)):
      for j in range(len(rows[i])):
        self.SetCellValue(i, j, rows[i][j])
        self.SetCellAlignment (i, j, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        
    sort_state = self.container.get_sorting_state ( )
    if (sort_state[0] != None) and (sort_state[1] != None):
      if sort_state[0] < 0:
        lab = ''
      else:
        lab = headers[sort_state[0]]
      if sort_state[1]:
        self.SetColLabelValue(sort_state[0], lab + ' »')
      else:
        self.SetColLabelValue(sort_state[0], lab + ' «')
        
    self.AutoSize ( )
    self.GetParent( ).GetSizer ( ).Layout ( )
    
    
  def __select (self, col, row):
    if col >=-1:
      if row < 0:
        self.ClearSelection ( )
      else:
        self.MakeCellVisible (row, 0)
        self.SelectRow(row)
        
    wx.PostEvent(self.GetEventHandler(), SelectEvent(self.GetId()))
    
  def __grid_clicked(self, event):
    """
    Event listener for the cell selection.
    """
    if event.GetRow ( ) == -1 and event.GetCol ( ) != -1:
      self.__sort(event.GetCol ( ))
    else:
      self.__select(event.GetCol ( ), event.GetRow ( ))
      
  def __autosize_labels (self):
    """
    This method sizes all the labels.
    """
    # Common setup.
    devContext = wx.ScreenDC ( )
    devContext.SetFont (self.GetLabelFont ( ))
    
    # First do row labels.
    maxWidth = 0
    curRow   = self.GetNumberRows() - 1
    while curRow >= 0:
            curWidth = devContext.GetTextExtent ("M%s"% (self.GetRowLabelValue (curRow)))[0]
            if curWidth > maxWidth:
                    maxWidth = curWidth
            curRow = curRow - 1
    self.SetRowLabelSize (maxWidth)
    
    # Then column labels.
    maxHeight = 0
    curCol    = self.GetNumberCols ( ) - 1
    while curCol >= 0:
            (_,h,d,l) = devContext.GetFullTextExtent (self.GetColLabelValue (curCol))
            curHeight = h + d + l + 4
            if curHeight > maxHeight:
                    maxHeight = curHeight
            curCol = curCol - 1
    self.SetColLabelSize (maxHeight)
    
    # even the column width
    width = 0
    for i in range (self.GetNumberCols ( ) - 1):
      if self.GetColSize (i) > width:
        width = self.GetColSize (i)
    for i in range (self.GetNumberCols ( ) - 1):
      self.SetColSize (i, width)
      
    