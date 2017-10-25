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

import collections

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

        self.wheelValue = fpsys.config.points
        self.Bind( wx.EVT_MOUSEWHEEL, self.onWheel )

        ## July 2016
        ## Sep 2017. New hacks. Might not need this...
        #self.Bind(wx.EVT_SIZE, self.onSize)
        
        self.fitmap_sizer = wx.FlexGridSizer(cols = 1)
        self.SetSizer(self.fitmap_sizer)

        self.SetupScrolling(rate_y = 5, scroll_x = False)

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

            #fpsys.state.point_size_changed_flag = True
            fpsys.state.reflow_only = False 
            ps.pub( update_font_view ) # starts a chain of calls.
            #fpsys.state.point_size_changed_flag = False
            fpsys.state.reflow_only = True

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
        print "-------------------------"
        print "MinimalCreateFitmaps runs"
        self.Freeze()
        if len(viewobject) == 0:
            self.fitmap_sizer.Clear(True) # Wipe-out the past
            empty_fitem = fontcontrol.InfoFontItem()
            fm = Fitmap( self, empty_fitem )
            fm.prepareBitmap()
            self.fitmap_sizer.Add( fm )
        else:
            # Let's compare what we had before (the contents of the sizer!) with what
            # is coming-in new, i.e. the viewobject list.
            td = {}
            for kid in self.fitmap_sizer.GetChildren():
                fitmap = kid.GetWindow() #is the fitmap within
                fitem = fitmap.fitem
                if fitem not in viewobject:
                    ## If the fitem is not one we want to show:
                    ## 1. Remove it from the sizer
                    ## 2. Destroy it.
                    print " ..Murdering:", fitmap.name
                    self.fitmap_sizer.Detach(fitmap)
                    fitmap.Destroy()
                else:
                    ## This "old" fitmap is okay, let's keep it aside.
                    td[fitem]=fitmap
            

            w=[] # widths
            for fitem in viewobject:
                # Seek it in the dict we just made:
                fm = td.get(fitem, None)
                if not fm:
                    ## the fitmap was not found, it must be instanced
                    fm = Fitmap(self, fitem)
                    td[ fitem ] = fm # Store it for just now

                wid = fm.measureBitmap()

                w.append(wid) # record the widths

            # Clear the sizer. Docs say this "detaches" all children.
            # Therefore, the fitmaps that were in there, are no longer in there.
            # (They are physically laying about in the parent - the FontViewPanel.)
            # In a moment, we'll re-add all the relevant fitmaps to the sizer,
            # so everything kind of works-out. I hope...
            self.fitmap_sizer.Clear() # ..(True) murders the fitmaps. We no like. Hisssssss!

            self.Scroll(0,0) # Immediately scroll to the top. This fixed a big bug.
            
            panelwidth = self.GetSize()[0] #First run it's 0. After that it works.

            ## Get some kind of average width.
            avw = int( sum(w) / max( len(w), 1) )
            ## Can we afford some columns?
            cols = max( 1, int(panelwidth / avw) )
            ## Get a better actual width for the columns!
            colw = int(panelwidth/cols)

            self.fitmap_sizer.SetCols(cols)

            ## Loop viewobject, get fitmaps, prep them with the new width
            ## and then plug them into the sizer
            for fitem in viewobject:
                fm = td[ fitem ] # we get them from the dict
                fm.prepareBitmap(colw)
                self.fitmap_sizer.Add(fm) # Here we re-add the fitmaps.

        self.fitmap_sizer.FitInside(self)
        ## Trying this freeze/thaw thing. Not sure if there's any advantage.
        self.Thaw()
        print "====EXIT MinimalCreateFitmaps====="







    def xxxMinimalCreateFitmaps( self, viewobject):#, force = False ) :
        print "-------------------------"
        print "MinimalCreateFitmaps runs"
        self.Freeze()
        if len(viewobject) == 0:
            self.fitmap_sizer.Clear(True) # Wipe-out the past
            empty_fitem = fontcontrol.InfoFontItem()
            fm = Fitmap( self, empty_fitem )
            fm.prepareBitmap()
            self.fitmap_sizer.Add( fm )
        else:
            # Let's compare what we had before (the contents of the sizer!) with what
            # is coming-in new, i.e. the viewobject list.
            td = {}
            for kid in self.fitmap_sizer.GetChildren():
                fitmap = kid.GetWindow() #is the fitmap within
                fitem = fitmap.fitem
                if fitem not in viewobject:
                    ## If the fitem is not one we want to show:
                    ## 1. Remove it from the sizer
                    ## 2. Destroy it.
                    print " ..Murdering:", fitmap.name
                    self.fitmap_sizer.Detach(fitmap)
                    fitmap.Destroy()
                else:
                    ## This "old" fitmap is okay, let's keep it aside.
                    td[fitem]=fitmap
            

            w=[] # widths
            for fitem in viewobject:
                # Seek it in the dict we just made:
                fm = td.get(fitem, None)
                if fm:
                    ## The "old" fitmap is there. Let's refresh it.
                    ## This avoids as much work as poss, for e.g. in the
                    ## rendering of the font faces etc. See gui_Fitmap.py
                    fm.prepareBitmap()
                else:
                    ## the fitmap was not found, it's must be instanced
                    fm = Fitmap(self, fitem)
                    fm.prepareBitmap() # Does more work on a fresh spawn.
                    td[ fitem ] = fm # Store it for just now
                w.append(fm.width) # record the widths

            # Clear the sizer. Docs say this "detaches" all children.
            # Therefore, the fitmaps that were in there, are no longer in there.
            # (They are physically laying about in the parent - the FontViewPanel.)
            # In a moment, we'll re-add all the relevant fitmaps to the sizer,
            # so everything kind of works-out. I hope...
            self.fitmap_sizer.Clear() # ..(True) murders the fitmaps. We no like. Hisssssss!

            self.Scroll(0,0) # Immediately scroll to the top. This fixed a big bug.
            
            print "***CALC"
            self.colw = int( sum(w) / max( len(w), 1) )
            print "sum(w):", sum(w)
            print "averaged is: colw:", self.colw

            panelwidth = self.GetSize()[0] #First run it's 0. After that it works.
            print "panelwidth:", panelwidth

            ## Can we afford some columns?
            #cols = int(panelwidth / self.colw) if self.colw < panelwidth else 1
            cols = max( 1, int(panelwidth / self.colw) )
            print "cols:",cols
            print " vs int(/):", int(panelwidth/self.colw)
            print "***END CALC"

            ## Let's also divvy-up the hgap
            #hgap = (panelwidth - (cols * self.colw)) / 2

            self.fitmap_sizer.SetCols(cols)

            ## Loop viewobject, get fitmaps and plug them into the sizer
            for fitem in viewobject:
                fm = td[ fitem ] # we get them from the dict
                ## JULY 2016
                ## =========
                ## If the bitmap is wider than a column, we will crop it
                ## IDEA: Do a fade to white instead of a hard cut on the right.
                #if fm.bitmap.GetWidth() > self.colw:
                if fm.width > self.colw:
                    fm.crop(self.colw)
                self.fitmap_sizer.Add(fm) # Here we re-add the fitmaps.

        self.fitmap_sizer.FitInside(self)
        ## Trying this freeze/thaw thing. Not sure if there's any advantage.
        self.Thaw()
        print "====EXIT MinimalCreateFitmaps====="

































    def OKOKOKMinimalCreateFitmaps( self, viewobject):#, force = False ) :
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

        OCT 2017
        ==
        self.fitmap_sizer.Clear(True) sucks, and here's why:
        1. You have to call True to get the sizer items to fuck off.
        2. It deletes the shit out of those objects. Any other variables to them
           now hold "wxPython wrapper for DELETED Fitmap object"s. HAND.
        This means I cannot keep some fitmaps around if they do not need to redraw.
        I have to make them anew and fill the sizer every time.
        Fuck.

        """
        print "-------------------------"
        print "MinimalCreateFitmaps runs"

        print " AND self.fitmaps:", self.fitmaps
        print
        ## Sept2017:
        ## WIP. Seeking a way to detect whether what we showed last time
        ## is different from what we must show now.
        ## On wheel zoom -> it should recreate fitmaps,for e.g.
        ## But, on a mere resize of the window, why bother?
        
        ## If our viewobject has NO FONTS inside it (i.e. it's an EmptyView object)
        ## then setup a fake FontItem so we can have a dud Fitmap to show.
        if len(viewobject) == 0:
            self.fitmap_sizer.Clear(True) # Wipe-out the past
            self.fitmaps.clear() # no need for this either
            empty_fitem = fontcontrol.InfoFontItem()
            fm = Fitmap( self, empty_fitem )
            fm.prepareBitmap()
            self.fitmap_sizer.Add( fm )
        else:

            # Let's compare what we had before (the fitmaps dict) with what
            # is coming in now, the viewobject list.
            # I am using an OrderedDict with fitems as keys and fitmaps as values.
            # to relate these two domains.
            
            oldfitmaps=self.fitmaps.copy()
            print "oldfitmaps just made:", oldfitmaps
            for newfis in viewobject:
                oldfitmaps.pop(newfis.name,None) # remove anything that's new, sans error.
            # now, oldfitmaps is only wnatever fitmaps are not relevant
            print "oldfitmaps:", oldfitmaps

            ## trying to see how this sizer ticks. fucking fuck.
            #for i in self.fitmap_sizer.GetItem(i):
            kids = self.fitmap_sizer.GetChildren()
            for kid in kids:
                w = kid.GetWindow() #is the fitmap within
                if oldfitmaps.get(w.name, None):
                    print "Murdering:", w
                    self.fitmap_sizer.Detach(w) #???
                    w.Destroy()#?
            
            ## fresh fitmaps: Only the fitmaps not deleted.
            ffs = {}
            ffs = {k:v for k,v in self.fitmaps.items() if k not in oldfitmaps}

            ## Make my fitmaps list be this new fresh list:
            self.fitmaps.clear()
            self.fitmaps = ffs


            w=[] # widths
            td={}
             
            for fi in viewobject:
                # Seek it in my dict of fitmaps that already exist
                #print "**SEEK:", fi.name
                #print "  in:", self.fitmaps.keys()
                fm = self.fitmaps.get(fi.name, None)
                #print "Found:", fm
                if fm:
                    #print "Exists, calling prepareBitmap on ", fm.name
                    fm.prepareBitmap()
                else:
                    # the fi key was not found, it's new
                    fm = Fitmap(self, fi) # so, make it.
                    #print "Making ", fm.name
                    # slow call: pil and bitmaps etc.
                    fm.prepareBitmap()
                    # put it into my fitmaps dict
                    self.fitmaps[fi.name] = fm
                #td[ fi.name ] = fm
                w.append(fm.width) # rec width

            #print "td aescrawl.ttf contains:", td["aescrawl.ttf"]
            # Now, replace the last od with the one we just filled:
            #self.fitmaps.clear()
            #self.fitmaps.update(td) #self.tod
            #for k,v in td.iteritems(): self.fitmaps[k]=v
            #print " ! self.fitmaps:", self.fitmaps


            # Clear the sizer. This seems to work. It's all right. IT'S ALL RIGHT...
            self.fitmap_sizer.Clear() # ..(True) murders the fitmaps. Hisssssss!

            self.Scroll(0,0) # Immediately scroll to the top. This fixed a big bug.

            self.colw = int( sum(w) / max( len(w), 1) )

            panelwidth = self.GetSize()[0] #First run it's 0. After that it works.

            ## Can we afford some columns?
            cols = int(panelwidth / self.colw) if self.colw < panelwidth else 1

            ## Let's also divvy-up the hgap
            #hgap = (panelwidth - (cols * self.colw)) / 2

            self.fitmap_sizer.SetCols(cols)

            ## Loop again and plug them into the sizer
            for fi in viewobject: #self.fitmaps.values():
                #print "  ! Getting fitmap for:", fi.name
                fm = self.fitmaps[fi.name]
                #print "---", fm.name
                ## JULY 2016
                ## =========
                ## If the bitmap is wider than a column, we will crop it
                ## IDEA: Do a fade to white instead of a hard cut on the right.
                if fm.bitmap.GetWidth() > self.colw:
                    fm.crop(self.colw)
                #import copy
                #fm2=copy.copy(fm)
                self.fitmap_sizer.Add(fm)




        self.fitmap_sizer.FitInside(self)
        print "====EXIT MinimalCreateFitmaps====="

