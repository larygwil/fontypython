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
					},
			'PIL_SEGFAULT_ERROR':
				{
					'backcol': (183,200,190),
					'fcol'   : black,
					'bcol'   : white,
					'icon'	 : "SEGFAULT" ,
					},
			'PIL_IO_ERROR':
				{
					'backcol': ndc,
					'fcol'   : black,
					'bcol'   : white,
					'icon'	 : "NO_DRAW",
					},
			'PIL_UNICODE_ERROR':
				{
					'backcol': ndc,
					'fcol'   : black,
					'bcol'   : white,
					'icon'	 : "NO_DRAW",
					},
			'PIL_CANNOT_RENDER':
				{
					'backcol': ndc,
					'fcol'   : black,
					'bcol'   : white,
					'icon'	 : "NO_DRAW",
					},
			'ACTIVE':
				{
					'backcol': white,
					'fcol'   : black,
					'bcol'   : (200,200,200),
					'icon'	 : None,
				},
			'INACTIVE':
				{
					'backcol': white,
					'fcol'   : (128,128,128), 
					'bcol'   : white,
					'icon'	 : None,
				},
			'INFO_FONT_ITEM':
				{
					'backcol': white,
					'fcol'   : black,
					'icon'	 : "INFO_ITEM",
				}
			}

	def __init__( self, parent, pos, fitem ) :
		self.name = fitem.name
		
		self.fitem = fitem
		#self.parent = parent

		Fitmap.styles['INFO_FONT_ITEM']['backcol']=parent.GetBackgroundColour()
		self.FVP = parent.parent #The Font View Panel
		self.TICKMAP = parent.parent.TICKMAP 

		self.height =  0
	
		self.style = {} #Temporary space for style of fitem while drawing. It's a copy of one key from Fitem.styles
		
		## I control font's own height due to mad results.
		## I based this on my preference. Some ttfs had these crazy heights
		## and would shoot off the page. So, I nixed that.
		self.maxHeight = int( fpsys.config.points * 1.55 )

		# Some values for drawing
		self.minHeight = 70
		self.spacer = 35 # Gap below each font bitmap
		self.gradientheight = 50

		self.bitmap = None
		self.prepareBitmap()
		
		sz = (self.bitmap.GetWidth(), self.bitmap.GetHeight())
	   
		## Do mystical voodoo that I can't remember from 2006.
		self.gsb = wx.lib.statbmp.GenStaticBitmap.__init__(self, parent, -1, self.bitmap, pos, sz)
		

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
			self.drawInfoOrError(  self.width, self.minHeight, isinfo=True )
			return # Just get out.
		
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
			totheight += height + self.spacer
			maxwidth.append(pilwidth)
		## Limit the minimum we allow.
		if totheight < self.minHeight:
			totheight = self.minHeight		
		maxwidth = max(maxwidth) # find it.
		
		## BADFONT cases
		##  Badfonts are still available for installation, it's just that I can't
		##  display their glyph or fam/style info (until PIL is patched).
		
		self.setStyle() #Go set the self.style

		if self.fitem.badfont:
			## We have a badstyle to help us differentiate these.
			totheight = self.minHeight
			memDc=self.drawInfoOrError(  self.width, totheight)#self.minHeight )
			
		## It's *not* a badfont
		else:
			if self.fitem.inactive:
				totheight += (self.spacer-20) #want room for 'is in pog' message.
			## Make one big bitmap to house one or more faces (subfaces)
			memDc=self.makeBlankDC( maxwidth, totheight, white )
			fcol = self.style['fcol']
			bcol = self.style['bcol']		
			#Draw the gradient. The fonts will render in alpha over that.
			self.bottomFadeEffect( memDc, totheight, maxwidth )
			y = i = 0
			for pilimage, glyphHeight, pilwidth in pilList:
				try:
					## Get the data from PIL into wx.
					## Now with alpha! Thanks to:
					## http://nedbatchelder.com/blog/200801/truly_transparent_text_with_pil.html
					## http://wiki.wxpython.org/WorkingWithImages
					image=None
					image = apply( wx.EmptyImage, pilimage.size )
					image.SetData( pilimage.convert( "RGB").tostring() )
					image.SetAlphaData(pilimage.convert("RGBA").tostring()[3::4])
					faceBitmap = image.ConvertToBitmap() 
				except:
					## Some new error that I have not caught before has happened.
					## It may also be a bad sub-face from a ttc font.
					## Draw error message into the memDc
					memDc.SetTextForeground( fcol )
					txt=_("This text cannot be drawn. Hey, it happens...")
					memDc.SetFont( wx.Font( fpsys.config.points, family=wx.SWISS, style=wx.ITALIC, weight=wx.NORMAL))
					memDc.DrawText( txt, 10, y+2)
				else: #no error happened, we carry on.
					## Place it into the main image, down a tad so it looks better.
					facex = 5
					if i > 0: facex *= 2 # Shift sub-faces over a little
					## Draw the face into the memDc
					memDc.DrawBitmap( faceBitmap, facex, y + 4, True )
				
				## Postion 
				texty = y + glyphHeight + 8

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
				y = y + glyphHeight +  self.spacer
					
				## Goto next face, if any.
				i += 1			
		
		## Record the calculated height
		self.height = totheight

		## Special message
		if self.fitem.inactive:
			memDc.SetFont( wx.Font(11,family=wx.SWISS, style=wx.NORMAL, weight=wx.NORMAL))
			memDc.DrawText( self.fitem.activeInactiveMsg, 10, self.height-20 )

		## Draw the tick/cross if it's not a FILE_NOT_FOUND font (can't be found)
		## NB: FILE_NOT_FOUND is not available for installation!
		if self.fitem.badstyle != "FILE_NOT_FOUND":
			if self.fitem.ticked:
				memDc.DrawBitmap(self.TICKMAP, 20, 5, True)
			
		## Now a dividing line
		memDc.SetPen( wx.Pen( (200,200,200),1 ) )#black, 1 ) ) 
		memDc.DrawLine( 0, self.height-1, maxwidth, self.height-1 )



	def setStyle( self ):
		'''Set a copy of the styles key and alter colours as needed.'''
		# InfoFontItem does not use this, all others do.
		if self.fitem.badfont:
			self.style=Fitmap.styles[self.fitem.badstyle].copy() #damn! this was tricky!
			if self.fitem.inactive:
				self.style['fcol'] = Fitmap.styles['INACTIVE']['fcol']
				# Dim the colour of the badfont to match look of other inactive fitems
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


	#TODO : Pre-calc all these colours.

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

	def bottomFadeEffect( self, dc, height, width, step=1.12):
		"""
		Baptiste's idea! New implementation : June 2009
		 "Now a dividing gradient, you can say "wow" ;-)"
		 Donn says, "..Wow!" :-D   
		
		It goes from backcol and darkens it a little as it draws downwards.
		"""

		if self.fitem.inactive: step=1.08 #inactive fonts get a lighter colour.
		
		col = self.style["backcol"] #from
		hsv = self.rgb_to_hsv(col) 
		tob=self.hsv_to_rgb((hsv[0],hsv[1],hsv[2]/step)) #to a darker brightness.
		sy=height-self.gradientheight
		rect=wx.Rect(0, sy, width, self.gradientheight)
		dc.GradientFillLinear( rect, col, tob, nDirection=wx.SOUTH )


	def drawInfoOrError( self, w,h, isinfo=False ):
		"""
		Draw the Info Font block, or an Error message block. Much clearer than it was before.
		"""
		memDc=self.makeBlankDC( w, h, self.style['backcol'])
		if not isinfo:
			self.bottomFadeEffect( memDc, self.minHeight, self.width )
	
		icon = self.style['icon']
		if icon:
			Icon = eval("self.FVP." + icon)
			ix,iy = (6,15) if isinfo else (2,3)
			memDc.DrawBitmap(Icon,ix,iy,True)

		textTup = self.fitem.InfoOrErrorText()
		
		memDc.SetTextForeground( self.style['fcol'])
		
		memDc.SetFont( wx.Font(12, family=wx.SWISS, style=wx.NORMAL, weight=wx.BOLD))
		tx,ty = (46,15) if isinfo else (32 ,15)
		memDc.DrawText( textTup[0], tx, ty)
		
		memDc.SetFont( wx.Font(7, family=wx.SWISS, style=wx.NORMAL, weight=wx.NORMAL))
		tx,ty = (46,38) if isinfo else (8 ,38)
		memDc.DrawText( textTup[1], tx, ty)

		return memDc

