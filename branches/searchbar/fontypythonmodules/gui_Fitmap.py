import wx
import colorsys

import wx.lib.statbmp
import fontcontrol
import fpsys # Global objects
from pubsub import *
from wxgui import ps

class Fitmap(wx.lib.statbmp.GenStaticBitmap):
	"""
	This class is a bitmap of a TTF font - it detects a click and 
	also displays itself with other information below it.
	"""
	styles={
			'FILE_NOT_FOUND':
				{
					'backcol': (255,214,57),
					'fcol'   : "black", #fcol is forecol for fatfont
					'bcol'   : "white", #bcol is backcol for fatfont
					},
			'PIL_SEGFAULT_ERROR':
				{
					'backcol': (255,116,57),
					'fcol'   : "black",
					'bcol'   : "white"
					},
			'PIL_IO_ERROR':
				{
					'backcol': (255,116,107),
					'fcol'   : "black",
					'bcol'   : "white"
					},
			'PIL_UNICODE_ERROR':
				{
					'backcol': (255,116,136),
					'fcol'   : "black",
					'bcol'   : "white"
					},
			'PIL_CANNOT_RENDER':
				{
					'backcol': (255,116,193),
					'fcol'   : "black",
					'bcol'   : "white"
					},
			'ACTIVE':
				{
					'backcol': (255,255,255),
					'fcol'   : "black",
					'bcol'   : (200,200,200)
				},
			'INACTIVE':
				{
					'backcol': (254,154,36),
					'fcol'   : "gray",
					'bcol'   : "white" 
				},
			'INFO_FONT_ITEM':
				{
					'backcol': (255,255,255),
					'fcol'   : "black"
				}

			}

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
		self.Bind(wx.EVT_MIDDLE_UP, self.__onMiddleClick)	
		
		## Redraw event
		self.Bind(wx.EVT_PAINT,  self.__onPaint) 
		
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

	def __onMiddleClick(self, event):
		ps.pub( menu_settings, None )

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

	def prepareBitmap( self ):
		"""
		This is where all the drawing code goes. It gets the font rendered
		from the FontItems (via PIL) and then draws a single Fitmap.
		"""
		## Is this a normal FontItem, or an InfoFontItem?
		## InfoFontItem is a fake font item for the purposes
		## of saying "There are no fonts to see here."
		if isinstance( self.fitem, fontcontrol.InfoFontItem ):
			style=Fitmap.styles['INFO_FONT_ITEM']
			self.drawInfoOrError(  self.width, self.minHeight, style )
			return # Just get out.
			
		## Normal FontItem object
		spacer = 38 # Gap below each font bitmap
		
		
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
		
		if self.fitem.badfont:
			## We have a badstyle to help us differentiate these.
			style=Fitmap.styles[self.fitem.badstyle]
			memDc=self.drawInfoOrError(  self.width, self.minHeight, style )

			## Record the calculated height
			self.height = self.minHeight
			
		## It's *not* a badfont
		else:
			## Make one big bitmap to house one or more faces (subfaces)
			memDc=self.makeBlankDC( maxwidth, totheight, (255,255,255) )
			if self.fitem.inactive: 
				fcol = Fitmap.styles['INACTIVE']['fcol']
				bcol = Fitmap.styles['INACTIVE']['bcol']
			else: 
				fcol = Fitmap.styles['ACTIVE']['fcol']
				bcol = Fitmap.styles['ACTIVE']['bcol']		

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
					self.bottomFadeEffect( memDc, totheight, maxwidth, (255,255,255) )
				
				## Postion 
				texty = y + glyphHeight + (spacer/8)

				## Now draw the text showing the font name/family/style.
				## -- suggested by Chris Mohler.
				## Prep the text to show "font family name (font file name)"
				## Added Style info 3 Dec 2006:			
				txt = "%s - %s - [%s]" % (self.fitem.family[i], self.fitem.style[i], self.name)
				memDc.SetTextForeground( fcol )
				memDc.SetFont( wx.Font( 8, family=wx.SWISS, style=wx.NORMAL, weight=wx.NORMAL))
				memDc.DrawText( txt, 16, texty)
						
				## Move TOP down to next BOTTOM (for next sub-face)
				y = y + glyphHeight +  spacer
					
				## Goto next face, if any.
				i += 1			
		
			## Record the calculated height
			self.height = totheight

		## Special message
		if self.fitem.inactive:
			self.fatFont( memDc, 10, self.height-20, Fitmap.styles['INACTIVE']['fcol'],Fitmap.styles['INACTIVE']['bcol'], 10, wx.NORMAL, self.fitem.activeInactiveMsg )		

		## Draw the tick/cross if it's not a FILE_NOT_FOUND font (can't be found)
		if self.fitem.badstyle != "FILE_NOT_FOUND":
			if self.fitem.ticked:
				memDc.DrawBitmap(self.TICKMAP, 20, 5, True)
			
		## Now a dividing line
		memDc.SetPen( wx.Pen( (0,0,0), 2 ) ) 
		memDc.SetBrush( wx.TRANSPARENT_BRUSH ) 
		memDc.DrawLine( 0, self.height-1, maxwidth, self.height-1 )

	def makeBlankDC( self, w, h, backcol ):
		bitmap = wx.EmptyImage( w,h ).ConvertToBitmap()
		memDc = wx.MemoryDC()
		memDc.SelectObject( bitmap )
		memDc.SetBackground( wx.Brush( backcol, wx.SOLID) )
		memDc.Clear()		
		self.bitmap = bitmap #record this for the init
		return memDc

	def bottomFadeEffect( self, memDc, liney, width, col ):
		"""
		Baptiste's idea! New implementation : June 2009
		 "Now a dividing gradient, you can say "wow" ;-)"
		 Donn says, "..Wow!" :-D   
		
		It goes from col and darkens it to almost black.
		"""
		memDc.SetBrush ( wx.TRANSPARENT_BRUSH ) 
		##Go from int colour to float colour (0 to 1 range)
		sr = col[0]/255.0
		sg = col[1]/255.0
		sb = col[2]/255.0
		## A wee generator to provide a range of float numbers
		def frange(start,end):
			step = 0.01 #small steps so we get a visible band
			v = start
			while True:
				if v > end:
					raise StopIteration
				yield v
				v += step
		## get the HSV of the incoming col.
		hsv = colorsys.rgb_to_hsv(sr,sg,sb)
		tob=hsv[2] # I want the brightness
		## Start at 0.8 (fairly light) and go to the brightness
		for bright in frange( 0.8, tob ):
			## get the rgb of that hsv
			rgb=colorsys.hsv_to_rgb( hsv[0],hsv[1],bright )
			## go back to int colours (0 to 255)
			rgb=( rgb[0]*255,rgb[1]*255,rgb[2]*255)
			## draw yonder lines.
			memDc.SetPen( wx.Pen( rgb, 1 ) ) 
			memDc.DrawLine( 0, liney, width, liney )
			liney -= 1

	def fatFont(self, dc, x, y, fcol, bcol, points, weight, txt):
		"""
		Draw a string with a backdrop highlight. Makes it "fat".
		I suppose I should draw one string, then try blitting it around 
		rather than DrawTexting it. Later ...
		"""
		dc.SetFont(wx.Font(points, family=wx.SWISS, style=wx.NORMAL, weight=weight))
		
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



	def drawInfoOrError( self, w,h, style ):
		"""
		Draw the Info Font block, or an Error message block. Much clearer than it was before.
		"""
		memDc=self.makeBlankDC( w, h, style['backcol'])
		self.bottomFadeEffect( memDc, self.minHeight, self.width, style['backcol'] )
		
		textTup = self.fitem.InfoOrErrorText()
		
		memDc.SetTextForeground(style['fcol'])
		
		memDc.SetFont( wx.Font(12, family=wx.SWISS, style=wx.NORMAL, weight=wx.BOLD))
		memDc.DrawText( textTup[0], 10, 15)
		
		memDc.SetFont( wx.Font(7, family=wx.SWISS, style=wx.NORMAL, weight=wx.NORMAL))
		memDc.DrawText( textTup[1], 10, 34)

		return memDc

