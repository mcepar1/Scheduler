# -*- coding: Cp1250 -*-

from data import locations
from data.turnus import Turnus, TurnusContainer

import os
import sys
import csv
from utils import time_conversion
  
  
def input_turnuses():
  
  FILES_DIR = os.path.join('persistence', 'data', 'start_data')
  FILE_NAME = 'turnusi.csv'
  
  print 'Zacetek vzpostavljanja zacetnega stanja turnusov.'
  print 'Zaceli boste z vnosom turnusov.'
  
  sys.stdout.write('\tBranje datoteke...')
  f = file(os.path.join(FILES_DIR, FILE_NAME), 'rb')
  reader = csv.reader(f)
  sys.stdout.write('OK\n')
  
  turnuses = []
  for row in reader:
    sys.stdout.write('\tUstvarjanje turnusa: ' + str(row) + '...')
    row[2] = time_conversion.string_to_time(row[2])
    row[3] = time_conversion.string_to_time(row[3])
    row[4] = time_conversion.time_to_timedelta(time_conversion.string_to_time(row[4]))
    row[5] = time_conversion.time_to_timedelta(time_conversion.string_to_time(row[5]))
    row[6] = bool(int(row[6]))
    turnuses.append(Turnus(*row))
    sys.stdout.write('OK\n')
  
  sys.stdout.write('\tBrisanje starih in pisanje novih turnusov ...')
  tc = TurnusContainer(locations.TURNUS_DATA, Turnus, turnuses)
  tc.save()
  sys.stdout.write('OK\n')
  
  print 'Konec vnosa turnusov.'
  print 'Zacetno stanje turnusov vzpostavljeno.\n'
