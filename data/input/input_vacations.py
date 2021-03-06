# -*- coding: Cp1250 -*-

from data          import locations 
from data.vacation import Vacation
from data.general  import DataContainer
from utils         import time_conversion

import os
import sys
import csv

  
  
def input_vacations():
  FILES_DIR = os.path.join('persistence', 'data', 'start_data')
  FILE_NAME = 'dopusti.csv'
  
  print 'Zacetek vzpostavljanja zacetnega stanja dopustov.'
  print 'Zaceli boste z vnosom dopustov.'
  
  sys.stdout.write('\tBranje datoteke...')
  f = file(os.path.join(FILES_DIR, FILE_NAME), 'rb')
  reader = csv.reader(f)
  sys.stdout.write('OK\n')
  
  vacations = []
  for row in reader:
    sys.stdout.write('\tUstvarjanje dopusta: ' + str(row) + '...')
    row[2]=time_conversion.time_to_timedelta(time_conversion.string_to_time(row[2]))
    vacations.append(Vacation(*row))
    sys.stdout.write('OK\n')
  
  sys.stdout.write('\tBrisanje starih in pisanje novih dopustov ...')
  vc = DataContainer(locations.VACATION_DATA, Vacation, sorted(vacations))
  vc.save()
  sys.stdout.write('OK\n')
  
  print 'Konec vnosa dopustov.'
  print 'Zacetno stanje dopustov vzpostavljeno.\n'
