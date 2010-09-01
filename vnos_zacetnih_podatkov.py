"""
This file is used to set the initial state of the application.
If you use this way of importing data, all the already inserted data
will be lost!
"""

import sys
import getopt

import data.input


def parse():
  try:
    options, _ = getopt.gnu_getopt(sys.argv[1:], 'szp', ['medicinske_sestre', 'zdravniki', 'pomoc'])
    
    insert_nurses = False
    insert_doctors = False
    print_help = False
    
    #if no parameter was given
    if not options:
      return (False, False, True)
    
    for option, _ in options:
      if option in ('-s', '--medicinske_sestre'):
        insert_nurses = True
      if option in ('-z', '--zdravniki'):
        insert_doctors = True
      if option in ('-p', '--pomoc'):
        print_help = True
    return insert_doctors, insert_nurses, print_help
      
  except getopt.GetoptError:
    print 'Podali ste napacne parametre.\n'
  
  return (False, False, True)

def load_inports(insert_doctors=False, insert_nurses=False, print_help=True):
  
  if print_help:
    help()
    return
  
  if insert_nurses:
    data.input.input_nurses()
  
  if insert_doctors:
    data.input.input_doctors()

def help():
  message = """Ta program se uporablja za vnos podatkov v aplikacijo, pri cemer se izbrise stare podatke.
  Uporaba: V konzolo vpisemo ime programa, ki mu sledijo paramteri. 
           Parametri so loceni s presledki.
  Parametri:
    -s ali --medicinske_sestre:
      izbrise obstojece medicinske sestre in vnese nove
    -z ali --zdravniki:
      izbrise obstojece zdravnike in vnese nove
    -h ali --pomoc:
      izpise to sporocilo"""
    
  print message

if __name__ == '__main__':
  insert_doctors, insert_nurses, print_help = parse()
  load_inports(insert_doctors, insert_nurses, print_help)
  try:
    input('\nPritisnite enter za izhod.\n')
  except:
    pass
