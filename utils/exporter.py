import csv

def exportCSV(workplace_matrix, path):
  """
  Exports the grid into a CSV file.
    workplace_matrix: the scheduler's workplace matrix result
    path: the whole path to the file, that will be saved
  """  
  
  writer = csv.writer(file(path, 'wb'))
    
  for workplace in sorted(workplace_matrix.keys()):
    writer.writerow((str(workplace), ''))
    
    for row in workplace_matrix[workplace]:
      writer.writerow(row)
      
    writer.writerow((''))
    writer.writerow((''))
    writer.writerow((''))
