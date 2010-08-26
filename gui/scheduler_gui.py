# -*- coding: utf-8 -*-

import wx
import wx_extensions

from global_vars import employment_types, workplaces, turnuses, nurses
from data import employment_type
from scheduler import nurse_scheduler

class SchedulerPanel(wx.Panel):
  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    main_sizer = wx.BoxSizer(wx.VERTICAL)
    
    self.month_picker = wx_extensions.MonthChoice(self, wx.NewId())
    main_sizer.Add(self.month_picker, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT)
    
    self.start_button = wx.Button(self, wx.NewId(), 'Start')
    self.Bind(wx.EVT_BUTTON, self.schedule, self.start_button)
    main_sizer.Add(self.start_button, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT)
    
    helper_sizer = wx.BoxSizer(wx.HORIZONTAL)
    self.shift_control = ShiftControl(self, wx.NewId())
    helper_sizer.Add(self.shift_control, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT)
    
    self.monthly_hours_control = MothlyHoursControl(self, wx.NewId())
    helper_sizer.Add(self.monthly_hours_control, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT)
    
    main_sizer.Add(helper_sizer, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT)
    
    self.SetSizerAndFit(main_sizer)
    
  def schedule(self, event):
    
    #force the nurses to refresh employment_types
    #TODO: this should be done automaticly
    for employment_type in employment_types.employment_types:
      for nurse in nurses.nurses:
        if nurse.employment_type == employment_type:
          # skips the built in method on purpose
          nurse.employment_type = employment_type
    
    workers = self.shift_control.get_workers()
    ns = nurse_scheduler.NurseScheduler(nurses.nurses, workers.keys(), self.__get_date())
    for workplace in ns.workplaces:
      for turnus in workers[workplace]:
        workplace.set_worker(turnus, workers[workplace][turnus])
    
    ns.schedule()
    print 'Done'


    
  def __get_date(self):
    """Returns a datetime.date object."""
    return self.month_picker.get_value()
    
    
class ShiftControl(wx.Panel):

  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.workers = MetaWorkersContainer()
    self.workplace = None
    
    shift_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), "Stevilo zaposlenih v izmeni"), wx.VERTICAL)
    
    self.workplace_selector = wx_extensions.WorkplaceChoice(workplaces.workplaces, self, wx.NewId())
    self.Bind(wx.EVT_CHOICE, self.__set_workplace, self.workplace_selector)
    shift_sizer.Add(self.workplace_selector, 0, wx.CENTER)
    
    sub_sizer = wx.GridSizer(rows=0, cols=2)
    
    self.turnuses = []
    for turnus in turnuses.turnuses:
      sub_sizer.Add(wx.StaticText(self, wx.NewId(), str(turnus) + ":"), 0, wx.ALIGN_LEFT)
      self.turnuses.append(wx_extensions.LinkedSpinCtr(turnus, self, wx.NewId(), style=wx.SP_VERTICAL))
      self.turnuses[-1].SetRange(0, 200)
      self.turnuses[-1].SetValue(0)
      self.Bind(wx.EVT_SPINCTRL, self.__number_changed, self.turnuses[-1])
      sub_sizer.Add(self.turnuses[-1], 0, wx.ALIGN_TOP | wx.ALIGN_LEFT)
    
    
    shift_sizer.Add(sub_sizer, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT)
    
    self.__set_workplace(None)
    
    self.SetSizerAndFit(shift_sizer)
    
  def __set_workplace(self, event):
    self.workplace = self.workplace_selector.get_value()
    
    for turnus_spin in self.turnuses:
      if turnus_spin.element in self.workplace.allowed_turnuses:
        turnus_spin.Enable()
        #load spins with correct numbers
        turnus_spin.SetValue(self.workers.get_worker(self.workplace, turnus_spin.element))
      else:
        turnus_spin.Disable()
    
        
  def __number_changed(self, event):
    self.workers.set_worker(self.workplace, event.GetEventObject().element, event.GetEventObject().GetValue())
    
  def get_workers(self):
    """
    Returns a dictionary, that maps workplaces to turnuses and turnuses to the number of employees that must 
    work in that turnus.
      return: a double dictionary
    """
    
    temp = {}
    workers = self.workers.get_workers()
    
    for workplace in workers:
      for turnus in workers[workplace]:
        if workers[workplace][turnus] != 0:
          for turnus_num in self.turnuses:
            if turnus_num.IsEnabled and turnus_num.element == turnus:
              if workplace not in temp:
                temp[workplace] = {}
              temp[workplace][turnus] = workers[workplace][turnus]
    
    return temp 
    
    
class MothlyHoursControl(wx.Panel):
  
  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    hours_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), 'Stevilo ur v mesecu'), wx.VERTICAL)
    
    sub_sizer = wx.GridSizer(rows=0, cols=2)
    self.employment_type_hours = []
    for employment_type in employment_types.employment_types:
      self.employment_type_hours.append(wx_extensions.LinkedIntCtrl(employment_type, self, wx.NewId(), value=employment_type.monthly_hours, min=0))
      
      sub_sizer.Add(wx.StaticText(self, wx.NewId(), label=employment_type.label + ':'), 0, wx.ALIGN_LEFT)
      sub_sizer.Add(self.employment_type_hours[-1], 0, wx.ALIGN_TOP | wx.ALIGN_LEFT)
      
    hours_sizer.Add(sub_sizer, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT)
      
    self.SetSizerAndFit(hours_sizer)

""" A helper class """    
class MetaWorkersContainer:
  def __init__(self):
    self.container = {}
    
    for workplace in workplaces.workplaces:
      self.container[workplace] = {}
      for turnus in turnuses.turnuses:
        self.container[workplace][turnus] = 0
        
  def set_worker(self, workplace, turnus, number):
    self.container[workplace][turnus] = number
    
  def get_worker(self,workplace,turnus):
    return self.container[workplace][turnus]
    
  def get_workers(self):
    return self.container
      
