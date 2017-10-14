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



class History(object):
    """
    A history that remembers a key's last value.
    You set it while checking for a difference.
    """
    def __init__(self):
        self._d = {}
    def differs(self, key, something):
        """
        Sets the value and tests if it differs from
        the last value. 
        Returns: True or False
        (If first run, it sets and returns true)
        """
        if key not in self._d:
            tf = True
        else:
            tf = self._d[key] != something

        self._d[key] = something
        return tf



class DrawState(object):
    """TODO: comment better
    States: when or-ed together indicate they were SET..
    Not what they are set-to, just *that* they changed.
    #These states are related to other state variables
    #like "inactive" (in an fitem) but live in this object.
    #We would say:
    # When the font item becomes inactive, the fitmap's
    #  activechanged status bit must be set.
    # Then we react on that fact and clear the bit for 
    #  that status.

    ## AND masks to extract block info out of the state byte
    ## Multiple states can land one in a single block.
    ## A combo of activechanged plus pointsizechanged -> 
    ## both go in block A
    ## because the two flags overlap in their intentions.
    ## activechanged means all new face bitmaps and more.
    ## pointsizechanged means much the same
    ## Therefore we gather them into "blocks" of work.
    """
    mask_A = 1
    mask_B = 2
    mask_C = 4
    mask_D = 8
    mask_E = 16

    blocks = {"A":1,"B":2,"C":4,"D":8}
   
    def __init__(self, fitmap):
        self.parent = fitmap
        self.state = 0
        self.laststate = self.state
        self._history = History()

    def determine(self):
        """
        Looking at very specific variables which 
        influence how we will draw the font bitmap.
        We OR the values onto state as we go.
        
        Because of the way History.differs works, on first 
        run, the state will be maxed, all blocks are on.
        """
        self.state = 0
        # A
        if self._history.differs("pointschanged", fpsys.config.points):
            self.state |= DrawState.mask_A
        # A
        if self._history.differs("textchanged", fpsys.config.text):
            self.state |= DrawState.mask_A
        # B
        if self._history.differs("activechanged", self.parent.fitem.inactive):
            self.state |= DrawState.mask_B
        # C
        if self._history.differs("tickedchanged", self.parent.fitem.ticked):
            self.state |= DrawState.mask_C
        # D
        if self._history.differs("tlchanged", fpsys.config.ignore_adjustments):
            self.state |= DrawState.mask_D

    def isblock(self, c):
        """
        This looks at the state and determines 
        which block it's in.
        E.g. if xx.isblock("A"):
        """
        return self.state & DrawState.blocks[c] == \
                DrawState.blocks[c]

        


class Pencil(object):
    """
    Used to store drawing code for DrawText and DrawBitmap.
    I make them and store them in a list. This gives an
    ordering in time and overlapping too.
    I can loop and draw them all in one go.
    """
    def __init__( self, id, x=0, y=0 ):
        self.id = id; self.x = x; self.y = y
    def deploy(self): pass
    def getwidth(self): return 0 
    def draw(self, memdc): pass

class EmptyPencil(Pencil):
    def __init__(self,id):
        Pencil.__init__(self,id)

class TextPencil(Pencil):
    textExtentsDict = {}
    def __init__( self, id, x, y, txt, styleptr, points, 
            style=wx.NORMAL, weight=wx.NORMAL, 
            encoding = wx.FONTENCODING_DEFAULT ):
        Pencil.__init__(self, id, x, y)
        self.txt = txt
        self.styleptr = styleptr
        self.font =  wx.Font( points, fpsys.DFAM, style, weight, encoding=encoding )
        self._width = 0

    def getwidth(self): return self._width

    def deploy(self):
        """
        Measure a line of text in my font. Return a wx.Size
        Cache these widths in Pencil class variable.
        """
        ## Do we have a cached measurement for this txt?
        if self.txt in TextPencil.textExtentsDict:
            return TextPencil.textExtentsDict[self.txt] #yep!
        dc = wx.ScreenDC()
        dc.SetFont( self.font )
        try:
            sz = dc.GetTextExtent( self.txt )
        except:
            sz = (Fitmap.MIN_FITEM_WIDTH,Fitmap.MIN_FITEM_HEIGHT)
        TextPencil.textExtentsDict[self.txt] = sz # cache it in my parent
        
        self._width = sz[0]
        #return sz[0]

    def draw(self, memdc):
        memdc.SetTextForeground( self.styleptr["fcol"] )
        memdc.SetFont( self.font )
        memdc.DrawText( self.txt, self.x, self.y )



class BitmapPencil(Pencil):
    def __init__( self, id, x, y, bitmap):
        Pencil.__init__(self, id, x, y)
        self.bitmap = bitmap
    def getwidth(self): return self.bitmap.GetWidth()
    def draw(self, memdc):
        memdc.DrawBitmap( self.bitmap, self.x, self.y, True )


class FacemapPencil(BitmapPencil):
    def __init__( self, id, pilimage, x, y):
        self._pilimage = pilimage
        self.wximage = self._make_wximage(pilimage)
        self.bitmap = self.image_to_bitmap()
        BitmapPencil.__init__(self,id,x,y, bitmap, self.bitmap.GetWidth())
    def _make_wximage(self,pilimage):


    def bitmap(self):
        return self.wximage.ConvertToBitmap()
    def get_lightened_bitmap(self,n):
        i = self.wximage.AdjustChannels(0,0,0,factor_alpha = n)
                    #    opil.putalpha(128) # not working as expected..

        self.bitmap = i...
        return i
        

class FaceErrorPencil(TextPencil):
    def __init__(self, id, x, y, styleptr, err):
        txt = _("Bad things happened. Original error:{}").format(fpsys.LSP.to_unicode(err))
        TextPencil.__init__(self, id, x, y, txt, styleptr, points, style=wx.ITALIC )


class FaceImagePencil(Pencil):
    def __init__(self, id, x, y, wximage, fitmap):
        self.bitmap = wximage.ConvertToBitmap()
        Pencil.__init__(self, id, x, y)
        self.fitmap = fitmap
        self.wxi = wximage
        self.bmp_inactive = None
        self.tlcache = ()
    def draw(self, memdc):
        # determine tl_adjustment stuff
        fx,fy = 0,0
        if not fpsys.config.ignore_adjustments:
            # i.e. We have to calculate the tl
            if not self.tlcache():
                # We don't have the coords cached
                fx, fy = self.calculate_top_left_adjustments()
                self.tlcache = (fx,fy) #cache 'em!
            else:
                fx, fy = self.tlcache
        # Are we inactive?
        if self.fitmap.fitem.inactive:
            if not self.bmp_inactive:
                ##http://xoomer.virgilio.it/infinity77/wxPython/Widgets \
                ##/wx.Image.html#AdjustChannels
                tmp = self.wxi.AdjustChannels(0,0,0,factor_alpha = 0.5)
                self.bmp_inactive = tmp.ConvertToBitmap()
            b = self.bmp_inactive
        else:
            b = self.bitmap
        memdc.DrawBitmap( b, self.x-fx, self.y-fy, True )
        memdc.DrawCheckMark(0, 0, 10,10)# what will it do?

    def calculate_top_left_adjustments(self):
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

        self.pilbitmaps = []
        self.pilwidth = 0
        self.pilheight = 0
        self.wxImages = []

        # To keep all the pencils in a stack
        self.drawDict = collections.OrderedDict()

        self.height =  0
        self.drawstate = DrawState(self)

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
        #	self.CURSOR = wx.StockCursor( wx.CURSOR_ARROW )
        #if self.fitem.inactive:
        #	self.CURSOR = wx.StockCursor( wx.CURSOR_ARROW )
    
    def addPencil(self,pencil):
        if not isinstance(pencil, list): 
            listofpencils = [whatever]
        else:
            listofpencils = whatever        
        # beware, this does not preserve the order of the
        # input list!
        d = dict((o.id, o) for o in listofpencils)

        self.drawDict.update(d)# {id:pencil})

    def usePencils(self, h):
        """
        Makes a new mem dc with the best size.
        Loops the drawlist and uses the Pencils to draw text and bitmaps
        Returns a memdc for sundry use.
        """
        w = max((p.getwidth() + int(1.5 * p.x)) for p in self.drawDict.values())

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
            #print "Drawing pencil:", pencil
            pencil.draw(memDc)

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

        self.width = w
        
        # Vital line: I can't tell you ... Man. The suffering.
        self.SetBestSize((w, h))        

        return memDc

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

    def qpencils(self, whatever):
        """
        stuffs pencils into an ordered dict. 
        The keys allow items to be added and replaced. 
        This list sticks-around, so we can use what came before- or replace old 
        slots with new pencils.
        """
        #print
        #print "queue with:{} id:{}".format( newpencil, newpencil.id)
        if not isinstance(whatever, list): 
            listofpencils = [whatever]
        else:
            listofpencils = whatever

        for p in listofpencils: 
            if p: # filter-out Nones
                p.deploy()
                self.drawDict.update( { p.id : p } )
        #print "drawDict is:"
        #print self.drawDict

    def info_or_badfont_pencils( self, isinfo = False ):
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

        ## prep the two lines of text
        tx,ty = (46,15) if isinfo else (38 , 20)

        tx += offx
        text0 = TextPencil( "tup0", tx, ty, textTup[0], fcol, points=12, weight=wx.BOLD)

        tx,ty = (46,40) if isinfo else (5 ,40)

        tx += offx
        text1 = TextPencil( "tup1", tx, ty, textTup[1], fcol, points=10 )

        return [ iconpencil, text0, text1 ]



    

    def gen_face_samples(self):
        totheight = 0
        pilbitmaps = []
        widths = [Fitmap.MIN_FITEM_WIDTH]
        for pilimage in self.fitem.generatePilFont():
            #Only fitems that have a successful pilimage appear in this loop
            #Broken pil images set badfont on the fitem, and do not yield a pilgimge.
            pilbitmaps.append( pilimage )
            totheight += pilimage.size[1] + Fitmap.SPACER
            widths.append(pilimage.size[0])
        pilwidth = max(widths)
        pilheight = totheight

        totheight = max(pilheight, Fitmap.MIN_FITEM_HEIGHT)
        
        self.setStyle()

        if self.fitem.badfont:
            self.addPencil( self.info_or_badfont_pencils() )
            return

        if self.fitem.inactive:
            totheight += (Fitmap.SPACER-10) #want room for 'is in pog' message.
        mainy = 10
        for i,pilimage in enumerate(pilbitmaps):
            glyphHeight = pilimage.size[1]
            ## The Face Sample:
            try:
                ## Get the data from RGBA PIL into wx.
                ## Thx, http://nedbatchelder.com/blog/200801/ \
                ## truly_transparent_text_with_pil.html
                image = wx.EmptyImage(*pilimage.size)
                image.SetData(pilimage.convert("RGB").tobytes() )
                #image.SetAlphaData(pilimage.convert("RGBA").tobytes()[3::4])
                image.SetAlphaData(pilimage.tobytes()[3::4])

                x = 16
                if i > 0: x *= 3 # Shift sub-faces over a little
                self.addPencil(
                    FaceImagePencil(
                        "face-{}".format(i),
                        x,
                        mainy,
                        image,
                        self)
                    )
                
                #forcederror() #to test the except
            except Exception as e:
                self.addPencil(
                    FaceErrorPencil(
                        "face-{}-error".format(i),
                        10,
                        mainy + 2,
                        e)
                    )

            ## The Caption: fam, style, name
            self.addPencil( 
                TextPencil( 
                    "face-{}-caption".format(i),
                    28,
                    mainy + glyphHeight + 8,
                    "{} - {} - [{}]".format(
                        self.fitem.family[i],
                        self.fitem.style[i],
                        self.fitem.name
                    ),
                    self.style,
                    points = 8)
                )

            ## Move TOP down to next BOTTOM (for next sub-face)
            mainy += glyphHeight +  Fitmap.SPACER


    def font_bitmap_pencils(self):
        ## Get a list of pilimages, for each subface: Some fonts 
        ## have multiple faces, and their heights.
        ## (For example TTC files.)
        ## REMEMBER: This loop is all FOR THIS ONE FONT ITEM.
        ## It only supplies pilimages for fonts it could open and
        ## render. So this font may indeed have nothing in the pilList[]
        ## after this loop.
        ## NOTE: generatePilFont sets the colour of the font bitmap!
        ## The color comes from fitem.inactive t/f
        #pillist = []
        #totheight = 0

        #widths = [Fitmap.MIN_FITEM_WIDTH]
        #for pilimage in self.fitem.generatePilFont():
        #    #Only fitems that have a successful pilimage appear in this loop
        #    #Broken pil images set badfont on the fitem, and do not yield a pilgimge.
        #    pillist.append( pilimage )
        #    totheight += pilimage.size[1] + Fitmap.SPACER
        #    widths.append(pilimage.size[0])

        #TODO -- back to doing too much.... fix me
        ## IF I can alter the grey/alpha *after* the pil bitmaps are drawn,
        ## then I can divorce the active/inactive thing form the rendering.
        ## That means I won't need to call it here... (because I call it
        ## manually in MinimalCreateFitmaps up in gui_Fitmap.py)
        self.generate_pil_bitmaps()

        ## Now that badfont is determined, we can fetch a colour:
        self.setStyle() #Go set the self.style
        fcol = self.style['fcol']

        ## Limit the minimum we allow.
        #if totheight < Fitmap.MIN_FITEM_HEIGHT:
        #    totheight = Fitmap.MIN_FITEM_HEIGHT
        totheight = max(self.pilheight, Fitmap.MIN_FITEM_HEIGHT) # right?

        if self.fitem.badfont:
            ## We have a badstyle to help us differentiate these.
            #totheight = Fitmap.MIN_FITEM_HEIGHT
            if self.fitem.inactive: totheight += 5 #Need more space
            retlist = self.info_or_badfont_pencils()

        ## It's *not* a badfont
        else:
            if self.fitem.inactive:
                totheight += (Fitmap.SPACER-10) #want room for 'is in pog' message.

            mainy = 10
            i = 0
            #print "fam:", self.fitem.family
            for pilimage in self.pilbitmaps:
                #print "!! :", pilimage
                glyphHeight = pilimage.size[1]
                try:
                    ## Get the data from PIL into wx.
                    ## Now with alpha! Thanks to:
                    ## http://nedbatchelder.com/blog/200801/truly_transparent_text_with_pil.html
                    ## http://wiki.wxpython.org/WorkingWithImages
                    image=None
                    #image = apply( wx.EmptyImage, pilimage.size )
                    image = wx.EmptyImage(*pilimage.size)
                    #opil = pilimage
                    #if self.fitem.inactive:
                    #    opil.putalpha(128) # not working as expected..
                    image.SetData(pilimage.convert("RGB").tobytes() )
                    #image.SetAlphaData(pilimage.convert("RGBA").tobytes()[3::4])
                    image.SetAlphaData(pilimage.tobytes()[3::4])
                    #image.Blur(2)
working here
                    fx,fy = self.calculate_top_left_adjustments( image, i, pilimage )
                    image = image.AdjustChannels(0,0,0,factor_alpha = 0.2)

                    faceBitmap = image.ConvertToBitmap()
                    #forcederror() #to test the except
                except Exception as e:
                    ## Oddballs or possible bad sub-face in a ttc font.
                    ##TODO: Include the error message somehow.
                    txt = _("This text cannot be drawn. Hey, it happens...")
                    fontbitmap = TextPencil( "cannotdraw", 10, mainy+2, txt, fcol,
                                    fpsys.config.points, style=wx.ITALIC)
                    raise
                    #self.queue( cannotdraw )
                else:
                    ## Place it into the main image, down a tad so it looks better.
                    x = 16
                    if i > 0: x *= 3 # Shift sub-faces over a little
                    fontbitmap = BitmapPencil( "facebitmap", x-fx, mainy-fy,
                                    faceBitmap, width = self.pilwidth )
                    #self.queue( fontbitmap )

                ## The font name/fam/style : fnfs
                txt = "%s - %s - [%s]" % (self.fitem.family[i],
                                          self.fitem.style[i], self.fitem.name)
                nfs = TextPencil( "namefamstyle", 28,
                                    mainy + glyphHeight + 8, txt, fcol, points=8 )
                #self.queue( nfs )

                ## Move TOP down to next BOTTOM (for next sub-face)
                mainy += glyphHeight +  Fitmap.SPACER

                ## Goto next face, if any.
                i += 1
            retlist = [ fontbitmap, nfs ]

        self.height = totheight
        #print self.fitem, self.height

        return retlist

    def active_inactive_pencils(self):
        ## Special INACTIVE (Font already in...) message:
        if self.fitem.inactive:
            x,y=(25,self.height-20) if self.fitem.badfont else (48,self.height-26)
            greentick = BitmapPencil( "bmpinactive", x-16, y-1, self.TICKSMALL)

            txt = self.fitem.activeInactiveMsg
            fcol = self.style['fcol']
            act_inact_message = TextPencil( "fntinactive", x+2, y, txt, fcol, points=10)
            return [ greentick, act_inact_message ]
        return None

    def selected_and_how_pencils(self):
        ## Draw the tick/cross if it's not a FILE_NOT_FOUND font (can't be found)
        #print "self.fitem.ticked:", self.fitem.ticked
        ## NB: FILE_NOT_FOUND is not available for installation!
        if self.fitem.badstyle != "FILE_NOT_FOUND":
            print "self.fitem.name ticked:", self.fitem.ticked
            if self.fitem.ticked:
                self.TICKMAP = self.parent.parent.TICKMAP
                return BitmapPencil( "tickmap", 20, 5, self.TICKMAP)
        return EmptyPencil(id = "tickmap")
        

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

    def xxx_calculate_top_left_adjustments(self, image, i, pilimage):
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


    def prepareBitmap( self ):
        """
        This is where all the drawing code goes. It gets the font rendered
        from the FontItems (via PIL) and then draws a single Fitmap.

        Info or Bad Font item layers:
        Layer #	
        0	Colour gradient bottom to top
        1	Font info text
        2	Icon and message

        For the actual font bitmaps:
        Normal Font item layers:
        Layer #	
        0	Gradient gray up to white
        1	Each face bitmap, and the caption under it.
        2	The Green tick and "This font is in __" text
        3	Red tick or cross or nothing
        4	Charmap button

        Blocks relate to these layers like this:
        Layer   Variable/thing  Set
                to watch.       mask
        L 1,2   activechanged   A
        L 1     textchanged     B
        L 1     pointschanged   B
        L 3     tickedchanged   C

        Layer 0 is composed in usePencils()
        Layer 4 is composed in onPaint()

        The entire bitmap is reset in usePencils()

        onPaint() --> draws if there's a self.bitmap

        The flow is prepareBitmap() --> usePencils() --> onPaint()
        I am not sure exactly when/how onPaint fires.
        """




        #print "prepareBitmap runs for:", self

        ## InfoFontItem is a fake font item for the purposes
        ## of saying "There are no fonts to see here."
        if isinstance( self.fitem, fontcontrol.InfoFontItem ):
            self.style=Fitmap.styles['INFO_FONT_ITEM']
            self.qpencils(self.info_or_badfont_pencils( isinfo=True ))
            self.usePencils(Fitmap.MIN_FITEM_HEIGHT + 20)
            return

        ## Go determine my draw state. 
        # Initial run has all set.
        self.drawstate.determine()
        

        self.drawstate.watch(
                {"textchanged": lambda: fpsys.config.text,
                    "pointschanged", lambda: fpsys.config.points,
                    "tlchanged", lambda: fpsys.config.ignore_adjustments,
                    "activechanged", lambda: self.fitem.inactive,
                    "tickedchanged", lambda: self.fitem.ticked})


        if self.drawstate.isblock("A"):
            # Block A: Always erase and make new face sample pencils
            self.gen_face_samples()

        if self.drawstate.isblock("B"):
            # Block B: Reuse if, else make new footer pencil
            if "footer" not in self.drawDict:
                self.genFooter()

        if self.drawstate.isblock("C"):
            # Block C: Resuse if, else make new ticked pencil
            if "ticked" not in self.drawDict:
                self.genTicked()
    
        ## If we actually have something to draw...
        if self.drawstate > 0:
            ## Make one big bitmap to house one or more faces (subfaces)
            ## Draw it all - via the pencils. Also makes the memDc and returns
            ## it so we can do some last-minute stuff later.
            ## NOTE: By drawing into memDc, we are drawing into self.bitmap
            memDc = self.usePencils(self.height)
            
            if memDc:
                ## Now a dividing line
                memDc.SetPen( wx.Pen( (180,180,180),1 ) )#black, 1 ) ) 
                memDc.DrawLine( 0, self.height-1, self.bitmap.GetWidth(), self.height-1 )

        # Capture the state
        ds = self.drawstate
        # Reset the state
        self.drawstate.state = 0

        #Return the state. See MinimalCreateFitmaps in gui_ScrolledFontView.py
        return ds

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






