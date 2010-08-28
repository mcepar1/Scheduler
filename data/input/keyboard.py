# -*- coding: utf-8 -*-
from utils import time_conversion
from global_vars import turnuses, workplaces

def get_date():
  MESSAGE = "Datum mora biti v navednicah in oblike DD.MM.LLLL. Primer datuma je: '01.01.2010'\nVnesi datum: "
  
  try:
    return time_conversion.string_to_date(input(MESSAGE))
  except EOFError:
    print 'Niste vnesli datuma.'
    return get_date()
  except NameError:
    print "Datum mora biti v navednicah in oblike DD.MM.LLLL. Primer datuma je: '01.01.2010'"
    return get_date()
  except Exception as e:
    print e
    return get_date()
    
def get_turnus(print_choices=True):
  MESSAGE = 'Vnesi cifro: '
  
  if (print_choices):
    for i, turnus in enumerate(turnuses.turnuses):
      print str(i + 1) + ' -> ' + str(turnus)
    
  try:
    i = int(input(MESSAGE)) - 1
    if i in range(len(turnuses.turnuses)):
      return turnuses.turnuses[i]
    else:
      print 'Cifra mora biti med 1 in ' + str(len(turnuses.turnuses)) + '.'
      return get_turnus(False)
  except EOFError:
    print 'Niste vnesli cifre'
    return get_turnus(False)
  except NameError:
    print 'Vnesite zgolj cifro, brez dodatnih znakov ali presledkov.'
    return get_turnus(False)
  except Exception as e:
    print e
    return get_turnus(False)
  
def get_workplace(print_choices=True):
  MESSAGE = 'Vnesi cifro: '
  
  if (print_choices):
    for i, workplace in enumerate(workplaces.workplaces):
      print str(i + 1) + ' -> ' + str(workplace)
    
  try:
    i = int(input(MESSAGE)) - 1
    if i in range(len(workplaces.workplaces)):
      return workplaces.workplaces[i]
    else:
      print 'Cifra mora biti med 1 in ' + str(len(workplaces.workplaces)) + '.'
      return get_workplace(False)
  except EOFError:
    print 'Niste vnesli cifre'
    return get_workplace(False)
  except NameError:
    print 'Vnesite zgolj cifro, brez dodatnih znakov ali presledkov.'
    return get_workplace(False)
  except Exception as e:
    print e
    return get_workplace(False)
  
def get_three_way_choice(print_choices=True):
  MESSAGE = 'Vnesi cifro: '

  if print_choices:
    print '1 -> Za ta dan se ne ve se nic'
    print '2 -> To je bil prost dan (navaden prost dan ali dopust)'
    print '3 -> To je bil turnus'
    
  try:
    i = int(input(MESSAGE))
    if i in range(1, 4):
      return i
    else:
      print 'Cifra mora biti med 1 in 3.'
      return get_three_way_choice(False)
  except EOFError:
    print 'Niste vnesli cifre'
    return get_three_way_choice(False)
  except NameError:
    print 'Vnesite zgolj cifro, brez dodatnih znakov ali presledkov.'
    return get_three_way_choice(False)
  except Exception as e:
    print e
    return get_three_way_choice(False)
