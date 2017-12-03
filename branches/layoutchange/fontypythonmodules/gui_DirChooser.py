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

        self.treectrl = self.GetTreeCtrl()

        self.SelectPath( startdir, True )
        # create the image list:
        isz = (16,16)
        il = wx.ImageList(isz[0], isz[1])
        # Add images to list. You need to keep this exact order for
        # this to work!
        #bmplst=['icon_closed_folder', 'icon_open_folder', 'icon_root', 'icon_drive', 'icon_cdrom', 'icon_ext_drive', 'icon_ext_drive']
        bmplst=['icon_closed_folder', 'icon_open_folder', 'icon_root', 'icon_drive', 'icon_cdrom', 'icon_ext_drive', 'icon_ext_drive','view16x16']
        [il.Add( fpwx.wxbmp(f) ) for f in bmplst]
        # assign image list:
        self.il = il
        #self.GetTreeCtrl().SetImageList(il)
        self.treectrl.SetImageList(il)

        sid = self.treectrl.GetSelection()
        self._set_icon(sid)
        #self.treectrl.ScrollTo(sid)
        self._st()

        #self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.__OnActivate, self.treectrl, id=10)
        #self.Bind(wx.EVT_TREE_SEL_CHANGED, self.__OnThing, self.treectrl)#, id=10)
        self.treectrl.Bind(wx.EVT_TREE_SEL_CHANGED, self.__OnThing)#, self.treectrl)#, id=10)

    def __OnThing(self, evt):
        """
        Happens second. After whatever binding in FontSources etc.
        (They must Skip() the event along to me.)
        """
        print '**THING on', self.treectrl.GetItemText(evt.GetItem())
        ti = evt.GetItem()
        self._set_icon(ti)

    def _set_icon(self,tid):
        self.treectrl.SetItemImage( tid, 7, which=wx.TreeItemIcon_SelectedExpanded)#TreeItemIcon_Selected)#TreeItemIcon_Normal)
        self.treectrl.SetItemImage( tid, 7, which=wx.TreeItemIcon_Selected)#TreeItemIcon_Normal)
        #evt.Skip()

    def _one_down(self):
        sp = self.treectrl.GetScrollPos(wx.VERTICAL)
        srange = self.treectrl.GetScrollRange(wx.VERTICAL) - \
                  self.treectrl.GetScrollThumb(wx.VERTICAL)
        e = wx.ScrollEvent(wx.wxEVT_SCROLLWIN_LINEDOWN,
                             self.treectrl.GetId(),
                             min(sp+1, srange),
                             wx.VERTICAL)
        print sp, srange
        self.treectrl.GetEventHandler().ProcessEvent(e)

    def _st(self):
        for x in xrange(1,15):
            self._one_down()
        return
        
    # first find last visible item by starting with the first
        
        next = None
        last = None
        item = self.treectrl.GetFirstVisibleItem()
        while item:
         if not self.treectrl.IsVisible(item): break
         last = item
         item = self.treectrl.GetNextVisible(item)

        # figure out what the next visible item should be,
        # either the first child, the next sibling, or the
        # parent's sibling
        if last:
         if self.treectrl.IsExpanded(last):
            next = self.treectrl.GetFirstChild(last)[0]
         else:
            next = self.treectrl.GetNextSibling(last)
            if not next:
               prnt = self.treectrl.GetItemParent(last)
               if prnt:
                  next = self.treectrl.GetNextSibling(prnt)

        if next:
         #self.treectrl.ScrollTo(next)
         self._one_down()#(next)
        elif last:
         self.treectrl.EnsureVisible(last)         
