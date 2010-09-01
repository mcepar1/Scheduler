# -*- coding: utf-8 -*-

import wx
import wx_extensions
import result_gui

from global_vars import employment_types, workplaces, turnuses, nurses, doctors
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
    
  def refresh (self, event = None):
    self.shift_control.refresh()
    
  def schedule(self, event):
    """
    persons = self.schedule_control.get_persons()
    
    #force the persons to refresh employment_types
    #TODO: this should be done automaticly
    for employment_type in employment_types.employment_types:
      for person in persons:
        if person.employment_type == employment_type:
          # skips the built in method on purpose
          person.employment_type = employment_type
          
    #force the persons to refresh workplaces
    #TODO: this should be done automatically
    for workplace in workplaces.workplaces:
      for person in persons:
        if workplace in person.workplaces:
          person.workplaces.remove(workplace)
          person.workplaces.add(workplace)
    
    static_workers, date_workers = self.shift_control.get_workers()
    ps = person_scheduler.PersonScheduler(persons, static_workers.keys() + date_workers.keys(), self.__get_date())
    for workplace in ps.workplaces:
      if workplace in static_workers:
        for turnus in static_workers[workplace]:
          workplace.set_worker(turnus, static_workers[workplace][turnus])
      if workplace in date_workers:
        for date in date_workers[workplace]:
          for turnus in date_workers[workplace][date]:
            workplace.set_worker(turnus, date_workers[workplace][date][turnus], date)
    
    
    ps.schedule()
    #ps.start_thread()
    self.__show_result(ps)
    """
    persons = self.schedule_control.get_persons()
    static_workers, date_workers = self.shift_control.get_workers()
    date = self.__get_date()
    
    window = result_gui.Result(persons, static_workers, date_workers, date, None, wx.NewId(), title = 'Razpored')
    window.start()

  """
  def __show_result(self, scheduler):
    dialog = result_gui.Result(scheduler, self, wx.NewId())
    dialog.CenterOnScreen()
    dialog.Show(True)
  """
    
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
    
    self.turnuses = []
    for turnus in turnuses.turnuses:
      sub_sizer.Add(wx.StaticText(self, wx.NewId(), str(turnus) + ":"), 0, wx.ALIGN_LEFT)
      self.turnuses.append(wx_extensions.LinkedSpinCtr(turnus, self, wx.NewId(), style=wx.SP_VERTICAL))
      self.turnuses[-1].SetRange(0, 200)
      self.turnuses[-1].SetValue(0)
      self.Bind(wx.EVT_SPINCTRL, self.__number_changed, self.turnuses[-1])
      sub_sizer.Add(self.turnuses[-1], 0, wx.ALIGN_TOP | wx.ALIGN_LEFT)

    
    
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
    
    for turnus_spin in self.turnuses:
      if turnus_spin.element in self.workplace.allowed_turnuses:
        turnus_spin.Enable()
        #load spins with correct numbers
        try:
          turnus_spin.SetValue(self.workers[self.workplace][turnus_spin.element])
        except:
          turnus_spin.SetValue(0)
      else:
        turnus_spin.Disable()
    
        
  def __number_changed(self, event):
    self.workers[self.workplace][event.GetEventObject().element] = event.GetEventObject().GetValue()
    
  def __show_date_specific(self, event):
    if self.workplace not in self.date_workers:
      self.date_workers[self.workplace] = {}
    
    dialog = DateShiftControl(self.workplace, self.workers[self.workplace], self.date_workers[self.workplace], self, wx.NewId())
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
      for turnus in self.workers[workplace]:
        if self.workers[workplace][turnus] != 0:
          for turnus_num in self.turnuses:
            if turnus_num.IsEnabled and turnus_num.element == turnus:
              if workplace not in static_workers:
                static_workers[workplace] = {}
              static_workers[workplace][turnus] = self.workers[workplace][turnus]
              
    
    return (static_workers, self.date_workers)
  
class DateShiftControl(wx.Dialog):
  def __init__(self, workplace, workers, date_workers, *args, **kwargs):
    wx.Dialog.__init__(self, *args, **kwargs)
    
    self.workplace = workplace
    self.workers = workers
    self.date_workers = date_workers
    
    sizer = wx.BoxSizer(wx.VERTICAL)
    
    sizer.Add(wx.StaticText(self, wx.NewId(), label=str(self.workplace)), 0, wx.CENTER)
    
    self.calendar = wx_extensions.EnhancedCalendar(self, wx.NewId())
    self.Bind(wx.calendar.EVT_CALENDAR_SEL_CHANGED, self.__update_date, self.calendar)
    sizer.Add(self.calendar, 0, wx.ALIGN_LEFT | wx.EXPAND)
    
    
    sub_sizer = wx.FlexGridSizer(rows=0, cols=2)
    
    self.turnuses = []
    for turnus in turnuses.turnuses:
      sub_sizer.Add(wx.StaticText(self, wx.NewId(), str(turnus) + ":"), 0, wx.ALIGN_LEFT)
      self.turnuses.append(wx_extensions.LinkedSpinCtr(turnus, self, wx.NewId(), style=wx.SP_VERTICAL))
      self.turnuses[-1].SetRange(0, 200)
      self.turnuses[-1].SetValue(0)
      self.turnuses[-1].Disable()
      self.Bind(wx.EVT_SPINCTRL, self.__number_changed, self.turnuses[-1])
      sub_sizer.Add(self.turnuses[-1], 0, wx.ALIGN_TOP | wx.ALIGN_LEFT)
    
    
    sizer.Add(sub_sizer, 0, wx.ALIGN_LEFT)
    
    self.close = wx.Button(self, wx.NewId(), label='OK')
    self.Bind(wx.EVT_BUTTON, self.__close, self.close)
    sizer.Add(self.close, 0, wx.ALIGN_RIGHT)
    
    self.SetSizerAndFit(sizer)
    
  def __close(self, event):
    self.Close()
    
  def __number_changed(self, event):
    number = event.GetEventObject().GetValue()
    turnus = event.GetEventObject().element
    
    if self.calendar.PyGetDate() not in self.date_workers:
      self.date_workers[self.calendar.PyGetDate()] = {}
    self.date_workers[self.calendar.PyGetDate()][turnus] = number
    
  def __update_date(self, event):
    date = self.calendar.PyGetDate()
    
    for turnus_spin in self.turnuses:
      if turnus_spin.element in self.workplace.allowed_turnuses:
        turnus_spin.Enable()
      else:
        turnus_spin.Disable()
    
    if date not in self.date_workers:
      self.date_workers[date] = {}
      for turnus_spin in self.turnuses:
        if turnus_spin.IsEnabled() and turnus_spin.element in self.workers:
          self.date_workers[date][turnus_spin.element] = self.workers[turnus_spin.element]
        else:
          self.date_workers[date][turnus_spin.element] = 0
    
    turnus_workers = self.date_workers[date]
    for turnus in turnus_workers:
      for turnus_spin in self.turnuses:
        if turnus_spin.IsEnabled() and turnus == turnus_spin.element:
          turnus_spin.SetValue(self.date_workers[date][turnus])
      
      
    
    
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
  
    
