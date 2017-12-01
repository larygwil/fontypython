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

import wx, locale

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

from pubsub import * #I want all the topics.
from wxgui import ps

import fpsys # Global objects
import fontcontrol
import fontybugs

from fpwx import wxbmp 

class PogChooser(wx.ListCtrl) :
    """
    Basic list control for pogs - instanced by TargetPogChooser
    and in the NoteBook in gui_FontSources.

    This single class (being used twice) causes all kinds of
    twisty tests. I'm not sure how better to do it.
    """

    ## CLASS LEVEL variables - Independent of instances.
    ## i.e. common to all.
    __poglistCopy = {} # To help in sorting.
    __TARGET = None
    __VIEW = None

    def __init__(self, parent, whoami, select = None) :
        self.indexselected = 0
        self.lastindexselected = -1
        self.parent = parent
        self.whoami = whoami

        ## Use Class-level attributes to record the history of 
        ## the instantiation of this class. These vars do not
        ## belong to the instances, but to this one class.
        ## We keep refs to the two parents of this class.
        if whoami == "SOURCEPOG":
            PogChooser.__VIEW = self
            style = wx.LC_LIST | wx.LC_SORT_ASCENDING | wx.LC_SINGLE_SEL
        else:
            PogChooser.__TARGET = self.parent
            style = wx.LC_LIST | wx.LC_SORT_ASCENDING

        il = wx.ImageList(16,16,True)
        il.Add( wxbmp('pog16x16') )
        il.Add( wxbmp('pog16x16.installed') )
        ## Dec 2007 : target icon
        il.Add( wxbmp( 'pog16x16.target') )

        wx.ListCtrl.__init__( self,parent,-1, style=style |
                wx.SUNKEN_BORDER, name="pog_chooser" )

        self.AssignImageList(il, wx.IMAGE_LIST_SMALL)

        self.fillPogList()

        ## Highlight the pog selected (the last one, or the
        ## cli chosen one)
        if select:
            i = self.FindItem(-1, select)
            self.indexselected = i # Set to help initial icon settings
            self.Select(i, True)
        else:
            ## Nov 2017
            ## == "FichteFoll" hit a bug here.
            ## When fp starts with zero pogs ... :O ...
            ## there's an index problem with self.Select
            ## TBH, I can't remember why this else branch is here.
            ## Rather than court the revenge of my bad memory,
            ## I have stuck a count test on the Select:
            if self.GetItemCount() > 0: self.Select(0, False)
            self.indexselected = -1


        self.ClearBackground()
        self.items = None

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)

        ## This one is a double click event
        ## self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.__onActivate)

        #self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))

        ## This subscribe line here will register TWICE
        ##  with the global "ps" - since this PogChooser class 
        ##  is instanced twice by the app...
        ## Only the first occ. of the function is ever called.
        ps.sub(change_pog_icon, self.ChangeIcon) ##DND: class PogChooser

    def Sorter(self, key1, key2):
        """
        Fetch the strings from our CLASS LEVEL copy of the pognames
        so that we can compare them via locale.
        """
        s1,s2 = PogChooser.__poglistCopy[key1], \
                PogChooser.__poglistCopy[key2]
        ## Since the gui is unicode, I *think* I don't have to 
        ## worry about errors here.
        return locale.strcoll( s1, s2 )

    def onSelect(self, e):
        wx.BeginBusyCursor()
        self.indexselected = e.m_itemIndex
        pognochange = False
        if self.indexselected == self.lastindexselected:
            ## We have clicked on the same Pog as last time
            ## - ergo do nothing.
            pognochange = True
        # Record this for next time around
        self.lastindexselected = self.indexselected 

        # Gets UNICODE !!!
        textpogname = self.GetItemText(self.indexselected)

        if self.whoami=="SOURCEPOG":
            ps.pub(source_pog_has_been_selected,
                    textpogname, pognochange)
        else:
            ps.pub(target_pog_has_been_selected,
                    textpogname, pognochange)

        self.SortOutTheDamnImages( pognochange )

        wx.EndBusyCursor()

    def SortOutTheDamnImages( self, pognochange ):
        """
        Dec 2007 : This took me an entire day to figure out.
                   Man...
        Determines the images of the list items.
        Is called from TargetPogChooser as well 
        (when clear button is clicked)
        """
        if pognochange is ():
            pognochange = True

        c = self.GetItemCount()
        # the actual selection index, does not go to -1
        sel = self.indexselected 

        ## Which kind of a McList am I?
        iAmTargetList = self.whoami=="TARGETPOG"
        ## If there is an active selection?
        if sel > -1:
            for x in xrange(0, c):
                i = self.GetItem(x, 0)
                ## Must make a tmp Pog before I can test
                ## installed status.
                tmpPog = fontcontrol.Pog(i.GetText())
                if tmpPog.isInstalled():
                    self.SetItemImage(x, 1)
                else:
                    ## Handle the other icons (in the target
                    ## list only)
                    ## that are not installed.
                    if iAmTargetList:
                        if x == sel:
                            ## No change means it *was* selected
                            ## and now it's been selected again
                            ## thus it can't be the target anymore.
                            if pognochange: n = 0
                            else: n = 2
                            # new target icon
                            self.SetItemImage(x, n )
                        else:
                            self.SetItemImage(x, 0)
            ## Tell the VIEW to imitate this picture.
            for x in xrange(0,c):
                # the 0 is 'column'. Ignore.
                ti = self.__TARGET.pogTargetlist.GetItem(x, 0)
                # gets the image index, not an image bitmap.
                CLONE = ti.GetImage()
                self.__VIEW.SetItemImage(x, CLONE)

    def __del__(self) :
        del self.items

    def fillPogList(self):
        """
        This is among the very FIRST things we do.
        Fill the list with pogs.
        This will CULL any bad pogs (i.e. those with 
        malformed content)
        Thus the PogInvalid error should not happen 
        any more after a run.
        """
        # pl will always be a BYTE STRING list
        pl = fpsys.iPC.getPogNames()

        for p in pl: # 'p' is a byte string.
            ipog = fontcontrol.Pog(p)
            try: #catch pogs that are not properly formed
                # isInstalled opens the pog file.
                if ipog.isInstalled(): i = 1
                else: i = 0
            except fontybugs.PogInvalid, eInst:
                ## An "invalid" pog is one that does not have
                ## installed/not installed on the first line.
                print _(u"(%s) skipped. It's an invalid pog.") % [p]
                continue

            ## Let's try to make a unicode of p so li.SetText(p)
            ## can display it:
            try:
                p = fpsys.LSP.to_unicode( p )
            except UnicodeDecodeError:
                ## We can't convert it under this locale
                print _(u"(%s) skipped. I can't display this name "\
                        "under your locale.") % [p]
                continue
            ## Okay, we have a valid pog name to use:
            li = wx.ListItem()
            li.SetImage(i)
            li.SetText(p)

            ## June 25, 2016: Something in wxPython changed 
            ## and li now needs an Id>0
            li.Id = 1

            id = wx.NewId()
            PogChooser.__poglistCopy[id] = p # record the pog name
            row = self.InsertItem( li )
            # associate back to __poglistCopy
            self.SetItemData( row, id )

        self.SortItems( self.Sorter )

    def AddItem(self, pogname):
        """
        Add a pogname to myself, then sort.
        """
        li = wx.ListItem()
        li.SetImage(0)
        li.SetText(pogname)

        #July 5th, 2016 - wxPython Id fix
        li.Id = 1

        id = wx.NewId()
        self.__poglistCopy[id] = pogname
        row = self.InsertItem(li)
        self.SetItemData( row, id )
        self.SortItems( self.Sorter )

    def RemoveItem(self, pogname):
        row = self.FindItem(-1, pogname)
        id = self.GetItemData(row)
        self.DeleteItem(row)
        # cull from our private store too.
        del( PogChooser.__poglistCopy[id] )

    def ClearSelection(self):
        # removes all selections, even for multi-selections
        for x in range(self.GetSelectedItemCount()):
            self.Select(self.GetFirstSelected(), False)
        self.lastindexselected = -1

    def ChangeIcon(self):
        """
        Change a single Pog's icon to installed/uninstalled.
        ONLY called from InstallPog and UninstallPog.
        """
        #print "ChangeIcon:",self
        T = fpsys.state.targetobject
        pn = T.name
        index = self.FindItem(0, pn)
        if T.isInstalled(): n = 1
        else: n = 0
        self.SetItemImage(index, n) ## Found in wxWidgets documentation!

    def ClearLastIndex(self):
        """
        We need to reset the lastindexselected so that a click on the
        same item as last time will register. This is used in the Notebook
        when the page changes back to page 1, we want the user to
        be able to re-click the item that was clicked last time.
        """
        self.lastindexselected = -1
