# -*- coding: Cp1250 -*-

import cPickle as pickle
import os

from Scheduler.data import locations

class Container:
  """ A generic class that handles multiple instances of the data classes. """
  
  def __init__(self, filename, headers, elements_list=None):
    """
    This is the constructor
      filename: a string, that represents the file name to the container's data file
      headers: a list of strings, that represent column names, when the container is represented as a list
      elements_list: a list (or set) that contains elements of the data class
    """
    
    self.path = os.path.join(locations.DATA_DIR, filename)
    self.headers = headers
    self.filter = []
    self.elements = []
    
    if elements_list:
      self.add_all(elements_list)
      
  def add_all(self, elements_list):
    """Adds all the elements of the elements_list into the container
      elements_list: a list that contains  instances of the data class"""
      
    for element in elements_list:
      for existing_element in self.elements:
        if element == existing_element:
          raise Exception(u'Element ' + unicode (element) + u' že obstaja.')
      self.elements.append (element)
 
  def save(self):
    """Saves the current state into an external file."""
    pickle.dump(self.elements, file(self.path, 'wb'))
    
    
  def load(self):
    """Loads the contents from the external file. The current state is LOST!!!!"""
    self.elements = pickle.load(file(self.path, 'rb'))
    
  def as_table(self, filter=False):
    """
    Returns a table-like representation of self.
      return: a dictionary with two string keys:
        header: a list that contains headers of the table:
        items: a list of lists. The external list represents rows and the internal one represents columns within a single row.
        filter: determines, if the output should be filtered. The default value is set to false.
    """
        
    
    rows_list = []
    for element in self.get_filtered( ):
      rows_list.append(element.as_list())
    
    table = {}
    table['header'] = self.headers 
    table['items'] = rows_list
   
    return table
  
  def as_table_filtered(self):
    """
    Return a table-like representation of self and a map, that maps filtered indexes to internal indexes.
      return: two variables (table and map):
        table: same as the as_table method
        index_map: same as the __get_filtered_indexes method
    """
    return self.as_table(filter=True), self.__get_filtered_indexes()
  
  def sort(self, column, ascending=True):
    """
    Sorts the internal container. Does not return anything.
      column: which column to use for sorting: if it is lower than 0, the elements are ordered in their natural
        order, if it is larger than the number of columns, no sorting is performed.
      ascending: set the order in which the values are sorted. Default value is 0.
    """
    
    if column < 0:
      self.elements.sort(reverse= not ascending)
    elif column < len (self.headers):
      self.elements.sort(cmp=lambda x, y: cmp(x.as_data_list()[column], y.as_data_list()[column]), reverse=not ascending)
  
  def set_filter(self, filter):
    """
    Sets the container's filter. A filter is a list of strings. For element to pass a filter, each of the
    filter's strings must match with at least one column of the element. The filter is case insensitive.
    """
    self.filter = []
    for string in filter:
      self.filter.append(string.lower())
    
  def get_element(self, index):
    """
    Returns the element at the specified index.
      index: index of the nurse
    """
    # TODO: verify, that the self.elements and the GUI table always match indexes
    return self.elements[index]
  
  def get_index(self, element):
    """
    Returns the element at the specified index.
      element: the element, that for which we want the index
      return: an integer
    """
    return self.elements.index(element)
    
  
  def get_filtered(self):
    """
    Returns a list of elements, that passed the filter.
      return: a list of elements
    """
    
    if not self.filter:
      return self.get_all()
    
    
    passed = []
    for element in self.elements:
      if self.__filter_passed(element):
        passed.append(element)
      
    return passed
  
  def get_all(self):
    """
    Returns all elements.
      return: the internal list of elements
    """
    return self.elements
    
  def __filter_passed(self, element):
    """
    Checks, if the element passes the filter.
      return: true if successful, false otherwise
    """
    
    passes_all = True
    stringified = element.as_list ( )
    for string in self.filter:
      passes_string = False
      for column in stringified:
        passes_string |= column.lower().startswith(string)
      passes_all &= passes_string
      
    return passes_all
  
  def __get_filtered_indexes(self):
    """
    Constructs a map, that maps filtered indexes into internal indexes.
      return:  a dictionary that maps the filtered elements list into the internal self.elements indexes
    """
    
    map = {}
    index = 0
    for i, element in enumerate (self.elements):
      if self.__filter_passed(element):
        map[index] = i
        index += 1
    
    return map
    
  def __str__(self):
    return ", ".join([unicode(element) for element in self.elements])