# -*- coding: Cp1250 -*-
from log import DummyLog

def load (log=DummyLog()):
  """
  This method loads the entire data model. It also prevents duplicates from being created.
    return: a tuple of DataContainer objects. They are in the following order:
      vacations, titles, turnus_types, roles, turnuses, workplaces, employment_types, nurses
  """
  data = []
  
  #first load all the objects, that have no dependencies
  log.send_message ('Nalagam vrste dopustov...', 0)
  import vacation, title, turnus_type, role
  vacations    = vacation.load ( )
  data        += vacations.get_all ( )
  
  log.send_message ('Nalagam nazive...', 10)
  titles       = title.load ( )
  data        += titles.get_all ( )
  
  log.send_message ('Nalagam vrste turnusov..', 20)
  turnus_types = turnus_type.load ( )
  data        += turnus_types.get_all ( )
  
  log.send_message ('Nalagam vloge...', 30)
  roles        = role.load ( )
  data        += roles.get_all ( )
  
  # now load all the instances, that depend only on the above objects
  log.send_message ('Nalagam turnuse...', 40)
  import turnus
  turnuses = turnus.load ( )
  turnuses.synchronize_data (*data)
  data    += turnuses.get_all ( )
  
  # level up
  import workplace, employment_type
  
  log.send_message ('Nalagam delovišča...', 50)
  workplaces = workplace.load ( )
  workplaces.synchronize_data (*data)
  data      += workplaces.get_all ( )
  
  log.send_message ('Nalagam vrste zaposlitev...', 60)
  employment_types = employment_type.load ( )
  employment_types.synchronize_data (*data)
  data            += employment_types.get_all ( )
  
  # level up
  import scheduling_unit
  
  log.send_message ('Nalagam pare delovišče - vloga', 70)
  scheduling_units = scheduling_unit.load ( )
  scheduling_units.synchronize_data (*data)
  data            += scheduling_units.get_all ( )
  
  # last level - persons
  import nurse
  log.send_message ('Nalagam medicinske setre...', 80)
  nurses = nurse.load ( )
  nurses.synchronize_data (*data)
  
  
  log.send_message ('Končano...', 100)
  return vacations, titles, turnus_types, roles, turnuses, workplaces, scheduling_units, employment_types, nurses
