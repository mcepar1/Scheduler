# -*- coding: utf-8 -*-

from data.role import Role, RoleContainer

import os
import sys
import csv
  
  
def input_roles():
  
  FILES_DIR = os.path.join('persistence', 'data', 'start_data')
  FILE_NAME = 'vloge.csv'
  
  print 'Zacetek vzpostavljanja zacetnega stanja vlog.'
  print 'Zaceli boste z vnosom vlog.'
  
  sys.stdout.write('\tBranje datoteke...')
  f = file(os.path.join(FILES_DIR, FILE_NAME), 'rb')
  reader = csv.reader(f)
  sys.stdout.write('OK\n')
  
  roles = []
  for row in reader:
    sys.stdout.write('\tUstvarjanje vloge: ' + str(row) + '...')
    roles.append(Role(*row))
    sys.stdout.write('OK\n')
  
  sys.stdout.write('\tBrisanje starih in pisanje novih vlog ...')
  tc = RoleContainer(sorted(roles))
  tc.save()
  sys.stdout.write('OK\n')
  
  print 'Konec vnosa vlog\n'
  print 'Zacetno stanje vlog vzpostavljeno.'
