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

from fpwx import SYSFONT


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
    I make them and store them in a dict. This gives an
    ordering in time and overlapping too.
    I can loop and draw them all in one go.
    """
    def __init__( self, id, x = 0, y = 0, fcol = (0,0,0)):
        self.id = id; self.x = x; self.y = y
        self._fcol = fcol
    def getwidth(self): return 0 
    def draw(self, memdc): pass

class TextPencil(Pencil):
    _text_extents_dict = {}
    def __init__( self, id, txt, 
            x = 0, y = 0, 
            fcol = (0,0,0),
            points = "points_normal",
            style = wx.NORMAL, 
            weight = wx.NORMAL ):
        Pencil.__init__(self, id, x = x, y = y, fcol = fcol)
        self.txt = txt
        ## I get point sizes from the SYSFONT dict
        points = SYSFONT[points]
        self.font =  wx.Font( points, SYSFONT["family"],
                style, weight, encoding=wx.FONTENCODING_DEFAULT )

        ## Measure a line of text in my font.
        ## Cache these widths in Pencil class variable, so that
        ## future identical strings can avoid work.
        ## Turned out I don't use this much.
        if not self.txt in TextPencil._text_extents_dict:
            dc = wx.ScreenDC()
            dc.SetFont( self.font )
            try:
                sz = dc.GetTextExtent( self.txt )
            except:
                sz = (Fitmap.MIN_FITEM_WIDTH,Fitmap.MIN_FITEM_HEIGHT)
            # cache it in the class
            TextPencil._text_extents_dict[self.txt] = sz

    def getwidth(self):
        return TextPencil._text_extents_dict[self.txt][0]

    def getheight(self): 
        return TextPencil._text_extents_dict[self.txt][1]

    def draw(self, memdc):
        memdc.SetTextForeground( self._fcol )
        memdc.SetFont( self.font )
        memdc.DrawText( self.txt, self.x, self.y )

class BitmapPencil(Pencil):
    def __init__( self, id, x=0, y=0, bitmap = None, use_mask = True ):
        Pencil.__init__(self, id, x, y)
        self.bitmap = bitmap
        self.use_mask = use_mask
    def getwidth(self): return self.bitmap.GetWidth()
    def getheight(self): return self.bitmap.GetHeight()
    def draw(self, memdc):
        memdc.DrawBitmap( self.bitmap, self.x, self.y, self.use_mask )





ndc=(200,190,183) # No Draw Color: colour of background for the fonts I can't draw
ndi=(227,226,219) # No Draw Inactive => "ndi"
black=(0,0,0)
white=(255,255,255)

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
    MIN_FITEM_WIDTH = 500
    MIN_FITEM_HEIGHT = 10
    SPACER = 0
    LINEHEIGHT = 0

    def __init__( self, parent, fitem ) :

        self.name = fitem.name

        self.fitem = fitem

        Fitmap.styles['INFO_FONT_ITEM']['backcol']=parent.GetBackgroundColour()

        self.FVP = parent.parent #The Scrolled Font View Panel

        self.parent = parent
        self.TICKSMALL = parent.parent.TICKSMALL

        self.style = {}

        self.gradientheight = 50

        Fitmap.LINEHEIGHT = TextPencil("X", 0, 0, points = "points_smaller").getheight()
        Fitmap.SPACER = Fitmap.LINEHEIGHT * 3

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
        Sets the dict key's value to something
        and tests if it differs from the last value. 
        Returns: True or False
        (If first run, it sets and returns true)
        """
        if key not in self.history_dict:
            tf = True
        else:
            tf = self.history_dict[key] != something

        self.history_dict[key] = something
        return tf

    ## Class vars for state stuff
    blocks = {"A":1,"B":2}
    flagA = 1
    flagB = 2
    def determine_draw_state(self):
        """
        Looking at very specific variables which 
        influence how we will draw the font bitmap.
        We OR the values onto state as we go.
        
        Fitmap.flagBecause of the way has_changed works, on first 
        run, the state will be maxed, all blocks are on.
        """
        # A | B
        if self.has_changed("pointschanged", fpsys.config.points):
            self.state |= Fitmap.flagA | Fitmap.flagB
        # A | B
        if self.has_changed("textchanged", fpsys.config.text):
            self.state |= Fitmap.flagA | Fitmap.flagB
        # B
        if self.has_changed("activechanged", self.fitem.inactive):
            self.state |= Fitmap.flagB
        # B
        if self.has_changed("tickedchanged", self.fitem.ticked):
            self.state |= Fitmap.flagB
        # B
        if self.has_changed("tlchanged", fpsys.config.ignore_adjustments):
            self.state |= Fitmap.flagB

    def is_block(self, c):
        """
        This looks at the state and determines 
        which block it's in.
        E.g. if xx.is_block("A"):
        """
        #print u"state of {} is {}".format(self.name, self.state)
        return self.state & Fitmap.blocks[c] == Fitmap.blocks[c]

    def accrue_height(self,n):
        self.height = max(self.height, n)

    def add_pencil(self, *pencils):
        # Beware, this does not preserve the order of the
        # input list!
        d = dict((o.id, o) for o in pencils)
        self.drawDict.update(d)

    def remove_pencil(self, *ids):
        [ self.drawDict.pop(id, None) for id in ids ]

    def gen_info_or_badfont( self, isinfo = False ):
        """
        Draw the Info Font block, or an Error message block. Much clearer than it was before.
        """
        #Sept 2017: Move it all over by an offset
        offx = 10

        icon = self.style['icon']

        iconpencil = None
        if icon:
            Icon = self.FVP.__dict__[icon] #See gui_FontView.py ~line 97
            ix,iy = (6,10) if isinfo else (2,10)

            ix += offx
            iconpencil = BitmapPencil( "infoicon", ix, iy, Icon)

        ## Prep and measure the texts to be drawn. Add them to drawlist.
        fcol = self.style['fcol']

        textTup = self.fitem.InfoOrErrorText()

        ## Text 0: The bold, large text of the message.
        tx,ty = (76,45) if isinfo else (38 , 15)

        tx += offx
        text0 = TextPencil( "tup0", textTup[0], fcol=fcol, x=tx,y=ty,
                points="points_large", weight=wx.BOLD)

        ## Text 1 - under Text 0
        ty += text0.getheight()
        # if there are newlines in the first text, we need more space
        if textTup[0].count("\n") == 0: ty += Fitmap.LINEHEIGHT + (Fitmap.LINEHEIGHT/3)
        tx = 76 if isinfo else 5
        pnts = "points_normal" if isinfo else "points_smaller"

        tx += offx
        text1 = TextPencil( "tup1", textTup[1], fcol=fcol,x=tx,y=ty,
                points = pnts )

        self.add_pencil( iconpencil, text0, text1 )

        h = sum(p.getheight() for p in [iconpencil, text0, text1])
        return h


    def make_inactive_bitmap(self, wxim):
        if wxim in self._inactive_images:
            #print u"Cached inactive for {}".format(self.name)
            return self._inactive_images[wxim]
        tmp = wxim.AdjustChannels(0,0,0,factor_alpha = 0.5)
        self._inactive_images[wxim] = tmp#.ConvertToBitmap()
        return tmp
     

    def _gen_glyphs(self):
        """
        NB: Determines the intial measured width of a fitmap.
        """
        w = 1 if not self.fitem.badfont else Fitmap.MIN_FITEM_WIDTH
        #if self.fitem.badfont:
        #    w = Fitmap.MIN_FITEM_WIDTH
        #else:
        #    w = 1
        paf, points, text = self.fitem.glyphpaf, fpsys.config.points, " " + fpsys.config.text + "  "
        i = 0
        del self.face_image_stack[:]
        glyph_widths = [w]
        there_are_more_faces=True
        while (there_are_more_faces):
            try:
                ## This access by i can cause an error.
                font = ImageFont.truetype(paf, points,index = i, encoding = "unicode")

                w,h = font.getsize( text )
                #print u"{} {},{}".format(paf,w,h)
                ## Some fonts (50SDINGS.ttf) return a 0 width.
                pilheight = max(1, int(h))
                pilwidth = max(1, int(w))


                ## Sept 2009 : Fiddled this to produce alpha (ish) images.
                ## pilimage is of type PIL.Image.Image. 
                ## python
                ## >>> from PIL import Image
                ## >>> pi = Image("RGBA",(10,10))
                ## >>> dir(pi)
                pilimage = Image.new("RGBA", (pilwidth, pilheight), (0,0,0,0))

                ## Well, I have since discovered that some fonts
                ## cause a MemoryError on the next command:
                drawnFont = ImageDraw.Draw( pilimage ) # Draws INTO pilimage
                drawnFont.text((0,0) , text, font=font, fill=(0,0,0,255))

                ## Get the data from RGBA PIL into wx.
                ## Thx, http://nedbatchelder.com/blog/200801/ \
                ## truly_transparent_text_with_pil.html
                image = wx.EmptyImage(*pilimage.size)
                image.SetData(pilimage.convert("RGB").tobytes() )
                #image.SetAlphaData(pilimage.convert("RGBA").tobytes()[3::4])
                image.SetAlphaData(pilimage.tobytes()[3::4])

                self.face_image_stack.append(image)

                #self.accrue_width( pilwidth )
                glyph_widths.append(pilwidth)


                ## All is well, so we step ahead to the next *potential* sub-face
                i += 1

            ## On any kind of error, end the loop.

            ## IOError happens when i is out of bounds:
            except IOError:
                there_are_more_faces = False   

            ## Whatever else goes wrong, just set badfont.
            except Exception as e: 
                self.fitem.badfontmsg = _("Font causes a memory error, it can't be drawn.\nOriginal error was:\n{}").format(e)
                self.fitem.badstyle = "PIL_CANNOT_RENDER"
                self.fitem.badfont = True
                there_are_more_faces = False

        return max(glyph_widths)

    def CalculateTopLeftAdjustments(self, wxi):
        ## Sept 2009
        ## Find the first pixel from the top-left of the image (if it's not stored)
        ## Using this pixel as the x,y I can draw fonts from where their actual data
        ## begins and not where the pilimage *thinks* it does (leaving big white spaces
        ## to the left of many fonts.)
        wx.BeginBusyCursor()
        fx,fy=0,0
        W,H = wxi.GetSize()
        fx=fy=0
        esc = False
        # Scan ACROSS WIDTH and repeatedly DOWN looking for a pixel.
        for tx in xrange(W):
            for ty in xrange(H):
                ap=wxi.GetAlpha(tx,ty)
                if ap != 0: #Found X coord, let's kill both loops
                    fx=tx
                    esc = True
                    break
            if esc: break #uses fact that 0 is False
        # Scan DOWN the HEIGHT and repeatedly ACROSS.
        esc = False
        for ty in xrange(H):
            for tx in xrange(W):
                ap=wxi.GetAlpha(tx,ty)
                if ap != 0:
                    fy=ty # Found Y coord
                    esc = True
                    break
            if esc: break
        wx.EndBusyCursor()
        return fx,fy        

    def render_and_measure_glyphs( self ):
        """
        The process is split into "render/measure" and the "assemble"
        This is step ONE: the render/measure part.

        Call must happen immediately after instancing a new Fitmap. 
        * This happens in gui_ScrolledFontView.MinimalCreateFitmaps()

        If the state is appropriate, render the glyphs into wximages.
        
        (It's possible to call this on exisiting fitmaps, in which case
        the state might not hold flagA, so we need not call _gen_glyphs)

        We return the width so we can calculate the columns and
        their widths in gui_ScrolledFontView.MinimalCreateFitmaps()
        """
        self.determine_draw_state()
        #print u"measure Draw state: {} for {}".format(self.state,self.name)
        max_glyph_width = self.width
        if self.is_block("A"):
            max_glyph_width = self._gen_glyphs()
            self.state = self.state & ~Fitmap.flagA #Switch off flagA
        return max_glyph_width

    def assemble_bitmap( self, colw = None ):
        """
        This is step TWO of the process, the "assemble" part:
        This checks state and possibly draws into the bitmap.

        We've have already had render_and_measure_glyphs() run before arriving here; 
        thus the glyphs are ready and waiting.

        (The only internal call to assemble_bitmap() comes from self.onClick()
        afer this fitmap already exists and has been measured, therefore
        we don't need _gen_glyphs in this method.)

        As it happens, right now, there are only two states:
        bits 0 "A" and/or 1 "B", i.e. 
        "A" gen_glyphs 
        "B" draw_bitmap+use_pencils;
        """
        ## Go determine_draw_state my draw state. 
        self.determine_draw_state()
        #print u"assemble_bitmap Draw state: {} for {}".format(self.state,self.name)

        if self.is_block("B"):
            # Block B: Draw the entire fitmap
            #print " ..calling draw_bitmap and use_pencils for ", self.name
            self._draw_bitmap()
            self._use_pencils( colw )
    
        if self.state > 0:
            self.Refresh()# force onPaint()
        
        self.state = 0




    def _draw_bitmap(self):
        ## Is this a normal FontItem, or an InfoFontItem?
        ## InfoFontItem is a fake font item for the purposes
        ## of saying "There are no fonts to see here."
        if isinstance( self.fitem, fontcontrol.InfoFontItem ):
            self.style=Fitmap.styles['INFO_FONT_ITEM']
            h = self.gen_info_or_badfont( isinfo = True )       
            self.height = Fitmap.MIN_FITEM_HEIGHT + h + 20
            return

        self.setStyle()
        fcol = self.style['fcol']

        if self.fitem.badfont:
            bh = self.gen_info_or_badfont()
            #h = Fitmap.MIN_FITEM_HEIGHT
            #if self.fitem.inactive: mainy += 5 #Need more space
            mainy = bh + 5 #self.height = h
        else:
            mainy = Fitmap.MIN_FITEM_HEIGHT#10
            self.height = mainy #reset the height!

            for i,wximage in enumerate(self.face_image_stack):
                #print u"..draw_bitmap loop for {} i is {} wximage is {}".format(self.name,i,wximage)
                glyphHeight = wximage.GetSize()[1]
                ## The Face Sample:
                x = 16
                if i > 0: x *= 3 # Shift sub-faces over a little

                if self.fitem.inactive:
                    image = self.make_inactive_bitmap(wximage)
                else:
                    image = wximage

                fx, fy = 0, 0
                if not fpsys.config.ignore_adjustments:
                    fx,fy = self.CalculateTopLeftAdjustments(wximage)
                    
                ## The face bitmap itself:
                glyph = BitmapPencil("face-{}".format(i),
                        x - fx,
                        mainy - fy,
                        image.ConvertToBitmap() )
                
                
                ## The Caption: fam, style, name
                caption = TextPencil( "face-{}-caption".format(i),
                        "{} - {} - [{}]".format(
                            self.fitem.family[i],
                            self.fitem.style[i],
                            self.fitem.name ),
                        28,
                        mainy + glyphHeight + (Fitmap.SPACER/3),
                        fcol,
                        points = "points_smaller")

                self.add_pencil( glyph, caption )

                ## Move TOP down to next BOTTOM (for next sub-face)
                mainy += glyphHeight + Fitmap.SPACER

        #if self.fitem.inactive:
        #    mainy += (Fitmap.SPACER)# -10) what? TODO fix #want room for 'is in pog' message.

        mainy += Fitmap.SPACER
        self.accrue_height( mainy )

        ## The inactive footer
        if self.fitem.inactive:
            xx = 40
            #x,y=(25,self.height-20) if self.fitem.badfont else (48,self.height-26)
            #y= self.height-20 if self.fitem.badfont else self.height-26
            y = self.height - 25
            self.add_pencil( BitmapPencil( "bmpinactive", xx, y, self.TICKSMALL) )

            txt = self.fitem.activeInactiveMsg
            self.add_pencil( TextPencil( "fntinactive", txt, xx + 22 + 4, y + 1, fcol) )
            
        else:
            self.remove_pencil("bmpinactive", "fntinactive")
            
        ## The ticked state
        ## Draw the tick/cross if it's not a FILE_NOT_FOUND font (can't be found)
        ## NB: FILE_NOT_FOUND is not available for installation!
        #print u"{} is {}".format(self.name,  self.fitem.badstyle)
        if self.fitem.badstyle != "FILE_NOT_FOUND":
            #print "self.fitem.name ticked:", self.fitem.ticked
            if self.fitem.ticked:
                self.TICKMAP = self.parent.parent.TICKMAP
                self.add_pencil( BitmapPencil( "tickmap", 40, 10, self.TICKMAP) )    
            else:
                self.remove_pencil("tickmap")

            

    def _use_pencils(self, colw = None):
        """
        Makes a new mem dc with the best size.
        Loops the drawDict for Pencils to draw text and bitmaps.

        NOTE
        ====
        (See gui_ScrolledFontView.MinimalCreateFitmaps for more.)

        I used to tote-up the widths of my pencils to get my overall width.
        i.e: w = max(p.getwidth() + int(1.5 * p.x) for p in self.drawDict.values())
        This caused problems. I discovered that the width of a fitmap is best
        imposed from without - from the ScrolledFontView where they live.

        There is one use of assemble_bitmap within myself - in self.onClick()
        In this one method, we can be certain it's running *after* the fitmap
        has been created - and thus already has a width imposed.
        (This use-case is when colw would be None.)

        """
        if colw:
            w = colw
        else:
            w = self.width #We already exist and have a width, so use it.
        
        self.width = w
        h = self.height

        bitmap = wx.EmptyImage( w, h ).ConvertToBitmap()
        memDc = wx.MemoryDC()
        memDc.SelectObject( bitmap )
        #memDc.SetBackground( wx.Brush( wx.Colour(255,255,255,wx.ALPHA_OPAQUE), wx.SOLID) )
        memDc.Clear()
        
        if not isinstance( self.fitem, fontcontrol.InfoFontItem ):
            ## Backdrop gradient:
            ## Baptiste's idea! New implementation: Oct 2017
            ## "Now a dividing gradient, you can say "wow" ;-)"
            ## Donn says, "..Wow!" :-D
            ctx = wx.GraphicsContext.Create(memDc)
            b = ctx.CreateLinearGradientBrush(0,h,0,0, self.parent.gstops["baptiste"])
            ctx.SetBrush (b)
            ctx.DrawRectangle(0,0,w,h)

            #if self.fitem.ticked:
            #    ctx.SetBrush(wx.Brush(wx.Colour(0,170,212)))
            #    ctx.DrawRectangle(0,0,4,h)

        ## Draw it all - via the pencils
        for pencil in self.drawDict.values():
            pencil.draw(memDc)

        if not isinstance( self.fitem, fontcontrol.InfoFontItem ):
            ## Right-hand side gradient, to fade long glyphs
            fr = w/7
            b = ctx.CreateLinearGradientBrush(w-fr,0,w,0, self.parent.gstops["white_to_alpha"] )
            ctx.SetBrush (b)
            ctx.DrawRectangle(w-fr,0,w,h)

            ## Now a dividing line
            b = ctx.CreateLinearGradientBrush(0,0,w,0,self.parent.gstops["underline"])
            ctx.SetBrush(b)
            ctx.DrawRectangle(0,h-1,w,h-1)

        #memDc.DrawCheckMark(50, 50, 20,20) # a liiitle fugly. Not gonna lie.

        self.bitmap = bitmap #record this for the init

        # Vital line: I can't tell you ... Man. The suffering.
        self.SetBestSize((w, h))    


    def onPaint(self, event):
        """
        Dump the bitmap to the screen.
        """
        if self.bitmap:
            ## Create a buffered paint DC.  It will create the real
            ## wx.PaintDC and then blit the bitmap to it when dc is
            ## deleted by leaving this function.
            dc = wx.BufferedPaintDC(self, self.bitmap, wx.BUFFER_VIRTUAL_AREA)

            if not self.can_have_button(): return
            
            ## The charmap button is not part of the underlying process
            ## of drawing the bitmap, in that it needs to react to the mouse. 
            ## We call onPaint via self.refresh() and bypass all the 
            ## other drawing code.

            #self.cmb_rect=wx.Rect(0,self.bitmap.GetHeight()-40,19,32)
            # x, y, w, h
            self.cmb_rect=wx.Rect(4,self.height-31, 32, 27)

            # Draw the charmap button
            x,y = self.cmb_rect[0],self.cmb_rect[1]
            #ctx = wx.GraphicsContext.Create( dc )
            if self.cmb_overout.truthstate:
                #ctx.DrawBitmap( self.CHARMAP_BUTTON_OVER, x, y, 27, 27 )
                dc.DrawBitmap( self.CHARMAP_BUTTON_OVER, x, y, True )
            else:
                #ctx.DrawBitmap( self.CHARMAP_BUTTON_OUT, x,y, 27, 27 )
                dc.DrawBitmap( self.CHARMAP_BUTTON_OUT, x,y, True )







    def setStyle( self ):
        """
        Set a copy of the styles key and alter colours as needed.
        """
        # InfoFontItem does not use this, all others do.
        if self.fitem.badfont:
            ## Make a copy because I'm going to alter it a bit:
            self.style=Fitmap.styles[self.fitem.badstyle].copy()
            if self.fitem.inactive:
                self.style['fcol'] = Fitmap.styles['INACTIVE']['fcol']
                self.style['backcol'] = Fitmap.styles[self.fitem.badstyle]['ndi']
        else:
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
        """
        iCM = fpsys.config.CMC.GetInstance()
        iCM.OpenApp( *args )
        iCM.Cleanup( )

    def onMiddleClick(self, event):
        ps.pub( open_settings_panel)

    def can_have_button( self ):
        """
        Because I just can't guarantee that there is a family name
        and because bad fonts that can't draw (but do not segfault)
        are so rare that I can't bloody find any to test with (grrr)
        I make the sweeping fiat that FILE_NOT_FOUND badfonts will 
        not get a button.

        Other fitems like info and FILE_NOT_FOUND don't get buttons.
        """
        if not fpsys.config.CMC.apps_are_available: return False
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
            self.assemble_bitmap() # This only redraws a single font item.
            self.Refresh()  #forces a redraw.

            ## Inc or dec a counter depending on the tickedness of this item
            if self.fitem.ticked: fpsys.state.numticks += 1
            if not self.fitem.ticked: fpsys.state.numticks -= 1
            ps.pub(toggle_main_button)
