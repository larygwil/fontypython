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
		self.dobestsizeonlyonce = True
		#self.initialCalculatedWidth = 0

		
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
		#import pdb; pdb.set_trace()
		# This is actually called BEFORE the __init__ to this object!
		#  What calls this function and when is a dark art. It's related to splitter events (at least)
		#  In my big 30 Sept 2009 fix I just ended-up with this solution -- it's not really something I am savvy about :(


		#if self.dobestsizeonlyonce:
		ps = self.parent.GetSize()
		print "DoGetBestSize runs:",ps.width, ps.height

		if ps.width <=128: #self.parent.doInitialCalcOfScrolledFontViewBestSize:
			w = fpsys.config.size[0]# Use the last known width of the entire window as an initial size estimate.
			wl = fpsys.config.leftSash
			wr = fpsys.config.rightSash
			ps.width = w-wl-wr
			#import pdb; pdb.set_trace()

			print " override width to:", ps.width
			#self.parent.doInitialCalcOfScrolledFontViewBestSize = False
			#self.initialCalculatedWidth = w
		#else:
			#w = self.initialCalculatedWidth
			## This try block is to get-around the odd fact that DoGetBestSize is called prior to __init__
			#try:
				## If this succeeds then we have the width of the parent panel.
			#	w2=self.parent.GetSize()[0]
			#	print "self.parent.GetSize()[0] runs:", w2
				## This is not always sensible, esp. on first run. So, fake it if it's too small.
			#	if w2 < w: w2=w
			#except:
				## __init__ not run yet, we need a value. Use the default.
			#	w2=w
			#	print "!!!!! except runs:", w2
			#w=w2
			#self.initialCalculatedWidth = w
			#self.width=w # This property is helpful

		#best = wx.Size(w,0)
		#self.CacheBestSize(best) #Prevent this def running too often.
		#print "best is:", best.width, best.height
		return ps #best


	def CreateFitmaps(self, viewobject) :
		"""
		Creates fitmaps (which draws them) of each viewobject FontItem down the control.
		
		viewobject: is a sub-list of fitems to display - i.e. after the page number math.

		** See filterAndPageThenCallCreateFitmaps in gui_Middle.py
		"""
		#self.InvalidateBestSize() # Reset the cache (seems uneccessary)
		#self.DoGetBestSize() # Force re-call

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
			self.mySizer.Add( fm,0,0)# pos=(0,0))# 0, wx.GROW ) 
		else:
			i=0
			#halfway=0
			#print dir(viewobject)
			#import pdb; pdb.set_trace()
			#gbs = wx.GridBagSizer(0,0)
			#print L, rows
			#row=col=0
			widths=[]
			for fitem in viewobject:
				#1. Build all the fitmaps - keep widths in a list

				## Create a Fitmap out of the FontItem we have at hand.
				fm = Fitmap( self, (0,0),fitem)# i * h), fitem )
				self.fitmaps.append(fm) 
				widths.append(fm.totwidth)
				print "Fitmap made: %s" % fm.name
				if fpsys.config.numinpage > 20: wx.Yield() #Added Oct 2009 to let app live on loooong lists.

			#2. Get max width
			#3. cmp to parent width etc.

			#print "widths:", widths
			columnwidth = max(widths)

			#s=self.DoGetBestSize()
			#print "s.wdth:",s.width
			#ww = s.width#[0]
			#ww = self.DoGetSize()[0]
			#vs = wx.Size(*self.DoGetSize())
			vs= self.DoGetVirtualSize()
			#
			vs= self.DoGetBestSize()
			print "vs w,h:", vs.width, vs.height
			ww = vs.width

			print "columnwidth, ww:", columnwidth, ww
			cols=1
			if columnwidth < ww:
				#The fitems are smaller than the panel
				#How small? Can we fit two columns, three?
				#import pdb; pdb.set_trace()
				cols = int(ww / columnwidth)
				exactcolwidth = (ww / cols) # for drawing an underline.. maybe

			L = len(self.fitmaps)
			rows = (int(L)/cols)	 + L%cols
			rows = rows if (rows>0) else 1


			#4. make the sizer
			print cols, rows
			gs = wx.GridSizer(cols=cols)#rows=rows, cols=cols, hgap=0, vgap=0)

			#5. reloop and add to sizer
			for fm in self.fitmaps:
				#self.mySizer.Add(fm, 0, wx.ALL,0) #pos=(row,col))#, wx.GROW) 
				gs.Add(fm,0,0)
				#row += col



			self.mySizer.Clear() # Wipe all items out of the sizer.
			self.Scroll(0,0) # Immediately scroll to the top. This fixed a big bug.
		
			self.mySizer.Add(gs)

	
		# Layout should be called after adding items.
		self.mySizer.Layout()
		#self.Fit()

		#self.SetBestSize(vs)#wx.Size(
		# This gets the sizer to resize in harmony with the virtual (scrolling) nature of its parent (self).
		self.mySizer.FitInside(self)	
		#self.mySizer.Fit(self)	
	

