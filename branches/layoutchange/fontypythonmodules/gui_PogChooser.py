## Fonty Python Copyright (C) 2006, 2007, 2008, 2009, 2017 Donn.C.Ingle
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

    ## turns-out, we can also fetch these via self.xxx
    icon_normal    = 0 # empty P
    icon_installed = 1 # filled-in P
    icon_targetted = 2 # triangle
    icon_viewing   = 3 # eye

    def __init__(self, parent, whoami, select = None) :
        """
        select is None or a Pog that will be selected in the control.
        """
        self.indexselected = -1
        self.lastindexselected = -1
        self.parent = parent
        self.whoami = whoami

        ## Use Class-level attributes to record the history of 
        ## the instantiation of this class. These vars do not
        ## belong to the instances, but to this one class.
        ## We keep refs to the two parents of this class.
        ## __VIEW and __TARGET are useful when I want to 
        ## refer to the *other* one from <whatever I am>
        if whoami == "SOURCEPOG":
            PogChooser.__VIEW = self
            style = wx.LC_LIST | wx.LC_SORT_ASCENDING | wx.LC_SINGLE_SEL
        else:
            PogChooser.__TARGET = self
            style = wx.LC_LIST | wx.LC_SORT_ASCENDING

        il = wx.ImageList( 16, 16, True )
        il.Add( wxbmp( 'pog16x16') )
        il.Add( wxbmp( 'pog16x16.installed') )
        il.Add( wxbmp( 'pog16x16.target') ) # Dec 2007: triangle target
        il.Add( wxbmp( 'view16x16') ) # Dec 2017: little eye

        wx.ListCtrl.__init__( self,parent,-1, style=style |
                wx.SUNKEN_BORDER, name="pog_chooser" )

        self.AssignImageList(il, wx.IMAGE_LIST_SMALL)

        self.fillPogList()

        ## Highlight the pog selected (the last one, or the
        ## cli chosen one)
        ## Done manually because things are still in an __init__
        ## state.
        if select:
            i = self.FindItem( -1, select )
            self.indexselected = i # Set to help initial icon settings
            self.SetItemImage( i, self.icon_viewing )
            self.Select( i, True )
        #else:
            ## Nov 2017
            ## == "FichteFoll" hit a bug here.
            ## When fp starts with zero pogs ... :O ...
            ## there's an index problem with self.Select
            ## Fix: Just exlude this else branch.


        self.ClearBackground()
        self.items = None

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)

        ## This one is a double click event
        ## self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.__onActivate)

        #self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))

        ## This subscribe line here will register TWICE
        ##  with the global "ps" - since this PogChooser class 
        ##  is instanced twice (view and target).
        ## I.e. There will be two "self".ChangeIcon funcs 
        ## fired on any one ps.pub(change_pog_icon) call.
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
        """
        pognochange: means No change to the selected Pog.
        """
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

        self.toggle_list_icons_according_to_selection( pognochange )

        wx.EndBusyCursor()

    def toggle_list_icons_according_to_selection( self, pognochange ):
        """
        Dec 2007 : This took me an entire day to figure out.
                   Man...

        Dec 2017: Updated and added much remarking. Ten years
        later... Hello past-Donn; you wrote terrible comments.

        Determines the images of the list items from the pov
        of whether we are VIEW or TARGET.

        The target control cal have multiple selections, this
        factors-in too.

        This is called from:
        1. wxgui: __init__
        2. gui_PogTargets: clear button event
        3. gui_PogChooser (myself): on select event
        """
        #print "self.indexselected:", self.indexselected
        ## Is there is an active selection?
        if self.indexselected > -1:
            
            ## Yep - let's work:
            c = self.GetItemCount()
            ## A little test of which kind of a McList am I?
            iAmTargetList = self.whoami=="TARGETPOG"

            for x in xrange(0, c):
                li = self.GetItem(x, 0)
                
                # WE ARE THE TARGET
                if iAmTargetList:
                    ## Installed test is for image index 1
                    isInstalled = li.GetImage() == 1

                    # Only if NOT installed do we even try to draw 
                    # the "triangle" target icon:
                    if not isInstalled:
                        # We are on the selected item.
                        if x == self.indexselected:

                            # A: pognochange == True
                            # i.e. The same pog is being
                            # clicked again, thus it can't be 
                            # the target anymore. (It's toggled off)
                            # Change the icon to normal (0)

                            # B: pognochange == False
                            # i.e. A different pog has been
                            # clicked. It's a new valid selection, so
                            # make it the target icon (2)
                            #n = 0 if pognochange else 2
                            n = self.icon_normal if pognochange \
                                    else self.icon_targetted

                            self.SetItemImage( x, n ) # This works.
                            # li.SetImage( n ) # This does
                            # not actually set the image.
                            # I can't burn more time on it.

                        # We are on an UNselected item
                        else:
                            # It is also NOT installed.
                            # Make it a normal icon (0)
                            # This is done because we can select
                            # multiple target pogs: we only 
                            # want ONE target icon so we must
                            # switch the others off.
                            n = self.icon_normal #0
                            self.SetItemImage( x, n )

                        # Go adjust the VIEW as well.
                        # If it's not an 'eye' (3) make
                        # it the same as me:
                        #vi = self.__VIEW.GetItem( x, 0 )
                        if self.__VIEW.GetItem( x, 0 ).GetImage() != \
                                self.icon_viewing:
                            self.__VIEW.SetItemImage( x, n )

                # WE ARE THE VIEW            
                else:
                    # We are the selected item
                    if x == self.indexselected:
                        # Make it an eye
                        self.SetItemImage( x, self.icon_viewing )
                    # We are NOT the selected
                    else:
                        # Make me whatever the icon in TARGET is
                        # It's my way to remember what I was. The 
                        # target icons are a good reference because
                        # they show:
                        # 1. Installed/Not installed
                        # 2. Targetted item
                        n = self.__TARGET.GetItem( x, 0 ).GetImage()
                        self.SetItemImage( x, n )


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
                if ipog.isInstalled(): 
                    i = self.icon_installed #1
                else: 
                    i = self.icon_normal #0
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
                        "under your locale.") % [p] # Irony in print!
                continue
            ## Okay, we have a valid pog name to use:
            li = wx.ListItem()
            li.SetImage(i)
            li.SetText(p)

            ## June 25, 2016: Something in wxPython changed 
            ## and li now needs an Id>0 (Capital "I"d. Weird)
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
        li.SetImage( self.icon_normal )#0)
        li.SetText( pogname )

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
        if T.isInstalled(): n = self.icon_installed #1
        else: n = self.icon_normal #0
        self.SetItemImage( index, n ) ## Found in wxWidgets documentation!

    def ClearLastIndex(self):
        """
        We need to reset the lastindexselected so that a click on the
        same item as last time will register. This is used in the Notebook
        when the page changes back to page 1, we want the user to
        be able to re-click the item that was clicked last time.
        """
        self.lastindexselected = -1
