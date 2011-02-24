# -*- coding: Cp1250 -*-

import wx
import wx.lib.newevent

"""
New events, for easier communication between the toolbar and it's parents.
"""
AddEvent,    EVT_TB_ADD    = wx.lib.newevent.NewCommandEvent ( )
RemoveEvent, EVT_TB_REMOVE = wx.lib.newevent.NewCommandEvent ( )
SaveEvent,   EVT_TB_SAVE   = wx.lib.newevent.NewCommandEvent ( )
SearchEvent, EVT_TB_SEARCH = wx.lib.newevent.NewCommandEvent ( )


"""
This is a toolbar, that is displayed on the top of every Page.
"""
class NotebookPageToolbar (wx.ToolBar):
  
  ADD = wx.NewId ( )
  REMOVE = wx.NewId ( )
  SAVE = wx.NewId ( )
  
  def __init__ (self, *args, **kwargs):
    """
    The default constructor.
    """
    wx.ToolBar.__init__(self, *args, **kwargs)
    
    self.AddLabelTool(NotebookPageToolbar.ADD, 'Dodaj', wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR), shortHelp='Dodaj')
    self.AddLabelTool(NotebookPageToolbar.REMOVE, 'Izbriši', wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_TOOLBAR), shortHelp='Izbriši izbrano')
    self.AddSeparator ( )
    
    self.AddLabelTool(NotebookPageToolbar.SAVE, 'Shrani', wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE), shortHelp = 'Shrani podatke v tem oknu')
    
    self.AddSeparator ( )
    
    self.search = wx.SearchCtrl (self, wx.NewId ( ), style=wx.TB_HORIZONTAL | wx.TB_NODIVIDER)
    self.search.SetDescriptiveText ('Iskanje')
    self.search.ShowSearchButton (True)
    self.search.ShowCancelButton (True)
    
    self.AddControl(self.search)
    
    self.Bind(wx.EVT_TOOL, self.__add,    id = NotebookPageToolbar.ADD)
    self.Bind(wx.EVT_TOOL, self.__remove, id = NotebookPageToolbar.REMOVE)
    self.Bind(wx.EVT_TOOL, self.__save,   id = NotebookPageToolbar.SAVE)
    
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
    return self.search.GetValue().split( )
    
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
    
    