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
    ## A class var
    textExtentsDict = {}
    def __init__( self, id, x, y ):
        self.id = id; self.x = x; self.y = y
        self._old = False
        self._drawlist=[] #my own pencils

    def queue(self, pencil):
        pencil.deploy()
        self._drawList.append(pencil)

    def setold(self,tf):
        self._old=tf
    def isold(self): return self._old
    def getwidth(self): pass
    def deploy(self): pass
    def draw(self, memdc): pass

    def _inspect(self, you):
        print "Inspecting:", self.__class__
        print '{:>20} {:>20} {:>20}'.format("","self", "other")
        for k,v in self.__dict__.iteritems():
            if not k.startswith("_"):
                youv = you.__dict__.get(k)
                if k=="parent": v=id(v); youv=id(youv)
                tf = v==youv
                v = u"{}".format(v)
                v = v[-1*min(max(len(v),20),20):]
                youv = u"{}".format(youv)
                youv = youv[-1*min(max(len(youv),20),20):]
                print '{:>20}={:>20} {:>20} :{}'.format(k, v, youv, tf)

    ## Yet another stackoverflow gem:
    ## https://stackoverflow.com/questions/20498436/most-efficient-way-of-comparing-the-contents-of-two-class-instances-in-python
    ## I had to alter it somewhat.
    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        attributes = self.__dict__
        if attributes:
            self._inspect(other)
            d = float('NaN') # d won't compare equal, even with itself
            # exclude underscore attributes and compare all others
            return all(self.__dict__.get(a, d) == other.__dict__.get(a, d) for a in attributes if not a.startswith("_"))
        return self.__dict__ == other.__dict__


class DrawTextPencil(Pencil):
    def __init__( self, id, x, y, txt, fcol, points, style=wx.NORMAL, weight=wx.NORMAL, encoding = wx.FONTENCODING_DEFAULT ):
        Pencil.__init__(self, id, x, y)
        self.txt = txt
        self.fcol = fcol
        self.font =  wx.Font( points, fpsys.DFAM, style, weight, encoding=encoding )

        #Defer this... don't do it in __init__
        self._width = 0 #self.__mf()[0]

    def getwidth(self): return self._width

    def deploy(self):
        """
        Measure a line of text in my font. Return a wx.Size
        Cache these widths in Pencil class variable.
        """
        ## Do we have a cached size for this txt?
        if self.txt in Pencil.textExtentsDict:
            #print "Got from cache:",  Pencil.textExtentsDict[self.txt]
            return Pencil.textExtentsDict[self.txt] #yep!
        dc = wx.ScreenDC()
        dc.SetFont( self.font )
        try:
            sz = dc.GetTextExtent( self.txt )
        except:
            sz = (Fitmap.MIN_FITEM_WIDTH,Fitmap.MIN_FITEM_HEIGHT)
        Pencil.textExtentsDict[self.txt] = sz # cache it in my parent
        
        self._width = sz[0]
        #return sz[0]

    def draw(self, memdc):
        memdc.SetTextForeground( self.fcol )
        memdc.SetFont( self.font )
        memdc.DrawText( self.txt, self.x, self.y )

class DrawBitmapPencil(Pencil):
    def __init__( self, id, x, y, bitmap, width=0 ):
        Pencil.__init__(self, id, x, y)
        self.bitmap = bitmap
        self.width = width
    def getwidth(self): return self.width
    def draw(self, memdc):
        memdc.DrawBitmap( self.bitmap, self.x, self.y, True )

class InactiveMessagePencil(Pencil):

class TickMapPencil(Pencil):
    def __init__(self,id, fitmap):
        Pencil.__init__(self, id, 0, 0)
        # private
        self._fitem = fitmap.fitem
        self._fitmap = fitmap
        # state comparable
        self.badfont = self._fitem.badfont
        self.inactive = self._fitem.inactive
    def deploy(self):
        fm = self.fitmap; fi = self._fitem
        fcol = fm.fcol
        bitmap = fm.TICKSMALL
        if fi.inactive:
            self.x, self.y = (25, fm.height-20) if fi.badfont else (48, fm.height-26)

            self._drawlist.append( DrawBitmapPencil( "bmpinactive", x-16, y-1, self.bitmap) )

            txt = self.txt
            self._drawlist.append( DrawTextPencil( "fntinactive", x+2, y, txt, fcol, points=10) )
        
class PilFontPencil(Pencil):
    def __init__(self, id, points, text, fitmap):
        Pencil.__init__(self, id, 0, 0)
        self.points = points
        self.text = text
        self.parent = fitmap
        self.inactive = fitmap.fitem.inactive
        #private attrs
        self._fitem = fitmap.fitem
        self._totheight = 0
        self._maxpilwidth = []
        self._pillist=[]

    def deploy(self):
        ## Get a list of pilimages, for each subface: Some fonts 
        ## have multiple faces, and their heights.
        ## (For example TTC files.)
        ## REMEMBER: This loop is all FOR THIS ONE FONT ITEM.
        ## It only supplies pilimages for fonts it could open and
        ## render. So this font may indeed have nothing in the pilList[]
        ## after this loop.
        ## NOTE: generatePilFont sets the colour of the font bitmap!
        ## The color comes from fitem.inactive t/f
        myfitem = self._fitem 

        self._maxpilwidth = [Fitmap.MIN_FITEM_WIDTH]
        for pilimage in myfitem.generatePilFont( self.points, self.text ):
            #Only fitems that have a successful pilimage appear in this loop
            #Broken pil images set badfont on the fitem, and do not yield a pilgimge.
            self._pillist.append( pilimage )
            self._totheight += pilimage.size[1] + Fitmap.SPACER
            self._maxpilwidth.append(pilimage.size[0])

        self.parent.setStyle() # reaches into the fitem to do this.
        fcol = self.parent.style['fcol']
        bcol = self.parent.style['bcol']

        if not myfitem.badfont:
            mainy = 10
            i = 0
            for pilimage in self._pillist:
                ## We don't need pilwidth here as we already have the max
                ## from up-code in the for loop.
                ## We do use the glyphHeight
                pilwidth, glyphHeight = pilimage.size
                try:
                    ## Get the data from PIL into wx.
                    ## Now with alpha! Thanks to:
                    ## http://nedbatchelder.com/blog/200801/truly_transparent_text_with_pil.html
                    ## http://wiki.wxpython.org/WorkingWithImages
                    image=None
                    #image = apply( wx.EmptyImage, pilimage.size )
                    image = wx.EmptyImage(*pilimage.size)
                    image.SetData(pilimage.convert( "RGB").tobytes() )
                    image.SetAlphaData(pilimage.convert("RGBA").tobytes()[3::4])

                    fx,fy = self.parent.CalculateTopLeftAdjustments( image, i, pilimage )

                    faceBitmap = image.ConvertToBitmap()
                    #forcederror() #to test the except
                except Exception as e:
                    ## Oddballs or possible bad sub-face in a ttc font.
                    ##TODO: Include the error message somehow.
                    txt = _("This text cannot be drawn. Hey, it happens...")
                    cannotdraw = DrawTextPencil( "cannotdraw", 10, mainy+2, txt, fcol,
                                    fpsys.config.points, style=wx.ITALIC)
                    self.queue( cannotdraw )
                else:
                    ## Place it into the main image, down a tad so it looks better.
                    x = 16
                    if i > 0: x *= 3 # Shift sub-faces over a little
                    fontbitmap = DrawBitmapPencil( "facebitmap", x-fx, mainy-fy,
                                    faceBitmap, width = max(self._maxpilwidth) )
                    self.queue( fontbitmap )

                ## The font name/fam/style : fnfs
                txt = "%s - %s - [%s]" % (myfitem.family[i],
                                          myfitem.style[i], myfitem.name)
                nfs = DrawTextPencil( "namefamstyle", 28,
                                    mainy + glyphHeight + 8, txt, fcol, points=8 )
                self.queue( nfs )

                ## Move TOP down to next BOTTOM (for next sub-face)
                mainy += glyphHeight +  Fitmap.SPACER

                ## Goto next face, if any.
                i += 1

    def totheight(self): return self._totheight

    def getwidth(self): return max(self._maxpilwidth)

    def draw(self, memdc):
        for pencil in self._drawlist:
            pencil.draw(memdc)


class Fitmap(wx.lib.statbmp.GenStaticBitmap):
    """
    This class is a bitmap of a font - it detects events and
    displays itself.

    Sept 2009
    Added code to adjust top-left of displayed sample text.

    Oct 2009
    Added a 'button' to open a character map viewer.
    """

    ## This class-level dict is a kind of "style sheet" to use in fitmap drawing.
    styles={
            'FILE_NOT_FOUND':
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
                    'fcol'   : (98,98,98), #128,128,128), 
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

        self.widestpilimage = 0 # July 2016: The final, drawn, width of this fitem.

        ## The charmap button
        self.CHARMAP_BUTTON_OVER = self.FVP.BUTTON_CHARMAP_OVER
        self.CHARMAP_BUTTON_OUT = self.FVP.BUTTON_CHARMAP
        ## Point to the handler for the signal re charmap button
        self.cmb_overout = OverOutSignal( self.charmap_button_signal )

        self.entire_fitmap_unchanged = False

        ## Go draw the fitmap into a memory dc
        #self.drawlist = []
        self.drawDict = collections.OrderedDict()

        #self.dcw = []
        self.bitmap = None
        self.prepareBitmap()
        sz = (self.bitmap.GetWidth(), self.bitmap.GetHeight())

        ## Now I can calc the y value of the button.
        self.cmb_rect=wx.Rect(0,sz[1]-40,19,32)
        self.height =  0

        ## init my parent class 
        ## This also sets the SIZE of the fitmap widget.
        ## Calling DoGetBestSize on it will return that size.
        wx.lib.statbmp.GenStaticBitmap.__init__(self, parent, -1, self.bitmap, (0,0), sz)

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



    def usePencils(self, h):
        """
        Makes a new mem dc with the best size.
        Loops the drawlist and uses the Pencils to draw text and bitmaps
        Clears the drawlist.
        Clears the dcw (dc width list)
        Returns a memdc for sundry use.
        """

        #if all(the pencils are old) then return
        if all( p.isold() for p in self.drawDict.values()): return None

        #w = max(self.dcw)
        w = max((p.getwidth() + int(1.5 * p.x)) for p in self.drawDict.values())

        bitmap = wx.EmptyImage( w,h ).ConvertToBitmap()
        memDc = wx.MemoryDC()
        memDc.SelectObject( bitmap )
        memDc.SetBackground( wx.Brush( wx.Colour(255,255,255,wx.ALPHA_OPAQUE), wx.SOLID) )
        memDc.Clear()
        self.bitmap = bitmap #record this for the init

        ## Draw it all - via the pencils
        for pencil in self.drawDict.values():
            pencil.draw(memDc)
            #print "drawing:", pencil.id

        ## Now empty the drawlist
        #del self.drawDict
        #??? self.drawDict.clear()

        ## Also empty the dcw list
        #del self.dcw[:]

        return memDc

    def queue(self, newpencil):
        """
        Given a pencil, this will append it to the drawDict.
        If there's a width in the pencil, that goes into the
        dcw list (a space on the right-hand side is calculated by
        n times the x coord added to the width)
        """
        print
        print "queue with:{} id:{}".format( newpencil, newpencil.id)
        #def _growdcw(pencil):
        #    w = pencil.getwidth()
        #    if w > 0: self.dcw.append( w + int(1.5 * pencil.x) )

        oldpencil = self.drawDict.get(newpencil.id, None)
        if oldpencil:
            print "  has an oldpencil"
            ## And.. they are the same...
            if newpencil == oldpencil:
                print "Keeping oldpencil:", oldpencil.id
                #print "_maxpilwidth:", oldpencil._maxpilwidth
                oldpencil.setold(True)
                #_growdcw(oldpencil)
                #del newpencil
                return oldpencil
            else:
                del oldpencil
                
        ## So, there' no oldpencil or the newpencil differs
        ## This: deploy(), and add it to my drawDict.
        newpencil.deploy()
        #_growdcw(newpencil)
        ## .update will also add if key is not found.
        ## The oldpencil's slot in the dict is held by the .id
        ## therefore we are gonna replace it by update.
        print "Using newpencil:{} id:{}".format(newpencil, newpencil.id)
        self.drawDict.update( {newpencil.id : newpencil} )
        print "drawDict is:"
        print self.drawDict
        #import pdb; pdb.set_trace()
        return newpencil


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
        I make the sweeping fiat that no badfonts will get a button.

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


    def prepareBitmap( self ):
        """
        This is where all the drawing code goes. It gets the font rendered
        from the FontItems (via PIL) and then draws a single Fitmap.
        """

        ##Sept 2017
        ## My thinking is that:
        ## If this routine can somehow determine that the visual state is about to change
        ## (from what it was last time), then we can know if we can return early -- i.e.
        ## reuse the current bitmap as-is.
        ## If so, then we can save a lot of time in creating fitmaps in the MinimalCreateFitmaps
        ## method of gui_ScrolledFontView
        ##
        ## Idea - What if the pencils can make a state "stamp" we can match on?
        ## It's not ideal because the pencils happen after a lot of work
        ## on x,y coords and colours and so on..
        ## Esp problematic with faceBitmap ... Damn ...
        ##  if isinstance(o, (set, tuple, list)): return tuple([make_hash(e) for e in o])


        #print "prepareBitmap runs for:", self
        ## Is this a normal FontItem, or an InfoFontItem?
        ## InfoFontItem is a fake font item for the purposes
        ## of saying "There are no fonts to see here."
        if isinstance( self.fitem, fontcontrol.InfoFontItem ):
            self.style=Fitmap.styles['INFO_FONT_ITEM']
            self.drawInfoOrError( isinfo=True )
            ##Sept 2017:Added some to height to cater for newlines in 
            ## the info text. See class InfoFontItem in fontcontrol.py
            self.usePencils(Fitmap.MIN_FITEM_HEIGHT + 20)
            return

        points, text = fpsys.config.points, " " + fpsys.config.text + "  "
        #pilpencil = PilFontPencil( "pilpencil", points, text, self ) 

        # queue will cause PilFontPencil to draw the entire shebang
        # into a bitmap.
        pilpencil = self.queue(PilFontPencil( "pilpencil", points, text, self ))

        totheight = pilpencil.totheight()

        print
        print pilpencil#.getwidth()
        print 

        ## Limit the minimum we allow.
        if totheight < Fitmap.MIN_FITEM_HEIGHT:
            totheight = Fitmap.MIN_FITEM_HEIGHT

        # badfont has been set by the PilFontPencil
        if self.fitem.badfont:
            ## We have a badstyle to help us differentiate these.
            totheight = Fitmap.MIN_FITEM_HEIGHT
            if self.fitem.inactive: totheight += 5 #Need more space
            self.drawInfoOrError( )

        if self.fitem.inactive:
            totheight += (Fitmap.SPACER-10) #want room for 'is in pog' message.

        ## Record the calculated height
        self.height = totheight
        
        #self.setStyle() # was done in PilFontPencil's deploy() method
        fcol = self.style['fcol']
        bcol = self.style['bcol']

        ## Special INACTIVE (Font already in...) message:
        #self.queue(InactiveMessagePencil('imp', self.height, self.fitem.badfont, self.fitem.inactive, fcol, self.fitem.activeInactiveMsg, self.TICKSMALL))
        self.queue(InactiveMessagePencil('imp', self ))
        if self.fitem.inactive:
            x,y=(25,self.height-20) if self.fitem.badfont else (48,self.height-26)

            self.queue( DrawBitmapPencil( "bmpinactive", x-16, y-1, self.TICKSMALL) )

            txt = self.fitem.activeInactiveMsg
            self.queue( DrawTextPencil( "fntinactive", x+2, y, txt, fcol, points=10) )

















        ## Draw the tick/cross if it's not a FILE_NOT_FOUND font (can't be found)
        ## NB: FILE_NOT_FOUND is not available for installation!
        if self.fitem.badstyle != "FILE_NOT_FOUND":
            #print "self.fitem.name ticked:", self.fitem.ticked
            if self.fitem.ticked:
                #print " tickmap is tick:", self.TICKMAP

                self.TICKMAP = self.parent.parent.TICKMAP
                self.queue( DrawBitmapPencil( "tickmap", 20, 5, self.TICKMAP) )

        ## Make one big bitmap to house one or more faces (subfaces)
        ## Draw it all - via the pencils. Also makes the memDc and returns
        ## it so we can do some last-minute stuff later.
        ## NOTE: By drawing into memDc, we are drawing into self.bitmap


        memDc = self.usePencils( totheight )
        
        if memDc:
            ## Now a dividing line
            memDc.SetPen( wx.Pen( (180,180,180),1 ) )#black, 1 ) ) 
            memDc.DrawLine( 0, self.height-1, pilpencil.getwidth(), self.height-1 )

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

        #Sept 2017: Move it all over by an offset
        offx = 20

        icon = self.style['icon']
        if icon:
            Icon = self.FVP.__dict__[icon] #See gui_FontView.py ~line 97
            ix,iy = (6,10) if isinfo else (2,6)

            ix += offx
            self.queue( DrawBitmapPencil( "infoicon", ix, iy, Icon) )

        ## Prep and measure the texts to be drawn. Add them to drawlist.
        fcol = self.style['fcol']

        textTup = self.fitem.InfoOrErrorText()

        ## prep the two lines of text
        tx,ty = (46,15) if isinfo else (38 , 20)

        tx += offx
        self.queue( DrawTextPencil( "tup0", tx, ty, textTup[0], fcol, points=12, weight=wx.BOLD) )

        tx,ty = (46,40) if isinfo else (5 ,40)

        tx += offx
        self.queue( DrawTextPencil( "tup1", tx, ty, textTup[1], fcol, points=10 ) )
