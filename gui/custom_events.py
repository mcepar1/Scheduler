# -*- coding: Cp1250 -*-
"""
An utility class, that contains custom events, that help to maintain the GUI in sync,
restarting the application.
"""

import wx.lib.newevent

"""
This event should be fired only, when an internal value has changed.
"""
UpdateEvent, EVT_UPDATED = wx.lib.newevent.NewCommandEvent ( )

