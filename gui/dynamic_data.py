# -*- coding: Cp1250 -*-
"""
This file contains classes for editing the object's dynamic data.
"""
import wx
import wx_extensions
import wx.lib.intctrl
import wx.lib.expando
import wx.lib.ticker
import custom_events

import locale

import global_vars


"""
This class is responsible for editing the nurse's dynamic data.
"""
class EditNursePanel(wx.Panel):
  
  def __init__(self, *args, **kwargs):
    """
    The default constructor.
    """
    from data.nurse import Nurse
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.person = None
    
    self.header             = HeaderNursePanel       (self, wx.ID_ANY)
    self.title_selector     = TitlePanel             (global_vars.get_titles ( ), self, wx.ID_ANY)
    self.turnus_checkers    = CheckerPanel           ('Turnusi',   global_vars.get_turnuses ( ), Nurse.is_turnus_allowed, Nurse.add_allowed_turnus, Nurse.remove_allowed_turnus, self, wx.ID_ANY)
    self.workplace_checkers = CheckerPanel           ('Delovišča', global_vars.get_workplaces ( ), Nurse.is_workplace_allowed, Nurse.add_workplace, Nurse.remove_workplace,      self, wx.ID_ANY)
    self.role_selector      = RolePanel              (global_vars.get_roles ( ), self, wx.ID_ANY)
    self.special_properties = SpecialNurseProperties (self, wx.ID_ANY)
    #TODO: remove this!
    self.rest_button        = wx.Button              (self, wx.ID_ANY, 'Vezano na datum')
    
    self.Bind(custom_events.EVT_UPDATED, self.__workplaces_to_roles, self.workplace_checkers)
    self.Bind (wx.EVT_BUTTON, self.__obsolete, self.rest_button)
    
    grid_sizer = wx.FlexGridSizer (cols=2)
    grid_sizer.Add (self.title_selector,     0, wx.ALIGN_LEFT | wx.ALIGN_TOP | wx.EXPAND)
    grid_sizer.Add (self.turnus_checkers,    0, wx.ALIGN_LEFT | wx.ALIGN_TOP | wx.EXPAND)
    grid_sizer.Add (self.workplace_checkers, 0, wx.ALIGN_LEFT | wx.ALIGN_TOP | wx.EXPAND)
    grid_sizer.Add (self.role_selector,      0, wx.ALIGN_LEFT | wx.ALIGN_TOP | wx.EXPAND)
    grid_sizer.Add (self.special_properties, 0, wx.ALIGN_LEFT | wx.ALIGN_TOP | wx.EXPAND)
    grid_sizer.Add (self.rest_button,        0, wx.ALIGN_LEFT | wx.ALIGN_TOP | wx.EXPAND)
    
    
    sizer = wx.BoxSizer (wx.VERTICAL)
    sizer.Add (self.header, 0, wx.EXPAND)
    sizer.Add (grid_sizer,  1, wx.ALIGN_LEFT | wx.EXPAND)
    
    
    self.SetSizerAndFit(sizer)
    
  def __obsolete(self,event):
    dialog = DateDialog(self.person, self, wx.NewId(), title=str(self.person))
    dialog.CenterOnScreen()
    dialog.ShowModal()
    
    
  def set_unit(self, person):
    """
    Sets the person, that is represented by this panel.
      person: the person, that is represented
    """
    self.person = person
    
    self.header.set_unit             (self.person)
    self.turnus_checkers.set_unit    (self.person)
    self.title_selector.set_unit     (self.person)
    self.workplace_checkers.set_unit (self.person)
    self.role_selector.set_unit      (self.person)
    self.special_properties.set_unit (self.person) 
    
  def __workplaces_to_roles(self, event):
    """
    Keeps the workplace drop down of the RolePanel in sync with the workplace checkers. 
    """
    self.set_unit(self.person)

"""
This class is responsible for editing the turunes' dynamic data.
"""    
class EditTurnusPanel (wx.Panel):
  
  def __init__(self, *args, **kwargs):
    """
    The default constructor.
    """
    # did not simply extend the CheckerPanel, because it would corrupt the layout
    from data.turnus import Turnus
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.turnus = None
    
    self.turnus_type_checkers = CheckerPanel ('Vrste turnusov', global_vars.get_turnus_types ( ), Turnus.has_type, Turnus.add_type, Turnus.remove_type, self, wx.ID_ANY)
    
    sizer = wx.BoxSizer (wx.VERTICAL)
    sizer.Add(self.turnus_type_checkers, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
    self.SetSizerAndFit (sizer)
    
  def set_unit (self, turnus):
    """
    Sets the turnus, represented by this panel.
      turnus: a data turnus object
    """
    self.turnus = turnus
    
    self.turnus_type_checkers.set_unit (self.turnus)

"""
This class is responsible for editing the workplace data.
"""
class EditWorkplacePanel (wx.Panel):
  
  def __init__(self, *args, **kwargs):
    """
    The default constructor
    """
    from data.workplace import Workplace
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.workplace = None
    
    self.turnus_checkers = CheckerPanel ('Turnusi', global_vars.get_turnuses ( ), Workplace.is_allowed_turnus, Workplace.add_allowed_turnus, Workplace.remove_allowed_turnus, self, wx.ID_ANY)
    self.role_checkers   = CheckerPanel ('Vloge',   global_vars.get_roles ( ), Workplace.has_role, Workplace.add_role, Workplace.remove_role,                                  self, wx.ID_ANY)
    
    sizer = wx.BoxSizer (wx.VERTICAL)
    sizer.Add (self.turnus_checkers, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    sizer.Add (self.role_checkers,   0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
    self.SetSizerAndFit (sizer)
    
  def set_unit(self, workplace):
    """
    Sets the workplace, represented by this panel.
      workplace: a workplace data object
    """
    self.workplace = workplace
    
    self.turnus_checkers.set_unit (self.workplace)
    self.role_checkers.set_unit   (self.workplace)
    
"""
This class is responsible for editing employment type data.
"""
class EditEmploymentTypePanel (wx.Panel):
  
  def __init__(self, *args, **kwargs):
    """
    The default constructor.
    """
    wx.Panel.__init__ (self, *args, **kwargs)
    
    self.employment_type = None
    
    self.monthly_hours = wx.lib.intctrl.IntCtrl (self, wx.ID_ANY)
    self.comment_text  = wx.lib.expando.ExpandoTextCtrl (self, wx.ID_ANY)
    
    self.monthly_hours.SetMin (0)
    self.monthly_hours.SetLimited (True)
    
    self.Bind(wx.lib.intctrl.EVT_INT, self.__hours_changed, self.monthly_hours)
    self.Bind(wx.EVT_TEXT, self.__commented, self.comment_text)
    
    
    sizer_hours   = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, 'Število ur v mesecu'), wx.VERTICAL)
    sizer_hours.Add (self.monthly_hours, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
    sizer_comment = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, 'Komentar'), wx.VERTICAL)
    sizer_comment.Add (self.comment_text, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
    #wrap around another sizer, to keep the GUI consistent
    workaround_sizer = wx.BoxSizer (wx.VERTICAL)
    workaround_sizer.Add (sizer_hours,   0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    workaround_sizer.Add (sizer_comment, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
    self.SetSizerAndFit (workaround_sizer)
    
  def set_unit (self, employment_type):
    """
    Sets the employment type for which will be edited.
      emplyoment_type: an employment type data object
    """
    self.employment_type = employment_type
    self.__set_permissions ( )
    
  def __hours_changed(self, event):
    """
    Event listener for the spin control.
    """
    if self.employment_type:
      self.employment_type.monthly_hours = self.monthly_hours.GetValue ( )
      self.__set_permissions ( )
    
  def __commented(self, event):
    """
    Event listener for the comment field.
    """
    if self.employment_type:
      self.employment_type.comment = self.comment_text.GetValue ( )
    
  def __set_permissions(self):
    """Keeps the GUI in sync with the data"""
    
    if self.employment_type:
      self.monthly_hours.Enable ( )
      self.comment_text.Enable ( )
      
      # if we do not unbind it, it causes a loop
      self.Unbind(wx.lib.intctrl.EVT_INT, self.monthly_hours)
      self.monthly_hours.SetValue (self.employment_type.monthly_hours)
      self.Bind(wx.lib.intctrl.EVT_INT, self.__hours_changed, self.monthly_hours)
      
      self.comment_text.SetValue (self.employment_type.comment)
      
    else:
      self.monthly_hours.SetValue (0)
      self.comment_text.SetValue ('')
      
      self.monthly_hours.Disable  ( )
      self.comment_text.Disable ( )
    
"""
This class contains two list boxes and is used to assert the nurse's titles.
"""        
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
  
  def __init__ (self, data_container, *args, **kwargs):
    """
    The default constructor.
      data_container: an instance of the data container
    """
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.data_object = None
    
    self.all_titles = wx.ListCtrl (self, wx.NewId(), style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES | wx.LC_NO_HEADER)
    self.all_titles.InsertColumn (0, 'Vsi nazivi')
    for i, title in enumerate (data_container.get_all ( )):
      self.all_titles.InsertStringItem(i, str (title))
    self.all_titles.SetColumnWidth(0, wx.LIST_AUTOSIZE)
      
    
    self.object_titles = wx.ListCtrl (self, wx.NewId(), style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES | wx.LC_NO_HEADER)
    self.object_titles.InsertColumn (0, 'Izbrani nazivi')
    self.object_titles.SetColumnWidth(0, wx.LIST_AUTOSIZE)
    
    dt = TitlePanel.MyTextDropTarget(self.object_titles)
    self.object_titles.SetDropTarget(dt)
    
    self.Bind(wx.EVT_LIST_BEGIN_DRAG, self.InsertDrag, self.all_titles)
    self.Bind(wx.EVT_LIST_BEGIN_DRAG, self.OrderDrag,  self.object_titles)
    
    self.__set_permissions ( )
    
    sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Nazivi"), wx.VERTICAL)
    sizer.Add (self.all_titles,    3, wx.ALIGN_LEFT | wx.ALIGN_TOP | wx.EXPAND)
    sizer.Add (self.object_titles, 2, wx.ALIGN_LEFT | wx.ALIGN_TOP | wx.EXPAND)
    
    self.SetSizerAndFit (sizer)
    
  def InsertDrag(self, event):
    """
    The event listener for starting a drag in the all titles field.
    """
    text = self.all_titles.GetItemText (event.GetIndex ( ))
    tdo  = wx.TextDataObject (text)
    tds  = wx.DropSource (self.object_titles)
    tds.SetData (tdo)
    tds.DoDragDrop (True)
    
    self.__set_titles ( )
    
  def OrderDrag(self, event):
    """
    The event listener for starting a drag in the data object's titles.
    """
    text = self.object_titles.GetItemText (event.GetIndex ( ))
    
    if text != str (self.data_object):
      self.object_titles.DeleteItem(event.GetIndex ( ))
      
      tdo = wx.TextDataObject( text)
      tds = wx.DropSource (self.object_titles)
      tds.SetData (tdo)
      tds.DoDragDrop (True)
      
      self.__set_titles ( )
    
  def set_unit(self, data_object):
    """
    Titles are always set on a person basis. This method sets the person.
      data_object: is the person for which the permissions will be edited.
    """
    self.object_titles.DeleteAllItems ( )
    self.data_object = data_object
    self.__set_permissions ( )
    
    
  def __set_titles_width(self):
    """
    Sets the appropriate width for the lists.
    """
    width = self.GetSize ( )[0] - 21
    self.all_titles.SetColumnWidth (0, width)
    self.object_titles.SetColumnWidth( 0, width)
    
  def __set_titles (self):
    """
    Sets the object's titles, as defined in the object_titles field.
    """
    #TODO: add the appropriate method into the container
    from data.title import Title
    prefixes = []
    suffixes = []
    i = 0
    
    while i < self.object_titles.GetItemCount ( ):
      if not locale.strcoll (self.object_titles.GetItemText (i), str (self.data_object)):
        break
      prefixes.append(Title (self.object_titles.GetItemText (i)))
      i += 1
      
    i += 1 # skip the person
    
    while i < self.object_titles.GetItemCount ( ):
      suffixes.append(Title (self.object_titles.GetItemText (i)))
      i += 1
      
    self.data_object.set_titles (prefixes, suffixes)
    self.__set_permissions ( )

    
  def __set_permissions (self):
    """Set's the correct permissions."""
    self.object_titles.DeleteAllItems ( )
    if self.data_object:
      self.all_titles.Enable ( )
      self.object_titles.Enable ( )
      
      i = -1
      prefixes, suffixes = self.data_object.get_titles ( )
      
      if prefixes:
        for i, title in enumerate (prefixes):
          self.object_titles.InsertStringItem (i, str (title))
      
      i += 1    
      self.object_titles.InsertStringItem(i, str (self.data_object))
      item = self.object_titles.GetItem (i)
      item.SetTextColour (wx.BLUE)
      self.object_titles.SetItem (item)
      
      if suffixes:
        for i, title in enumerate (suffixes):
          self.object_titles.InsertStringItem (i + 1 + len (prefixes), str (title))
          
      self.object_titles.SetColumnWidth (0, wx.LIST_AUTOSIZE)
      
    else:
      self.object_titles.Disable ( )
      self.all_titles.Disable ( )
      
    self.__set_titles_width ( )

"""
This class represents a panel, that consists only from checkers that handle the same data class.
"""
class CheckerPanel (wx.Panel):
  def __init__(self, title, data_container, check_method, add_method, remove_method, *args, **kwargs):
    """
    The default constructor.
      data_container: a data container object
    """
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.data_object   = None
    self.check_method  = check_method
    self.add_method    = add_method
    self.remove_method = remove_method
    
    #set the turnuses
    self.checkers = []
    for element in data_container.get_all ( ):
      self.checkers.append (wx_extensions.LinkedCheckBox(element, self, wx.NewId(), str(element)))
    
      
    for checker in self.checkers:
      self.Bind(wx.EVT_CHECKBOX, self.__checker_edited, checker)
      
    sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), title), wx.VERTICAL)   
    for checker in self.checkers:
      sizer.Add (checker, 0, wx.ALIGN_TOP, wx.ALIGN_LEFT)
    self.SetSizerAndFit (sizer)
    
  def set_unit (self, data_object):
    """
    Sets the data object, that will be edited.
      data_object: the data object
    """
    self.data_object = data_object
    self.__set_permissions ( )
    
  def __checker_edited (self, event):

    if event.IsChecked ( ):
      self.add_method    (self.data_object, event.GetEventObject ( ).element)
    else:
      self.remove_method (self.data_object, event.GetEventObject ( ).element)
           
    self.__set_permissions ( )
    
    # propagate the event, if the information might be needed on a higher level (workplaces => roles)
    wx.PostEvent(self.GetEventHandler ( ), custom_events.UpdateEvent (self.GetId()))
      
          
  def __set_permissions (self):
    """Checks and unchecks the checkers according to the current state."""
    
    if self.data_object:
      for checker in self.checkers:
        checker.Enable ( )
        if self.check_method (self.data_object, checker.element):
          checker.SetValue (True)
        else:
          checker.SetValue (False)
    else:
      for checker in self.checkers:
        checker.SetValue (False)
        checker.Disable ( )
   

"""
This class is used for selecting which roles the nurse works at the specific which workplace.
"""
class RolePanel (wx.Panel):
  
  def __init__(self, roles, *args, **kwargs):
    """
    The default constructor.
      roles: a data container instance
    """
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.data_object = None
    
    sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), "Vloge"), wx.VERTICAL)
    
    self.workplaces = wx_extensions.LinkedChoice (global_vars.get_workplaces ( ).get_all ( ), self, wx.NewId())
    self.Bind(wx.EVT_CHOICE, self.__workplace_selected, self.workplaces)
    sizer.Add(self.workplaces, 0, wx.ALIGN_LEFT)
    
    self.roles = []
    for role in roles.get_all ( ):
      self.roles.append(wx_extensions.LinkedCheckBox(role, self, wx.NewId(), str(role)))
      self.Bind(wx.EVT_CHECKBOX, self.__role_edited, self.roles[-1])
      sizer.Add(self.roles[-1], 0, wx.ALIGN_LEFT)
      
    self.SetSizerAndFit(sizer)
      
    self.__set_permissions()
      
  def set_unit(self, data_object):
    """
    Sets the data_object for which the roles will be edited.
    """
    if data_object:
      self.data_object = data_object
      self.workplaces.set_elements (sorted (self.data_object.workplaces))
    else:
      self.data_object = None
      self.workplaces.set_elements ([])
      
    self.__set_permissions ( )
      
  def __role_edited(self, event):
    """
    The event listener for the roles checkboxes.
    """
    if event.IsChecked():
      # add the role
      self.data_object.add_role (self.workplaces.get_value ( ), event.GetEventObject ( ).element)
    else:
      # remove the role
      self.data_object.remove_role (self.workplaces.get_value ( ), event.GetEventObject ( ).element)
      
    # reload permissions
    self.__set_permissions()
    
  def __workplace_selected(self, event):
    """
    The event listener for the workplaces drop-down.
    """
    self.__set_permissions ( )
    
  def __set_permissions(self):
    """Keeps the GUI in sync with the data"""
    if not self.data_object:
      self.workplaces.Disable ( )
      for role in self.roles:
        role.SetValue (False)
        role.Disable ( )
    else:
      try:
        self.workplaces.Enable ( )
        workplace = self.workplaces.get_value ( )
        roles = self.data_object.roles[workplace]
        for role_checker in self.roles:
          if role_checker.element in workplace.roles:
            role_checker.Enable ( )
            role_checker.SetValue (role_checker.element in roles)
          else:
            role_checker.SetValue (False)
            role_checker.Disable ( )
      except:
        self.workplaces.Disable ( )
        for role in self.roles:
          role.SetValue (False)
          role.Disable ( )

"""
This class represents the edit nurse panel's attributes.
"""
class HeaderNursePanel (wx.Panel):
  
  # if no person is selected
  INVALID_LABEL = "Izberite osebo za urejanje."
  
  def __init__(self, *args, **kwargs):
    """
    The default constructor.
    """
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.nurse = None
    
    self.person_info      = wx.lib.ticker.Ticker         (self, wx.ID_ANY, HeaderNursePanel.INVALID_LABEL)
    text                  = wx.StaticText                (self, wx.ID_ANY, "Vrsta zaposlitve: ")
    self.employment_types = wx_extensions.LinkedComboBox (self, wx.ID_ANY, style=wx.CB_READONLY)
    
    self.Bind(wx.EVT_COMBOBOX, self.__employment_type_selected, self.employment_types)
    
    employment_type_sizer = wx.BoxSizer (wx.HORIZONTAL)
    
    employment_type_sizer.Add (text,                  0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
    employment_type_sizer.Add (self.employment_types, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT)
    
    sizer = wx.BoxSizer (wx.VERTICAL)
    sizer.Add (self.person_info,      0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    sizer.Add (employment_type_sizer, 0, wx.ALIGN_CENTER)
    
    self.SetSizerAndFit (sizer)
    
  def set_unit(self, nurse):
    """
    Sets the nurse for which the header will be displayed/edited.
      nurse: a data nurse instance
    """ 
    self.nurse = nurse
    self.__set_permissions ( )
    
  def __employment_type_selected(self, event):
    """
    Event listener for the employment types.
    """
    self.nurse.set_employment_type (self.employment_types.get_selected_type ( ))
    self.__set_permissions ( )
    
  def __set_permissions(self):
    """
    Keeps the GUI in sync with the data.
    """
    if self.nurse:
      self.person_info.SetText (self.nurse.get_academic_name ( ))
      self.employment_types.Enable ( )
      self.employment_types.set_selection (self.nurse.employment_type)
    else:
      self.person_info.SetLabel (HeaderNursePanel.INVALID_LABEL)
      self.employment_types.set_selection (None)
      self.employment_types.Disable ( )
    

"""
This class sets the special properties, which are specific for the data Nurse class.
"""
class SpecialNurseProperties (wx.Panel):
  
  def __init__(self, *args, **kwargs):
    """
    The default constructor.
    """
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.nurse = None
    
    self.packet_night_turnuses = wx.CheckBox(self, wx.ID_ANY, label='Združuj nočne turnuse')
    self.week_morning          = wx.CheckBox (self, wx.ID_ANY, label='Dela samo med tednom dopoldne')
    
    self.Bind (wx.EVT_CHECKBOX, self.__packet_night_turnuses, self.packet_night_turnuses)
    self.Bind (wx.EVT_CHECKBOX, self.__week_morning, self.week_morning)
    
    
    sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), "Ostalo"), wx.VERTICAL)
    sizer.Add(self.packet_night_turnuses, 0, wx.ALIGN_LEFT)
    sizer.Add(self.week_morning,          0, wx.ALIGN_LEFT)
    
    self.SetSizerAndFit (sizer)
    
  def set_unit (self, nurse):
    """
    Sets the nurse for which the properties will be edited.
      nurse: a data nurse instance
    """ 
    self.nurse = nurse
    self.__set_permissions ( )
    
  def __packet_night_turnuses(self, event):
    """
    The event listener for the packet night turnuses check box.
    """
    self.nurse.packet_night_turnuses = event.IsChecked ( )
    self.__set_permissions ( )
    
  def __week_morning(self, event):
    """
    The event listener for the morning weekday check box.
    """
    self.nurse.week_morning = event.IsChecked ( ) 
    self.__set_permissions ( )
    
  def __set_permissions(self):
    """
    Keeps the GUI in sync with the data.
    """
    if self.nurse:
      self.packet_night_turnuses.Enable ( )
      self.week_morning.Enable ( )
      
      self.packet_night_turnuses.SetValue (self.nurse.packet_night_turnuses)
      self.week_morning.SetValue          (self.nurse.week_morning)
    else:
      self.packet_night_turnuses.SetValue (False)
      self.week_morning.SetValue          (False)
      
      self.packet_night_turnuses.Disable ( )
      self.week_morning.Disable ( )
      

"""
Deprecated
"""      
class DateDialog(wx.Dialog):
  
  def __init__(self, person, *args, **kwargs):
    """
    The default constructor.
      person: the person, that this dialog will represent
    """
    import wx
    wx.Dialog.__init__(self, *args, **kwargs)
    
    self.person = person
    
    sizer = wx.BoxSizer(wx.VERTICAL)
    import wx.calendar
    self.calendar = wx_extensions.EnhancedCalendar(self, wx.NewId(), style=wx.calendar.CAL_MONDAY_FIRST | wx.calendar.CAL_SHOW_SURROUNDING_WEEKS | wx.calendar.CAL_SEQUENTIAL_MONTH_SELECTION)
    self.Bind(wx.calendar.EVT_CALENDAR_SEL_CHANGED, self.__update_date, self.calendar)
    sizer.Add(self.calendar, 1, wx.CENTER | wx.EXPAND)
    
    
    self.permissions = DatePermissionsPanel(person, self.__get_date(), self, wx.NewId())
    sizer.Add(self.permissions, 0, wx.ALIGN_LEFT)
    
    self.SetSizerAndFit(sizer)
      
    self.permissions.set_unit(self.__get_date())
      
  def __update_date(self, event):
    """Event listener of the calendar object"""
    self.permissions.set_unit(self.__get_date())
    
  def __get_date(self):
    """Reads the date from the calendar control and returns a python date object.
      return: a python date, as selected in the calendar control.
    """
    return self.calendar.PyGetDate ()
  
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
    for vacation in global_vars.get_vacations().get_all():
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
      