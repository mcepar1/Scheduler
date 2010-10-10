# -*- coding: utf-8 -*-

"""
This script contains global variables, that are accessed throughout the whole GUI.
To set their initial values use the vnos_zacetnih_podatkov.py script. 
"""

from data import turnus, vacation, nurse, doctor, workplace, employment_type, title, turnus_type

# init the turnus types
turnus_types = turnus_type.load ()

# init the turnuses
turnuses = turnus.load ()

# init the vacations
vacations = vacation.load ()

# init the employement types
employment_types = employment_type.load ()

# init the workplaces
workplaces = workplace.load ()

# init the titles
titles = title.load ()

# init the nurses
nurses = nurse.load ()

# init the doctors
doctors = doctor.load ()



def save():
  """An utility method, that saves all the data"""
  turnuses.save()
  vacations.save()
  nurses.save()
  doctors.save()
  workplaces.save()
  employment_types.save()
  titles.save()
  turnus_types.save()

  
