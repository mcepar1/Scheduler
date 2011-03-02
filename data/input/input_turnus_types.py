# -*- coding: Cp1250 -*-

from data             import locations 
from data.turnus_type import TurnusType
from data.general     import DataContainer

import os
import sys
import csv
  
  
def input_turnus_types():
  
  FILES_DIR = os.path.join('persistence', 'data', 'start_data')
  FILE_NAME = 'vrste_turnusov.csv'
  
  print 'Zacetek vzpostavljanja zacetnega stanja vrst turnusov.'
  print 'Zaceli boste z vnosom vrst turnusov.'
  
  sys.stdout.write('\tBranje datoteke...')
  f = file(os.path.join(FILES_DIR, FILE_NAME), 'rb')
  reader = csv.reader(f)
  sys.stdout.write('OK\n')
  
  turnus_types = []
  for row in reader:
    sys.stdout.write('\tUstvarjanje vrste turnusa: ' + str(row) + '...')
    turnus_types.append(TurnusType(*row))
    sys.stdout.write('OK\n')
  
  sys.stdout.write('\tBrisanje starih in pisanje novih vrst turnusov ...')
  tc = DataContainer(locations.TURNUS_TYPE_DATA, TurnusType, sorted(turnus_types))
  tc.save()
  sys.stdout.write('OK\n')
  
  print 'Konec vnosa vrst turnsov.'
  print 'Zacetno stanje vrst turnusov vzpostavljeno.\n'