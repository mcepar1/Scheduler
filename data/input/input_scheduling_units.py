# -*- coding: Cp1250 -*-

from data                 import locations
from data.scheduling_unit import SchedulingUnit
from data.general         import DataContainer

import os
import sys
import csv

def __find_role (label):
  """
  Attempts to find an existing role.
    @param label: a string
    @return: the role with the given label
  """
  from data import role as mod
  roles = mod.load ( )
  
  for role in roles.get_all ( ):
    if label == role.label:
      return role
  else:
    raise Exception ('Aplikacija ne pozna vloge: ' + label)
  
def __find_workplace (label):
  """
  Attempts to find an existing workplace.
    @param label: a string
    @return: the workplace with the given label
  """
  from data import workplace as mod
  workplaces = mod.load ( )
  
  for workplace in workplaces.get_all ( ):
    if label == workplace.label:
      return workplace
  else:
    raise Exception ('Aplikacija ne pozna delovisca: ' + label)

def input_scheduling_units():
  
  FILES_DIR = os.path.join('persistence', 'data', 'start_data')
  FILE_NAME = 'pari.csv'
  
  print 'Zacetek vzpostavljanja zacetnega stanja parov delovisce - vloga.'
  print 'Zaceli boste z vnosom parov.'
  
  sys.stdout.write('\tBranje datoteke...')
  f = file(os.path.join(FILES_DIR, FILE_NAME), 'rb')
  reader = csv.reader(f)
  sys.stdout.write('OK\n')
  
  elements = []
  for row in reader:
    sys.stdout.write('\tUstvarjanje para: ' + str(row) + '...')
    row[0] = __find_workplace (row[0])
    row[1] = __find_role      (row[1])
    elements.append (SchedulingUnit (*row))
    sys.stdout.write('OK\n')
  
  sys.stdout.write('\tBrisanje starih in pisanje novih vlog ...')
  dc = DataContainer(locations.SCHEDULE_UNIT_DATA, SchedulingUnit, sorted (elements))
  dc.save()
  sys.stdout.write('OK\n')
  
  print 'Konec vnosa parov.'
  print 'Zacetno stanje parov delovisce-vloga je vzpostavljeno.\n'
