# -*- coding: Cp1250 -*-
"""
This file contains classes for editing the object's dynamic data.
"""
import wx
import wx_extensions
import wx.lib.ticker
import wx.lib.intctrl
import wx.lib.colourselect

import custom_events, custom_widgets

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
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.person = None
    
    self.header             = HeaderNursePanel       (self, wx.ID_ANY)
    self.title_selector     = TitlePanel             (global_vars.get_titles ( ), self, wx.ID_ANY)
    self.turnus_permissions = TurnusPermissions      (self, wx.ID_ANY)
    self.special_properties = SpecialNurseProperties (self, wx.ID_ANY)
    self.comment_text       = EditCommentPanel       (self, wx.ID_ANY)
    
    
    grid_sizer = wx.FlexGridSizer (cols=2)
    grid_sizer.Add (self.title_selector,     0, wx.ALIGN_LEFT | wx.ALIGN_TOP | wx.EXPAND)
    grid_sizer.Add (self.turnus_permissions, 0, wx.ALIGN_LEFT | wx.ALIGN_TOP | wx.EXPAND)
    grid_sizer.Add (self.special_properties, 1, wx.ALIGN_LEFT | wx.ALIGN_TOP | wx.EXPAND)
    grid_sizer.Add (self.comment_text,       1, wx.ALIGN_LEFT | wx.ALIGN_TOP | wx.EXPAND)
    
    
    sizer = wx.BoxSizer (wx.VERTICAL)
    sizer.Add (self.header, 0, wx.EXPAND)
    sizer.Add (grid_sizer,  1, wx.ALIGN_LEFT | wx.EXPAND)
    
    
    self.SetSizerAndFit(sizer)
    
    
    
  def set_unit(self, person):
    """
    Sets the person, that is represented by this panel.
      person: the person, that is represented
    """
    self.person = person
    
    self.header.set_unit             (self.person)
    self.turnus_permissions.set_unit (self.person)
    self.title_selector.set_unit     (self.person)
    self.special_properties.set_unit (self.person)
    self.comment_text.set_unit       (self.person)
    

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
    
    self.turnus_type_checkers = CheckerPanel     (global_vars.get_turnus_types ( ), Turnus.has_type, Turnus.add_type, Turnus.remove_type, self, wx.ID_ANY, name='Vrste turnusov')
    self.comment_text         = EditCommentPanel (self, wx.ID_ANY)
    
    sizer = wx.BoxSizer (wx.VERTICAL)
    sizer.Add (self.turnus_type_checkers, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    sizer.Add (self.comment_text,         0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
    self.SetSizerAndFit (sizer)
    
  def set_unit (self, turnus):
    """
    Sets the turnus, represented by this panel.
      turnus: a data turnus object
    """
    self.turnus = turnus
    
    self.turnus_type_checkers.set_unit (self.turnus)
    self.comment_text.set_unit (self.turnus)

"""
This class is responsible for editing the workplace data.
"""
class EditSchedilungUnitPanel (wx.Panel):
  
  def __init__(self, *args, **kwargs):
    """
    The default constructor
    """
    from data.scheduling_unit import SchedulingUnit
    wx.Panel.__init__(self, *args, **kwargs)
    
    self.scheduling_unit = None
    
    self.turnus_checkers = CheckerPanel (global_vars.get_turnuses ( ), SchedulingUnit.is_allowed_turnus, SchedulingUnit.add_allowed_turnus, SchedulingUnit.remove_allowed_turnus, self, wx.ID_ANY, name='Dovoljeni turnusi')
    self.color_chooser   = wx.lib.colourselect.ColourSelect (self, wx.ID_ANY)
    self.comment_text    = EditCommentPanel                 (self, wx.ID_ANY)
    
    self.Bind (wx.lib.colourselect.EVT_COLOURSELECT, self.__color_selected, self.color_chooser)
    
    color_sizer = wx.StaticBoxSizer (wx.StaticBox (self, wx.ID_ANY, 'Barva ozadja'), wx.VERTICAL)
    color_sizer.Add (self.color_chooser, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
    sizer = wx.BoxSizer (wx.VERTICAL)
    sizer.Add (self.turnus_checkers, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    sizer.Add (color_sizer,          0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    sizer.Add (self.comment_text,    0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
    self.__set_permissions ( )
    
    self.SetSizerAndFit (sizer)
    
  def set_unit(self, scheduling_unit):
    """
    Sets the scheduling unit, represented by this panel.
      @param scheduling_unit: a data object
    """
    self.scheduling_unit = scheduling_unit   
    
    self.turnus_checkers.set_unit (self.scheduling_unit)
    self.comment_text.set_unit (self.scheduling_unit)
    
    self.__set_permissions ( )
    
  def __set_permissions (self):
    """
    Keeps the GUI in sync with the data model.
    """
    if self.scheduling_unit:
      self.color_chooser.Enable ( )
      self.color_chooser.SetLabel ('Klikni za spremembo')
      self.color_chooser.SetColour (self.scheduling_unit.get_color ( ))
    else:
      self.color_chooser.Disable ( )
      self.color_chooser.SetLabel ('')
      self.color_chooser.SetColour((255, 255, 255))
      
  def __color_selected (self, event):
    """
    Event listener for the color selector.
    """
    self.scheduling_unit.set_color (self.color_chooser.GetColour ( ))
    self.__set_permissions ( )
    
    
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
    self.comment_text  = EditCommentPanel (self, wx.ID_ANY)
    
    self.monthly_hours.SetMin (0)
    self.monthly_hours.SetLimited (True)
    
    self.Bind(wx.lib.intctrl.EVT_INT, self.__hours_changed, self.monthly_hours)
    
    
    sizer_hours   = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, 'Število ur v mesecu'), wx.VERTICAL)
    sizer_hours.Add (self.monthly_hours, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
    #wrap around another sizer, to keep the GUI consistent
    workaround_sizer = wx.BoxSizer (wx.VERTICAL)
    workaround_sizer.Add (sizer_hours,       0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    workaround_sizer.Add (self.comment_text, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
    self.SetSizerAndFit (workaround_sizer)
    
  def set_unit (self, employment_type):
    """
    Sets the employment type for which will be edited.
      emplyoment_type: an employment type data object
    """
    self.employment_type = employment_type
    self.comment_text.set_unit (employment_type)
    self.__set_permissions ( )
    
  def __hours_changed(self, event):
    """
    Event listener for the spin control.
    """
    if self.employment_type:
      self.employment_type.monthly_hours = self.monthly_hours.GetValue ( )
      self.__set_permissions ( )
    
  def __set_permissions(self):
    """Keeps the GUI in sync with the data"""
    
    if self.employment_type:
      self.monthly_hours.Enable ( )
      self.comment_text.Enable ( )
      
      # if we do not unbind it, it causes a loop
      self.Unbind(wx.lib.intctrl.EVT_INT, self.monthly_hours)
      self.monthly_hours.SetValue (self.employment_type.monthly_hours)
      self.Bind(wx.lib.intctrl.EVT_INT, self.__hours_changed, self.monthly_hours)
      
    else:
      self.monthly_hours.SetValue (0)
      
      self.monthly_hours.Disable  ( )
      self.comment_text.Disable ( )

"""
A class that can only edit comments.
"""    
class EditCommentPanel (wx.Panel):
  
  def __init__ (self, *args, **kwargs):
    """
    The default constructor.
    """
    wx.Panel.__init__ (self, *args, **kwargs)
    
    self.data_object   = None
    
    self.comment_text  = wx.TextCtrl (self, wx.ID_ANY, style=wx.TE_MULTILINE)
    
    self.Bind(wx.EVT_TEXT, self.__commented, self.comment_text)
    
    sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, 'Komentar'), wx.VERTICAL)
    sizer.Add (self.comment_text, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
    self.comment_text.SetMinSize ((150, 100))
    
    self.SetSizerAndFit (sizer)
    
  def set_unit (self, data_object):
    """
    Sets the data_object, that will be edited.
      @param data_object: a data object
    """
    self.data_object = data_object
    self.__set_permissions ( )
    
  def __commented(self, event):
    """
    Event listener for the comment field.
    """
    if self.data_object:
      self.data_object.set_comment (self.comment_text.GetValue ( ))
    
  def __set_permissions (self):
    """
    Keeps the GUI in sync with the data.
    """
    if self.data_object:
      self.comment_text.Enable ( )
      self.comment_text.SetValue (self.data_object.get_comment ( ))
    else:
      self.comment_text.Disable ( )
      self.comment_text.SetValue ('Za urejanje izberite objekt iz tabele.')
   
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
This class is used to set the individual nurse's turnus allowances.
"""
class TurnusPermissions (wx.Panel):
  
  def __init__ (self, *args, **kwargs):
    """
    The default constructor
    """
    wx.Panel.__init__ (self, *args, **kwargs)
    
    from data.nurse import Nurse
    self.person = None
    
    self.scheduling_unit_selector = custom_widgets.ScheduleUnitSelector (global_vars.get_scheduling_units ( ), self, wx.ID_ANY)
    self.turnus_checkers          = ParameterCheckerPanel (global_vars.get_turnuses ( ), Nurse.is_turnus_allowed, Nurse.add_allowed_turnus, Nurse.remove_allowed_turnus, self, wx.ID_ANY)
    
    self.Bind(custom_events.EVT_UPDATED, self.__scheduling_unit_selsected, self.scheduling_unit_selector)
    
    sizer = wx.StaticBoxSizer (wx.StaticBox (self, wx.ID_ANY, 'Turnusi'), wx.VERTICAL)
    sizer.Add (self.turnus_checkers,          1, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND | wx.BOTTOM, 5)
    sizer.Add (self.scheduling_unit_selector, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT | wx.EXPAND)
    
    
    self.SetSizerAndFit (sizer)
    self.set_unit (self.person)
    
  def set_unit (self, person):
    """
    Sets the data object, that will be edited.
      data_object: the data object
    """
    self.person = person
    self.turnus_checkers.set_unit ((self.person, self.scheduling_unit_selector.get_selection ( )))
    self.__set_permissions ( )
    
  def __scheduling_unit_selsected (self, event):
    """
    The event listener for the schedule units selectors.
    """
    self.set_unit (self.person)
    
  def __set_permissions (self):
    """
    Keeps the GUI in sync with the data model.
    """
    if self.person:
      self.scheduling_unit_selector.Enable ( )
      self.turnus_checkers.Enable ( )
    else:
      self.scheduling_unit_selector.Disable ( )
      self.turnus_checkers.Disable ( )
    

"""
This class represents a panel, that consists only from checkers that handle the same data class.
"""
class CheckerPanel (wx.Panel):
  def __init__(self, data_container, check_method, add_method, remove_method, *args, **kwargs):
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
      self.Bind(wx.EVT_CHECKBOX, self._checker_edited, checker)
    
    if self.GetLabel ( ) == '' or self.GetLabel ( )== 'panel':
      sizer = wx.BoxSizer (wx.VERTICAL)
    else:  
      sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), self.GetLabel ( )), wx.VERTICAL)   
    for checker in self.checkers:
      sizer.Add (checker, 0, wx.ALIGN_TOP, wx.ALIGN_LEFT)
    self.SetSizerAndFit (sizer)
    
  def set_unit (self, data_object):
    """
    Sets the data object, that will be edited.
      data_object: the data object
    """
    self.data_object = data_object
    self._set_permissions ( )
    
  def _checker_edited (self, event):
    """Event listener for the checkers."""

    if event.IsChecked ( ):
      self.add_method    (self.data_object, event.GetEventObject ( ).element)
    else:
      self.remove_method (self.data_object, event.GetEventObject ( ).element)
           
    self._set_permissions ( )
    
      
          
  def _set_permissions (self):
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
This class is the same as the checker panel, but it can handle one additional parameter with the
methods.
"""
class ParameterCheckerPanel (CheckerPanel):
  
  def __init__ (self, title, data_container, check_method, add_method, remove_method, *args, **kwargs):
    """
    The default constructor.
      @param title: the title
      @param data_container: a data container instance
      @param check_method: the method, that will be used to determine, how to set the checker
      @param add_method: the method, that will be used to add instances
      @param remove_method: the method, that will be used to remove instances
    """
    CheckerPanel.__init__(self, title, data_container, check_method, add_method, remove_method, *args, **kwargs)
    
    # the parameter for the methods
    self.parameter = None
    
  def set_unit (self, data_object_parameter):
    """
    This method will set the objects, that are edited.
      @param data_container_parameter: a 2-tuple, the first element is the data object, the second element
        is the parameter for the methods.
    """
    self.data_object, self.parameter = data_object_parameter
    
    self._set_permissions ( )
    
  def _checker_edited (self, event):
    """Event listener for the checkers."""

    if event.IsChecked ( ):
      self.add_method    (self.data_object, self.parameter, event.GetEventObject ( ).element)
    else:
      self.remove_method (self.data_object, self.parameter, event.GetEventObject ( ).element)
           
    self._set_permissions ( )
    
  def _set_permissions (self):
    """Checks and unchecks the checkers according to the current state."""
    
    if self.data_object and self.parameter:
      for checker in self.checkers:
        checker.Enable ( )
        if self.check_method (self.data_object, self.parameter, checker.element):
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
      self.person_info.SetText (HeaderNursePanel.INVALID_LABEL)
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
    
    self.overtime              = wx.CheckBox (self, wx.ID_ANY, label='Ima nadure')
    self.packet_night_turnuses = wx.CheckBox (self, wx.ID_ANY, label='Združuj nočne turnuse')
    
    self.Bind (wx.EVT_CHECKBOX, self.__overtime,              self.overtime)
    self.Bind (wx.EVT_CHECKBOX, self.__packet_night_turnuses, self.packet_night_turnuses)
    
    sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.NewId(), "Ostalo"), wx.VERTICAL)
    sizer.Add (self.overtime,              0, wx.ALIGN_LEFT)
    sizer.Add (self.packet_night_turnuses, 0, wx.ALIGN_LEFT)
    
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
    
  def __overtime(self, event):
    """
    The event listener for the overtime check box.
    """
    self.nurse.set_overtime (event.IsChecked ( )) 
    self.__set_permissions ( )
    
  def __set_permissions(self):
    """
    Keeps the GUI in sync with the data.
    """
    if self.nurse:
      self.overtime.Enable ( )
      self.packet_night_turnuses.Enable ( )
      
      self.overtime.SetValue              (self.nurse.has_overtime ( ))
      self.packet_night_turnuses.SetValue (self.nurse.packet_night_turnuses)
    else:
      self.overtime.SetValue              (False)
      self.packet_night_turnuses.SetValue (False)
      
      self.overtime.Disable ( )
      self.packet_night_turnuses.Disable ( )
      
      