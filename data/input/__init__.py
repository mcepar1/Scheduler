# -*- coding: Cp1250 -*-

import input_nurses as inurses
import input_turnuses as iturnuses
import input_vacations as ivacations
import input_workplaces as iworkplaces
import input_employment_types as iemployment_types
import input_titles as ititles
import input_turnus_types as iturnus_types
import input_roles as iroles

# load the global data first
import data
import global_vars
args = data.load ( )
inv = [global_vars.set_vacations, 
       global_vars.set_titles, 
       global_vars.set_turnus_types,
       global_vars.set_roles,
       global_vars.set_turnuses,
       global_vars.set_workplaces,
       global_vars.set_employment_types,
       global_vars.set_nurses]
    
for i, method in enumerate (inv):
  method (args[i])
  
def input_nurses():
  inurses.input_nurses()

def input_turnuses():
  iturnuses.input_turnuses()
  
def input_vacations():
  ivacations.input_vacations()
  
def input_workplaces():
  iworkplaces.input_workplaces()
  
def input_employment_types():
  iemployment_types.input_emplyment_types()
  
def input_titles():
  ititles.input_titles()

def input_turnus_types():
  iturnus_types.input_turnus_types()
  
def input_roles():
  iroles.input_roles()
  
