# -*- coding: Cp1250 -*-

"""
This file contains a class, that handles a month's schedule. 
"""
import scheduler_gui
import result_gui_new

import wx.lib.scrolledpanel

"""
This class contains a single notebook page.
"""
class SchedulePage (wx.lib.scrolledpanel.ScrolledPanel):
  
  def __init__ (self, proxy, *args, **kwargs):
    """
    The default constructor.
      @param proxy: a proxy object
    """
    wx.lib.scrolledpanel.ScrolledPanel.__init__(self, *args, **kwargs)
    
    self.proxy          = proxy
    self.show_results   = []
    self.results        = []
    self.number_results = 0

    self.workers = scheduler_gui.SchedulerPanel (self.proxy, self, wx.ID_NEW)
    
    workers_sizer = wx.StaticBoxSizer (wx.StaticBox (self, wx.ID_ANY, ''), wx.VERTICAL)
    workers_sizer.Add (self.workers, 1, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
    self.result_sizer = wx.StaticBoxSizer (wx.StaticBox (self, wx.ID_ANY, 'Rezultat'), wx.VERTICAL)
    
    sizer = wx.BoxSizer (wx.VERTICAL)
    sizer.Add (workers_sizer,        0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    sizer.Add (self.result_sizer,    1, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    self.SetSizerAndFit (sizer)
    
    self.add_schedule ( )
    
    self.SetupScrolling ( )
    
  def add_schedule (self):
    """
    Adds a new schedule result.
    """
    self.Freeze ( )
    self.number_results += 1
    
    
    self.results.append (result_gui_new.Result (self.proxy, self, wx.ID_ANY, name='Rezultat ' + str (self.number_results)))
    self.result_sizer.Add (self.results[-1], 1, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
    self.set_displayed (self.results[-1].GetLabel ( ))
    
    self.Thaw ( )
    self.Layout ( )
    self.ScrollChildIntoView (self.results[-1])
    
  def is_workers_shown (self):
    """
    Checks, if the workers panel is being displayed.
      @return: a boolean
    """
    return self.workers.IsShown ( )
  
  def toggle_workers (self, show):
    """
    Shows or hides the workers panel.
    """
    self.workers.Show (show)
    self.Layout ( )
    
  def get_results (self):
    """
    Returns a list of result names.
      @return: an ordered list of strings.
    """
    names = []
    for result in self.results:
      names.append (result.GetLabel ( ))
    return sorted (names)
  
  def get_displayed (self):
    """
    Returns the name of the displayed result.
      @return: a string
    """
    for result in self.results:
      if result.IsShown ( ):
        return result.GetLabel ( )
    return ''
  
  def set_displayed (self, name):
    """
    Set's the result, that will be displayed.
      @param name: a string
    """
    self.Freeze ( )
    for result in self.results:
      if result.GetLabel ( ) == name:
        result.Show ( )
        self.result_sizer.GetStaticBox ( ).SetLabel (result.GetLabel ( ))
      else:
        result.Hide ( )
    self.Layout ( )
    self.Thaw ( )
    
