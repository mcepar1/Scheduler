# -*- coding: Cp1250 -*-

from person_gui import PersonPanel
from common import GenericTablePanel
from global_vars import nurses

class NursePanel(GenericTablePanel):
  
  def __init__(self,parent):
    GenericTablePanel.__init__(self, nurses, parent, edit_panel=PersonPanel)
        
      
