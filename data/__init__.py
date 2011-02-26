# -*- coding: Cp1250 -*-

def load ( ):
  """
  This method loads the entire data model. It also prevents duplicates from being created.
    return: a tuple of DataContainer objects. They are in the following order:
      vacations, titles, turnus_types, roles, turnuses, workplaces, employment_types, nurses
  """
  data = []
  
  #first load all the objects, that have no dependencies
  import vacation, title, turnus_type, role
  vacations    = vacation.load ( )
  data        += vacations.get_all ( )
  
  titles       = title.load ( )
  data        += titles.get_all ( )
  
  turnus_types = turnus_type.load ( )
  data        += turnus_types.get_all ( )
  
  roles        = role.load ( )
  data        += roles.get_all ( )
  
  
  # now load all the instances, that depend only on the above objects
  import turnus
  turnuses = turnus.load ( )
  turnuses.synchronize_data (*data)
  data    += turnuses.get_all ( )
  
  # level up
  import workplace, employment_type
  workplaces = workplace.load ( )
  workplaces.synchronize_data (*data)
  data      += workplaces.get_all ( )
  
  employment_types = employment_type.load ( )
  employment_types.synchronize_data (*data)
  data            += employment_types.get_all ( )
  
  # last level - persons
  import nurse
  nurses = nurse.load ( )
  nurses.synchronize_data (*data)
  
  return vacations, titles, turnus_types, roles, turnuses, workplaces, employment_types, nurses
