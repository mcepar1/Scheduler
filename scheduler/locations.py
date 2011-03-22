# -*- coding: Cp1250 -*-

"""
This file lists the directory locations and the file names of the internal storage.
"""
import os

def __get_files (dir):
  """
  Returns a list of files.
    @return: a list of files
  """
  files = []
  for file in os.listdir(os.path.join('persistence', 'scheduler', 'nurses')):
    if str(file).endswith('dat'):
      files.append(file)
  return files

def __date_to_filename (date):
  """
  Constructs a filename from the given date.
    @param date: a datetime.date object
    @return: a string
  """
  return str (date.month) + '_' + str (date.year) + '.dat'
  
def get_file_path (date):
  """
  Returns the file path for the specified date.
    @param date: a datetime.date object
    @return: a string
  """
  return os.path.join (DATA_DIR, __date_to_filename (date))

DATA_DIR = os.path.join ('persistence', 'scheduler', 'nurses')
FILES    = __get_files (DATA_DIR)
