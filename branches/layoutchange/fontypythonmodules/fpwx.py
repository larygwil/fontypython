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
    """
    def __init__(self, parent,
            ustr,
            point_size,
            style,
            weight):

        pos = wx.DefaultPosition

        self.p = parent
        wx.PyControl.__init__(self, parent, -1,
                wx.DefaultPosition,
                wx.DefaultSize, wx.NO_BORDER,
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
        f = self.st.GetFont()
        dc = wx.ScreenDC()
        dc.SetFont(f)
        w,h,lh = dc.GetMultiLineTextExtent(ustr,f)
        self._lineheight = lh

        self._Rewrap()
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
        sz = wx.Size( max(sw, 300), h )
        print sz
        return sz

    def SetLabel(self, label):
        # This is the NB one. I need to set different
        # strings - and they can be long or short.
        # I.e. they can wrap or not.
        # The space the string is in should resize,
        # but I can't get it right.
        print "SetLabel:",label
        self._label = label
        #self._anew()
        self._Rewrap()
        print self.GetParent()
        self.GetParent().GetParent().Layout()

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
        self.st.SetLabel(self._label)
        w=self.GetSize().width
        if w > 360:
            print "wrap to w:",w
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
        size = None,
        weight=None,
        align = wx.ALIGN_LEFT,
        ellip = None,
        wrap = False):

    s = align
    if ellip: s |= ellip
    
    if wrap: 
        # This is a live version that can have its
        # label set and will resize properly.
        lbl = AutoWrapStaticText( parent,
                ustr,
                size,
                s,
                weight)
    else:
        # This is a single-use static text
        lbl = wx.StaticText( parent, -1, ustr, style = s)

        f = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        f.SetPointSize(SYSFONT[size])
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

def parar( parent, ustr, size="points_normal" ):
    return xlabel( parent, ustr, size,
            weight=wx.FONTWEIGHT_NORMAL,
            align=wx.ALIGN_RIGHT )

def para( parent, ustr, align="wx.ALIGN_TOP", size="points_normal" ):
    return xlabel( parent, ustr, size,
            weight=wx.FONTWEIGHT_NORMAL, wrap = True )

def label( parent, ustr, align = wx.ALIGN_LEFT, ellip = None, wrap = False ):
    return xlabel( parent, ustr, size="points_normal",
           weight=wx.FONTWEIGHT_NORMAL,
           align = align, ellip=ellip, wrap=wrap)

def large_label( parent, ustr ):
    return xlabel( parent, ustr, size="points_x_normal",
            weight=wx.FONTWEIGHT_NORMAL )

def small_label( parent, ustr ):
    return xlabel( parent, ustr, size="points_small",
            weight=wx.FONTWEIGHT_NORMAL )

def boldlabel( parent, ustr ):
    return xlabel( parent, ustr, size="points_x_normal",
            weight=wx.FONTWEIGHT_BOLD )

def h0( parent, ustr ):
    return xlabel( parent, ustr, "points_xxx_large",
            wx.FONTWEIGHT_BOLD )

def h1( parent, ustr, ellip = None, wrap = False ):
    return xlabel( parent, ustr, size="points_large",
            weight=wx.FONTWEIGHT_BOLD, ellip = ellip, wrap=wrap )

def h2( parent, ustr ):
    return xlabel( parent, ustr, size="points_large",
            weight=wx.FONTWEIGHT_NORMAL )


def wxbmp( filename ):
    return wx.Bitmap( fpsys.mythingsdir + filename+".png", 
            wx.BITMAP_TYPE_PNG )

def icon(parent, filename):
    b = wxbmp( filename )
    i = wx.StaticBitmap( parent, -1, b )
    return i
