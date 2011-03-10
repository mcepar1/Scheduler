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
  


DATA_DIR = os.path.join('persistence', 'scheduler', 'nurses')
FILES    = __get_files (DATA_DIR)