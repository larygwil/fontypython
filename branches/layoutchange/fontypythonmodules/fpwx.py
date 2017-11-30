##	Fonty Python Copyright (C) 2017 Donn.C.Ingle
##	Contact: donn.ingle@gmail.com - I hope this email lasts.
##
##	This file is part of Fonty Python.
##	Fonty Python is free software: you can redistribute it and/or modify
##	it under the terms of the GNU General Public License as published by
##	the Free Software Foundation, either version 3 of the License, or
##	(at your option) any later version.
##
##	Fonty Python is distributed in the hope that it will be useful,
##	but WITHOUT ANY WARRANTY; without even the implied warranty of
##	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##	GNU General Public License for more details.
##
##	You should have received a copy of the GNU General Public License
##	along with Fonty Python.  If not, see <http://www.gnu.org/licenses/>.

import wx
import fpsys
from pubsub import *
from wxgui import ps

## Oct 2017 Default Font Family (System font)
## And colours from the user's gui settings:
## Setup in showMain() in wxgui.py
SYSFONT={}
SYSCOLS={}
HTMLCOLS={}
def setup_fonts_and_colours():
    SYSCOLS.update(
    {"dark"  : wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNTEXT),
     "gray"  : wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT),
     "shadow": wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNSHADOW),
    "neutral": wx.SystemSettings.GetColour(wx.SYS_COLOUR_BACKGROUND),
     "light" : wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW),
  "highlight": wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT),
    })

    ##Colours for things that use html
    hcol = SYSCOLS["highlight"]
    HTMLCOLS.update({
    "logotype":hcol,
    "dark"    :SYSCOLS["dark"],
    "medium"  :SYSCOLS["gray"],
    "bg"      :SYSCOLS["neutral"],
    "heading1":hcol,
    "heading2":hcol,
    "heading3":hcol,
    "heading4":hcol,
    "heading5":hcol,
    "heading6":hcol,
    })
    # I need them all in #RRGGBB format:
    for k,v in HTMLCOLS.iteritems():
        HTMLCOLS[k] = v.GetAsString(flags=wx.C2S_HTML_SYNTAX)

    # Going with the sys colours.
    #HTMLCOLS.update({"fontyblue":u"#768b94"})
    
    wxfont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
    # Point sizes are integers.
    ps = wxfont.GetPointSize()
    # I had this in SYSFONT:
    #"font"            : wxfont, 
    # But it acts weirdly later on.
    # Do not store refs to a font...
    SYSFONT.update(
       {
        "points_tiny"     : ps-2,
        "points_small"    : ps-1,
        "points_normal"   : ps,
        "points_x_normal" : ps+1,
        "points_large"    : ps+2,
        "points_x_large"  : ps+5,
        "points_xx_large" : ps+8,
        "points_xxx_large": ps*2,
        })


class AutoWrapStaticText(wx.PyControl):
    """
    Mostly by Robin Dunn

    Layout_func: 
       Means we will set the text many times.
       Is called when SetLabel() happens.
       Nominate some object in the parent
       tree which can have .Layout() called
       on it such that this control will be 
       re-drawn. It's the only way to get 
       this StaticText to fit the space.
       I can't predict which object will 
       work, so it's left to the caller.
    """
    def __init__(self, parent,
            ustr,
            point_size,
            style,
            weight,
            Layout_func = None):

        pos = wx.DefaultPosition

        # Tip:
        # The parent *must* have a legitimate width
        # To do that: ensure the parent's constructor 
        #  has a size argument that makes sense.
        # Without a width, none of this works.
        # The -1 on the height seems to be vital,
        #  remove it and nothing works.
        sz = wx.Size( parent.GetSize()[0], -1)

        self._lf = Layout_func

        wx.PyControl.__init__(self, parent, -1,
                wx.DefaultPosition,
                sz,
                wx.NO_BORDER,
                wx.DefaultValidator)

        # Make our static text and give it
        # some default system properties.
        self.st = wx.StaticText(self, -1, ustr,
                size=sz, style = style )
        # Stuff that can't go into the constructor:
        f = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        f.SetPointSize(SYSFONT[point_size])
        f.SetWeight(weight)    
        self.st.SetFont( f )       

        self._label = ustr # save the unwrapped text
        self._rows = 0 # Will be the number of rows after a wrap.

        # Found a func that gives me pixels! I don't need
        # the whole dc measure thing.
        self._lineheight = f.GetPixelSize()[1] + 2 # add some extra padding.
   
        self._Rewrap()
        self.Bind(wx.EVT_SIZE, self.OnSize)    

    def _lh(self):
        """
        return a tup of my width, text's height
        lineheight * rows = +/- height
        """
        rows = self.st.GetLabel().count("\n") + 1
        h = rows * self._lineheight
        sw = self.GetSize().width
        sz = wx.Size( sw, h )
        return sz

    def SetLabel(self, label):
        """
        This is the NB one. I need to set different
        strings - and they can be long or short.
        I.e. they may need to wrap, or not.
        """
        # What's the new label?
        self._label = label
        # Go wrap it:
        self._Rewrap()
        # If we have a Layout func, call it:
        if self._lf: self._lf()

    def GetLabel(self):
        return self._label

    #def SetFont(self, font):
    #    self.st.SetFont(font)
    #    self._Rewrap()
    #def GetFont(self):
    #    return self.st.GetFont()

    def OnSize(self, evt):
        # Make the StaticText be my width
        self.st.SetSize( self.GetSize() )
        # Go wrap it again:
        self._Rewrap()

    def _Rewrap(self):
        """
        Change the StaticText's label to the
        unwrapped version. 
        Use my width and re-wrap.
        (This alters the actual string by adding 
        newlines. I've noticed it fails on 
        strings that have no spaces ...)
        """
        self.st.Freeze()
        self.st.SetLabel(self._label)
        w=self.GetSize().width
        self.st.Wrap(w)
        self.st.Thaw()

    def DoGetBestSize(self):
        """
        Don't ask me. This is a total mystery.
        I make it return something sensible.
        """
        sz = self._lh()
        self.CacheBestSize(sz)
        return sz



def xlabel(parent, 
             ustr,
        pointsize = None,
           weight = None,
            align = wx.ALIGN_LEFT,
            ellip = None,
    Layout_func = None,
             wrap = False):
    """
    Generic label func.

    Args:
    wrap or Layout_func
       They are exclusive: use either, not both.

       Either flag means: use AutoWrapStaticText control.

       AutoWrapStaticText is a live static text that wraps 
       and can have its label set (it will resize properly by 
       calling Layout_func() to force a proper redraw.

       If there is no Layout_func it implies that SetLabel
       will never be called.

       wrap on its own means we can go without the 
       Layout_func - i.e. it will not alter the label's
       string. It will only wrap in the space it started
       with. (e.g. the long paragraphs in the HushPanel.)

    Neither:
        Defaults to a StaticText which will not wrap.
    """

    s = align
    if ellip: s |= ellip
    
    if wrap or Layout_func:
        lbl = AutoWrapStaticText( parent,
                ustr,
                pointsize,
                s,
                weight,
                Layout_func = Layout_func)
    else:
        # This is a single-use static text. No wrapping.
        lbl = wx.StaticText( parent, -1, u"..", style = s)
        # I can't feed these in via the contrsuctor, hence
        # this second stage:
        f = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        f.SetPointSize(SYSFONT[pointsize])
        f.SetWeight(weight)    
        lbl.SetFont(f)
        # This causes a resize on the label.
        lbl.SetLabel(ustr) 

    return lbl


# A bunch of funcs that all feed into xlabel
# I prefer web concepts like p, h1, to the argument-heavy stuff.
def parar( parent, ustr, pointsize="points_normal" ):
    return xlabel( parent, ustr, pointsize,
            weight=wx.FONTWEIGHT_NORMAL,
            align=wx.ALIGN_RIGHT )

def para( parent, ustr, align="wx.ALIGN_TOP", pointsize="points_normal", **args):
    return xlabel( parent, ustr, pointsize,
            weight=wx.FONTWEIGHT_NORMAL,
            **args)

def label( parent, ustr, align = wx.ALIGN_LEFT, **args):
    return xlabel( parent, ustr, pointsize="points_normal",
           weight=wx.FONTWEIGHT_NORMAL,
           align = align,
           **args)

def large_label( parent, ustr, **args ):
    return xlabel( parent, ustr, pointsize="points_x_normal",
            weight=wx.FONTWEIGHT_NORMAL,
            **args)

def small_label( parent, ustr, **args ):
    return xlabel( parent, ustr, pointsize="points_small",
            weight=wx.FONTWEIGHT_NORMAL,
            **args)

def boldlabel( parent, ustr, **args ):
    return xlabel( parent, ustr, pointsize="points_x_normal",
            weight=wx.FONTWEIGHT_BOLD,
            **args)

def h0( parent, ustr, **args ):
    return xlabel( parent, ustr, "points_xxx_large",
            wx.FONTWEIGHT_BOLD,
            **args)

def h1( parent, ustr, **args):
    return xlabel( parent, ustr, pointsize="points_large",
            weight=wx.FONTWEIGHT_BOLD,
            **args)

def h2( parent, ustr, **args ):
    return xlabel( parent, ustr, pointsize="points_large",
            weight=wx.FONTWEIGHT_NORMAL,
            **args)

# A quick way to get a file form the things directory:
def wxbmp( filename ):
    return wx.Bitmap( fpsys.mythingsdir + filename+".png", 
            wx.BITMAP_TYPE_PNG )

# I don't even recall...
def icon(parent, filename):
    b = wxbmp( filename )
    i = wx.StaticBitmap( parent, -1, b )
    return i
