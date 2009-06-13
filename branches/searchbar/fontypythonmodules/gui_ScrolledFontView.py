import wx
import wx.lib.scrolledpanel

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
		wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, -1, style=wx.VSCROLL)
		
		self.fitmaps = []
		self.parent = parent
		
		## Whitebrush is really whatever the default colour is.
		self.whitebrush = wx.Brush(self.parent.GetBackgroundColour(),wx.SOLID)
				
		## At least this one works.
		self.wheelValue = fpsys.config.points
		self.Bind( wx.EVT_MOUSEWHEEL, self.__onWheel )
		
		## Redraw event
		self.Bind(wx.EVT_PAINT,  self.__onPaint) 
		
		## Tried to get double or right click, or anything to fire.
		## No go.
		## EVT_RIGHT_UP (nope)
		#evt = wx.EVT_COMMAND_LEFT_DCLICK
		#self.Bind( evt, self.__onDoubleClick )
		#def __onDoubleClick( self, evt ):
		#"""
		#Not working. I wanted to show the settings dialog.
		#"""
		#print "huh???"
		#ps.pub( menu_settings )

	def __onPaint(self, event):
		"""
		Dump the bitmap to the screen.
		"""
		dc = wx.PaintDC(self) 
		self.PrepareDC(dc) # Suggested on list. Unsure as to purpose.
		dc.SetBackground(self.whitebrush)
		dc.Clear()		 
		return
		
	def __onWheel( self, evt ):
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
			
			ps.pub( update_font_view ) # starts a chain of calls.
			
			##self.Scroll(xPos, yPos)
			return
		## Keep the wheel event going
		evt.Skip()
		
	def CreateFitmaps(self, viewobject) :
		"""
		Creates fitmaps (whic draws them) of each viewobject FontItem down the control.
		"""
		
		## Setup intial width and subsequent ones
		## Found on the web, thanks to James Geurts' Blog
		sbwidth = wx.SystemSettings.GetMetric(wx.SYS_VSCROLL_X)
		global firstRunSizeFlag
		if not firstRunSizeFlag:
			firstRunSizeFlag = True
			self.width = 1024 # I cannot get a sensible value for 1st run.
		else:
			## Prevent deprecation warning:
			#if wx28:
			try:
				self.width = self.DoGetSize()[0] - sbwidth  # 2.8 onwards, I hope.
			#else:
			except:
				self.width = self.base_DoGetSize()[0] - sbwidth # old 2.6 version of that.

		## Ensure we destroy all old fitmaps -- and I mean it.
		for f in self.fitmaps:
		   f.Destroy()  #Ah, nailed ya! You bastard! I fart in your general direction!

		self.fitmaps = []
		
		####
		## It's NB to notice that the fitems being put into self.fitmaps are
		## the SAME items that are in the viewobject.
		## Hence, when one is flagged as ticked, it's not just the one
		## in here (self.fitmaps), but because they are ONE OBJECT,
		## you can rely on the the fitem within viewobject having a ticked True/False
		## attribute outside of this class.
		
		i = 0
		h = 0
		self.mySizer = wx.BoxSizer(wx.VERTICAL) 
		## If our viewobject has NO FONTS inside it (i.e. it's an EmptyView object)
		## then setup a fake FontItem so we can have a dud Fitmap to show.
		if len(viewobject) == 0:
			empty_fitem = fontcontrol.InfoFontItem("EMPTY")
			fm = Fitmap( self, (0, 0), empty_fitem )
			self.mySizer.Add( fm, 0, wx.GROW )
		else:
			for fitem in viewobject:
				## Create a Fitmap out of the FontItem we have at hand.
				fm = Fitmap( self, (0, i * h), fitem )
				h = fm.height + 10
				self.fitmaps.append(fm) 
				self.mySizer.Add(fm, 0, wx.GROW) 
				i += 1

		self.SetSizer(self.mySizer) 
		
		self.SetAutoLayout(True) 
		self.SetupScrolling(rate_x=5, rate_y=4) 
