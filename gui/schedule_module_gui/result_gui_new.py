# -*- coding: Cp1250 -*-

import wx
import wx.grid
import wx.lib.newevent

from utils import time_conversion, exporter

import os
from threading import Thread



# This creates a new Event class and a EVT binder function
(ScheduleMessageEvent, EVT_SCHEDULE_MESSAGE) = wx.lib.newevent.NewEvent()

"""
This class represents the final view of the scheduled nurses.
"""
class Result(wx.Panel):
  def __init__(self, proxy, *args, **kwargs):
    """
    The default constructor.
      @param proxy: the intermediate class between the data model and the scheduler's model.
    """
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.scheduler      = Scheduler(self, proxy)
    
    self.progress_panel = ProgressPanel (self, wx.ID_ANY, name='Status razvrščanja ...')
    self.grid           = wx.grid.Grid  (self, wx.ID_ANY)
    self.warnings       = WarningsPanel (self, wx.ID_ANY)
    self.save_button    = wx.Button     (self, wx.ID_ANY, label='Shrani')
    
    self.Bind (EVT_SCHEDULE_MESSAGE, self.__message_recieved)
    self.Bind (wx.EVT_BUTTON,        self.__save,           self.save_button)
    
    
    result_sizer = wx.BoxSizer(wx.HORIZONTAL)
    result_sizer.Add (self.grid,     4, wx.ALIGN_LEFT | wx.EXPAND | wx.LEFT, 4)
    result_sizer.Add (self.warnings, 1, wx.ALIGN_LEFT | wx.EXPAND)
    
    main_sizer = wx.BoxSizer (wx.VERTICAL)
    main_sizer.Add (self.progress_panel, 0, wx.ALIGN_LEFT | wx.EXPAND)
    main_sizer.Add (result_sizer,        1, wx.ALIGN_LEFT | wx.EXPAND)
    main_sizer.Add (self.save_button,    0, wx.ALIGN_LEFT | wx.EXPAND)
    
    self.SetSizerAndFit(main_sizer)
    
    self.progress_panel.Hide ( )
    self.fill_grid ( )
    
  def start (self):
    self.progress_panel.Show ( )
    self.grid.Hide ( )
    self.warnings.Hide ( )
    
    self.scheduler.start ( )
    
    
    
  def fill_grid(self):
    table = self.scheduler.get_result ( )
    headers = table[0]
    rows = table[1:]
    
    self.grid.ClearGrid ( )
    self.grid.SetTable (None)
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
      self.progress_panel.update(event.message)
    else:
      if event.error:
        dlg = wx.MessageDialog(self, event.message, 'Napaka', wx.OK | wx.ICON_INFORMATION)
        dlg.CenterOnScreen()
        dlg.ShowModal()
        dlg.Close()
        self.Destroy()
      else:
        self.__reconstruct()
        
  def __reconstruct(self):
    self.fill_grid ( )
    self.warnings.display_warnings (self.scheduler.get_warnings ( ))
    
    self.grid.Show ( )
    self.warnings.Show ( )
    self.progress_panel.Hide ( )
    
    self.Layout ( )
    self.Refresh ( )
    
        
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
          self.scheduler.save(overwrite=True)
        else:
          return
        
      # save the final *.csv file
      exporter.exportCSV(self.scheduler.get_workplace_result(), path)
    dlg.Destroy()
        
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
  TIMER_SPEED = 200
  
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
    self.scheduler = self.__initialize_scheduler (self.proxy)
    
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
    
  def save(self, overwrite=False):
    """A wrapper around the Person's save method"""
    if self.scheduler:
      return self.proxy.save(self.scheduler, overwrite=overwrite)
    else:
      raise Exception ('Razpored ne obstaja')
    
    
  def __schedule(self, proxy):
    """
    This method creates the scheduler and start's scheduling.
      @param proxy: the intermediate class between the data model and the scheduling model.
    """
    
    self.running = True
    #try:
    self.proxy     = proxy
    self.scheduler = self.__initialize_scheduler (proxy)
    self.scheduler.schedule ( )
    #except Exception as e:
    #  self.send_message(message=str(e), running=False, error=True)
          
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

        
