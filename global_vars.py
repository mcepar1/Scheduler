# -*- coding: utf-8 -*-

"""This script contains global vars, that are accessed throughout the whole GUI. """

from data import turnus, vacation, nurse, doctor, workplace, employment_type

# init the turnuses
turnuses = turnus.load ( )

# init the vacations
vacations = vacation.load ( )

# init the nurses
nurses = nurse.load ( )

# init the doctors
doctors = doctor.load ( )

# init the workplaces
workplaces = workplace.load ( )

# init the employement types
employment_types = employment_type.load ( )

def save():
  """An utility method, that saves all the data"""
  turnuses.save()
  vacations.save()
  nurses.save()
  doctors.save()
  workplaces.save()
  employment_type.save()


"""Following methods are used to set the initial state
DO NOT USE THEM UNLESS YOU KNOW WHAT YOU ARE DOING"""
def set_turnuses():
  import datetime
  hardcoded_turnuses = [
                         ['D', 'eno izmensko',datetime.time(hour = 8), datetime.time(hour = 16)],
                         ['D', 'več izmensko',datetime.time(hour = 7), datetime.time(hour = 14)],
                         ['P', 'več izmensko',datetime.time(hour = 14), datetime.time(hour = 19)],
                         ['N', 'več izmensko',datetime.time(hour = 19), datetime.time(hour = 7)],
                         ['C', 'celodnevno',datetime.time(hour = 7), datetime.time(hour = 19)],
                         
                         ['D', 'več izmensko',datetime.time(hour = 7), datetime.time(hour = 11)],
                         ['P', 'več izmensko',datetime.time(hour = 14), datetime.time(hour = 18)],
                       ]
  
  turnuses.turnuses = []                     
  for new_turnus in hardcoded_turnuses:
    turnuses.add_all([turnus.Turnus(new_turnus[0], new_turnus[1], new_turnus[2], new_turnus[3])])
    
  turnuses.save()


def set_vacations():
  hardcoded_vacations = [
                          ["X","državni praznik"],
                          ["L","letni dopust - tek. leto"],
                          ["T","letni dopust - pre. leto"],
                          ["S","izred. plač. dopust"],
                          ["Š","študijski dopust"],
                          ["O","plačana odsotnost"],
                          ["Y","neplačana odsotnost"],
                          ["B","bolniška odsotnost"],
                          ["R","porodniški dopust"]
                        ]
        
  vacations.vacations = []      
  for new_vacation in hardcoded_vacations:
    vacations.vacations.append(vacation.Vacation(new_vacation[0], new_vacation[1]))
    
  vacations.save()
  
def set_nurses():
  hardcoded_nurses = [
                      ["Marija","Šraj"],
                      ["Nadja","Robič"],
                      ["Mateja","Segulin"],
                      ["Nika","Valenčič"],
                      ["Kristina","Košmrlj"],
                      ["Neža","Skrt"]
                     ]
                    
  nurses = nurse.NurseContainer()
  for new_nurse in hardcoded_nurses:
    nurses.add_all([nurse.Nurse(new_nurse[0], new_nurse[1])])
    
  nurses.save()
  
def set_doctors():
  hardcoded_doctors = [
                       ["Matjaž","Čepar"],
                       ["Matej","Ravšelj"],
                       ["Miloš","Čotar"],
                       ["Simon","Križman"],
                       ["Davor","Petrinja"],
                       ["Urban","Jernejčič"]
                      ]
  
  doctors = doctor.DoctorContainer()
  for new_doctor in hardcoded_doctors:
    doctors.add_all([doctor.Doctor(new_doctor[0], new_doctor[1])])
    
  doctors.save()
  
def set_workplaces():
  hardcoded_workplaces =  [
                            ["Ambulanta"]
                          ]
                      
  workplaces = workplace.WorkplaceContainer()
  for new_workplace in hardcoded_workplaces:
    workplaces.add_all([workplace.Workplace(new_workplace[0])])
    
  workplaces.save()
  
def set_employement_types():
  hardcoded_employment_types = [
                                  ['Normalna zaposlitev', 40, 200, True, turnuses.turnuses[:5]],
                                  ['Polovicen delovni cas', 20, 100, False, turnuses.turnuses[-2:]],
                                  ['35 ur/teden', 35, 150, True, turnuses.turnuses[:3] + [turnuses.turnuses[4]]]
                                ]
  
  employment_types = employment_type.EmploymentTypeContainer()                              
  for new_employment_type in hardcoded_employment_types:
    employment_types.add_all([employment_type.EmploymentType(new_employment_type[0], new_employment_type[1], new_employment_type[2], new_employment_type[3], new_employment_type[4])])
    
  employment_types.save()

"""Uncomment the correct method to reset the specific data"""
#set_turnuses()
#set_vacations()  
#set_nurses()
#set_doctors()
#set_workplaces()
#set_employement_types()

  
