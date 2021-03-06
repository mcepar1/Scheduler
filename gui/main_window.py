# -*- coding: Cp1250 -*-

import wx
import os

import get_panels
import utils_gui
from scheduler_gui import SchedulesPanel



class MainWindow(wx.Frame):

  TITLE     = 'Urnik'
  PARENT    = None
  ICON_PATH = os.path.join ('persistence', 'gui', 'clock.png')

  def __init__(self,
               vacations, 
               titles, 
               turnus_types, 
               roles, 
               turnuses, 
               workplaces,
               scheduling_units,
               employment_types, 
               nurses):
    wx.Frame.__init__(self, MainWindow.PARENT, title = MainWindow.TITLE, style = wx.DEFAULT_FRAME_STYLE)
    
    
    notebook = wx.Notebook(self)
    notebook.AddPage(SchedulesPanel (workplaces, roles, turnus_types, notebook, wx.ID_ANY), "Razporedi")
    notebook.AddPage(get_panels.get_nurse_panel (nurses, notebook), "Medicinske sestre")
    notebook.AddPage(get_panels.get_employment_type_panel (employment_types, notebook), "Vrste zaposlitve")
    notebook.AddPage(get_panels.get_turnus_panel (turnuses, notebook), "Turnusi")
    notebook.AddPage(get_panels.get_vacation_panel (vacations, notebook), "Dopusti")
    notebook.AddPage(get_panels.get_scheduling_unit_panel (scheduling_units, notebook), "Delovi��a - vloge")
    notebook.AddPage(get_panels.get_workplace_panel (workplaces, notebook), "Delovi��a")
    notebook.AddPage(get_panels.get_simple_panel (titles, notebook), "Nazivi")
    notebook.AddPage(get_panels.get_simple_panel (turnus_types, notebook), "Vrste turnusov")
    notebook.AddPage(get_panels.get_simple_panel (roles, notebook), 'Vloge')
    
    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(notebook,1,wx.ALIGN_LEFT | wx.EXPAND)
    
    self.SetSizerAndFit (sizer)
    self.SetMinSize ((100,100))
    self.SetIcon(utils_gui.make_icon(wx.Image(name = MainWindow.ICON_PATH)))
  
class SplashScreen(wx.Frame):
  SPLASH_PATH = os.path.join ('persistence', 'gui', 'splash.png')
  ICON_PATH   = os.path.join ('persistence', 'gui', 'clock.png')
  
  def __init__(self):
    wx.Frame.__init__(self, None, title = MainWindow.TITLE, style = wx.NO_BORDER)
    
    aBitmap = wx.Image(name = SplashScreen.SPLASH_PATH).ConvertToBitmap()
    
    sizer = wx.BoxSizer(wx.VERTICAL)
    
    pic                = wx.StaticBitmap(self, wx.ID_ANY, aBitmap)
    self.text          = wx.StaticText(self, wx.ID_ANY, size = (pic.GetSize()[0], -1), style = wx.ST_NO_AUTORESIZE)
    self.progress      = wx.Gauge(self, wx.ID_ANY)
    
    sizer.Add (pic,           1, wx.ALIGN_TOP    | wx.ALIGN_LEFT | wx.SHAPED)
    sizer.Add (self.text,     0, wx.ALIGN_BOTTOM | wx.ALIGN_LEFT | wx.EXPAND)
    sizer.Add (self.progress, 0, wx.ALIGN_BOTTOM | wx.ALIGN_LEFT | wx.EXPAND)
    
    self.text.SetFont(wx.Font(20, wx.FONTFAMILY_SCRIPT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
    
    self.SetIcon(utils_gui.make_icon(wx.Image(name = SplashScreen.ICON_PATH)))
    self.SetSizerAndFit (sizer)
    self.CenterOnScreen ( )
    self.Show ( )
    
  
    wx.Yield ( )  
    import data
    self.__application_loaded(*data.load(self))
    
  def send_message (self, text, percent):
    self.text.SetLabel (text)
    self.progress.SetValue(percent)
    
  def __application_loaded(self, *args):
    import global_vars
    inv = [global_vars.set_vacations, 
           global_vars.set_titles, 
           global_vars.set_turnus_types,
           global_vars.set_roles,
           global_vars.set_turnuses,
           global_vars.set_workplaces,
           global_vars.set_scheduling_units,
           global_vars.set_employment_types,
           global_vars.set_nurses]
    
    for i, method in enumerate (inv):
      method (args[i])
    
    frame = MainWindow (*args)
    self.Hide ( )
    frame.Show(True)
    wx.GetApp ( ).SetTopWindow(frame)
    self.Destroy ( )
