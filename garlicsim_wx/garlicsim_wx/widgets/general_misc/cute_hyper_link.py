# Copyright 2009-2011 Ram Rachum.
# This program is distributed under the LGPL2.1 license.

'''
This module defines the `CuteHyperLink` class.

See its documentation for more information.
'''

import wx

from garlicsim_wx.widgets.general_misc.cute_control import CuteControl


class CuteHyperLink(wx.HyperlinkCtrl, CuteControl):
    ''' '''
    def __init__(self, parent, id=-1, label='', url='', pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.HL_DEFAULT_STYLE,
                 name=wx.HyperlinkCtrlNameStr):

        wx.HyperlinkCtrl.__init__(
            parent=parent, id=id, label=label, url=url, pos=pos, size=size, 
            style=style, name=name
        )
        
    
    