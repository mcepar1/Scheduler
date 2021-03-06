# -*- coding: Cp1250 -*-

import copy

import wx
import wx.calendar

from gui import custom_events, custom_widgets, wx_extensions

from scheduler.workers import Workers

"""
The main panel for editing the scheduling data.
"""
class WorkersPanel (wx.Panel):
  def __init__(self, proxy, *args, **kwargs):
    """
    The default constructor.
      @param proxy: the class that maps the data model into the schedule model.
    """
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.proxy               = None
    
    self.workplace_role_pair = None
    self.shift_control       = None
    
    self.rebuild (proxy)
    
  def rebuild (self, proxy):
    """
    Reconstructs the entire panel.
    """
    self.Freeze ( )
    self.proxy = proxy
    
    self.DestroyChildren ( )
    
    title                    = wx.StaticText (self, wx.ID_ANY, '�tevilo zaposlenih v turnusu')
    self.workplace_role_pair = custom_widgets.ScheduleUnitSelector (self.proxy.get_scheduling_units_container ( ), self, wx.ID_ANY)
    self.shift_control       = ShiftControl (self.proxy.get_turnus_types ( ), self.proxy.get_workers ( ), self, wx.ID_ANY)
    
    self.Bind(custom_events.EVT_UPDATED, self.__pair_selected, self.workplace_role_pair)
    
    sizer = wx.GridBagSizer ( )
    sizer.Add (title,                    (0,0), (1,3), wx.ALIGN_CENTER)
    sizer.Add (self.workplace_role_pair, (1,0), (1,1), wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    sizer.Add (self.shift_control,       (1,1), (1,2), wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
    
    self.SetSizerAndFit (sizer)
    
    self.Thaw ( )
    
    
    
  def __pair_selected (self, event):
    """
    Event listener for the workplace-role pair selector
    """
    self.shift_control.set_unit (self.workplace_role_pair.get_selection ( ))
    
  def get_workers (self):
    """
    Returns a copy of the proxy object.
      @return: a proxy object
    """    
    return copy.deepcopy (self.proxy)
 
"""
This class selects the handles the selection of number of nurses for the specific shift.
"""   
class ShiftControl (wx.Panel):
  
  def __init__(self, turnus_types, workers, *args, **kwargs):
    """
    The default constructor.
      turnus_types: a list of data objects
      workers: a workers container
      dates: a list of all valid dates in that will be set
    """
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.worker_container   = workers
    self.schedule_unit      = None
    
    
    
    self.work_days_selector = ShiftSelector     (turnus_types, 
                                                 self.worker_container,
                                                 Workers.get_workday_workers, 
                                                 Workers.add_worday_dates, 
                                                 self, wx.ID_ANY, name='Delovni dnevi')
    
    self.holidays_selector  = ShiftSelector     (turnus_types, 
                                                 self.worker_container, 
                                                 Workers.get_holiday_workers, 
                                                 Workers.add_holiday_dates,  
                                                 self, wx.ID_ANY, name='Prosti dnevi')
    
    self.date_specific      = DateShiftControl  (turnus_types, 
                                                 self.worker_container,  
                                                 self, wx.ID_ANY, name='Za posamezen dan')
    
    
    self.Bind (custom_events.EVT_UPDATED, self.__updated, self.work_days_selector)
    self.Bind (custom_events.EVT_UPDATED, self.__updated, self.holidays_selector)
    
    sizer = wx.GridBagSizer ( )
    sizer.Add (self.work_days_selector, (0,0), (1,1), wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    sizer.Add (self.holidays_selector,  (0,1), (1,1), wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    sizer.Add (self.date_specific,      (0,2), (1,1), wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
    self.SetSizerAndFit (sizer)
    
    
  def set_unit(self, schedule_unit):
    """
    Sets which workplace role pair is currently beeing edited by the application.
      @param schedule_unit: a data object
    """
    self.schedule_unit = schedule_unit
    
    self.work_days_selector.set_unit (self.schedule_unit)
    self.holidays_selector.set_unit  (self.schedule_unit)
    self.date_specific.set_unit      (self.schedule_unit)
    
  def __updated (self, event):
    """
    Event listener for the shift selectors.
    """
    self.set_unit (self.schedule_unit)
    
"""
This class handles the date specific shifts.
"""
class DateShiftControl(wx.Panel):
  
  def __init__ (self, turnus_types, workers_instance, *args, **kwargs):
    """
    The default constructor.
      turnus_types: list of data objects
      workers_instance: a workers object
    """
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.scheduling_unit = None
    
    self.workers         = workers_instance
    
    self.calendar       = wx_extensions.EnhancedCalendar (self, wx.ID_ANY, style=wx.calendar.CAL_MONDAY_FIRST | wx.calendar.CAL_SHOW_SURROUNDING_WEEKS | wx.calendar.CAL_SEQUENTIAL_MONTH_SELECTION)
    self.enable_shifts  = wx.CheckBox (self, wx.ID_ANY, 'Uredi datum')
    self.shift_selector = DateShiftSelector (turnus_types,  
                                             workers_instance,  
                                             Workers.get_manual_date_workers,  
                                             None,  
                                             self, wx.ID_ANY)
    
    
    # limit the calendar and set the first date
    self.calendar.PySetDateRange(*self.workers.get_range ( ))
    self.calendar.PySetDate (self.workers.get_range ( )[0])
    # shifts must start disabled
    self.shift_selector.Disable ( )
    
    self.Bind (wx.EVT_CHECKBOX, self.__edit_date, self.enable_shifts)
    self.Bind (wx.calendar.EVT_CALENDAR_SEL_CHANGED, self.__date_changed, self.calendar)
    self.Bind (custom_events.EVT_UPDATED, self.__edit_date, self.shift_selector)
    
    
    sizer     = wx.StaticBoxSizer (wx.StaticBox (self, wx.ID_ANY, self.GetLabel ( )), wx.HORIZONTAL)
    sub_sizer = wx.BoxSizer       (wx.VERTICAL)
    
    sub_sizer.Add (self.shift_selector, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    sub_sizer.Add (self.enable_shifts,  0, wx.CENTER | wx.ALL, 5)
    
    sizer.Add (sub_sizer,     0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    sizer.Add (self.calendar, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
    self.SetSizerAndFit (sizer)
    
    self.__set_permissions ( )
    
  def set_unit(self, scheduling_unit):
    """
    Sets which scheduling unit is currently being edited by the application.
      @param scheduling_unit: a data object
    """
    self.scheduling_unit = scheduling_unit
    
    self.__set_permissions ( )
    
    self.shift_selector.set_unit ((self.scheduling_unit, self.calendar.PyGetDate ( )))
    
    if self.enable_shifts.GetValue ( ):
      self.shift_selector.Enable ( )
    else:
      self.shift_selector.Disable ( )
    

    
  def __date_changed (self, event):
    """
    Event listener for the calendar.
    """
    self.__set_permissions ( )
    
    self.shift_selector.set_unit ((self.scheduling_unit, self.calendar.PyGetDate ( )))
    if self.enable_shifts.GetValue ( ):
      self.shift_selector.Enable ( )
    else:
      self.shift_selector.Disable ( )
    
  def __edit_date (self, event):
    """
    Event listener for the edit date checker.
    """
    if self.enable_shifts.GetValue ( ):
      self.workers.add_manual_date (self.calendar.PyGetDate ( ), self.scheduling_unit, self.shift_selector.get_values ( ))
      self.calendar.mark_special_date (self.calendar.PyGetDate ( ))
    else:
      self.workers.remove_manual_date (self.calendar.PyGetDate ( ), self.scheduling_unit)
      self.calendar.unmark_special_date (self.calendar.PyGetDate ( ))
    
    self.shift_selector.Enable (self.enable_shifts.GetValue ( ))
    self.__set_permissions ( )
    
  def __set_permissions (self):
    if self.scheduling_unit:
      self.calendar.Enable ( )
      self.enable_shifts.Enable ( )
      
      self.enable_shifts.SetValue (self.workers.is_date_manual (self.calendar.PyGetDate ( ), self.scheduling_unit))
      
    else:
      self.calendar.Disable ( )
      
      self.enable_shifts.SetValue (False)
      self.enable_shifts.Disable ( )
      

"""
This class handles the actual number of shifts.
"""    
class ShiftSelector(wx.Panel):
  
  def __init__(self, turnus_types, workers_instance, get_method ,add_method, *args, **kwargs):
    """
    The default constructor.
      turnus_types: list of data objects
      workers_instance: a workers object
      get_method: a method, that will be used for fetching data from the workers instance
      add_method: a method, that will be used for adding data into the workers instance 
    """
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.schedule_unit    = None
    
    self.workers_instance = workers_instance
    self.get_method       = get_method
    self.add_method       = add_method
    
    self.spin_controls = []
    name               = ''
    if 'name' in kwargs:
      name = kwargs['name']
    
    labels = []
    for turnus_type in turnus_types:
      la = wx.StaticText (self, wx.ID_ANY, str (turnus_type))
      sc = wx_extensions.LinkedSpinCtr (turnus_type, self, wx.ID_ANY)
      
      labels.append (la)
      self.spin_controls.append (sc)
      
    for spin_control in self.spin_controls:
      self.Bind(wx.EVT_SPINCTRL, self._spinned, spin_control)
    
    grid_sizer = wx.FlexGridSizer (cols = 2)  
    for i, sc in enumerate (self.spin_controls):
      grid_sizer.Add (labels[i], 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 2)
      grid_sizer.Add (sc,        0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
    if name:
      sizer = wx.StaticBoxSizer (wx.StaticBox (self, wx.ID_ANY, name), wx.VERTICAL)
    else:
      sizer = wx.BoxSizer (wx.VERTICAL)
    sizer.Add (grid_sizer, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    self.SetSizerAndFit (sizer)
    
    self._set_permissions ( )
    
  def Enable (self, arg=True):
    """
    Overrides the default method.
    """
    super(ShiftSelector, self).Enable (arg)
    self._set_permissions ( )
    
  def Disable (self):
    """
    Overrides the default method.
    """
    self.Enable (False)
    
  def set_unit(self, schedule_unit):
    """
    Sets which workplace role pair is currently beeing edited by the application.
      @param schedule_unit: a data object
    """
    self.schedule_unit = schedule_unit
    self._set_permissions ( )
    
  def _spinned (self, event):
    """
    Event listener for the turnus type spin controls. Fires an update event.
    """
    self.add_method (self.workers_instance, self.schedule_unit, event.GetEventObject ( ).element, event.GetEventObject ( ).GetValue ( ))
    wx.PostEvent (self.GetEventHandler ( ), custom_events.UpdateEvent (self.GetId ( )))
    
  def _set_permissions(self):
    """
    Keeps the GUI in sync with the data.
    """
    if self.schedule_unit:
      turnus_types = self.schedule_unit.get_turnus_types ( )
      for spin_control in self.spin_controls:
        spin_control.SetValue (self.get_method (self.workers_instance, self.schedule_unit, spin_control.element))
        if spin_control.element in turnus_types and self.IsEnabled ( ):
          spin_control.Enable ( )
        else:
          spin_control.Disable  ( )
    else:
      for spin_control in self.spin_controls:
        spin_control.SetValue (0)
        spin_control.Disable  ( )

"""
This class is similar, to the ShiftSelector, but it doesn't handle logic. It fires events instead.
"""        
class DateShiftSelector (ShiftSelector):
  
  def __init__ (self, *args, **kwargs):
    """
    The default constructor.
    """
    ShiftSelector.__init__(self, *args, **kwargs)
    
    self.date = None
    
  def set_unit(self, schedule_unit_date):
    """
    Sets which schedule unit is currently being edited by the application.
      @param schedule_unit_date: a 2-tuple with a schedule unit as it's first element and a datetime.date 
        as it's last
    """
    self.schedule_unit, self.date = schedule_unit_date
    self._set_permissions ( )
    
  def get_values (self):
    """
    Returns a map, that maps turnus types, to the number of workers.
      return: a map
    """
    map = {}
    for spin_control in self.spin_controls:
      map[spin_control.element] = spin_control.GetValue ( )
    return map
    
  def Enable (self, arg=True):
    """
    Overrides the default method.
    """
    super(ShiftSelector, self).Enable (arg)      
    self._set_permissions ( )
    
  def Disable (self):
    """
    Overrides the default method.
    """
    self.Enable (False)
    
  def _spinned (self, event):
    """
    Event listener for the turnus type spin controls.
    """
    wx.PostEvent (self.GetEventHandler ( ), custom_events.UpdateEvent (self.GetId ( )))
    
  def _set_permissions(self):
    """
    Keeps the GUI in sync with the data.
    """
    if self.schedule_unit and self.date:
      turnus_types = self.schedule_unit.get_turnus_types ( )
      for spin_control in self.spin_controls:
        spin_control.SetValue (self.get_method (self.workers_instance, self.schedule_unit, spin_control.element, self.date))
        if spin_control.element in turnus_types and self.IsEnabled ( ):
          spin_control.Enable ( )
        else:
          spin_control.Disable  ( )
    else:
      for spin_control in self.spin_controls:
        spin_control.SetValue (0)
        spin_control.Disable  ( )
        