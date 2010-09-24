# Copyright 2009-2010 Ram Rachum. No part of this program may be used, copied
# or distributed without explicit written permission from Ram Rachum.

'''Defines various tools for wxPython.'''

from __future__ import division

import warnings
import colorsys

import wx

from garlicsim.general_misc import caching


@caching.cache()
def get_background_color():
    '''Get the default garlicsim_wx background color'''
    
    if wx.Platform == '__WXMSW__':
        # return wx.Color(212, 208, 200)
        return wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENUBAR)
    elif wx.Platform == '__WXMAC__':
        return wx.Color(232, 232, 232)
    elif wx.Platform == '__WXGTK__':
        # Until SYS_COLOUR_* get their act togother, we're using Windows colors
        # for Linux.
        return wx.Color(212, 208, 200)
    
    else:
        warnings.warn("Unidentified platform! It's neither '__WXGTK__', "
                      "'__WXMAC__' nor '__WXMSW__'. Things might not work "
                      "properly.")
        return wx.Color(212, 208, 200)


@caching.cache()
def get_background_brush():
    '''Get the default garlicsim_wx background brush.'''
    return wx.Brush(get_background_color())


def wx_color_to_html_color(wx_color):
    rgb = wx_color.GetRGB()
    (green_blue, red) = divmod(rgb, 256)
    (blue, green) = divmod(green_blue, 256)
    return '#%02x%02x%02x' % (red, green, blue)


def hls_to_wx_color(hls, alpha=255):
    return rgb_to_wx_color(colorsys.hls_to_rgb(*hls), alpha=alpha)


def wx_color_to_hls(wx_color):
    return colorsys.rgb_to_hls(wx_color.red, wx_color.blue, wx_color.green)


def rgb_to_wx_color(rgb, alpha=255):
    r, g, b = rgb
    return wx.Color(r * 255, g * 255, b * 255, alpha)


def wx_color_to_rgb(wx_color):
    return (
        wx_color.red / 255,
        wx_color.blue / 255,
        wx_color.green / 255
    )


def wx_color_to_big_rgb(wx_color):
    return (
        wx_color.red,
        wx_color.green,
        wx_color.blue
    )


def post_event(evt_handler, event_binder, source=None, **kwargs):
    '''Post an event to an evt_handler.'''
    # todo: Use wherever I post events    
    # todo: possibly it's a problem that I'm using PyEvent here for any type of
    # event, because every event has its own type. but i don't know how to get
    # the event type from `event_binder`. problem.
    event = wx.PyEvent(source.GetId() if source else 0)
    for key, value in kwargs.iteritems():
        setattr(event, key, value)
    event.SetEventType(event_binder.evtType[0])
    wx.PostEvent(evt_handler, event)
    
    
class Key(object):    
    '''A key combination.'''

    def __init__(self, key_code, cmd=False, alt=False, shift=False):

        self.key_code = key_code        
        '''The numerical code of the pressed key.'''
        
        self.cmd = cmd
        '''Flag saying whether the ctrl/cmd key was pressed.'''
        
        self.alt = alt
        '''Flag saying whether the alt key was pressed.'''
        
        self.shift = shift
        '''Flag saying whether the shift key was pressed.'''
        
        
    @staticmethod
    def get_from_key_event(event):
        '''Construct a Key from a wx.EVT_KEY_DOWN event.'''
        return Key(event.GetKeyCode(), event.CmdDown(),
                   event.AltDown(), event.ShiftDown())
    
    def __hash__(self):
        return hash(tuple(sorted(tuple(vars(self)))))
    
    def __eq__(self, other):
        if not isinstance(other, Key):
            return NotImplemented
        return self.key_code == other.key_code and \
               self.cmd == other.cmd and \
               self.shift == other.shift and \
               self.alt == other.alt
        
menu_keys = [Key(wx.WXK_MENU), Key(wx.WXK_WINDOWS_MENU),
             Key(wx.WXK_F10, shift=True)]
    
def iter_rects_of_region(region):
    '''Iterate over the rects of a region.'''
    i = wx.RegionIterator(region)
    while i.HaveRects():
        yield i.GetRect()
        i.Next()
        


def color_replaced_bitmap(bitmap, old_rgb, new_rgb):
    old_r, old_g, old_b = old_rgb
    new_r, new_g, new_b = new_rgb
    image = wx.ImageFromBitmap(bitmap)
    assert isinstance(image, wx.Image)
    image.Replace(old_r, old_g, old_b, new_r, new_g, new_b)
    return wx.BitmapFromImage(image)
    