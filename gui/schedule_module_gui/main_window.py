# -*- coding: Cp1250 -*-

import wx

import os


from gui import custom_events, wx_extensions
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
    
    self.generated_results = 1
    
    self.notebook_toolbar = NotebookPageToolbar (self, wx.ID_ANY, style = wx.TB_HORIZONTAL | wx.TB_FLAT | wx.TB_NODIVIDER)
    self.notebook = wx_extensions.EnhancedAUINotebook (self, wx.ID_ANY)
    import schedule_page
    self.notebook.AddPage(schedule_page.SchedulePage (proxy, self.notebook, wx.ID_NEW), 'Razpored ' + str (self.generated_results))
    
    self.Bind (custom_events.EVT_TB_ADD,    self.__add,     id=wx.ID_NEW)
    self.Bind (custom_events.EVT_TB_TOGGLE, self.__toggle,  self.notebook_toolbar)
    self.Bind (custom_events.EVT_TB_SEARCH, self.__display, self.notebook_toolbar)
    self.Bind (custom_events.EVT_TB_START,  self.__start,   self.notebook_toolbar)
    
    sizer = wx.BoxSizer (wx.VERTICAL)
    sizer.Add(self.notebook_toolbar, 0, wx.ALIGN_LEFT | wx.EXPAND)
    sizer.Add(self.notebook,         1, wx.ALIGN_LEFT | wx.EXPAND)
    
    self.SetSizerAndFit (sizer)
    self.SetIcon (make_icon (wx.Image (name = MainWindow.ICON_PATH)))
    self.Maximize ( )
    
    self.__set_permissions ( )
    
    
  def __add (self, event):
    self.notebook.GetCurrentPage ( ).add_schedule ( )
    self.__set_permissions ( )
    
  def __toggle (self, event):
    page = self.notebook.GetCurrentPage ( )
    page.toggle_workers (event.toggle)
    self.__set_permissions ( )
    
  def __display (self, event):
    page = self.notebook.GetCurrentPage ( )
    page.set_displayed (self.notebook_toolbar.get_selected_choice ( ))
    
  def __start (self, event):
    page = self.notebook.GetCurrentPage ( )
    self.__display (event)
    page.start_scheduling ( )
    
  def __set_permissions (self):
    page = self.notebook.GetCurrentPage ( )
    self.notebook_toolbar.set_choices(page.get_results ( ), page.get_displayed ( ))
    self.notebook_toolbar.set_toggle (page.is_workers_shown ( ))
    
"""
This is a toolbar, that is linked with the notebook's pages.
"""
class NotebookPageToolbar (wx.ToolBar):
  
  def __init__ (self, *args, **kwargs):
    """
    The default constructor.
    """  
    wx.ToolBar.__init__ (self, *args, **kwargs)
    
    self.AddCheckLabelTool (wx.ID_EDIT,  'Prikaži število',     wx.ArtProvider.GetBitmap (wx.ART_LIST_VIEW,       wx.ART_TOOLBAR), shortHelp='Prikaži število zaposlenih v turnusu.')
    self.AddLabelTool      (wx.ID_RESET, 'Zaženi razporejanje', wx.ArtProvider.GetBitmap (wx.ART_EXECUTABLE_FILE, wx.ART_TOOLBAR), shortHelp='Zaženi razporejanje')
    self.AddSeparator ( )
    self.AddControl (wx.Choice (self, wx.ID_VIEW_LIST))
    
    self.Bind (wx.EVT_TOOL,   self.__toggle, id = wx.ID_EDIT)
    self.Bind (wx.EVT_CHOICE, self.__choice, id = wx.ID_VIEW_LIST)
    self.Bind(wx.EVT_TOOL,    self.__start,  id = wx.ID_RESET)
    
    self.Realize ( )
    
  def set_toggle (self, toggle):
    """
    Sets the toggle button.
      @param toggle: a boolean that defines the toggle state.
    """
    self.ToggleTool (wx.ID_EDIT, toggle)
    
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
    wx.PostEvent (self.GetEventHandler ( ), custom_events.ToggleEvent (self.GetId ( ), toggle=event.IsChecked ( )))
    
  def __choice (self, event):
    """
    Event listener for the choice menu.
    """
    wx.PostEvent (self.GetEventHandler ( ), custom_events.SearchEvent (self.GetId ( )))
    
  def __start (self, event):
    """
    Event listener for the start / run button.
    """
    wx.PostEvent (self.GetEventHandler ( ), custom_events.StartEvent (self.GetId ( )))
    
