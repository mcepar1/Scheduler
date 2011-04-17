# -*- coding: Cp1250 -*-

"""
This file contains a class, that handles a month's schedule. 
"""
import result_gui
import workers_gui


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

    self.workers = workers_gui.WorkersPanel (self.proxy, self, wx.ID_NEW)
    
    workers_sizer = wx.StaticBoxSizer (wx.StaticBox (self, wx.ID_ANY, ''), wx.VERTICAL)
    workers_sizer.Add (self.workers, 1, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
    self.result_sizer = wx.StaticBoxSizer (wx.StaticBox (self, wx.ID_ANY, 'Rezultat'), wx.VERTICAL)
    
    sizer = wx.BoxSizer (wx.VERTICAL)
    sizer.Add (workers_sizer,        0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    sizer.Add (self.result_sizer,    1, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    self.SetSizerAndFit (sizer)
    
    self.add_schedule ( )
    self.synchronize_workers ( )
    
    self.SetupScrolling ( )
    
  def add_schedule (self):
    """
    Adds a new schedule result.
    """
    self.Freeze ( )
    self.number_results += 1
    
    
    self.results.append (result_gui.Result (self.proxy, self, wx.ID_ANY, name='Rezultat ' + str (self.number_results)))
    self.result_sizer.Add (self.results[-1], 1, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
    self.set_displayed (self.results[-1].GetLabel ( ))
    
    self.Thaw ( )
    self.Layout ( )
    self.ScrollChildIntoView (self.results[-1])
    
  def start_scheduling (self):
    """
    Starts to schedule the displayed schedule.
    """
    self.Freeze ( )
    
    for result in self.results:
      if result.IsShown ( ):
        result.start ( )
        break
      
    self.Thaw ( )
    
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
    
  def toggle_view (self, compact):
    """
    Sets the type of the view, that will be displayed.
      @param compact: a boolean that defines the view. Compact view if True, full view if False.
    """
    self.__get_displayed ( ).toggle_view (compact)
    
  def is_compact (self):
    """
    Checks, if this container is set to the compact view mode.
      @return: True, if it compact, False otherwise.
    """
    return self.__get_displayed ( ).is_compact ( )
  
  def set_span (self, full):
    """
    Sets the date range of the view. Span can be set to full (the neighbouring months) or normal (only the
    main scheduling month).
      @param full: a boolean that sets the span. True if full span, False otherwise. 
    """
    self.__get_displayed ( ).set_span (full)
    
  def is_full_span (self):
    """
    Checks, if this container is set to the full span view mode.
      @return: True, if it is full, False otherwise.
    """
    return self.__get_displayed ( ).is_full_span ( )
    
  def synchronize_workers (self, show_workers=True):
    """
    Returns the displayed result's proxy object.
      @return: a proxy object
    """
    result = self.__get_displayed ( )
    if result:
      self.workers.rebuild (result.get_proxy ( ))
      self.toggle_workers (True)
    
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
    result = self.__get_displayed ( )
    if result:
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
    self.synchronize_workers ( )
    self.Thaw ( )
    
  def save (self):
    """
    Saves the displayed result.
    """
    self.__get_displayed ( ).save ( )
        
  def __get_displayed (self):
    """
    Returns the displayed result, None if no result is displayed.
    """
    for result in self.results:
      if result.IsShown ( ):
        return result
    return None
    
