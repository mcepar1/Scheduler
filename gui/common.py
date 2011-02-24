# -*- coding: Cp1250 -*-

import wx
import wx.lib.newevent

from Scheduler.gui import wx_extensions

"""
New events, for easier communication between the toolbar and it's parents.
"""
AddEvent,    EVT_TB_ADD    = wx.lib.newevent.NewCommandEvent ( )
RemoveEvent, EVT_TB_REMOVE = wx.lib.newevent.NewCommandEvent ( )
SaveEvent,   EVT_TB_SAVE   = wx.lib.newevent.NewCommandEvent ( )
ReloadEvent, EVT_TB_RELOAD = wx.lib.newevent.NewCommandEvent ( )
SearchEvent, EVT_TB_SEARCH = wx.lib.newevent.NewCommandEvent ( )

"""
This is a standard GUI panel, for editing the data elements.
"""
class GenericTablePanel(wx.Panel):
  def __init__(self, container, *args, **kwargs):
    
    edit_panel = None
    if 'edit_panel' in kwargs:
      edit_panel = kwargs['edit_panel']
      del kwargs['edit_panel']
    
    wx.Panel.__init__(self, *args, **kwargs)
    
    sizer = wx.BoxSizer(wx.VERTICAL)
    self.SetSizer (sizer)
    
    self.toolbar = NotebookPageToolbar (self, wx.NewId ( ), style = wx.TB_HORIZONTAL | wx.TB_FLAT | wx.TB_NODIVIDER)
    sizer.Add(self.toolbar, 0, wx.ALIGN_LEFT | wx.EXPAND)
    
    self.grid = wx_extensions.EnhancedGrid (container, self, wx.NewId ( ))
    self.edit_panel = None
    if edit_panel:
      self.edit_panel = edit_panel (self, wx.NewId())
      
      sub_sizer = wx.BoxSizer (wx.HORIZONTAL)
      sub_sizer.Add (self.edit_panel, 0, wx.ALIGN_LEFT | wx.SHAPED)
      sub_sizer.Add (self.grid, 1, wx.CENTER | wx.LEFT | wx.EXPAND, 4)
      sizer.Add (sub_sizer, 1, wx.EXPAND)
    else:
      sizer.Add(self.grid, 1, wx.ALIGN_LEFT | wx.EXPAND)
    
    
    self.Bind(EVT_TB_ADD,    self.__add,    self.toolbar)
    self.Bind(EVT_TB_REMOVE, self.__remove, self.toolbar)
    self.Bind(EVT_TB_SAVE,   self.__save,   self.toolbar)
    self.Bind(EVT_TB_RELOAD, self.__reload, self.toolbar)
    self.Bind(EVT_TB_SEARCH, self.__search, self.toolbar)
    

    self.Bind(wx_extensions.EVT_GRID_SELECTED, self.__element_selected, self.grid)
    self.__element_selected (None)
    
    self.SetSizerAndFit(sizer)
    
  def __element_selected(self, event):
    """
    Event listener for the grid selection.
    """
    self.toolbar.EnableRemove(bool (self.grid.get_selected_element ( )))
    
    if self.edit_panel:
      self.edit_panel.set_unit (self.grid.get_selected_element( ))

  def __add(self, event):
    """
    Adds a new element into the global container.
    """
    print 'Adding...'
    
  def __remove(self, event):
    """
    Removes an element from the global container.
    """
    self.grid.delete ( )
    self.__element_selected (None)
    
  def __save(self, event):
    """
    Saves the current state of the global container.
    """
    self.grid.save ( )
    
  def __reload(self, event):
    """
    Reloads the stored state of the global container.
    """
    self.grid.reload ( )
    self.__element_selected (None)
    
  def __search(self, event):
    """
    Searches the global container for the matching entries.
    """
    self.grid.search(self.toolbar.get_search_values())
    

"""
This is a toolbar, that is displayed on the top of every Page.
"""
class NotebookPageToolbar (wx.ToolBar):
  
  ADD    = wx.NewId ( )
  REMOVE = wx.NewId ( )
  SAVE   = wx.NewId ( )
  RELOAD = wx.NewId ( )
  
  def __init__ (self, *args, **kwargs):
    """
    The default constructor.
    """
    wx.ToolBar.__init__(self, *args, **kwargs)
    
    self.AddLabelTool(NotebookPageToolbar.ADD, 'Dodaj', wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR), shortHelp='Dodaj')
    self.AddLabelTool(NotebookPageToolbar.REMOVE, 'Izbriši', wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_TOOLBAR), shortHelp='Izbriši izbrano')
    self.AddSeparator ( )
    
    self.AddLabelTool(NotebookPageToolbar.SAVE, 'Shrani', wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR), shortHelp = 'Shrani podatke v tem oknu')
    self.AddLabelTool(NotebookPageToolbar.RELOAD, 'Razveljavi', wx.ArtProvider.GetBitmap(wx.ART_UNDO, wx.ART_TOOLBAR), shortHelp = 'Razveljavi vse neshranjene spremembe')
    
    self.AddSeparator ( )
    
    self.search = wx.SearchCtrl (self, wx.NewId ( ), style=wx.TB_HORIZONTAL | wx.TB_NODIVIDER)
    self.search.SetDescriptiveText ('Iskanje')
    self.search.ShowSearchButton (True)
    self.search.ShowCancelButton (True)
    
    self.AddControl(self.search)
    
    self.Bind(wx.EVT_TOOL, self.__add,    id = NotebookPageToolbar.ADD)
    self.Bind(wx.EVT_TOOL, self.__remove, id = NotebookPageToolbar.REMOVE)
    self.Bind(wx.EVT_TOOL, self.__save,   id = NotebookPageToolbar.SAVE)
    self.Bind(wx.EVT_TOOL, self.__reload, id = NotebookPageToolbar.RELOAD)
    
    self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.__clear_search, self.search)
    self.Bind(wx.EVT_TEXT, self.__search)
    
    # this hack enables clearing the search field with the escape key
    if wx.Platform in ['__WXGTK__', '__WXMSW__']:
      for child in self.search.GetChildren():
        if isinstance(child, wx.TextCtrl):
          child.Bind(wx.EVT_KEY_UP, self.__key_pressed)
          break
        
    self.Realize()
    
  def get_search_values (self):
    """
    Return a list of search strings.
      return: a list of strings
    """
    return self.search.GetValue ( ).split( )
  
  def EnableRemove (self, enable):
    """
    Enables and disables the delete button.
      enable: if set to true, the delete button will be enabled and vice-versa
    """
    self.EnableTool(NotebookPageToolbar.REMOVE, enable)
    
  def __search(self, event):
    """
    Fires the search event.
    """
    wx.PostEvent(self.GetEventHandler(), SearchEvent(self.GetId()))
    
  def __key_pressed (self, event):
    """
    Listens for the escape key and clears the search key, if pressed.
    """
    if event.GetKeyCode() == wx.WXK_ESCAPE:
      self.__clear_search(None)
    
  def __clear_search (self, event):
    """
    Clears the search field and fires the search event.
    """
    self.search.Clear()
    
  def __add (self, event):
    """
    Fires the add event.
    """
    wx.PostEvent(self.GetEventHandler(), AddEvent(self.GetId()))
    
  def __remove (self, event):
    """
    Fires the remove event.
    """
    wx.PostEvent(self.GetEventHandler(), RemoveEvent(self.GetId()))
    
  def __save (self, event):
    """
    Fires the save event.
    """
    wx.PostEvent(self.GetEventHandler(), SaveEvent(self.GetId()))
    
  def __reload (self, event):
    """
    Fires the reload event.
    """
    wx.PostEvent(self.GetEventHandler(), ReloadEvent(self.GetId()))
       
    