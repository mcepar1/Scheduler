# -*- coding: Cp1250 -*-

import wx

import global_vars
from common import GenericTablePanel

from scheduler_gui import SchedulerPanel
from turnus_gui import TurnusPanel
from nurse_gui import NursePanel
from workplace_gui import WorkplacePanel

class MainWindow(wx.Frame):

  TITLE = "Urnik"
  PARENT = None

  def __init__(self):
    wx.Frame.__init__(self, MainWindow.PARENT, title = MainWindow.TITLE, style = wx.DEFAULT_FRAME_STYLE)
    
    self.sizer = wx.BoxSizer(wx.VERTICAL)
    
    notebook = wx.Notebook(self)
    notebook.AddPage(SchedulerPanel(notebook), "Urnik")
    notebook.AddPage(NursePanel(notebook), "Medicinske sestre")
    #notebook.AddPage(DoctorPanel(notebook), "Zdravniki")
    notebook.AddPage(GenericTablePanel(global_vars.employment_types, notebook), "Vrste zaposlitve")
    notebook.AddPage(TurnusPanel(notebook), "Turnusi")
    notebook.AddPage(GenericTablePanel(global_vars.vacations, notebook), "Dopusti")
    notebook.AddPage(WorkplacePanel(notebook), "Delovišča")
    notebook.AddPage(GenericTablePanel(global_vars.titles, notebook), "Nazivi")
    notebook.AddPage(GenericTablePanel(global_vars.turnus_types, notebook), "Vrste turnusov")
    notebook.AddPage(GenericTablePanel(global_vars.roles, notebook), 'Vloge')
    
    self.sizer.Add(notebook,1,wx.ALIGN_LEFT | wx.EXPAND)
    
    panel = MainButtons(self)
    self.sizer.Add(panel,0,wx.ALIGN_RIGHT | wx.BOTTOM)
    
    self.SetSizer(self.sizer)
    self.SetAutoLayout(1)
    self.sizer.Fit(self)
    
    self.Show()
    
        
class MainButtons(wx.Panel):
  
  def __init__(self, *args, **kwargs):
    
    wx.Panel.__init__(self, *args, **kwargs)
        
    sizer = wx.BoxSizer(wx.VERTICAL)
        
    self.button = wx.Button(self, wx.NewId(), "Shrani")
    sizer.Add(self.button,0,wx.ALIGN_RIGHT)
    self.Bind(wx.EVT_BUTTON,self.save_all,self.button)
       
    self.SetSizerAndFit(sizer)
    
  def save_all(self,event):
    #TODO: this is used only for testing
    #TODO: remove or change in a final release
    global_vars.save()
   
    
