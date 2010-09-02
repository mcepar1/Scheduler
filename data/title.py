# -*- coding: utf-8 -*-

import cPickle as pickle
import os

class Title:
  
  HEADERS = ["NAZIV"]
  
  def __init__(self, label):
    
    self.label = label
    
  def as_list(self):
    """Returns this object's attribute values in a list. 
    This method should always correspond with the HEADERS variable."""
    return [self.label]
    
  def __str__(self):
    return self.label
    
  def __hash__(self):
    return hash(str(self))
    
  def __eq__(self, other):
    return self.__cmp__(other) == 0
    
  def __cmp__(self, other):
    try:
      return cmp(self.label, other.label)
    except:
      return - 1
    
class TitleContainer:
  """Contains methods, that deal with multiple instances of the Title
  class at once (loading, saving, representing as a table, ...)"""
  
  FILES_DIR = os.path.join("persistence", "data")
  FILE_NAME = "title.dat"
  
  def __init__(self, title_list=None):
    """This is the constructor
    title_list: a list (or set) that contains instances of the Title class"""
    
    self.titles = []
    
    if title_list:
      self.add_all(title_list)
        
  def add_all(self, title_list):
    """Adds all the elements of the title_list into the container
      title_list: a list that contains  instances of the Title class"""
      
    for title in title_list:
        self.titles.append(title)
  
  def save(self):
    """Saves the current state into an external file."""
    pickle.dump(self.titles, file(os.path.join(TitleContainer.FILES_DIR, TitleContainer.FILE_NAME), 'wb'))
    
  def load(self):
    """Loads the contens from the external file. The current state is LOST!!!!"""
    self.titles = pickle.load(file(os.path.join(TitleContainer.FILES_DIR, TitleContainer.FILE_NAME), 'rb'))
    
  def as_table(self):
    """Returns a table-like representation of self.
      return: a dictionary with two string keys:
        header: a list that contains headers of the table:
        items: a list of lists. The external list represents rows and the internal one represents columns within a single row."""
        
    
    rows_list = []
    for title in self.titles:
      rows_list.append(title.as_list())
    
    table = {}
    table['header'] = Title.HEADERS  
    table['items'] = rows_list
   
    return table
    
  def __str__(self):
    return ", ".join([str(title) for title in self.titles])
    
def load():
  """
  Loads and returns a container instance.
  """
  el = TitleContainer()
  try:
    el.load()
  except Exception as e:
    print e
    
  return el
  