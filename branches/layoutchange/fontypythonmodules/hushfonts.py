## Fonty Python Copyright (C) 2017 Donn.C.Ingle
## Contact: donn.ingle@gmail.com - I hope this email lasts.
##
## This file is part of Fonty Python.
## Fonty Python is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Fonty Python is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Fonty Python.  If not, see <http://www.gnu.org/licenses/>.


import subprocess

"""
This is how you can get the system font from wx into python:
import wx
tmpapp = TmpApp(0)
#app.MainLoop()
class TmpApp(wx.App):
    def OnInit(self):
        return True

wxfont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
c = subprocess.check_output(['fc-list','--format=%{file}:',wxfont.GetFaceName()])
if c: 
    l = c.split(":")
    l = l.remove("")

Now you have the full pafs to all the system fonts in a list.

sundry:

def is_fclist_installed():
    try:
        # run fc-list -V (version output)
        c = subprocess.check_output(["fc-list" ,"-V"])
    except:
        # nope
        return False
    return True

"""



xmlpaf = 

