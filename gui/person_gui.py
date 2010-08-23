# -*- coding: utf-8 -*-

import wx
import wx.grid
import wx.calendar
import wx_extensions

import datetime

from global_vars import turnuses, vacations

class PersonPanel(wx.Panel):

  # if no person is selected
  INVALID_LABEL = "Izberite osebo za urejanje."

  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.person = None
    
    sizer = wx.BoxSizer(wx.VERTICAL)
    
    self.person_info = wx.StaticText(self,wx.NewId(),PersonPanel.INVALID_LABEL)
    sizer.Add(self.person_info,0,wx.CENTER)
    
    sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
    sub_sizer.Add(wx.StaticText(self,wx.NewId(),"Vrsta zaposlitve: "), 0, wx.ALIGN_LEFT|wx.ALL)
    self.types = wx_extensions.LinkedComboBox(self, wx.NewId(),style = wx.CB_READONLY)
    self.Bind(wx.EVT_COMBOBOX, self.__update_employment_type, self.types)
    sub_sizer.Add(self.types,0,wx.CENTER|wx.SHAPED|wx.CB_READONLY)
    sizer.Add(sub_sizer,0,wx.ALIGN_LEFT)
    
    self.calendar = wx_extensions.EnhancedCalendar(self, wx.NewId(), style = wx.calendar.CAL_MONDAY_FIRST | wx.calendar.CAL_SHOW_HOLIDAYS)
    self.Bind(wx.calendar.EVT_CALENDAR_SEL_CHANGED, self.__update_date, self.calendar)
    sizer.Add(self.calendar,1,wx.CENTER | wx.EXPAND)
    
    
    self.permissions = PermissionsPanel(self)
    sizer.Add(self.permissions,0, wx.ALIGN_LEFT)
    
    self.SetSizerAndFit(sizer)
    
  def set_person(self,person):
    """
    Sets the person, that is represnted by this panel.
      person: the person, that is represented
    """
    self.person = person
    
    if self.person:
      self.person_info.SetLabel(str(self.person))
    else:
      self.person_info.SetLabel(PersonPanel.INVALID_LABEL)
      
    self.permissions.set_unit(self.person, self.__get_date())
    self.__set_choices ( )  
      
  def __update_date(self,event):
    """Event listener of the calendar object"""
    self.permissions.set_unit(self.person, self.__get_date())
    
  def __update_employment_type(self, event):
    """Event listener of the emplment choices dropdown menu."""
    self.person.set_employment_type(self.types.get_selected_type())
    self.permissions.set_unit(self.person, self.__get_date())
    
  def __get_date(self):
    """Reads the date from the calendar control and returns a python date object.
      return: a python date, as selected in the calendar control.
    """
    return self.calendar.GetDateObject ( )
    
  def __set_choices(self):
    """Sets the emplyment choices in the dropdown menu"""
    self.types.set_selection(self.person)
      
      
    
class PermissionsPanel(wx.Panel):
  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.person = None
    self.date = None
    
    topSizer = wx.BoxSizer(wx.HORIZONTAL)
    
    turnusSizer = wx.StaticBoxSizer(wx.StaticBox(self,wx.NewId(),"Turnusi"),wx.VERTICAL)
    vacationSizer = wx.StaticBoxSizer(wx.StaticBox(self,wx.NewId(),"Dopusti"), wx.VERTICAL)
    
    #set the turnuses
    self.turnuses = []
    for turnus in turnuses.turnuses:
      self.turnuses.append(wx_extensions.LinkedCheckBox(turnus,self,wx.NewId(),str(turnus)))
      self.Bind(wx.EVT_CHECKBOX, self.__turnus_edited, self.turnuses[-1])
      turnusSizer.Add(self.turnuses[-1],0,wx.ALIGN_LEFT)
    

    #set the vacations
    self.vacations = []
    for vacation in vacations.vacations:
      self.vacations.append(wx_extensions.LinkedCheckBox(vacation,self,wx.NewId(),str(vacation)))
      self.Bind(wx.EVT_CHECKBOX, self.__vacation_edited, self.vacations[-1])
      vacationSizer.Add(self.vacations[-1],0,wx.ALIGN_LEFT)
    
    #set the initial permissions  
    self.__set_permissions()
    
    topSizer.Add(turnusSizer,0,wx.ALIGN_RIGHT)
    topSizer.Add(vacationSizer,0,wx.ALIGN_RIGHT)
    
    self.SetSizerAndFit(topSizer)
    
  def set_unit(self, person, date):
    """
    Permissions are always edited on a person + date basis.
    This method sets the person and date.
      person: is the person, that will have their permission changed
      date: is the date for which the permissions apply
    """
    
    # either both are valid or both are invalid
    # it would work otherwise, but this keeps the internal state consistent
    if person and date:
      self.person = person
      self.date = date
    else:
      self.person = None
      self.date = None
    
    self.__set_permissions()
    
  def __turnus_edited(self,event):
    """The event listener for the turnus checkboxes."""
    if event.IsChecked():
      # remove the turnus from restrictions
      self.person.remove_invalid_turnus(self.date,event.GetEventObject().element)
    else:
      # add the restriction
      self.person.add_invalid_turnus(self.date,event.GetEventObject().element)
      
    # reload permissions - vacation to turnus sync
    self.__set_permissions()
    
  def __vacation_edited(self,event):
    """The event listener for the vacation checkboxes."""
    if event.IsChecked():
      # remove the turnus from restrictions
      self.person.add_vacation(self.date,event.GetEventObject().element)
    else:
      # add the restriction
      self.person.remove_vacation(self.date,event.GetEventObject().element)
      
    # reload permissions - vacation to turnus sync
    self.__set_permissions()
    
  def __set_permissions(self):
    """This method set's the initial permissions, according to the person and date attributes."""
    
    # edititing should not be possible
    if self.person == None or self.date == None:
      for turnus_checker in self.turnuses:
        turnus_checker.Disable()
      for vacation_checker in self.vacations:
        vacation_checker.Disable()
    else:
      for turnus_checker in self.turnuses:
        if turnus_checker.element in self.person.get_allowed_turnuses():
          turnus_checker.Enable()
        else:
          turnus_checker.Disable()
          
      for vacation_checker in self.vacations:
        vacation_checker.Enable()
        
      # select correct turnus permissons
      if self.date in self.person.forbidden_turnuses:
        turnuses = self.person.forbidden_turnuses[self.date]
        for turnus_checker in self.turnuses:
          if turnus_checker.element in turnuses:
            turnus_checker.SetValue(False)
          else:
            turnus_checker.SetValue(True)
      else:
        for turnus_checker in self.turnuses:
          turnus_checker.SetValue(True)
      
      # set the correct vacation permissions    
      if self.date in self.person.vacations:
        vacations = self.person.vacations[self.date]
        for vacation_checker in self.vacations:
          if vacation_checker.element in vacations:
            vacation_checker.SetValue(True)
          else:
            vacation_checker.SetValue(False)
      else:
        for vacation_checker in self.vacations:
          vacation_checker.SetValue(False)
      
    
