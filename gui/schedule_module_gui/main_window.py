# -*- coding: Cp1250 -*-

import wx

import os

import schedule_page
from gui import custom_events
from gui.utils_gui import make_icon


"""
This class represents the Main window for the entire scheduling process.
"""
class MainWindow(wx.Frame):

  TITLE     = 'Razpored'
  PARENT    = None
  ICON_PATH = os.path.join ('persistence', 'gui', 'clock.png')

  def __init__(self, proxy, parent):
    wx.Frame.__init__(self, parent, title = MainWindow.TITLE + ': ' + str (proxy), style = wx.DEFAULT_FRAME_STYLE)
    
    self.notebook_toolbar = NotebookPageToolbar (self, wx.ID_ANY, style = wx.TB_HORIZONTAL | wx.TB_FLAT | wx.TB_NODIVIDER)
    self.schedule_page = schedule_page.SchedulePage (proxy, self, wx.ID_ANY)
    
    self.Bind (custom_events.EVT_TB_ADD,    self.__add,     self.notebook_toolbar)
    self.Bind (custom_events.EVT_TB_TOGGLE, self.__toggle,  self.notebook_toolbar)
    self.Bind (custom_events.EVT_TB_SEARCH, self.__display, self.notebook_toolbar)
    self.Bind (custom_events.EVT_TB_START,  self.__start,   self.notebook_toolbar)
    self.Bind (custom_events.EVT_TB_SAVE,   self.__save,    self.notebook_toolbar)
    self.Bind (custom_events.EVT_TB_RELOAD, self.__reload,  self.notebook_toolbar)
    
    sizer = wx.BoxSizer (wx.VERTICAL)
    sizer.Add(self.notebook_toolbar, 0, wx.ALIGN_LEFT | wx.EXPAND)
    sizer.Add(self.schedule_page,    1, wx.ALIGN_LEFT | wx.EXPAND)
    
    self.SetSizerAndFit (sizer)
    self.SetIcon (make_icon (wx.Image (name = MainWindow.ICON_PATH)))
    self.Maximize ( )
    
    self.__set_permissions ( )
    
    
  def __add (self, event):
    self.schedule_page.add_schedule ( )
    self.__set_permissions ( )
    
  def __toggle (self, event):
    if event.source == wx.ID_EDIT:
      self.schedule_page.toggle_workers (event.toggle)
    elif event.source == wx.ID_VIEW_DETAILS:
      self.schedule_page.toggle_view    (event.toggle)
    elif event.source == wx.ID_VIEW_SORTDATE:
      self.schedule_page.set_span (event.toggle)
    self.__set_permissions ( )
    
  def __display (self, event):
    self.schedule_page.set_displayed (self.notebook_toolbar.get_selected_choice ( ))
    self.__set_permissions ( )
    
  def __start (self, event):
    self.__display (event)
    self.schedule_page.start_scheduling ( )
    
  def __save (self, event):
    self.schedule_page.save ( )
    
  def __reload (self, event):
    self.schedule_page.synchronize_workers ( )
    self.__set_permissions ( )
    
  def __set_permissions (self):
    self.notebook_toolbar.set_choices        (self.schedule_page.get_results ( ), self.schedule_page.get_displayed ( ))
    self.notebook_toolbar.set_toggle_workers (self.schedule_page.is_workers_shown ( ))
    self.notebook_toolbar.set_toggle_view    (self.schedule_page.is_compact ( ))
    self.notebook_toolbar.set_toggle_span    (self.schedule_page.is_full_span ( ))
    
"""
This is a toolbar, that is linked with the notebook's pages.
"""
class NotebookPageToolbar (wx.ToolBar):
  
  def __init__ (self, *args, **kwargs):
    """
    The default constructor.
    """  
    wx.ToolBar.__init__ (self, *args, **kwargs)
    
    self.AddCheckLabelTool (wx.ID_EDIT,          'Prikaži število',                            wx.ArtProvider.GetBitmap (wx.ART_LIST_VIEW,       wx.ART_TOOLBAR), shortHelp='Prikaži število zaposlenih v turnusu.')
    self.AddCheckLabelTool (wx.ID_VIEW_DETAILS,  'Kompakten/poln pogled',                      wx.ArtProvider.GetBitmap (wx.ART_REPORT_VIEW,     wx.ART_TOOLBAR), shortHelp='Preklapljaj med polnim in minimalnim izgledom')
    self.AddCheckLabelTool (wx.ID_VIEW_SORTDATE, 'Prikaži celoten razpon/samo trenuten mesec', wx.ArtProvider.GetBitmap (wx.ART_HELP_SIDE_PANEL, wx.ART_TOOLBAR), shortHelp='Prikaži tudi sosednja meseca')
    self.AddSeparator ( )
    self.AddLabelTool      (wx.ID_NEW,    'Ustvari nov razpored',  wx.ArtProvider.GetBitmap (wx.ART_NEW,             wx.ART_TOOLBAR), shortHelp='Ustvari nov razpored')
    self.AddLabelTool      (wx.ID_RESET,  'Zaženi razporejanje',   wx.ArtProvider.GetBitmap (wx.ART_EXECUTABLE_FILE, wx.ART_TOOLBAR), shortHelp='Zaženi razporejanje')
    self.AddSeparator ( )
    self.AddLabelTool      (wx.ID_SAVE,   'Shrani razpored',       wx.ArtProvider.GetBitmap (wx.ART_FILE_SAVE,       wx.ART_TOOLBAR), shortHelp='Shrani razpored')
    self.AddLabelTool      (wx.ID_REVERT, 'Obnovi zaposlene',      wx.ArtProvider.GetBitmap (wx.ART_UNDO,            wx.ART_TOOLBAR), shortHelp='Obnovi število zaposlenih na vrednost trenutno prikazanega razporeda.')
    
    self.AddSeparator ( )
    self.AddControl (wx.Choice (self, wx.ID_VIEW_LIST))
    
    self.Bind (wx.EVT_TOOL,   self.__toggle, id = wx.ID_EDIT)
    self.Bind (wx.EVT_TOOL,   self.__toggle, id = wx.ID_VIEW_DETAILS)
    self.Bind (wx.EVT_TOOL,   self.__toggle, id = wx.ID_VIEW_SORTDATE)
    self.Bind (wx.EVT_CHOICE, self.__choice, id = wx.ID_VIEW_LIST)
    self.Bind (wx.EVT_TOOL,   self.__add,    id = wx.ID_NEW)
    self.Bind (wx.EVT_TOOL,   self.__start,  id = wx.ID_RESET)
    self.Bind (wx.EVT_TOOL,   self.__save,   id = wx.ID_SAVE)
    self.Bind (wx.EVT_TOOL,   self.__revert, id = wx.ID_REVERT)
    
    self.Realize ( )
    
  def set_toggle_workers (self, toggle):
    """
    Sets the toggle workers button.
      @param toggle: a boolean that defines the toggle state.
    """
    self.ToggleTool (wx.ID_EDIT, toggle)
    
  def set_toggle_view (self, toggle):
    """
    Sets the toggle full or compact view button.
      @param toggle: a boolean that defines the toggle state.
    """
    self.ToggleTool (wx.ID_VIEW_DETAILS, toggle)
    
  def set_toggle_span (self, toggle):
    """
    Sets the toggle span button.
      @param toggle: a boolean that defines the toggle state.
    """
    self.ToggleTool (wx.ID_VIEW_SORTDATE, toggle)
    
  def get_selected_choice (self):
    """
    Returns the selected choice.
      @return: a string
    """
    wx_choice = self.FindControl (wx.ID_VIEW_LIST)
    return wx_choice.GetStringSelection ( )
    
  def set_choices (self, choices, selected=None):
    """
    Sets the choices in the drop-down menu and selects a choice, if the parameter was specified.
      @param choices: a list of strings
      @param selected: a string. Default is value is set to None.
    """
    wx_choice = self.FindControl (wx.ID_VIEW_LIST)
    wx_choice.Clear ( )
    wx_choice.AppendItems (choices)
    
    if selected != None and selected in choices:
      wx_choice.Select (choices.index (selected))
      
  def __toggle (self, event):
    """
    Event listener for the toggle button.
    """
    wx.PostEvent (self.GetEventHandler ( ), custom_events.ToggleEvent (self.GetId ( ), toggle=event.IsChecked ( ), source=event.GetId ( )))
    
  def __choice (self, event):
    """
    Event listener for the choice menu.
    """
    wx.PostEvent (self.GetEventHandler ( ), custom_events.SearchEvent (self.GetId ( )))
    
  def __add (self, event):
    """
    Event listener for the add menu.
    """
    wx.PostEvent (self.GetEventHandler ( ), custom_events.AddEvent (self.GetId ( )))
    
  def __start (self, event):
    """
    Event listener for the start / run button.
    """
    wx.PostEvent (self.GetEventHandler ( ), custom_events.StartEvent (self.GetId ( )))
    
  def __save (self, event):
    """
    Event listener for the save button.
    """
    wx.PostEvent (self.GetEventHandler ( ), custom_events.SaveEvent (self.GetId ( )))
    
  def __revert (self, event):
    """
    Event listener for the revert button.
    """
    wx.PostEvent (self.GetEventHandler ( ), custom_events.ReloadEvent (self.GetId ( )))
    
