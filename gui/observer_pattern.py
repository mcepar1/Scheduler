# -*- coding: Cp1250 -*-

"""
This file contains various events, used for the observer pattern. 
"""
import wx
from wx.lib.pubsub import Publisher 

"""
The various event.
"""
SCHEDULER_SAVED = wx.NewId ( )


def send_notification (event):
  """
  A wrapper around the publisher method.
    @param event: the event type
  """
  Publisher.sendMessage (event)
  
def register (method, event):
  """
  A wrapper around the publisher method.
    @param method: the listening method
    @param event:  the listening message
  """
  Publisher.subscribe (method, event)
  