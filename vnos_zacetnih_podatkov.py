"""
This file is used to set the initial state of the application.
If you use this way of importing data, all the already inserted data
will be lost!
"""

import sys
import getopt

import data.input


def parse():
  error_ret = (False, False, False, False, False, False, False, True)
  
  try:
    options, _ = getopt.gnu_getopt(sys.argv[1:], 'szptdevna', ['medicinske_sestre', 'zdravniki', 'pomoc', 'turnusi', 'dopusti', 'delovisca', 'zaposlitve', 'nazivi', 'vsi'])
    
    insert_nurses = False
    insert_doctors = False
    insert_turnuses = False
    insert_vacations = False
    insert_workplaces = False
    insert_employment_types = False
    insert_titles = False
    print_help = False
    
    #if no parameter was given
    if not options:
      return error_ret
    
    for option, _ in options:
      if option in ('-s', '--medicinske_sestre'):
        insert_nurses = True
      if option in ('-z', '--zdravniki'):
        insert_doctors = True
      if option in ('-t', '--turnusi'):
        insert_turnuses = True
      if option in ('-p', '--pomoc'):
        print_help = True
      if option in ('-d', '--dopusti'):
        insert_vacations = True
      if option in ('-e', '--delovisca'):
        insert_workplaces = True
      if option in ('-v', '--zaposlitve'):
        insert_employment_types = True
      if option in ('-n', '--nazivi'):
        insert_titles = True
      if option in ('-a', '--vsi'):
        insert_nurses = True
        insert_doctors = True
        insert_turnuses = True
        insert_vacations = True
        insert_workplaces = True
        insert_employment_types = True
        insert_titles = True
        print_help = False
    return insert_doctors, insert_nurses, insert_turnuses, insert_vacations, insert_workplaces, insert_employment_types, insert_titles, print_help
      
  except getopt.GetoptError:
    print 'Podali ste napacne parametre.\n'
  
  return error_ret

def load_inports(insert_doctors=False, insert_nurses=False, insert_turnuses=False, insert_vacations=False, insert_workplaces=False, insert_employment_types=False, insert_titles=False, print_help=True):
  
  if print_help:
    help()
    return
  try: 
    if insert_turnuses:
      data.input.input_turnuses()
      
    if insert_vacations:
      data.input.input_vacations()
      
    if insert_workplaces:
      data.input.input_workplaces()
      
    if insert_titles:
      data.input.input_titles()
      
    if insert_employment_types:
      data.input.input_employment_types()
      
    if insert_nurses:
      data.input.input_nurses()
    
    if insert_doctors:
      data.input.input_doctors()
  except IOError as e:
    print '\n\nManjka datoteka: ' + str(e.filename)

def help():
  message = """Ta program se uporablja za vnos podatkov v aplikacijo, pri cemer se izbrise stare podatke.
  Uporaba: V konzolo vpisemo ime programa, ki mu sledijo paramteri. 
           Parametri so loceni s presledki.
  Parametri:
    -s ali --medicinske_sestre:
      izbrise obstojece medicinske sestre in vnese nove
    -z ali --zdravniki:
      izbrise obstojece zdravnike in vnese nove
    -t ali --turnusi:
      izbrise obstojece turnuse in vnese nove
    -d ali --dopusti:
      izbrise obstojece dopuste in vnese nove
    -e ali --delovisca:
      izprise obstojeca delovisca in vnese nova
    -v ali --zaposltive:
      izbrise obstojece vrste zaposlitve in vnese nove
    -n ali --nazivi:
      izbrise obstojece nazive in vnese nove
    -p ali --pomoc:
      izpise to sporocilo"""
    
  print message

if __name__ == '__main__':
  args = parse()
  load_inports(*args)
  try:
    input('\nPritisnite enter za izhod.\n')
  except:
    pass
