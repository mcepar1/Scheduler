# -*- coding: Cp1250 -*-


import wx.wizard
import wx.lib.newevent
import wx.lib.scrolledpanel

import static_data
import wx_extensions

"""
New events, for easier communication between the toolbar and it's parents.
"""
AddEvent,    EVT_TB_ADD    = wx.lib.newevent.NewCommandEvent ( )
RemoveEvent, EVT_TB_REMOVE = wx.lib.newevent.NewCommandEvent ( )
SaveEvent,   EVT_TB_SAVE   = wx.lib.newevent.NewCommandEvent ( )
ReloadEvent, EVT_TB_RELOAD = wx.lib.newevent.NewCommandEvent ( )
SearchEvent, EVT_TB_SEARCH = wx.lib.newevent.NewCommandEvent ( )

"""
This is a standard GUI panel, for editing the data elements.
"""
class GenericTablePanel(wx.lib.scrolledpanel.ScrolledPanel):
  def __init__(self, container, *args, **kwargs):
    
    self.edit_panel_class = None
    if 'edit_panel' in kwargs:
      self.edit_panel_class = kwargs['edit_panel']
      del kwargs['edit_panel']
      
    self.static_panel_class = static_data.TextStaticPanel
    if 'static_panel' in kwargs:
      self.static_panel_class = kwargs['static_panel']
      del kwargs['static_panel']
    
    wx.lib.scrolledpanel.ScrolledPanel.__init__(self, *args, **kwargs)
    self.container = container
    
    sizer = wx.BoxSizer(wx.VERTICAL)
    self.SetSizer (sizer)
    
    self.toolbar = NotebookPageToolbar (self, wx.NewId ( ), style = wx.TB_HORIZONTAL | wx.TB_FLAT | wx.TB_NODIVIDER)
    sizer.Add(self.toolbar, 0, wx.ALIGN_LEFT | wx.EXPAND)
    
    self.grid = wx_extensions.EnhancedGrid (container, self, wx.NewId ( ))
    self.edit_panel = None
    if self.edit_panel_class:
      self.edit_panel = self.edit_panel_class (self, wx.NewId())
      
      sub_sizer = wx.BoxSizer (wx.HORIZONTAL)
      sub_sizer.Add (self.edit_panel, 0, wx.ALIGN_LEFT | wx.EXPAND)
      sub_sizer.Add (self.grid, 1, wx.CENTER | wx.LEFT | wx.EXPAND, 4)
      sizer.Add (sub_sizer, 1, wx.EXPAND)
    else:
      sizer.Add(self.grid, 1, wx.ALIGN_LEFT | wx.EXPAND)
    
    
    self.Bind(EVT_TB_ADD,    self.__add,    self.toolbar)
    self.Bind(EVT_TB_REMOVE, self.__remove, self.toolbar)
    self.Bind(EVT_TB_SAVE,   self.__save,   self.toolbar)
    self.Bind(EVT_TB_RELOAD, self.__reload, self.toolbar)
    self.Bind(EVT_TB_SEARCH, self.__search, self.toolbar)
    

    self.Bind(wx_extensions.EVT_GRID_SELECTED, self.__element_selected, self.grid)
    self.__element_selected (None)
    
    self.SetSizerAndFit (sizer)
    self.SetupScrolling ( )
    
  def __element_selected(self, event):
    """
    Event listener for the grid selection.
    """
    self.toolbar.EnableRemove(bool (self.grid.get_selected_element ( )))
    
    if self.edit_panel:
      self.edit_panel.set_unit (self.grid.get_selected_element( ))

  def __add(self, event):
    """
    Adds a new element into the global container.
    """
    object = AddWizard (self.container, self, wx.ID_ANY, title='Čarovnik za dodajanje',
                                                         static_panel=self.static_panel_class,
                                                         edit_panel=self.edit_panel_class).get_object ( )
                                                         
    if object:
      self.container.add_all ([object])
      self.grid.Refresh ( )
      self.grid.select_element (object)
    
  def __remove(self, event):
    """
    Removes an element from the global container.
    """
    self.grid.delete ( )
    self.__element_selected (None)
    
  def __save(self, event):
    """
    Saves the current state of the global container.
    """
    self.grid.save ( )
    
  def __reload(self, event):
    """
    Reloads the stored state of the global container.
    """
    self.grid.reload ( )
    self.__element_selected (None)
    
  def __search(self, event):
    """
    Searches the global container for the matching entries.
    """
    self.grid.search(self.toolbar.get_search_values())
    

"""
This is a toolbar, that is displayed on the top of every Page.
"""
class NotebookPageToolbar (wx.ToolBar):
  
  ADD    = wx.NewId ( )
  REMOVE = wx.NewId ( )
  SAVE   = wx.NewId ( )
  RELOAD = wx.NewId ( )
  
  def __init__ (self, *args, **kwargs):
    """
    The default constructor.
    """
    wx.ToolBar.__init__(self, *args, **kwargs)
    
    self.AddLabelTool(NotebookPageToolbar.ADD, 'Dodaj', wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR), shortHelp='Dodaj')
    self.AddLabelTool(NotebookPageToolbar.REMOVE, 'Izbriši', wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_TOOLBAR), shortHelp='Izbriši izbrano')
    self.AddSeparator ( )
    
    self.AddLabelTool(NotebookPageToolbar.SAVE, 'Shrani', wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR), shortHelp = 'Shrani podatke v tem oknu')
    self.AddLabelTool(NotebookPageToolbar.RELOAD, 'Razveljavi', wx.ArtProvider.GetBitmap(wx.ART_UNDO, wx.ART_TOOLBAR), shortHelp = 'Razveljavi vse neshranjene spremembe')
    
    self.AddSeparator ( )
    
    self.search = wx.SearchCtrl (self, wx.NewId ( ), style=wx.TB_HORIZONTAL | wx.TB_NODIVIDER)
    self.search.SetDescriptiveText ('Iskanje')
    self.search.ShowSearchButton (True)
    self.search.ShowCancelButton (True)
    
    self.AddControl(self.search)
    
    self.Bind(wx.EVT_TOOL, self.__add,    id = NotebookPageToolbar.ADD)
    self.Bind(wx.EVT_TOOL, self.__remove, id = NotebookPageToolbar.REMOVE)
    self.Bind(wx.EVT_TOOL, self.__save,   id = NotebookPageToolbar.SAVE)
    self.Bind(wx.EVT_TOOL, self.__reload, id = NotebookPageToolbar.RELOAD)
    
    self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.__clear_search, self.search)
    self.Bind(wx.EVT_TEXT, self.__search)
    
    # this hack enables clearing the search field with the escape key
    if wx.Platform in ['__WXGTK__', '__WXMSW__']:
      for child in self.search.GetChildren():
        if isinstance(child, wx.TextCtrl):
          child.Bind(wx.EVT_KEY_UP, self.__key_pressed)
          break
        
    self.Realize()
    
  def get_search_values (self):
    """
    Return a list of search strings.
      return: a list of strings
    """
    return self.search.GetValue ( ).split( )
  
  def EnableRemove (self, enable):
    """
    Enables and disables the delete button.
      enable: if set to true, the delete button will be enabled and vice-versa
    """
    self.EnableTool(NotebookPageToolbar.REMOVE, enable)
    
  def __search(self, event):
    """
    Fires the search event.
    """
    wx.PostEvent(self.GetEventHandler(), SearchEvent(self.GetId()))
    
  def __key_pressed (self, event):
    """
    Listens for the escape key and clears the search key, if pressed.
    """
    if event.GetKeyCode() == wx.WXK_ESCAPE:
      self.__clear_search(None)
    
  def __clear_search (self, event):
    """
    Clears the search field and fires the search event.
    """
    self.search.Clear()
    
  def __add (self, event):
    """
    Fires the add event.
    """
    wx.PostEvent(self.GetEventHandler(), AddEvent(self.GetId()))
    
  def __remove (self, event):
    """
    Fires the remove event.
    """
    wx.PostEvent(self.GetEventHandler(), RemoveEvent(self.GetId()))
    
  def __save (self, event):
    """
    Fires the save event.
    """
    wx.PostEvent(self.GetEventHandler(), SaveEvent(self.GetId()))
    
  def __reload (self, event):
    """
    Fires the reload event.
    """
    wx.PostEvent(self.GetEventHandler(), ReloadEvent(self.GetId()))

"""
A wizard, that adds a new data instances.
"""    
class AddWizard (wx.wizard.Wizard):
  def __init__(self, container, *args, **kwargs):
    """
    The default constructor.
      container: a data container object
      static_panel: a wx panel subclass, that edits the object's static data. The default value is the 
        TextStaticPanel
      edit_panel: a wx panel subclass, that edits the objects's dynamic data
    """
    static_panel = static_data.TextStaticPanel
    dynamic_panel = None
    self.container = container
    
    if 'static_panel' in kwargs:
      static_panel = kwargs['static_panel']
      del kwargs['static_panel']
    if 'edit_panel' in kwargs:
      dynamic_panel = kwargs['edit_panel']
      del kwargs['edit_panel']
    
    wx.wizard.Wizard.__init__(self, *args, **kwargs)
    
    self.static_page  = StaticPage (self.container, self, static_panel=static_panel)
    self.dynamic_page = None
    if dynamic_panel:
      self.dynamic_page = DynamicPage (dynamic_panel, self)
      wx.wizard.WizardPageSimple_Chain (self.static_page, self.dynamic_page)
    
    self.GetPageAreaSizer ( ).Add(self.static_page)
    
    self.data_object = None
    
    self.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGING, self.__page_changed)
    
    if not self.RunWizard (self.static_page):
      self.data_object = None
    
  def get_object(self):
    """
    Returns a data object, that was created by this wizard. If the wizard was canceled, returns None.
    """
    return self.data_object
  
  def __page_changed (self, event):
    """
    Event listener for changing the page.
    """
    if event.GetPage ( ).PAGE_NUMBER == StaticPage.PAGE_NUMBER:
      if event.GetPage ( ).is_valid ( ):
        self.data_object = self.container.create (*event.GetPage ( ).get_attributes ( ))
        if self.container.has_element (self.data_object):
          self.static_page.set_error_message ('Ta element že obstaja v aplikaciji.')
          event.Veto ( )
        elif self.dynamic_page:
          self.dynamic_page.set_unit (self.data_object)
      else:
        event.Veto ( )
        
"""
An empty static page.
"""  
class StaticPage (wx.wizard.WizardPageSimple):
  PAGE_NUMBER = 0
  
  def __init__(self, container, *args, **kwargs):
    """
    The default constructor.
      container: a data container object
      static_panel: a wx panel subclass, that edits the object's static data. The default value is the 
        TextStaticPanel
    """
    static_panel = static_data.TextStaticPanel
    if 'static_panel' in kwargs:
      static_panel = kwargs['static_panel']
      del kwargs['static_panel']
    
    wx.wizard.WizardPageSimple.__init__(self, *args, **kwargs)
    
    sizer = wx.BoxSizer(wx.VERTICAL)
    
    title = wx.StaticText(self, -1, 'Statični podatki')
    title.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
    
    self.static_panel = static_panel (container, self)
    
    sizer.Add (title, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
    sizer.Add (wx.StaticLine(self, -1), 0, wx.EXPAND|wx.ALL, 5)
    sizer.Add (self.static_panel, 1, wx.ALIGN_LEFT | wx.ALIGN_TOP | wx.SHAPED)
    self.SetSizerAndFit(sizer)
    
  
  def get_attributes (self):
    """
    Return a list of all attributes.
      return: a list, that contains the static panel's attribute values.
    """
    return self.static_panel.get_attributes ( )
  
  def is_valid (self):
    """
    Checks, if all the input fields have a valid entry.
      return: true, if it is valid, false otherwise
    """
    return self.static_panel.is_valid ( )
  
  def set_error_message (self, message):
    """
    Displays an error message.
    """
    self.static_panel.set_error_msg (message)
  
"""
An empty dynamic page
"""
class DynamicPage (wx.wizard.WizardPageSimple):
  PAGE_NUMBER = 1
  
  def __init__(self, edit_panel, *args, **kwargs):
    """
    The default constructor.
      container: a data container object
      edit_panel: a wx panel subclass, that edits the objects's dynamic data
    """
    wx.wizard.WizardPageSimple.__init__(self, *args, **kwargs)
    
    sizer = wx.BoxSizer (wx.VERTICAL)
    
    title = wx.StaticText(self, -1, 'Dinamični podatki')
    title.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
    
    self.edit_panel = edit_panel (self, wx.NewId())
    
    sizer.Add (title, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
    sizer.Add (wx.StaticLine(self, -1), 0, wx.EXPAND|wx.ALL, 5)
    sizer.Add (self.edit_panel, 1, wx.ALIGN_LEFT | wx.ALIGN_TOP, wx.SHAPED)
    
    self.SetSizerAndFit (sizer)
    
  def set_unit(self, element):
    """
    Sets the data object, that will be edited.
    """
    self.edit_panel.set_unit (element)   
    