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

"""
This event is used for handling grid selection with multiple columns and rows.
"""
ComplexSelectEvent, EVT_COMPLEX_SELECTED = wx.lib.newevent.NewCommandEvent ( )

"""
New events, for easier communication between the tool bar and it's parents.
"""
AddEvent,    EVT_TB_ADD    = wx.lib.newevent.NewCommandEvent ( )
CreateEvent, EVT_TB_CREATE = wx.lib.newevent.NewCommandEvent ( )
OpenEvent,   EVT_TB_OPEN   = wx.lib.newevent.NewCommandEvent ( )
StartEvent,  EVT_TB_START  = wx.lib.newevent.NewCommandEvent ( )
RemoveEvent, EVT_TB_REMOVE = wx.lib.newevent.NewCommandEvent ( )
SaveEvent,   EVT_TB_SAVE   = wx.lib.newevent.NewCommandEvent ( )
ReloadEvent, EVT_TB_RELOAD = wx.lib.newevent.NewCommandEvent ( )
SearchEvent, EVT_TB_SEARCH = wx.lib.newevent.NewCommandEvent ( )
ToggleEvent, EVT_TB_TOGGLE = wx.lib.newevent.NewCommandEvent ( )

