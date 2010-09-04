# -*- coding: utf-8 -*-

import wx
import wx_extensions
import result_gui

from global_vars import employment_types, workplaces, turnuses, nurses, doctors, turnus_types
from data import employment_type
from scheduler import person_scheduler

class SchedulerPanel(wx.Panel):
  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    main_sizer = wx.BoxSizer(wx.HORIZONTAL)
    
    self.shift_control = ShiftControl(self, wx.NewId())
    main_sizer.Add(self.shift_control, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT)
    
    
    helper_sizer = wx.BoxSizer(wx.VERTICAL)
    self.monthly_hours_control = MothlyHoursControl(self, wx.NewId())
    helper_sizer.Add(self.monthly_hours_control, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT)
    
    self.schedule_control = ScheduleControl(self, wx.NewId())
    helper_sizer.Add(self.schedule_control, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
    main_sizer.Add(helper_sizer, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT)
    
    
    
    self.Bind(wx.EVT_SET_FOCUS, self.refresh, self)
    self.SetSizerAndFit(main_sizer)
    
  def refresh (self, event=None):
    self.shift_control.refresh()
    
  def schedule(self, event):
    """Event listener for the start button."""
    
    persons = self.schedule_control.get_persons()
    static_workers, date_workers = self.shift_control.get_workers()
    date = self.__get_date()
    
    window = result_gui.Result(persons, static_workers, date_workers, date, None, wx.NewId(), title='Razpored')
    window.start()

    
  def __get_date(self):
    """Returns a datetime.date object."""
    return self.schedule_control.get_date()

class ScheduleControl(wx.Panel):
  
  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.persons = nurses.nurses
    
    main_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), "Razvrscanje"), wx.VERTICAL)
    
    self.month_picker = wx_extensions.MonthChoice(self, wx.NewId())
    main_sizer.Add(self.month_picker, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT)
    
    self.select_persons = wx.RadioBox(self, wx.NewId(), 'Izberi za razvrscanje', choices=['Razvrsti medicinske setsre', 'Razvrsti zdravnike'], majorDimension=1, style=wx.RA_SPECIFY_COLS)
    self.Bind(wx.EVT_RADIOBOX, self.__select_persons, self.select_persons)
    main_sizer.Add(self.select_persons, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT)
    
    self.start_button = wx.Button(self, wx.NewId(), 'Start')
    self.Bind(wx.EVT_BUTTON, self.Parent.schedule, self.start_button)
    main_sizer.Add(self.start_button, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT)
    
    self.SetSizerAndFit(main_sizer)
  
  def __select_persons(self, event):
    """Event listener for the radiobox."""
    if event.GetInt() == 0:
      self.persons = nurses.nurses
    elif event.GetInt() == 1:
      self.persons = doctors.doctors
    else:
      raise Exception('Neveljavna izbira.')
    
  def get_persons(self):
    """Returns the persons, that are set to be scheduled."""
    return self.persons
    
  def get_date(self):
    """Returns a datetime.date object."""
    return self.month_picker.get_value()
    
class ShiftControl(wx.Panel):

  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.workers = {}
    self.date_workers = {}
    self.workplace = None
    
    for workplace in workplaces.workplaces:
      self.workers[workplace] = {}
      for turnus in workplace.allowed_turnuses:
        self.workers[workplace][turnus] = 0
    
    shift_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), "Stevilo zaposlenih v izmeni"), wx.VERTICAL)
    
    self.workplace_selector = wx_extensions.WorkplaceChoice(workplaces.workplaces, self, wx.NewId())
    self.Bind(wx.EVT_CHOICE, self.__set_workplace, self.workplace_selector)
    shift_sizer.Add(self.workplace_selector, 0, wx.CENTER)
    
    
    sub_sizer = wx.FlexGridSizer(rows=0, cols=2)
    
    self.turnus_types = []
    for turnus_type in turnus_types.turnus_types:
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
    
  def __set_workplace(self, event):
    self.workplace = self.workplace_selector.get_value()
    
    for turnus_type_spin in self.turnus_types:
      # if the workplace has at least one turnus of the specified type
      if len (turnuses.get_by_type(turnus_type_spin.element) & self.workplace.allowed_turnuses):
        turnus_type_spin.Enable()
        #load spins with correct numbers
        try:
          turnus_type_spin.SetValue(self.workers[self.workplace][turnus_type_spin.element])
        except:
          turnus_type_spin.SetValue(0)
      else:
        turnus_type_spin.Disable()
    
        
  def __number_changed(self, event):
    self.workers[self.workplace][event.GetEventObject().element] = event.GetEventObject().GetValue()
    
  def __show_date_specific(self, event):
    if self.workplace not in self.date_workers:
      self.date_workers[self.workplace] = {}
    
    dialog = DateShiftControl(self.workplace, self.workers[self.workplace], self.date_workers[self.workplace], self, wx.NewId(), title=str(self.workplace))
    dialog.CenterOnScreen()
    dialog.ShowModal()
    
  def get_workers(self):
    """
    Returns a 2 -tuple. The first element of the tuple is a dictionary, that maps 
    workplaces to turnuses and turnuses to the number of employees that must work 
    in that turnus. The second element is a dictionary that maps workplaces to dates, 
    dates to turnuses and turnuses to the number of employees that must work in that 
    turnus in the specific date. The second element takes priority over the first one.
      return: 2 - tuple
    """
    
    static_workers = {}
    
    for workplace in self.workers:
      for turnus_type in self.workers[workplace]:
        if self.workers[workplace][turnus_type] != 0:
          for turnus_type_num in self.turnus_types:
            if turnus_type_num.IsEnabled and turnus_type_num.element == turnus_type:
              if workplace not in static_workers:
                static_workers[workplace] = {}
              static_workers[workplace][turnus_type] = self.workers[workplace][turnus_type]
              
    
    return (static_workers, self.date_workers)
  
class DateShiftControl(wx.Dialog):
  def __init__(self, workplace, workers, date_workers, *args, **kwargs):
    wx.Dialog.__init__(self, *args, **kwargs)
    
    self.workplace = workplace
    self.workers = workers
    self.date_workers = date_workers
    
    sizer = wx.BoxSizer(wx.VERTICAL)
    
    self.calendar = wx_extensions.EnhancedCalendar(self, wx.NewId(), style=wx.calendar.CAL_MONDAY_FIRST | wx.calendar.CAL_SHOW_SURROUNDING_WEEKS | wx.calendar.CAL_SEQUENTIAL_MONTH_SELECTION)
    self.Bind(wx.calendar.EVT_CALENDAR_SEL_CHANGED, self.__update_date, self.calendar)
    sizer.Add(self.calendar, 0, wx.ALIGN_LEFT | wx.EXPAND)
    
    
    sub_sizer = wx.FlexGridSizer(rows=0, cols=2)
    
    self.turnus_types = []
    for turnus_type in turnus_types.turnus_types:
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
      if len (turnuses.get_by_type(turnus_type_spin.element, self.workplace)):
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
    
    hours_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), 'Stevilo ur v mesecu'), wx.VERTICAL)
    
    sub_sizer = wx.FlexGridSizer(rows=0, cols=2)
    self.employment_type_hours = []
    for employment_type in employment_types.employment_types:
      self.employment_type_hours.append(wx_extensions.LinkedIntCtrl(employment_type, self, wx.NewId(), value=employment_type.monthly_hours, min=0))
      
      sub_sizer.Add(wx.StaticText(self, wx.NewId(), label=employment_type.label + ':'), 0, wx.ALIGN_LEFT)
      sub_sizer.Add(self.employment_type_hours[-1], 0, wx.ALIGN_TOP | wx.ALIGN_LEFT)
      
    hours_sizer.Add(sub_sizer, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT)
      
    self.SetSizerAndFit(hours_sizer)
  
    
