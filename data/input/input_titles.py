# -*- coding: Cp1250 -*-

from data         import locations 
from data.title   import Title
from data.general import DataContainer

import os
import sys
import csv
  
  
def input_titles():
  
  FILES_DIR = os.path.join('persistence', 'data', 'start_data')
  FILE_NAME = 'nazivi.csv'
  
  print 'Zacetek vzpostavljanja zacetnega stanja nazivov.'
  print 'Zaceli boste z vnosom nazivov.'
  
  sys.stdout.write('\tBranje datoteke...')
  f = file(os.path.join(FILES_DIR, FILE_NAME), 'rb')
  reader = csv.reader(f)
  sys.stdout.write('OK\n')
  
  titles = []
  for row in reader:
    sys.stdout.write('\tUstvarjanje naziva: ' + str(row) + '...')
    titles.append(Title(*row))
    sys.stdout.write('OK\n')
  
  sys.stdout.write('\tBrisanje starih in pisanje novih nazivov ...')
  tc = DataContainer(locations.TITLE_DATA, Title, sorted(titles))
  tc.save()
  sys.stdout.write('OK\n')
  
  print 'Konec vnosa nazivov.'
  print 'Zacetno stanje nazivov vzpostavljeno.\n'
