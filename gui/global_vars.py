# -*- coding: utf-8 -*-

"""This script contains global vars, that are accessed throughout the whole GUI. """

from data import turnus, holiday, nurse, doctor

# init the turnuses
turnuses = turnus.TurnusContainer()
turnuses.load()

# init the holidays
holidays = holiday.HolidayContainer()
holidays.load()

# init the nurses
nurses = nurse.NurseContainer()
nurses.load()

doctors = doctor.DoctorContainer()
doctors.load()

def save():
  """An utility method, that saves all the data"""
  turnuses.save()
  holidays.save()
  nurses.save()
  doctors.save()


"""Following methods are used to set the initial state
DO NOT USE THEM UNLESS YOU KNOW WHAT YOU ARE DOING"""
def set_turnuses():
  pass


def set_holidays():
  hardcoded_holidays = [
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
        
  holidays.holidays = []      
  for new_holiday in hardcoded_holidays:
    holidays.holidays.append(holiday.Holiday(new_holiday[0], new_holiday[1]))
    
  holidays.save()
  
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

"""Uncomment the correct method to reset the specific data"""
#set_turnuses()
#set_holidays()  
#set_nurses()
#set_doctors()
  
