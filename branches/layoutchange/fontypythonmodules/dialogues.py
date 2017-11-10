##	Fonty Python Copyright (C) 2006, .., 2017 Donn.C.Ingle
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

import fpwx 


class LocateDirectory(wx.Dialog):
    """
    Sep 2009 : A nicer (than std dir dialogue) dialogue for locating a directory.
    It starts in the cwd.
    """
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, title = _("Locate a directory for the zip file(s)."), pos=wx.DefaultPosition,style=wx.DEFAULT_FRAME_STYLE)

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


