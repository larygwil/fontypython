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
import wx.lib.scrolledpanel

from pubsub import *

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

import fpsys # Global objects

from gui_Fitmap import * #Also brings in 'ps' variable

class ScrolledFontView(wx.lib.scrolledpanel.ScrolledPanel):
    """
    This is the main font control, the child of CLASS FontViewPanel (in gui_FontView.py)
    Draw a list of fitmaps from a font list object (derived from BasicFontList)

    July 2016
    =========
  Useful url: http://stackoverflow.com/questions/21431366/scrolledpanel-with-vertical-scrollbar-only-and-wrapsizer

    """
    def __init__(self, parent):
        self.parent = parent
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, -1, style=wx.VSCROLL|wx.SUNKEN_BORDER)

        self.SetBackgroundColour('white')

        self.fitmaps = []

        self._last_viewobject = None

        self.wheelValue = fpsys.config.points
        self.Bind( wx.EVT_MOUSEWHEEL, self.onWheel )

        ## July 2016
        ## Sep 2017. New hacks. Might not need this...
        #self.Bind(wx.EVT_SIZE, self.onSize)

        self.SetupScrolling(rate_y=5, scroll_x=False)

        ps.sub( reset_top_left_adjustments, self.ResetTopLeftAdjustFlag ) ##DND: class ScrolledFontView 

    def onSize(self, evt):
        """
        Set my virtual size to be actual size across, by
        virtual size down. Cleverly solves much pain. Thanks Anon.
        """
        size = self.GetSize()
        vsize = self.GetVirtualSize()
        self.SetVirtualSize( (size[0], vsize[1]) )
        evt.Skip()

    def onWheel( self, evt ):
        """
        Added Dec 2007
        Change point size with ctrl+scroll
        """
        n = 10
        if evt.GetWheelRotation() < 0: n = -10
        if evt.ControlDown():
            self.wheelValue += n
            if self.wheelValue < 10: self.wheelValue = 10
            if self.wheelValue > 200: self.wheelValue = 200
            fpsys.config.points = int(self.wheelValue)

            ## Tried to restore the scrollbar, but it crashes the app
            ##xPos, yPos = self.GetViewStart()
            self.ResetTopLeftAdjustFlag() ## Sept 2009 : size change means we need new values for fitmaps

            fpsys.state.point_size_changed_flag = True
            ps.pub( update_font_view ) # starts a chain of calls.
            fpsys.state.point_size_changed_flag = False

            return
        ## Keep the wheel event going
        evt.Skip()

    # Sept 2009
    def ResetTopLeftAdjustFlag( self ):
        '''
        Each fitem has a top_left_adjust_completed flag.
        False forces the fitmaps to re-calculate the adjustment for top-left.
        (Only when a call to update_font_view happens, of course.)
        '''
        for fi in fpsys.state.viewobject:
            fi.top_left_adjust_completed = False



    def MinimalCreateFitmaps( self, viewobject):#, force = False ) :
        """
        July 16, 2016
        =============
        A forceful approach: Destroy old sizer, make a new one.
        It seems to work.

        FlexGridSizer
        =============
        With this sizer, I get predictable columns of the same size. It forces more work - to
        calculate the max width fitmap and thence the number of columns.
        I also perform a crop on bitmaps over the average width.

        Sept 2017
        =========
        Added the _last_viewobject stuff to detect when the stuff in the fontview has not
        changed from what was here last time.

        OCT 2017
        ==
        Stripped all wx.Yield() out. Too fubar to grok.

        """
        print "-------------------------"
        print "MinimalCreateFitmaps runs"

        ## Sept2017:
        ## WIP. Seeking a way to detect whether what we showed last time
        ## is different from what we must show now.
        ## On wheel zoom -> it should recreate fitmaps,for e.g.
        ## But, on a mere resize of the window, why bother?
        allsame = False
        if not fpsys.state.point_size_changed_flag:
            if self._last_viewobject == viewobject:
                allsame = True

        #print "allsame:", allsame

        self._last_viewobject = viewobject


        ## Uncertain: Feel I should strive to delete previous sizers..
        sz = self.GetSizer()
        if sz:
            print "Found old sizer:", sz
            # remove all the items
            sz.Clear()
            # destroy it
            self.SetSizer(None) # (vim) ddp here, and run - fonty segfaults!
            #sz.Destroy() # This errors out.
            del sz
        ## I think that sizer is at least suffering and will soon die. RIP!

        self.Scroll(0,0) # Immediately scroll to the top. This fixed a big bug.

        if not allsame:
            ## Ensure we destroy all old fitmaps -- and I mean it.
            for f in self.fitmaps:
                print "Destroying fitmap:", f
                f.Destroy()  #Ah, nailed ya! You bastard! I fart in your general direction!

            ## Yes, die. Die!
            del self.fitmaps[:]

        ## If our viewobject has NO FONTS inside it (i.e. it's an EmptyView object)
        ## then setup a fake FontItem so we can have a dud Fitmap to show.
        if len(viewobject) == 0:
            ## We only need a simple box sizer
            bs = wx.BoxSizer(wx.VERTICAL)

            empty_fitem = fontcontrol.InfoFontItem()
            fm = Fitmap( self, empty_fitem )
            self.fitmaps.append(fm) # I MUST add it to the list so that it can get destroyed when this func runs again next round.

            bs.Add( fm )
            self.SetSizer(bs)
            bs.FitInside(self)

        else:
            ## Okay - let's make fonts!
            if not self.fitmaps:
                #print "Making fitmap from:", viewobject
                w = []
                for fitem in viewobject:
                    ## Create a Fitmap out of the FontItem we have at hand.
                    #print "Fitmap instance."
                    fm = Fitmap( self, fitem )
                    #print "generate_pil_bitmaps"
                    fm.generate_pil_bitmaps()
                    print "Made fitmap:", fm.name
                    #print " height:",fm.height
                    self.fitmaps.append( fm )
                    #w.append(fm.GetBestSize()[0])
                    w.append(fm.pilwidth)

                ## I am getting an AVERAGE of all the widths
                ## This cuts the super-long bitmaps down to
                ## a more-or-less size with the others.
                self.colw = int( sum(w) / max( len(w), 1) )

            # Let's redraw whatever may have changed within
            # each fitmap's drawing state:
            for fitmap in self.fitmaps:
                print "refresh:",fitmap.name
                #print " height:",fitmap.height
                ds = fitmap.prepareBitmap()
                # If there was some change in the draw state, refresh the bitmap.
                if ds > 0:
                    # Force a redraw of the bitmap. 
                    # Without this, nothing appears to change...
                    fitmap.Refresh() 

            cols = 1
            print "*** self.colw:", self.colw#max(w)

            panelwidth = self.GetSize()[0] #First run it's 0. After that it works.

            ## Can we afford some columns?
            if self.colw < panelwidth:
                cols = int(panelwidth / self.colw)

            ## Let's also divvy-up the hgap
            hgap = (panelwidth - (cols * self.colw)) / 2

            ## Make the new FlexGridSizer
            #fgs = wx.FlexGridSizer( cols=cols, hgap=hgap, vgap=2 )
            self.fgs = wx.BoxSizer(wx.VERTICAL)
            print "New sizer cols %s" % cols

            ## Loop again and plug them into the sizer
            for fm in self.fitmaps:
                ## JULY 2016
                ## =========
                ## If the bitmap is wider than a column, we will crop it
                ## IDEA: Do a fade to white instead of a hard cut on the right.
                ##
                if fm.bitmap.GetWidth() > self.colw:
                    fm.crop(self.colw)

                ## Add fm to the sizer
                print "adding to sizer:", fm.name, (fm.height, fm.width)
                #fgs.Add(fm, 0, wx.ALIGN_LEFT | wx.ALIGN_BOTTOM)
                #fgs.Add(fm,0,wx.ALIGN_LEFT|wx.ALIGN_BOTTOM)
                self.fgs.Add(fm)

            print "   for loop done."
            self.SetSizer(self.fgs)
            self.fgs.FitInside(self)
            print "====EXIT MinimalCreateFitmaps====="


    def xxMinimalCreateFitmaps( self, viewobject):#, force = False ) :
        """
        July 16, 2016
        =============
        A forceful approach: Destroy old sizer, make a new one.
        It seems to work.

        FlexGridSizer
        =============
        With this sizer, I get predictable columns of the same size. It forces more work - to
        calculate the max width fitmap and thence the number of columns.
        I also perform a crop on bitmaps over the average width.

        Sept 2017
        =========
        Added the _last_viewobject stuff to detect when the stuff in the fontview has not
        changed from what was here last time.

        OCT 2017
        ==
        Stripped all wx.Yield() out. Too fubar to grok.

        """
        #print "-------------------------"
        #print "MinimalCreateFitmaps runs"

        ## Sept2017:
        ## WIP. Seeking a way to detect whether what we showed last time
        ## is different from what we must show now.
        ## On wheel zoom -> it should recreate fitmaps,for e.g.
        ## But, on a mere resize of the window, why bother?
        allsame = False
        if not self._point_size_changed_flag:
            if self._last_viewobject == viewobject:
                allsame = True

        #print "allsame:", allsame

        self._last_viewobject = viewobject


        ## Uncertain: Feel I should strive to delete previous sizers..
        sz = self.GetSizer()
        if sz:
            # remove all the items
            sz.Clear()
            # destroy it
            self.SetSizer(None) # (vim) ddp here, and run - fonty segfaults!
            #sz.Destroy() # This errors out.
            del sz
        ## I think that sizer is at least suffering and will soon die. RIP!

        self.Scroll(0,0) # Immediately scroll to the top. This fixed a big bug.

        if not allsame:
            ## Ensure we destroy all old fitmaps -- and I mean it.
            for f in self.fitmaps:
                print "Destroying fitmap:", f
                f.Destroy()  #Ah, nailed ya! You bastard! I fart in your general direction!

            ## Yes, die. Die!
            del self.fitmaps[:]

        ## If our viewobject has NO FONTS inside it (i.e. it's an EmptyView object)
        ## then setup a fake FontItem so we can have a dud Fitmap to show.
        if len(viewobject) == 0:
            ## We only need a simple box sizer
            bs = wx.BoxSizer(wx.VERTICAL)

            empty_fitem = fontcontrol.InfoFontItem()
            fm = Fitmap( self, empty_fitem )
            self.fitmaps.append(fm) # I MUST add it to the list so that it can get destroyed when this func runs again next round.

            bs.Add( fm )
            self.SetSizer(bs)
            bs.FitInside(self)

        else:
            ## Okay - let's make fonts!
            if not self.fitmaps:
                #print "Making fitmap from:", viewobject
                w = []
                for fitem in viewobject:
                    ## Create a Fitmap out of the FontItem we have at hand.
                    fm = Fitmap( self, fitem )
                    #print "Made fitmap:", fm
                    #print " height:",fm.height
                    self.fitmaps.append( fm )
                    #w.append(fm.GetBestSize()[0])
                    w.append(fm.bitmap.GetWidth())

                ## I am getting an AVERAGE of all the widths
                ## This cuts the super-long bitmaps down to
                ## a more-or-less size with the others.
                self.colw = int( sum(w) / max( len(w), 1) )
            else:
                # Let's redraw whatever may have changed within
                # each fitmap's drawing state:
                for fitmap in self.fitmaps:
                    #print "refresh:",fitmap
                    #print " height:",fitmap.height
                    ds = fitmap.prepareBitmap()
                    # If there was some change in the draw state, refresh the bitmap.
                    if ds > 0:
                        # Force a redraw of the bitmap. 
                        # Without this, nothing appears to change...
                        fitmap.Refresh() 

            cols = 1

            panelwidth = self.GetSize()[0] #First run it's 0. After that it works.

            ## Can we afford some columns?
            if self.colw < panelwidth:
                cols = int(panelwidth / self.colw)

            ## Let's also divvy-up the hgap
            hgap = (panelwidth - (cols * self.colw)) / 2

            ## Make the new FlexGridSizer
            fgs = wx.FlexGridSizer( cols=cols, hgap=hgap, vgap=2 )
            print "New sizer cols %s" % cols

            ## Loop again and plug them into the sizer
            for fm in self.fitmaps:
                ## JULY 2016
                ## =========
                ## If the bitmap is wider than a column, we will crop it
                ## IDEA: Do a fade to white instead of a hard cut on the right.
                ##
                if fm.bitmap.GetWidth() > self.colw:
                    fm.crop(self.colw)

                ## Add fm to the sizer
                print "adding to sizer"
                #fgs.Add(fm, 0, wx.ALIGN_LEFT | wx.ALIGN_BOTTOM)
                fgs.Add(fm,0,wx.ALIGN_LEFT|wx.ALIGN_BOTTOM)

            print "   for loop done."
            self.SetSizer(fgs)
            fgs.FitInside(self)
            print "====EXIT MinimalCreateFitmaps====="


