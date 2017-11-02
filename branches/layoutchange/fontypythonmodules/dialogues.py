##	Fonty Python Copyright (C) 2006, 2007, 2008, 2009 Donn.C.Ingle
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

import os, locale
import fpsys
#import fontsearch
import strings
import wx

## June 25th 2016
## Remarking these two lines because they are causing a segfault:
##  ../src/common/stdpbase.cpp(62): assert "traits" failed in Get(): 
##  create wxApp before calling this
##  Segmentation fault (core dumped)
##
##  I do not know how to test or fix this, hence simply removing it.
##  AFAICT, stock buttons will be in the system language.
##
## Setup wxPython to access translations : enables the stock buttons.
##langid = wx.LANGUAGE_DEFAULT # Picks this up from $LANG
##mylocale = wx.Locale( langid )

from fpwx import SYSFONT, label
  

class SegfaultDialog(wx.Dialog):
    """
    Dec 2007
    Runs from the wrapper script (which runs start_fontypython) so that we
    can tell the user that there was a segfault and why.
    """
    def __init__(self, parent, sadStory, culprit):
        wx.Dialog.__init__(self, parent, -1, _("Oh boy..."), pos = wx.DefaultPosition )
        ## The layout begins:
        labelHeading = label(self, _("Fonty Python, um ... crashed."), 
                size="points_large", weight=wx.FONTWEIGHT_BOLD)
        
        ohDear = label( self, _("Oh dear,"))
        sadStory = label( self, sadStory)

        ## Have to use a size. Can't get them to just fit the dialog. fcuk....
        tickettxt = label(self, _("You can get help by opening a ticket, or sending me an email."))
        emaillink = wx.TextCtrl(self, -1, strings.contact,  size=(450,-1), style = wx.TE_READONLY)
        ticketurl = wx.TextCtrl(self, -1, strings.ticket_url, size=(450,-1), style = wx.TE_READONLY)

        verticalSizer = wx.BoxSizer(wx.VERTICAL)
        verticalSizer.Add(labelHeading, 0, wx.BOTTOM, border = 4 )
        verticalSizer.Add(ohDear, 0 )
        verticalSizer.Add(sadStory,  0, wx.BOTTOM, border = 8 )
        if culprit: 
            msg = _('The bad font is: "{}"').format(culprit)
            culprit = label(self, msg,  weight=wx.FONTWEIGHT_BOLD)
            verticalSizer.Add(culprit, 0 )
        verticalSizer.Add((1,32), 0 )
        verticalSizer.Add(tickettxt, 0 )
        verticalSizer.Add(ticketurl, 0 )
        verticalSizer.Add(emaillink, 0 )
        
        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
                
        verticalSizer.Add(btn, 0, wx.ALIGN_CENTER_VERTICAL| wx.ALIGN_RIGHT | wx.TOP, border = 15)

        b = wx.BoxSizer( wx.HORIZONTAL )
        b.Add( verticalSizer, 0, wx.ALL, border=10 )

        self.SetSizer( b )
        b.Fit(self) 
        self.Layout()
        
class LocateDirectory(wx.Dialog):
    """
    Sep 2009 : A nicer (than std dir dialogue) dialogue for locating a directory.
    It starts in the cwd.
    """
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, title = _("Locate a directory for the zip file(s)."),
                pos=wx.DefaultPosition,style=wx.DEFAULT_FRAME_STYLE)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.treedir = wx.GenericDirCtrl( self, -1, dir=os.getcwd(), style=wx.DIRCTRL_DIR_ONLY )

        btno = wx.Button(self, wx.ID_OK)
        btnc = wx.Button(self, wx.ID_CANCEL)

        sizer.Add(self.treedir, 1, wx.EXPAND)
        sizer.Add(btno, 0, wx.EXPAND)
        sizer.Add(btnc, 0, wx.EXPAND)

        btnsizer = wx.StdDialogButtonSizer()
        btno.SetDefault()
        btnsizer.AddButton(btno)
        btnsizer.AddButton(btnc)
        btnsizer.Realize()

        self.SetSizer(sizer)
        self.SetAutoLayout(True)

    def GetPath(self):
        return self.treedir.GetPath()

class DialogCheckFonts( wx.Dialog ):
    """
    18 Jan 2008
    Open a dircontrol to locate a folder, a text box of some kind to
    show the progress, and build the segfonts file/list
    """
    def __init__( self, parent, startdir ):
        wx.Dialog.__init__(self, parent, -1, _("Check for dangerous fonts."), \
        size=(800,400),pos = wx.DefaultPosition, style=wx.DEFAULT_FRAME_STYLE )

        ## LEFT
        leftsz = wx.BoxSizer(wx.VERTICAL)

        font = wx.Font(SYSFONT["points_large"], SYSFONT["family"], wx.NORMAL, wx.FONTWEIGHT_BOLD)
        title = wx.StaticText( self,-1,  _("Choose a directory and double click it to start"))
        title.SetFont( font )
        leftsz.Add(title,0,wx.EXPAND | wx.ALL, border=4 )
        self.treedir = wx.GenericDirCtrl( self, -1, dir=startdir, style=wx.DIRCTRL_DIR_ONLY )
        leftsz.Add( self.treedir, 1, wx.EXPAND|wx.ALL)

        ## RIGHT
        rightsz = wx.BoxSizer(wx.VERTICAL)
        self.output = wx.TextCtrl( self, -1, "...", \
        size=(200,-1), style = wx.TE_MULTILINE | wx.TE_READONLY )
        rightsz.Add(self.output,1,wx.EXPAND | wx.ALL)

        ## Because I want a CLOSE button -- I have to do all the button
        ## stuff manually. StdDialogButtonSizer only provides certain buttons
        ## that are not appropriate for this form.
        bsz = wx.BoxSizer(wx.HORIZONTAL)
        self.btn = wx.Button(self, wx.ID_CLOSE)
        self.btn.SetDefault()
        bsz.Add(self.btn,1,wx.EXPAND)
        self.btn.Bind( wx.EVT_BUTTON, self.OnClick)

        rightsz.Add(bsz,0,wx.EXPAND)

        sz = wx.BoxSizer(wx.HORIZONTAL)

        sz.Add(leftsz, 1, wx.EXPAND)
        sz.Add(rightsz, 1, wx.EXPAND )# this wx.EXPAND got the text control to fit the height.

        self.SetSizer(sz)

        self.tree = self.treedir.GetTreeCtrl()

        self.tree.Bind(wx.EVT_LEFT_DCLICK, self.__goFigure)
    def OnClick(self,e):
        self.Close(True)

    def printer( self, txt=None ):
        if txt is None: txt = "\n"
        self.output.WriteText(txt + "\n")
        wx.SafeYield()

    def __goFigure( self, e ):
        self.output.Clear()
        wx.BeginBusyCursor()
        dirtocheck = self.treedir.GetPath()
        fpsys.checkFonts( dirtocheck, self.printer )
        wx.EndBusyCursor()

## May 2009 - Busy
## June 2009 - Given up on this code for now.

#class PopupInfo(wx.Frame):
#	def __init__(self, parent, id, title, fmap):
#		wx.Frame.__init__(self, parent, id, title)
#		self.box = wx.BoxSizer(wx.VERTICAL)
#		self.list = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE|wx.TE_WORDWRAP)
#		self.box.Add(self.list, proportion=1, flag=wx.EXPAND)
#		font = fmap.fitem
#		info = fontsearch.getInfo(font)
#		try:
#			self.SetTitle(info['Name Records']['Full Name'])
#		except KeyError:
#			self.SetTitle(font.name)
#		except:
#			self.SetTitle("Font Information")
#		text = str(info)
#		self.list.AppendText(text)
#		self.butClose = wx.Button(self, id = wx.ID_OK)
#		self.butClose.Bind(wx.EVT_BUTTON, lambda event : self.Close())
#		self.Bind(wx.EVT_COMMAND_KILL_FOCUS, lambda event : self.Close())
#		self.box.Add(self.butClose, flag=wx.FIXED_MINSIZE|wx.ALIGN_CENTER)
#		self.box.Layout()
#		self.SetSizer(self.box)		
