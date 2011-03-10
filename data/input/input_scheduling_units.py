# -*- coding: Cp1250 -*-

from data                 import locations
from data.scheduling_unit import SchedulingUnit
from data.general         import DataContainer

import sys

def input_scheduling_units():
  
  #FILES_DIR = os.path.join('persistence', 'data', 'start_data')
  #FILE_NAME = 'vloge.csv'
  
  print 'Zacetek vzpostavljanja zacetnega stanja parov delovisce - vloga.'
  print 'Zaceli boste z vnosom parov.'
  
  #sys.stdout.write('\tBranje datoteke...')
  #f = file(os.path.join(FILES_DIR, FILE_NAME), 'rb')
  #reader = csv.reader(f)
  #sys.stdout.write('OK\n')
  
  elements = []
  #for row in reader:
  #  sys.stdout.write('\tUstvarjanje vloge: ' + str(row) + '...')
  #  roles.append(Role(*row))
  #  sys.stdout.write('OK\n')
  
  sys.stdout.write('\tBrisanje starih in pisanje novih vlog ...')
  dc = DataContainer(locations.SCHEDULE_UNIT_DATA, SchedulingUnit, sorted (elements))
  dc.save()
  sys.stdout.write('OK\n')
  
  print 'Konec vnosa parov.'
  print 'Zacetno stanje parov delovisce-vloga je vzpostavljeno.\n'
