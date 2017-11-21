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
    "dark"    :SYSCOLS["dark"],
    "medium"  :SYSCOLS["gray"],
    "bg"      :SYSCOLS["neutral"],
    "heading1":hcol,
    "heading2":hcol,
    "heading3":hcol,
    "heading4":hcol,
    "heading5":hcol,
    })
    # I need them all in #RRGGBB format:
    for k,v in HTMLCOLS.iteritems():
        HTMLCOLS[k] = v.GetAsString(flags=wx.C2S_HTML_SYNTAX)
    HTMLCOLS.update({"fontyblue":u"#768b94"})
    
    wxfont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
    ps = wxfont.GetPointSize()
    SYSFONT.update(
       {"font"            : wxfont,
        "family"          : wxfont.GetFamily(),
        "points_smaller"  : ps*0.8,
        "points_small"    : ps*0.9,
        "points_normal"   : ps,
        "points_x_normal" : ps*1.05,
        "points_large"    : ps*1.07,
        "points_x_large"  : ps*1.2,
        "points_xx_large" : ps*1.5,
        "points_xxx_large": ps*2,
        })

def parar( parent, ustr, size="points_normal" ):
    p = xlabel( parent, ustr, size, weight=wx.FONTWEIGHT_NORMAL, align=wx.ALIGN_RIGHT )
    return p

def para( parent, ustr, size="points_normal" ):
    p = xlabel( parent, ustr, size, weight=wx.FONTWEIGHT_NORMAL )
    return p

def label( parent, ustr ):
    p = xlabel( parent, ustr, size="points_normal", weight=wx.FONTWEIGHT_NORMAL )
    return p

def small_label( parent, ustr ):
    p = xlabel( parent, ustr, size="points_small", weight=wx.FONTWEIGHT_NORMAL )
    return p

def boldlabel( parent, ustr ):
    p = xlabel( parent, ustr, size="points_normal", weight=wx.FONTWEIGHT_BOLD )
    return p

def h0( parent, ustr ):
    p = xlabel( parent, ustr, "points_xxx_large", wx.FONTWEIGHT_BOLD )
    return p

def h1( parent, ustr ):
    p = xlabel( parent, ustr, size="points_large", weight=wx.FONTWEIGHT_BOLD )
    return p

def h2( parent, ustr ):
    p = xlabel( parent, ustr, size="points_large", weight=wx.FONTWEIGHT_NORMAL )
    return p

def xlabel(parent, 
        ustr, size, weight,
        align = wx.ALIGN_LEFT):
    lbl = wx.StaticText( parent, -1, ustr, style = align )
    lbl.SetFont( wx.Font(SYSFONT[size], SYSFONT["family"], 
                wx.NORMAL, weight) )
    return lbl

def wxbmp( filename ):
    return wx.Bitmap( fpsys.mythingsdir + filename+".png", 
            wx.BITMAP_TYPE_PNG )

def icon(parent, filename):
    b = wxbmp( filename )
    i = wx.StaticBitmap( parent, -1, b )
    return i
