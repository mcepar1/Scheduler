# -*- coding: Cp1250 -*-

import locale
import cPickle as pickle
import os

from data import locations

class DataClass:
  """ A generic class that defines some common methods, for all the subclasses. """
  
  def as_data_list(self):
    """
    Returns this object's attribute values in a list. 
      return: a list of static attributes of this class
    """
    raise Exception ('Not implemented')
    
  def as_list(self):
    """
    Returns this object's attribute values in a list. 
      return: same as as_data_list, only the attributes are now transformed into strings
    """
    raise Exception ('Not implemented')
  
  def synchronize_data(self, *args):
    """
    This is used to keep the instances of the subclasses consistent. This method updates every internal
    attribute of the class, so that the matching objects are forced into the data structure. Look at the
    data model for more details. 
    """
    pass

class DataContainer:
  """ A generic class that handles multiple instances of the data classes. """
  
  def __init__(self, filename, data_class, elements_list=None):
    """
    This is the constructor
      filename: a string, that represents the file name to the container's data file
      data_class: a data class for which the this container holds its objects
      elements_list: a list (or set) that contains elements of the data class
    """
    
    self.path = os.path.join(locations.DATA_DIR, filename)
    self.data_class = data_class
    self.filter = []
    self.elements = []
    
    #sort state
    self.column = None
    self.sort_ascending = None
    
    if elements_list:
      self.add_all(elements_list)
      
  def add_all(self, elements_list):
    """Adds all the elements of the elements_list into the container
      elements_list: a list that contains  instances of the data class"""
      
    for element in elements_list:
      if isinstance(element, self.data_class):
        for existing_element in self.elements:
          if element == existing_element:
            raise Exception(u'Element ' + str (element) + u' že obstaja.')
      else:
        raise Exception ('Dodajanje ' + str (type (element)) + ' med ' + str (self.data_class) + '!')
      self.elements.append (element)
    
    # sort the table, according to the sorting state
    self.sort (self.column, self.sort_ascending)
 
  def save(self):
    """Saves the current state into an external file."""
    pickle.dump((self.elements, self.column, self.sort_ascending), file(self.path, 'wb'))
    
    
  def load(self):
    """Loads the contents from the external file. The current state is LOST!!!!"""
    self.elements, self.column, self.sort_ascending = pickle.load(file(self.path, 'rb'))
    self.sort(self.column, self.sort_ascending)
    
  def synchronize_data(self, *args):
    """Keeps the data in sync."""
    for element in self.elements:
      element.synchronize_data(*args)
    
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
    table['header'] = self.data_class.HEADERS 
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
  
  def sort(self, column, sort_ascending=None):
    """
    Sorts the internal container. Does not return anything.
      column: which column to use for sorting: if it is lower than 0, the elements are ordered in their natural
        order, if it is larger than the number of columns or None, no sorting is performed.
      sort_ascending: will sort ascending if set to true, descending if set to false. If it is set to none,
        the sorting order will be determined automatically 
    """
    
    if column == None:
      self.column = None
      self.sort_ascending = None
      return
    
    if sort_ascending == None:
      if column == None:
        self.sort_ascending = None
      elif self.column != column:
        self.sort_ascending = True
      else:
        self.sort_ascending = not self.sort_ascending
    else:
      self.sort_ascending = sort_ascending 
    self.column = column
    
    if self.column < 0:
      self.elements.sort(reverse= not self.sort_ascending)
    elif self.column < len (self.data_class.HEADERS) and len (self.data_class.HEADERS):
      el = self.elements[0].as_data_list( )[self.column]
      #locale aware sorting
      if isinstance(el, str) or isinstance(el, unicode):
        self.elements.sort(cmp=lambda x, y: locale.strcoll(x.as_data_list()[self.column], y.as_data_list()[self.column]), reverse=not self.sort_ascending)
      else:
        self.elements.sort(cmp=lambda x, y: cmp(x.as_data_list()[self.column], y.as_data_list()[self.column]), reverse=not self.sort_ascending)
  
  def create (self, *args):
    """
    Creates and returns a single data object of this container. It does not insert it into the container.
      return: a single object, that can be put into this container.
    """
    return self.data_class (*args)
        
  def delete (self, element):
    """
    Deletes the element form the self.elements. Does not store the change to the hard drive.
    """
    self.elements.remove(element)
    
  def get_sorting_state (self):
    """
    Returns the sorting state of this container.
      return: a 2-tuple: the first element is the column, the second is a boolean, that defines if it was
        sorted in an ascending order
    """
    return (self.column, self.sort_ascending)
  
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
    return ", ".join([str(element) for element in self.elements])
  
def load (file_location, data_class, container_class=DataContainer):
  """
  Loads and returns a container instance.
  """
  el = container_class (file_location, data_class)
  try:
    el.load()
  except Exception:
    pass
  return el
  