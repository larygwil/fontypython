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
    This is the main font control, the child of CLASS FontViewPanel
    (in gui_FontView.py). Draw a list of fitmaps from a font list 
    object (derived from BasicFontList).
    """
    def __init__(self, parent):
        self.parent = parent
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self,
                parent, -1, style=wx.VSCROLL|wx.SUNKEN_BORDER)

        ## Stops to use in fitmap drawing code.
        white_full = wx.Colour(255,255,255,255)
        white_zero = wx.Colour(255,255,255,0)
        black_zero = wx.Colour(0,0,0,0)
        c=255
        ucl = wx.Colour(c,c,c,255)
        ucd = wx.Colour(c-38,c-40,c-41,255)

        lbrown = wx.Colour(238,235,234,255)

        self.gstops = {
             "white_to_alpha" : wx.GraphicsGradientStops( 
                            startCol = white_zero, endCol = white_full ),
             "baptiste" : wx.GraphicsGradientStops(
                            startCol = lbrown, endCol = white_full ),
             "underline": wx.GraphicsGradientStops( 
                            startCol = ucd, endCol = ucl)
            }
        self.gstops["white_to_alpha"].Add(wx.Colour(255,255,255,128), 0.5)
        self.gstops["underline"].Add( ucd, 0.4)

        self.SetBackgroundColour(white_full)

        self.wheelValue = fpsys.config.points
        self.Bind( wx.EVT_MOUSEWHEEL, self.onWheel )

        ## July 2016
        ## Sep 2017. New hacks. Might not need this...
        #self.Bind(wx.EVT_SIZE, self.onSize)
        
        self.fitmap_sizer = wx.FlexGridSizer(cols = 1, vgap = 0, hgap = 0)
        self.SetSizer(self.fitmap_sizer)
        self.Fit()

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

            ##fpsys.state.point_size_changed_flag = True
            #TODO Kill: fpsys.state.reflow_only = False 
            ps.pub( update_font_view ) # starts a chain of calls.
            ##fpsys.state.point_size_changed_flag = False
            ##fpsys.state.reflow_only = True

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

    def MinimalCreateFitmaps( self, viewobject):
        """
        Note: I am not rendering the fitmaps when the frame's size changed.
              
        """
        #print "-------------------------"
        #print "MinimalCreateFitmaps runs"
        self.Freeze()
        panelwidth = max(420,self.GetSize()[0]) #First run it's weird. After that it works.
        #print self.GetSize()[0]

        if len(viewobject) == 0:
            self.fitmap_sizer.Clear(True) # Wipe-out the past
            empty_fitem = fontcontrol.InfoFontItem()
            fm = Fitmap( self, empty_fitem )
            # force the width down a little. I want
            # wrapping to happen when window is too
            # small.
            #panelwidth = self.GetSize()[0]
            #print panelwidth
            #panelwidth = max(360,self.GetSize()[0]) #First run it's weird. After that it works.
            #if panelwidth < 300
            pw = panelwidth - 25#(panelwidth/4))
            fm.assemble_bitmap( pw )
            self.fitmap_sizer.Add( fm )
        else:
            # Let's compare what we had before (the contents of the sizer!) with what
            # is coming-in new, i.e. the viewobject list.
            #print self.fitmap_sizer.GetChildren()
            td = {}
            for kid in self.fitmap_sizer.GetChildren():
                fitmap = kid.GetWindow() #is the fitmap within
                fitem = fitmap.fitem
                if fitem not in viewobject:
                    ## If the fitem is not one we want to show:
                    ## 1. Remove it from the sizer
                    ## 2. Destroy it.
                    #print " ..Murdering:", fitmap.name
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
                ## Since their states may have changed, we do the
                ## render_and_measure_glyphs on all fitmaps again:
                wid = fm.render_and_measure_glyphs()
                ## Record the width, but if it's wider than the panel
                ## just chop it. It's an asshole anyway.
                w.append(min(wid, panelwidth))


            # Clear the sizer. Docs say this "detaches" all children.
            # Therefore, the fitmaps that were in there, are no longer in there.
            # (They are physically laying about in the parent - the FontViewPanel.)
            # In a moment, we'll re-add all the relevant fitmaps to the sizer,
            # so everything kind of works-out. I hope...
            self.fitmap_sizer.Clear() # ..(True) murders the fitmaps. We no like. Hisssssss!

            self.Scroll(0,0) # Immediately scroll to the top. This fixed a big bug.
            
            ## Let's bother with all the math if columns are even a thing:
            if fpsys.config.max_num_columns > 1:
                ## Credit to Michael Moller for clueing me onto "standard deviation".
                ## My soluition: Take the mean of the widths and add a bit "more".
                lw = len(w) # cannot be 0. I feel confident!
                sw = sum(w)
                #print w

                ## 1. Standard Deviation
                ##    Calc the variance by subtracting each width from the 
                ##    average and then taking the square summing along. 
                ##    Calc the std deviation by sqrting that variance.
                a = sw / lw # the average
                sd = ( sum( ( a - i ) **2 for i in w ) / lw ) ** 0.5

                ## 2. I also get av of that std deviation, just to 
                ##    shorten it a little bit "more".
                asd = sd / lw

                ## 3. My result is the sum of these two.
                avw = a + asd

                ## Can we afford some columns?
                ##  ..Also prevent any poss div by 0
                cols = max( 1, int(panelwidth / max(avw, 1) ) )

                #Nov 2017: New option in settings to control columns"
                cols = min( cols, fpsys.config.max_num_columns )

                ## Get a better actual width for the columns!
                ##  ..Also prevent any poss div by 0
                colw = int(panelwidth / max(cols, 1))
            else:
                cols = 1
                colw = panelwidth

            #print "colw:",colw
            self.fitmap_sizer.SetCols(cols)

            ## Loop viewobject, get fitmaps, prep them with the new width
            ## and then plug them into the sizer
            for fitem in viewobject:
                fm = td[ fitem ] # we get them from the dict
                #print fm
                #print colw
                fm.assemble_bitmap(colw)
                self.fitmap_sizer.Add(fm, flag=wx.wx.ALIGN_BOTTOM) # Here we re-add the fitmaps.

        self.fitmap_sizer.FitInside(self)
        ## Trying this freeze/thaw thing. Not sure if there's any advantage.
        self.Thaw()
        #print "====EXIT MinimalCreateFitmaps====="

"""
Unused algorithms in MinimalCreateFitmaps
            if alg==1:
                percent = .2 # == 10%
                def trimmed_mean(data, percent):
                    # sort list
                    data = sorted(data)
                    # number of elements to remove from both ends of list
                    outliers = int(percent * len(data))
                    # remove elements
                    data = data[outliers:-outliers]
                    return sum(data) / len(data)
                avw = trimmed_mean(w, percent)                

            elif alg==2:
                ## A hacky trimmed mean mess
                l = len(w)
                if l < 3: 
                    avw = sum(w)/l
                else:
                    ## When the widths are all similar, it's hard to know
                    ## which to discard... Too much math for my head. :(
                    avw_tm = max( 1, (sum(w) - max(w) - min(w)) / l-2 )
                    avw_foo = sum(w)/l
                    avw = min(avw_foo, avw_tm) # a hack to prefer fewer cols
"""
