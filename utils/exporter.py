# -*- coding: Cp1250 -*-

import csv

def exportCSV(workplace_matrix, path):
  """
  Exports the grid into a CSV file.
    workplace_matrix: the scheduler's workplace matrix result
    path: the whole path to the file, that will be saved
  """  
  
  writer = csv.writer(file(path, 'wb'))
    
  for scheduling_unit in sorted(workplace_matrix.keys()):
    writer.writerow((str(scheduling_unit), ''))
    
    for row in workplace_matrix[scheduling_unit]:
      writer.writerow(row)
      
    writer.writerow((''))
    writer.writerow((''))
    writer.writerow((''))
