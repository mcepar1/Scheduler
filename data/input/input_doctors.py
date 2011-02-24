# -*- coding: Cp1250 -*-
"""
from data.doctor import Doctor, DoctorContainer
from utils import time_conversion
from global_vars import doctors, workplaces
from scheduler import person_scheduler
import keyboard

import os
import sys
import csv
import calendar
import datetime


def input_doctors():
  print 'Zacetek vzpostavljanja zacetnega stanja zdravnikov.'
  input_persons()
  input_last_month()
  print 'Zacetno stanje zdravnikov vzpostavljeno.'
  
def input_persons():
  FILES_DIR = os.path.join('persistence', 'data', 'start_data')
  FILE_NAME = 'zdravniki.csv'
  
  print 'Zaceli boste z vnosom zdravnikov.'
  
  sys.stdout.write('\tBranje datoteke...')
  f = file(os.path.join(FILES_DIR, FILE_NAME), 'rb')
  reader = csv.reader(f)
  sys.stdout.write('OK\n')
  
  doctors = []
  for row in reader:
    sys.stdout.write('\tUstvarjanje zdravnika: ' + str(row) + '...')
    row[-1] = time_conversion.string_to_date(row[-1])
    doctors.append(Doctor(*row))
    sys.stdout.write('OK\n')
  
  sys.stdout.write('\tBrisanje starih in pisanje novih zdravnikov ...')
  dc = DoctorContainer(sorted(doctors))
  dc.save()
  sys.stdout.write('OK\n')
  
  print 'Konec vnosa zdravnikov\n'
  
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
  
  ps = person_scheduler.PersonScheduler(doctors.doctors, workplaces.get_all ( ), date, input_raw=True)
  doctor_map = {}
  for doctor in ps.people:
    doctor_map[doctor] = doctor 
  
  for doctor in doctors.doctors:
    for date in sorted(set(weeks)):
        print 'Vnasamo podatke za zdravnika: ' + str(doctor.as_list())
        print 'Datum: ' + time_conversion.date_to_string(date)
        if manual:
          choice = keyboard.get_three_way_choice()
        else:
          choice = 1
          
          
        if choice == 2:
          doctor_map[doctor].add_free_day(date)
          print '\tProst dan uspesno dodan.'
        elif choice == 3:
          workplace = keyboard.get_workplace()
          turnus = keyboard.get_turnus()
          doctor_map[doctor].schedule_turnus(date, turnus, workplace)
          print '\tUspesen vnos za:'
          print '\t\t Zdravnik: ' + str(doctor_map[doctor])
          print '\t\t Datum: ' + time_conversion.date_to_string(date)
          print '\t\t Delovisce: ' + str(workplace)
          print '\t\t Turnus: ' + str(turnus)
        else:
          print '\tDan je prost za razvrscanje.'
          
  
  sys.stdout.write('Shranjevanje ...')
  ps.save(force=True)
  sys.stdout.write('OK\n')
  
"""  
  


