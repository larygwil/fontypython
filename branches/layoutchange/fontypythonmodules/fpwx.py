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
    By Robin Dunn
    Under hackery. Not working right now.
    :(

    wrapping *and* SetLabel
    
    wrap: Alone, does not need a SetLabel_func
    SetLabel: Is the one that needs the SetLabel_func

    SetLabel_func : Called when SetLabel happens.
    Nominate some object in the parent
    tree which can have .Layout() called on it such
    that this control will be re-drawn. It's the only
    way to get this StaticText to fit the space.
    I can't predict which object will work, so it's
    left to the caller.
    """
    def __init__(self, parent,
            ustr,
            point_size,
            style,
            weight,
            SetLabel_func = None):

        pos = wx.DefaultPosition

        # Tip:
        # The parent *must* have a legitimate width
        # To do that ensure the parent's constructor 
        # had a size argument that makes sense.
        # Without a width, none of this work.
        sz = wx.Size( parent.GetSize()[0],-1) # must be a valid width.

        self.p = parent

        self._lf = SetLabel_func

        wx.PyControl.__init__(self, parent, -1,
                wx.DefaultPosition,
                sz,
                wx.NO_BORDER,
                wx.DefaultValidator)

        # Make our static text and give it
        # default system properties
        self.st = wx.StaticText(self, -1, ustr, style = style )
        
        f = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        f.SetPointSize(SYSFONT[point_size])
        f.SetWeight(weight)    

        self.st.SetFont( f )       

        self._label = ustr # save the unwrapped text
        self._rows = 0

        # Measure the string once, to get a line height.
        #f = self.st.GetFont()
        #dc = wx.ScreenDC()
        #dc.SetFont(f)
        #w,h,lh = dc.GetMultiLineTextExtent(ustr,f)
        self._lineheight = f.GetPixelSize()[1] + 2


        print "init of AutoWrapStaticText"
        print ustr
        print "1.",self.GetSize()
        print "2.",self.GetVirtualSize()
        print "3.",self.GetParent().GetSize()
        print "4.",self.GetParent().GetVirtualSize()
        print "5.",self.GetParent().GetParent().GetSize()
        print "6.",self.GetParent().GetParent().GetVirtualSize()
   
        self._Rewrap()
        self._lf()
        self.Bind(wx.EVT_SIZE, self.OnSize)    

    def _lh(self):
        # return a tup of parent width, text height
        # lineheight * rows should == ~ height
        #print "_lh() on :",self.st.GetLabel()
        rows = self.st.GetLabel().count("\n") + 1
        print "rows:", rows
        h = rows * self._lineheight
        #sz = wx.Size( self.GetParent().GetSize()[0], h )
        sw = self.GetSize().width
        #sz = wx.Size( max(sw, 300), h )
        sz = wx.Size( sw, h )
        print sz
        return sz

    def SetLabel(self, label):
        # This is the NB one. I need to set different
        # strings - and they can be long or short.
        # I.e. they can wrap or not.
        # The space the string is in should resize,
        # but I can't get it right.
        print "SetLabel:",label
        if not self._lf:
            print "Empty layout func"
            raise SystemExit
        self._label = label
        #self._anew()
        self._Rewrap()
        #print self.GetParent()
        #self.GetParent().GetParent().Layout()
        #ps.pub(self._pub_topic)
        self._lf()

    def GetLabel(self):
        return self._label

    def SetFont(self, font):
        self.st.SetFont(font)
        self._Rewrap()
    def GetFont(self):
        return self.st.GetFont()

    def OnSize(self, evt):
        self.st.SetSize(self.GetSize())#GetSize())
        self._Rewrap()
        #evt.Skip()

    def _Rewrap(self):
        #self.st.Freeze()
        print "_Rewrap on:", self._label
        self.st.SetLabel(self._label)
        w=self.GetSize().width
        #if w > 360:
        #    print "wrap to w:",w
        self.st.Wrap(w)
        # here I count the rows:
        #self._rows = self.st.GetLabel().count("\n") + 1
        #self.st.Thaw()

    def DoGetBestSize(self):
        # Trying to use the lineheight etc.
        sz = self._lh()
        #self.CacheBestSize(sz)
        return sz



def xlabel(parent, 
             ustr,
        pointsize = None,
           weight = None,
            align = wx.ALIGN_LEFT,
            ellip = None,
    SetLabel_func = None,
             wrap = False):

    s = align
    if ellip: s |= ellip
    
    if wrap or SetLabel_func:
        # Either flags: we must use the AutoWrapStaticText control
        # This is a live static text that wraps and can have its 
        # label set (it will resize properly by calling 
        # SetLabel_func() to force a proper redraw.
        lbl = AutoWrapStaticText( parent,
                ustr,
                pointsize,
                s,
                weight,
                SetLabel_func = SetLabel_func)
    else:
        # This is a single-use static text
        lbl = wx.StaticText( parent, -1, ustr, style = s)

        f = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        f.SetPointSize(SYSFONT[pointsize])
        f.SetWeight(weight)    
        
        # Wrap the text once, to get it to fit better
        # Reach up two parents to the MainFrame. I think.
        ppw = lbl.GetParent().GetParent().GetSize().width
        # wrap to half that.
        lbl.Wrap( ppw/2 )
        # get a pixel height for this font
        pxh = f.GetPixelSize()[1] + 2
        rows = ustr.count("\n") + 1
        h = pxh * rows

        lbl.SetSize( ( -1, h) )
        lbl.SetFont( f )
    return lbl

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


def wxbmp( filename ):
    return wx.Bitmap( fpsys.mythingsdir + filename+".png", 
            wx.BITMAP_TYPE_PNG )

def icon(parent, filename):
    b = wxbmp( filename )
    i = wx.StaticBitmap( parent, -1, b )
    return i
