# -*- coding: Cp1250 -*-

from Scheduler.gui.person_gui import PersonPanel
from Scheduler.gui.common import GenericTablePanel
from Scheduler.global_vars import nurses

class NursePanel(GenericTablePanel):
  
  def __init__(self,parent):
    GenericTablePanel.__init__(self, nurses, parent, edit_panel=PersonPanel)
        
      
