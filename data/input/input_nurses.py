# -*- coding: Cp1250 -*-

from data.nurse import Nurse, NurseContainer
from utils import time_conversion
from global_vars import nurses, workplaces
from scheduler import person_scheduler
import keyboard

import os
import sys
import csv
import calendar
import datetime


def input_nurses():
  print 'Zacetek vzpostavljanja zacetnega stanja medicinskih sester.'
  input_persons()
  input_last_month()
  print 'Zacetno stanje medicinskih sester vzpostavljeno.'
  
def input_persons():
  FILES_DIR = os.path.join('persistence', 'data', 'start_data')
  FILE_NAME = 'sestre.csv'
  
  print 'Zaceli boste z vnosom medicinskih sester.'
  
  sys.stdout.write('\tBranje datoteke...')
  f = file(os.path.join(FILES_DIR, FILE_NAME), 'rb')
  reader = csv.reader(f)
  sys.stdout.write('OK\n')
  
  nurses = []
  for row in reader:
    sys.stdout.write('\tUstvarjanje medicinske sestre: ' + str(row) + '...')
    row[-1] = time_conversion.string_to_date(row[-1])
    nurses.append(Nurse(*row))
    sys.stdout.write('OK\n')
  
  sys.stdout.write('\tBrisanje starih in pisanje novih medicinskih sester ...')
  nc = NurseContainer(sorted(nurses))
  nc.save()
  sys.stdout.write('OK\n')
  
  print 'Konec vnosa medicinskih sester\n'
  
def input_last_month():
  
  print 'Zacetek vnosa zadnjega tedna v zadnjem razvrscenem mesecu.'
  
  print 'Vnestie poljuben datum iz zadnjega razvrscenega meseca.'
  date = keyboard.get_date()
  next_date = datetime.date(day=28, month=date.month, year=date.year) + datetime.timedelta(days=10)
  weeks = calendar.Calendar().monthdatescalendar(year=date.year, month=date.month)[-2]
  weeks += calendar.Calendar().monthdatescalendar(year=date.year, month=date.month)[-1]
  weeks += calendar.Calendar().monthdatescalendar(year=next_date.year, month=next_date.month)[0]
  weeks += calendar.Calendar().monthdatescalendar(year=next_date.year, month=next_date.month)[1]
  
  print 'Ali zelite rocno vnesti zadnji razpored v aplikacijo?\nPOZOR: Ce tega ne storite se bodo vsi zadnji dnevi v zadnjem razvrscenem mesecu steli kot nerazvrsceni!'
  manual = keyboard.get_yes_no_choice()
  
  print 'Za potrebe razvrscanja je dovolj, ce vnesemo le zadnja dva tedna v mesecu in prva tedna v naslednjem mesecu.'
  
  ps = person_scheduler.PersonScheduler(nurses.nurses, workplaces.workplaces, date, input_raw=True)
  nurse_map = {}
  for nurse in ps.people:
    nurse_map[nurse] = nurse 
  
  for nurse in nurses.nurses:
    for date in sorted(set(weeks)):
        print 'Vnasamo podatke za medicinsko sestro: ' + str(nurse.as_list())
        print 'Datum: ' + time_conversion.date_to_string(date)
        if manual:
          choice = keyboard.get_three_way_choice()
        else:
          choice = 1
        
        if choice == 2:
          nurse_map[nurse].add_free_day(date)
          print '\tProst dan uspesno dodan.'
        elif choice == 3:
          workplace = keyboard.get_workplace()
          turnus = keyboard.get_turnus()
          nurse_map[nurse].schedule_turnus(date, turnus, workplace)
          print '\tUspesen vnos za:'
          print '\t\t Medicinska sestra: ' + str(nurse_map[nurse])
          print '\t\t Datum: ' + time_conversion.date_to_string(date)
          print '\t\t Delovisce: ' + str(workplace)
          print '\t\t Turnus: ' + str(turnus)
        else:
          print '\tDan je prost za razvrscanje.'
          
  
  sys.stdout.write('Shranjevanje ...')
  ps.save()
  sys.stdout.write('OK\n')
  
  
  


