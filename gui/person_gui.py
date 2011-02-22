# -*- coding: Cp1250 -*-

import wx
import wx.grid
import wx.calendar
import wx_extensions

import global_vars
from global_vars import turnuses, vacations, workplaces, titles, roles

class PersonPanel(wx.Panel):
  
  # if no person is selected
  INVALID_LABEL = "Izberite osebo za urejanje."
  

  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.person = None
    
    sizer = wx.BoxSizer(wx.VERTICAL)
    
    self.person_info = wx.StaticText(self, wx.NewId(), PersonPanel.INVALID_LABEL)
    sizer.Add(self.person_info, 0, wx.CENTER)
    
    sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
    sub_sizer.Add(wx.StaticText(self, wx.NewId(), "Vrsta zaposlitve: "), 0, wx.ALIGN_LEFT | wx.ALL)
    self.types = wx_extensions.LinkedComboBox(self, wx.NewId(), style=wx.CB_READONLY)
    self.Bind(wx.EVT_COMBOBOX, self.__update_employment_type, self.types)
    sub_sizer.Add(self.types, 0, wx.ALIGN_LEFT | wx.EXPAND)
    sizer.Add(sub_sizer, 0, wx.ALIGN_LEFT)
    
    self.permissions = PermissionsPanel(self)
    sizer.Add(self.permissions, 0, wx.ALIGN_LEFT)
    
    self.button = wx.Button(self, wx.NewId(), "Uredi ostalo")
    self.button.Disable()
    self.Bind(wx.EVT_BUTTON, self.__show_date_specific, self.button)
    sizer.Add(self.button, 0, wx.ALIGN_LEFT)
    
    self.SetSizerAndFit(sizer)
    
  def set_person(self, person):
    """
    Sets the person, that is represented by this panel.
      person: the person, that is represented
    """
    self.person = person
    
    if self.person:
      self.person_info.SetLabel(str(self.person))
      self.button.Enable()
    else:
      self.person_info.SetLabel(PersonPanel.INVALID_LABEL)
      self.button.Disable()
      
    self.permissions.set_unit(self.person)
    self.__set_choices ()  
      
  def __update_employment_type(self, event):
    """Event listener of the employment choices dropdown menu."""
    self.person.set_employment_type(self.types.get_selected_type())
    self.permissions.set_unit(self.person)
    
  def __show_date_specific (self, event):
    """Event listener of the button"""
    dialog = DateDialog(self.person, self, wx.NewId(), title=str(self.person))
    dialog.CenterOnScreen()
    dialog.ShowModal()
    
        
  def __set_choices(self):
    """Sets the employment choices in the dropdown menu"""
    self.types.set_selection(self.person)
    


class DateDialog(wx.Dialog):
  
  def __init__(self, person, *args, **kwargs):
    """
    The default constructor.
      person: the person, that this dialog will represent
    """
    
    wx.Dialog.__init__(self, *args, **kwargs)
    
    self.person = person
    
    sizer = wx.BoxSizer(wx.VERTICAL)
    
    self.calendar = wx_extensions.EnhancedCalendar(self, wx.NewId(), style=wx.calendar.CAL_MONDAY_FIRST | wx.calendar.CAL_SHOW_SURROUNDING_WEEKS | wx.calendar.CAL_SEQUENTIAL_MONTH_SELECTION)
    self.Bind(wx.calendar.EVT_CALENDAR_SEL_CHANGED, self.__update_date, self.calendar)
    sizer.Add(self.calendar, 1, wx.CENTER | wx.EXPAND)
    
    
    self.permissions = DatePermissionsPanel(person, self.__get_date(), self, wx.NewId())
    sizer.Add(self.permissions, 0, wx.ALIGN_LEFT)
    
    self.close = wx.Button(self, wx.ID_CLOSE)
    self.Bind(wx.EVT_BUTTON, self.__close, self.close)
    sizer.Add(self.close, 0, wx.ALIGN_RIGHT)
    
    self.SetSizerAndFit(sizer)
      
    self.permissions.set_unit(self.__get_date())
    
  def __close(self, event):
    """Closes the window."""
    self.Close()
      
  def __update_date(self, event):
    """Event listener of the calendar object"""
    self.permissions.set_unit(self.__get_date())
    
  def __get_date(self):
    """Reads the date from the calendar control and returns a python date object.
      return: a python date, as selected in the calendar control.
    """
    return self.calendar.PyGetDate ()
    
    

    
class PermissionsPanel(wx.Panel):
  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.person = None
    
    topSizer = wx.FlexGridSizer(cols=2)
    
    turnusSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), "Turnusi"), wx.VERTICAL)
    workplaceSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), "Delovišča"), wx.VERTICAL)
    titlesSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), "Nazivi"), wx.VERTICAL)
    specialCaseSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), "Ostalo"), wx.VERTICAL)
    
    #set the turnuses
    self.turnuses = []
    for turnus in turnuses.get_all ( ):
      self.turnuses.append(wx_extensions.LinkedCheckBox(turnus, self, wx.NewId(), str(turnus)))
      self.Bind(wx.EVT_CHECKBOX, self.__turnus_edited, self.turnuses[-1])
      turnusSizer.Add(self.turnuses[-1], 0, wx.ALIGN_LEFT)
      
    #set the workplaces
    self.workplaces = []
    for workplace in workplaces.get_all ( ):
      self.workplaces.append(wx_extensions.LinkedCheckBox(workplace, self, wx.NewId(), str(workplace)))
      self.Bind(wx.EVT_CHECKBOX, self.__workplace_edited, self.workplaces[-1])
      workplaceSizer.Add(self.workplaces[-1], 0, wx.ALIGN_LEFT)
        
    self.titles = TitlePanel (self, wx.NewId ())
    titlesSizer.Add(self.titles, 0, wx.ALIGN_LEFT)
      
        
    self.packet_night_turnuses = wx.CheckBox(self, wx.NewId(), label='Združuj nočne turnuse')
    self.Bind(wx.EVT_CHECKBOX, self.__packet_night_turnuses, self.packet_night_turnuses)
    specialCaseSizer.Add(self.packet_night_turnuses, 0, wx.ALIGN_LEFT)
    
    self.week_morning = wx.CheckBox(self,wx.NewId(), label = 'Dela samo med tednom dopoldne')
    self.Bind(wx.EVT_CHECKBOX, self.__week_morning, self.week_morning)
    specialCaseSizer.Add(self.week_morning, 0, wx.ALIGN_LEFT)
    
    self.roles = RolePanel (self, wx.NewId())
        
    #set the initial permissions  
    self.__set_permissions()
    
    topSizer.Add(turnusSizer, 0, wx.ALIGN_LEFT)
    topSizer.Add(titlesSizer, 0, wx.ALIGN_LEFT)
    topSizer.Add(workplaceSizer, 0, wx.ALIGN_LEFT)
    topSizer.Add(self.roles, 0, wx.ALIGN_LEFT)
    topSizer.Add(specialCaseSizer, 0 , wx.ALIGN_LEFT)
    
    self.SetSizerAndFit(topSizer)
    
  def set_unit(self, person):
    """
    Permissions are always edited on a person basis.
    This method sets the person.
      person: is the person, that will have their permission changed
    """
    

    self.person = person
    self.roles.set_unit(self.person)
    self.titles.set_unit(self.person)
    self.__set_permissions()
    
  def __turnus_edited(self, event):
    """The event listener for the turnus checkboxes."""
    if event.IsChecked():
      # remove the turnus from restrictions
      self.person.add_allowed_turnus (event.GetEventObject().element)
    else:
      # add the restriction
      self.person.remove_allowed_turnus(event.GetEventObject().element)
      
    # reload permissions
    self.__set_permissions()
    
    
  def __workplace_edited(self, event):
    """The event listener for the workplace checkboxes."""
    if event.IsChecked():
      # remove the workplace to the person
      self.person.add_workplace(event.GetEventObject().element)
    else:
      # add remove the workplace from the person
      self.person.remove_workplace(event.GetEventObject().element)
      
    # reload permissions - vacation to turnus sync
    self.__set_permissions()
    
    # refresh the role panel
    self.roles.refresh()
    
  def __title_edited(self, event):
    """The event listener for the title checkboxes."""
    if event.IsChecked():
      # add the title to the person
      self.person.add_title(event.GetEventObject().element)
    else:
      # remove the title from the person
      self.person.remove_title(event.GetEventObject().element)
    
    # reload parmissions  
    self.__set_permissions()
      
    
    
  def __packet_night_turnuses(self, event):
    """The event listener for the packet night turnuses check box"""
    self.person.packet_night_turnuses = event.IsChecked()
    self.__set_permissions()
    
  def __week_morning(self, event):
    """The event listener for the moring weekaday check box"""
    self.person.week_morning = event.IsChecked() 
    self.__set_permissions()
    
    
  def __set_permissions(self):
    """This method set's the initial permissions, according to the person attribute."""
    
    # edititing should not be possible
    if self.person == None:
      for turnus_checker in self.turnuses:
        turnus_checker.Disable()
      for workplace_checker in self.workplaces:
        workplace_checker.Disable()
      self.packet_night_turnuses.Disable()
      self.week_morning.Disable()
    else:
      for turnus_checker in self.turnuses:
        turnus_checker.Enable()
          
      for workplace_checker in self.workplaces:
        workplace_checker.Enable()
        
      self.packet_night_turnuses.Enable()
      self.packet_night_turnuses.SetValue(self.person.packet_night_turnuses)
      
      self.week_morning.Enable()
      self.week_morning.SetValue(self.person.week_morning)
        
      # select correct turnus permissons
      for turnus_checker in self.turnuses:
        if turnus_checker.element in self.person.get_allowed_turnuses():
          turnus_checker.SetValue(True)
        else:
          turnus_checker.SetValue(False)
          
          
      # set the correct workplace
      for workplace_checker in self.workplaces:
        if workplace_checker.element in self.person.workplaces:
          workplace_checker.SetValue(True)
        else:
          workplace_checker.SetValue(False)

class TitlePanel (wx.Panel):
  
  class MyTextDropTarget(wx.TextDropTarget):
    def __init__(self, object):
      wx.TextDropTarget.__init__(self)
      self.object = object

    def OnDropText(self, x, y, data):
      index, flag = self.object.HitTest (wx.Point(x,y))
      if flag == wx.LIST_HITTEST_NOWHERE:
        self.object.InsertStringItem(self.object.GetItemCount(), data)
      else:
        self.object.InsertStringItem(index, data)
  
  def __init__ (self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.person = None
    
    sizer = wx.BoxSizer(wx.VERTICAL)
    
    self.all_titles = wx.ListCtrl (self, wx.NewId(), style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_NO_HEADER | wx.LC_HRULES)
    self.all_titles.InsertColumn (0,'')
    for i, title in enumerate (global_vars.titles.get_all ( )):
      self.all_titles.InsertStringItem(i, unicode (title))
    self.all_titles.SetColumnWidth(0, wx.LIST_AUTOSIZE)
      
    
    self.person_titles = wx.ListCtrl (self, wx.NewId(), style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_NO_HEADER | wx.LC_HRULES)
    self.person_titles.InsertColumn (0,'')
    dt = TitlePanel.MyTextDropTarget(self.person_titles)
    self.person_titles.SetDropTarget(dt)
    self.person_titles.SetColumnWidth(0, wx.LIST_AUTOSIZE)
    self.Bind(wx.EVT_LIST_BEGIN_DRAG, self.InsertDrag, self.all_titles)
    self.Bind(wx.EVT_LIST_BEGIN_DRAG, self.OrderDrag,  self.person_titles)
    
    self.__set_permissions ( )
    
    sizer.Add (self.all_titles)
    sizer.Add (self.person_titles)
    
    self.SetSizerAndFit (sizer)
    
  def InsertDrag(self, event):
    text = self.all_titles.GetItemText(event.GetIndex())
    tdo = wx.TextDataObject(text)
    tds = wx.DropSource(self.person_titles)
    tds.SetData(tdo)
    tds.DoDragDrop(True)
    
    self.__set_titles()
    
  def OrderDrag(self, event):
    text = self.person_titles.GetItemText(event.GetIndex())
    
    if text != unicode (self.person):
      self.person_titles.DeleteItem(event.GetIndex())
      
      tdo = wx.TextDataObject(text)
      tds = wx.DropSource(self.person_titles)
      tds.SetData(tdo)
      tds.DoDragDrop(True)
      
      self.__set_titles()
    
  def set_unit(self, person):
    """
    Titles are always set on a person basis. This method sets the person.
      person: is the person for which the permissions will be edited.
    """
    self.person_titles.DeleteAllItems ( )
    self.person = person
    self.__set_permissions()
    
  def __set_titles (self):
    """
    Sets the persons titles, as defined in the person_titles field.
    """
    #TODO: add the appropriate method into the container
    from Scheduler.data.title import Title
    prefixes = []
    suffixes = []
    i = 0
    
    while i < self.person_titles.GetItemCount ( ):
      if self.person_titles.GetItemText (i) == unicode (self.person):
        break
      prefixes.append(Title (self.person_titles.GetItemText (i)))
      i += 1
      
    i += 1 # skip the person
    
    while i < self.person_titles.GetItemCount ( ):
      suffixes.append(Title (self.person_titles.GetItemText (i)))
      i += 1
      
    self.person.set_titles (prefixes, suffixes)
    self.__set_permissions ( )

    
  def __set_permissions (self):
    """Set's the correct permissions."""
    self.person_titles.DeleteAllItems()
    if self.person:
      self.all_titles.Enable()
      self.person_titles.Enable()
      
      i = -1
      prefixes, suffixes = self.person.get_titles ( )
      
      if prefixes:
        for i, title in enumerate (prefixes):
          self.person_titles.InsertStringItem (i, unicode (title))
      
      i += 1    
      self.person_titles.InsertStringItem(i, unicode (self.person))
      item = self.person_titles.GetItem(i)
      item.SetTextColour(wx.BLUE)
      self.person_titles.SetItem(item)
      
      if suffixes:
        for i, title in enumerate (suffixes):
          self.person_titles.InsertStringItem (i + 1 + len (prefixes), unicode (title))
          
      self.person_titles.SetColumnWidth(0, wx.LIST_AUTOSIZE)
      
    else:
      self.person_titles.Disable()
      self.all_titles.Disable()
      
    
          
class RolePanel (wx.Panel):
  
  def __init__(self, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.person = None
    
    rolesSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), "Vloge"), wx.VERTICAL)
    
    self.workplaces = wx_extensions.LinkedChoice (workplaces.get_all ( ), self, wx.NewId())
    self.Bind(wx.EVT_CHOICE, self.__workplace_selected, self.workplaces)
    rolesSizer.Add(self.workplaces, 0, wx.ALIGN_LEFT)
    
    self.roles = []
    for role in roles.get_all ( ):
      self.roles.append(wx_extensions.LinkedCheckBox(role, self, wx.NewId(), str(role)))
      self.Bind(wx.EVT_CHECKBOX, self.__role_edited, self.roles[-1])
      rolesSizer.Add(self.roles[-1], 0, wx.ALIGN_LEFT)
      
    self.SetSizerAndFit(rolesSizer)
      
    self.__set_permissions()
      
  def set_unit(self, person):
    """Sets the person for which the roles will be edited"""
    if person:
      self.person = person
      self.workplaces.set_elements (sorted (self.person.workplaces))
    else:
      self.person = None
      self.workplaces.set_elements([])
      
    self.__set_permissions()
    
  def refresh(self):
    """Redraws the whole panel"""
    self.set_unit(self.person)
      
  def __role_edited(self, event):
    """The event listener for the roles checkboxes."""
    if event.IsChecked():
      # add the role
      self.person.add_role (self.workplaces.get_value(), event.GetEventObject().element)
    else:
      # remove the role
      self.person.remove_role (self.workplaces.get_value(), event.GetEventObject().element)
      
    # reload permissions
    self.__set_permissions()
    
  def __workplace_selected(self, event):
    """The event listener for the workplaces drop-down."""
    self.__set_permissions()
    
  def __set_permissions(self):
    """Keeps the GUI in sync with the data"""
    if not self.person:
      self.workplaces.Disable()
      for role in self.roles:
        role.SetValue(False)
        role.Disable()
    else:
      try:
        self.workplaces.Enable()
        workplace = self.workplaces.get_value()
        roles = self.person.roles[workplace]
        for role_checker in self.roles:
          if role_checker.element in workplace.roles:
            role_checker.Enable()
            role_checker.SetValue(role_checker.element in roles)
          else:
            role_checker.SetValue(False)
            role_checker.Disable()
      except:
        self.workplaces.Disable()
        for role in self.roles:
          role.SetValue(False)
          role.Disable()
        
    
      
    
    
class DatePermissionsPanel(wx.Panel):
  def __init__(self, person, date, *args, **kwargs):
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.person = person
    self.date = date
    
    topSizer = wx.BoxSizer(wx.HORIZONTAL)
    
    turnusSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), "Dovoljeni turnusi"), wx.VERTICAL)
    preScheduleSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), "Vnaprej doloci"), wx.VERTICAL)
    vacationSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), "Dopusti"), wx.VERTICAL)

    
    #set the turnuses
    self.turnuses = []
    for turnus in person.allowed_turnuses:
      self.turnuses.append(wx_extensions.LinkedCheckBox(turnus, self, wx.NewId(), str(turnus)))
      self.Bind(wx.EVT_CHECKBOX, self.__turnus_edited, self.turnuses[-1])
      turnusSizer.Add(self.turnuses[-1], 0, wx.ALIGN_LEFT)
      
    #set the preschedule options
    self.workplaces = wx_extensions.LinkedChoice(person.workplaces, self, wx.NewId())
    self.Bind(wx.EVT_CHOICE, self.__workplace_changed, self.workplaces)
    preScheduleSizer.Add(self.workplaces, 0, wx.CENTER)
    
    self.roles = wx_extensions.LinkedChoice([], self, wx.NewId())
    self.Bind(wx.EVT_CHOICE, self.__set_permissions_wrapper, self.roles)
    preScheduleSizer.Add(self.roles, 0, wx.CENTER) 
    
    self.pre_turnuses = []
    for turnus in self.person.allowed_turnuses:
      self.pre_turnuses.append(wx_extensions.LinkedCheckBox(turnus, self, wx.NewId(), str(turnus)))
      self.Bind(wx.EVT_CHECKBOX, self.__predefined_edited, self.pre_turnuses[-1])
      preScheduleSizer.Add(self.pre_turnuses[-1], 0, wx.ALIGN_LEFT) 
      
    
    

    #set the vacations
    self.vacations = []
    for vacation in vacations.get_all ( ):
      self.vacations.append(wx_extensions.LinkedCheckBox(vacation, self, wx.NewId(), str(vacation)))
      self.Bind(wx.EVT_CHECKBOX, self.__vacation_edited, self.vacations[-1])
      vacationSizer.Add(self.vacations[-1], 0, wx.ALIGN_LEFT)
      
          
    
    # set the initial permissions  
    self.__set_permissions()
    # set the initial roles
    self.__workplace_changed(None)
    
    topSizer.Add(turnusSizer, 0, wx.ALIGN_RIGHT)
    topSizer.Add(preScheduleSizer, 0, wx.ALIGN_RIGHT)
    topSizer.Add(vacationSizer, 0, wx.ALIGN_RIGHT)
    
    self.SetSizerAndFit(topSizer)
    
  def set_unit(self, date):
    """
    Permissions are always edited on a person + date basis.
    This method sets the date (person is constant for the whole dialog).
      date: is the date for which the permissions apply
    """
    
    # either both are valid or both are invalid
    # it would work otherwise, but this keeps the internal state consistent
    if self.person and date:
      self.date = date
    else:
      self.date = None
    
    self.__set_permissions()
    
    
  def __turnus_edited(self, event):
    """The event listener for the turnus checkboxes."""
    if event.IsChecked():
      # remove the turnus from restrictions
      self.person.remove_invalid_turnus(self.date, event.GetEventObject().element)
    else:
      # add the restriction
      self.person.add_invalid_turnus(self.date, event.GetEventObject().element)
      
    # reload permissions - vacation to turnus sync
    self.__set_permissions()
    
  def __vacation_edited(self, event):
    """The event listener for the vacation checkboxes."""
    if event.IsChecked():
      # remove the turnus from restrictions
      self.person.add_vacation(self.date, event.GetEventObject().element)
    else:
      # add the restriction
      self.person.remove_vacation(self.date, event.GetEventObject().element)
      
    # reload permissions - vacation to turnus sync
    self.__set_permissions()
    
  def __predefined_edited(self, event):
    """The event listener for the predefined checkboxes."""
    if event.IsChecked():
      # overwrite any existing schedule
      self.person.add_predefined(self.date, event.GetEventObject().element, self.workplaces.get_value(), self.roles.get_value())
    else:
      # remove the prescheduled
      self.person.remove_predefined(self.date)
      
    # reload permissions - synchronizes everything
    self.__set_permissions()
    
  def __workplace_changed(self, event):
    """Event listener for the workplace choice"""
    
    self.roles.set_elements(self.workplaces.get_value().roles & self.person.roles[self.workplaces.get_value()])
    self.__set_permissions()
    
  def __set_permissions_wrapper(self, event):
    """Just wraps an event listener around the set permissions method."""
    self.__set_permissions()
    
  def __set_permissions(self):
    """This method set's the initial permissions, according to the person and date attributes."""
    
    # edititing should not be possible
    if self.person == None or self.date == None:
      for turnus_checker in self.turnuses:
        turnus_checker.Disable()
      for vacation_checker in self.vacations:
        vacation_checker.Disable()
      self.workplaces.Disable()
      self.roles.set_elements([])
      self.roles.Disable()
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
          
      # disable / enable the correct turnuses for prescheduling
      roles = self.workplaces.get_value().roles & self.person.roles[self.workplaces.get_value()]
      if roles:
        self.roles.Enable()
        allowed_turnuses = set()
        for turnus in self.workplaces.get_value().allowed_turnuses & self.person.allowed_turnuses:
          if not self.person.is_turnus_forbidden(turnus, self.date):
            allowed_turnuses.add(turnus)
          
        # set the permissions
        for turnus_checker in self.pre_turnuses:
          if turnus_checker.element in allowed_turnuses:
            turnus_checker.Enable()
            if self.person.is_predefined(self.date):
              turnus_checker.SetValue(self.person.predefined[self.date][0] == turnus_checker.element and self.person.predefined[self.date][1] == self.workplaces.get_value() and self.person.predefined[self.date][2] == self.roles.get_value())
            else:
              turnus_checker.SetValue(False)
          else:
            turnus_checker.SetValue(False)
            turnus_checker.Disable()
      else:
        self.roles.Disable()
        for turnus_checker in self.pre_turnuses:
          turnus_checker.SetValue (False)
          turnus_checker.Disable()
      
          
          
      
    
