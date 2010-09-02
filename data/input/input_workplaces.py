# -*- coding: utf-8 -*-

from data.workplace import Workplace, WorkplaceContainer

import os
import sys
import csv
  
  
def input_workplaces():
  FILES_DIR = os.path.join('persistence', 'data', 'start_data')
  FILE_NAME = 'delovisca.csv'
  
  print 'Zacetek vzpostavljanja zacetnega stanja delovisc.'
  print 'Zaceli boste z vnosom delovisc.'
  
  sys.stdout.write('\tBranje datoteke...')
  f = file(os.path.join(FILES_DIR, FILE_NAME), 'rb')
  reader = csv.reader(f)
  sys.stdout.write('OK\n')
  
  workplaces = []
  for row in reader:
    sys.stdout.write('\tUstvarjanje delovisca: ' + str(row) + '...')
    row[-1] = bool(int(row[-1]))
    workplaces.append(Workplace(*row))
    sys.stdout.write('OK\n')
  
  sys.stdout.write('\tBrisanje starih in pisanje novih delovisc ...')
  wc = WorkplaceContainer(sorted(workplaces))
  wc.save()
  sys.stdout.write('OK\n')
  
  print 'Konec vnosa delovisc\n'
  print 'Zacetno stanje delovisc vzpostavljeno.'
