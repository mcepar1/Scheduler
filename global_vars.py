# -*- coding: utf-8 -*-

"""This script contains global vars, that are accessed throughout the whole GUI. """

from data import turnus, vacation, nurse, doctor, workplace, employment_type

# init the turnuses
turnuses = turnus.load ()

# init the vacations
vacations = vacation.load ()

# init the nurses
nurses = nurse.load ()

# init the doctors
doctors = doctor.load ()

# init the workplaces
workplaces = workplace.load ()

# init the employement types
employment_types = employment_type.load ()

def save():
  """An utility method, that saves all the data"""
  turnuses.save()
  vacations.save()
  nurses.save()
  doctors.save()
  workplaces.save()
  employment_types.save()


"""Following methods are used to set the initial state
DO NOT USE THEM UNLESS YOU KNOW WHAT YOU ARE DOING"""
def set_turnuses():
  import datetime
  hardcoded_turnuses = [
                         ['D', 'eno izmensko', datetime.time(hour=7), datetime.time(hour=15), datetime.timedelta(hours=8), datetime.timedelta(hours=12), False],
                         ['D', 'vec izmensko', datetime.time(hour=7), datetime.time(hour=14), datetime.timedelta(hours=7), datetime.timedelta(hours=12), False],
                         ['P', 'vec izmensko', datetime.time(hour=14), datetime.time(hour=21), datetime.timedelta(hours=7), datetime.timedelta(hours=12), False],
                         ['N', 'vec izmensko', datetime.time(hour=21), datetime.time(hour=7), datetime.timedelta(hours=10), datetime.timedelta(hours=12), False],
                         ['N', 'vec izmensko (nedelja)', datetime.time(hour=19), datetime.time(hour=7), datetime.timedelta(hours=12), datetime.timedelta(hours=12), True],
                         ['C', 'celodnevno', datetime.time(hour=7), datetime.time(hour=19), datetime.timedelta(hours=12), datetime.timedelta(hours=12), True],
                         
                         ['D-', 'vec izmensko', datetime.time(hour=7), datetime.time(hour=14), datetime.timedelta(hours=4), datetime.timedelta(hours=12), False],
                         ['P-', 'vec izmensko', datetime.time(hour=14), datetime.time(hour=21), datetime.timedelta(hours=4), datetime.timedelta(hours=12), False],
                         
                         ['D8', 'tro izmensko', datetime.time(hour=7), datetime.time(hour=15), datetime.timedelta(hours=8), datetime.timedelta(hours=12), False],
                         ['P8', 'tro izmensko', datetime.time(hour=15), datetime.time(hour=23), datetime.timedelta(hours=8), datetime.timedelta(hours=12), False],
                         ['N8', 'tro izmensko', datetime.time(hour=23), datetime.time(hour=7), datetime.timedelta(hours=8), datetime.timedelta(hours=12), False],
                         
                         ['E', 'dezurna', datetime.time(hour=7), datetime.time(hour=7), datetime.timedelta(hours=24), datetime.timedelta(hours=12), False],
                         ['I', 'pripravljenost', datetime.time(hour=15), datetime.time(hour=7), datetime.timedelta(hours=24), datetime.timedelta(hours=12), False],
                         ['I-TX', 'pripravljenost za transplantacijo', datetime.time(hour=15), datetime.time(hour=7), datetime.timedelta(hours=24), datetime.timedelta(hours=12), False],
                         ['D-', 'dopoldanska po dezurni', datetime.time(hour=7), datetime.time(hour=11), datetime.timedelta(hours=4), datetime.timedelta(hours=12), False]
                       ]
  
  turnuses.turnuses = []                     
  for new_turnus in hardcoded_turnuses:
    turnuses.add_all([turnus.Turnus(*new_turnus)])
    
  turnuses.save()


def set_vacations():
  hardcoded_vacations = [
                          ["X", "drzavni praznik"],
                          ["L", "letni dopust - tek. leto"],
                          ["T", "letni dopust - pre. leto"],
                          ["S", "izred. plac. dopust"],
                          ["Š", "studijski dopust"],
                          ["O", "placana odsotnost"],
                          ["Y", "neplacana odsotnost"],
                          ["B", "bolniska odsotnost"],
                          ["R", "porodniski dopust"]
                        ]
        
  vacations.vacations = []      
  for new_vacation in hardcoded_vacations:
    vacations.vacations.append(vacation.Vacation(new_vacation[0], new_vacation[1]))
    
  vacations.save()
  
  
def set_workplaces():
  hardcoded_workplaces = [
                            ["Ambulanta" , False],
                            ["Navadna nega (odd)", True],
                            ["Intenzivna terapija A", True],
                            ["Intenzivna terapija B", True],
                            ["Intenzivna nega", True],
                            ["Perfuzija", False],
                            ["Administracija", False]
                          ]
                      
  workplaces = workplace.WorkplaceContainer()
  for new_workplace in hardcoded_workplaces:
    workplaces.add_all([workplace.Workplace(*new_workplace)])
    
  workplaces.save()
  
def set_employement_types():
  hardcoded_employment_types = [
                                  ['Medicinska sestra: Normalna zaposlitev', 40, True, turnuses.turnuses[8:11]],
                                  ['Medicinska sestra: Polovicen delovni cas', 20, False, turnuses.turnuses[6:8]],
                                  ['Medicinska sestra: 35 ur/teden', 35, True, turnuses.turnuses[:4]],
                                  ['Zdravnik: Normalna zaposlitev', 40, True, turnuses.turnuses[:5] + turnuses.turnuses[-4:]]
                                ]
  
  employment_types = employment_type.EmploymentTypeContainer()                              
  for new_employment_type in hardcoded_employment_types:
    employment_types.add_all([employment_type.EmploymentType(*new_employment_type)])
    
  employment_types.save()

"""Uncomment the correct method to reset the specific data"""
#set_turnuses()
#set_vacations()
#set_workplaces()
#set_employement_types()  
#use the vnos_zactinh_podatkov.py script for inserting nurses or doctor
  
