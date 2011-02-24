# -*- coding: Cp1250 -*-

import wx

from Scheduler.global_vars import turnus_types
from Scheduler.gui import wx_extensions
from Scheduler.gui import common


class TurnusTypePanel(wx.Panel):
  def __init__(self,parent):
    wx.Panel.__init__(self, parent)
    
    sizer = wx.BoxSizer(wx.VERTICAL)
    
    self.toolbar = common.NotebookPageToolbar (self, wx.NewId ( ), style = wx.TB_HORIZONTAL | wx.TB_FLAT | wx.TB_NODIVIDER)
    sizer.Add(self.toolbar, 0, wx.ALIGN_LEFT)
    
    self.grid = wx_extensions.EnhancedGrid (turnus_types, self, wx.NewId ( ))
    sizer.Add(self.grid, 1, wx.ALIGN_LEFT)
    
    self.Bind(common.EVT_TB_ADD,    self.__add,    self.toolbar)
    self.Bind(common.EVT_TB_REMOVE, self.__remove, self.toolbar)
    self.Bind(common.EVT_TB_SAVE,   self.__save,   self.toolbar)
    self.Bind(common.EVT_TB_SEARCH, self.__search, self.toolbar)
    
    self.SetSizerAndFit(sizer)
    

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
    