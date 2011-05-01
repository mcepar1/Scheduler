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

def check_occurence (data_object):
  """
  Checks all the occurrences of the specified object.
    @param data_object: a data object
    @return: a set of all the elements, in which the object occured
  """
  import utils
  
  occuernces  = set ( )
  occuernces |= __check_container (get_vacations ( ),        data_object)
  occuernces |= __check_container (get_titles ( ),           data_object)
  occuernces |= __check_container (get_turnus_types ( ),     data_object)
  occuernces |= __check_container (get_roles ( ),            data_object)
  occuernces |= __check_container (get_turnuses ( ),         data_object)
  occuernces |= __check_container (get_workplaces ( ),       data_object)
  occuernces |= __check_container (get_employment_types ( ), data_object)
  occuernces |= __check_container (get_scheduling_units ( ), data_object)
  occuernces |= __check_container (get_nurses ( ),           data_object)
  
  to_sort = []  
  for o in occuernces:
    to_sort.append ((utils.translate (type (o).__name__), o))
  to_sort.sort ( )
  
  return [str(el[0]) + ': ' + str (el[1]) for el in to_sort]
  
  
  
def __check_container (container, data_object):
  """
  Checks in which objects does the data object occur.
    @param container: a data container object
    @param data_object: a data object
    @return: set of objects, in which all the data_object's parents are listed
  """
  occurences =  set ( )
  if container:
    occurences |= container.synchronize_data (data_object)
  return occurences

