# -*- coding: Cp1250 -*-
"""
This script contains global variables, that are accessed throughout the whole GUI.
To set their initial values use the vnos_zacetnih_podatkov.py script. 
"""
vacations, titles, turnus_types, roles, turnuses, workplaces, scheduling_units, employment_types, nurses = \
(None,     None,   None,         None,  None,     None,       None,             None,             None)

def set_vacations (data_container):
  global vacations
  vacations = data_container

def set_titles (data_container):
  global titles
  titles = data_container

def set_turnus_types (data_container):
  global turnus_types
  turnus_types = data_container

def set_roles (data_container):
  global roles
  roles = data_container

def set_turnuses (data_container):
  global turnuses
  turnuses = data_container

def set_workplaces (data_container):
  global workplaces
  workplaces = data_container
  
def set_scheduling_units (data_container):
  global scheduling_units
  scheduling_units = data_container

def set_employment_types (data_container):
  global employment_types
  employment_types = data_container

def set_nurses (data_container):
  global nurses
  nurses = data_container

  
def get_vacations ( ):
  return vacations

def get_titles ( ):
  return titles

def get_turnus_types ( ):
  return turnus_types

def get_roles ( ):
  return roles

def get_turnuses ( ):
  return turnuses

def get_workplaces ( ):
  return workplaces

def get_scheduling_units ( ):
  return scheduling_units

def get_employment_types ( ):
  return employment_types

def get_nurses ( ):
  return nurses


