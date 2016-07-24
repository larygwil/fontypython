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

		#tc = wx.StaticText( self, -1, "abcdefghijklnbop"*100 )
		#tmpsizer = wx.BoxSizer(wx.VERTICAL)
		#tmpsizer.Add(tc,0,wx.ALL)
		#tmpsizer.AddSpacer( 700 )
		#self.SetSizer(tmpsizer)
		#tmpsizer.FitInside(self)

		## July 2016
		self.Bind(wx.EVT_SIZE, self.onSize)

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


	def CreateFitmapsWRAPSIZER(self, viewobject) :
		"""
		Creates fitmaps (which draws them) of each viewobject FontItem down the control.
		viewobject: is a sub-list of fitems to display - i.e. after the page number math.
			** See filterAndPageThenCallCreateFitmaps in gui_Middle.py

		NOTE: Uses a WrapSizer which has some side-effects. Wide fitmaps, early in the
					list tend to "shield" narrow ones under them, so the wrapping leaves them
					inline - causing some singles and some doubles, in a line.

					I tried to crop the fitmaps so they are all the same size. This road is fail.
		"""

		## Ensure we destroy all old fitmaps -- and I mean it.
		for f in self.fitmaps:
			f.Destroy()  #Ah, nailed ya! You bastard! I fart in your general direction!

		## Yes, die. Die!
		del self.fitmaps
		self.fitmaps = []

		## Create the sizer once, on the fly.
		if self.GetSizer() is None:
			self.mySizer = wx.WrapSizer( flags=wx.EXTEND_LAST_ON_EACH_LINE )
			self.SetSizer(self.mySizer)

		self.mySizer.Clear() # Wipe all items out of the sizer.
		self.Scroll(0,0) # Immediately scroll to the top. This fixed a big bug.

		## If our viewobject has NO FONTS inside it (i.e. it's an EmptyView object)
		## then setup a fake FontItem so we can have a dud Fitmap to show.
		if len(viewobject) == 0:
			empty_fitem = fontcontrol.InfoFontItem()
			fm = Fitmap( self, empty_fitem )
			self.fitmaps.append(fm) # I MUST add it to the list so that it can get destroyed when this func runs again next round.
			self.mySizer.Add( fm )
		else:

			## Okay - let's make fonts!
			yld = fpsys.config.numinpage > 20
			for fitem in viewobject:
				## Create a Fitmap out of the FontItem we have at hand.
				fm = Fitmap( self, fitem )
				self.fitmaps.append( fm )
				## July 2016: Add it to the amazing WrapSizer
				## wx.RIGHT specifies we want border on the right!
				self.mySizer.Add( fm, 0, wx.ALIGN_LEFT|wx.ALIGN_BOTTOM|wx.RIGHT, border=10)

				## Added Oct 2009 to let app live on loooong lists.
				if yld: wx.Yield()

		#import pdb; pdb.set_trace()

		# Layout should be called after adding items.
		self.mySizer.Layout()
		self.mySizer.FitInside(self) # Iterative hacking leaves this one standing. self.Fit(), not so much.


	def CreateFitmaps(self, viewobject) :
		"""
		July 16, 2016
		=============
		A forceful approach: Destroy old sizer, make a new one.
		It seems to work. At least the fitmaps draw properly - even on a fresh restart of Fonty.
		FlexGridSizer
		=============
		With this sizer, I get predictable columns of the same size. It forces more work - to
		calculate the max width fitmap and thence the number of columns.
		"""
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

		## Ensure we destroy all old fitmaps -- and I mean it.
		for f in self.fitmaps:
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
			w = []

			yld = fpsys.config.numinpage > 20
			for fitem in viewobject:
				## Create a Fitmap out of the FontItem we have at hand.
				fm = Fitmap( self, fitem )
				self.fitmaps.append( fm )
				#w.append(fm.GetBestSize()[0])
				w.append(fm.bitmap.GetWidth())

				## If I allow this yield, there's a visible flicker as fitmaps are made.
				## I don't understand why. I hope there's no memory leak going on...
				## JULY 2016 - remarked it.
				#if yld: wx.Yield()

			## I am getting an AVERAGE of all the widths
			## This cuts the super-long bitmaps down to
			## a more-or-less size with the others.
			colw = int( sum(w)/max(len(w),1) )
			cols = 1

			panelwidth = self.GetSize()[0] #First run it's 0. After that it works.

			print "panelwidth is:", panelwidth
			if panelwidth < colw:
				pass
				## Having so much trouble with an initial size of 0.
				## Had to resort to this old code to get the panel's fucking size:
				#ret = ps.pub( get_sashes_position )
				#print "I called pub:", ret
				w = fpsys.config.size[0]# Use the last known width of the entire window as an initial size estimate.
				wl = fpsys.config.leftSash
				wr = fpsys.config.rightSash
				panelwidth = w-wl-wr

			## Now, fucking, continue as usual.
			## Can we afford some columns?
			if colw < panelwidth:
				cols = int(panelwidth / colw)

			## Let's also divvy-up the hgap
			hgap = (panelwidth - (cols * colw)) / 2

			## Make the new FlexGridSizer
			fgs = wx.FlexGridSizer( cols=cols, hgap=hgap, vgap=2 )

			## Loop again and plug them into the sizer
			for fm in self.fitmaps:
				## JULY 2016
				## =========
				## If the bitmap is wider than a column, we will resize it
				##
				if fm.bitmap.GetWidth() > colw:
					h = fm.bitmap.GetHeight()
					img = fm.bitmap.ConvertToImage().Resize( (colw, h),(0,0),255,255,255 )
					fm.bitmap = img.ConvertToBitmap()
					fm.SetBestSize((colw,h))

				## Add fm to the sizer
				fgs.Add(fm,0,wx.ALIGN_LEFT|wx.ALIGN_BOTTOM)

				## This yield is ok. No flickering of bitmaps on the panel.
				if yld: wx.Yield()

			self.SetSizer(fgs)
			fgs.FitInside(self)
