# -*- coding: Cp1250 -*-

import wx

from Scheduler.gui import wx_extensions
from Scheduler.gui import common


class GenericTablePanel(wx.Panel):
  def __init__(self, container, *args, **kwargs):
    
    edit_panel = None
    if 'edit_panel' in kwargs:
      edit_panel = kwargs['edit_panel']
      del kwargs['edit_panel']
    
    wx.Panel.__init__(self, *args, **kwargs)
    
    sizer = wx.BoxSizer(wx.VERTICAL)
    self.SetSizer (sizer)
    
    self.toolbar = common.NotebookPageToolbar (self, wx.NewId ( ), style = wx.TB_HORIZONTAL | wx.TB_FLAT | wx.TB_NODIVIDER)
    sizer.Add(self.toolbar, 0, wx.ALIGN_LEFT | wx.EXPAND)
    
    self.grid = wx_extensions.EnhancedGrid (container, self, wx.NewId ( ))
    self.edit_panel = None
    if edit_panel:
      self.edit_panel = edit_panel (self)
      
      sub_sizer = wx.BoxSizer (wx.HORIZONTAL)
      sub_sizer.Add (self.grid, 1, wx.CENTER | wx.EXPAND)
      sub_sizer.Add (self.edit_panel, 0, wx.ALIGN_LEFT | wx.LEFT, 4)
      sizer.Add (sub_sizer, 1, wx.EXPAND)
    else:
      sizer.Add(self.grid, 1, wx.ALIGN_LEFT | wx.EXPAND)
    
    
    self.Bind(common.EVT_TB_ADD,    self.__add,    self.toolbar)
    self.Bind(common.EVT_TB_REMOVE, self.__remove, self.toolbar)
    self.Bind(common.EVT_TB_SAVE,   self.__save,   self.toolbar)
    self.Bind(common.EVT_TB_SEARCH, self.__search, self.toolbar)
    
    if self.edit_panel:
      self.Bind(wx_extensions.EVT_GRID_SELECTED, self.__element_selected, self.grid)
    
    self.SetSizerAndFit(sizer)  
    
  def __element_selected(self, event):
    """
    Event listener for the grid selection.
    """
    self.edit_panel.set_unit (self.grid.get_selected_element( ))
    print self.grid.get_selected_element()  

  def __add(self, event):
    """
    Adds a new element into the global container.
    """
    print 'Adding...'
    
  def __remove(self, event):
    """
    Removes an element from the global container.
    """
    print 'Removing...'
    
  def __save(self, event):
    """
    Saves the current state of the global container.
    """
    print 'Saving...'
    
  def __search(self, event):
    """
    Searches the global container for the matching entries.
    """
    self.grid.search(self.toolbar.get_search_values())
    