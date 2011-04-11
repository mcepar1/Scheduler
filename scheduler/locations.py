# -*- coding: Cp1250 -*-

"""
This file lists the directory locations and the file names of the internal storage.
"""
import os

DATA_DIR = os.path.join ('persistence', 'scheduler', 'nurses')

def __date_to_filename (date):
  """
  Constructs a filename from the given date.
    @param date: a datetime.date object
    @return: a string
  """
  return str (date.month) + '_' + str (date.year) + '.dat'

def get_files (dir=DATA_DIR):
  """
  Returns a list of file paths.
    @return: a list of files paths
  """
  files = []
  for file in os.listdir(dir):
    if str(file).endswith('dat'):
      files.append(os.path.join (dir, file))
  return files

def delete_schedule (date):
  """
  Permanently deletes the schedule.
    @param date: a datetime.date object. Day parameter is unimportant.
  """
  os.remove (get_file_path (date))
  
def get_file_path (date):
  """
  Returns the file path for the specified date.
    @param date: a datetime.date object
    @return: a string
  """
  return os.path.join (DATA_DIR, __date_to_filename (date))
