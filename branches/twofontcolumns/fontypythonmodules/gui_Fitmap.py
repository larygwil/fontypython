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
import subprocess,os
import threading

import wx.lib.statbmp
import fontcontrol
import fpsys # Global objects
from pubsub import *
from wxgui import ps

ndc=(200,190,183) # No Draw Color: colour of background for the fonts I can't draw
ndi=(227,226,219) # No Draw Inactive.
black=(0,0,0)
white=(255,255,255)

class OverOutSignal(object):
	'''
	Signal an external function when a state has CHANGED from
	True to False or vice-vera
	'''
	def __init__( self, func_to_signal ):
		self.announce = func_to_signal
		self.state = False
		self.last_state = False
	def __changed( self ):
		if self.state != self.last_state:
			self.last_state = self.state
			return True
		return False
	def set( self, truth ):
		if self.state == truth:	return
		self.state = truth
		if self.__changed(): self.announce()


class Pencil(object):
	"""
	Used to store drawing code for DrawText and DrawBitmap.
	I make them and store them in a list. This gives an
	ordering in time and overlapping too.
	I can loop and draw them all in one go.
	"""
	def __init__( self, x, y ):
		self.x = x; self.y = y
	def Draw(self, memdc):
		pass

class FontPencil(Pencil):
	def __init__( self, x, y, font, txt, fcol ):
		Pencil.__init__(self, x, y)
		self.font = font
		self.txt = txt
		self.fcol = fcol
	def Draw(self, memdc):
		memdc.SetTextForeground( self.fcol )
		memdc.SetFont( self.font )
		memdc.DrawText( self.txt, self.x, self.y )

class BitmapPencil(Pencil):
	def __init__( self, x, y, bitmap ):
		Pencil.__init__(self, x, y)
		self.bitmap = bitmap
	def Draw(self, memdc):
		memdc.DrawBitmap( self.bitmap, self.x, self.y, True )


class Fitmap(wx.lib.statbmp.GenStaticBitmap):
	"""
	This class is a bitmap of a TTF font - it detects events and
	displays itself.

	Sept 2009
	Added code to adjust top-left of displayed sample text.

	Oct 2009
	Added a 'button' to open a character map viewer.
	"""

	## This class-level dict is a kind of "style sheet" to use in fitmap drawing.
	styles={
			'FILE_NOT_FOUND': #Needs purging
				{
					'backcol': (255,214,57),
					'fcol'   : black,
					'bcol'   : white,
					'icon'	 : "NOT_FOUND",
					'ndi'    : ndi
					},
			'PIL_SEGFAULT_ERROR':
				{
					'backcol': (152,147,157), #255,140,20),
					'fcol'   : black,
					'bcol'   : white,
					'icon'	 : "SEGFAULT",
					'ndi'	 : (216,193,193)
					},
			'PIL_IO_ERROR':
				{
					'backcol': ndc,
					'fcol'   : black,
					'bcol'   : white,
					'icon'	 : "NO_DRAW",
					'ndi'	 : ndi
					},
			'PIL_UNICODE_ERROR':
				{
					'backcol': ndc,
					'fcol'   : black,
					'bcol'   : white,
					'icon'	 : "NO_DRAW",
					'ndi'	 : ndi
					},
			'PIL_CANNOT_RENDER':
				{
					'backcol': ndc,
					'fcol'   : black,
					'bcol'   : white,
					'icon'	 : "NO_DRAW",
					'ndi'	 : ndi
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
					'ndi'    : ndi
				},
			'INFO_FONT_ITEM':
				{
					'backcol': white,
					'fcol'   : black,
					'icon'	 : "INFO_ITEM",
				}
			}
	MIN_FITEM_WIDTH = 450
	MIN_FITEM_HEIGHT = 70
	SPACER = 35 # Gap below each font bitmap

	def __init__( self, parent, fitem ) :

		#print pos
		self.name = fitem.name
		#print self.name

		self.fitem = fitem

		Fitmap.styles['INFO_FONT_ITEM']['backcol']=parent.GetBackgroundColour()
		self.FVP = parent.parent #The Font View Panel
		self.TICKMAP = parent.parent.TICKMAP
		self.TICKSMALL = parent.parent.TICKSMALL


		self.style = {} #Temporary space for style of fitem while drawing. It's a copy of one key from Fitem.styles

		# Some values for drawing
		self.gradientheight = 50

		#self.width = parent.width # Get it from the scrollFontViewPanel.
		#self.width = parent.width/2 # Get it from the scrollFontViewPanel.

		self.widestpilimage = 0 # July 2016: The final, drawn, width of this fitem.

		## The charmap button
		self.CHARMAP_BUTTON_OVER = self.FVP.BUTTON_CHARMAP_OVER
		self.CHARMAP_BUTTON_OUT = self.FVP.BUTTON_CHARMAP
		## Point to the handler for the signal re charmap button
		self.cmb_overout = OverOutSignal( self.charmap_button_signal )


		## Go draw the fitmap into a memory dc
		self.drawlist = []
		self.dcw = []
		self.bitmap = None
		self.prepareBitmap()
		sz = (self.bitmap.GetWidth(), self.bitmap.GetHeight())

		## Now I can calc the y value of the button.
		self.cmb_rect=wx.Rect(0,sz[1]-40,19,32)
		self.height =  0

		## init my parent class 
		## This also sets the SIZE of the fitmap widget.
		## Calling DoGetBestSize on it will return that size.
		self.gsb = wx.lib.statbmp.GenStaticBitmap.__init__(self, parent, -1, self.bitmap, (0,0), sz)

		## Fitmap's over out signal
		self.overout = OverOutSignal( self.overout_signal )

		## Very cool event, gives us life!
		self.Bind(wx.EVT_LEFT_UP,self.onClick)
		self.Bind(wx.EVT_MIDDLE_UP, self.onMiddleClick)
		#self.Bind(wx.EVT_LEFT_DCLICK, self.onDClick)
		self.Bind( wx.EVT_MOTION, self.onHover )
		self.Bind( wx.EVT_LEAVE_WINDOW, self.onLeave)

		## Redraw event
		self.Bind(wx.EVT_PAINT,  self.onPaint)

		## Get cursors setup
		self.CURSOR = wx.StockCursor( wx.CURSOR_ARROW )
		if fpsys.state.action in ("REMOVE", "APPEND"):
			self.CURSOR = wx.StockCursor( wx.CURSOR_HAND )
		if self.fitem.badstyle == "FILE_NOT_FOUND":
			self.CURSOR = wx.StockCursor( wx.CURSOR_ARROW )
		if self.fitem.inactive:
			self.CURSOR = wx.StockCursor( wx.CURSOR_ARROW )



	def __aFont( self, points, style=wx.NORMAL, weight=wx.NORMAL, encoding = wx.FONTENCODING_DEFAULT ):
		return wx.Font( points, fpsys.DFAM, style, weight, encoding=encoding )


	def usePencils(self, h):
		W = max(self.dcw)
		## Make the DC- now that we have all the widths!
		memDc=self.makeBlankDC( W, h, white )
		## Draw it all - via the pencils
		for pencil in self.drawlist:
			pencil.Draw(memDc)
		return memDc


	def openCharacterMap( self ):
		fi=self.fitem
		dirname = os.path.basename( fi.glyphpaf )
		dest = os.path.join(fpsys.iPC.userFontPath(), dirname )

		## I don't want to hold an fitem in the thread to come, so I will
		## take the essential info out and make a tuple instead:
		## (This is mere superstition and ignorance, I fear threads :) )

		argstup=(fi.glyphpaf, dest, self.fitem.family[0],fpsys.config.points )

		## Never done threading before. Not really sure if this is kosher...

		#~ MICHAEL 4.2011:
		#~ I tried threading myself, too. But I don't really understand it
		#~ down to the present day. As I see "Popen" in charmaps.py/Run
		#~ starts his own thread, so we don`t need to make assurance double sure.
		#~ By the way, this push gucharmap to work as we want.

		self.run(*argstup)

		#~ thread = threading.Thread(target=self.run, args=argstup)
		#~ thread.setDaemon(True)
		#~ thread.start()

	def run(self, *args):
		'''
		Uses the instance (held in fpsys.config) of the classes in charmaps.py.
		'''
		iCM = fpsys.config.CMC.GetInstance()
		iCM.OpenApp( *args )
		iCM.Cleanup( )

	def onMiddleClick(self, event):
		ps.pub( menu_settings, None )

	def can_have_button( self ):
		'''
		Because I just can't guarantee that there is a family name
		and because bad fonts that can't draw (but do not segfault)
		are so rare that I can't bloody find any to test with (grrr)
		I make the sweeping fiat that no badfonts will get a button.

		Other fitems like info and FILE_NOT_FOUND don't get buttons.
		'''
		if not fpsys.config.CMC.APPS_ARE_AVAILABLE: return False
		if isinstance( self.fitem, fontcontrol.InfoFontItem ): return False
		if self.fitem.badstyle == "FILE_NOT_FOUND": return False
		if not self.fitem.family: return False
		return True

	def onHover( self, e ):
		if not self.can_have_button():
			self.overout.set ( True )
			return
		if self.cmb_rect.Contains( e.GetPositionTuple() ):
			self.cmb_overout.set( True )
			self.overout.set( False ) #Not 'on' fitmap
		else:
			self.cmb_overout.set ( False )
			self.overout.set( True )

	def charmap_button_signal( self ):
		if self.cmb_overout.state:
			self.SetCursor(wx.StockCursor(wx.CURSOR_MAGNIFIER))
		self.Refresh() # Force onPaint()

	def overout_signal( self ):
		if self.overout.state:
			self.SetCursor( self.CURSOR )

	def onLeave(self, event):
		'''
		Catch the leave event for set the charmap button off,
		if the pointer goes out on the left edge.
		'''
		self.onHover(event)

	def onClick(self, event) :
		if self.cmb_overout.state and self.can_have_button():
			self.openCharacterMap()
			return

		if fpsys.state.cantick and not self.fitem.inactive:
			self.fitem.ticked = not(self.fitem.ticked)
			self.prepareBitmap() # This only redraws a single font item.
			self.Refresh()  #forces a redraw.
 
			## Inc or dec a counter depending on the tickedness of this item
			if self.fitem.ticked: fpsys.state.numticks += 1
			if not self.fitem.ticked: fpsys.state.numticks -= 1
			ps.pub(toggle_main_button)

	def onPaint(self, event):
		"""
		Dump the bitmap to the screen.
		"""
		#sz = self.GetClientSize()
		#dc = wx.PaintDC(self)

		if self.bitmap:
			## Create a buffered paint DC.  It will create the real
			## wx.PaintDC and then blit the bitmap to it when dc is
			## deleted.  
			dc = wx.BufferedPaintDC(self, self.bitmap, wx.BUFFER_VIRTUAL_AREA)

			if not self.can_have_button(): return

			# Draw the charmap button
			x,y = self.cmb_rect[0],self.cmb_rect[1]
			if self.cmb_overout.state:
				dc.DrawBitmap( self.CHARMAP_BUTTON_OVER, x, y, True )
			else:
				dc.DrawBitmap( self.CHARMAP_BUTTON_OUT, x,y, True )

	def CalculateTopLeftAdjustments(self, image, i, pilimage):
		## Sept 2009
		## Find the first pixel from the top-left of the image (if it's not stored)
		## Using this pixel as the x,y I can draw fonts from where their actual data
		## begins and not where the pilimage *thinks* it does (leaving big white spaces
		## to the left of many fonts.)

		if fpsys.config.ignore_adjustments: return 0,0
		wx.BeginBusyCursor()
		if not self.fitem.top_left_adjust_completed:
			W,H = pilimage.size
			fx=fy=0
			esc = False
			# Scan ACROSS WIDTH and repeatedly DOWN looking for a pixel.
			for tx in xrange(W):
				for ty in xrange(H):
					ap=image.GetAlpha(tx,ty)
					#image.SetRGB(tx,ty,0,255,0)
					#image.SetAlpha(tx,ty,255)
					if ap != 0: #Found X coord, let's kill both loops
						fx=tx
						esc = True
						break
				if esc: break #uses fact that 0 is False
			# Scan DOWN the HEIGHT and repeatedly ACROSS.
			esc = False
			for ty in xrange(H):
				for tx in xrange(W):
					ap=image.GetAlpha(tx,ty)
					if ap != 0:
						fy=ty # Found Y coord
						esc = True
						break
				if esc: break
			self.fitem.fx[i]=fx
			self.fitem.fy[i]=fy
			# If we are at the end of the number of faces (for ttc files this is > 0) then flag it true
			if i+1 == self.fitem.numFaces: self.fitem.top_left_adjust_completed = True
		else:
			## Fetch the values from the cache list.
			fx,fy = (self.fitem.fx[i], self.fitem.fy[i])
		wx.EndBusyCursor()
		return fx,fy



	def __mf( self, wxfont, txt ):
		"""
		Measure a line of text in a given font. Return a wx.Size
		"""
		## Do we have a cached size for this txt?
		if txt in self.fitem.textExtentsDict:
			return self.fitem.textExtentsDict[txt] #yep!

		dc = wx.ScreenDC()
		dc.SetFont(wxfont)
		try:
			sz = dc.GetTextExtent(txt)
		except:
			sz = (Fitmap.MIN_FITEM_WIDTH,Fitmap.MIN_FITEM_HEIGHT)
		self.fitem.textExtentsDict[txt] = sz # cache it in my parent
		return sz


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
			self.drawInfoOrError( isinfo=True )
			self.usePencils(Fitmap.MIN_FITEM_HEIGHT)
			return # Just get out.

		## Get a list of pilimages, for each subface: Some fonts 
		## have multiple faces, and their heights.
		## (For example TTC files.)
		## REMEMBER: This loop is all FOR THIS ONE FONT ITEM.
		## It only supplies pilimages for fonts it could open and
		## render. So this font may indeed have nothing in the pilList[]
		## after this loop.
		pilList=[]
		totheight = 0
		maxwidth = [Fitmap.MIN_FITEM_WIDTH]

		for pilimage in self.fitem.generatePilFont( ):
			pilList.append( pilimage )
			totheight += pilimage.size[1] + Fitmap.SPACER
			maxwidth.append(pilimage.size[0])
		## Limit the minimum we allow.
		if totheight < Fitmap.MIN_FITEM_HEIGHT:
			totheight = Fitmap.MIN_FITEM_HEIGHT

		self.widestpilimage = max(maxwidth) # find it.

		## BADFONT cases
		##  Badfonts are still available for installation, it's just that I can't
		##  display their glyph or fam/style info (until PIL is patched).

		self.setStyle() #Go set the self.style
		fcol = self.style['fcol']
		bcol = self.style['bcol']

		if self.fitem.badfont:
			## We have a badstyle to help us differentiate these.
			totheight = Fitmap.MIN_FITEM_HEIGHT
			if self.fitem.inactive: totheight += 5 #Need more space
			self.drawInfoOrError( )

		## It's *not* a badfont
		else:
			if self.fitem.inactive:
				totheight += (Fitmap.SPACER-20) #want room for 'is in pog' message.

			#TODO self.bottomFadeEffect( memDc, totheight, maxwidth )

			mainy = i = 0

			for pilimage in pilList:
				pilwidth, glyphHeight = pilimage.size
				state = 0
				try:
					## Get the data from PIL into wx.
					## Now with alpha! Thanks to:
					## http://nedbatchelder.com/blog/200801/truly_transparent_text_with_pil.html
					## http://wiki.wxpython.org/WorkingWithImages
					image=None
					#image = apply( wx.EmptyImage, pilimage.size )
					image = wx.EmptyImage(*pilimage.size)

					## June 25, 2016
					## PIL has changed. It now requires tobytes()
					## not tostring(). 
					## Since I don't want to break on older installs of PIL,
					## I will use a try block here. 
					## TODO: Test for a new min PIL version and kill this try:
					try:
						#Old style:
						image.SetData( pilimage.convert( "RGB").tostring() )
						image.SetAlphaData(pilimage.convert("RGBA").tostring()[3::4])
					except:
						#New style
						image.SetData( pilimage.convert( "RGB").tobytes() )
						image.SetAlphaData(pilimage.convert("RGBA").tobytes()[3::4])

					fx,fy = self.CalculateTopLeftAdjustments( image, i, pilimage )

					faceBitmap = image.ConvertToBitmap()
				except:
					#debug: raise
					## Some new error that I have not caught before has happened.
					## It may also be a bad sub-face from a ttc font.
					txt=_("This text cannot be drawn. Hey, it happens...")
					f = self.__aFont(fpsys.config.points, style=wx.ITALIC)
					w = self.__mf(f, txt)[0]
					x = 10 #error x coord
					y = mainy+2 # y coord
					self.dcw.append( w + (2*x)) #x across and a gap on end
					self.drawlist.append( FontPencil(x, y, f, txt, fcol))
				else:
					## Place it into the main image, down a tad so it looks better.
					x = 10
					if i > 0: x *= 2 # Shift sub-faces over a little
					## Draw the face into the memDc
					x = x-fx
					y = mainy-fy
					self.dcw.append( 2*x + self.widestpilimage )
					self.drawlist.append( BitmapPencil(x,y,faceBitmap))

				## The font name/fam/style : fnfs
				txt = "%s - %s - [%s]" % (self.fitem.family[i], self.fitem.style[i], self.name)
				f = self.__aFont( 8, encoding=wx.FONTENCODING_DEFAULT)
				w = self.__mf( f, txt )[0]
				## Postion 
				x = 28
				y = mainy + glyphHeight + 8
				self.dcw.append( w + 2*x )
				self.drawlist.append( FontPencil( x, y, f, txt, fcol ) )

				## Move TOP down to next BOTTOM (for next sub-face)
				mainy += glyphHeight +  Fitmap.SPACER

				## Goto next face, if any.
				i += 1

		## Record the calculated height
		self.height = totheight

		## Special message
		if self.fitem.inactive:
			x,y=(25,self.height-20) if self.fitem.badfont else (48,self.height-26)
			self.drawlist.append( BitmapPencil( x-16, y-1, self.TICKSMALL ) )

			txt = self.fitem.activeInactiveMsg
			f = self.__aFont( 11 )
			w = self.__mf(f,txt)[0]
			self.dcw.append( w + x*2 )
			self.drawlist.append(FontPencil(x,y,f,txt,fcol))

		## Draw the tick/cross if it's not a FILE_NOT_FOUND font (can't be found)
		## NB: FILE_NOT_FOUND is not available for installation!
		if self.fitem.badstyle != "FILE_NOT_FOUND":
			if self.fitem.ticked:
				self.drawlist.append( BitmapPencil( 20, 5, self.TICKMAP ) )

		## Make one big bitmap to house one or more faces (subfaces)
		##
		## NOTE: By drawing into memDc, we are drawing into self.bitmap
		##
		#W = max(self.dcw)

		## Make the DC- now that we have all the widths!
		#memDc=self.makeBlankDC( W, totheight, white )
		memDc = self.usePencils( totheight )
		## Draw it all - via the pencils
		#for pencil in self.drawlist:
		#	pencil.setDc(memDc)
		#	pencil.Draw()

		## Now a dividing line
		memDc.SetPen( wx.Pen( (180,180,180),1 ) )#black, 1 ) ) 
		memDc.DrawLine( 0, self.height-1, self.widestpilimage, self.height-1 )

	def setStyle( self ):
		'''Set a copy of the styles key and alter colours as needed.'''
		# InfoFontItem does not use this, all others do.
		if self.fitem.badfont:
			self.style=Fitmap.styles[self.fitem.badstyle].copy() #damn! this was tricky!
			if self.fitem.inactive:
				## July 2016
				## =========
				## Happened on cases where 'ndi' key was not in styles dict. 
				## Added them in.
				#print "bad:", self.fitem.name
				#print "style:", self.fitem.badstyle
				self.style['fcol'] = Fitmap.styles['INACTIVE']['fcol']
				self.style['backcol'] = Fitmap.styles[self.fitem.badstyle]['ndi'] #ndi = No Draw Inactive
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
		backcol="red"
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

	def bottomFadeEffect( self, dc, height, width, step=1.13):
		#TODO
		return
		"""
		Baptiste's idea! New implementation : June 2009
		"Now a dividing gradient, you can say "wow" ;-)"
		Donn says, "..Wow!" :-D

		It goes from backcol and darkens it a little as it draws downwards.
		"""

		if self.fitem.inactive:
			return
			#step=1.08 #inactive fonts get a lighter colour.

		col = self.style["backcol"] #from
		hsv = self.rgb_to_hsv(col)
		tob=self.hsv_to_rgb((hsv[0],hsv[1],hsv[2]/step)) #to a darker brightness.
		sy=height-self.gradientheight
		rect=wx.Rect(0, sy, width, self.gradientheight)
		dc.GradientFillLinear( rect, col, tob, nDirection=wx.SOUTH )


	def drawInfoOrError( self, isinfo=False ):
		"""
		Draw the Info Font block, or an Error message block. Much clearer than it was before.
		"""
		#import pdb; pdb.set_trace()

		## This icon is not as wide as the text. I don't need to put it into dcw
		icon = self.style['icon']
		if icon:
			Icon = self.FVP.__dict__[icon]
			ix,iy = (6,10) if isinfo else (2,3)
			self.drawlist.append( BitmapPencil( ix, iy, Icon ) )

		## Prep and measure the texts to be drawn. Add them to drawlist.
		fcol = self.style['fcol']

		f1 = self.__aFont(12,weight=wx.BOLD)
		f2 = self.__aFont(7)

		textTup = self.fitem.InfoOrErrorText()

		## Measure text 1
		tx,ty = (46,15) if isinfo else (38 ,13)
		w = self.__mf(f1, textTup[0])[0]
		self.dcw.append(w + 2*tx)
		self.drawlist.append( FontPencil( tx, ty, f1, textTup[0], fcol ) )

		## Measure text 2
		tx,ty = (46,40) if isinfo else (5 ,40)
		w = self.__mf(f2, textTup[1])[0]
		self.dcw.append(w + 2*tx)
		self.drawlist.append( FontPencil( tx, ty, f2, textTup[1], fcol ) )
