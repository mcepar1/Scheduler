# -*- coding: Cp1250 -*-

from data import locations
from data.employment_type import EmploymentType
from data.general import DataContainer
 

import os
import sys
import csv
  
  
def input_emplyment_types():
  FILES_DIR = os.path.join('persistence', 'data', 'start_data')
  FILE_NAME = 'vrste_zaposlitev.csv'
  
  print 'Zacetek vzpostavljanja zacetnega stanja vrst zaposlitve.'
  print 'Zaceli boste z vnosom zaposlitev.'
  
  sys.stdout.write('\tBranje datoteke...')
  f = file(os.path.join(FILES_DIR, FILE_NAME), 'rb')
  reader = csv.reader(f)
  sys.stdout.write('OK\n')
  
  employment_types = []
  for row in reader:
    sys.stdout.write('\tUstvarjanje vrste zaposlitve: ' + str(row) + '...')
    row[1] = int(row[1])
    employment_types.append(EmploymentType(*row))
    sys.stdout.write('OK\n')
  
  sys.stdout.write('\tBrisanje starih in pisanje novih vrst zaposlitve ...')
  ec = DataContainer(locations.EMPLOYMENT_TYPE_DATA, EmploymentType, sorted(employment_types))
  ec.save()
  sys.stdout.write('OK\n')
  
  print 'Konec vnosa vrst zaposlitve.'
  print 'Zacetno stanje vrst zaposlitve vzpostavljeno.\n'
