import wx
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
		
		## If this is not a FILE_NOT_FOUND then allow the cursor to change
		## FILE_NOT_FOUND means we have a glyphpaf but no match on the drive.
		## This means the Pog should be purged.
		if self.fitem.badstyle != "FILE_NOT_FOUND":
			if fpsys.state.action == "REMOVE":
				self.SetCursor( wx.StockCursor( wx.CURSOR_PENCIL ) )
			elif fpsys.state.action == "APPEND":
				if not self.fitem.inactive:
					self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))

	def __onMiddleClick(self, event):
		ps.pub( menu_settings, None )
		
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
				fadecol = (180,0,0)
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
					self.__fatFont(memDc, 16, texty, fcol, "white", 8, wx.NORMAL, txt)
					
					## Special message
					if self.fitem.inactive:
						self.__fatFont\
						(memDc, 16, texty + 14, "black", "white", 8, wx.NORMAL, self.fitem.msg)
						
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
		for q in xrange(0, 25):
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

		

