# -*- coding: Cp1250 -*-

import wx
import wx.lib.intctrl
import wx.lib.newevent
import wx.lib.agw.foldpanelbar as fpb

import schedule_grid
from scheduler import proxy
from data      import turnus, vacation
from utils     import time_conversion, exporter
from gui       import wx_extensions, custom_events, custom_widgets, observer_pattern

import os
import copy
from threading import Thread



# This creates a new Event class and a EVT binder function
(ScheduleMessageEvent, EVT_SCHEDULE_MESSAGE) = wx.lib.newevent.NewEvent()

"""
This class represents the final view of the scheduled nurses.
"""
class Result (wx.Panel):
  def __init__(self, proxy, *args, **kwargs):
    """
    The default constructor.
      @param proxy: the intermediate class between the data model and the scheduler's model.
    """
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.proxy          = copy.deepcopy (proxy)
    self.scheduler      = None
    self.compact        = None
    self.full_span      = None
    
    self.progress_panel = ProgressPanel               (            self, wx.ID_ANY, name='Status razvrščanja ...')
    self.grid           = schedule_grid.ScheduleGrid  (            self, wx.ID_ANY)
    self.manual_edit    = ManualEditPanel             (self.proxy, self, wx.ID_ANY, agwStyle = fpb.FPB_EXCLUSIVE_FOLD | fpb.FPB_SINGLE_FOLD)
    self.warnings       = WarningsPanel               (            self, wx.ID_ANY)
    
    self.Bind (EVT_SCHEDULE_MESSAGE,               self.__message_recieved)
    self.Bind (custom_events.EVT_COMPLEX_SELECTED, self.__selected, self.grid)
    self.Bind (custom_events.EVT_UPDATED,          self.__edited,   self.manual_edit)
    self.Bind (custom_events.EVT_TB_SEARCH,        self.__search,   self.manual_edit)
    
    result_sizer = wx.BoxSizer(wx.HORIZONTAL)
    result_sizer.Add (self.manual_edit, 1, wx.ALIGN_LEFT | wx.EXPAND)
    result_sizer.Add (self.grid,        5, wx.ALIGN_LEFT | wx.EXPAND | wx.LEFT, 4)
    result_sizer.Add (self.warnings,    1, wx.ALIGN_LEFT | wx.EXPAND)
    
    main_sizer = wx.BoxSizer (wx.VERTICAL)
    main_sizer.Add (self.progress_panel, 0, wx.ALIGN_LEFT | wx.EXPAND)
    main_sizer.Add (result_sizer,        1, wx.ALIGN_LEFT | wx.EXPAND)
    
    self.SetSizerAndFit(main_sizer)
    
    self.progress_panel.Hide ( )
    self.grid.set_unit (self.proxy.get_people_container ( ))
    self.grid.select ([], [])
    
    self.compact   = self.grid.is_compact ( )
    self.full_span = self.grid.is_full_span ( )
    
  def start (self):
    self.Freeze ( )
    
    self.grid.Hide ( )
    self.warnings.Hide ( )
    self.manual_edit.Hide ( )
    self.progress_panel.Show ( )
    
    self.scheduler = Scheduler(self, self.proxy)
    
    self.Layout ( )
    self.Thaw ( )
    
    self.scheduler.start ( )
    
  def get_proxy (self):
    """
    Returns this result's proxy object.
      @return: a proxy object
    """
    return self.proxy
    
    
  def toggle_view (self, compact):
    """
    Sets the type of the view, that will be displayed.
      @param compact: a boolean that defines the view. Compact view if True, full view if False.
    """
    self.grid.toggle_view (compact)
    self.compact = self.grid.is_compact ( )
    self.Layout ( )
    self.grid.select (self.manual_edit.get_people ( ), self.manual_edit.get_dates ( ))
    
  def is_compact (self):
    """
    Checks, if this container is set to the compact view mode.
      @return: True, if it compact, False otherwise.
    """
    return self.grid.is_compact ( )
  
  def set_span (self, full):
    """
    Sets the date range of the view. Span can be set to full (the neighbouring months) or normal (only the
    main scheduling month).
      @param full: a boolean that sets the span. True if full span, False otherwise. 
    """
    self.grid.set_span (full)
    self.full_span = self.grid.is_full_span ( )
    self.Layout ( )
    self.grid.select (self.manual_edit.get_people ( ), self.manual_edit.get_dates ( ))
    
  def is_full_span (self):
    """
    Checks, if this container is set to the full span view mode.
      @return: True, if it is full, False otherwise.
    """
    return self.grid.is_full_span ( )
  
  def save(self):
    """Saves the schedule"""
    dlg = wx.FileDialog(self, message="Shrani datoteko ...", defaultDir=os.path.expanduser("~"), defaultFile="razpored.csv", wildcard="CSV datoteka (*.csv)|*.csv", style=wx.SAVE | wx.FD_OVERWRITE_PROMPT)
    if dlg.ShowModal() == wx.ID_OK:
      path = dlg.GetPath()
      #force the csv appendix
      if path.split(r'.')[-1] != 'csv':
        path += '.csv'
      
      # save the internal schedule
      if not proxy.save (self.proxy, overwrite = False):
        action = wx.MessageBox(parent=self, message='Za ta mesec ze obstaja shranjen razpored, ki se bo uporabil pri razvrcanju naslednjega meseca. Ali ga zelite prepisati?', style=wx.YES_NO | wx.ICON_EXCLAMATION)
        if action == wx.YES:
          proxy.save (self.proxy, overwrite = True)
        else:
          return
        
      # save the final *.csv file
      exporter.exportCSV (self.proxy.get_exportable ( ), path)
      observer_pattern.send_notification (observer_pattern.SCHEDULER_SAVED)
    dlg.Destroy ( )
  
    
  def __message_recieved(self, event):
    """
    The event listener for thread synchronization.
    """
    if event.running:
      self.progress_panel.update (event.message)
    else:
      if event.error:
        dlg = wx.MessageDialog (self, event.message, 'Napaka', wx.OK | wx.ICON_INFORMATION)
        dlg.CenterOnScreen ( )
        dlg.ShowModal ( )
        dlg.Close ( )
        self.Destroy ( )
      else:
        self.__reconstruct ( )
        
  def __selected (self, event):
    """
    The event listener for the grid selection.
    """
    self.manual_edit.set_unit ((event.people, event.dates))
    
  def __edited (self, event):
    """
    The event listener for manual editing.
    """
    self.Freeze ( )
    
    self.grid.refresh ( )
    self.Layout ( )
    self.grid.select (self.manual_edit.get_people ( ), self.manual_edit.get_dates ( ))
    
    self.warnings.display_warnings(self.scheduler.get_warnings())
    
    self.Thaw ( )
        
  def __reconstruct(self):
    self.Freeze ( )
    
    self.proxy.set_people (self.scheduler.get_result ( ))
    
    self.grid.set_unit (self.proxy.get_people_container ( ))
    self.warnings.display_warnings (self.scheduler.get_warnings ( ))
    self.manual_edit.set_unit(([], []))
    
    self.grid.Show ( )
    self.grid.toggle_view (self.compact)
    self.grid.set_span (self.full_span)
    self.grid.select ([], [])
    
    self.warnings.Show ( )
    self.manual_edit.Show ( )
    self.__edited (None)
    
    self.progress_panel.Hide ( )
    
    self.Layout ( )
    self.Refresh ( )
    self.Thaw ( )
    
  def __search(self, event):
    """
    Searches the global container for the matching entries.
    """
    self.grid.search (self.manual_edit.get_text_search_values ( ), 
                      self.manual_edit.get_scheduling_unit_search_values ( ))
    self.Layout ( )

"""
This class is the panel, that allows manula editing of an existing schedule.
"""
class ManualEditPanel (fpb.FoldPanelBar):
  
  def __init__ (self, proxy, *args, **kwargs):
    """
    The default constructor.
      @param proxy: a proxy object
    """
    fpb.FoldPanelBar.__init__ (self, *args, **kwargs)
    
    self.proxy        = proxy
    self.people       = None
    self.dates        = None
    self.selected_schedule_unit = None
    
    scheduleable_item = self.AddFoldPanel("Turnusi in dopusti", collapsed=True)
    unpaid_item       = self.AddFoldPanel("Neplačane ure",      collapsed=True)
    restrictions_item = self.AddFoldPanel("Filtri",             collapsed=True)
    
    self.schedule_unit_selector = custom_widgets.ScheduleUnitSelector (self.proxy.get_scheduling_units_container ( ), scheduleable_item, wx.ID_ANY)
    self.AddFoldPanelWindow (scheduleable_item, self.schedule_unit_selector, fpb.FPB_ALIGN_WIDTH)
    
    
    
    self.turnus_checkers    = []
    self.vacations_checkers = []
    
    self.turnus_checkers.append (wx_extensions.LinkedCheckBox (None, scheduleable_item, wx.ID_ANY, 'Brez', style=wx.CHK_3STATE))
    self.AddFoldPanelWindow (scheduleable_item, self.turnus_checkers[-1], fpb.FPB_ALIGN_LEFT)
    for turnus in proxy.get_turnuses ( ):
      self.turnus_checkers.append (wx_extensions.LinkedCheckBox (turnus, scheduleable_item, wx.ID_ANY, str (turnus), style=wx.CHK_3STATE))
      self.AddFoldPanelWindow (scheduleable_item, self.turnus_checkers[-1], fpb.FPB_ALIGN_LEFT)
    
    self.AddFoldPanelSeparator (scheduleable_item)
     
    import global_vars
    self.vacations_checkers.append (wx_extensions.LinkedCheckBox (None, scheduleable_item, wx.ID_ANY, 'Brez', style=wx.CHK_3STATE))
    self.AddFoldPanelWindow (scheduleable_item, self.vacations_checkers[-1], fpb.FPB_ALIGN_LEFT)
    for vacation in global_vars.get_vacations ( ).get_all ( ):
      self.vacations_checkers.append (wx_extensions.LinkedCheckBox (vacation, scheduleable_item, wx.ID_ANY, str (vacation), style=wx.CHK_3STATE))
      self.AddFoldPanelWindow (scheduleable_item, self.vacations_checkers[-1], fpb.FPB_ALIGN_LEFT)
      
    self.unpaid_hours = wx.lib.intctrl.IntCtrl (unpaid_item, wx.ID_ANY)
    self.AddFoldPanelWindow (unpaid_item, self.unpaid_hours, fpb.FPB_ALIGN_LEFT)
    
    
    self.name_search = wx.SearchCtrl (restrictions_item, wx.ID_ANY, size=(200,-1))
    self.AddFoldPanelWindow (restrictions_item, self.name_search, fpb.FPB_ALIGN_LEFT)
    
    self.schedule_unit_search = custom_widgets.ScheduleUnitSelector (self.proxy.get_scheduling_units_container ( ), restrictions_item, wx.ID_ANY)
    self.AddFoldPanelWindow (restrictions_item, self.schedule_unit_search, fpb.FPB_ALIGN_LEFT)
    
    self.clear_search = wx.Button (restrictions_item, wx.ID_ANY, 'Prikaži vse')
    self.AddFoldPanelWindow (restrictions_item, self.clear_search, fpb.FPB_ALIGN_WIDTH)
    
    
    self.Bind (custom_events.EVT_UPDATED, self.__schedule_unit_selected, self.schedule_unit_selector)
    self.Bind (wx.lib.intctrl.EVT_INT,    self.__unpaid_hours_changed,   self.unpaid_hours)
    
    for turnus_checker in self.turnus_checkers:
      self.Bind (wx.EVT_CHECKBOX, self.__turnus_checker_clicked, turnus_checker)
    for vacation_checker in self.vacations_checkers:
      self.Bind(wx.EVT_CHECKBOX, self.__vacation_checker_clicked, vacation_checker)
      
    self.Bind (wx.EVT_SEARCHCTRL_CANCEL_BTN, self.__clear_search,      self.name_search)
    self.Bind (wx.EVT_TEXT,                  self.__search)
    self.Bind (custom_events.EVT_UPDATED,    self.__search,            self.schedule_unit_search)
    self.Bind (wx.EVT_BUTTON,                self.__clear_all_filters, self.clear_search)
    
    # this hack enables clearing the search field with the escape key
    if wx.Platform in ['__WXGTK__', '__WXMSW__']:
      for child in self.name_search.GetChildren():
        if isinstance(child, wx.TextCtrl):
          child.Bind(wx.EVT_KEY_UP, self.__key_pressed)
          break
    
    
    self.unpaid_hours.SetNoneAllowed (True)
    
    self.name_search.SetDescriptiveText ('Iskanje po imenu in priimku')
    self.name_search.ShowSearchButton (True)
    self.name_search.ShowCancelButton (True)
    
    self.__set_permissions ( )
    self.Expand (scheduleable_item)
    
  def set_unit (self, data):
    """
    Set's the panels data.
      @param data: a 2-tuple:
                    at the first index is a list of all people (data objects)
                    at the second index is a list of all dates (datetime.date objects)
    """
    self.people = data[0]
    self.dates  = data[1]
    
    self.__set_permissions ( )
    
  def get_people (self):
    """
    Returns the stored people.
      @return: a list of data objects
    """
    return self.people
    
  def get_dates (self):
    """
    Returns the stored dates.
      @return: a list of datetime.date objects
    """
    return self.dates
  
  def get_text_search_values (self):
    """
    Return a list of search strings.
      return: a list of strings
    """
    return self.name_search.GetValue ( ).split( )
  
  def get_scheduling_unit_search_values (self):
    """
    Return a list of searched scheduling units.
      @return: a list of data objects
    """
    if self.schedule_unit_search.get_selection ( ):
      return [self.schedule_unit_search.get_selection ( )]
    else:
      return []
    
  def __schedule_unit_selected (self, event):
    """
    Event listener for the schedule unit selector.
    """
    self.selected_schedule_unit = self.schedule_unit_selector.get_selection ( )
    self.__set_permissions ( )
    
  def __turnus_checker_clicked (self, event):
    """
    Event listener for the turnus checkboxes.
    """
    for person in self.people:
      for date in self.dates:
        if event.IsChecked ( ) and event.GetEventObject ( ).element:
          person.clear_date (date)
          person.schedule_turnus (date, event.GetEventObject ( ).element, self.selected_schedule_unit)
        elif event.IsChecked ( ) and not event.GetEventObject ( ).element:
          person.clear_date (date)
        elif person.get_scheduled_raw (date)[0] == event.GetEventObject ( ).element:
          person.clear_date (date)
    
    self.__set_permissions ( )
    wx.PostEvent (self.GetEventHandler ( ), custom_events.UpdateEvent (self.GetId ( )))
  
  def __vacation_checker_clicked (self, event):
    """
    Event listener for the vacation checkboxes.
    """
    for person in self.people:
      for date in self.dates:
        if event.IsChecked ( ) and event.GetEventObject ( ).element:
          person.clear_date (date)
          person.schedule_turnus (date, event.GetEventObject ( ).element, '')
        elif event.IsChecked ( ) and not event.GetEventObject ( ).element:
          person.clear_date (date)
        elif person.get_scheduled_raw (date)[0] == event.GetEventObject ( ).element:
          person.clear_date (date)
    
    self.__set_permissions ( )
    wx.PostEvent (self.GetEventHandler ( ), custom_events.UpdateEvent (self.GetId ( )))
    
  def __unpaid_hours_changed (self, event):
    """
    Event listener for the unpaid hours field.
    """
    if self.people:      
      for person in self.people:
        if self.unpaid_hours.GetValue ( ) != None:
          person.set_unpaid_hours (self.unpaid_hours.GetValue ( ))
        else:
          person.set_unpaid_hours (0)
      self.__set_permissions ( )
      wx.PostEvent (self.GetEventHandler ( ), custom_events.UpdateEvent (self.GetId ( )))
      
  def __search (self, event):
    """
    Fires the search event.
    """
    wx.PostEvent (self.GetEventHandler ( ), custom_events.SearchEvent (self.GetId ( )))
    
  def __key_pressed (self, event):
    """
    Listens for the escape key and clears the search key, if pressed.
    """
    if event.GetKeyCode ( ) == wx.WXK_ESCAPE:
      self.__clear_search (None)
    
  def __clear_search (self, event):
    """
    Clears the search field and fires the search event.
    """
    self.name_search.Clear ( )
    
  def __clear_all_filters (self, event):
    """
    Wipes the search criteria clean.
    """
    self.schedule_unit_search.set_selection(None)
    self.__clear_search (event)
    
  def __set_permissions (self):
    """
    Keeps the GUI in sync with the data.
    """
    
    self.Unbind (wx.lib.intctrl.EVT_INT, self.unpaid_hours)
    
    if self.people:
      self.unpaid_hours.Enable ( )
      values = set ( )
      for person in self.people:
        values.add (person.get_unpaid_hours ( ))
      if len (values) == 1:
        self.unpaid_hours.SetValue (values.pop ( ))
      else:
        self.unpaid_hours.SetValue (None)
    else:
      self.unpaid_hours.SetValue (None)
      self.unpaid_hours.Disable ( )
    
    if self.people and self.dates:
      #schedule_units = self.__get_schedule_units ( )
      turnuses       = self.__get_turnuses ( )
      vacations      = self.__get_vacations ( )
      mix            = self.__get_turnuses_or_vacations ( )
      
      self.schedule_unit_selector.Enable ( )
      self.selected_schedule_unit = self.schedule_unit_selector.get_selection ( )
      
      for turnus_checker in self.turnus_checkers:
        if self.selected_schedule_unit:
          turnus_checker.Enable ( )
        else:
          turnus_checker.Disable ( )
        if turnus_checker.element in turnuses and len (mix) == 1:
          turnus_checker.SetValue (True)
        elif turnus_checker.element in turnuses:
          turnus_checker.Set3StateValue (wx.CHK_UNDETERMINED)
        else:
          turnus_checker.SetValue (False)
        
      for vacation_checker in self.vacations_checkers:
        vacation_checker.Enable ( )
        if vacation_checker.element in vacations and len (mix) == 1:
          vacation_checker.SetValue (True)
        elif vacation_checker.element in vacations:
          vacation_checker.Set3StateValue (wx.CHK_UNDETERMINED)
        else:
          vacation_checker.SetValue (False)
    else:
      self.schedule_unit_selector.Disable ( )
      for turnus_checker in self.turnus_checkers:
        turnus_checker.SetValue (False)
        turnus_checker.Disable ( )
      for vacation_checker in self.vacations_checkers:
        vacation_checker.SetValue (False)
        vacation_checker.Disable ( )
        
    self.Bind (wx.lib.intctrl.EVT_INT, self.__unpaid_hours_changed, self.unpaid_hours)

  def __get_schedule_units (self):
    """
    Returns all schedule units.
      @return: a set of data objects
    """
    elements = set ( )
    for person in self.people:
      for date in self.dates:
        elements.add (person.get_scheduled_raw (date)[1])
    return elements

  def __get_turnuses (self):
    """
    Returns all turnuses.
      @return: a set of data objects
    """
    turnuses = set ( )
    for object in self.__get_turnuses_or_vacations ( ):
      if isinstance (object, turnus.Turnus) or object == None:
        turnuses.add (object)
    return turnuses
  
  def __get_vacations (self):
    """
    Returns all vacations.
      @return: a set of data objects
    """
    vacations = set ( )
    for object in self.__get_turnuses_or_vacations ( ):
      if isinstance (object, vacation.Vacation) or object == None:
        vacations.add (object)
    return vacations
        
  def __get_turnuses_or_vacations (self):
    """
    Returns all the turnuses and vacations.
      @return: a set of data objects
    """
    elements = set ( )
    for person in self.people:
      for date in self.dates:
        elements.add (person.get_scheduled_raw (date)[0])
    return elements

class WarningsPanel(wx.Panel):
  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), "Opozorila"), wx.VERTICAL)
    self.tree = TreeWarnings(self, wx.NewId(), style=wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT)
    sizer.Add(self.tree, 1, wx.ALIGN_LEFT | wx.EXPAND)
    
    self.SetSizerAndFit(sizer)
    
  def display_warnings (self, warnings):
    self.tree.display_warnings(warnings)
        
class TreeWarnings(wx.TreeCtrl):
  def __init__(self, *args, **kwargs):
    wx.TreeCtrl.__init__(self, *args, **kwargs)
    
    
    
            
  def display_warnings (self, warnings):
    self.DeleteAllItems ( )
    root = self.AddRoot("Koren")
    for workplace in sorted(warnings.keys()):
      w_item = self.AppendItem(root, str(workplace))
      for turnus in sorted(warnings[workplace].keys()):
        t_item = self.AppendItem(w_item, str(turnus))
        for date in sorted(warnings[workplace][turnus].keys()):
          self.AppendItem(t_item, time_conversion.date_to_string(date) + ': ' + warnings[workplace][turnus][date])

    
"""
This is a custom class that behaves very similar to the wx.ProgressDialog.
"""    
class ProgressPanel(wx.Panel):
  
  """
  This variable contains the pulse interval in milliseconds.
  """
  TIMER_SPEED = 500
  
  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.timer   = wx.Timer (self)
    self.message = ''
    
    self.text  = wx.StaticText (self, wx.ID_ANY, label='')
    self.gauge = wx.Gauge      (self, wx.ID_ANY, size=(-1,10), style=wx.GA_HORIZONTAL | wx.GA_SMOOTH)
    
    self.Bind(wx.EVT_TIMER, self.__smooth)
    
    if self.GetLabel ( ) == '' or self.GetLabel ( ) == 'panel':
      sizer = wx.BoxSizer(wx.VERTICAL)
    else:
      sizer = wx.StaticBoxSizer (wx.StaticBox (self, wx.ID_ANY, self.GetLabel ( )), wx.VERTICAL)
    sizer.Add( self.text,  0, wx.ALIGN_TOP |wx.ALIGN_LEFT | wx.EXPAND)
    sizer.Add (self.gauge, 0, wx.ALIGN_TOP |wx.ALIGN_LEFT | wx.EXPAND)
    
    self.SetSizerAndFit(sizer)
    
  def Show (self, bool=True):
    """
    Overrides the main method.
    """
    if bool and not self.timer.IsRunning ( ):
      self.timer.Start (ProgressPanel.TIMER_SPEED)
    if not bool:
      self.timer.Stop ( )
    return super (ProgressPanel, self).Show (bool)
    
  def Hide (self):
    """
    Overrides the main method.
    """
    return self.Show (False)
    
  def __smooth(self, event):
    """
    Event listener for the timer. Keeps the progress bar smooth.
    """
    self.update (self.text.GetLabel ( ))
    self.gauge.Pulse ( )
    
  def update(self, message):
    self.text.SetLabel (message)
    
    
  def __del__ (self):
    self.timer.Stop ( )

"""
This class is the scheduling thread.
"""
class Scheduler(Thread):
  
  """
  This class contains the current status of the whole thread.
  """
  class RunningStatus:
    
    def __init__ (self, active, error, status):
      """
      The default constructor.
        @param running: a boolean, that specifies is the scheduling process is still running. True if it is,
          false otherwise.
        @param error: a boolean, that tells if an error occurred during the scheduling process. True if it has,
          false otherwise.
        @param message: a string, that contains the status of the thread.
      """
      self.__active  = active
      self.__error   = error
      self.__status  = status
      
    def is_active (self):
      """
      Checks if the thread is still performing the scheduling process.
        @return: true if it is, false otherwise 
      """
      return self.__active
    
    def is_error (self):
      """
      Checks if an error occurred during the scheduling process.
        @return: true if it is, false otherwise
      """
      return self.__error
    
    def get_status (self):
      """
      Return the current status.
        @return: a string
      """
      return self.__status
      
  
  def __init__(self, parent, proxy, *args, **kwargs):
    """
    The default constructor.
      parent: an instance of the wx.Window
      @param args: look the __schedule method
    """
    
    #TODO: remove this
    self.wx_parent = parent
    
    Thread.__init__(self, target=self.__schedule, args=args)
    self.__running = False
    self.__status  = None
    self.proxy     = proxy
    self.scheduler = None
    
  def send_message(self, message=None, running=True, error=False):
    """
    Creates and sends the scheduling message to the GUI.
      message: is a string message
      running: if true, the scheduler is still running, else it has stopped
      error: if true, an error has occurred during the scheduling, if should
             never be true at the same time as the running parameter
    """
    if running and error:
      error = False
      
    if message:
      self.message = message
    else:
      message = self.message
    
    evt = ScheduleMessageEvent(message=message, running=running, error=error)
    wx.PostEvent(self.wx_parent, evt)
    
  def get_result(self):
    """A wrapper around the Person_scheduler.get_result method."""
    if self.scheduler:
      return self.scheduler.get_result ( )
    else:
      None
    
  def get_warnings(self):
    """A wrapper around the Personget_workplace_warnings function."""
    if self.scheduler:
      return self.scheduler.get_workplace_warnings ( )
    else:
      raise Exception('Razpored ne obstaja')
    
    
  def __schedule(self):
    """
    This method creates the scheduler and start's scheduling.
      @param proxy: the intermediate class between the data model and the scheduling model.
    """
    
    self.running = True
    
    self.scheduler = self.__initialize_scheduler (self.proxy)
    self.scheduler.schedule ( )
    
    self.proxy.set_people (self.scheduler.get_result ( ))
          
    self.send_message ('Razvrscevanje koncano.', running=False, error=False)
    self.running = False
    
    
    
  def __initialize_scheduler(self, proxy):
    """
    This method initializes the scheduler.
      @param proxy: the intermediate class between the data and the scheduler's model
      @return: a Scheduler object
    """
    
    self.send_message('Predpriprave ...')
            
    ps = proxy.get_scheduler ( )
    ps.set_log (self)
    return ps

        
