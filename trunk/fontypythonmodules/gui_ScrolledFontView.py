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

from gui_Fitmap import *

## Crappy flag to handle startup sizing issues.
firstRunSizeFlag = False

class ScrolledFontView(wx.lib.scrolledpanel.ScrolledPanel) :
	"""
	This is the main font control, the child of CLASS FontViewPanel.
	Draw a list of fitmaps from a font list object (derived from BasicFontList)
	"""
	def __init__(self, parent):
		wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, -1, style=wx.VSCROLL|wx.SUNKEN_BORDER)
		
		self.fitmaps = []
		self.parent = parent
		
		## At least this one works.
		self.wheelValue = fpsys.config.points
		self.Bind( wx.EVT_MOUSEWHEEL, self.onWheel )
		
		## Make the sizer to hold the fitmaps
		self.mySizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.mySizer)

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

	def CreateFitmaps(self, viewobject) :
		"""
		Creates fitmaps (which draws them) of each viewobject FontItem down the control.
		"""

		# June 2009: Added this test to prevent re-drawing of fonts when the list has not actually changed.
		## Cancelled. There are problems with this. Need more time to fix.
		#if viewobject == self.lastViewList: return
		#self.lastViewList = viewobject
			
		## Setup intial width and subsequent ones
		## Found on the web, thanks to James Geurts' Blog
		sbwidth = wx.SystemSettings.GetMetric(wx.SYS_VSCROLL_X)
		global firstRunSizeFlag
		if not firstRunSizeFlag:
			firstRunSizeFlag = True
			self.width = 1024 # I cannot get a sensible value for 1st run.
		else:
			## Prevent deprecation warning: Not needed in vers 0.4 as we use 2.8 wxPython
			#try:
			self.width = self.DoGetSize()[0] - sbwidth  # 2.8 onwards, I hope.
			#except:
			#	self.width = self.base_DoGetSize()[0] - sbwidth # old 2.6 version of that.

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
				## Create a Fitmap out of the FontItem we have at hand.
				fm = Fitmap( self, (0,0),fitem)# i * h), fitem )
				self.fitmaps.append(fm) 
				self.mySizer.Add(fm, 0, wx.GROW) 

		# Layout should be called after adding items.
		self.mySizer.Layout()

		# This gets the sizer to resize in harmony with the virtual (scrolling) nature of it's parent (self).
		self.mySizer.FitInside(self)	
