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

import wx, fpwx

class ATree(wx.GenericDirCtrl):
    """
    Nov 2017
    ==
    A dir control with my custom icons.
    Used as a Pog source, and when choosing a zip file directory. So far.
    Note: Directory names are all UNICODE!
    """
    def __init__(self, parent, startdir):
        wx.GenericDirCtrl.__init__(self, parent, -1, 
                dir = startdir, 
                style=wx.DIRCTRL_DIR_ONLY )
        self.SelectPath( startdir, True )
        # create the image list:
        isz = (16,16)
        il = wx.ImageList(isz[0], isz[1])
        # Add images to list. You need to keep this exact order for
        # this to work!
        bmplst=['icon_closed_folder', 'icon_open_folder', 'icon_root', 'icon_drive', 'icon_cdrom', 'icon_ext_drive', 'icon_ext_drive']
        [il.Add( fpwx.wxbmp(f) ) for f in bmplst]
        # assign image list:
        self.il = il
        self.GetTreeCtrl().SetImageList(il)
