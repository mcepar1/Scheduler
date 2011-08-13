# -*- coding: Cp1250 -*-

import csv

class Office2003Dialect (csv.excel):
  def __init__(self):
    csv.Dialect.__init__(self)
    self.delimiter=';'

def exportCSV(workplace_matrix, path):
  """
  Exports the grid into a CSV file.
    workplace_matrix: the scheduler's workplace matrix result
    path: the whole path to the file, that will be saved
  """  
  
  writer = csv.writer(file(path, 'wb'), dialect=Office2003Dialect())
    
  for scheduling_unit in sorted(workplace_matrix.keys()):
    writer.writerow((str(scheduling_unit), ''))
    
    for row in workplace_matrix[scheduling_unit]:
      writer.writerow(row)
      
    writer.writerow((''))
    writer.writerow((''))
    writer.writerow((''))
