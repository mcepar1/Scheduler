# -*- coding: Cp1250 -*-

"""
This file contains a wxGrid, specialized for displaying the schedule.
"""

import wx.grid

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
        self.SetCellValue(i, j, rows[i][j])
        self.SetReadOnly (i, j)
        
    self.AutoSize ( )
    
  def __autosize_labels(self):
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
    