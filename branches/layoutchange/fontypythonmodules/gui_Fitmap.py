## Fonty Python Copyright (C) 2017 Donn.C.Ingle
## Contact: donn.ingle@gmail.com - I hope this email lasts.
##
## This file is part of Fonty Python.
## Fonty Python is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Fonty Python is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Fonty Python.  If not, see <http://www.gnu.org/licenses/>.

import wx
import colorsys
import subprocess,os
import threading

import wx.lib.statbmp
import fontcontrol
import fpsys # Global objects
from pubsub import *
from wxgui import ps

##Oct 2017 - Moved the PIL draw code into Fitmap.
from PIL import Image, ImageFont, ImageDraw

import collections

ndc=(200,190,183) # No Draw Color: colour of background for the fonts I can't draw
ndi=(227,226,219) # No Draw Inactive => "ndi"
black=(0,0,0)
white=(255,255,255)


class OverOutSignal(object):
    """
    Signal an external function when a state has CHANGED from
    True to False or vice-vera
    """
    def __init__( self, func_to_signal ):
        self.announce = func_to_signal
        self.truthstate = False
    def set( self, newtruth ):
        if self.truthstate == newtruth: return # no change
        # implies there's now an actual change, thus:
        self.truthstate = newtruth # Orwell would be proud! :D
        self.announce()



class Pencil(object):
    """
    Used to store drawing code for DrawText and DrawBitmap.
    I make them and store them in a list. This gives an
    ordering in time and overlapping too.
    I can loop and draw them all in one go.
    """
    def __init__( self, id, x = 0, y = 0, fcol = (0,0,0)):
        self.id = id; self.x = x; self.y = y
        self._fcol = fcol
    def getwidth(self): return 0 
    def draw(self, memdc): pass


class EmptyPencil(Pencil):
    def __init__(self,id):
        Pencil.__init__(self,id)


class TextPencil(Pencil):
    _text_extents_dict = {}
    def __init__( self, id, txt, x = 0, y = 0, fcol = (0,0,0), points = 8,
                    style = wx.NORMAL, weight = wx.NORMAL ):
        Pencil.__init__(self, id, x = x, y = y, fcol = fcol)
        self.txt = txt
        self.font =  wx.Font( points, fpsys.DFAM, style, weight, encoding=wx.FONTENCODING_DEFAULT )

        ## Measure a line of text in my font. Return a wx.Size
        ## Cache these widths in Pencil class variable, so that
        ## future identical strings can avoid work.

        ## Do we have a cached measurement for this txt?
        #print "*** MEASURING:", self.txt
        if not self.txt in TextPencil._text_extents_dict:
            dc = wx.ScreenDC()
            dc.SetFont( self.font )
            try:
                sz = dc.GetTextExtent( self.txt )
                #print "measured as:",sz
            except:
                sz = (Fitmap.MIN_FITEM_WIDTH,Fitmap.MIN_FITEM_HEIGHT)
            # cache it in the class
            TextPencil._text_extents_dict[self.txt] = sz

    def getwidth(self):
        #print u"##getwidth on '{}' is reporting width of {}".format(self.txt, TextPencil._text_extents_dict[self.txt][0])
        return TextPencil._text_extents_dict[self.txt][0]

    def getsize(self): 
        # returns a tuple
        return TextPencil._text_extents_dict[self.txt]

    def draw(self, memdc):
        #print self," txt is:", self.txt
        memdc.SetTextForeground( self._fcol )
        memdc.SetFont( self.font )
        memdc.DrawText( self.txt, self.x, self.y )



class BitmapPencil(Pencil):
    def __init__( self, id, x=0, y=0, bitmap=None):
        Pencil.__init__(self, id, x, y)
        self.bitmap = bitmap
    def getwidth(self): return self.bitmap.GetWidth()
    def draw(self, memdc):
        #print self
        #print self.bitmap
        memdc.DrawBitmap( self.bitmap, self.x, self.y, True )







class Fitmap(wx.lib.statbmp.GenStaticBitmap):
    """
    This class is a bitmap of a font - it detects events and
    displays itself.

    Sept 2009
    Added code to adjust top-left of displayed sample text.

    Oct 2009
    Added a 'button' to open a character map viewer.

    Sept/Oct 2017
    Lots of work. A total overhaul. Arguably worthless. Dunno.
    """

    ## This class-level dict is a kind of "style sheet" to use in fitmap drawing.
    styles={
            'FILE_NOT_FOUND':
                {
                    'backcol': (255,214,57),
                    'fcol'   : black,
                    'bcol'   : white,
                    'icon'   : "NOT_FOUND",
                    'ndi'    : ndi
                    },
            'PIL_SEGFAULT_ERROR':
                {
                    'backcol': (152,147,157), #255,140,20),
                    'fcol'   : black,
                    'bcol'   : white,
                    'icon'   : "SEGFAULT",
                    'ndi'    : (216,193,193)
                    },
            'PIL_IO_ERROR':
                {
                    'backcol': ndc,
                    'fcol'   : black,
                    'bcol'   : white,
                    'icon'   : "NO_DRAW",
                    'ndi'    : ndi
                    },
            'PIL_UNICODE_ERROR':
                {
                    'backcol': ndc,
                    'fcol'   : black,
                    'bcol'   : white,
                    'icon'   : "NO_DRAW",
                    'ndi'    : ndi
                    },
            'PIL_CANNOT_RENDER':
                {
                    'backcol': ndc,
                    'fcol'   : black,
                    'bcol'   : white,
                    'icon'   : "NO_DRAW",
                    'ndi'    : ndi
                    },
            'ACTIVE':
                {
                    'backcol': white,
                    'fcol'   : black,
                    'bcol'   : (200,200,200),
                    'icon'   : None,
                },
            'INACTIVE':
                {
                    'backcol': white,
                    'fcol'   : (98,98,98), #128,128,128), 
                    'bcol'   : white,
                    'icon'   : None,
                    'ndi'    : ndi
                },
            'INFO_FONT_ITEM':
                {
                    'backcol': white,
                    'fcol'   : black,
                    'icon'   : "INFO_ITEM",
                }
            }
    MIN_FITEM_WIDTH = 450
    MIN_FITEM_HEIGHT = 70
    SPACER = 35 # Gap below each font bitmap


    ## Used in state logic. See is_block and prepareBitmap
    blocks = {"A":1,"B":2}#,"C":4,"D":8}

    def __init__( self, parent, fitem ) :

        self.name = fitem.name

        self.fitem = fitem

        Fitmap.styles['INFO_FONT_ITEM']['backcol']=parent.GetBackgroundColour()

        self.FVP = parent.parent #The Font View Panel

        #self.TICKMAP = parent.parent.TICKMAP
        self.parent = parent
        self.TICKSMALL = parent.parent.TICKSMALL


        self.style = {} #Temporary space for style of fitem while drawing. It's a copy of one key from Fitem.styles

        # Some values for drawing
        self.gradientheight = 50


        self.face_image_stack = []
        self._inactive_images = {}

        # To keep all the pencils in a stack
        self.drawDict = collections.OrderedDict()

        self.height =  Fitmap.MIN_FITEM_HEIGHT
        self.width = 0

        self.history_dict = {}
        self.state = 0

        self.bitmap = None

        ## The charmap button
        self.CHARMAP_BUTTON_OVER = self.FVP.BUTTON_CHARMAP_OVER
        self.CHARMAP_BUTTON_OUT = self.FVP.BUTTON_CHARMAP
        ## Point to the handler for the signal re charmap button
        self.cmb_overout = OverOutSignal( self.charmap_button_signal )
        self.cmb_rect = None

        ## init my parent class 
        ## Give it a fake size. It has issues...
        wx.lib.statbmp.GenStaticBitmap.__init__(self, parent, -1, self.bitmap, size=(2,2))

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
        #if self.fitem.badstyle == "FILE_NOT_FOUND":
        #    self.CURSOR = wx.StockCursor( wx.CURSOR_ARROW )
        #if self.fitem.inactive:
        #    self.CURSOR = wx.StockCursor( wx.CURSOR_ARROW )

    def has_changed(self, key, something):
        """
        Sets the value and tests if it differs from
        the last value. 
        Returns: True or False
        (If first run, it sets and returns true)
        """
        if key not in self.history_dict:
            tf = True
        else:
            tf = self.history_dict[key] != something

        self.history_dict[key] = something
        return tf

    def determine(self):
        """
        Looking at very specific variables which 
        influence how we will draw the font bitmap.
        We OR the values onto state as we go.
        
        Because of the way History.differs works, on first 
        run, the state will be maxed, all blocks are on.
        """
        self.state = 0
        A = 1
        B = 2
        # A
        if self.has_changed("pointschanged", fpsys.config.points):
            self.state |= A | B
        # A
        if self.has_changed("textchanged", fpsys.config.text):
            self.state |= A | B
        # B
        if self.has_changed("activechanged", self.fitem.inactive):
            self.state |= B
        # C
        if self.has_changed("tickedchanged", self.fitem.ticked):
            self.state |= B
        # D
        if self.has_changed("tlchanged", fpsys.config.ignore_adjustments):
            self.state |= B

    def is_block(self, c):
        """
        This looks at the state and determines 
        which block it's in.
        E.g. if xx.is_block("A"):
        """
        print "state is:", self.state
        return self.state & Fitmap.blocks[c] == Fitmap.blocks[c]





    def accrue_width(self,n):
        self.width = max(self.width, n)

    def accrue_height(self,n):
        self.height = max(self.height, n)

    def addPencil(self, *pencils):
        # beware, this does not preserve the order of the
        # input list!
        d = dict((o.id, o) for o in pencils)

        self.drawDict.update(d)# {id:pencil})

    

    def bottomFadeEffect( self, dc, height, width, step=1.13):
        """
        Baptiste's idea! New implementation : June 2009
        "Now a dividing gradient, you can say "wow" ;-)"
        Donn says, "..Wow!" :-D

        It goes from backcol and darkens it a little as it draws downwards.
        """
        #TODO : Pre-calc all these colours.
        ctx = wx.GraphicsContext.Create(dc)
        b = ctx.CreateLinearGradientBrush(0,height,0,0,"#eeeeeeff", "#ffffffff")
        ctx.SetBrush (b)
        ctx.DrawRectangle(0,0,width,height)
        b = ctx.CreateLinearGradientBrush(width,0,width/2,0, "#ffffffff", "#ffffff00")
        ctx.SetBrush (b)
        ctx.DrawRectangle(0,0,width,height)

        return

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


        if self.fitem.inactive:
            return
            #step=1.08 #inactive fonts get a lighter colour.

        col = self.style["backcol"] #from
        hsv = self.rgb_to_hsv(col)
        tob=self.hsv_to_rgb((hsv[0],hsv[1],hsv[2]/step)) #to a darker brightness.
        sy=height-self.gradientheight
        rect=wx.Rect(0, sy, width, self.gradientheight)
        dc.GradientFillLinear( rect, col, tob, nDirection=wx.SOUTH )
        dc.GradientFillLinear( rect, "#ffffff", tob, nDirection=wx.SOUTH )



    def gen_info_or_badfont( self, isinfo = False ):
        """
        Draw the Info Font block, or an Error message block. Much clearer than it was before.
        """
        #Sept 2017: Move it all over by an offset
        offx = 20

        icon = self.style['icon']

        iconpencil = None
        if icon:
            Icon = self.FVP.__dict__[icon] #See gui_FontView.py ~line 97
            ix,iy = (6,10) if isinfo else (2,6)

            ix += offx
            iconpencil = BitmapPencil( "infoicon", ix, iy, Icon)

        ## Prep and measure the texts to be drawn. Add them to drawlist.
        fcol = self.style['fcol']

        textTup = self.fitem.InfoOrErrorText()
        #print textTup

        ## prep the two lines of text
        tx,ty = (46,15) if isinfo else (38 , 20)

        tx += offx
        text0 = TextPencil( "tup0", textTup[0], fcol=fcol, x=tx,y=ty, points=12, weight=wx.BOLD)

        tx,ty = (46,40) if isinfo else (5 ,40)

        tx += offx
        text1 = TextPencil( "tup1", textTup[1], fcol=fcol,x=tx,y=ty, points=10 )

        self.addPencil( iconpencil, text0, text1 )



    def make_inactive_bitmap(self, wxim):
        if wxim in self._inactive_images:
            return self._inactive_images[wxim]
        tmp = wxim.AdjustChannels(0,0,0,factor_alpha = 0.5)
        self._inactive_images[wxim] = tmp#.ConvertToBitmap()
        return tmp
     

    def gen_face_samples(self):

        if isinstance(self.fitem, fontcontrol.InfoFontItem):
            return

        paf, points, text = self.fitem.glyphpaf, fpsys.config.points, " " + fpsys.config.text + "  "
        i = 0
        there_are_more_faces=True
        while (there_are_more_faces):
            try:
                ## This access by i can cause an error.
                font = ImageFont.truetype(paf, points,index = i, encoding = "unicode")

                w,h = font.getsize( text )
                ## Some fonts (50SDINGS.ttf) return a 0 width.
                ## I don't know exactly why; maybe it could not render
                ## any of the chars in text.
                #if int(w) == 0:
                #    w = 1
                pilheight = max(1, int(h))
                pilwidth = max(1, int(w))

                pilheight += Fitmap.SPACER

                ## Sept 2009 : Fiddled this to produce alpha (ish) images.
                ## pilimage is of type PIL.Image.Image. 
                ## python
                ## >>> from PIL import Image
                ## >>> pi = Image("RGBA",(10,10))
                ## >>> dir(pi)

                pilimage = Image.new("RGBA", (pilwidth, pilheight), (0,0,0,0))

                #if self.inactive:
                #    col = (0,0,0,64) #alpha makes it gray
                #else:
                #    col = (0,0,0,255)
                col = (0,0,0,255)

                ## Well, I have since discovered that some fonts
                ## cause a MemoryError on the next command:
                drawnFont = ImageDraw.Draw( pilimage ) # Draws INTO pilimage
                drawnFont.text((0,0) , text, font=font, fill=col)

                ## Get the data from RGBA PIL into wx.
                ## Thx, http://nedbatchelder.com/blog/200801/ \
                ## truly_transparent_text_with_pil.html
                image = wx.EmptyImage(*pilimage.size)
                image.SetData(pilimage.convert("RGB").tobytes() )
                #image.SetAlphaData(pilimage.convert("RGBA").tobytes()[3::4])
                image.SetAlphaData(pilimage.tobytes()[3::4])

                self.face_image_stack.append(image)

                self.accrue_width( pilwidth )
                #self.accrue_height( pilheight )

                ## All is well, so we step ahead to the next *potential* sub-face
                i += 1

            ## On any kind of error, end the loop.

            ## IOError happens when i is out of bounds:
            except IOError:
                there_are_more_faces = False   

            ## Whatever else goes wrong, just set badfont.
            except Exception as e: 
                self.fitem.badfontmsg = _("Font causes a memory error, it can't be drawn.\nError was:{}").format(e)
                self.fitem.badstyle = "PIL_CANNOT_RENDER"
                self.fitem.badfont = True
                there_are_more_faces = False

    def CalculateTopLeftAdjustments(self, wxi):
        ## Sept 2009
        ## Find the first pixel from the top-left of the image (if it's not stored)
        ## Using this pixel as the x,y I can draw fonts from where their actual data
        ## begins and not where the pilimage *thinks* it does (leaving big white spaces
        ## to the left of many fonts.)
        wx.BeginBusyCursor()
        fx,fy=0,0
        W,H = self.wxi.GetSize()#pilimage.size
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
        wx.EndBusyCursor()
        return fx,fy        


    def prepareBitmap( self ):
        """
        This prepares and draws a single fitmap
        """

        ## Go determine my draw state. 
        # Initial run has A and B set.
        self.determine()

        if self.is_block("A"):
            # Block A: Generate new face bitmaps
            #print "Calling gen_face_samples for ", self.name
            self.gen_face_samples()

        if self.is_block("B"):
            # Block B: Draw the entire fitmap
            #print " ..calling draw_bitmap and use_pencils for ", self.name
            self._draw_bitmap()
            self._use_pencils()
    
        if self.state > 0:
            self.Refresh()# to force onPaint()


    def _draw_bitmap(self):
        ## Is this a normal FontItem, or an InfoFontItem?
        ## InfoFontItem is a fake font item for the purposes
        ## of saying "There are no fonts to see here."
        if isinstance( self.fitem, fontcontrol.InfoFontItem ):
            self.style=Fitmap.styles['INFO_FONT_ITEM']
            self.gen_info_or_badfont( isinfo = True )       
            self.height = Fitmap.MIN_FITEM_HEIGHT + 20
            return

        self.setStyle()

        if self.fitem.badfont:
            self.gen_info_or_badfont()
            h = Fitmap.MIN_FITEM_HEIGHT
            if self.fitem.inactive: h += 5 #Need more space
            self.height = h
            return

        fcol = self.style['fcol']
        mainy = 10
        if self.fitem.inactive:
            #totheight += (Fitmap.SPACER-10)
            mainy += (Fitmap.SPACER-10) #want room for 'is in pog' message.

        #for i,pilimage in enumerate(pilbitmaps):
        for i,wximage in enumerate(self.face_image_stack):
            glyphHeight = wximage.GetSize()[1]
            ## The Face Sample:
            x = 16
            if i > 0: x *= 3 # Shift sub-faces over a little

            if self.fitem.inactive:
                image = self.make_inactive_bitmap(wximage)
            else:
                image = wximage

            image = image.ConvertToBitmap()

            fx, fy = 0, 0
            if not fpsys.config.ignore_adjustments:
                fx,fy = self.CalculateTopLeftAdjustments(wximage)
                
            self.addPencil(
                BitmapPencil("face-{}".format(i),
                    x - fx,
                    mainy - fy,
                    image)
                )
                
            ## The Caption: fam, style, name
            self.addPencil( 
                TextPencil( "face-{}-caption".format(i),
                    "{} - {} - [{}]".format(
                        self.fitem.family[i],
                        self.fitem.style[i],
                        self.fitem.name ),
                    28,
                    mainy + glyphHeight + 8,
                    fcol, 
                    points = 8)
                )

            ## Move TOP down to next BOTTOM (for next sub-face)
            mainy += glyphHeight + Fitmap.SPACER

        #mainy might be a better indication of the height
        #self.height = mainy # vs totheight
        self.accrue_height( mainy )

        ## The inactive footer
        if self.fitem.inactive:
            x,y=(25,self.height-20) if self.fitem.badfont else (48,self.height-26)
            self.addPencil( BitmapPencil( "bmpinactive", x-16, y-1, self.TICKSMALL) )

            txt = self.fitem.activeInactiveMsg
            self.addPencil( TextPencil( "fntinactive", txt, x+2, y, fcol, points=10) )
        else:
            ## Better to simply remove them...TODO
            self.addPencil( EmptyPencil("bmpinactive"))
            self.addPencil( EmptyPencil("fntinactive"))
            
        ## The ticked state
        ## Draw the tick/cross if it's not a FILE_NOT_FOUND font (can't be found)
        ## NB: FILE_NOT_FOUND is not available for installation!
        if self.fitem.badstyle != "FILE_NOT_FOUND":
            #print "self.fitem.name ticked:", self.fitem.ticked
            if self.fitem.ticked:
                self.TICKMAP = self.parent.parent.TICKMAP
                self.addPencil( BitmapPencil( "tickmap", 20, 5, self.TICKMAP) )    
            else:
                self.addPencil( EmptyPencil( "tickmap" ))


    def _use_pencils(self):
        """
        Makes a new mem dc with the best size.
        Loops the drawlist and uses the Pencils to draw text and bitmaps
        Returns a memdc for sundry use.
        """
        w = max((p.getwidth() + int(1.5 * p.x)) for p in self.drawDict.values())
        h = self.height

        #import pdb; pdb.set_trace()
        #print "w, height:",w, h #self.height
        #if h == 0: raise SystemExit

        bitmap = wx.EmptyImage( w, h ).ConvertToBitmap()
        memDc = wx.MemoryDC()
        memDc.SelectObject( bitmap )
        #memDc.SetBackground( wx.Brush( wx.Colour(255,255,255,wx.ALPHA_OPAQUE), wx.SOLID) )
        memDc.Clear()
        
        #self.bottomFadeEffect( memDc, h, w )

        #ctx = wx.GraphicsContext.Create(memDc)
        #b = ctx.CreateLinearGradientBrush(0,h,0,0,"#eeeeeeff", "#ffffffff")
        #ctx.SetBrush (b)
        #ctx.DrawRectangle(0,0,w,h)

        self.bitmap = bitmap #record this for the init

        ## Draw it all - via the pencils
        for pencil in self.drawDict.values(): 
            #print "Drawing pencil:", pencil.id
            pencil.draw(memDc)
            #print "done"

        #gstops = wx.GraphicsGradientStops(wx.Colour(255,255,255,255), wx.Colour(255,255,255,0))
        #gstops.Add(wx.Colour(255,255,255,255), 0.8)
        #b = ctx.CreateLinearGradientBrush(w,0,w-(w/8),0, gstops )
        #ctx.SetBrush (b)
        #ctx.DrawRectangle(0,0,w,h)


        ## Thinking of drawing with a bitmap brush onto a larger bg image somehow
        ## want to get all the fitmaps equal width...
        # brush1 = wx.BrushFromBitmap(wx.Bitmap('pattern1.png'))
        # dc.SetBrush(brush1)
        # dc.DrawRectangle(10, 15, 90, 60)

        ## Now a dividing line
        memDc.SetPen( wx.Pen( (180,180,180),1 ) )#black, 1 ) ) 
        memDc.DrawLine( 0, self.height-1, self.bitmap.GetWidth(), self.height-1 )

        self.width = w
        
        # Vital line: I can't tell you ... Man. The suffering.
        self.SetBestSize((w, h))    


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

            #sz = (self.bitmap.GetWidth(), self.bitmap.GetHeight())

            #self.SetBestSize((sz[0], sz[1]))        
            
            ## Now I can calc the y value of the button.
            self.cmb_rect=wx.Rect(0,self.bitmap.GetHeight()-40,19,32)

            # Draw the charmap button
            x,y = self.cmb_rect[0],self.cmb_rect[1]
            if self.cmb_overout.truthstate:
                dc.DrawBitmap( self.CHARMAP_BUTTON_OVER, x, y, True )
            else:
                dc.DrawBitmap( self.CHARMAP_BUTTON_OUT, x,y, True )


    def crop(self, newwidth):
        #print "Cropping:",self.name
        h = self.bitmap.GetHeight()
        #print " Before w,h:", self.bitmap.GetWidth(), self.bitmap.GetHeight()
        img = self.bitmap.ConvertToImage().Resize( (newwidth, h),(0,0),255,255,255 )
        self.bitmap = img.ConvertToBitmap()
        self.SetBestSize((newwidth, h))        
        #print " After w,h:", self.bitmap.GetWidth(), self.bitmap.GetHeight()
        #print " After (my vars) w,h:", newwidth, h





    def setStyle( self ):
        """
        Set a copy of the styles key and alter colours as needed.
        """
        # InfoFontItem does not use this, all others do.
        if self.fitem.badfont:
            self.style=Fitmap.styles[self.fitem.badstyle].copy() #damn! this was tricky!
            if self.fitem.inactive:
                ## July 2016
                ## =========
                ## Happened on cases where 'ndi' key was not in styles dict. 
                ## Added them in.
                self.style['fcol'] = Fitmap.styles['INACTIVE']['fcol']
                self.style['backcol'] = Fitmap.styles[self.fitem.badstyle]['ndi'] #ndi = No Draw Inactive
            return

        # Not bad font, just get vals from style sheet.
        if self.fitem.inactive:
            self.style = Fitmap.styles['INACTIVE']
        else:
            self.style = Fitmap.styles['ACTIVE']










    def openCharacterMap( self ):
        fi=self.fitem
        dirname = os.path.basename( fi.glyphpaf )
        dest = os.path.join(fpsys.iPC.userFontPath(), dirname )

        ## I don't want to hold an fitem in the thread to come, so I will
        ## take the essential info out and make a tuple instead:
        ## (This is mere superstition and ignorance; I fear threads :) )

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
        """
        Uses the instance (held in fpsys.config) of the classes in charmaps.py.
        was in gui_ScrolledFontView.py
        """
        iCM = fpsys.config.CMC.GetInstance()
        iCM.OpenApp( *args )
        iCM.Cleanup( )

    def onMiddleClick(self, event):
        ps.pub( menu_settings, None )

    def can_have_button( self ):
        """
        Because I just can't guarantee that there is a family name
        and because bad fonts that can't draw (but do not segfault)
        are so rare that I can't bloody find any to test with (grrr)
        I make the sweeping fiat that FILE_NOT_FOUND badfonts will 
        not get a button.

        Other fitems like info and FILE_NOT_FOUND don't get buttons.
        """
        if not fpsys.config.CMC.APPS_ARE_AVAILABLE: return False
        if isinstance( self.fitem, fontcontrol.InfoFontItem ): return False
        if self.fitem.badstyle == "FILE_NOT_FOUND": return False
        if not self.fitem.family: return False
        return True

    def onHover( self, e ):
        if not self.can_have_button():
            self.overout.set ( True )
            return
        if self.cmb_rect: # It's None when a Fitmap is first instanced.
            if self.cmb_rect.Contains( e.GetPositionTuple() ):
                self.cmb_overout.set( True )
                self.overout.set( False ) #Not 'on' fitmap
            else:
                self.cmb_overout.set ( False )
                self.overout.set( True )

    def charmap_button_signal( self ):
        if self.cmb_overout.truthstate:
            self.SetCursor(wx.StockCursor(wx.CURSOR_MAGNIFIER))
        self.Refresh() # Force onPaint()

    def overout_signal( self ):
        if self.overout.truthstate:
            self.SetCursor( self.CURSOR )

    def onLeave(self, event):
        """
        Catch the leave event for set the charmap button off,
        if the pointer goes out on the left edge.
        """
        self.onHover(event)

    def onClick(self, event) :
        """
        Deals with clicks on self.
        Charmap button is a sub-test on a rect.
        This refreshes the underlying bitmap and DOES NOT cause the
        chain update_font_view (in gui_FontView) to run.
        """
        if self.cmb_overout.truthstate and self.can_have_button():
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
