# -*- coding: Cp1250 -*-

import wx
import wx_extensions
import wx.lib.scrolledpanel


from schedule_module_gui import main_window
from gui import custom_events
from scheduler import proxy

class SchedulesPanel(wx.lib.scrolledpanel.ScrolledPanel):
  def __init__(self, workplaces, roles, turnus_types, *args, **kwargs):
    wx.lib.scrolledpanel.ScrolledPanel.__init__(self, *args, **kwargs)
    
    
    self.workplaces   = workplaces
    self.roles        = roles
    self.turnus_types = turnus_types
    
    self.toolbar = SchedulersPageToolbar          (self, wx.NewId ( ), style = wx.TB_HORIZONTAL | wx.TB_FLAT | wx.TB_NODIVIDER)
    self.list    = wx_extensions.EnhancedListCtrl (self, wx.ID_ANY, style=wx.LC_REPORT | wx.BORDER_NONE | wx.LC_HRULES)
    
    self.__build_list ( )
    
    self.Bind (custom_events.EVT_TB_CREATE, self.__show, self.toolbar)
    
    list_sizer = wx.StaticBoxSizer (wx.StaticBox (self, wx.ID_ANY, 'Razporedi'), wx.VERTICAL)
    list_sizer.Add (self.list, 1, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
    sizer = wx.BoxSizer (wx.VERTICAL)
    sizer.Add (self.toolbar, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    sizer.Add (list_sizer,   1, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
    self.SetSizerAndFit (sizer)
    self.SetupScrolling( )
    
  def __build_list (self):
    """
    Constructs the list, that displays the existing schedules.
    """
    self.list.InsertColumn (0, "Mesec", wx.LIST_FORMAT_CENTER)
    self.list.InsertColumn (1, "Leto",  wx.LIST_FORMAT_LEFT)
    
    for vals in proxy.get_saved_schedules ( ):
      self.list.Append (vals)

    self.list.SetColumnWidth (0, 80)
    self.list.SetColumnWidth (1, wx.LIST_AUTOSIZE)
    self.list.SetMinSize ((133,50))
    
    
  
    
  def __show (self, event):

    import global_vars
    p = proxy.DataToSchedule (False, event.date, global_vars.get_nurses(), global_vars.get_scheduling_units(), global_vars.get_turnus_types())
    f = main_window.MainWindow  (p, self)
    f.Show ( )
    
"""
This is a toolbar, that is displayed on the top of every Page.
"""
class SchedulersPageToolbar (wx.ToolBar):
  
  CREATE = wx.NewId ( )
  OPEN   = wx.NewId ( )
  REMOVE = wx.NewId ( )
  
  def __init__ (self, *args, **kwargs):
    """
    The default constructor.
    """
    wx.ToolBar.__init__(self, *args, **kwargs)
    
    self.year_month_choice = MonthYearWrapper (self)
    
    self.AddLabelTool(SchedulersPageToolbar.CREATE, 'Nov razpored',           wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR),       shortHelp='Ustvari nov razpored')
    self.AddControl(self.year_month_choice.get_month_control ( ))
    self.AddControl(self.year_month_choice.get_year_control ( ))
    self.AddSeparator ( )
    
    self.AddLabelTool(SchedulersPageToolbar.OPEN,   'Odpri obsojeć razpored', wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR), shortHelp='Odpri obsoječ razpored')
    self.AddLabelTool(SchedulersPageToolbar.REMOVE, 'Izbriši',                wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_TOOLBAR),    shortHelp='Izbriši izbrano')
    self.AddSeparator ( )
    
    self.search = wx.SearchCtrl (self, wx.ID_FIND, style=wx.TB_HORIZONTAL | wx.TB_NODIVIDER)
    self.search.SetDescriptiveText ('Iskanje')
    self.search.ShowSearchButton (True)
    self.search.ShowCancelButton (True)
    
    self.AddControl(self.search)
    
    self.Bind(wx.EVT_TOOL, self.__create,    id = SchedulersPageToolbar.CREATE)
    #self.Bind(wx.EVT_TOOL, self.__remove, id = NotebookPageToolbar.REMOVE)
    #self.Bind(wx.EVT_TOOL, self.__save,   id = NotebookPageToolbar.SAVE)
    #self.Bind(wx.EVT_TOOL, self.__reload, id = NotebookPageToolbar.RELOAD)
    
    #self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.__clear_search, self.search)
    #self.Bind(wx.EVT_TEXT, self.__search)
    
    # this hack enables clearing the search field with the escape key
    #if wx.Platform in ['__WXGTK__', '__WXMSW__']:
    #  for child in self.search.GetChildren():
    #    if isinstance(child, wx.TextCtrl):
    #      child.Bind(wx.EVT_KEY_UP, self.__key_pressed)
    #      break
    self.EnableTool (SchedulersPageToolbar.OPEN, False)
    self.EnableTool (SchedulersPageToolbar.REMOVE, False)
    self.search.Disable ( )
    self.Realize ( )
    
  def __create (self, event):
    """
    Event listener for the create schedule button.
    """
    wx.PostEvent(self, custom_events.CreateEvent (self.GetId ( ), date=self.year_month_choice.get_selected_date ( )))

"""
This class is a wrapper around the month and year drop-down widgets. Works similar as the  MonthYearSelector
in the custom widgets. It is implemented in a way so that it can be used in the toolbar.
"""    
class MonthYearWrapper:
  
  def __init__ (self, parent):
    """
    The default constructor.
      @param parent: the toolbar, that will contain the controls.
    """
    
    self.__months = wx_extensions.MonthChoice (parent, wx.ID_ANY)
    self.__years  = wx.Choice (parent, wx.ID_ANY)
    
    year = self.__months.get_value ( ).year
    self.__years.SetItems ([str (year - 1), str (year), str (year + 1)])
    self.__years.Select (1)
    
  def get_month_control (self):
    """
    Returns the control for selecting months.
      @return: a wx.Control object
    """
    return self.__months
  
  def get_year_control (self):
    """
    Return the control for selecting years.
      @return: a wx.Control object
    """
    return self.__years
    
  def get_selected_date (self):
    """
    Returns a datetime.date object, that represents the selected combination.
      @return: a datetime.date object
    """
    return self.__months.get_value ( ).replace (year = int (self.__years.GetItems ( )[self.__years.GetSelection ( )]))
    