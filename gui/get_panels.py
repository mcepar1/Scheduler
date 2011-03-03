# -*- coding: Cp1250 -*-
"""
An utility module, that returns the appropriate panels for the main window.
"""
import common
import static_data

def __make_panel (container, parent, static_panel=None, edit_panel=None):
  if static_panel and edit_panel:
    return common.GenericTablePanel (container, parent, static_panel=static_panel, edit_panel=edit_panel)
  elif static_panel:
    return common.GenericTablePanel (container, parent, static_panel=static_panel)
  elif edit_panel:
    return common.GenericTablePanel (container, parent, edit_panel=edit_panel)
  else:
    return common.GenericTablePanel (container, parent)
  
def get_simple_panel (container, parent):
  """
  Returns a panel without dynamic data and with text only static data.
  """
  return __make_panel(container, parent)

def get_nurse_panel (container, parent):
  """
  Returns the nurse panel,
  """
  from dynamic_data import EditNursePanel
  return __make_panel (container, parent, static_data.StaticNursePanel, edit_panel=EditNursePanel)

def get_employment_type_panel (container, parent):
  """
  Returns the employment type panel.
  """
  from dynamic_data import EditEmploymentTypePanel
  return __make_panel (container, parent, static_panel=static_data.StaticEmploymentTypePanel, edit_panel=EditEmploymentTypePanel)

def get_turnus_panel (container, parent):
  """
  Returns the turnus panel.
  """
  from dynamic_data import EditTurnusPanel
  return __make_panel(container, parent, static_panel=static_data.StaticTurnusPanel, edit_panel=EditTurnusPanel)

def get_workplace_panel (container, parent):
  """
  Returns the workplace panel.
  """
  from dynamic_data import EditWorkplacePanel
  return __make_panel(container, parent, static_data.StaticWorkplacePanel, EditWorkplacePanel)

def get_vacation_panel (container, parent):
  """
  Return the vacation panel.
  """
  return __make_panel(container, parent, static_panel=static_data.StaticVacationPanel)
