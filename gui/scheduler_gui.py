# -*- coding: Cp1250 -*-

import wx
import wx.lib.scrolledpanel

from utils               import calendar_utils
from schedule_module_gui import main_window
from gui                 import custom_events, wx_extensions, observer_pattern
from scheduler           import proxy, schedule_utils

class SchedulesPanel(wx.lib.scrolledpanel.ScrolledPanel):
  def __init__(self, workplaces, roles, turnus_types, *args, **kwargs):
    wx.lib.scrolledpanel.ScrolledPanel.__init__(self, *args, **kwargs)
    
    
    self.workplaces    = workplaces
    self.roles         = roles
    self.turnus_types  = turnus_types
    self.search_values = []
    
    self.toolbar = SchedulersPageToolbar          (self, wx.ID_ANY, style = wx.TB_HORIZONTAL | wx.TB_FLAT | wx.TB_NODIVIDER)
    self.list    = wx_extensions.EnhancedListCtrl (self, wx.ID_ANY, style = wx.LC_REPORT | wx.BORDER_NONE | wx.LC_HRULES | wx.LC_SINGLE_SEL)
    
    self.__build_list ( )
    
    
    self.Bind (wx.EVT_LIST_ITEM_SELECTED,   self.__schedule_selected, self.list)
    self.Bind (custom_events.EVT_TB_BLANK,  self.__blank,             self.toolbar)
    self.Bind (custom_events.EVT_TB_CREATE, self.__create,            self.toolbar)
    self.Bind (custom_events.EVT_TB_OPEN,   self.__open,              self.toolbar)
    self.Bind (custom_events.EVT_TB_MERGE,  self.__merge,             self.toolbar)
    self.Bind (custom_events.EVT_TB_REMOVE, self.__remove,            self.toolbar)
    self.Bind (custom_events.EVT_UPDATED,   self.__select_schedule,   self.toolbar)
    self.Bind (custom_events.EVT_TB_SEARCH, self.__search,            self.toolbar)
    
    observer_pattern.register (self.__build_list, observer_pattern.SCHEDULER_SAVED)
    
    
    list_sizer = wx.StaticBoxSizer (wx.StaticBox (self, wx.ID_ANY, 'Razporedi'), wx.VERTICAL)
    list_sizer.Add (self.list, 1, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
    sizer = wx.BoxSizer (wx.VERTICAL)
    sizer.Add (self.toolbar, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    sizer.Add (list_sizer,   1, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
    self.SetSizerAndFit (sizer)
    self.SetupScrolling( )
    
  def __build_list (self, message=None):
    """
    Constructs the list, that displays the existing schedules.
      @param message: used by the observer pattern
    """
    self.list.DeleteAllItems ( )
    self.list.DeleteAllColumns ( )
    
    self.list.InsertColumn (0, "Mesec",         wx.LIST_FORMAT_CENTER)
    self.list.InsertColumn (1, "Leto",          wx.LIST_FORMAT_LEFT)
    self.list.InsertColumn (2, "Spremenejeno",  wx.LIST_FORMAT_LEFT)
    
    # also filter
    for vals in proxy.get_saved_schedules ( ):
      if self.search_values:
        for search in self.search_values:
          for val in vals:
            if val.lower ( ).startswith (search.lower ( )):
              self.list.Append (vals)
              break
          else:
            if vals[1].lower ( ).endswith (search.lower ( )):
              self.list.Append (vals)
      else:
        self.list.Append (vals)

    self.list.SetColumnWidth (0, 80)
    self.list.SetColumnWidth (1, 40)
    self.list.SetColumnWidth (2, wx.LIST_AUTOSIZE)
    self.list.SetMinSize ((133,50))
    
    self.__select_schedule (None)
    self.toolbar.toggle_schedule_specific (self.list.GetFirstSelected ( ) != -1)
    
    #if there is only one item, select it
    if self.list.GetItemCount ( ) == 1:
      self.list.Select (0)
    
    # workaround a bug that does not expand the last column
    self.Freeze ( )
    temp_size = self.GetSizeTuple ( )
    self.SetSize ((temp_size[0] + 1 , temp_size[1]))
    self.SetSize (temp_size)
    self.Thaw ( )
  
  
  def __show (self, type):
    """
    Creates and displays a schedule.
      @param type: the type of the schedule creation @see: scheduler.proxy.create_proxy
    """
    
    f = main_window.MainWindow  (proxy.create_proxy (self.toolbar.get_date ( ), type) , self)
    f.Show ( )
    
  def __blank (self, event):
    """
    Creates and displays a new blank schedule.
    """
    self.__show (proxy.CREATE_BLANK)
    
  def __create (self, event):
    """
    Creates and displays a new blank schedule, but loads the neighbouring months.
    """
    self.__show (proxy.CREATE_NEW)
    
  def __open (self, event):
    """
    Opens and displays an existing schedule. Exact replika of the saved one.
    """
    self.__show (proxy.LOAD_EXACT)
    
  def __merge (self, event):
    """
    Open and displays an existing schedule. The non-date data is taken from the current data state.
    """
    self.__show (proxy.LOAD_MERGE)
    
  def __remove (self, event):
    """
    Removes the selected schedule.
    """
    import wx.lib.agw.genericmessagedialog as GMD
    dlg = GMD.GenericMessageDialog (self, 'Želite trajno izbrisati razpored?', 'Opozorilo', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
    if dlg.ShowModal ( ) == wx.ID_YES:
      schedule_utils.remove_schedule (self.toolbar.get_date ( ))
    dlg.Destroy ( )
    
    self.__build_list ( )
    
  def __search (self, event):
    """
    Event listener for the toolbar search field.
    """
    self.search_values = self.toolbar.get_search_values ( )
    self.__build_list ( )
    
  def __schedule_selected (self, event):
    """
    Event listener for selecting an list item.
    """
    if self.list.GetFirstSelected ( ) != -1:
      month_index = calendar_utils.get_month_index (self.list.GetItem (self.list.GetFirstSelected ( ), 0).GetText ( ))
      year        =  self.list.GetItem (self.list.GetFirstSelected ( ), 1).GetText ( )
      self.toolbar.set_date (month_index, year)
      self.toolbar.toggle_schedule_specific (True)
      
  def __select_schedule (self, event):
    """
    Event listener, if the schedule was selected from the toolbar.
    """
    date = self.toolbar.get_date ( )
    item = [calendar_utils.get_month_name (date.month), str (date.year)]
    
    for i in range (0, self.list.GetItemCount ( )):
      self.list.Select (i, False)
      
      if \
      item[0] == self.list.GetItem (i, 0).GetText ( ) and \
      item[1] == self.list.GetItem (i, 1).GetText ( ):
        self.list.Select (i)
        self.toolbar.toggle_schedule_specific (True)
        break
    
"""
This is a toolbar, that is displayed on the top of every Page.
"""
class SchedulersPageToolbar (wx.ToolBar):
  
  BLANK  = wx.NewId ( )
  CREATE = wx.NewId ( )
  OPEN   = wx.NewId ( )
  MERGE  = wx.NewId ( )
  REMOVE = wx.NewId ( )
  
  def __init__ (self, *args, **kwargs):
    """
    The default constructor.
    """
    wx.ToolBar.__init__(self, *args, **kwargs)
    
    self.year_month_choice = MonthYearWrapper (self)
    
    self.AddLabelTool(SchedulersPageToolbar.CREATE, 'Nov razpored', wx.ArtProvider.GetBitmap(wx.ART_NEW,          wx.ART_TOOLBAR),       shortHelp='Ustvari prazen razpored, z obsoječima mejnima mesecema')
    self.AddLabelTool(SchedulersPageToolbar.BLANK,  'Nov razpored', wx.ArtProvider.GetBitmap(wx.ART_ADD_BOOKMARK, wx.ART_TOOLBAR),       shortHelp='Ustvari prazen razpored, tudi mejna meseca sta prazna')
    self.AddControl(self.year_month_choice.get_month_control ( ))
    self.AddControl(self.year_month_choice.get_year_control ( ))
    self.AddSeparator ( )
    
    self.AddLabelTool(SchedulersPageToolbar.OPEN,   'Odpri',        wx.ArtProvider.GetBitmap(wx.ART_FOLDER_OPEN,  wx.ART_TOOLBAR), shortHelp='Odpri izbran razpored, v natančno taki obliki, kot je bil shranjen.')
    self.AddLabelTool(SchedulersPageToolbar.MERGE,  'Združi',       wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN,    wx.ART_TOOLBAR), shortHelp='Odpri izbran razpored s takimi podatki, kot so trenutno v aplikaciji')
    self.AddLabelTool(SchedulersPageToolbar.REMOVE, 'Izbriši',      wx.ArtProvider.GetBitmap(wx.ART_DELETE,       wx.ART_TOOLBAR), shortHelp='Izbriši izbrano')
    self.AddSeparator ( )
    
    self.search = wx.SearchCtrl (self, wx.ID_FIND, style=wx.TB_HORIZONTAL | wx.TB_NODIVIDER)
    self.search.SetDescriptiveText ('Iskanje')
    self.search.ShowSearchButton (True)
    self.search.ShowCancelButton (True)
    
    self.AddControl(self.search)
    
    
    self.Bind (custom_events.EVT_UPDATED,   self.__date_selected, self.year_month_choice.get_month_control ( ))
    self.Bind (custom_events.EVT_UPDATED,   self.__date_selected, self.year_month_choice.get_year_control ( ))
    self.Bind (wx.EVT_TOOL,                 self.__blank,         id = SchedulersPageToolbar.BLANK)
    self.Bind (wx.EVT_TOOL,                 self.__create,        id = SchedulersPageToolbar.CREATE)
    self.Bind (wx.EVT_TOOL,                 self.__open,          id = SchedulersPageToolbar.OPEN)
    self.Bind (wx.EVT_TOOL,                 self.__merge,         id = SchedulersPageToolbar.MERGE)
    self.Bind (wx.EVT_TOOL,                 self.__remove,        id = SchedulersPageToolbar.REMOVE)
    
    self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.__clear_search, self.search)
    self.Bind(wx.EVT_TEXT, self.__search)
    
    # this hack enables clearing the search field with the escape key
    if wx.Platform in ['__WXGTK__', '__WXMSW__']:
      for child in self.search.GetChildren():
        if isinstance(child, wx.TextCtrl):
          child.Bind(wx.EVT_KEY_UP, self.__key_pressed)
          break
    
    self.EnableTool (SchedulersPageToolbar.OPEN, False)
    self.EnableTool (SchedulersPageToolbar.REMOVE, False)
    self.Realize ( )
    
  def toggle_schedule_specific (self, enable):
    """
    Enables / disables the open and delete schedule buttons.
      @param enable: a boolean
    """
    self.EnableTool (SchedulersPageToolbar.OPEN,   enable)
    self.EnableTool (SchedulersPageToolbar.MERGE,  enable)
    self.EnableTool (SchedulersPageToolbar.REMOVE, enable)
    
  def set_date (self, month=None, year=None):
    """
    Sets the displayed month and year.
      @param month: the month's index (integer), default is set None
      @param year: the year (integer), default is set to None
    """
    if month:
      self.year_month_choice.set_month (month)
    if year:
      self.year_month_choice.set_year (year)
  
  def get_date (self):
    """
    Returns the selected date.
      @return: a datetime.date object 
    """
    return self.year_month_choice.get_selected_date ( )
  
  def get_search_values (self):
    """
    Return a list of search strings.
      return: a list of strings
    """
    return self.search.GetValue ( ).split( )
  
  def __blank (self, event):
    """
    Event listener for the create blank schedule button.
    """
    wx.PostEvent (self.GetEventHandler ( ), custom_events.BlankEvent (self.GetId ( )))
    
  def __create (self, event):
    """
    Event listener for the create schedule button.
    """
    wx.PostEvent (self, custom_events.CreateEvent (self.GetId ( ), date=self.year_month_choice.get_selected_date ( )))
    
  def __open (self, event):
    """
    Event listener for the open schedule button.
    """
    wx.PostEvent (self.GetEventHandler ( ), custom_events.OpenEvent (self.GetId ( )))
    
  def __merge (self, event):
    """
    Event listener for the merge schedule button.
    """
    wx.PostEvent (self.GetEventHandler ( ), custom_events.MergeEvent (self.GetId ( )))
    
  def __remove (self, event):
    """
    Event listener for the remove schedule button.
    """
    wx.PostEvent (self.GetEventHandler ( ), custom_events.RemoveEvent (self.GetId ( )))
    
  def __date_selected (self, event):
    """
    Event listener for the year and month choice.
    """
    self.toggle_schedule_specific (False)
    wx.PostEvent (self.GetEventHandler ( ), custom_events.UpdateEvent (self.GetId ( )))
    
  def __search(self, event):
    """
    Fires the search event.
    """
    wx.PostEvent (self.GetEventHandler(), custom_events.SearchEvent(self.GetId()))
    
  def __clear_search (self, event):
    """
    Clears the search field and fires the search event.
    """
    self.search.Clear ( )
    
  def __key_pressed (self, event):
    """
    Listens for the escape key and clears the search key, if pressed.
    """
    if event.GetKeyCode ( ) == wx.WXK_ESCAPE:
      self.__clear_search (None)

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
    
    self.__months.Bind (wx.EVT_CHOICE, self.__date_selected)
    self.__years.Bind  (wx.EVT_CHOICE, self.__date_selected)
    
  def set_month (self, month):
    """
    Sets the month.
      @param month: a 1 based month index
    """
    self.__months.Select (month)
    
  def set_year (self, year):
    """
    Sets the year.
      @param year: an integer
    """
    if str (year) not in self.__years.GetItems ( ):
      items = self.__years.GetItems ( )
      for _ in items:
        self.__years.Delete (0)
        
      items.append (str (year))
      items.sort ( )
      self.__years.AppendItems (items)  
      
    self.__years.Select (self.__years.GetItems ( ).index(str (year)))
    
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
  
  def __date_selected (self, event):
    """
    Event listener for the year and month choices.
    """
    wx.PostEvent (self.__months.GetEventHandler ( ), custom_events.UpdateEvent (self.__months.GetId ( )))
    