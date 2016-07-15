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

class ScrolledFontView(wx.lib.scrolledpanel.ScrolledPanel):
	"""
	This is the main font control, the child of CLASS FontViewPanel (in gui_Middle.py)
	Draw a list of fitmaps from a font list object (derived from BasicFontList)

	July 2016
	=========
	After much fruitless slog, I finally found a crack in the problem of multiple columns of fonts
	at this URL: http://stackoverflow.com/questions/21431366/scrolledpanel-with-vertical-scrollbar-only-and-wrapsizer

	"""
	def __init__(self, parent):
		self.parent = parent
		wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, -1, style=wx.VSCROLL|wx.SUNKEN_BORDER)

		self.SetBackgroundColour('white')

		self.fitmaps = []

		## At least this one works.
		self.wheelValue = fpsys.config.points
		self.Bind( wx.EVT_MOUSEWHEEL, self.onWheel )

		## Make the sizer to hold the fitmaps: July 2016
		self.mySizer = wx.WrapSizer( flags=wx.EXTEND_LAST_ON_EACH_LINE )

		self.SetSizer(self.mySizer)

		## July 2016
		self.Bind(wx.EVT_SIZE, self.onSize)

		## July 2016
		## =========
		## Added this here too. There's some voodoo with a first run of Fonty.
		## If you rm the fp.conf and run, the fontview sometimes shows no 
		## scrollbar. this FitInside is a part of the battle against that.
		## Not 100% sure if this is kosher. Fuck it, I can't burn more time on it.
		self.mySizer.FitInside(self)

		#self.SetAutoLayout(1) #Iterative hacking says remark this. Go figure.
		self.SetupScrolling(rate_y=5, scroll_x=False)

		ps.sub( reset_top_left_adjustments, self.ResetTopLeftAdjustFlag ) ##DND: class ScrolledFontView 

	def onSize(self, evt):
		size = self.GetSize()
		vsize = self.GetVirtualSize()
		self.SetVirtualSize((size[0], vsize[1]))
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
			ps.pub( update_font_view ) # starts a chain of calls.

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


	def CreateFitmaps(self, viewobject) :
		"""
		Creates fitmaps (which draws them) of each viewobject FontItem down the control.
		viewobject: is a sub-list of fitems to display - i.e. after the page number math.
			** See filterAndPageThenCallCreateFitmaps in gui_Middle.py
		"""

		## Ensure we destroy all old fitmaps -- and I mean it.
		for f in self.fitmaps:
			f.Destroy()  #Ah, nailed ya! You bastard! I fart in your general direction!

		## Yes, die. Die!
		del self.fitmaps
		self.fitmaps = []

		## If our viewobject has NO FONTS inside it (i.e. it's an EmptyView object)
		## then setup a fake FontItem so we can have a dud Fitmap to show.
		if len(viewobject) == 0:
			empty_fitem = fontcontrol.InfoFontItem()
			fm = Fitmap( self, empty_fitem )
			self.fitmaps.append(fm) # I MUST add it to the list so that it can get destroyed when this func runs again next round.
			self.mySizer.Add( fm )
		else:

			## Okay - let's make fonts!
			self.mySizer.Clear() # Wipe all items out of the sizer.
			self.Scroll(0,0) # Immediately scroll to the top. This fixed a big bug.

			yld = fpsys.config.numinpage > 20
			for fitem in viewobject:
				## Create a Fitmap out of the FontItem we have at hand.
				fm = Fitmap( self, fitem )
				self.fitmaps.append( fm )
				## July 2016: Add it to the amazing WrapSizer
				## wx.RIGHT specifies we want border on the right!
				self.mySizer.Add( fm, 0, wx.ALIGN_LEFT|wx.ALIGN_BOTTOM|wx.RIGHT, border=5)

				## Added Oct 2009 to let app live on loooong lists.
				if yld: wx.Yield()

		#import pdb; pdb.set_trace()

		# Layout should be called after adding items.
		self.mySizer.Layout()
		self.mySizer.FitInside(self) # Iterative hacking leaves this one standing. self.Fit(), not so much.
