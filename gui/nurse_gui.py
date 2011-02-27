# -*- coding: Cp1250 -*-

from person_gui import PersonPanel
from common import GenericTablePanel
import global_vars

class NursePanel(GenericTablePanel):
  
  def __init__(self,parent):
    GenericTablePanel.__init__(self, global_vars.get_nurses ( ), parent, edit_panel=PersonPanel)
        
      
