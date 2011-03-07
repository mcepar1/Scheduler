# -*- coding: Cp1250 -*-

import wx
import wx.calendar
import wx.lib.scrolledpanel
import wx.lib.buttons

from gui import custom_events, custom_widgets, wx_extensions

from data import employment_type

from scheduler.workers import Workers

"""
The main panel for editing the scheduling data.
"""
class SchedulerPanel(wx.lib.scrolledpanel.ScrolledPanel):
  def __init__(self, workplaces, roles, turnus_types, *args, **kwargs):
    """
    The default constructor.
    """
    wx.lib.scrolledpanel.ScrolledPanel.__init__(self, *args, **kwargs)
    
    
    from scheduler import workers
    #import wx.lib.buttons
    self.worker_container    = workers.get_workers ( )
    bitmap = wx.ArtProvider ( ).GetBitmap(wx.ART_TICK_MARK, wx.ART_BUTTON)
    
    self.workplace_role_pair = WorkplaceRoleSelector (workplaces, roles, self, wx.ID_ANY)
    self.start_button        = wx.lib.buttons.ThemedGenBitmapTextButton (self, wx.ID_ANY, bitmap, 'Zaženi')
    self.shift_control       = ShiftControl (turnus_types.get_all ( ), self.worker_container, self, wx.ID_ANY)
    
    self.start_button.SetLabel ('Zaženi')
    
    self.Bind(custom_events.EVT_UPDATED, self.__pair_selected, self.workplace_role_pair)
    self.Bind(wx.EVT_BUTTON, self.__start, self.start_button)
    
    sizer = wx.GridBagSizer ( )
    sizer.Add (self.workplace_role_pair, (0,0), (1,1), wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    sizer.Add (self.start_button,        (0,1), (1,1), wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.SHAPED)
    sizer.Add (self.shift_control,       (1,0), (1,2), wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
    
    self.SetSizerAndFit(sizer)
    self.SetupScrolling ( )
    
  def __pair_selected (self, event):
    """
    Event listener for the workplace-role pair selector
    """
    self.shift_control.set_unit (self.workplace_role_pair.get_selection ( ))
    
  def __start (self, event):
    """
    Starts the scheduling.
    """
    #TODO: rewrite the whole procedure.
    print 'OK'
    from gui import result_gui
    import global_vars
    window = result_gui.Result(global_vars.get_nurses ( ).get_all ( ),self.worker_container, self.worker_container.get_range ( )[0], None, wx.NewId(), title='Razpored')
    window.start()

"""
This class is used to select the workplace - role pair.
"""    
class WorkplaceRoleSelector(wx.Panel):
  def __init__ (self, workplaces, roles, *args, **kwargs):
    """
    The default constructor.
      workplaces: a data container object
      roles: a data container object
    """
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.workplace_selector = custom_widgets.CustomRadioBox (workplaces.get_all ( ), self, wx.ID_ANY, name='Delovišča', selectable=workplaces.get_all ( ))
    self.role_selector      = custom_widgets.CustomRadioBox (roles.get_all ( ),      self, wx.ID_ANY, name='Vloge')
    
    self.Bind(custom_events.EVT_UPDATED, self.__synchronize_workplace, self.workplace_selector)
    self.Bind(custom_events.EVT_UPDATED, self.__synchronize_role,      self.role_selector)
    
    
    sizer = wx.BoxSizer (wx.HORIZONTAL)
    sizer.Add (self.workplace_selector, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    sizer.Add (self.role_selector,      0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    self.SetSizerAndFit (sizer)
    
  def __synchronize_workplace (self, event):
    """
    Keeps the role elements in sync with the selected workplace and continues the event propagation.
    """
    workplace = self.workplace_selector.get_selected ( )
    self.role_selector.set_selectable (workplace.roles)
    
    wx.PostEvent (self.GetEventHandler ( ), custom_events.UpdateEvent (self.GetId ( )))
    
  def __synchronize_role (self, event):
    """
    Propagates the event.
    """
    wx.PostEvent (self.GetEventHandler ( ), custom_events.UpdateEvent (self.GetId ( )))
    
  def get_selection (self):
    """
    Returns a 2-tuple, that has a workplace as it's first element and a role as it's second.
      return: a 2-tuple, both elements are none if a single element is not selected.
    """
    workplace = self.workplace_selector.get_selected ( )
    role      = self.role_selector.get_selected ( )
    
    if workplace and role:
      return (workplace, role)
    else:
      return (None, None)
 
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
    self.workplace          = None
    self.role               = None
    
    
    
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
    sizer.Add (self.holidays_selector,  (1,0), (1,1), wx.ALIGN_BOTTOM)
    sizer.Add (self.date_specific,      (0,1), (2,1), wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
    self.SetSizerAndFit (sizer)
    
  def set_unit(self, workplace_role_pair):
    """
    Sets which workplace role pair is currently beeing edited by the application.
      workplace_role_pair: a 2-tuple with a workplace as it's first element and a role as it's second
    """
    # TODO: a tuple was chosen to keep the set_unit method as a single attribute method throughout the application
    # TODO: document this!
    self.workplace = workplace_role_pair[0]
    self.role      = workplace_role_pair[1]
    
    self.work_days_selector.set_unit ((self.workplace, self.role))
    self.holidays_selector.set_unit  ((self.workplace, self.role))
    self.date_specific.set_unit      ((self.workplace, self.role))
    
  def __updated (self, event):
    """
    Event listener for the shift selectors.
    """
    self.set_unit ([self.workplace, self.role])
    
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
    
    self.workplace = None
    self.role      = None
    
    self.workers       = workers_instance
    
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
    
    
    sizer = wx.StaticBoxSizer (wx.StaticBox (self, wx.ID_ANY, self.GetLabel ( )), wx.VERTICAL)
    sizer.Add (self.calendar,       0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    sizer.Add (self.enable_shifts,  0, wx.CENTER | wx.ALL, 5)
    sizer.Add (self.shift_selector, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
    self.SetSizerAndFit (sizer)
    
    self.__set_permissions ( )
    
  def set_unit(self, workplace_role_pair):
    """
    Sets which workplace role pair is currently beeing edited by the application.
      workplace_role_pair: a 2-tuple with a workplace as it's first element and a role as it's second
    """
    self.workplace = workplace_role_pair[0]
    self.role      = workplace_role_pair[1]
    
    self.__set_permissions ( )
    
    self.shift_selector.set_unit ((self.workplace, self.role, self.calendar.PyGetDate ( )))
    
    if self.enable_shifts.GetValue ( ):
      self.shift_selector.Enable ( )
    else:
      self.shift_selector.Disable ( )
    

    
  def __date_changed (self, event):
    """
    Event listener for the calendar.
    """
    self.__set_permissions ( )
    
    self.shift_selector.set_unit ((self.workplace, self.role, self.calendar.PyGetDate ( )))
    if self.enable_shifts.GetValue ( ):
      self.shift_selector.Enable ( )
    else:
      self.shift_selector.Disable ( )
    
  def __edit_date (self, event):
    """
    Event listener for the edit date checker.
    """
    if self.enable_shifts.GetValue ( ):
      self.workers.add_manual_date (self.calendar.PyGetDate ( ), self.workplace, self.role, self.shift_selector.get_values ( ))
      self.calendar.mark_special_date (self.calendar.PyGetDate ( ))
    else:
      self.workers.remove_manual_date (self.calendar.PyGetDate ( ), self.workplace, self.role)
      self.calendar.unmark_special_date (self.calendar.PyGetDate ( ))
    
    self.shift_selector.Enable (self.enable_shifts.GetValue ( ))
    self.__set_permissions ( )
    
  def __set_permissions (self):
    if self.workplace and self.role:
      self.calendar.Enable ( )
      self.enable_shifts.Enable ( )
      
      self.enable_shifts.SetValue (self.workers.is_date_manual (self.calendar.PyGetDate ( ), self.workplace, self.role))
      
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
    
    self.workplace = None
    self.role      = None
    
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
    
  def set_unit(self, workplace_role):
    """
    Sets which workplace role pair is currently beeing edited by the application.
      workplace_role: a 2-tuple with a workplace as it's first element and a role as it's second
    """
    self.workplace = workplace_role[0]
    self.role      = workplace_role[1]
    self._set_permissions ( )
    
  def _spinned (self, event):
    """
    Event listener for the turnus type spin controls. Fires an update event.
    """
    self.add_method (self.workers_instance, self.workplace, self.role, event.GetEventObject ( ).element, event.GetEventObject ( ).GetValue ( ))
    wx.PostEvent (self.GetEventHandler ( ), custom_events.UpdateEvent (self.GetId ( )))
    
  def _set_permissions(self):
    """
    Keeps the GUI in sync with the data.
    """
    if self.workplace and self.role:
      turnus_types = self.workplace.get_turnus_types ( )
      for spin_control in self.spin_controls:
        spin_control.SetValue (self.get_method (self.workers_instance, self.workplace, self.role, spin_control.element))
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
    
  def set_unit(self, workplace_role_date):
    """
    Sets which workplace role pair is currently beeing edited by the application.
      workplace_role_dates: a 3-tuple with a workplace as it's first element, a role as it's second and
        a datetime.date as it's last
    """
    self.workplace = workplace_role_date[0]
    self.role      = workplace_role_date[1]
    self.date      = workplace_role_date[2]
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
    if self.workplace and self.role and self.date:
      turnus_types = self.workplace.get_turnus_types ( )
      for spin_control in self.spin_controls:
        spin_control.SetValue (self.get_method (self.workers_instance, self.workplace, self.role, spin_control.element, self.date))
        if spin_control.element in turnus_types and self.IsEnabled ( ):
          spin_control.Enable ( )
        else:
          spin_control.Disable  ( )
    else:
      for spin_control in self.spin_controls:
        spin_control.SetValue (0)
        spin_control.Disable  ( )
         

class ScheduleControl(wx.Panel):
  
  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.persons = global_vars.get_nurses ( ).get_all ( )
    
    main_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), "Razvrščanje"), wx.HORIZONTAL)
    
    self.month_picker = wx_extensions.MonthChoice(self, wx.NewId())
    main_sizer.Add(self.month_picker, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT)
    
    self.start_button = wx.Button(self, wx.NewId(), 'Start')
    self.Bind(wx.EVT_BUTTON, self.Parent.schedule, self.start_button)
    main_sizer.Add(self.start_button, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT)
    
    self.SetSizerAndFit(main_sizer)
    
  def get_persons(self):
    """Returns the persons, that are set to be scheduled."""
    return self.persons
    
  def get_date(self):
    """Returns a datetime.date object."""
    return self.month_picker.get_value()


class ShiftControl_obsolete(wx.Panel):

  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.workers = {}
    self.date_workers = {}
    self.workplace = None
    self.role = None
    
    for workplace in global_vars.get_workplaces ( ).get_all ( ):
      self.workers[workplace] = {}
      for role in workplace.roles:
        self.workers[workplace][role] = {}
        for turnus in workplace.allowed_turnuses:
          self.workers[workplace][role][turnus] = 0
    
    shift_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), "Število zaposlenih v izmeni"), wx.VERTICAL)
    
    self.workplace_selector = wx_extensions.LinkedChoice(global_vars.get_workplaces ( ).get_all ( ), self, wx.NewId())
    self.Bind(wx.EVT_CHOICE, self.__set_workplace, self.workplace_selector)
    shift_sizer.Add(self.workplace_selector, 0, wx.CENTER)
    
    roles_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), "Vloge"), wx.VERTICAL)
    self.roles = []
    for role in global_vars.get_roles ( ).get_all ( ):
      self.roles.append(wx_extensions.LinkedCheckBox(role, self, wx.NewId(), str(role)))
      self.Bind(wx.EVT_CHECKBOX, self.__role_edited, self.roles[-1])
      roles_sizer.Add(self.roles[-1], 0, wx.ALIGN_LEFT)
    shift_sizer.Add(roles_sizer, 0, wx.CENTER)
    
    
    sub_sizer = wx.FlexGridSizer(rows=0, cols=2)
    
    self.turnus_types = []
    for turnus_type in global_vars.get_turnus_types ( ).get_all ( ):
      sub_sizer.Add(wx.StaticText(self, wx.NewId(), str(turnus_type) + ":"), 0, wx.ALIGN_LEFT)
      self.turnus_types.append(wx_extensions.LinkedSpinCtr(turnus_type, self, wx.NewId(), style=wx.SP_VERTICAL))
      self.turnus_types[-1].SetRange(0, 200)
      self.turnus_types[-1].SetValue(0)
      self.Bind(wx.EVT_SPINCTRL, self.__number_changed, self.turnus_types[-1])
      sub_sizer.Add(self.turnus_types[-1], 0, wx.ALIGN_TOP | wx.ALIGN_LEFT)

    
    
    shift_sizer.Add(sub_sizer, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT)
    
    self.date_specific_buttons = wx.Button(self, wx.NewId(), label='Uredi za posamezen dan')
    self.Bind(wx.EVT_BUTTON, self.__show_date_specific, self.date_specific_buttons)
    shift_sizer.Add(self.date_specific_buttons, 0, wx.CENTER)
    
    self.__set_workplace(None)
    
    self.SetSizerAndFit(shift_sizer)
    
  def refresh (self):
    self.__set_workplace(None)
    self.__role_edited(None)
    
  def __role_edited(self, event):
    if not event:
      self.role = None
    else:
      self.role = event.GetEventObject().element
    self.__set_permissions()
    
  def __set_workplace(self, event):
    self.workplace = self.workplace_selector.get_value()
    if not self.workplace:
      self.role = None
      
    if self.workplace and self.role not in self.workplace.roles:
      self.role = None
      
    self.__set_permissions()
    
        
  def __set_permissions(self):
    """This method keeps the whole GUI in sync."""
    
    if not self.workplace:
      for role_checker in self.roles:
        role_checker.SetValue(False)
        role_checker.Disable()
    if not self.role:
      for turnus_type_spin in self.turnus_types:
        turnus_type_spin.SetValue(0)
        turnus_type_spin.Disable()
        
        if self.workplace:
          for role_checker in self.roles:
            if role_checker.element in self.workplace.roles:
              role_checker.Enable()
              role_checker.SetValue(role_checker.element == self.role)
            else:
              role_checker.SetValue(False)
              role_checker.Disable()
        
    if self.workplace and self.role:
      #synchronize the roles first
      for role_checker in self.roles:
        if role_checker.element in self.workplace.roles:
          role_checker.Enable()
          if role_checker.element == self.role:
            role_checker.SetValue(True)
          else:
            role_checker.SetValue(False)
        else:
          role_checker.SetValue(False)
          role_checker.Disable() 
      
      for turnus_type_spin in self.turnus_types:
        # if the workplace has at least one turnus of the specified type
        if len (global_vars.get_turnuses ( ).get_by_type(turnus_type_spin.element) & self.workplace.allowed_turnuses):
          turnus_type_spin.Enable()
          #load spins with correct numbers
          try:
            turnus_type_spin.SetValue(self.workers[self.workplace][self.role][turnus_type_spin.element])
          except:
            if self.role not in self.workers[self.workplace]:
              self.workers[self.workplace][self.role] = {}
            self.workers[self.workplace][self.role][turnus_type_spin.element] = 0
            turnus_type_spin.SetValue(self.workers[self.workplace][self.role][turnus_type_spin.element])
        else:
          turnus_type_spin.SetValue(0)
          turnus_type_spin.Disable()
        
  def __number_changed(self, event):
    #might happen, if the workplace was changed during the runtime
    if self.workplace not in self.workers:
      self.workers[self.workplace] = {}
    if self.role not in self.workers[self.workplace]:
      self.workers[self.workplace][self.role] = {}
    self.workers[self.workplace][self.role][event.GetEventObject().element] = event.GetEventObject().GetValue()
    
  def __show_date_specific(self, event):
    if self.workplace not in self.date_workers:
      self.date_workers[self.workplace] = {}
      
    if self.role not in self.date_workers[self.workplace]:
      self.date_workers[self.workplace][self.role] = {}
    
    dialog = DateShiftControl(self.workplace, self.role, self.workers[self.workplace][self.role], self.date_workers[self.workplace][self.role], self, wx.NewId(), title=str(self.workplace))
    dialog.CenterOnScreen()
    dialog.ShowModal()
    
  def get_workers(self):
    """
    Returns a 2 -tuple. The first element of the tuple is a dictionary, that maps 
    workplaces to roles, roles to turnuses and turnuses to the number of employees 
    that must work in that turnus. The second element is a dictionary that maps 
    workplaces to roles, roles to dates, dates to turnuses and turnuses to the number
    of employees that must work in that turnus in the specific date. The second 
    element takes priority over the first one.
      return: 2 - tuple
    """
    
    static_workers = {}
    
    for workplace in self.workers:
      for role in self.workers[workplace]:
        for turnus_type in self.workers[workplace][role]:
          if self.workers[workplace][role][turnus_type] != 0:
            for turnus_type_num in self.turnus_types:
              if turnus_type_num.IsEnabled and turnus_type_num.element == turnus_type:
                if workplace not in static_workers:
                  static_workers[workplace] = {}
                if role not in static_workers[workplace]:
                  static_workers[workplace][role] = {}
                static_workers[workplace][role][turnus_type] = self.workers[workplace][role][turnus_type]
              
    
    return (static_workers, self.date_workers)
  
class DateShiftControl_obsolete(wx.Dialog):
  def __init__(self, workplace, role, workers, date_workers, *args, **kwargs):
    wx.Dialog.__init__(self, *args, **kwargs)
    
    self.workplace = workplace
    self.role = role
    self.workers = workers
    self.date_workers = date_workers
    
    sizer = wx.BoxSizer(wx.VERTICAL)
    
    self.calendar = wx_extensions.EnhancedCalendar(self, wx.NewId(), style=wx.calendar.CAL_MONDAY_FIRST | wx.calendar.CAL_SHOW_SURROUNDING_WEEKS | wx.calendar.CAL_SEQUENTIAL_MONTH_SELECTION)
    self.Bind(wx.calendar.EVT_CALENDAR_SEL_CHANGED, self.__update_date, self.calendar)
    sizer.Add(self.calendar, 0, wx.ALIGN_LEFT | wx.EXPAND)
    
    
    sub_sizer = wx.FlexGridSizer(rows=0, cols=2)
    
    self.turnus_types = []
    for turnus_type in global_vars.get_turnus_types ( ).get_all ( ):
      sub_sizer.Add(wx.StaticText(self, wx.NewId(), str(turnus_type) + ":"), 0, wx.ALIGN_LEFT)
      self.turnus_types.append(wx_extensions.LinkedSpinCtr(turnus_type, self, wx.NewId(), style=wx.SP_VERTICAL))
      self.turnus_types[-1].SetRange(0, 200)
      self.turnus_types[-1].SetValue(0)
      self.turnus_types[-1].Disable()
      self.Bind(wx.EVT_SPINCTRL, self.__number_changed, self.turnus_types[-1])
      sub_sizer.Add(self.turnus_types[-1], 0, wx.ALIGN_TOP | wx.ALIGN_LEFT)
    
    
    sizer.Add(sub_sizer, 0, wx.ALIGN_LEFT)
    
    self.close = wx.Button(self, wx.NewId(), label='OK')
    self.Bind(wx.EVT_BUTTON, self.__close, self.close)
    sizer.Add(self.close, 0, wx.ALIGN_RIGHT)
    
    self.SetSizerAndFit(sizer)
    
  def __close(self, event):
    self.Close()
    
  def __number_changed(self, event):
    number = event.GetEventObject().GetValue()
    turnus_type = event.GetEventObject().element
    
    if self.calendar.PyGetDate() not in self.date_workers:
      self.date_workers[self.calendar.PyGetDate()] = {}
    self.date_workers[self.calendar.PyGetDate()][turnus_type] = number
    
  def __update_date(self, event):
    date = self.calendar.PyGetDate()
    
    for turnus_type_spin in self.turnus_types:
      if len (global_vars.get_turnuses ( ).get_by_type(turnus_type_spin.element, self.workplace)):
        turnus_type_spin.Enable()
      else:
        turnus_type_spin.Disable()
    
    if date not in self.date_workers:
      self.date_workers[date] = {}
      for turnus_type_spin in self.turnus_types:
        if turnus_type_spin.IsEnabled() and turnus_type_spin.element in self.workers:
          self.date_workers[date][turnus_type_spin.element] = self.workers[turnus_type_spin.element]
        else:
          self.date_workers[date][turnus_type_spin.element] = 0
    
    turnus_workers = self.date_workers[date]
    for turnus_type in turnus_workers:
      for turnus_type_spin in self.turnus_types:
        if turnus_type_spin.IsEnabled() and turnus_type == turnus_type_spin.element:
          turnus_type_spin.SetValue(self.date_workers[date][turnus_type])
  
      
    
    
class MothlyHoursControl(wx.Panel):
  
  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    hours_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), 'Število ur v mesecu'), wx.VERTICAL)
    
    sub_sizer = wx.FlexGridSizer(rows=0, cols=2)
    self.employment_type_hours = []
    for employment_type in global_vars.get_employment_types ( ).get_all ( ):
      self.employment_type_hours.append(wx_extensions.LinkedIntCtrl(employment_type, self, wx.NewId(), value=employment_type.monthly_hours, min=0))
      
      sub_sizer.Add(wx.StaticText(self, wx.NewId(), label=employment_type.label + ':'), 0, wx.ALIGN_LEFT)
      sub_sizer.Add(self.employment_type_hours[-1], 0, wx.ALIGN_TOP | wx.ALIGN_LEFT)
      
    hours_sizer.Add(sub_sizer, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT)
      
    self.SetSizerAndFit(hours_sizer)
  
    
