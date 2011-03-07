# -*- coding: Cp1250 -*-

from data import nurse

from scheduler import person as person_module
from scheduler import workplace as workplace_module
from scheduler import weights
from scheduler import modules

import global_vars
import log
from utils import time_conversion, holiday
from data import turnus_type

import random
import datetime
import calendar
import cPickle as pickle
import os
    
"""
Contains the plug-ins, that will be used in this scheduler.
The order is important!
"""    
PLUG_INS = [modules.PreSchedulerPlugin, modules.HolidayRulePlugin] 

"""
Contains the plug-ins, that are used after the scheduling phase.
"""
CLEAN_UP = []#modules.WeekMorning, modules.FillHours]

class PersonScheduler:
  FILES_DIR = os.path.join("persistence", "scheduler")
  DOCTOR_DIR = 'doctors'
  NURSE_DIR = 'nurses'

  def __init__(self, people, workplaces, date, input_raw=False, log=log.DummyLog()):
    """
    The default constructor.
      people: a list of all the people, that will be scheduled
      workplaces: a list of workplaces, that the people will be scheduled into
      date: is the starting date of the scheduling
      input_raw: a boolean that tells the scheduler, not perform certain tasks, thus
                 enabling total control over data input
      log: a class that is capable of outputting log results
    """
    
    self.log = log
    
    self.log.send_message('Ustvarjam razvrscevalnik ...')
    
    if not people:
      raise Exception('Ni nobene osebe za razvrscanje')
    
    schedule_nurses = False
    
    for person in people:
      if isinstance(person, nurse.Nurse):
        schedule_nurses = True
      else:
        raise Exception('Razvrščamo lahko le medicinske sestre sestre.')
      
    
    # if this point is reached, the the parameters are legal
    self.file_dir = ''
    if schedule_nurses:
      self.file_dir = os.path.join(PersonScheduler.FILES_DIR, PersonScheduler.NURSE_DIR)
    
    
    self.people = []
    for person in people:
      if person.allowed_turnuses or input_raw:
        if schedule_nurses:
          self.people.append(person_module.Nurse(person))
        self.people[-1].add_month (date)
        #add the next month, because it may overflow
        self.people[-1].add_month(datetime.date(day=28, month=date.month, year=date.year) + datetime.timedelta(days=10))
    
    if not input_raw:
      self.__get_previous_month(date)
      
    
    self.workplaces = set ()
    for workplace_ in workplaces:
      self.workplaces.add(workplace_module.Workplace(workplace_))
    # transform to list again, so it can be shuffled
    self.workplaces = list(self.workplaces)
    
    self.date = date
    
    #set various maps, for the ease of access
    
    #maps workplaces to people
    self.workplace_people = {}
    for workplace in global_vars.get_workplaces( ).get_all ( ):
      self.workplace_people[workplace] = set()
    
    for workplace in self.workplaces:
      self.workplace_people[workplace] = set()
      for person in self.people:
        if workplace in person.workplaces:
          self.workplace_people[workplace].add(person)
        
    #maps employment types to people
    self.employment_type_people = {}
    for employment_type in global_vars.get_employment_types ( ).get_all ( ):
      self.employment_type_people[employment_type] = set ()
    
    for person in self.people:
      if person.employment_type not in self.employment_type_people:
        self.employment_type_people[person.employment_type] = set()
      self.employment_type_people[person.employment_type].add(person)
      
    #maps turnuses to people
    self.turnus_people = {}
    for turnus in global_vars.get_turnuses ( ).get_all ( ):
      self.turnus_people[turnus] = set ()
    
    for person in self.people:
      for turnus in person.allowed_turnuses:
        if turnus not in self.turnus_people:
          self.turnus_people[turnus] = set()
        self.turnus_people[turnus].add(person)
        
    # maps roles to people    
    self.role_people = {}
    for person in self.people:
      for workplace in person.roles:
        for role in person.roles[workplace]:
          if role not in self.role_people:
            self.role_people[role] = set()
          self.role_people[role].add (person)
     
    # no auto execution, when inputing raw_data
    self.active_plugins = []
    self.clean_up_plugins = []
    if not input_raw:    
      for plug_in in PLUG_INS:
        self.active_plugins.append(plug_in(self.people, self.workplaces, global_vars.get_turnuses ( ).get_all ( ), self.date, self.log))
      for plug_in in CLEAN_UP:
        self.clean_up_plugins.append(plug_in(self.people, self.workplaces, global_vars.get_turnuses ( ).get_all ( ), self.date, self.log))
    
        
      
      
    
    
  def __get_previous_month(self, date):
    """
    This reloads the previously scheduled month into the application.
      date: is the current schedule date
    """
    
    prev_date = datetime.date(day=1, month=date.month, year=date.year) - datetime.timedelta (days=1) 
    filename = str(prev_date.month) + '_' + str(prev_date.year) + '.dat'
    
    try:
      old_people = pickle.load(file(os.path.join(self.file_dir, filename), 'rb'))
    except Exception:
      #raise Exception('Ni podatkov o prejsnjem mesecu v aplikaciji.')
      old_people = []
    
    for person in self.people:
      for old_person in old_people:
        if person == old_person:
          #we can always do that, because the past is always right
          person.load_previous_month(old_person, prev_date)
          

  def schedule(self):
    dates = [datetime.date(day=day, month=self.date.month, year=self.date.year) for day in self.__get_days()]
    
    
    no_ovetime_people = set()
    for person in self.people:
      if not person.employment_type.has_overtime:
        no_ovetime_people.add(person)
    
    self.log.send_message('Prva faza razvrscanja ...')
    #invoke the plugins
    for plugin in self.active_plugins:
      plugin.perform_task (overtime=False) 
    
    """
    #for each date and workplace go through each allowed turnus and add 
    #one employee, until reaching the point, where the overtime is needed
    #or enough workers are working in a turnus
    scheduled = True
    overtime_people = set(self.people) - no_ovetime_people
    
    
    while (scheduled):
      #start with workplaces
      random.shuffle(self.workplaces)
      
      scheduled = False
      for workplace in self.workplaces:
        for date in dates:
          scheduled = scheduled | self.__schedule_workplace(workplace, date, overtime_people, overtime=False)
          
    self.log.send_message('Druga faza razvrscanja ...')
    #repeat the process for the part-time employees
    
    
    #invoke the plugins
    for plugin in self.active_plugins:
      plugin.perform_task (overtime=False)
    
    scheduled = True
    
    while (scheduled):
      #start with workplaces
      random.shuffle(self.workplaces)
      scheduled = False
      for workplace in self.workplaces:
        for date in dates:
          scheduled = scheduled | self.__schedule_workplace(workplace, date, no_ovetime_people, overtime=False)
          
          
    self.log.send_message('Tretja faza razvrscanja ...')
    #finally add all the people, including the ones with the overtime
    """
    #invoke the plugins
    for plugin in self.active_plugins:
      plugin.perform_task (overtime=True)
    """
    scheduled = True
    people = set(self.people)
    
    
    while (scheduled):
      #start with workplaces
      random.shuffle(self.workplaces)
      scheduled = False
      for workplace in self.workplaces:
        for date in dates:
          scheduled = scheduled | self.__schedule_workplace(workplace, date, people, overtime=True)
    
          
    """
    self.log.send_message('Zadnja faza razvrscanja ...')
    for plugin in self.clean_up_plugins:
      plugin.perform_task (overtime=True)      
    #self.print_human_readable_output()
    
  def get_schedule_matrix(self):
    """
    Returns a matrix, that is close to what the final output might be.
    """
    dates = [datetime.date(day=day, month=self.date.month, year=self.date.year) for day in self.__get_days()]
    #dates = sorted(self.people[0].scheduled_turnus.keys())
    scheduled = {}
    
    for person in self.people:
      scheduled[person] = []
      for date in dates:
        temp = person.get_scheduled(date)
        scheduled[person].append(temp[0] + '\n' + temp[1] + '\n' + temp[2])
        
    headers = ['Oseba']
    for date in dates:
      headers.append(time_conversion.date_to_string(date))
    headers.append('Nadure')
    lines = [headers]
    for person in self.people:
      lines.append([])
      lines[-1].append(str(person))
      lines[-1] += scheduled[person]
      lines[-1].append(str(person.get_monthly_hours_difference(self.date)))
      
    return lines
  
  def get_workplace_matrix(self):
    """
    Returns a dictionary, that maps workplaces to roles and roles to a schedule matrix, 
    that contains only persons and turnuses, that were scheduled into this role - 
    workplace pair.
    """
    map = {}
    dates = sorted([datetime.date(day=day, month=self.date.month, year=self.date.year) for day in self.__get_days()])
    
    headers = ['Oseba']
    for date in dates:
      headers.append(time_conversion.date_to_string(date))
    
    for workplace in self.workplaces:
      map[workplace] = {}
      for role in workplace.roles:
        
        map[workplace][role] = [headers] 
        people = []
        if role in self.role_people and workplace in self.workplace_people:
          for person in self.workplace_people[workplace] & self.role_people[role]:
            if workplace in person.roles and role in person.roles[workplace]:
              people.append(person)
        
        for person in people:
          person_schedule = [str(person)]
          for date in dates:
              turnus = person.get_turnus(date, workplace, role)
              if turnus:
                person_schedule.append(turnus.code[0])
              else:
                person_schedule.append('')
          map[workplace][role].append(person_schedule)
    
    return map
            
          
  
  def get_workplace_warnings(self):
    """
    Returns workplace warnings.
      returns: a nested dictionary that maps workplaces to roles, roles to turnuses, 
               turnuses to dates and dates to warning messages
    """
    
    dates = [datetime.date(day=day, month=self.date.month, year=self.date.year) for day in self.__get_days()]
    
    
    temp = {}
    
    for workplace in sorted(self.workplaces):
      for date in sorted(dates):
        workers = workplace.get_workers(date)
        #turnus_types = workers.keys()
        roles = workers.keys()
        for role in sorted(roles):
          turnus_types = workers[role].keys()
          for turnus_type in sorted(turnus_types):
            needed = workers[role][turnus_type]
            scheduled = self.__get_alerady_scheduled_by_type(workplace, role, [turnus_type], date)[turnus_type]
            if scheduled < needed or scheduled > needed:
              if workplace not in temp:
                temp[workplace] = {}
              if role not in temp[workplace]:
                temp[workplace][role] = {}
              if turnus_type not in temp[workplace][role]:
                temp[workplace][role][turnus_type] = {}
              
              if scheduled < needed:
                temp[workplace][role][turnus_type][date] = 'Premalo:' + str(needed - scheduled)
              elif scheduled > needed:
                temp[workplace][role][turnus_type][date] = 'Prevec:' + str(scheduled - needed)
    
    return temp
        
  
  def save(self, force=False):
    """
    Saves the schedule.
      force: if this parameter is set to true, it will override any existing file,
             if it is set to false, it will not override the file
      return: True, if the schedule has been saved, false otherwise
    """
    
    filename = str(self.date.month) + '_' + str(self.date.year) + '.dat'
    path = os.path.join(self.file_dir, filename)
    
    if not os.path.isfile(path) or force:
      prev_month = datetime.date(day=1, month=self.date.month, year=self.date.year) - datetime.timedelta(days=1)
      prev_month.replace (day=1)
      
      for person in self.people:
        for date in person.get_scheduled_dates():
          if date < prev_month:
            person.remove_scheduled_date(date)
      
      pickle.dump(self.people, file(path, 'wb'))
      return True
    else:
      return False
    
  def __schedule_workplace(self, workplace, date, people=[], overtime=False):
    """
    Schedules a single person into each allowed workplace's roles and turnuses.
      workplace: the workplace, that will be scheduled
      date: the date for which the scheduling will occur
      people: a collection of people to chose form, default value is an empty list
      overtime: allow scheduling people with overtime, default value is false
      return: false, if no person was scheduled, true if at least one person was scheduled
    """
    
    workers = workplace.get_workers(date)
    
    roles = list(workers.keys())
    random.shuffle(roles)
    
    scheduled = False
    for role in roles:
      if self.__schedule_role(workplace, role, date, workers[role], people, overtime):
        scheduled = True
        
    return scheduled
    
  def __schedule_role(self, workplace, role, date, workers, people=[], overtime=False):
    """
    Schedules a single person into the workplace - role pair.
      workplace: is the workplace
      role: is the role
      date:is the date
      workers: are role specific workers
      people: a list of people to choose from, default value is an empty list
      overtime: allow scheduling people with overtime, default value is false
      return: false, if no person was scheduled, true if at least one person was scheduled
    """

    turnuses = []
    for type in workers.keys():
      turnuses += list(global_vars.get_turnuses ( ).get_by_type(type, workplace))
    
    random.shuffle(turnuses)

    
    scheduled = False
    for turnus in turnuses:
      #if there are enough workers, schedule none
      if self.__can_continue_scheduling(self.__get_alerady_scheduled_by_type(workplace, role, turnus.types, date), workers):
        heuritsitc_people = self.__get_heuristic_sorted_people(people & self.workplace_people[workplace] & self.turnus_people[turnus] & self.role_people[role] , date)
        while (len(heuritsitc_people) > 0):
          person = heuritsitc_people.pop(0)
          if self.__schedule_person(workplace, role, turnus, date, person, overtime):
            scheduled = scheduled | True
            break
          else:
            scheduled = scheduled | False
      else:
        scheduled = scheduled | False
        
    return scheduled
    
      
  def __schedule_person(self, workplace, role, turnus, date, person, overtime):
    """
    Tries to schedule the person.
      workplace: is the workplace, that we want scheduled
      role: is the role, that we want scheduled
      turnus: is the turnus, that we want scheduled
      date: is the turnus, that we want scheduled
      person: is the person, that we want scheduled
      overtime: if true, overtime is allowed
      return: true: if the person was scheduled, false otherwise
    """
    
    if self.__is_valid_move(workplace, role, turnus, date, person, overtime):
      person.schedule_turnus (date, turnus, workplace, role)
      
      #block the previous and next days, if it was the night turnus
      if turnus.code[0] == 'N' and not person.is_blocked(date - datetime.timedelta(days=1), turnus):
        person.add_invalid_turnus(date - datetime.timedelta(days=1), turnus)
        person.add_invalid_turnus(date + datetime.timedelta(days=1), turnus)
        
      
      # the is valid move has taken care of any potential violations, so that you
      # can just schedule turnuses
      if person.packet_night_turnuses and turnus.code[0] == 'N':
        next_date = date + datetime.timedelta(days=1)
        person.schedule_turnus (next_date, turnus, workplace, role)
        #if it is Saturday, schedule one more
        if next_date.weekday() == 5:
          next_date += datetime.timedelta(days=1)
          #find the workfree night turnus
          night_turnus = None
          for temp_turnus in global_vars.get_turnuses ( ).get_all ( ):
            if temp_turnus.holiday and temp_turnus.code[0] == 'N':
              night_turnus = temp_turnus
              break
          else:
            raise Exception ('Napaka pri dodajanju osebe z zdruzenimi nocnimi turnusi.')
          person.schedule_turnus(next_date, night_turnus, workplace, role)
          if turnus.code[0] == 'N' and not person.is_blocked(next_date + datetime.timedelta(days=1), turnus):
            person.add_invalid_turnus(next_date + datetime.timedelta(days=1), turnus)
        else:
          if turnus.code[0] == 'N' and not person.is_blocked(next_date + datetime.timedelta(days=1), turnus):
            person.add_invalid_turnus(next_date + datetime.timedelta(days=1), turnus)
      
      if holiday.is_workfree(date):
        self.__add_free_day(person, date)
      return True
    else:
      return False
      

  def __is_valid_move(self, workplace, role, turnus, date, person, overtime, depth=0, check_turnuses=[]):
    """
    Checks, if the person is allowed to work, on the combination of attributes.
      workplace: is the workplace checked
      role: is the role checked
      turnus: is the turnus checked
      date: is the date checked
      person: is the person checked
      overtime: if the overtime is allowed for the person
      depth: depth of the recursion. Never set this parameter when calling the method 
            form the outside
      check_turnuses: is a list of turnuses. This list contains turnuses that were 
                      checked in the previous recursions. They are needed for calculating
                      the potential overtime. Never set this parameter when calling the
                      method from the outside.
    """
    
    
    if turnus not in person.allowed_turnuses:
      return False
    
    if person.is_turnus_forbidden(turnus, date):
      return False
    
    if person.is_blocked(date, turnus):
      return False
    
    #block the workfree night turnus, if the day is not workfree
    if turnus.holiday and turnus.code[0] == 'N' and not holiday.is_workfree(date):
      return False
    
    #check the role
    if role not in workplace.roles or workplace not in person.roles or role not in person.roles[workplace]:
      return False
    
    #also check the people's employment type
    if not overtime or not person.employment_type.has_overtime:
      mh = person.get_monthly_hours_difference(date)
      wh = person.get_weekly_hours_difference(date)
      
      duration = time_conversion.timedelta_to_hours(turnus.duration)
      for prev_turnus in check_turnuses:
        duration += time_conversion.timedelta_to_hours(prev_turnus.duration)
      
      if mh - duration < 0:
        return False
      if wh - duration < 0:
        return False
      
    if holiday.is_workfree(date):
      # check if this a turnus, that can be scheduled in a workfree day
      if not turnus.holiday:
        return False
      
      #check for free days
      #check previous week
      week = self.__get_previous_week(date)
      for date_ in week:
        if person.is_free_day(date_):
          break
      else:
        #if there was no free day the previous week, perhaps there is in the next
        week = self.__get_next_week(date)
        for date_ in week:
          if person.is_free_day(date_):
            break
        else:
          # no free day was found
          return False
      
      # if the workplace has the special rule: work in the afternoon, if the next
      # day is a work free day and you will work the next day, and you won't work
      # the next day, work in the morning or not at all
      if workplace.holiday_rule:
        if holiday.is_workfree(date):
          prev_date = date - datetime.timedelta(days=1)
          prev_turnus = person.get_turnus(prev_date) 
          if prev_turnus:
            # all afternoon codes start with P
            # all double shift codes start with C
            # TODO: document this
            if prev_turnus.code[0] != 'P' or prev_turnus.code[0] != 'C':
              return False
          else:
            return False
        else:
          next_date = date + datetime.timedelta(days=1)
          if holiday.is_workfree(next_date):
            # this bottom condition is enough, because the dates are added ascending
            if not person.is_free_day(next_date):
              return False
    
    # if the person schedules night turnuses in packages: 
    #  (Monday + Tuesday)
    #  (Tuesday + Wednesday)
    #  (Wednesday + Thursday)
    #  (Friday + Saturday + Sunday)
    if person.packet_night_turnuses and turnus.code[0] == 'N':
      if depth == 0 and (date.weekday() == 0 or date.weekday() == 2 or date.weekday() == 4):
        return self.__is_valid_move(workplace, role, turnus, date + datetime.timedelta(days=1), person, overtime, depth + 1, check_turnuses + [turnus])
      #if this is the second day in the packet continue validation only if it is a Saturday
      elif depth == 1 and date.weekday() == 5:
        # TODO: allow only one holiday turnus per shift type (document this)
        sunday_night_turnus = None
        for alternative_turnus in global_vars.get_turnuses ( ).get_all ( ):
          if alternative_turnus.holiday and alternative_turnus.code[0] == 'N':
            sunday_night_turnus = alternative_turnus
            break
        else:
          return False
        
        return self.__is_valid_move(workplace, role, sunday_night_turnus, date + datetime.timedelta(days=1), person, overtime, depth + 1, check_turnuses + [turnus])
      #Thursday to Friday combination does not exist
      elif depth == 1 and date.weekday() == 4:
        return False
      elif depth == 1:
        return True
      elif depth == 2:
        return True
      
      else:
        return False
        
              
    return True

  
  def __add_free_day(self, person, date):
    """
    Adds a free day to the person, if necessary. See the person.Person.is_free_day_for 
    details.
      person: the person that needs a free day
      date: is the date that contains the week in which the person worked on a work
            free day
    """
    
    #check previous week
    week = self.__get_previous_week(date)
    for date_ in week:
      if person.is_free_day(date_):
        return
    else:
      #if there was no free day the previous week, perhaps there is in the next
      week = self.__get_next_week(date)
      free_day = []
      for date_ in week:
        if person.is_free_day(date_) and not person.is_scheduled(date_):
          free_day.append(date_)
      
      if free_day:
        # add a random not yet scheduled day as a free day
        person.add_free_day(random.choice(free_day))
      else:
        raise Exception('Nisem mogel dodati prostega dneva.')

  def __get_heuristic_sorted_people(self, people, date):
    """
    Returns a sorted list of people, according to their heuristic score.
      people: the list of people, to be sorted
      date: the date that we want scheduled
      return: a list of people
    """
    
    temp = {}
    result = []
    
    for person in people:
      heuristic_score = self.__get_heuristic_score(person, date)
      if heuristic_score not in temp:
        temp[heuristic_score] = []
      temp[heuristic_score].append(person)
      
    for heuristic_score in sorted(temp.keys()):
      result += temp[heuristic_score]
      
    return result
    
  
  def __get_heuristic_score(self, person, date):
    """
    Returns a value. The higher the value, the worst choice the person is.
      person: is the person, that will have the score computed
      date: is the date, that we want scheduled
      return: a float
    """
    
    month_hours = -1 * person.get_monthly_hours_difference(date)
    week_hours = -1 * person.get_weekly_hours_difference(date)
    turnus_dispersion = person.get_turnus_dispersion()
    workplace_dispersion = person.get_workplace_dispersion()
    
    return weights.MONTH_HOURS * month_hours + weights.WEEK_HOURS * week_hours + weights.TURNUS_DISPERSION * turnus_dispersion + weights.WORKPLACE_DISPERSION * workplace_dispersion
  
  def __can_continue_scheduling(self, scheduled_types, workers):
    """
    Checks, if the workplace has enough people working at it, to be considered
    full.
      scheduled_types: a dictionary, that maps turnus types to the number of 
                       currently scheduled turnuses of that type
      workers: a dictionary, that maps turnus types to the number of required
               scheduled turnuses of that type
      return: true, if there aren't enough people working, false otherwise
    """
    
    for type in scheduled_types:
      if scheduled_types[type] < workers[type]:
        return True
    
    return False

  
  def __get_alerady_scheduled_by_type(self, workplace, role, types, date):
    """
    Return the number of currently scheduled people for the specific types
    date and workplace
      workplace: is the workplace
      role: is the role
      types: is the sequence of types
      date: is the date
      return: a dictionary, that maps types to thr number of scheduled turnuses
              for each type
    """
    
    map = {}
    
    for type in types:
      turnuses = global_vars.get_turnuses ( ).get_by_type(type, workplace)
      map[type] = 0
      for turnus in turnuses:
        map[type] += self.__get_already_scheduled(workplace, role, turnus, date)
      
    return map
  
  def __get_already_scheduled(self, workplace, role, turnus, date):
    """
    Returns the number of currently scheduled people, for the specific turnus, 
    date and workplace.
      workplace: is the workplace
      role: is the role
      turnus: is the turnus
      date: is the date
      return: the number of people
    """
    
    number = 0
    for person in self.people:
      if person.is_scheduled_exact(workplace, role, turnus, date):
        number += 1
    
    return number
    
  def __get_scheduled_people(self, date):
    """
    Returns a set of people, that are already scheduled.
      date: is the date that is checked
      return: a set
    """
    
    scheduled = set()
    for person in self.people:
      if person.is_scheduled(date):
        scheduled.add(person)
    
    return scheduled
  
  
  def __get_days(self):
    """Returns a sorted list of days for the scheduling date"""
    days = []
    for day in calendar.Calendar().itermonthdays(self.date.year, self.date.month):
      if day:
        days.append(day)
        
    days.sort()
    
    return days
  
  def __get_week(self, date):
    """
    Returns the week in which the date is located.
      date: instance of the datetime.date class
      return: a list of dates
    """
    
    for week in calendar.Calendar().monthdatescalendar(year=date.year, month=date.month):
      if date in week:
        return week
    else:
      raise Exception('Date week error')
  
  def __get_next_week(self, date):
    """
    Returns all dates in the week after the week in which the date is located.
      date: instance of the datetime.date class
      return: a list of dates
    """
      
    return self.__get_week(date + datetime.timedelta(days=7))
  
  def __get_previous_week(self, date):
    """
    Returns all dates in the week after the week in which the date is located.
      date: instance of the datetime.date class
      return: a list of dates
    """
      
    return self.__get_week(date + datetime.timedelta(days= -7))
  
  def print_human_readable_output(self):
    """Prints a console version of the final output."""
    for line in self.get_schedule_matrix():
      print '\t'.join(line)
      
        
        
      
    
  
  def debug_print_people(self):
    min_date = datetime.date(day=1, month=self.date.month, year=self.date.year)
    
    for person in self.people:
      print str(person)
      schedule = person.get_schedule()
      for date in sorted(schedule.keys()):
        if date >= min_date:
          print '\tDate: ' + str(date)
          print '\t\t Turnus: ' + str(schedule[date][0])
          print '\t\t Workplace: ' + str(schedule[date][1])
      print ''
      
  def debug_print_workplaces(self):
    dates = [datetime.date(day=day, month=self.date.month, year=self.date.year) for day in self.__get_days()]
    
    for workplace in self.workplace_people.keys():
      print str(workplace)
      
      counter = {}
      for turnus in self.turnus_people.keys():
        print '\t' + str(turnus)
        for date in dates:
          counter = 0
          for person in self.people:
            if person.is_scheduled_exact(workplace, turnus, date):
              counter += 1
          
          print '\t\t' + str(date) + ': ' + str(counter)
      
      print ''
