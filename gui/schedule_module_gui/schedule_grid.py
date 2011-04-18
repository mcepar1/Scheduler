# -*- coding: Cp1250 -*-

"""
This file contains a wxGrid, specialized for displaying the schedule.
"""

import wx.grid

from gui import custom_events
from utils import holiday

"""
This class is the grid.
"""
class ScheduleGrid (wx.grid.Grid):
  
  def __init__ (self, *args, **kwargs):
    """
    The default constructor.
    """
    wx.grid.Grid.__init__ (self, *args, **kwargs)
    
    self.container = None
    
    self.SetCellHighlightPenWidth(-1) # disables the selected cell's bold border
    self.EnableEditing (False)
    
    self.Bind (wx.grid.EVT_GRID_RANGE_SELECT, self.__range_selected)
    self.Bind (wx.grid.EVT_GRID_SELECT_CELL,  self.__cell_selected)
    
  def AutoSize (self):
    """
    Overrides the main method.
    Adds a label sizing ability.
    """
    super (ScheduleGrid, self).AutoSize ( )
    self.__autosize_labels ( )
    
  def set_unit (self, container):
    """
    Set's the displayed container.
      @param container: a schedule container object
    """
    self.container = container
    self.__set_permissions ( )
    
  def select (self, people, dates):
    """
    Selects the matching area of the grid.
      @param people: a list of data objects
      @param dates: a list of datetime.date object
    """
    if people and dates:
      top    = self.GetNumberRows ( ) + 1
      bottom = -1
      
      left   = self.GetNumberCols ( ) + 1
      right  = -1
      
      #get top and bottom index
      for i, person in enumerate (self.container.get_filtered ( )):
        if person in people:
          if i < top:
            top = i
          if i > bottom:
            bottom = i 
            
      #get the left and right index
      for i, date in enumerate (self.container.get_dates (range (self.GetNumberCols ( ) - 1))):
        if date in dates:
          if i < left:
            left = i
          if i > right:
            right = i
      
      if top < self.GetNumberRows ( ) and bottom > -1 and left < self.GetNumberCols ( ) and right > -1:    
        self.SelectBlock (top, left, bottom, right)
        self.MakeCellVisible (top, right)
    
  def refresh (self):
    """
    Redraws the grid.
    """    
    self.__set_permissions ( )
    
    
  def toggle_view (self, compact):
    """
    Sets the type of the view, that will be displayed.
      @param compact: a boolean that defines the view. Compact view if True, full view if False.
    """
    self.container.set_compact (compact)
    self.__set_permissions ( )
    
  def is_compact (self):
    """
    Checks, if this container is set to the compact view mode.
      @return: True, if it compact, False otherwise.
    """
    if self.container:
      return self.container.is_compact ( )
    else:
      return False
    
  def set_span (self, full):
    """
    Sets the date range of the view. Span can be set to full (the neighbouring months) or normal (only the
    main scheduling month).
      @param full: a boolean that sets the span. True if full span, False otherwise. 
    """
    self.container.set_span (full)
    self.__set_permissions ( )
    
  def is_full_span (self):
    """
    Checks, if this container is set to the full span view mode.
      @return: True, if it is full, False otherwise.
    """
    return self.container.is_full_span ( )
    
  def __set_permissions (self):
    """
    Keeps the GUI in check with the data.
    """
    self.__fill_grid ( )
    
  def __fill_grid (self):
    """
    (Re)populates the grid.
    """
    
    table   = self.container.as_table ( )
    headers = table['header']
    titles  = table['titles']
    rows    = table['items']
    
    self.ClearGrid ( )
    self.SetTable (None)
    self.CreateGrid (len (rows), len (headers))
    
    for i in range (len (headers)):
      self.SetColLabelValue (i, headers[i])
      
    for i in range (len (titles)):
      self.SetRowLabelValue (i, titles[i])
    
    #for i in range  
    for i in range(len(rows)):
      for j in range(0, len(rows[i])):
        self.SetCellValue (i, j, rows[i][j])
        if self.is_compact ( ):
          self.SetCellAlignment (i, j, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        else:
          self.SetCellAlignment (i, j, wx.ALIGN_LEFT,   wx.ALIGN_CENTER)
          
    self.__format ( )       
    self.AutoSize ( )
    
  def __format (self):
    """
    Formats the grid.
    """
    # sets the background colors
    colors = self.container.get_colors ( )
    for i in range (len (colors)):
      for j in range (len (colors[i])):
        self.SetCellBackgroundColour (i, j, colors[i][j])
        
    # sets the holiday label color.
    for i, date in enumerate (self.container.get_dates (range (self.GetNumberCols ( )))):
      if holiday.is_workfree (date):
        for j in range (self.GetNumberRows ( )):
          print self.GetCellValue(j, i), len (self.GetCellValue(j, i))
          if len (self.GetCellValue(j, i)) != 0:
            font = self.GetCellFont (j, i)
            font.SetWeight (wx.FONTWEIGHT_BOLD)
            self.SetCellFont (j, i, font)
          else:
            self.SetCellBackgroundColour (j, i, (250, 235, 215))
    
    
  def __cell_selected (self, event):
    """
    Event listener for a single cell selection.
    """
    if event.Selecting ( ):
      self.SelectBlock (event.GetRow ( ), event.GetCol ( ), event.GetRow ( ), event.GetCol ( ))
      
      dates  = self.container.get_dates  ([event.GetCol ( )])
      people = self.container.get_people ([event.GetRow ( )])
      wx.PostEvent (self.GetEventHandler ( ), custom_events.ComplexSelectEvent (self.GetId ( ), dates=dates, people=people))
    
    event.Skip ( )
    
  def __range_selected (self, event):
    """
    Event listener for the multiple selection.
    """
    if event.Selecting ( ):
      dates  = self.container.get_dates  (range (event.GetTopLeftCoords ( )[1], event.GetBottomRightCoords ( )[1] + 1))
      people = self.container.get_people (range (event.GetTopLeftCoords ( )[0], event.GetBottomRightCoords ( )[0] + 1))
      wx.PostEvent (self.GetEventHandler ( ), custom_events.ComplexSelectEvent (self.GetId ( ), dates=dates, people=people))
    event.Skip ( )
    
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
    
    