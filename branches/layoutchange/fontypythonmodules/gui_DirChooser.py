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

    The startdir is always going to be some valid path, even
    if only $HOME.
    """
    def __init__(self, parent, startdir):
        wx.GenericDirCtrl.__init__(self, parent, -1, 
                dir = startdir, 
                style=wx.DIRCTRL_DIR_ONLY )

        self.treectrl = self.GetTreeCtrl()

        self.SelectPath( startdir, True )
        # create the image list:
        isz = (16,16)
        il = wx.ImageList(isz[0], isz[1])

        # Add images to list. You need to keep this exact order for
        # this to work!
        # Dec 2017: Added item # 7, the little eye icon.
        bmplst=['icon_closed_folder', 'icon_open_folder', 'icon_root', 'icon_drive', 'icon_cdrom', 'icon_ext_drive', 'icon_ext_drive','view16x16']
        [il.Add( fpwx.wxbmp(f) ) for f in bmplst]

        # assign image list:
        self.il = il
        self.treectrl.SetImageList(il)

        # Set the initial icon
        sid = self.treectrl.GetSelection()
        self._set_icon(sid)
        
        # I can't get it to scroll to the selected dir 
        #self.treectrl.ScrollTo(sid), etc.

        self.treectrl.Bind(wx.EVT_TREE_SEL_CHANGED, self.__OnThing)
        #self.treectrl.Bind(wx.EVT_SET_FOCUS, self._foo)

    #def _foo(self,evt):
    #    print evt

    def __OnThing(self, evt):
        """
        This event happens second; after whatever binding is in 
        FontSources etc.
        (They must Skip() the event along to me.)
        If they don't Skip(), this won't run and the icons won't
        change. I do this in the ChooseZipDirPanel.
        (See gui_dismissable_panels.py)
        """
        #print '**THING on', self.treectrl.GetItemText(evt.GetItem())
        ti = evt.GetItem()
        self._set_icon(ti)
        evt.Skip()

    def _set_icon(self,tid):
        """
        Found this in the docs. Got lucky.
        It's a way to set an icon on various selection states.
        It better reflects the little eye in the
        Pog list controls now. (here it's #7)
        """
        self.treectrl.SetItemImage( tid, 7,
                which = wx.TreeItemIcon_SelectedExpanded)
        self.treectrl.SetItemImage( tid, 7,
                which = wx.TreeItemIcon_Selected)

        # The item selects, but it flashes from orange
        # to grey in the background. It's weird.
        # I can't fix it.
        #self.treectrl.SetFocusedItem(tid) # fail




    def _one_down(self):
        """
        Attempt to force the tree to scroll down. Fails.
        Will leave this here for one day.
        http://wxpython-users.1045709.n5.nabble.com/\
        Cross-platform-issues-Programmatically-Scrolling\
        -a-TreeCtrl-td2300200.html
        """
        sp = 100#self.treectrl.GetScrollPos(wx.VERTICAL)
        srange = 100# self.treectrl.GetScrollRange(wx.VERTICAL) - \
                  #self.treectrl.GetScrollThumb(wx.VERTICAL)
        e = wx.ScrollEvent(wx.wxEVT_SCROLLWIN_LINEDOWN,
                             self.treectrl.GetId(),
                             min(sp+1, srange),
                             wx.VERTICAL)
        print sp, srange
        self.treectrl.GetEventHandler().ProcessEvent(e)
