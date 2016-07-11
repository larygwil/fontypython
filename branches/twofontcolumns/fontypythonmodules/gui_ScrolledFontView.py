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

class ScrolledFontView(wx.lib.scrolledpanel.ScrolledPanel) :
	"""
	This is the main font control, the child of CLASS FontViewPanel (in gui_Middle.py)
	Draw a list of fitmaps from a font list object (derived from BasicFontList)
	"""
	def __init__(self, parent):
		self.parent = parent
		wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, -1, style=wx.VSCROLL|wx.SUNKEN_BORDER)

		self.SetBackgroundColour('white')

		
		self.fitmaps = []
		
		## At least this one works.
		self.wheelValue = fpsys.config.points
		self.Bind( wx.EVT_MOUSEWHEEL, self.onWheel )
		
		## Make the sizer to hold the fitmaps
		self.mySizer = wx.BoxSizer(wx.VERTICAL)
		#self.mySizer = wx.GridBagSizer(0,0)
		#self.mySizer = wx.WrapSizer() # Is very nice, but kinda nervous; skittish. V sensitive to widths.
		
		self.SetSizer(self.mySizer)

		self.firstrun =True 
		self.SetAutoLayout(1)
		self.SetupScrolling(rate_y=5, scroll_x=False)
		
		ps.sub( reset_top_left_adjustments, self.ResetTopLeftAdjustFlag ) ##DND: class ScrolledFontView 

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
			ps.pub( update_font_view ) # starts a chain of calls.
			
			##self.Scroll(xPos, yPos)
			return
		## Keep the wheel event going
		evt.Skip()

	# Sept 2009
	def ResetTopLeftAdjustFlag( self ):
		'''Each fitem has a top_left_adjust_completed flag. False forced the fitmaps to re-calculate the adjustment for top-left.'''
		for fi in fpsys.state.viewobject:
			fi.top_left_adjust_completed = False


	def DoGetBestSize(self):
		"""
		Very strange behaviour. AFAICT this is called automatically, sometimes, before
		__init__ of this class! :O

		Anyway: July 2016
		I noticed that on first run the width if the parent panel is 128
		So, I am gonna look for that rubbish and replace it with a size calculated from
		the stuff recorded in the config. (These, too, have defaults that work.)
		"""

		# Go get the size of the parent panel.
		ps = self.parent.GetSize()

		if ps.width <=128:
			# Yeah, override this damn width.
			w = fpsys.config.size[0]# Use the last known width of the entire window as an initial size estimate.
			wl = fpsys.config.leftSash
			wr = fpsys.config.rightSash
			ps.width = w-wl-wr

		self.CacheBestSize(ps) #Prevent this def running too often.
		return ps


	def CreateFitmaps(self, viewobject) :
		"""
		Creates fitmaps (which draws them) of each viewobject FontItem down the control.
		
		viewobject: is a sub-list of fitems to display - i.e. after the page number math.

		** See filterAndPageThenCallCreateFitmaps in gui_Middle.py
		"""

		## Ensure we destroy all old fitmaps -- and I mean it.
		for f in self.fitmaps:
			f.Destroy()  #Ah, nailed ya! You bastard! I fart in your general direction!

		del self.fitmaps
		self.fitmaps = []

		## It's NB to notice that the fitems being put into self.fitmaps are
		## the SAME items that are in the viewobject.


		## If our viewobject has NO FONTS inside it (i.e. it's an EmptyView object)
		## then setup a fake FontItem so we can have a dud Fitmap to show.
		if len(viewobject) == 0:
			empty_fitem = fontcontrol.InfoFontItem()
			fm = Fitmap( self, (0, 0), empty_fitem )
			self.fitmaps.append(fm) # I MUST add it to the list so that it can get destroyed when this func runs again next round.
			self.mySizer.Add( fm,0,0 )
		else:

			## Okay - let's make fonts!

			## 1. Build all the fitmaps - keep widths in a list
			widths=[]
			for fitem in viewobject:

				## Create a Fitmap out of the FontItem we have at hand.
				fm = Fitmap( self, (0,0), fitem )
				self.fitmaps.append( fm )
				widths.append( fm.totwidth )
				#print "Fitmap made: %s" % fm.name

				## Added Oct 2009 to let app live on loooong lists.
				if fpsys.config.numinpage > 20: wx.Yield() 

			## 2. Get max width
			columnwidth = max(widths)

			## 3. cmp to parent width to calc number of columns
			self.InvalidateBestSize() # Reset the cache
			s = self.DoGetBestSize() # Force re-call
			#print "s w,h:", s.width, s.height
			ww = s.width
			#print "columnwidth, ww:", columnwidth, ww
			cols=1
			if columnwidth < ww:
				## The fitems are smaller than the panel
				## How many columns can we squeeze in?
				cols = int(ww / columnwidth)
				exactcolwidth = (ww / cols) # for drawing an underline.. maybe

			## We don't need to calc rows - the GridSizer can do that.
			#L = len(self.fitmaps)
			#rows = (int(L)/cols)	 + L%cols
			#rows = rows if (rows>0) else 1

			## 4. make the sizer
			#gs = wx.GridSizer( cols=cols, hgap=0, vgap=0 )
			gs = wx.FlexGridSizer( cols=cols, hgap=0, vgap=0 )

			## 5. Reloop and add to GridSizer
			for fm in self.fitmaps:
				gs.Add(fm,0,wx.ALIGN_LEFT|wx.ALIGN_TOP)

			self.mySizer.Clear() # Wipe all items out of the sizer.
			self.Scroll(0,0) # Immediately scroll to the top. This fixed a big bug.
			self.mySizer.Add(gs)

		# Layout should be called after adding items.
		self.mySizer.Layout()
		# This gets the sizer to resize in harmony with the virtual (scrolling) nature of its parent (self).
		self.mySizer.FitInside(self)
