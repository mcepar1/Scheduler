import wx

"""
This class behaves the same way as a normal wxCheckBox.
The only difference is that is also has an attribute
element.
Element is an instance, that is beeing manipulated by
this CheckBox.
"""
class LinkedCheckBox(wx.CheckBox):
  def __init__(self,element,*args,**kwargs):
    wx.CheckBox.__init__(self,*args,**kwargs)
    
    self.element = element
    
