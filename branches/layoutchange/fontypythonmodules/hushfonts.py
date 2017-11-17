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


import wx

tmpapp = TmpApp(0)
#app.MainLoop()
class TmpApp(wx.App):
    def OnInit(self):
        return True

wxfont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
SYS_POG_NAME="SYS"

c = subprocess.check_output(['fc-list','--format=%{file}:',wxfont.GetFaceName()])
if c: 
    l = c.split(":")
    l = l.remove("")

## all done in cli2.py : fpsys.probeNoFontconfigDir and assoc err reporting


def get_or_make_SYS_pog():
    syspog = fontcontrol.Pog(SYS_POG_NAME)
    if not fpsys.isPog(SYS_POG_NAME):
        try:
            syspog.write()
        except fontybugs.PogWriteError, e:
            e.print_error_and_quit()
    return syspog

def is_syspog_valid(syspog):
    try:
        syspog.genList()
    #except fontybugs.PogInvalid, e:
    except:
        return False
    return True


Seek the SYS pog
Make the SYS pog
Check SYS pog empty
Choose a default sys font and put into SYS pog
INstall the SYS pog
Uninstall the SYS pog
create the XML
remove the XML

