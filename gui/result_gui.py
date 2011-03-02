# -*- coding: Cp1250 -*-

import global_vars
from scheduler import person_scheduler
from utils import time_conversion, exporter

import wx
import wx.grid
import wx.lib.newevent

from threading import Thread
import time
import os


# This creates a new Event class and a EVT binder function
(ScheduleMessageEvent, EVT_SCHEDULE_MESSAGE) = wx.lib.newevent.NewEvent()

class Result(wx.Frame):
  def __init__(self, persons, static_workers, date_workers, date, *args, **kwargs):
    wx.Frame.__init__(self, *args, **kwargs)
    
    self.progress_dialog = NonModalProgressDialog(self, wx.NewId(), title="Razvrscanje ...")
    
    self.scheduler = Scheduler(self, persons, static_workers, date_workers, date)
    self.Bind(EVT_SCHEDULE_MESSAGE, self.__message_recieved)
    
    self.Hide()
    
  def start (self):
    self.progress_dialog.CenterOnScreen()
    self.progress_dialog.Show(True)
    self.scheduler.start()
    Timer(self.scheduler).start()
    
    
    
  def fill_grid(self):
    table = self.scheduler.get_result()
    headers = table[0]
    rows = table[1:]
    
    self.grid.CreateGrid(len(rows), len(headers))
      
    for i in range(len(headers)):
      self.grid.SetColLabelValue(i, headers[i])
      
    for i in range(len(rows)):
      for j in range(len(rows[i])):
        self.grid.SetCellValue(i, j, rows[i][j])
        
    self.grid.AutoSize()
    
  def __message_recieved(self, event):
    """
    The event listener for thread synchronization.
    """
    if event.running:
      self.progress_dialog.update(event.message)
    else:
      self.progress_dialog.Destroy()
      if event.error:
        dlg = wx.MessageDialog(self, event.message, 'Napaka', wx.OK | wx.ICON_INFORMATION)
        dlg.CenterOnScreen()
        dlg.ShowModal()
        dlg.Close()
        self.Destroy()
      else:
        self.__reconstruct()
        
  def __reconstruct(self):
    main_sizer = wx.BoxSizer(wx.VERTICAL)
    
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    self.grid = wx.grid.Grid(self, wx.NewId())
    self.fill_grid()
    sizer.Add(self.grid, 4, wx.ALIGN_LEFT | wx.EXPAND)
    
    self.warnings = WarningsPanel(self.scheduler.get_warnings(), self, wx.NewId())
    sizer.Add(self.warnings, 1, wx.ALIGN_LEFT | wx.EXPAND)
    
    main_sizer.Add(sizer, 1, wx.ALIGN_LEFT | wx.EXPAND)
    
    self.save_button = wx.Button(self, wx.NewId(), label='Shrani')
    self.Bind(wx.EVT_BUTTON, self.__save, self.save_button)
    main_sizer.Add(self.save_button, 0, wx.ALIGN_RIGHT)
    
    self.SetSizerAndFit(main_sizer)
    self.Show(True)
        
  def __save(self, event):
    """Saves the schedule"""
    dlg = wx.FileDialog(self, message="Shrani datoteko ...", defaultDir=os.path.expanduser("~"), defaultFile="razpored.csv", wildcard="CSV datoteka (*.csv)|*.csv", style=wx.SAVE | wx.FD_OVERWRITE_PROMPT)
    if dlg.ShowModal() == wx.ID_OK:
      path = dlg.GetPath()
      #force the csv appendix
      if path.split(r'.')[-1] != 'csv':
        path += '.csv'
      
      # save the internal schedule
      if not self.scheduler.save():
        action = wx.MessageBox(parent=self, message='Za ta mesec ze obstaja shranjen razpored, ki se bo uporabil pri razvrcanju naslednjega meseca. Ali ga zelite prepisati?', style=wx.YES_NO | wx.ICON_EXCLAMATION)
        if action == wx.YES:
          self.scheduler.save(force=True)
        else:
          return
        
      # save the final *.csv file
      exporter.exportCSV(self.scheduler.get_workplace_result(), path)
    dlg.Destroy()
        
class WarningsPanel(wx.Panel):
  def __init__(self, warnings, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), "Opozorila"), wx.VERTICAL)
    self.tree = TreeWarnings(warnings, self, wx.NewId(), style=wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT)
    sizer.Add(self.tree, 1, wx.ALIGN_LEFT | wx.EXPAND)
    
    self.SetSizerAndFit(sizer)
        
class TreeWarnings(wx.TreeCtrl):
  def __init__(self, warnings, *args, **kwargs):
    wx.TreeCtrl.__init__(self, *args, **kwargs)
    
    root = self.AddRoot("Koren")
    
    for workplace in sorted(warnings.keys()):
      w_item = self.AppendItem(root, str(workplace))
      for role in sorted(warnings[workplace].keys()):
        r_item = self.AppendItem(w_item, str(role))
        for turnus in sorted(warnings[workplace][role].keys()):
          t_item = self.AppendItem(r_item, str(turnus))
          for date in sorted(warnings[workplace][role][turnus].keys()):
            self.AppendItem(t_item, time_conversion.date_to_string(date) + ': ' + warnings[workplace][role][turnus][date])

    
"""
This is a custom class that behaves very similar to the wx.ProgressDialog.
"""    
class NonModalProgressDialog(wx.Dialog):
  def __init__(self, *args, **kwargs):
    wx.Dialog.__init__(self, *args, **kwargs)
    
    sizer = wx.BoxSizer(wx.VERTICAL)
    
    self.text = wx.StaticText(self, wx.NewId(), label='')
    sizer.Add(self.text, 0, wx.CENTER)
    
    self.gauge = wx.Gauge(self, wx.NewId(), size=(400, 10))
    sizer.Add(self.gauge, 0, wx.ALIGN_LEFT)
    
    self.SetSizerAndFit(sizer)
    
  def update(self, message):
    self.text.SetLabel(message)
    self.gauge.Pulse()

"""
This class is just a wrapper around the Person
"""
class Scheduler(Thread):
  
  def __init__(self, parent, *args):
    """
    The default constructor.
      parent: an instance of the wx.Window
      *args: look the __schedule method
    """
    
    Thread.__init__(self, target=self.__schedule, args=args)
    self.wx_parent = parent
    self.running = True
    self.message = ''
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
    """A wrapper around the Personget_schedule_matrix method."""
    if self.scheduler:
      return self.scheduler.get_schedule_matrix()
    else:
      return [[], []]
  
  def get_workplace_result(self):
    """A wrapper around the Personget_workplace_matrix method."""
    if self.scheduler:
      return self.scheduler.get_workplace_matrix ()
    else:
      return {}
    
  def get_warnings(self):
    """A wrapper around the Personget_workplace_warnings function."""
    if self.scheduler:
      return self.scheduler.get_workplace_warnings()
    else:
      raise Exception('Razpored ne obstaja')
    
  def save(self, force=False):
    """A wrapper around the Personsave method"""
    
    if self.scheduler:
      return self.scheduler.save(force=force)
    else:
      raise Exception ('Razpored ne obstaja')
    
    
  def __schedule(self, persons, static_workers, date_workers, date):
    """
    This method creates the scheduler and start's scheduling.
      persons: a list of persons, that will be scheduled
      static_workers: a dictionary, that maps workplaces to turnuses and then to
                      the number of workers
      date_workers: similar as static workers, only that it maps workplaces to dates
                    and dates to turnuses, ...
      date: a datetime.date instance that contains the month and year that will 
            be scheduled
    """
    
    self.running = True
    #try:
    self.scheduler = self.__initialize_scheduler(persons, static_workers, date_workers, date)
    self.scheduler.schedule()
    #except Exception as e:
    #  self.send_message(message=str(e), running=False, error=True)
          
    self.send_message('Razvrscevanje koncano.', running=False, error=False)
    self.running = False
    
    
    
  def __initialize_scheduler(self, persons, static_workers, date_workers, date):
    """
    This method initializes the scheduler.
      arguments: look at __schedule method
      return: an instance of the PersonScheduler
    """
    
    self.send_message('Predpriprave ...')
    #force the persons to refresh employment_types
    #TODO: this should be done automatically
    for employment_type in global_vars.get_employment_types ( ).get_all ( ):
      for person in persons:
        if person.employment_type == employment_type:
          # skips the built in method on purpose
          person.employment_type = employment_type
          
    #force the persons to refresh workplaces
    #TODO: this should be done automatically
    for workplace in global_vars.get_workplaces ( ).get_all ( ):
      for person in persons:
        if workplace in person.workplaces:
          person.workplaces.remove(workplace)
          person.workplaces.add(workplace)
          
    ps = person_scheduler.PersonScheduler(persons, set(static_workers.keys() + date_workers.keys()), date, log=self)
    for workplace in ps.workplaces:
      if workplace in static_workers:
        for role in static_workers[workplace]:
          for turnus_type in static_workers[workplace][role]:
            workplace.set_worker(role, turnus_type, static_workers[workplace][role][turnus_type])
      if workplace in date_workers:
        for role in date_workers[workplace]:
          for date in date_workers[workplace][role]:
            for turnus_type in date_workers[workplace][role][date]:
              workplace.set_worker(role, turnus_type, date_workers[workplace][role][date][turnus_type], date)
            
    return ps
  
"""
Might be a performance risk
"""  
class Timer(Thread):
  #TODO: check performance
  def __init__(self, log):
    Thread.__init__(self)
    self.log = log
    
  def run(self):
    while(self.log.running):
      try:
        self.log.send_message()
        time.sleep(0.3)
      except:
        self.running = False
        
  

        
