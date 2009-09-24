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
import colorsys

import wx.lib.statbmp
import fontcontrol
import fpsys # Global objects
from pubsub import *
from wxgui import ps

ndc=(200,190,183) # No Draw Color: colour of background for the fonts I can't draw
black=(0,0,0)
white=(255,255,255)
class Fitmap(wx.lib.statbmp.GenStaticBitmap):
	"""
	This class is a bitmap of a TTF font - it detects a click and 
	also displays itself with other information below it.
	"""
	
	## This class-level dict is a kind of "style sheet" to use in fitmap drawing.
	styles={
			'FILE_NOT_FOUND':
				{
					'backcol': (255,214,57),
					'fcol'   : black,
					'bcol'   : white,
					'icon'	 : "NOT_FOUND",
					'fx'	 : {'step':0.02, 'range':0.6}
					},
			'PIL_SEGFAULT_ERROR':
				{
					'backcol': (183,200,190),
					'fcol'   : black,
					'bcol'   : white,
					'icon'	 : "SEGFAULT" ,
					'fx'	 : {'step':0.02, 'range':0.4}
					},
			'PIL_IO_ERROR':
				{
					'backcol': ndc,
					'fcol'   : black,
					'bcol'   : white,
					'icon'	 : "NO_DRAW",
					'fx'	 : {'step':0.02, 'range':0.4}
					},
			'PIL_UNICODE_ERROR':
				{
					'backcol': ndc,
					'fcol'   : black,
					'bcol'   : white,
					'icon'	 : "NO_DRAW",
					'fx'	 : {'step':0.02, 'range':0.4}
					},
			'PIL_CANNOT_RENDER':
				{
					'backcol': ndc,
					'fcol'   : black,
					'bcol'   : white,
					'icon'	 : "NO_DRAW",
					'fx'	 : {'step':0.02, 'range':0.4}
					},
			'ACTIVE':
				{
					'backcol': white,
					'fcol'   : black,
					'bcol'   : (200,200,200),
					'icon'	 : None,
					'fx'	 : {'step':0.01, 'range':0.8}
				},
			'INACTIVE':
				{
					'backcol': white,
					'fcol'   : (128,128,128), 
					'bcol'   : white,
					'icon'	 : None,
					'fx'	 : {'step':0.01, 'range':0.8}
				},
			'INFO_FONT_ITEM':
				{
					'backcol': white,
					'fcol'   : black,
					'icon'	 : "INFO_ITEM",
					'fx'	 : {'step':0.01, 'range':0.9}
				}

			}

	def __init__( self, parent, pos, fitem ) :
		self.name = fitem.name
		
		self.fitem = fitem
		self.parent = parent

		self.FVP = self.parent.parent #The Font View Panel
		self.TICKMAP =  self.FVP.TICKMAP 

		self.bitmapHeight = 0
	
		self.style = {} #Temporary space for style of fitem while drawing. It's a copy of one key from Fitem.styles
		
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
		self.Bind(wx.EVT_LEFT_UP,self.onClick) 
		self.Bind(wx.EVT_MIDDLE_UP, self.onMiddleClick)	
		
		## Redraw event
		self.Bind(wx.EVT_PAINT,  self.onPaint) 
		
		## Very cool,sets the icon for font items.
		self.SetCursor( wx.StockCursor( wx.CURSOR_ARROW ) )
		
		## If this is *not* a FILE_NOT_FOUND then allow the cursor to change
		## FILE_NOT_FOUND means we have a glyphpaf but no match on the drive.
		## This means the Pog should be purged.
		if self.fitem.badstyle != "FILE_NOT_FOUND":
			if fpsys.state.action == "REMOVE":
				self.SetCursor( wx.StockCursor( wx.CURSOR_PENCIL ) )
			elif fpsys.state.action == "APPEND":
				if not self.fitem.inactive:
					self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))

	@property # Cool.  I refer to blah.width and didn't want to alter them to blah.width(). This fixes that.
	def width(self):
		return self.FVP.getWidthOfMiddle()

	def onPaint(self, event):
		"""
		Dump the bitmap to the screen.
		"""
		if self.bitmap:
			## Create a buffered paint DC.  It will create the real
			## wx.PaintDC and then blit the bitmap to it when dc is
			## deleted.  Since we don't need to draw anything else
			## here that's all there is to it.
			dc = wx.BufferedPaintDC(self, self.bitmap, wx.BUFFER_VIRTUAL_AREA)

	def onMiddleClick(self, event):
		ps.pub( menu_settings, None )

	def onClick(self, event) :
		if fpsys.state.cantick and not self.fitem.inactive:
			self.fitem.ticked = not(self.fitem.ticked)
			self.prepareBitmap() # This only redraws a single font item.
			self.Refresh()  #forces a redraw.
			 
			## Inc or dec a counter depending on the tickedness of this item
			if self.fitem.ticked: fpsys.state.numticks += 1
			if not self.fitem.ticked: fpsys.state.numticks -= 1
			ps.pub(toggle_main_button)
		event.Skip()	

	def prepareBitmap( self ):
		"""
		This is where all the drawing code goes. It gets the font rendered
		from the FontItems (via PIL) and then draws a single Fitmap.
		"""
		## Is this a normal FontItem, or an InfoFontItem?
		## InfoFontItem is a fake font item for the purposes
		## of saying "There are no fonts to see here."
		if isinstance( self.fitem, fontcontrol.InfoFontItem ):
			self.style=Fitmap.styles['INFO_FONT_ITEM']
			self.drawInfoOrError(  self.width, self.minHeight )
			return # Just get out.
			
		## Normal FontItem object
		spacer = 40 # Gap below each font bitmap
		
		
		## Get a list of pilimages, for each subface: Some fonts 
		## have multiple faces, and their heights.
		## If the height returned by PIL is larger than the maxHeight then
		## I force pil to render to maxHeight.
		## REMEMBER: This loop is all FOR THIS ONE FONT ITEM.
		##
		## It only supplies pilimages for fonts it could open and
		## render. So this font may indeed have nothing in the pilList[]
		## after this loop.
		pilList=[]
		totheight = 0
		maxwidth = [self.width] # to figure-out the biggest width

		for pilimage,height,pilwidth in self.fitem.generatePilFont( self.maxHeight ):
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
		
		self.setStyle() #Go set the self.style

		if self.fitem.badfont:
			## We have a badstyle to help us differentiate these.
			memDc=self.drawInfoOrError(  self.width, self.minHeight )

			## Record the calculated height
			self.height = self.minHeight
			
		## It's *not* a badfont
		else:
			## Make one big bitmap to house one or more faces (subfaces)
			memDc=self.makeBlankDC( maxwidth, totheight, white )
			fcol = self.style['fcol']
			bcol = self.style['bcol']		

			y = i = 0
			for pilimage, glyphHeight, pilwidth in pilList:
				wxfaceimage = wx.EmptyImage( pilwidth, glyphHeight )
				try:
					## Get the data from PIL into wx
					wxfaceimage.SetData( pilimage.convert('RGB').tostring() ) 
					faceBitmap = wxfaceimage.ConvertToBitmap() 
				except:
					## Some new error that I have not caught before has happened.
					## It may also be a bad sub-face from a ttc font.
					## Draw error message into the memDc
					memDc.SetTextForeground( fcol )
					txt=_("This text cannot be drawn. Hey, it happens...")
					memDc.SetFont( wx.Font( fpsys.config.points, family=wx.SWISS, style=wx.ITALIC, weight=wx.NORMAL))
					memDc.DrawText( txt, 10, y-2)
				else: #no error happened, we carry on.
					## Place it into the main image, down a tad so it looks better.
					facex = 5
					if i > 0: facex *= 2 # Shift sub-faces over a little
					## Draw the face into the memDc
					memDc.DrawBitmap( faceBitmap, facex, y + 4, True )
				   
				## draw the fading effect under the faceBitmap  
				## only if we are at the end of the faces
				## must be done here so text goes above it.
				if i == self.fitem.numFaces-1:
					self.bottomFadeEffect( memDc, totheight, maxwidth )
				
				## Postion 
				texty = y + glyphHeight + (spacer/8)

				## Now draw the text showing the font name/family/style.
				## -- suggested by Chris Mohler.
				## Prep the text to show "font family name (font file name)"
				## Added Style info 3 Dec 2006:			
				txt = "%s - %s - [%s]" % (self.fitem.family[i], self.fitem.style[i], self.name)
				memDc.SetTextForeground( fcol )
				## Sep 2009: Trying to draw foreign chars via DrawText
				memDc.SetFont( wx.Font( 8, family=wx.SWISS, style=wx.NORMAL, weight=wx.NORMAL,encoding=wx.FONTENCODING_DEFAULT))
				memDc.DrawText( txt, 16, texty)
						
				## Move TOP down to next BOTTOM (for next sub-face)
				y = y + glyphHeight +  spacer
					
				## Goto next face, if any.
				i += 1			
		
			## Record the calculated height
			self.height = totheight

		## Special message
		if self.fitem.inactive:
			memDc.SetFont( wx.Font(10,family=wx.SWISS, style=wx.NORMAL, weight=wx.NORMAL))
			memDc.DrawText( self.fitem.activeInactiveMsg, 10, self.height-20 )

		## Draw the tick/cross if it's not a FILE_NOT_FOUND font (can't be found)
		if self.fitem.badstyle != "FILE_NOT_FOUND":
			if self.fitem.ticked:
				memDc.DrawBitmap(self.TICKMAP, 20, 5, True)
			
		## Now a dividing line
		memDc.SetPen( wx.Pen( black, 2 ) ) 
		memDc.SetBrush( wx.TRANSPARENT_BRUSH ) 
		memDc.DrawLine( 0, self.height-1, maxwidth, self.height-1 )



	def setStyle( self ):
		'''Set a copy of the styles key and alter colours as needed.'''
		# InfoFontItem does not use this, all others do.
		if self.fitem.badfont:
			self.style=Fitmap.styles[self.fitem.badstyle].copy() #damn! this was tricky!
			if self.fitem.inactive:
				self.style['fcol'] = Fitmap.styles['INACTIVE']['fcol']
				# Dim the colour of the badfont to match look of other inavtive fitems
				bg=self.style['backcol']
				hsv=self.rgb_to_hsv(bg)
				sat=self.clamp(hsv[1]/2.0)
				bright=self.clamp(hsv[2]*4.0)
				nbg=self.hsv_to_rgb((hsv[0],sat,bright))
				self.style['backcol'] = nbg
			return

		# Not bad font, just get vals from style sheet.
		if self.fitem.inactive:
			self.style = Fitmap.styles['INACTIVE']
		else: 
			self.style = Fitmap.styles['ACTIVE']


	def makeBlankDC( self, w, h, backcol ):
		bitmap = wx.EmptyImage( w,h ).ConvertToBitmap()
		memDc = wx.MemoryDC()
		memDc.SelectObject( bitmap )
		memDc.SetBackground( wx.Brush( backcol, wx.SOLID) )
		memDc.Clear()		
		self.bitmap = bitmap #record this for the init
		return memDc

	def clamp(self,v):
		if v > 1.0: v=1.0
		if v < 0.0: v=0.0
		return v

	def rgb_to_hsv(self,rgb):
		#Go from int colour to float colour (0 to 1 range)
		sr = rgb[0]/255.0
		sg = rgb[1]/255.0
		sb = rgb[2]/255.0
		return colorsys.rgb_to_hsv(sr,sg,sb)

	def hsv_to_rgb(self,hsv):
		rgb = colorsys.hsv_to_rgb( hsv[0],hsv[1],hsv[2] ) 
		# back to int
		sr = int(rgb[0]*255.0)
		sg = int(rgb[1]*255.0)
		sb = int(rgb[2]*255.0)
		return ( sr,sg,sb )

	def bottomFadeEffect( self, memDc, liney, width):
		"""
		Baptiste's idea! New implementation : June 2009
		 "Now a dividing gradient, you can say "wow" ;-)"
		 Donn says, "..Wow!" :-D   
		
		It goes from backcol and darkens it a little as it draws downwards.
		"""
		if self.fitem.inactive: return
		
		col = self.style["backcol"]
		step = self.style["fx"]["step"]
		fr = self.style["fx"]["range"]
		memDc.SetBrush ( wx.TRANSPARENT_BRUSH ) 

		## A wee generator to provide a range of float numbers
		def frange(start,end):
			v = start
			while True:
				if v > end:
					raise StopIteration
				yield v
				v += step
		hsv = self.rgb_to_hsv(col) 
		tob=hsv[2] # I want the brightness
		for bright in frange( fr, tob ):
			rgb=self.hsv_to_rgb((hsv[0],hsv[1],bright))
			memDc.SetPen( wx.Pen( rgb, 1 ) ) 
			memDc.DrawLine( 0, liney, width, liney )
			liney -= 1


	def drawInfoOrError( self, w,h ):
		"""
		Draw the Info Font block, or an Error message block. Much clearer than it was before.
		"""
		memDc=self.makeBlankDC( w, h, self.style['backcol'])
		self.bottomFadeEffect( memDc, self.minHeight, self.width )
	
		icon = self.style['icon']
		if icon:
			Icon = eval("self.FVP." + icon)
			memDc.DrawBitmap(Icon,0,0,True)

		textTup = self.fitem.InfoOrErrorText()
		
		memDc.SetTextForeground( self.style['fcol'])
		
		memDc.SetFont( wx.Font(12, family=wx.SWISS, style=wx.NORMAL, weight=wx.BOLD))
		memDc.DrawText( textTup[0], 32, 15)
		
		memDc.SetFont( wx.Font(7, family=wx.SWISS, style=wx.NORMAL, weight=wx.NORMAL))
		memDc.DrawText( textTup[1], 10, 34)

		return memDc

