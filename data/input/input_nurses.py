# -*- coding: Cp1250 -*-

from data.nurse   import Nurse
from utils        import time_conversion
from data.general import locations, DataContainer 

import os
import sys
import csv


def input_nurses():
  print 'Zacetek vzpostavljanja zacetnega stanja medicinskih sester.'
  input_persons()
  print 'Zacetno stanje medicinskih sester vzpostavljeno.'
  
def input_persons():
  FILES_DIR = os.path.join('persistence', 'data', 'start_data')
  FILE_NAME = 'sestre.csv'
  
  print 'Zaceli boste z vnosom medicinskih sester.'
  
  sys.stdout.write('\tBranje datoteke...')
  f = file(os.path.join(FILES_DIR, FILE_NAME), 'rb')
  reader = csv.reader(f)
  sys.stdout.write('OK\n')
  
  nurses = []
  for row in reader:
    sys.stdout.write('\tUstvarjanje medicinske sestre: ' + str(row) + '...')
    row[-1] = time_conversion.string_to_date(row[-1])
    nurses.append(Nurse(*row))
    sys.stdout.write('OK\n')
  
  sys.stdout.write('\tBrisanje starih in pisanje novih medicinskih sester ...')
  nc = DataContainer(locations.NURSES_DATA, Nurse, sorted(nurses))
  nc.save()
  sys.stdout.write('OK\n')
  
  print 'Konec vnosa medicinskih sester'
  


