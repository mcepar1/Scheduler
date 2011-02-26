# -*- coding: Cp1250 -*-

"""
This script contains global variables, that are accessed throughout the whole GUI.
To set their initial values use the vnos_zacetnih_podatkov.py script. 
"""

import data
vacations, titles, turnus_types, roles, turnuses, workplaces, employment_types, nurses = data.load ( )

def save():
  """An utility method, that saves all the data"""
  turnuses.save         ( )
  vacations.save        ( )
  nurses.save           ( )
  workplaces.save       ( )
  employment_types.save ( )
  titles.save           ( )
  turnus_types.save     ( )
  roles.save            ( )

  
