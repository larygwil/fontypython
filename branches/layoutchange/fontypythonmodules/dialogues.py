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

from fpwx import SYSFONT

        

class xxDialogSettings(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, _("Settings"), pos = wx.DefaultPosition)#, size =(450,-1))
        
        verticalSizer = wx.BoxSizer(wx.VERTICAL)
    
        nb = wx.Notebook(self, -1, style=0)
        PANE1= wx.Panel(nb, -1)
        PANE2 = wx.Panel(nb, -1)

        ## The layout of PANE1 begins:
        font = wx.Font(SYSFONT["points_x_large"], SYSFONT["family"], wx.NORMAL, wx.FONTWEIGHT_BOLD)
        labelHeading = wx.StaticText(self, -1, _("Settings"))
        labelHeading.SetFont(font)

        label_1 = wx.StaticText(PANE1, -1, _("Sample text:"))
        self.inputSampleString = wx.TextCtrl(PANE1, -1, fpsys.config.text, size = (200, -1)) 
        self.inputSampleString.SetFocus()
        
        label_2 = wx.StaticText(PANE1, -1, _("Point size:"))
        self.inputPointSize = wx.SpinCtrl(PANE1, -1, "")
        self.inputPointSize.SetRange(1, 500)
        self.inputPointSize.SetValue(fpsys.config.points)
        
        label_3 = wx.StaticText(PANE1, -1, _("Page length:"))
        self.inputPageLen = wx.SpinCtrl(PANE1, -1, "")
        self.inputPageLen.SetRange(1, 5000) # It's your funeral!
        self.inputPageLen.SetValue(fpsys.config.numinpage) 
        self.inputPageLen.SetToolTip( wx.ToolTip( _("Beware large numbers!") ) )

        PANE1sizer = wx.FlexGridSizer( rows=3, cols=2, hgap=5, vgap=8 )
        PANE1sizer.Add(label_1, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
        PANE1sizer.Add(self.inputSampleString, 1, wx.EXPAND )
        PANE1sizer.Add(label_2, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
        PANE1sizer.Add(self.inputPointSize, 0 )
        PANE1sizer.Add(label_3, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
        PANE1sizer.Add(self.inputPageLen, 0 )

        PANE1_buffer = wx.BoxSizer( wx.HORIZONTAL )
        PANE1_buffer.Add( PANE1sizer, 1, wx.EXPAND | wx.ALL, border=10 )
        PANE1.SetSizer( PANE1_buffer )


        ## Layout of PANE2
        ## Sept 2009 - Checkbox to ignore/use the font top left adjustment code
        self.chkAdjust = wx.CheckBox(PANE2, -1, _("Disable font top-left correction."))
        self.chkAdjust.SetValue(fpsys.config.ignore_adjustments) 
        self.chkAdjust.SetToolTip( wx.ToolTip( _("Disabling this speeds font drawing up a fraction, but degrades top-left positioning.") ) )
        PANE2sizer = wx.BoxSizer( wx.VERTICAL )
        PANE2sizer.Add(self.chkAdjust, 0, wx.ALIGN_LEFT | wx.BOTTOM, border=10 )

        # The Character map choice
        self.CMC = fpsys.config.CMC
        if self.CMC.APPS_ARE_AVAILABLE:
            self.CHOSEN_CHARACTER_MAP = self.CMC.GET_CURRENT_APPNAME()
            rb = wx.RadioBox(
                    PANE2, -1, _("Available character map viewers"), wx.DefaultPosition, wx.DefaultSize,
                    self.CMC.QUICK_APPNAME_LIST, 1, wx.RA_SPECIFY_COLS
                    )
            
            rb.SetSelection( self.CMC.QUICK_APPNAME_LIST.index( self.CHOSEN_CHARACTER_MAP ))

            self.Bind(wx.EVT_RADIOBOX, self.EvtRadioBox, rb)
            rb.SetToolTip(wx.ToolTip( _("Choose which app to use as a character map viewer.") ))
            PANE2sizer.Add( rb, 0, wx.ALIGN_LEFT )
        else:
            self.CHOSEN_CHARACTER_MAP = None
            no_app = wx.StaticText(PANE2, -1, _("Could not find a supported character viewer."))
            PANE2sizer.Add( no_app, 0, wx.ALIGN_LEFT )


        PANE2_buffer = wx.BoxSizer( wx.HORIZONTAL )
        PANE2_buffer.Add( PANE2sizer, 1, wx.EXPAND | wx.ALL, border=10 )
        PANE2.SetSizer( PANE2_buffer )

        ## Add the panels to the notebook
        nb.AddPage( PANE1, _("Quick settings") )
        nb.AddPage( PANE2, _("Voodoo") )

        ## Add label and a space to the vertical sizer
        verticalSizer.Add( labelHeading, 0, wx.ALIGN_LEFT )
        verticalSizer.Add( (0,5), 0 )

        ## Add the notebook
        verticalSizer.Add( nb, 1, wx.EXPAND | wx.ALL )
        verticalSizer.Add((0,10),0) #space between bottom of grid and buttons

        ## Make a std button group
        btnsizer = wx.StdDialogButtonSizer()
        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        btnsizer.AddButton(btn)
        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()
    
        ## Add button group to vertical sizer
        verticalSizer.Add( btnsizer, 0, wx.ALIGN_BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, border = 5)
    
        ## Make a 'buffer' to keep the insides away from the edges of the frame
        buffer=wx.BoxSizer( wx.HORIZONTAL )
        ## To get border to work use wx.EXPAND | wx.ALL
        buffer.Add( verticalSizer, 1,wx.EXPAND | wx.ALL,  border=10 )

        self.SetSizer( buffer )
        buffer.Fit(self)
        self.Layout()

    def EvtRadioBox(self, event):
        self.CHOSEN_CHARACTER_MAP = self.CMC.QUICK_APPNAME_LIST[event.GetInt()]

class SegfaultDialog(wx.Dialog):
    """
    Dec 2007
    Runs from the wrapper script (which runs start_fontypython) so that we
    can tell the user that there was a segfault and why.
    """
    def __init__(self, parent, culprit):
        wx.Dialog.__init__(self, parent, -1, _("Oh boy..."), pos = wx.DefaultPosition )
        ## The layout begins:
        font = wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)
        self.labelHeading = wx.StaticText(self, -1, _("Fonty Python, um ... crashed."))
        self.labelHeading.SetFont(font)
        
        font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)
        self.ohDear = wx.StaticText( self, -1, _("Oh dear,"))
        self.ohDear.SetFont( font )
        

        self.sadStory = wx.StaticText( self, -1, _("There's some problem with the font named below. Please use the Check Fonts tool in Fonty\n(from the command-line or the Tools menu) to go through this directory and mark all the dangerous fonts.\n(You could simply move this font elsewhere, but others may remain to cause trouble.)\n" ))

        font = wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)
        self.culprit = wx.StaticText( self, -1, culprit ) 
        self.culprit.SetFont( font )
        
        verticalSizer = wx.BoxSizer(wx.VERTICAL)
        verticalSizer.Add(self.labelHeading, 0, 0, 0)
        verticalSizer.Add(self.ohDear, 0, 0, 0)
        verticalSizer.Add(self.sadStory, 1, wx.EXPAND, 0)
        verticalSizer.Add(self.culprit, 1, wx.EXPAND, 0)
        
        btnsizer = wx.StdDialogButtonSizer()
        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        btnsizer.AddButton(btn)
        btnsizer.Realize()
                
        verticalSizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL| wx.ALIGN_RIGHT, border = 15)
        buffer=wx.BoxSizer( wx.HORIZONTAL )
        buffer.Add( verticalSizer, 1, wx.ALL, border=10 )

        self.SetSizer( buffer )
        buffer.Fit(self) 
        self.SetSizer( buffer )

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
