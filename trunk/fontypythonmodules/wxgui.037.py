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


"""
Fonty Python : wxgui module

Notice: I am not experienced in gui crafting and I apologize in advance for 
the horrible Flying Spaghetti Monster code you will soon encounter.
I am improving, but this file still gives me cold shivers.

Ramen.
"""

import sys, os, locale
##import pathcontrol
import strings
import fpsys # Global objects
import fontybugs
import fontcontrol
import fpversion

## Now, bring in all those big modules
import wx
import wx.lib.scrolledpanel
import wx.lib.statbmp
import wx.lib.foldpanelbar as fpb
import wxversion
wx28 = wxversion.checkInstalled('2.8')
del wxversion

## Setup wxPython to access translations : enables the stock buttons.
langid = wx.LANGUAGE_DEFAULT # Picks this up from $LANG
mylocale = wx.Locale( langid )

## Fetch my own pubsub stuff
from pubsub import *
ps = CPubsub()

## Fetch the dialogue classes *About, Settings, Help, etc.*
import dialogues

## Crappy flag to handle startup sizing issues.
firstRunSizeFlag = False

class Fitmap(wx.lib.statbmp.GenStaticBitmap):
	"""
	This class is a bitmap of a TTF font - it detects a click and 
	also displays itself with other information below it.
	"""
	def __init__( self, parent, pos, fitem ) :
		self.name = fitem.name
		
		self.fitem = fitem
		self.parent = parent
		self.TICKMAP =  self.parent.parent.TICKMAP # Ugly line
		
		self.bitmapHeight = 0
		self.width = parent.width
		
		## I control font's own height due to mad results.
		## I based this on my preference. Some ttfs had these crazy heights
		## and would shoot off the page. So, I nixed that.
		self.maxHeight = int( fpsys.config.points * 1.55 )
		self.minHeight = 70
		
		self.bitmap = None
		self.prepareBitmap()
		
		sz = (self.bitmap.GetWidth(), self.bitmap.GetHeight())
	   
		## Do mystical voodoo that I can't remember from 2006.
		self.gsb = wx.lib.statbmp.GenStaticBitmap.__init__(self,parent, -1, self.bitmap, pos, sz)
				
		## Very cool event, gives us life!
		self.Bind(wx.EVT_LEFT_UP,self.__onClick) 
		self.Bind(wx.EVT_RIGHT_UP, self.__onRightClick)
		
		## Redraw event
		self.Bind(wx.EVT_PAINT,  self.__onPaint) 
		
		## Very cool,sets the icon for font items.
		self.SetCursor( wx.StockCursor( wx.CURSOR_ARROW ) )
		
		## If this is not a FILE_NOT_FOUND then allow the cursor to change
		## FILE_NOT_FOUND means we have a glyphpaf but no match on the drive.
		## This means the Pog should be purged.
		if self.fitem.badstyle != "FILE_NOT_FOUND":
			if fpsys.state.action == "REMOVE":
				self.SetCursor( wx.StockCursor( wx.CURSOR_PENCIL ) )
			elif fpsys.state.action == "APPEND":
				if not self.fitem.inactive:
					self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
		
	def prepareBitmap( self ):
		"""
		This is where all the drawing code goes. It gets the font rendered
		from the FontItems (via PIL) and then draws a single Fitmap.
		"""
		## Is this a normal FontItem, or an InfoFontItem?
		## InfoFontItem is a fake font item for the purposes
		## of saying "There are no fonts to see here."
		if isinstance( self.fitem, fontcontrol.InfoFontItem ):
			lineCol = (0,0,0)
			block = (255, 255, 255)
			yll = (254,255,180)
			wxMainBitmap = wx.EmptyImage( self.width, self.minHeight ).ConvertToBitmap()
			## White it out
			memDc = wx.MemoryDC()
			memDc.SelectObject( wxMainBitmap )
			memDc.SetBackground( wx.Brush( block, wx.SOLID) )
			memDc.Clear()
			
			self.__fadeEffect( memDc, self.minHeight, self.width, yll )
			
			textTup = self.fitem.errorText()
			
			memDc.SetTextForeground("black") 
			memDc.SetFont\
			(wx.Font(12, family=wx.SWISS, style=wx.NORMAL, weight=wx.BOLD, underline=False) ) 
			memDc.DrawText( textTup[0], 10, 5)
			memDc.SetFont\
			(wx.Font(11, family=wx.SWISS, style=wx.NORMAL, weight=wx.NORMAL, underline=False) ) 
			memDc.DrawText( textTup[1], 10, 24)
			
			## Now a dividing line
			memDc.SetPen( wx.Pen( lineCol, 2 ) ) 
			memDc.SetBrush( wx.TRANSPARENT_BRUSH ) 
			memDc.DrawLine( 0, self.minHeight-1, self.width, self.minHeight-1 )
			
			self.bitmap = wxMainBitmap
			return # Just get out.
			
		## Normal FontItem object
		spacer = 38 # Gap below each font bitmap
		
		## Get a list of pilimages (for each subface) and their heights.
		## If the height returned by PIL is larger than the maxHeight then
		## I force pil to render to maxHeight.
		## REMEMBER: This loop is all FOR ONE FONT.
		##
		## It only supplies pilimages for fonts it could open and
		## render. So this font may indeed have nothing in the pilList[]
		## after this loop.
		pilList=[]
		totheight = 0
		maxwidth = [self.width] # to figure-out the biggest width

		for pilimage,height,pilwidth in self.fitem.generatePilFont( self.maxHeight ):#( self.width, self.maxHeight ):
			pilList.append( [pilimage, height, pilwidth] )
			totheight += height + spacer
			maxwidth.append(pilwidth)
		## Limit the minimum we allow.
		if totheight < self.minHeight:
			totheight = self.minHeight		
		maxwidth = max(maxwidth) # find it.
		
		## BADFONT cases
		##  Badfonts are still available for installation, it's just that I can't
		##  display their glyph or fam/style info (until PIL is patched).
		##
		## NB: FILE_NOT_FOUND is not available for installation!
		
		if self.fitem.badfont:
			## We have a badstyle to help us differentiate these.
			## I will treat PIL_IO_ERROR, PIL_CANNOT_RENDER and PIL_UNICODE_ERROR
			## as the same thing : they all mean we can use the font item, just not
			## actually see the typeface.
			lineCol = (0,0,0)
			if not self.fitem.inactive:
				fadecol = (218,118,0)
				block = (254, 154, 36)
				fcol = "black"
				bcol = fadecol
			else:
				fcol = "gray"
				bcol = "white"
				fadecol = (200,200,200)
				block = (236, 236, 236)
				
			## Must highlight FILE_NOT_FOUND because it's not clickable at all.
			if self.fitem.badstyle == "FILE_NOT_FOUND":
				block = (255,0,0)
				fadecol = (200,0,0)
				fcol = "yellow"
				bcol = fadecol				  
			
			## Jan 18 2008
			## Let's make the segfault fonts obvious
			if self.fitem.badstyle == "PIL_SEGFAULT_ERROR":
				block = (255,255,0)
				fadecol = (200,200,0)
				fcol = "red"
				bcol = fadecol 
				
			wxMainBitmap = wx.EmptyImage( self.width, self.minHeight ).ConvertToBitmap()
			## White it out
			memDc = wx.MemoryDC()
			memDc.SelectObject( wxMainBitmap )
			memDc.SetBackground(wx.Brush( block, wx.SOLID)) 
			memDc.Clear()
			## Fade effect
			self.__fadeEffect( memDc, self.minHeight, self.width, fadecol )

			## Message
			texty = 3
			self.__fatFont(memDc, 12, texty, fcol, bcol, 10, wx.NORMAL, self.fitem.badfontmsg )
			## Path
			texty = 20
			self.__fatFont(memDc, 12, texty, fcol, bcol, 7, wx.NORMAL, self.fitem.glyphpaf_unicode)
			## Filename
			texty = 34
			self.__fatFont(memDc, 10, texty, fcol, bcol, 10, wx.NORMAL, "Name: %s" % self.name)
			
			## Special message - it may already be in a Pog.
			if self.fitem.inactive:
				self.__fatFont\
				(memDc, 10, texty + 15, "black", bcol, 10, wx.NORMAL, self.fitem.msg)

			## Record the calculated height
			self.height = self.minHeight
			
		## It's okay and normal and let's please f*c!#6 draw it already.
		else:
			## Make one big bitmap to house one or more faces (subfaces)
			wxMainBitmap = wx.EmptyImage( maxwidth, totheight ).ConvertToBitmap()
			
			## White it out
			memDc = wx.MemoryDC()
			memDc.SelectObject( wxMainBitmap )
			brush= wx.Brush("WHITE",wx.SOLID)
			memDc.SetBackground(brush)
			memDc.Clear()	
			lineCol = (0,0,0)
			
			y = 0
			i = 0
			for pilimage, glyphHeight, pilwidth in pilList:
				wxfaceimage = wx.EmptyImage( pilwidth, glyphHeight )
				try:
				## Get the data from PIL into wx
					wxfaceimage.SetData( pilimage.convert('RGB').tostring() ) 
					faceBitmap = wxfaceimage.ConvertToBitmap() 
				except:
					## Hey, whaddayaknow, this happened! The font is called 
					## 50SDINGS.ttf and it screws the pooch.
					## What happened was that it returned width = 0
					## which then can't be drawn. So I forced it to 1.
					## Thus, that error is 'fixed', so this is back to being
					## unknown.
					## I am going to create a generic badfont.

					block = (255,255,0)
					fadecol = (200,200,0)
					fcol = "red"
					bcol = fadecol 
						
					wxMainBitmap = wx.EmptyImage( self.width, self.minHeight ).ConvertToBitmap()
					## White it out
					memDc = wx.MemoryDC()
					memDc.SelectObject( wxMainBitmap )
					memDc.SetBackground(wx.Brush( block, wx.SOLID)) 
					memDc.Clear()
					## Fade effect
					self.__fadeEffect( memDc, self.minHeight, self.width, fadecol )

					## Message
					texty = 3
					self.__fatFont(memDc, 12, texty, fcol, bcol, 10, wx.NORMAL, _("This font cannot be drawn") )
					## Path
					texty = 20
					self.__fatFont(memDc, 12, texty, fcol, bcol, 7, wx.NORMAL, self.fitem.glyphpaf_unicode)
					## Filename
					texty = 34
					self.__fatFont(memDc, 10, texty, fcol, bcol, 10, wx.NORMAL, "Name: %s" % self.name)
					
					## Special message - it may already be in a Pog.
					if self.fitem.inactive:
						self.__fatFont\
						(memDc, 10, texty + 15, "black", bcol, 10, wx.NORMAL, self.fitem.msg)

					## Record the calculated height
					self.height = self.minHeight


					#ps.pub( show_error_and_abort,\ # no longer aborting.
					print _("Error creating a wximage of %s") % [self.fitem.glyphpaf_unicode] # list hack, cos I'm still nervous about unicode errors.
				## do this if there was no error:
				else:
					
					## Place it into the main image, down a tad so it looks better.
					facex = 10
					if i > 0: facex = 24 # Shift sub-faces over a little
					memDc.DrawBitmap( faceBitmap, facex, y + 2, True )
				   
					## draw the fading effect under the faceBitmap  
					## only if we are at the end of the faces
					## must be done here so text goes above it.
					if i == self.fitem.numFaces-1:
						self.__fadeEffect( memDc, totheight, maxwidth, (218,218,218) )
					
					## Now draw the text showing the font name/family/style.
					## -- suggested by Chris Mohler.
					## Prep the text to show "font family name (font file name)"
					## Added Style info 3 Dec 2006:
					if self.fitem.inactive: fcol = "gray"
					else: fcol = "black"
					
					## Postion 
					texty = y + glyphHeight + (spacer/8)

					txt = "%s - %s - [%s]" % (self.fitem.family[i], self.fitem.style[i], self.name)
					self.__fatFont(memDc, 16, texty, fcol, "white", 10, wx.NORMAL, txt)
					
					## Special message
					if self.fitem.inactive:
						self.__fatFont\
						(memDc, 16, texty + 14, "black", "white", 10, wx.NORMAL, self.fitem.msg)
						
					## Move TOP down to next BOTTOM (for next sub-face)
					y = y + glyphHeight +  spacer
					
					## Goto next face, if any.
					i += 1			
		
			## Record the calculated height
			self.height = totheight
		
		## Draw the tick/cross if it's not a FILE_NOT_FOUND font (can't be found)
		if self.fitem.badstyle != "FILE_NOT_FOUND":
			if self.fitem.ticked:
				memDc.DrawBitmap(self.TICKMAP, 20, 5, True)
			
		## Now a dividing line
		memDc.SetPen( wx.Pen( lineCol, 2 ) ) 
		memDc.SetBrush( wx.TRANSPARENT_BRUSH ) 
		#memDc.DrawLine( 0, self.height-1, self.width, self.height-1 )
		memDc.DrawLine( 0, self.height-1, maxwidth, self.height-1 )

		self.bitmap = wxMainBitmap



##	def __drawBadFont( self, block, fadecol, fcol, bcol ):
##		"""Factored out on 22 Jan 2008 because badfonts suddenly happen in more than one place. """


	def __fadeEffect( self, memDc, liney, width, col ):
		"""
		Baptiste's idea!
		 "Now a dividing gradient, you can say "wow" ;-)"
		 Donn says, "..Wow!" :-D   
		
		It aims towards white from col (but might not get there)
		"""
		memDc.SetBrush ( wx.TRANSPARENT_BRUSH ) 
		sr,sg,sb = col
		#print "TO:", col
		for q in range(0, 25):
			r = min(255,int(1.5*q+sr))
			g = min(255,int(1.5*q+sg))
			b = min(255,int(1.5*q+sb))
			#print (r,g,b)
			memDc.SetPen( wx.Pen( wx.Colour( r, g ,b ), 1 ) ) 
			memDc.DrawLine( 0, liney-q, width, liney-q )

	def __fatFont(self, dc, x, y, fcol, bcol, points, weight, txt):
		"""
		Draw a string with a backdrop highlight. Makes it "fat".
		I suppose I should draw one string, then try blitting it around 
		rather than DrawTexting it. Later ...
		"""
		dc.SetFont\
		(wx.Font(points, family=wx.SWISS, style=wx.NORMAL, weight=weight, underline=False) ) 
		
		## Draw the back-drop text
		dc.SetTextForeground(bcol)
		dc.DrawText(txt, x-1, y-1)
		dc.DrawText(txt, x-1, y+1)
		dc.DrawText(txt, x+1, y-1)
		dc.DrawText(txt, x+1, y+1)
		
		dc.DrawText(txt, x, y-1)
		dc.DrawText(txt, x-1, y)
		dc.DrawText(txt, x+1, y)
		dc.DrawText(txt, x, y+1)
		## Final text
		dc.SetTextForeground(fcol)
		dc.DrawText(txt, x, y)

		
	def __onPaint(self, event):
		"""
		Dump the bitmap to the screen.
		"""
		if self.bitmap:
			## Create a buffered paint DC.  It will create the real
			## wx.PaintDC and then blit the bitmap to it when dc is
			## deleted.  Since we don't need to draw anything else
			## here that's all there is to it.
			dc = wx.BufferedPaintDC(self, self.bitmap, wx.BUFFER_VIRTUAL_AREA)


	def __onClick(self, event) :
		if fpsys.state.cantick and not self.fitem.inactive:
			self.fitem.ticked = not(self.fitem.ticked)
			self.prepareBitmap() # This only redraws a single font item.
			self.Refresh()  #forces a redraw.
			 
			## Inc or dec a counter depending on the tickedness of this item
			if self.fitem.ticked: fpsys.state.numticks += 1
			if not self.fitem.ticked: fpsys.state.numticks -= 1
			ps.pub(toggle_main_button)
		event.Skip()

	def __onRightClick(self, event):
		fitmap =  event.GetEventObject()
		win = dialogues.PopupInfo(self, -1, '', fitmap)
		win.CentreOnScreen()
		win.Show()

#   class PopupInfo(wx.Frame):
#	   """Shows Infos about Font/Pog"""
#	   def __init__(self, parent, id, title, fmap):
#		   wx.Frame.__init__(self, parent, id, title)
#		   self.box = wx.BoxSizer(wx.VERTICAL)
#		   self.list = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE|wx.TE_WORDWRAP)
#		   self.box.Add(self.list, proportion=1, flag=wx.EXPAND)
#		   font = fmap.fitem
#		   info = fontsearch.getInfo(font)
#		   self.SetTitle(info['Name Records']['Full Name'])
#		   text = str(info)
#		   self.list.AppendText(text)
#		   self.butClose = wx.Button(self, id = wx.ID_OK)
#		   self.butClose.Bind(wx.EVT_BUTTON, lambda event : self.Close())
#		   self.box.Add(self.butClose, flag=wx.FIXED_MINSIZE|wx.ALIGN_CENTER)
#		   self.box.Layout()
#		   self.SetSizer(self.box)

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
		
##		## Tried to get double or right click, or anything to fire.
##		## No go.
##		## EVT_RIGHT_UP (nope)
##		evt = wx.EVT_COMMAND_LEFT_DCLICK
##		self.Bind( evt, self.__onDoubleClick )
##	def __onDoubleClick( self, evt ):
##		"""
##		Not working. I wanted to show the settings dialog.
##		"""
##		print "huh???"
##		ps.pub( menu_settings )

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
		#TO DO : Jan 14 2008 - A user has reported an error on this command. Could it be 2.8 specific? 
		# I had used DoGetSize. The docs for 2.6 refer to base_DoGetSize. I have used that. On 2.8
		# I now get a deprecation warning...
			if wx28:
				self.width = self.DoGetSize()[0] - sbwidth
			else:
				self.width = self.base_DoGetSize()[0] - sbwidth

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

class FontViewPanel(wx.Panel):
	"""
	Standalone visual control to select TTF fonts.
	The Panel that holds the ScrolledFontView control.
	It holds the controls above it and the buttons below it.
	"""
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, id = -1)
		
		self.pageindex = 1 # I start here
		self.total_number_of_pages = 0
		
		self.filter = ""
		
		self.TICKMAP = None
		self.TICK = wx.Bitmap(fpsys.mythingsdir + "tick.png", type=wx.BITMAP_TYPE_PNG)
		self.CROSS = wx.Bitmap(fpsys.mythingsdir + "cross.png", type=wx.BITMAP_TYPE_PNG)
		
		## Main Label on top
		sizerMainLabel = wx.BoxSizer(wx.HORIZONTAL) 
		self.textMainInfo = wx.StaticText(self, -1, " ") 
		self.textMainInfo.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD))
		sizerMainLabel.Add(self.textMainInfo,1,wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT) 
		
		## Page choice and Filter controls
		sizerOtherControls = wx.BoxSizer(wx.HORIZONTAL)

		## The clear filter button: added 10 Jan 2008
		bmp = wx.Bitmap(fpsys.mythingsdir + "clear.png", type=wx.BITMAP_TYPE_PNG)
		self.clearButton = wx.BitmapButton(self, -1, bmp, style = wx.NO_BORDER)
		self.clearButton.SetToolTipString( _("Clear filter") )
		self.clearButton.Bind( wx.EVT_BUTTON, self.OnClearClick )

		self.textFilter = wx.StaticText(self, -1, _("Filter:"))
		self.inputFilter = wx.TextCtrl(self, -1, "")
		self.inputFilter.Bind(wx.EVT_CHAR, self.__evtChar) #catch the enter char
		self.choicePage = wx.Choice(self, -1, choices = ["busy"]) 
		self.choicePage.Bind(wx.EVT_CHOICE, self.__onPagechoiceClick) #Bind choice event
		
		## put them into the sizer
		sizerOtherControls.Add(self.textFilter, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
		sizerOtherControls.Add( self.clearButton, 0, wx.ALIGN_LEFT| wx.ALIGN_CENTER_VERTICAL ) # Clear button
		sizerOtherControls.Add(self.inputFilter, 1, wx.ALIGN_LEFT | wx.EXPAND)
		sizerOtherControls.Add(( 4,-1), 0, wx.EXPAND)
		sizerOtherControls.Add(self.choicePage, 0 ,wx.EXPAND | wx.ALIGN_RIGHT)  #Added it to the sizer
		
		## The FONT panel:
		self.scrolledFontView = ScrolledFontView(self) 
		
		buttonsSizer = wx.BoxSizer(wx.HORIZONTAL) 
		self.buttPrev = wx.Button(self, wx.ID_BACKWARD) # Also not in Afrikaans.

		self.buttMain = wx.Button(self, label=" ", id = 3) 
		## This stock button has not been translated into Afrikaans yet. (Dec 2007)
		## I can't tell you how this fkuced me around!
		self.buttNext = wx.Button(self, wx.ID_FORWARD)  
		self.buttPrev.Enable(False)  #Starts out disabled
		
		buttonsSizer.Add(self.buttPrev,0,wx.EXPAND) 
		buttonsSizer.Add((10,1) ,0,wx.EXPAND) 
		buttonsSizer.Add(self.buttMain,1,wx.EXPAND) 
		buttonsSizer.Add((10,1) ,0,wx.EXPAND) 
		buttonsSizer.Add(self.buttNext,0,wx.EXPAND) 

		## Now the sizer to hold all the fontview controls
		self.sizerFontView = wx.BoxSizer( wx.VERTICAL )
		## The Main label
		self.sizerFontView.Add(sizerMainLabel, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, border = 5 )
		## The font view
		self.sizerFontView.Add(self.scrolledFontView, 1, wx.EXPAND )
		## Choice and Filter
		self.sizerFontView.Add(sizerOtherControls, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, border = 3)
		## The buttons   
		self.sizerFontView.Add(buttonsSizer,0,wx.EXPAND)	
		
		self.SetSizer(self.sizerFontView)
		
		self.buttPrev.Bind(wx.EVT_LEFT_UP,self.__navClick) 
		self.buttNext.Bind(wx.EVT_LEFT_UP,self.__navClick) 
		self.buttMain.Bind(wx.EVT_LEFT_UP,self.__onMainClick) 
	
		ps.sub(toggle_main_button, self.ToggleMainButton) 

	def OnClearClick( self, event ):
		self.inputFilter.Clear()
		self.filter = ""
		## Now command a change of the view.
		## First, return user to page 1:
		self.pageindex = 1
		self.__filterAndPageThenCallCreateFitmaps()
		self.buttMain.SetFocus()  #a GTK bug demands this move. Restore the ESC key func.
			
	## Catch the ENTER key in the filter text input control
	def __evtChar(self, e):
		if e.GetKeyCode() == 13:
			## Time to filter and redraw my list
			self.filter = self.inputFilter.GetValue()
			## Now command a change of the view.
			## First, return user to page 1:
			self.pageindex = 1
			self.__filterAndPageThenCallCreateFitmaps()
			self.buttMain.SetFocus()  #a GTK bug demands this move. Restore the ESC key func.
		if e.GetKeyCode() == 27:
			self.buttMain.SetFocus()
		e.Skip() #vital to keep the control alive!
		
	def __filterAndPageThenCallCreateFitmaps(self):
		"""
		Figure out what list of fonts to draw, divide them into pages,
		then go make Fitmaps out of them.
		"""
##		print "filter"
##		print "len viewobject:", len(fpsys.state.viewobject)
##		print "self.pageindex:", self.pageindex
		
		self.total_number_of_pages = 1 # A default
		
		## Is there anything there to view?
		if len(fpsys.state.viewobject) > 0:
			## STEP 1 : Handle the Filter:
			filteredList = fpsys.state.viewobject
			
			#print "FILTER SAYS:",self.filter
			
			if self.filter is not "":
				## Okay, we have some kind of filter.
				## This idea was suggested by user Chris Mohler.
				filteredList = []
				import re
				test = re.compile(self.filter, re.IGNORECASE)
				for fi in fpsys.state.viewobject:
					## Make sure we don't try fetch info from a bad font.
					if not fi.badfont:
						if test.search( fi.name + fi.family[0] + fi.style[0] ):
							filteredList.append( fi )
					else:
						if test.search( fi.name ):
							filteredList.append( fi )
				
			## STEP 2 : Figure out how many pages we have to display
			current_page = self.pageindex - 1
			num_in_one_page = fpsys.config.numinpage
			total_num_fonts = len(filteredList)
			#print "total_num_fonts=", total_num_fonts
			gross = total_num_fonts / float(num_in_one_page)
			
			if gross <= 1:
				## There are less than num_in_one_page fonts to be viewed at all.
				self.total_number_of_pages = 1
			else:
				## Okay, we have at least 1 page, perhaps more.
				whole_number_of_pages = int(gross)
				remainder = whole_number_of_pages % num_in_one_page
				if remainder > 0: whole_number_of_pages += 1
				self.total_number_of_pages = whole_number_of_pages

			start = current_page * num_in_one_page #leaf thru the pages to the one we are on now.
			fin = start + num_in_one_page
			if fin > len(filteredList): fin = len(filteredList) #Make sure we don't overshoot.
			
			## Extract a single page of fonts to display
			sublist = filteredList[start:fin] 
			
			## Empty the choice control.
			self.choicePage.Clear() 
			## Now refill it
			[self.choicePage.Append(str(n)) for n in range(1, self.total_number_of_pages +1)] 
			self.choicePage.SetSelection(self.pageindex-1)
		## The viewobject is empty anyway.
		else: 
			sublist = []

		if self.total_number_of_pages == 1: 
			self.choicePage.Enable(False) #I tried to hide/show the choice, but it would not redraw properly.
		else:
			self.choicePage.Enable(True)
			
		self.scrolledFontView.CreateFitmaps( sublist ) # Tell my child to draw the fonts
		self.__buttonState()
		
	## Main BUTTON click -- the main "do something" button.
	def __onMainClick(self, e):
		xPos, yPos = self.scrolledFontView.GetViewStart() #Saved by Robin Dunn, once again ! ! !
		wx.BeginBusyCursor()
		ps.pub(main_button_click)
		wx.EndBusyCursor()
		self.scrolledFontView.Scroll(xPos, yPos)
		#e.Skip()# It sure doesn't help restore ESC key...
		
	def __onPagechoiceClick(self,event) :
		wx.BeginBusyCursor()
		if self.pageindex != int(event.GetString() ) : #Only redraw if actually onto another page.
			self.pageindex =  int(event.GetString() ) 
			self.__filterAndPageThenCallCreateFitmaps() 
		wx.EndBusyCursor()
		
	def __navClick(self,event) :
		wx.BeginBusyCursor()
		if event.GetId()  == wx.ID_FORWARD: 
			self.pageindex += 1
		else: #wx.ID_BACKWARD
			self.pageindex -= 1
		if self.pageindex > self.total_number_of_pages:
			self.pageindex = self.total_number_of_pages
		if self.pageindex == 0:
			self.pageindex = 1
		 
		self.buttMain.SetFocus()  #a GTK bug demands this move.
		self.__filterAndPageThenCallCreateFitmaps() 
		wx.EndBusyCursor()
		
	def __buttonState(self) :
		"""
		Enabled state of PREV/NEXT buttons
		"""
		n = True
		p = True
		if self.pageindex == self.total_number_of_pages: 
			n = False
		if self.pageindex == 1:
			p = False
		self.buttNext.Enable(n)		 
		self.buttPrev.Enable(p) 
		
	def ToggleMainButton(self, args = None):
		if fpsys.state.action == "NOTHING_TO_DO":
			self.buttMain.Enable( False )
			return
		if fpsys.state.numticks > 0: self.buttMain.Enable(True)
		else: self.buttMain.Enable(False)
			
	def MainFontViewUpdate(self):
		"""
		Vital routine - the heart if the app. 
		
		This decides what to do based on what has been selected.
		It draws the controls and the fonts as appropriate. 
		It also sets flags in fpsys.state
		"""
		
		## Get shorter vars to use.
		V = fpsys.state.viewobject
		T = fpsys.state.targetobject
			
		Vpatt = fpsys.state.viewpattern # View Pattern
		Tpatt = fpsys.state.targetpattern # Target pattern
	
		Patt = Vpatt + Tpatt # Patt = Pattern
		
##		print "Vpatt", Vpatt
##		print "Tpatt", Tpatt

		lab = ""
		status = ""
		

		## E == Empty View - no fonts in chosen Source.
		## N == Empty Target - no fonts.
		## P is Pog
		## F is Folder
		
		if Vpatt == "E": #NOTE : TESTING VPATT, not PATT - ergo: this covers E, EN, EP
			## Empty "E" - when the chosen Folder or Pog has NO FONTS IN IT.
			if Tpatt == "P":
				lab = _("Your active Target Pog is:%s") % T.name
				status = _("Please choose a Source.")
			else:
				lab = _("There are no fonts in here.")
				status = _("Please choose a Pog or a Font folder on the left.")
			btext = _("Nothing to do")
			fpsys.state.cantick = False
			fpsys.state.action = "NOTHING_TO_DO" # We will test this in mainframe::OnMainClick
			
		elif Patt == "FN":
			#View a Folder, no target
			lab = _("Viewing Folder:%s") % V.label()
			fpsys.state.cantick = False
			btext = _("Nothing to do")
			fpsys.state.action = "NOTHING_TO_DO" # We will test this in mainframe::OnMainClick
			status = _("Viewing a folder.")
		elif Patt == "PN": #A single Pog in the VIEW
			#View a pog, no target
			if V.isInstalled():
				## Cannot remove fonts from an installed pog
				lab = _("Viewing (installed) Pog: %s") % V.name
				btext = _("Nothing to do")
				fpsys.state.action = "NOTHING_TO_DO"
				fpsys.state.cantick = False
				status = _("You cannot change an installed Pog.")
			else:
				lab = _("Viewing (editable) Pog: %s") % V.name
				fpsys.state.cantick = True
				btext = _("Remove fonts from %s") % V.name
				self.TICKMAP = self.CROSS
				fpsys.state.action = "REMOVE" # We will test this in mainframe::OnMainClick
				status = _("You can remove fonts from the selected Target Pog.")
		elif Patt == "FP":
			#Folder to Pog
			if T.isInstalled():
				## We cannot put stuff into an installed pog
				lab = _("Viewing Folder:%s") % V.label()
				btext = _("Nothing to do")
				fpsys.state.action = "NOTHING_TO_DO"
				fpsys.state.cantick = False
				status = _("You cannot change an installed Pog.")
			else:
				lab = _("Append From: %(source)s To:%(target)s") % { "source":V.label(), "target":T.name }
				btext = _("Put fonts into %s") % T.name
				self.TICKMAP = self.TICK
				fpsys.state.cantick = True
				fpsys.state.action = "APPEND" # We will test this in mainframe::OnMainClick
				status = _("You can append fonts to your target Pog.")
		elif Patt == "PP":
			#Pog to Pog
			if T.isInstalled():
				## We cannot put fonts into an installed pog
				lab = _("Viewing Pog:%(source)s, but Pog:%(target)s is installed.") % {"source":V.name, "target":T.name}
				btext = _("Nothing to do")
				fpsys.state.action = "NOTHING_TO_DO"
				fpsys.state.cantick = False
				status = _("You cannot change an installed Pog.")
			else: #Not installed.
				if fpsys.state.samepogs: #Are the two pogs the same?
					## The validate routines determined the samepogs value.
					lab = _("These two are the same Pog.")
					fpsys.state.cantick = True
					btext = _("Nothing to do")
					fpsys.state.action = "NOTHING_TO_DO"
					status = _("Your Source and Target are the same Pog.")
				else: # Normal pog to pog
					lab = _("Append from Pog:%(source)s into Pog:%(target)s") % {"source":V.name, "target":T.name}
					btext = _("Put fonts into %s") % T.name
					self.TICKMAP = self.TICK
					fpsys.state.cantick = True	 
					fpsys.state.action = "APPEND" # We will test this in mainframe::OnMainClick
					status = _("You can append fonts to your target Pog.")
		else:
			print "MOJO ERROR: %s and trouble" % Patt
			raise SystemExit
			
		self.buttMain.SetLabel(btext)
		self.textMainInfo.SetLabel(lab)
		self.textMainInfo.Show()
		if status is not "":
			ps.pub(print_to_status_bar, status)
		self.ToggleMainButton()
		
		fpsys.markInactive()
		self.__filterAndPageThenCallCreateFitmaps()

	def ResetToPageOne(self):
		self.pageindex = 1 # I start here
		
class TargetPogChooser(wx.Panel):
	"""
	Far right-hand side control. Chooses target pogs. Houses control buttons.
	"""
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, id = -1)	
		
		self.icon = wx.StaticBitmap\
		(self, -1, wx.Bitmap(fpsys.mythingsdir + 'icon_target_16x16.png', wx.BITMAP_TYPE_PNG))
		self.textInfo = wx.StaticText(self, -1, _("Target Pogs"), style = wx.ALIGN_LEFT)
		self.textInfo.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD))
		
		s = None
		if fpsys.state.targetpattern == "P":
			s = fpsys.state.targetobject.name
			
		## The actual list control
		self.pogTargetlist = PogChooser(self, select = s) 
		
		## Subscriptions:
		ps.sub(pog_selected, self.OnPogTargetClick)
		ps.sub(toggle_buttons, self.ToggleButtons)
		ps.sub(select_no_target_pog, self.SelectNoTargetPog)
		
		## The "no pog" button
		self.idnone = wx.NewId()
		self.buttNoPog = wx.Button(self, label = _("Clear selection"), id = self.idnone)
		self.buttNoPog.SetToolTipString(_("Deselects any chosen pogs."))
		## The buttons under the pog list
		## Giving them all id numbers so my single handler can tell them apart.
		self.idnew = wx.NewId()
		self.idinstall = wx.NewId()
		self.iduninstall = wx.NewId()
		self.iddelete = wx.NewId()
		self.idpurge = wx.NewId()
		
		self.buttNew = wx.Button(self, label = _("New Pog"), id = self.idnew ) 
		self.buttNew.SetToolTipString(_("Creates a new, empty Pog"))
		self.buttInstall = wx.Button(self, label = _("Install Pog(s)"), id = self.idinstall ) 
		self.buttInstall.SetToolTipString(_("Installs all selected Pogs.\nUse SHIFT/CTRL+Click on the list above."))
		self.buttUninstall = wx.Button(self, label = _("Uninstall Pog(s)"), id = self.iduninstall ) 
		self.buttUninstall.SetToolTipString(_("Uninstalls all selected Pogs.\nUse SHIFT/CTRL+Click on the list above."))
		self.buttDelete = wx.Button(self, label = _("Delete Pog") , id = self.iddelete) 
		self.buttDelete.SetToolTipString(_("Deletes the last selected Pog"))
		self.buttPurge = wx.Button(self, label = _("Purge Pog"), id = self.idpurge) 
		self.buttPurge.SetToolTipString(_("Purges the last selected Pog"))
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)		 
		self.iconandtext = wx.BoxSizer(wx.HORIZONTAL)
		self.iconandtext.Add(self.icon, 0, wx.TOP | wx.BOTTOM, border = 4)
		self.iconandtext.Add(self.textInfo, 1, wx.EXPAND | wx.TOP | wx.BOTTOM | wx.LEFT, border = 4)
		self.sizer.Add(self.iconandtext, 0, wx.EXPAND)
		self.sizer.Add(self.buttNoPog, 0, wx.EXPAND)	  
		self.sizer.Add(self.pogTargetlist, 1, wx.EXPAND)
		self.sizer.Add(self.buttInstall, 0, wx.EXPAND) 
		self.sizer.Add(self.buttUninstall, 0, wx.EXPAND) 
		self.sizer.Add(self.buttNew, 0, wx.EXPAND) 
		self.sizer.Add(self.buttDelete, 0, wx.EXPAND) 
		self.sizer.Add(self.buttPurge, 0, wx.EXPAND)
		self.SetSizer(self.sizer)
		
		## Bind the events:
		self.buttNoPog.Bind(wx.EVT_BUTTON, self.__multiClick)
		self.buttNew.Bind(wx.EVT_BUTTON, self.__multiClick)
		self.buttInstall.Bind(wx.EVT_BUTTON, self.__multiClick)
		self.buttUninstall.Bind(wx.EVT_BUTTON, self.__multiClick)
		self.buttDelete.Bind(wx.EVT_BUTTON, self.__multiClick)
		self.buttPurge.Bind(wx.EVT_BUTTON, self.__multiClick)
		
		self.__toggleButtons()
		
	def newPogForAll(self, e, new_pogname = ""):
	#  makes __multiClick public
		self.__multiClick(e, new_pogname)

	## Catch all the button clicks on the control.
	def __multiClick(self, e, pogname = ""):
		## NEW
		if e.GetId() == self.idnew: 
			## New Pog button pressed
			dlg = wx.TextEntryDialog(
					self, _("Enter a name for the new pog"),
					_("New Pog"), _("Fonty Python"))
			dlg.SetValue(pogname)
			if dlg.ShowModal() == wx.ID_OK:
				## Is it unique?
				nam = dlg.GetValue()
				if fpsys.isPog(nam):
					## Nope, it's there already
					ps.pub(show_message, _("%s already exists.") % nam)
				else:
					## We have a winner.
					## Make a pog object and then write it,
					ipog = fontcontrol.Pog(nam)
					try:
						ipog.write()
					except fontybugs.PogWriteError, e:
						ps.pub(show_error_and_abort, unicode( e ))
					del ipog
					## Now put it into the list
					self.pogTargetlist.AddItem(nam)
					ps.pub(add_item_to_notebook, nam)
					ps.pub(update_font_view)
			dlg.Destroy()
			return
			
		## DELETE
		if e.GetId() == self.iddelete:
			## Selected Pog to be deleted
			pogname = fpsys.state.targetobject.name
			print _("%s is to be deleted") % pogname
			dlg = wx.MessageDialog(self, _("Remove %s, are you sure?") % pogname,
								   _("Are you sure?"),
								   wx.YES_NO | wx.ICON_INFORMATION
								  )
			if dlg.ShowModal() == wx.ID_YES:
				## Now kill the file on disk:
				try:
					fpsys.state.targetobject.delete()
				except fontybugs.PogCannotDelete, e:
					ps.pub(show_error, unicode( e ))
					return
				## This object was also our target object (it was selected - duh!)
				## Remove from the list:
				self.pogTargetlist.RemoveItem(pogname)
				ps.pub(remove_item_from_notebook, pogname)				
				## So, we must now select no pog.
				self.__selectNoPog()

				## What if it was ALSO our view object?
				if fpsys.state.viewobject.label() == pogname:
					## It was! We must declare it Empty.
					fpsys.SetViewPogToEmpty()
				## Now re-draw things
				ps.pub(update_font_view)
			dlg.Destroy()
			return 
		
		## NO POG pressed
		if e.GetId() == self.idnone:
			## Select No Pog button pressed
			if fpsys.state.targetobject is None: return #Already done.
			self.__selectNoPog()
			ps.pub(update_font_view)
			return #No need to tell mainframe about this.
			
		## PURGE
		if e.GetId() == self.idpurge:
			if not fpsys.state.targetobject.isInstalled():
				pogname = fpsys.state.targetobject.name
				dlg = wx.MessageDialog(self,_("Do you want to purge %s?\n\nPurging means all the fonts in the pog\nthat are not pointing to actual files\nwill be removed from this pog.") % pogname, _("Purge font?"), wx.YES_NO | wx.ICON_INFORMATION )
				if dlg.ShowModal() == wx.ID_YES:
					## pog.purge() Raises
					##		  PogEmpty
					##		  PogInstalled
					try:
						fpsys.state.targetobject.purge()
					except(fontybugs.PogEmpty, fontybugs.PogInstalled),e:
						ps.pub(show_error, unicode( e ))
						ps.pub(print_to_status_bar, _("%s has not been purged.") % pogname)
						return 

					## The problem here is that the targetobject has been
					## purged, but all those same bad fontitems are *still*
					## in the viewobject.
					## So, hack the list:
					fpsys.state.viewobject.clear()
					for fi in fpsys.state.targetobject:
						fpsys.state.viewobject.append(fi)
					## Update GUI
					ps.pub(print_to_status_bar, _("%s has been purged.") % pogname)

					ps.pub(update_font_view)
				
		## The next two get passed on to mainframe.
		tl = self.pogTargetlist
		if e.GetId() == self.idinstall:
			## Install button
		## install or uninstall all selected pogs
			wx.BeginBusyCursor()
			for p in [ tl.GetItemText(i) for i in range(tl.GetItemCount()) if tl.IsSelected(i)]:
				fpsys.instantiateTargetPog(p)
				ps.pub(install_pog)
			wx.EndBusyCursor()

		if e.GetId() == self.iduninstall:
			wx.BeginBusyCursor()
			for p in [ tl.GetItemText(i) for i in range(tl.GetItemCount()) if tl.IsSelected(i)]:
				fpsys.instantiateTargetPog(p)
				ps.pub(uninstall_pog)
			wx.EndBusyCursor()
		
	def OnPogTargetClick(self, args):
		"""
		This is called via pubsub. There are TWO pog_selected topics
		in there so they BOTH get called. Thus, this function AND
		the OnViewPogClick one in the NoteBook get called.
		So, we must reject a 'click' coming from the wrong control.
		
		args[0] pogname
		args[1] id of the originating instance
		args[2] is pognochange
		"""
		## We must be sure it came from pogTargetlist ...
		if args[1] != self.pogTargetlist.GetId(): return
		
		## Okay, the click came from the Target list control.
		
		## Made it so a second click on a target pog will unselect it.
		if args[2]: #pognochange = True, so let's deselect this pog
			self.__selectNoPog()
			ps.pub(update_font_view)
			return
		try:
			fpsys.instantiateTargetPog(args[0])
		except fontybugs.PogInvalid, e:
			ps.pub(show_error_and_abort, unicode( e ))
			return
##		## I removed this Dec 2007 :: Not sure why it was there ...
##		if fpsys.state.samepogs: #forbid same pogs selection
##			ps.pub(print_to_status_bar, "Pog already selected in the View")
##			ps.pub(select_no_view_pog)

		ps.pub(update_font_view)
		self.__toggleButtons()
		
	def ToggleButtons(self, args):
		"""
		Shadow the __toggleButtons func. 
		A bit of a stuff around. __toggleButtons can't be 
		reached due to the underscores...
		"""
		self.__toggleButtons()
	def __toggleButtons(self):
		## If this is a no target pog situation, hide 'em all.
		if fpsys.state.targetobject is None:
			self.buttDelete.Enable(False)
			self.buttDelete.Enable(False)
			self.buttInstall.Enable(False)
			self.buttUninstall.Enable(False)
			self.buttPurge.Enable(False)
			return 
		installed = fpsys.state.targetobject.isInstalled()
		self.buttDelete.Enable(not(installed)) # DELETE button is inverse of installed status
		self.buttInstall.Enable(not(installed)) # INSTALL button is inverse 
		self.buttUninstall.Enable(installed) # UNINSTALL = True if pog is installed.
		self.buttPurge.Enable(not(installed))
		
	def SelectNoTargetPog(self, args):
		## Shadow: this is dumb. I'm sorry. 
		self.__selectNoPog()
		
	def __selectNoPog(self):
		"""
		Public method : for access from mainframe
		"""
		wx.BeginBusyCursor()
		## Go figure out what item gets what image
		self.pogTargetlist.SortOutTheDamnImages( pognochange = True )
		self.pogTargetlist.ClearSelection() #Select nothing.

		fpsys.SetTargetPogToNone()  # Tell fpsys that we have no pog target selected	
		self.__toggleButtons() # Disable the buttons on the bottom right.		
		wx.EndBusyCursor()
		return

class PogChooser(wx.ListCtrl) :
	"""
	Basic list control for pogs - instanced by TargetPogChooser and NoteBook
	Parent: TargetPogChooser
	
	This single class (being used twice) causes terrible conceptual hardships
	and forces all kinds of twisty tests. I'm sorry for this, we need a better
	solution.
	"""
	## CLASS LEVEL variables - special things these.
	__poglistCopy = {} # To help in sorting.
	__TARGET = None
	__VIEW = None
	
	def __init__(self, parent, select = None) :
		self.indexselected = 0
		self.lastindexselected = -1
		self.parent = parent
		
		## Use Class-level attributes to record the history of 
		## the instantiation of this class. These vars do not
		## belong to the instances, but to this one class.
		## We keep refs to the two parents of this class.
		if isinstance( self.parent, TargetPogChooser ):
			PogChooser.__TARGET = self.parent
		else:
			PogChooser.__VIEW = self
		  
		il = wx.ImageList(16,16,True) 
		png = wx.Bitmap(fpsys.mythingsdir + "/pog16x16.png",wx.BITMAP_TYPE_PNG) 
		il.Add(png) 
		png = wx.Bitmap(fpsys.mythingsdir + "/pog16x16.installed.png",wx.BITMAP_TYPE_PNG) 
		il.Add(png)
		## Dec 2007 : target icon
		png = wx.Bitmap( fpsys.mythingsdir + "/pog16x16.target.png", wx.BITMAP_TYPE_PNG )
		il.Add( png )
		
		wx.ListCtrl.__init__\
		(self,parent,-1, style=wx.LC_LIST | wx.LC_AUTOARRANGE | wx.LC_SORT_ASCENDING) 
		
		self.AssignImageList(il, wx.IMAGE_LIST_SMALL) 

		self.__PC = fpsys.iPC # reuse the global pathcontrol object
		
		self.__fillPogList() 
		
		## Highlight the pog selected (the last one, or the cli chosen one)
		if select:
			i = self.FindItem(-1, select)
			self.indexselected = i # Set this to help initial icon settings.
			self.Select(i, True)
		else:
			self.Select(0, False)
			self.indexselected = -1


		self.ClearBackground() 
		self.items = None
		
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.__onSelect) 
		
		## This one is a double click event
##		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.__onActivate )
		
		#self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
		
		## This subscribe line here will register TWICE since this PogChooser object is instanced
		## twice by the app...
		ps.sub(change_pog_icon, self.ChangeIcon)
		
	def __Sorter(self, key1, key2):
		"""
		Fetch the strings from our CLASS LEVEL copy of the pognames
		so that we can compare them via locale.
		"""
		s1,s2 = PogChooser.__poglistCopy[key1], PogChooser.__poglistCopy[key2]
		## Since the gui is unicode, I *think* I don't have to worry about errors here.
		return locale.strcoll( s1, s2 )
		
	def __onSelect(self, e):
		wx.BeginBusyCursor()
		self.indexselected = e.m_itemIndex
		pognochange = False
		if self.indexselected == self.lastindexselected:
			## We have clicked on the same Pog as last time - ergo do nothing.
			pognochange = True
		self.lastindexselected = self.indexselected # Record this for next time around

		textpogname = self.GetItemText(self.indexselected) # Gets UNICODE !!!
		## CALLS BOTH CLICK ROUTINES: onViewPogClick, OnTargetPogClick
		## Each one decides where this comes from and rejects the other.
		ps.pub(pog_selected, textpogname, self.GetId(), pognochange)
		
		self.SortOutTheDamnImages( pognochange )
				
		wx.EndBusyCursor()
		
	def SortOutTheDamnImages( self, pognochange ):
		"""
		Dec 2007 : This took me an entire day to figure out. Man...
		Determines the images of the list items.
		Is called from TargetPogChooser as well (when clear button is clicked)
		"""
		
		if pognochange is ():
			pognochange = True
			
		c = self.GetItemCount()
		sel = self.indexselected # the actual selection index, does not go to -1
		
		## Which kind of a McList am I?
		iAmTargetList = isinstance( self.parent, TargetPogChooser )
		## If there is an active selection?
		if sel > -1:
			for x in range(0, c):
				i = self.GetItem(x, 0)
				## Must make a tmp Pog before I can test installed status.
				tmpPog = fontcontrol.Pog(i.GetText())
				if tmpPog.isInstalled():
					self.SetItemImage(x, 1)
				else:
					## Handle the other icons (in the target list only)
					## that are not installed.
					if iAmTargetList:
						if x == sel:
							## No change means it *was* selected
							## and now it's been selected again
							## thus it can't be the target anymore.
							if pognochange: n = 0
							else: n = 2
							self.SetItemImage(x, n ) # new target icon
						else:
							self.SetItemImage(x, 0)
		## Tell the VIEW to imitate this picture.
			for x in range(0,c):
				ti = self.__TARGET.pogTargetlist.GetItem(x, 0) # the 0 is 'column'. Ignore.
				CLONE = ti.GetImage()# gets the image index, not an image bitmap.
				self.__VIEW.SetItemImage(x, CLONE)
				
##	def __onActivate( self,e ):
##		print "I have been activated", self.GetItemText(e.m_itemIndex)
		
	def __del__(self) :
		del self.items
		

	def __fillPogList(self):
		"""
		This is among the very FIRST things we do.
		Fill the list with pogs.
		This will CULL any bad pogs (i.e. those with malformed content)
		Thus the PogInvalid error should not happen any more after a run.
		"""
		#print "__fillPogList runs:\n\n"
		pl = self.__PC.getPogNames() # pl will always be a BYTE STRING list
		#print "pl:", pl
		#print
		
		for p in pl: # 'p' is a byte string.
			ipog = fontcontrol.Pog(p)
			try: #catch pogs that are not properly formed
				if ipog.isInstalled(): i = 1 # isInstalled opens the pog file.
				else: i = 0
			except fontybugs.PogInvalid, eInst:
				## An "invalid" pog is one that does not have
				## installed/not installed on the first line.
				print _(u"(%s) skipped. It's an invalid pog.") % [p]
				continue

			## Let's try to make a unicode of p so li.SetText(p) can display it:
			## I think it's easier to do this myself.
			try:
				up = p.decode(locale.getpreferredencoding())
				p = up
			except UnicodeDecodeError:
				## We can't convert it under this locale
				print _(u"(%s) skipped. I can't display this name under your locale.") % [p]
				continue
			## Okay, we have a valid pog name to use:
			li = wx.ListItem() 
			li.SetImage(i) 
			li.SetText(p) 
			id = wx.NewId()
			PogChooser.__poglistCopy[id] = p # record the pog name
			row = self.InsertItem( li ) 
			self.SetItemData( row, id ) # associate back to __poglistCopy

		self.SortItems( self.__Sorter )
		
	def AddItem(self, pogname):
		"""
		Add a pogname to myself, then sort.
		"""
		li = wx.ListItem()
		li.SetImage(0)
		li.SetText(pogname)
		id = wx.NewId()
		self.__poglistCopy[id] = pogname 
		row = self.InsertItem(li)
		self.SetItemData( row, id )
		self.SortItems( self.__Sorter )
		
	def RemoveItem(self, pogname):
		row = self.FindItem(-1, pogname)
		id = self.GetItemData(row)
		self.DeleteItem(row)
		del( PogChooser.__poglistCopy[id] ) # cull from our private store too.

	def ClearSelection(self):
		# removes all selections, even for multi-selections
		for x in range(self.GetSelectedItemCount()):
			self.Select(self.GetFirstSelected(), False)
		self.lastindexselected = -1
		
	def ChangeIcon(self, args):
		"""
		Change a single Pog's icon to installed/uninstalled.
		ONLY called from InstallPog and UninstallPog.
		"""
		T = fpsys.state.targetobject
		pn = T.name
		index = self.FindItem(0, pn) 
		if T.isInstalled(): n = 1
		else: n = 0
		self.SetItemImage(index, n) ## Found in wxWidgets documentation!
		
	def ClearLastIndex(self):
		"""
		We need to reset the lastindexselected so that a click on the 
		same item as last time will register. This is used in the Notebook
		when the page changes back to page 1, we want the user to
		be able to re-click the item that was clicked last time.
		"""	
		self.lastindexselected = -1

class Splitter(wx.SplitterWindow):
	"""
	The splitter used twice in mainframe.
	"""
	def __init__(self, parent) :
		wx.SplitterWindow.__init__(self, parent, -1, style = wx.SP_LIVE_UPDATE | wx.SP_3D) 

class DirControl(wx.GenericDirCtrl) :
	"""
	The Directory tree view.
	"""
	def __init__(self, parent):
		if fpsys.state.viewpattern == "F": 
			startdir = fpsys.state.viewobject.path
		else: 
			##Let's get it from the config object
			lastdir = fpsys.config.lastdir
			
			if os.path.exists(lastdir):
				startdir = lastdir
			else:
				startdir = os.environ['HOME']
		wx.GenericDirCtrl.__init__(self, parent, -1, dir = startdir, style=wx.DIRCTRL_DIR_ONLY)
##		self.ShowHidden( True )
		
		## Weird step:
		self.tree = self.GetTreeCtrl() 
		## NOTE: The click event is bound in the otebook.
		
		#self.tree.SetCursor(wx.StockCursor(wx.CURSOR_HAND)) #dec 2007 : removed cos it sucked.

class SearchControl(wx.Panel):
	def __init__(self, parent):
		"""Search tab on the left part notebook."""
		wx.Panel.__init__(self, parent, style=wx.NO_BORDER)
		self._vsizer = wx.BoxSizer(wx.VERTICAL)
		self._fpb = fpb.FoldPanelBar(self, extraStyle=fpb.FPB_SINGLE_FOLD)
		self._vsizer.Add(self._fpb, 1, wx.EXPAND)

		# Controls for Name Record Search
		self._nr = self._fpb.AddFoldPanel(_("Name Records"), collapsed=True)
		self._fpb.AddFoldPanelWindow(self._nr, wx.StaticText(self._nr, -1, _("Search Name Records")))
		panel0 = wx.Panel(self._nr, style=wx.NO_BORDER)
		grid0 = wx.GridSizer(1,2,3,3)
		panel0.SetSizer(grid0)
		self._txtNR  = wx.TextCtrl(self._nr)
		self._buttNR = wx.Button(panel0, 0, _("Compile"), style=1)
		grid0.Add(self._buttNR,3, wx.EXPAND)
		self._helpNR = wx.Button(panel0, wx.ID_HELP, style=1)
		self._helpNR.Bind(wx.EVT_BUTTON, self._HelpNR)
		grid0.Add(self._helpNR, 1, wx.ALIGN_RIGHT)
		panel0.SetSize(grid0.GetMinSize())
		grid0.Layout()
		self._fpb.AddFoldPanelWindow(self._nr, self._txtNR, fpb.FPB_ALIGN_WIDTH)
		self._fpb.AddFoldPanelWindow(self._nr, panel0, fpb.FPB_ALIGN_WIDTH)

		# Controls for PANOSE Search
		self._pn = self._fpb.AddFoldPanel(_("PANOSE Classification"), collapsed=False)
		self._fpb.AddFoldPanelWindow(self._pn, wx.StaticText(self._pn, -1, _("Search PANOSE")))
		panel1 = wx.Panel(self._pn, style=wx.NO_BORDER)
		grid1 = wx.GridSizer(1,2,3,3)
		panel1.SetSizer(grid1)
		self._txtPAN  = wx.TextCtrl(self._pn)
		self._buttPAN = wx.Button(panel1, 0, _("Compile"), style=1)
		grid1.Add(self._buttPAN,3, wx.EXPAND)
		self._helpPAN = wx.Button(panel1, wx.ID_HELP, style=1)
		self._helpPAN.Bind(wx.EVT_BUTTON, self._HelpPAN)
		grid1.Add(self._helpPAN, 1, wx.ALIGN_RIGHT)
		panel1.SetSize(grid1.GetMinSize())
		grid1.Layout()
		self._fpb.AddFoldPanelWindow(self._pn, self._txtPAN, fpb.FPB_ALIGN_WIDTH)
		self._fpb.AddFoldPanelWindow(self._pn, panel1, fpb.FPB_ALIGN_WIDTH)

		# Controls for Appereance Search
		self._ap = self._fpb.AddFoldPanel(_("Appereance"), collapsed=True)
		self._fpb.AddFoldPanelWindow(self._ap, wx.StaticText(self._ap, -1, _("Search Appereance")))

		# Start the search in 4 different ways
		buttGrid = wx.GridSizer(4,1,0,0)
		buttActualPog = wx.Button(self, 0, _("Search actual Pog"))
		buttActualPog.Bind(wx.EVT_BUTTON, self._startSearch)
		buttAllPogs = wx.Button(self, 1, _("Search all Pogs"))
		buttAllPogs.Bind(wx.EVT_BUTTON, self._startSearch)
		buttActualFolder = wx.Button(self, 2, _("Search actual Folder"))
		buttActualFolder.Bind(wx.EVT_BUTTON, self._startSearch)
		buttFolder = wx.Button(self, 3, _("Search selected Folder"))
		buttFolder.Bind(wx.EVT_BUTTON, self._startSearch)
		buttGrid.AddMany([(buttActualPog, 1, wx.EXPAND),
						 (buttAllPogs  , 1, wx.EXPAND),
						 (buttActualFolder , 1, wx.EXPAND),
						 (buttFolder , 1, wx.EXPAND)])

		self._vsizer.Add(buttGrid, 0, wx.ALIGN_BOTTOM|wx.EXPAND)
		self.SetSizer(self._vsizer)
		self._vsizer.Layout()
		self.SetSize(self._vsizer.GetMinSize())

	def _HelpNR(self, event):
		dlg = wx.MessageDialog(None, strings.helpNR, _("Name Records"), wx.OK)
		dlg.ShowModal()

	def _HelpPAN(self, event):
		dlg = wx.MessageDialog(None, strings.helpPAN, _("PANOSE Classification"), wx.OK)
		dlg.ShowModal()

	def _startSearch(self, event):
		clime = event.GetEventObject().GetId()
		n = [x for x in range(3) if self._fpb.GetFoldPanel(x).IsExpanded()]
		pattern = "NPA"[n[0]]
		if clime == 3:
			dlg = wx.DirDialog(None)
			dlg.ShowModal()
			print dlg.GetPath()
			dlg.Destroy()
		dlg = wx.ProgressDialog(_("Searching..."), str(clime) + " " + pattern, parent = app.GetTopWindow(),
								style=wx.PD_APP_MODAL|wx.PD_CAN_ABORT|wx.PD_REMAINING_TIME|wx.PD_SMOOTH)
		for x in range(101):
			dlg.Update(x)

class NoteBook(wx.Notebook):
	"""
	Used in the left part of the splitter in mainframe.
	Has two tabs - Folders and Pogs
	THIS IS THE VIEW or SOURCE of fonts.	
	"""
	def __init__(self, parent):
		wx.Notebook.__init__(self, parent)
		self.imlist = wx.ImageList(16, 16)
		
		pan1 = wx.Panel(self) 
		self.dircontrol = DirControl(pan1) 

		self.buttAddAll = wx.Button(pan1, label = _('All fonts in a (new) Pog'))
		# self.buttAddAll.SetToolTipString(_('Creates a new pog and puts all fonts into'))
		self.buttAddAll.Enable(False)
		self.buttAddAll.Bind(wx.EVT_LEFT_UP,self.__addAllFontsToNewPog)
		
		box = wx.BoxSizer(wx.VERTICAL) 
		box.Add(self.dircontrol,1, wx.EXPAND) 
		box.Add(self.buttAddAll,0,wx.EXPAND) 
	
		pan1.SetSizer(box) 
		box.Layout() 

		self.pogindexselected = 0
		
		pan2 = wx.Panel(self) 

		page = 0
		s = None
		if fpsys.state.viewpattern  == "P": 
			s = fpsys.state.viewobject.name
			if s == "EMPTY": s= None #Very first run, the view will be an EMPTY object.
			page = 1
		self.listctrl = PogChooser(pan2, select = s)
		
		ps.sub(pog_selected, self.OnViewPogClick)
		ps.sub(select_no_view_pog, self.SelectNoView)
		
		self.tree = self.dircontrol.GetTreeCtrl()
		#self.tree.Bind(wx.EVT_LEFT_DCLICK, self.__onDirCtrlDClick) #Old system - double click.
		#self.tree.Bind(wx.EVT_LIST_ITEM_SELECTED, self.__onDirCtrlDClick) #Did not fire.
		
		## The trouble with this event is that a click on the little
		## arrow (to open a branch) ALSO fires this, so we get a redraw
		## of fonts everytime - which sucks big.
		self.tree.Bind(wx.EVT_LEFT_UP, self.__onDirCtrlClick)
		
		box2 = wx.BoxSizer(wx.HORIZONTAL) 
		box2.Add(self.listctrl,1,wx.EXPAND) 
		pan2.SetSizer(box2) 
		box2.Layout() 
		
		pan3 = SearchControl(self)

		self.AddPage(pan1, _("Folders"))
		self.AddPage(pan2, _("Pogs")) 
		self.AddPage(pan3, _("Search"))
		
		source_pog_icon = self.imlist.Add\
		(wx.Bitmap(fpsys.mythingsdir + "/icon_source_pog_16x16.png",wx.BITMAP_TYPE_PNG))

		target_pog_icon = self.imlist.Add\
		(wx.Bitmap(fpsys.mythingsdir + "/icon_source_folder_16x16.png",wx.BITMAP_TYPE_PNG))

		search_pog_icon = self.imlist.Add\
		(wx.Bitmap(fpsys.mythingsdir + "/icon_source_search_16x16.png",wx.BITMAP_TYPE_PNG))

		self.AssignImageList(self.imlist)
		self.SetPageImage(1, source_pog_icon)
		self.SetPageImage(0, target_pog_icon)
		self.SetPageImage(2, search_pog_icon)

		self.SetSelection(page)
	
		self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.__onPageChanged) # Bind page changed event
		
	def __onPageChanged(self, e):
		if e.GetSelection() == 1:
			self.buttAddAll.Enable(False)
			self.listctrl.ClearLastIndex()
			e.Skip()
		
	def __addAllFontsToNewPog(self, e):
		"""Puts all fonts in a folder in an new pog"""
		mfPogChooser = app.GetTopWindow().panelTargetPogChooser
		name = fpsys.config.lastview.split("/")[-1]
		oldpl = fpsys.iPC.getPogNames()
		# The fonts in this folder may saved in an other pog before
		# assume this is the case, if over 80 % in the pog
		count = 0
		for p in oldpl:
			pog = fontcontrol.Pog(p)
			pog.genList()
			for font in pog:
				if str(fpsys.config.lastview) in font.glyphpaf:
					count += 1
			if ((count * 100) / len(os.listdir(fpsys.config.lastview))) > 80:
				dlg = wx.MessageDialog(self, 
				_("The Source '%s' seems to be saved in\nPog '%s' before!\n\n\tContinue anyway?") %(name,pog.name),
				_("Warning"),
				wx.YES_NO | wx.ICON_INFORMATION
								  )
				if dlg.ShowModal() == wx.ID_NO:
				# OK do nothing
					del oldpl ; del pog ; del count
					return
				dlg.Destroy()
			count = 0

		if fpsys.state.targetobject is None:
			# Create the new pog
			mfPogChooser.newPogForAll(e, new_pogname = name)
			pl = fpsys.iPC.getPogNames()
			# Find the name given in the dialog
			name = [n for n in pl if n not in oldpl]
			if name:
				name = name[0]
			else:
				# We find no new pog
				return

			# Select only the new pog
			mfPogChooser.pogTargetlist.ClearSelection()
			mfPogChooser.pogTargetlist.Select(mfPogChooser.pogTargetlist.FindItem(0,name))
			del pl
		
		# Tick all fonts in the folder
		for fi in fpsys.state.viewobject:
			fi.ticked = True

		# and start the main action
		app.GetTopWindow().OnMainClick(None)

		if oldpl: 
			del pog
		del oldpl ; del count ; del name ; del mfPogChooser

		return

	def __onDirCtrlClick(self, e):
		wx.BeginBusyCursor() #Thanks to Suzuki Alex on the wxpython list!
		p = self.dircontrol.GetPath()
		try:
			fpsys.instantiateViewFolder(p)
			fpsys.config.lastdir = p
		except fontybugs.FolderHasNoFonts, e:
			pass # update_font_view handles this with a std message.
		
		ps.pub(reset_to_page_one)# reset before updating!		  
		ps.pub(update_font_view)
		
		if fpsys.state.viewpattern == "F":
			self.buttAddAll.Enable(True)
			self.buttAddAll.SetId(app.GetTopWindow().panelTargetPogChooser.idnew)
		else:
			self.buttAddAll.Enable(False)
		wx.EndBusyCursor()
		
	def OnViewPogClick(self, args):
		"""
		args is like this : (u'pogname', -223, False)
		"""
		## id of the originating instance is sent in args[1]
		## We must be sure it came from listctrl ...
		if args[1] != self.listctrl.GetId(): 
			return
		## Check pognochange, it means this is the same pog as last time.
		if args[2]: return 
		
		## instantiateViewPog calls pog.genList which bubbles:
		## PogInvalid
		## BUT - this error only makes sense from the
		## cli pov. By the time the gui is running, that
		## pog has been renamed .badpog and therefore 
		## won't even appear in the list. So, don't bother
		## catching it.
		fpsys.instantiateViewPog(args[0])

		if fpsys.state.samepogs: #forbid same pogs selection
			ps.pub(select_no_target_pog)
		else:
			ps.pub(reset_to_page_one)
		ps.pub(update_font_view)
	
	def AddItem(self, pogname):
		self.listctrl.AddItem(pogname)
	def RemoveItem(self, pogname):
		self.listctrl.RemoveItem(pogname)
		
	def SelectNoView(self, args):
		## Purpose: To select no viewobject and clear view pog list selections
		## Called when a TARGET item is clicked AND samepogs it True
		wx.BeginBusyCursor()
		self.listctrl.ClearSelection()
		fpsys.SetViewPogToEmpty()
		wx.EndBusyCursor()
		
class StatusBar(wx.StatusBar):
	"""
	The status bar
	"""
	def __init__(self, parent):
		wx.StatusBar.__init__(self, parent, -1)
		self.SetFieldsCount(1)
		self.SetStatusText( _("Welcome to Fonty Python version %s") % fpversion.version, 0)
	def Report(self, msg):
		self.SetStatusText(msg, 0)

class MainFrame(wx.Frame):

	def __init__(self, parent,title):
		## Draw the frame
		title = title + "   -   " + locale.getpreferredencoding()
		wx.Frame.__init__(self,parent,-1,title,fpsys.config.pos,fpsys.config.size) 
		
		## Suddenly don't need this anymore.
		#self.SetSizeHintsSz((300,400))  #After hours of hell, this is all that seems to work.
		#self.SetSizeHintsSz( fpsys.config.size )
		
		## Try to show an icon
		try:
			image = wx.Image(fpsys.mythingsdir + 'fplogo.png', wx.BITMAP_TYPE_PNG) 
			image = image.ConvertToBitmap() 
			icon = wx.EmptyIcon() 
			icon.CopyFromBitmap(image) 
			self.SetIcon(icon) 
		except:
			pass

		## STATUS BAR
		self.sb = StatusBar(self)
		self.SetStatusBar(self.sb)
		
		## Prepare the menu bar
		self.menuBar = wx.MenuBar()

		## 1st menu from left
		menu1 = wx.Menu()
		menu1.Append(101, _("&Settings\tCtrl+S"), _("Change settings"))
		menu1.AppendSeparator()
		## Jan 18 2008
		menu1.Append( 102, _("&Check fonts"), _("Find those fonts that crash Fonty.") )
		
		self.exit = menu1.Append(103, _("&Exit"), _("Close the app"))
		## Add menu to the menu bar
		self.menuBar.Append(menu1, _("&File"))

		## 2nd menu from left
		menu2 = wx.Menu() 
		menu2.Append(201, _("H&elp\tF1"))
		menu2.Append(202, _("&About"))
		## Append 2nd menu
		self.menuBar.Append(menu2, _("&Help"))

		## Tell the frame the news
		self.SetMenuBar(self.menuBar)

		## Setup the ESC key trap
		accel = wx.AcceleratorTable([(wx.ACCEL_NORMAL, wx.WXK_ESCAPE, self.exit.GetId())])
		self.SetAcceleratorTable(accel)
		
		## The X close window button.
		self.Bind( wx.EVT_CLOSE, self.__onHandleESC )
		
		self.Bind(wx.EVT_MENU, self.__onHandleESC, self.exit)
		self.Bind(wx.EVT_MENU, self.__menuSettings, id = 101)
		self.Bind(wx.EVT_MENU, self.__menuCheckFonts, id = 102 )
		self.Bind(wx.EVT_MENU, self.__menuAbout, id = 202)
		self.Bind(wx.EVT_MENU, self.__menuHelp, id = 201)

		## Create a splitter 
		self.splitter = Splitter(self) 
	
		## The notebook
		self.panelNotebook = wx.Panel(self.splitter) 
		
		## Notebook label and icon
		self.viewIcon = wx.StaticBitmap\
		(self.panelNotebook, -1, wx.Bitmap\
		(fpsys.mythingsdir + 'icon_source_16x16.png', wx.BITMAP_TYPE_PNG))		
		self.viewLabel = wx.StaticText\
		(self.panelNotebook, -1, _("Source Folder, or Pog"), style = wx.ALIGN_LEFT)
		self.viewLabel.SetFont\
		(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD))
		
		## A horiz sizer to hold the icon and text
		self.sizer_iconandtext = wx.BoxSizer(wx.HORIZONTAL)
		self.sizer_iconandtext.Add((4,1),0)
		self.sizer_iconandtext.Add\
		(self.viewIcon, 0, wx.TOP | wx.BOTTOM, border = 4)
		self.sizer_iconandtext.Add\
		(self.viewLabel, 1, wx.EXPAND | wx.TOP | wx.BOTTOM | wx.LEFT, border = 4)
		
		## Now the actual notebook
		self.nb = NoteBook(self.panelNotebook)

		## Make a Vertical sizer to hold them.
		self.sizerNotebook = wx.BoxSizer(wx.VERTICAL)
		
		## Add them to the sizer.
		self.sizerNotebook.Add(self.sizer_iconandtext, 0, wx.EXPAND)
		self.sizerNotebook.Add(self.nb,1,wx.EXPAND) 
		
		self.panelNotebook.SetSizer(self.sizerNotebook) 
		self.sizerNotebook.Layout() 
		
		## dec 2007 : Added a second splitter. It was a bitch!
		self.splitter2 = Splitter(self.splitter) # gets the second slot of splitter
		
		## Font View Panel Control:
		self.panelFontView = FontViewPanel(self.splitter2) # first slot in splitter2
		
		self.sizerFontView  = wx.BoxSizer(wx.VERTICAL) 
		self.sizerFontView.Add(self.panelFontView, 1, wx.EXPAND)
		self.panelFontView.Layout()
	   
		## THE FAR RIGHT HAND SIDE
		## The TargetPogChooser
		self.panelTargetPogChooser = TargetPogChooser(self.splitter2) # last slot of splitter2

		self.sizerRight = wx.BoxSizer(wx.HORIZONTAL)
		self.sizerRight.Add(self.panelTargetPogChooser, 1, wx.EXPAND)
		self.panelTargetPogChooser.Layout()
		
		self.splitter.SetMinimumPaneSize(64) 
		self.splitter.SplitVertically\
		(self.panelNotebook, self.splitter2, fpsys.config.leftSash )
		self.splitter2.SetMinimumPaneSize(128)
		# Negative here means pixels from the right edge.
		self.splitter2.SplitVertically\
		(self.panelFontView, self.panelTargetPogChooser, -fpsys.config.rightSash )

		self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
		
		## Now to subscribe to have my various def called from other places:
		ps.sub(update_font_view, self.UpdateFontViewPanel)
		ps.sub(show_error, self.ErrorBox)
		ps.sub(show_error_and_abort, self.ErrorAbort)
		ps.sub(show_message, self.MessageBox)
		ps.sub(reset_to_page_one, self.ResetToPageOne)
		ps.sub(add_item_to_notebook, self.NotebookAddItem)
		ps.sub(remove_item_from_notebook, self.NotebookRemoveItem)
		ps.sub(print_to_status_bar, self.StatusbarPrint)
		ps.sub(install_pog, self.InstallPog)
		ps.sub(uninstall_pog, self.UninstallPog)
		ps.sub(main_button_click, self.OnMainClick)
		
		
		## Dec 2007 - Actually this one does not function.
		ps.sub(menu_settings, self.__menuSettings)
		
		## When splitter is changed (after the drag), we want to redraw
		## the fonts to the new width.
		self.splitter.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.__onSize)
		
		self.Layout()

		## call the big one - the big chief, the big cheese:
		self.UpdateFontViewPanel() #Go and fill in the font view and surrounding controls
		
		## A nasty looking line to call the SortOutTheDamnImages function
		## This is to draw the right icons dep on the params from cli.
		self.panelTargetPogChooser.pogTargetlist.SortOutTheDamnImages(False)
		
	def __onSize(self, evt):
		"""
		The splitter has been moved. Don't ask me why splitter and not splitter2
		is the one we have to use. Go figure.
		"""
		ps.pub( update_font_view ) # starts a chain of calls.

	def GetSashesPos( self, args=None ):
		## For saving/restoring the sashes to where we bloody left them :\
		return ( self.splitter.GetSashPosition(), self.panelTargetPogChooser.GetClientSize()[0])
		
	def StatusbarPrint(self, args):
		self.sb.Report(args[0])
	def NotebookAddItem(self,args):
		self.nb.AddItem(args[0])
	def NotebookRemoveItem(self, args):
		self.nb.RemoveItem(args[0])
	def ResetToPageOne(self, args):
		"""
		Calls ResetToPageOne in the FontViewPanel
		"""
		self.panelFontView.ResetToPageOne()
		
	def MessageBox(self, args):
		dlg = wx.MessageDialog(self, args[0] , _("Warning"), wx.OK | wx.ICON_INFORMATION)
		dlg.ShowModal()
		dlg.Destroy()
	def ErrorBox(self, args):
		dlg = wx.MessageDialog(self, args[0], _("Error"), wx.OK | wx.ICON_ERROR)
		dlg.ShowModal()
		dlg.Destroy()
	def ErrorAbort(self, args):
		self.ErrorBox(args) #Pass it along to be displayed
		self.__endApp()
		
	def UpdateFontViewPanel(self, args = None):
		self.panelFontView.MainFontViewUpdate()
		self.Refresh()
	
	def InstallPog(self, args):
		"""
		pog.install() Raises:
				PogEmpty
				PogAllFontsFailedToInstall
				PogSomeFontsDidNotInstall
		"""
		try:
			fpsys.state.targetobject.install()
		except (fontybugs.PogSomeFontsDidNotInstall), e:
			## Show a warning, but continue.
			self.ErrorBox([unicode( e ),]) #send it as a list
		except (fontybugs.PogEmpty, fontybugs.PogAllFontsFailedToInstall), e:
			## Either Pog is empty, or
			## not a single font in this pog actually installed.
			## It has already been flagged as NOT INSTALLED
			self.ErrorBox([unicode( e ),])
			return # Make no changes to the display or icon - yet... badpog icon ?
		## Update GUI
		self.sb.Report(_("%s has been installed.") % fpsys.state.targetobject.name)
		ps.pub(change_pog_icon)
		ps.pub(toggle_buttons) # Update the greying of the buttons
		self.UpdateFontViewPanel()

	def UninstallPog(self, args):
		"""
		pog.uninstall() Raises:
				PogEmpty
				PogLinksRemain
				PogNotInstalled		
		"""
		try:
			fpsys.state.targetobject.uninstall()
		except (fontybugs.PogEmpty, 
						fontybugs.PogNotInstalled, 
						fontybugs.PogLinksRemain
					 ), e:
			## PogNotInstalled is prevented by buttons greying out in the gui.
			self.ErrorBox([unicode( e ),])
			return
		## Update GUI
		self.sb.Report(_("%s has been uninstalled.") % fpsys.state.targetobject.name)
		ps.pub(change_pog_icon)
		ps.pub(toggle_buttons) #Update the greying of the buttons
		self.UpdateFontViewPanel()

			
	def OnMainClick(self, args) :
		"""
		Removes fonts, or Appends fonts. Depends on situation in fpsys.state
		
		It's odd to have these routines in mainframe. I am using dialogues that
		parent to the wx.Frame but I suppose I could shift this to panelFontView.
		"""
		## Let's determine what kind of thing to do:
		if fpsys.state.action == "REMOVE":
			## We have a pog in viewobject and we must remove the selected fonts from it.
			vo = fpsys.state.viewobject
			victims = []
			dowrite = False
			for fi in vo:
				if fi.ticked:
					victims.append(fi) #Put it into another list
					dowrite = True
			for fi in victims:
				vo.remove(fi) #Now remove it from the vo
			del victims
			
			if dowrite:
				fpsys.flushTicks()
				bug = False
				try:
					vo.write()	  
				except(fontybugs.PogWriteError), e:
					bug = True
					self.errorBox([unicode( e ),])
				## Now, let's redraw the vo
				self.UpdateFontViewPanel()
				if not bug:
					self.sb.Report(_("Selected fonts have been removed."))
				else:
					self.sb.Report(_("There was an error writing the pog to disk. Nothing has been done"))
		
		## APPEND - Copy ttf to a pog.
		if fpsys.state.action == "APPEND":
			## We must append the fonts to the Pog
			vo = fpsys.state.viewobject
			to = fpsys.state.targetobject
			print _("Copying fonts from %(source)s to %(target)s") % {"source":vo.label(), "target":to.label()}
			dowrite = False
			for fi in vo:
				if fi.ticked:
					to.append(fi) 
					dowrite = True
			if dowrite: 
				fpsys.flushTicks() #Ensure we have no more ticks after a succ xfer.
				bug = False
				try:
					to.write()	  
				except(fontybugs.PogWriteError), e:
					bug = True
					self.ErrorBox( [repr( e )] )
				self.UpdateFontViewPanel()
				if not bug:
					self.sb.Report(_("Selected fonts are now in %s.") % to.label())
				else:
					self.sb.Report(_("There was an error writing the pog to disk. Nothing has been done"))
		
		## After pressing the button, the focus goes ... away ...
		## I don't know where and I'm trying to get it to go someplace
		## so that the ESC key continues working.
		## Forget it. I can't fix this. Onwards... other stuff to do!
		## self.menuBar.SetFocus()
		
	def __onHandleESC(self, e) :
		print strings.done
		self.__endApp() 

	def __endApp(self) :
		"""
		Save app's vital statistics and exit.
		See the end of start.py where it's actually saved.
		"""
		fpsys.config.pos = self.GetPositionTuple() 
		## Dec 2007 - I was using the wring func and the
		## main window kept getting smaller!
		fpsys.config.size = self.GetSizeTuple()
		fpsys.config.leftSash, fpsys.config.rightSash = self.GetSashesPos()
		self.Destroy() 
   
	def __menuSettings(self, e):
		lastnuminpage, lastpoints, lasttext = fpsys.config.numinpage ,fpsys.config.text, fpsys.config.points
		dlg = dialogues.DialogSettings(self)
		val = dlg.ShowModal()
		if val == wx.ID_OK:
			## Did anything change?
			num = int(dlg.inputPageLen.GetValue())
			points = int(dlg.inputPointSize.GetValue())
			txt = dlg.inputSampleString.GetValue()
			if (num, txt, points) != (lastnuminpage, lastpoints, lasttext):
				fpsys.config.numinpage = int(num)
				fpsys.config.points = int(points)
				if len(txt) > 0: fpsys.config.text =  txt
			## Now to refresh things:
			self.UpdateFontViewPanel()
		dlg.Destroy()

	def __menuAbout(self, e):
		dlg =dialogues.DialogAbout(self)
		val = dlg.ShowModal()
		dlg.Destroy()
		
	def __menuHelp(self, e):
		dlg = dialogues.DialogHelp(self, size=(800, 600))
		val = dlg.ShowModal()
		dlg.Destroy()

	def __menuCheckFonts( self, e ):
		"""
		Added Jan 18 2008
		User can visit suspicious directories with this tool
		to gather a list of fonts that kill the app. They will be
		marked as such and hereafter be safe to use.
		"""
		## Set startdir to the one our own dircontrol is in
		if fpsys.state.viewpattern == "F": 
			startdir = fpsys.state.viewobject.path
		else: 
			##Let's get it from the config object
			startdir = fpsys.config.lastdir
		dlg = dialogues.DialogCheckFonts( self, startdir )
		val = dlg.ShowModal()
		dlg.Destroy()
		
## Start the main frame and then show it.
class App(wx.App) :
	def OnInit(self) :
		## Initial dialogue to inform user about their potential fate:
		if not "unicode" in wx.PlatformInfo:
			wx.MessageBox(_("I am sorry, but Unicode is not supported by this installation of wxPython. Fonty Python relies on Unicode and will simply not work without it.\n\nPlease fetch and install the Unicode version of python-wxgtk."), caption=_("SORRY: UNICODE MUST BE SUPPORTED"), style=wx.OK | wx.ICON_EXCLAMATION )
			raise SystemExit
		frame = MainFrame(None, _("Fonty Python: bring out your fonts!"))
		self.SetTopWindow(frame) 
		frame.Show(True) 
		return True
		
## app
app = App(0) 
		
## start 
app.MainLoop() 
