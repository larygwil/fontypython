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

## Setup wxPython to access translations : enables the stock buttons.
langid = wx.LANGUAGE_DEFAULT # Picks this up from $LANG
mylocale = wx.Locale( langid )

import fpsys # Global objects

from gui_Fitmap import * #Also brings in 'ps' variable

class ScrolledFontView(wx.lib.scrolledpanel.ScrolledPanel) :
	"""
	This is the main font control, the child of CLASS FontViewPanel.
	Draw a list of fitmaps from a font list object (derived from BasicFontList)
	"""
	def __init__(self, parent):
		## Michael: Don´t need HSCROLL/VSCROLL, SetupScrolling kindly do this
		wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, -1,  style=wx.SUNKEN_BORDER)
		
		self.fitmaps = []
		self.parent = parent
		
		## At least this one works.
		self.wheelValue = fpsys.config.points
		self.Bind( wx.EVT_MOUSEWHEEL, self.onWheel )
		
		## Make the sizer to hold the fitmaps
		self.mySizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.mySizer)

		self.firstrun =True 

		## Michael: Perhaps scroll x and y? If we have a long sample text, the last words couldn't be seen.
		self.SetupScrolling(rate_y=5)#, scroll_x=False)
		
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
		# This is actually called BEFORE the __init__ to this object!
		#  What calls this function and when is a dark art. It's related to splitter events (at least)
		#  In my big 30 Sept 2009 fix I just ended-up with this solution -- it's not really something I am savvy about :(

		w = fpsys.config.size[0]# Use the last known width of the entire window as an initial size estimate.
		wl = fpsys.config.leftSash
		wr = fpsys.config.rightSash
		w = w-wl-wr
	
		## This try block is to get-around the odd fact that DoGetBestSize is called prior to __init__
		try:
			## If this succeeds then we have the width of the parent panel.
			w2=self.parent.GetSize()[0]
			## This is not always sensible, esp. on first run. So, fake it if it's too small.
			if w2 < w: w2=w
		except:
			## __init__ not run yet, we need a value. Use the default.
			w2=w
		w=w2
		self.width=w # This property is used in gui_Fitmap
		best = wx.Size(w,0)
		self.CacheBestSize(best) #Prevent this def running too often.
		return best


	def CreateFitmaps(self, viewobject) :
		"""
		Creates fitmaps (which draws them) of each viewobject FontItem down the control.
		"""
		#self.InvalidateBestSize() # Reset the cache (seems uneccessary)
		self.DoGetBestSize() # Force re-call

		## Ensure we destroy all old fitmaps -- and I mean it.
		for f in self.fitmaps:
		   f.Destroy()  #Ah, nailed ya! You bastard! I fart in your general direction!

		del self.fitmaps
		self.fitmaps = []
		
		## It's NB to notice that the fitems being put into self.fitmaps are
		## the SAME items that are in the viewobject.
		
		self.mySizer.Clear() # Wipe all items out of the sizer.
		self.Scroll(0,0) # Immediately scroll to the top. This fixed a big bug.

		## If our viewobject has NO FONTS inside it (i.e. it's an EmptyView object)
		## then setup a fake FontItem so we can have a dud Fitmap to show.
		if len(viewobject) == 0:
			empty_fitem = fontcontrol.InfoFontItem()
			fm = Fitmap( self, (0, 0), empty_fitem )
			self.fitmaps.append(fm) # I MUST add it to the list so that it can get destroyed when this func runs again next round.
			self.mySizer.Add( fm, 0, wx.GROW ) 
		else:
			for fitem in viewobject:
				#test if not fitem.badfont: continue
				## Create a Fitmap out of the FontItem we have at hand.
				fm = Fitmap( self, (0,0),fitem)# i * h), fitem )
				self.fitmaps.append(fm) 
				self.mySizer.Add(fm, 0, wx.GROW) 
				if fpsys.config.numinpage > 20: wx.Yield() #Added Oct 2009 to let app live on loooong lists.

		# Layout should be called after adding items.
		self.mySizer.Layout()

		# This gets the sizer to resize in harmony with the virtual (scrolling) nature of its parent (self).
		self.mySizer.FitInside(self)	
	

