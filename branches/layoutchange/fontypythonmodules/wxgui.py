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

import locale
import strings
import fontybugs
import fpsys # Global objects
import fpversion
## Now, bring in all those big modules
import wx


## June 25th 2016
## Remarking these two lines because they are causing a segfault:
##  ../src/common/stdpbase.cpp(62): assert "traits" failed in Get(): 
##  create wxApp before calling this
##  Segmentation fault (core dumped)
##
##  I do not know how to test or fix this, hence simply removing it.
##  AFAICT, stock buttons will be in the system language.
##
## Setup wxPython to access translations : enables the stock buttons.
#langid = wx.LANGUAGE_DEFAULT # Picks this up from $LANG
#mylocale = wx.Locale( langid )

## Fetch my own pubsub stuff
from pubsub import * #I want all the topics.
ps = CPubsub()

## Fetch the dialogue classes *About, Settings, Help, etc.*
import dialogues

from gui_FontSources import *
from gui_FontView import *
from gui_PogTargets import *

from fpwx import setup_fonts_and_colours, label, wxbmp, icon, SYSFONT






## Variables to do with the DismissablePanels
## and to map the close (X) button id to the
## state flags we use to show/hide the panels
flag_normal = 1
flag_help = 2
flag_about = 4
flag_settings = 8
id_from_flag   = {flag_help:201, flag_about:202, flag_settings:101}
flag_from_id = {v:k for k,v in id_from_flag.iteritems()} #invert it!

class DismissablePanel(wx.Panel):
    """
    Only for subclassing.
    Provides a bar with an icon, title and an X close button.
    Under that is .. whatever: usually a sizer.
    """
    def __init__(self, parent, flag, someicon=None, somelabel="Say something man!"):
        id = id_from_flag[flag]
        wx.Panel.__init__(self, parent, id, style=wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        self.flag = flag

        ## Go fetch the .. whatever 
        whatever = self.__post_init__()

        l = label( self, somelabel, size="points_xx_large", weight=wx.FONTWEIGHT_BOLD )
        i = icon( self, someicon ) if someicon else (1,1)

        self.x_button = wx.Button(self,id, label="X", style = wx.NO_BORDER | wx.BU_EXACTFIT)
        ## No Bind here because the button's event will shoot up the tree and arrive in the
        ## main frame, where we catch it.

        self.x_button.SetToolTipString( _("Dismiss") )

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add( i, 0, wx.EXPAND )
        hbox.Add( l, 1, wx.EXPAND )
        hbox.Add( self.x_button, 0, wx.ALIGN_RIGHT | wx.ALIGN_TOP | wx.BOTTOM, border = 4 )
        hbox.Add( (8,8),0)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add( hbox, 0, wx.EXPAND | wx.TOP , border = 8 ) #Wanted more space above.
        self.vbox.Add( whatever, 1, wx.EXPAND)
        self.SetSizer( self.vbox )
        self.Layout()

    def __post_init__(self):
        pass


## Help file stuff
## Moved from dialogues on 31 OCt 2017
import wx.html as html
## langcode = locale.getlocale()[0] # I must not use getlocale...
## This is suggested by Martin:
loc = locale.setlocale(locale.LC_CTYPE) # use *one* of the categories (not LC_ALL)
## returns something like 'en_ZA.UTF-8'
if loc is None or len(loc) < 2:
    langcode = 'en'
else:
    langcode = loc[:2].lower()# This is going to cause grief in the future...

class HtmlPanel(DismissablePanel):
    ## Weird stuff:
    class MyHtmlWindow(html.HtmlWindow):
        def __init__(self, parent):
            html.HtmlWindow.__init__(self, parent)
            if "gtk2" in wx.PlatformInfo or "gtk3" in wx.PlatformInfo:
                self.SetStandardFonts()    
    
    def __init__(self, parent):
        DismissablePanel.__init__(self, parent, flag_help, somelabel=_("Help! Help! I'm being repressed!") ) 

    def __post_init__(self):
        self.html = HtmlPanel.MyHtmlWindow(self)
        ## Find localized help, or default to English.
        packpath = fpsys.fontyroot
        helppaf = os.path.join(packpath, "help", langcode, "help.html")
        if not os.path.exists( helppaf ):
            helppaf = os.path.join(packpath, "help", "en", "help.html")
        self.html.LoadPage( helppaf )        
        return self.html


class AboutPanel(DismissablePanel):
    def __init__(self, parent):
        DismissablePanel.__init__(self, parent, flag_about, somelabel=_("About Fonty") )

    def __post_init__(self):
        nb = wx.Notebook(self, -1, style=0)

        nbabout_pane_1 = wx.Panel(nb, -1)
        nbabout_pane_2 = wx.Panel(nb, -1)
        nbabout_pane_3 = wx.Panel(nb, -1)

        fplogo = icon(nbabout_pane_1, 'aboutfplogo')

        AboutText = wx.StaticText(
                nbabout_pane_1, -1, strings.aboutText, style = wx.TE_MULTILINE)

        emaillink = wx.TextCtrl(
            nbabout_pane_1, -1, strings.contact, size =(200,-1 ), style = wx.TE_READONLY)

        GPL_TEXT = wx.TextCtrl(
                nbabout_pane_2, -1, strings.GPL, style=wx.TE_MULTILINE|wx.TE_READONLY)

        THANKS = wx.TextCtrl(
                nbabout_pane_3, -1, strings.thanks, style=wx.TE_MULTILINE|wx.TE_READONLY)

        # Once was done in wxGlade. Argh. What a mess....
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_thanks = wx.BoxSizer( wx.HORIZONTAL )

        sizerPane1 = wx.BoxSizer(wx.HORIZONTAL)
        sizerPane1.Add(fplogo, 0, 0, 0)

        textsizer = wx.BoxSizer(wx.VERTICAL)
        textsizer.Add(AboutText, 0, wx.ALIGN_LEFT | wx.ALL, border = 10)
        textsizer.Add(emaillink, 0, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, border = 10)

        sizerPane1.Add(textsizer, 0, wx.ALIGN_TOP, 0)
        
        #ABOUT
        nbabout_pane_1.SetSizer(sizerPane1)
        sizerPane1.Fit(nbabout_pane_1)
        sizerPane1.SetSizeHints(nbabout_pane_1)
        
        sizer_3.Add(GPL_TEXT,1, wx.EXPAND, 0)

        #LICENCE
        nbabout_pane_2.SetSizer(sizer_3)
        sizer_3.Fit(nbabout_pane_2)
        sizer_3.SetSizeHints(nbabout_pane_2)
        
        ## THANKS
        sizer_thanks.Add( THANKS,1, wx.EXPAND | wx.ALL, border = 6 )
        nbabout_pane_3.SetSizer( sizer_thanks )
        sizer_thanks.Fit( nbabout_pane_3 )
        sizer_thanks.SetSizeHints( nbabout_pane_3 )
        
        nb.AddPage(nbabout_pane_1, _("About"))
        nb.AddPage(nbabout_pane_3, _("Thanks"))
        nb.AddPage(nbabout_pane_2, _("Licence"))
        
        sizer_1.Add(nb, 1, wx.EXPAND, 0)
        
        nbabout_pane_1.SetFocus()
        return sizer_1




class SettingsPanel(DismissablePanel):
    def __init__(self, parent):
        DismissablePanel.__init__(self, parent, flag_settings, somelabel=_("Settings"))

    def _set_values(self):
        self.inputPageLen_val = fpsys.config.numinpage
        self.inputPointSize_val = fpsys.config.points
        self.inputSampleString_val = fpsys.config.text
        self.chkAdjust_val = fpsys.config.ignore_adjustments
        self.CMC_val = fpsys.config.CMC

    def show_or_hide(self,evt):
        """Event bound in MainFrame, fires when I hide or show."""
        if self.IsShown():
            self._update_form()

    def _update_form(self):
        self._set_values()
        # Most of the controls will "remember" their last setting.
        # (This is all show/hide anyway.)
        # The only one that can change outside the settings is:
        # The point size - can change by the wheel - hence update it:
        self.inputPointSize.SetValue( self.inputPointSize_val )

    def __post_init__(self):
        self._set_values()

        label_1 = label(self, _("Sample text:"), size="points_normal")
        self.inputSampleString = wx.TextCtrl(self, -1, self.inputSampleString_val, size = (200, -1)) 
        self.inputSampleString.SetFocus()
        
        label_2 = label(self,_("Point size:"), size="points_normal")
        self.inputPointSize = wx.SpinCtrl(self, -1, "")
        self.inputPointSize.SetRange(1, 500)
        self.inputPointSize.SetValue( self.inputPointSize_val )
        
        label_3 = label(self, _("Page length:"), size="points_normal")
        self.inputPageLen = wx.SpinCtrl(self, -1, "")
        self.inputPageLen.SetRange(1, 5000) # It's your funeral!
        self.inputPageLen.SetValue( self.inputPageLen_val ) 
        self.inputPageLen.SetToolTip( wx.ToolTip( _("Beware large numbers!") ) )


        ## Sept 2009 - Checkbox to ignore/use the font top left adjustment code
        self.chkAdjust = wx.CheckBox(self, -1, _("Disable font top-left correction."))
        #self.chkAdjust.SetValue(fpsys.config.ignore_adjustments) 
        self.chkAdjust.SetValue( self.chkAdjust_val ) 
        self.chkAdjust.SetToolTip( wx.ToolTip( _("Disabling this speeds font drawing up a fraction, but degrades top-left positioning.") ) )

        # The Character map choice
        self.CMC = self.CMC_val #fpsys.config.CMC
        if self.CMC.APPS_ARE_AVAILABLE:
            self.CHOSEN_CHARACTER_MAP = self.CMC.GET_CURRENT_APPNAME()
            rb_or_nada = wx.RadioBox(
                    self, -1, _("Available character map viewers"), wx.DefaultPosition, wx.DefaultSize,
                    self.CMC.QUICK_APPNAME_LIST, 1, wx.RA_SPECIFY_COLS )
            rb_or_nada.SetSelection( self.CMC.QUICK_APPNAME_LIST.index( self.CHOSEN_CHARACTER_MAP ))

            self.Bind(wx.EVT_RADIOBOX, self.EvtRadioBox, rb_or_nada)
            rb_or_nada.SetToolTip(wx.ToolTip( _("Choose which app to use as a character map viewer.") ))
        else:
            self.CHOSEN_CHARACTER_MAP = None
            rb_or_nada = label(self,_("Could not find a supported character viewer."), size="points_normal")

        settings_sizer = wx.FlexGridSizer( cols=2, hgap=5, vgap=8 )

        settings_sizer.Add(label_1, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
        settings_sizer.Add(self.inputSampleString, 1, wx.EXPAND )

        settings_sizer.Add(label_2, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
        settings_sizer.Add(self.inputPointSize, 1 )

        settings_sizer.Add(label_3, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
        settings_sizer.Add(self.inputPageLen, 1 )

        settings_sizer.Add((1,1),0)
        settings_sizer.Add(self.chkAdjust, 1)

        settings_sizer.Add((1,1),0)
        settings_sizer.Add(rb_or_nada, 1)

        ## Make an "apply" button. Click gets caught in MainFrame.
        btn = wx.Button(self, wx.ID_APPLY)
    
        ## Make a 'buffer' to keep the insides away from the edges of the frame
        b = wx.BoxSizer( wx.VERTICAL )
        b.Add( settings_sizer, 0, wx.EXPAND | wx.ALL,  border=10 )
        b.Add( btn, 0, wx.ALL, border=10)
        return b

    def EvtRadioBox(self, event):
        self.CHOSEN_CHARACTER_MAP = self.CMC.QUICK_APPNAME_LIST[event.GetInt()]










class StatusBar(wx.StatusBar):
    """
    The status bar
    """
    def __init__(self, parent):
        wx.StatusBar.__init__(self, parent, -1) # default style is good

        ##Sept2017
        ## Test if there's a need to warn about missing .fonts dir.
        try:
            fpsys.iPC.probeNoFontsDirError()
        except fontybugs.NoFontsDir as e:
            no_fonts_dir = True
            shorterr = e.short_unicode_of_error()
        else:
            no_fonts_dir = False

        ## Field 1 is Welcome...
        ## Field 2 is normal conversation.
        ## Field 3 <if missing user fonts dir> is the warning message.
        ## Last field "gripper" (32px)
        self.SetFieldsCount( 4 if no_fonts_dir else 3 )

        self.SetStatusText( _("Welcome to Fonty Python, vers %s") % fpversion.version, 0)

        if no_fonts_dir:
            self.SetStatusText( shorterr, 2)
            self.SetStatusWidths([300,-2,-1,32])
            #self.SetStatusStyles([wx.SB_SUNKEN]*3) #SB_SUNKEN is not available to me. 
        else:
            self.SetStatusWidths([300,-2,32])
            #self.SetStatusStyles([wx.SB_SUNKEN]*2)

    def Report(self, msg):
        self.SetStatusText(msg, 1)


class MainFrame(wx.Frame):

    """
    The main frame for the app.
    """
    def __init__(self,parent,title) :
        ## Draw the frame
        title = title + "   -   " + locale.getpreferredencoding()
        wx.Frame.__init__(self,parent,-1,title,fpsys.config.pos,fpsys.config.size)

        #print "Main frame:", self.GetSizeTuple()[0]

        ## Try to show an icon
        ## Oct 2017: Seems Unity (at least) doesn't even bother...
        try:
            i = wx.EmptyIcon()
            i.CopyFromBitmap( wxbmp('fplogo'))
            self.SetIcon(i)
        except:
            pass


        ## STATUS BAR
        ## ---------------------------------------
        self.sb = StatusBar(self)
        self.SetStatusBar(self.sb)

        ## MENUS
        ## ---------------------------------------
        self.menuBar = wx.MenuBar()

        ## FILE MENU : Changed to "Tools" menu Sep 2009
        menu1 = wx.Menu()
        menu1.Append(id_from_flag[flag_settings], _("&Settings\tCtrl+S"), _("Change settings"))
        menu1.AppendSeparator()
        ## Jan 18 2008
        menu1.Append( 102, _("&Check fonts"), _("Find those fonts that crash Fonty.") )
        menu1.Append( 103, _("&Purge Pog.See TogglePurgeMenuItem for actual string."), _("Remove all ghost fonts from the selected Pog.") )

        self.MENUPURGE = menu1

        self.exit = menu1.Append(104, _("&Exit"), _("Close the app"))
        self.menuBar.Append(menu1, _("&Tools"))


        ## SELECT MENU: June 2009
        menu3 = wx.Menu()
        menu3.Append( 301, _("&Select ALL the source fonts"), _("Select ABSOLUTELY ALL the fonts in the chosen source."))
        menu3.Append( 302, _("&Clear ENTIRE selection"), _("Clear the selection completely.") )
        self.menuBar.Append(menu3, _("&Selection"))
        self.MENUSELECTION = menu3

        ## HELP MENU
        menu2 = wx.Menu()
        menu2.Append(id_from_flag[flag_help], _("H&elp\tF1"))
        menu2.Append(id_from_flag[flag_about], _("&About"))
        self.menuBar.Append(menu2, _("&Help"))

        self.SetMenuBar(self.menuBar)

        ## Setup the ESC key and the LEFT / RIGHT keys
        accel = wx.AcceleratorTable([
            (wx.ACCEL_NORMAL, wx.WXK_ESCAPE, self.exit.GetId()),
            (wx.ACCEL_CTRL, wx.WXK_RIGHT, wx.ID_FORWARD),
            (wx.ACCEL_CTRL, wx.WXK_LEFT, wx.ID_BACKWARD)
            ])
        self.SetAcceleratorTable(accel)


        ## Do this generic bind for all menu events now.
        ## Then specific ones afterwards; else this one supercedes them.
        ## This is for the menus that open DismissablePanels:
        ## Help, About, Settings
        self.Bind(wx.EVT_MENU, self.toggle_dismissable_panel)


        ## Bind the Left and Right key shortcuts.	
        self.Bind(wx.EVT_MENU, self.OnAccelKey, id=wx.ID_FORWARD )
        self.Bind(wx.EVT_MENU, self.OnAccelKey, id=wx.ID_BACKWARD )

        ## The frame's close window button.
        self.Bind( wx.EVT_CLOSE, self.onHandleESC )

        ## Bind events for the menu items
        self.Bind(wx.EVT_MENU, self.onHandleESC, self.exit)
        self.Bind(wx.EVT_MENU, self.menuCheckFonts, id = 102 )
        self.Bind(wx.EVT_MENU, self.menuPurgePog, id = 103 )

        # June 2009
        self.Bind(wx.EVT_MENU, self.menuSelectionALL, id=301)
        self.Bind(wx.EVT_MENU, self.menuSelectionNONE, id=302)

        ## Nov 2017
        ## Catch all stray button events: This is dealing with the 
        ## close (X) button of the DismissablePanels at the moment.
        self.Bind(wx.EVT_BUTTON,self.toggle_dismissable_panel)

        ## Catch the Apply button in the settings panel.
        ## Placed *after* the generic catch for toggle_dismissable_panel
        ## because it was being superceded.
        self.Bind(wx.EVT_BUTTON, self.menuSettings, id=wx.ID_APPLY)


        ## THE MAIN GUI
        ## ------------------------------------------------------------------

        ## A temporary switch to test out various ideas
        self.whatgui = 1

        MINSCREENWIDTH = 800 #old skool
        minw = 360
        fvminw = MINSCREENWIDTH - minw
        ms = wx.Size(minw,1)

        if self.whatgui == 3:
            fvminw = MINSCREENWIDTH
            #splitter window of 2 across
            #left: a panel with sizer of two high of: source, then target guis
            #right: fontview
            ##This one freezes the app when you resize to the right... :(
            ## Hard to reproduce. I used gdb and got it to crash, then
            ## did a 'bt' and saw some complaints about get text extents
            ## might be a bug in my font drawing code..?
            ## self.spw = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
            ## This line seems less crashy, but not much less:
            ## self.spw = wx.SplitterWindow(self)

            self.spw = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
            self.spw.SetMinimumPaneSize(minw)

            p1 = wx.Panel(self.spw)
            self.panelFontSources = FontSourcesPanel(p1)
            self.panelTargetPogChooser = TargetPogChooser(p1)

            stsizer = wx.BoxSizer(wx.VERTICAL)
            stsizer.Add( self.panelFontSources, 1, wx.EXPAND|wx.ALL,border = 5 )
            stsizer.Add( self.panelTargetPogChooser, 1, wx.EXPAND|wx.ALL,border = 5 )

            p1.SetSizer(stsizer)

            self.fontViewPanel = FontViewPanel(self.spw)
            self.fontViewPanel.SetMinSize(wx.Size(fvminw,1))

            self.spw.SplitVertically( p1, self.fontViewPanel)#, self.initpos)
            # Thanks to the multiSplitterWindow code from the demo:
            self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, self.onSplitterPosChanging)
            self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.onSplitterPosChanged)

        elif self.whatgui == 1:

            ## PRIMARY GUI
            ## ===========
            ## No splitters at all.
            ## Box across: two
            ## Left box: Box vertical: two (source/target)
            ## Right box: Fontview
            ## :- kind of shape.

            self.panelFontSources = FontSourcesPanel(self)
            self.panelFontSources.SetMinSize(ms)

            self.panelTargetPogChooser = TargetPogChooser(self)
            self.panelTargetPogChooser.SetMinSize(ms)

            self.fontViewPanel = FontViewPanel(self)
            self.fontViewPanel.SetMinSize(wx.Size(fvminw,1))

            ## Oct/Nov 2017
            ## Moved some dialogues into the app as panels:
            self.help_panel = HtmlPanel(self)
            self.help_panel.Hide()

            self.about_panel = AboutPanel(self)
            self.about_panel.Hide()

            self.settings_panel = SettingsPanel(self)
            self.settings_panel.Hide()
            ## This panel needs to signal when it hides/shows:
            self.settings_panel.Bind(wx.EVT_SHOW, self.settings_panel.show_or_hide)
            
            stsizer = wx.BoxSizer(wx.VERTICAL)
            stsizer.Add( self.panelFontSources, 1, wx.EXPAND|wx.ALL,border = 5 )
            stsizer.Add( self.panelTargetPogChooser, 1, wx.EXPAND|wx.ALL,border = 5 )

            lrsizer = wx.BoxSizer(wx.HORIZONTAL)
            lrsizer.Add( stsizer, 0, wx.EXPAND)
            lrsizer.Add( self.fontViewPanel, 1, wx.EXPAND|wx.ALL, border = 5 )
            ##
            lrsizer.Add( self.help_panel, 1, wx.EXPAND )
            lrsizer.Add( self.about_panel, 1, wx.EXPAND )
            lrsizer.Add( self.settings_panel, 1, wx.EXPAND )

            self.SetSizer(lrsizer)

            ## A system to control the hide/show of these panels.
            self.panel_state = flag_normal
            self.panel_dict={
                    flag_normal  : self.fontViewPanel, 
                    flag_help    : self.help_panel,
                    flag_about   : self.about_panel,
                    flag_settings: self.settings_panel,
            }

        ## Idle/resize idea from here:
        ##https://stackoverflow.com/questions/13479831/what-is-the-simplest-way-of-monitoring-when-a-wxpython-frame-has-been-resized
        self.resized = False
        self.Bind(wx.EVT_IDLE, self.onIdle)
        self.Bind(wx.EVT_SIZE, self.onFrameSize)


        ## GUI ENDS
        ## =============

        self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

        ## Now to subscribe to have my various def called from other places:
        ps.sub(show_error, self.ErrorBox)
        ps.sub(show_error_and_abort, self.ErrorAbort)
        ps.sub(show_message, self.MessageBox)
        ps.sub(print_to_status_bar, self.StatusbarPrint)

        ## Dec 2007 - Used on middle click in gui_Fitmap.py
        ps.sub( open_settings_panel, self.open_settings_panel )
        ps.sub( toggle_selection_menu_item, self.toggleSelectionMenuItem )

        ps.sub( toggle_purge_menu_item, self.TogglePurgeMenuItem )
        ps.sub( ensure_fontview_shown, self.ensure_fontview_shown )
        

        ## call the big one - the big chief, the big cheese:
        ## This eventually draws all the Fitmaps - giving the middle a width.
        ps.pub( update_font_view ) #See gui_FontView.py under class FontViewPanel


        self.SetMinSize(wx.Size(MINSCREENWIDTH,600)) #Old Skool: Assuming monitor size...
        self.Layout()

        ## This is to draw the correct icons depending on cli params.
        self.panelTargetPogChooser.pogTargetlist.SortOutTheDamnImages(False)

    ## State stuff to manage the DismissablePanels
    def flag_state_on(self, flag):
        self.panel_state |= flag

    def flag_state_off(self, flag):
        self.panel_state &= ~flag

    def flag_state_exclusive_toggle(self, flag):
        fs = self.is_state_flagged(flag)
        self.panel_state = 0
        if fs: #swap it
            self.flag_state_off(flag)
        else:
            self.flag_state_on(flag)

    def is_state_flagged(self,flag):
        #print "state is: {:08b}".format( self.panel_state)
        return self.panel_state & flag == flag
    
    def hide_or_show_panels(self):
        if self.panel_state == 0:
            self.panel_state = flag_normal

        for flag, pan in self.panel_dict.iteritems():
            if self.is_state_flagged(flag):
                pan.Show()
                #pan.SetFocus() # useless
            else:
                pan.Hide()
                self.flag_state_off(flag)
        self.Layout()

    def ensure_fontview_shown(self):
        ## For use from outside. 
        ## See start of gui_FontView.MainFontViewUpdate()
        self.panel_state = flag_normal
        self.hide_or_show_panels()

    def toggle_dismissable_panel(self, evt):
        """
        Handles events from a few different sources: menus and buttons.
        Looks for an id in the flag_from_id dict. If found,
        we know it's to do with a DismissablePanel.
        """
        #print "toggleSelectionMenuItem runs."
        flag = flag_from_id.get(evt.GetId(),None)
        if flag:
            self.flag_state_exclusive_toggle(flag)
            self.hide_or_show_panels()




    ##Only used if whatgui != 1
    def onSplitterPosChanging(self,evt):
        """
        A Splitter is moving - PRESENT TENSE. Let's do the least work poss.
        """
        esp = evt.GetSashPosition()
        print esp
        if esp > 500:
            evt.Veto()
        return

    ##Only used if whatgui != 1
    def onSplitterPosChanged( self, evt ):
        """
        A Splitter has been moved - PAST TENSE.
        We only want to redraw the fonts when the splitter dragging is over.
        """
        ps.pub( update_font_view ) # starts a HUGE chain of calls.


    def onFrameSize(self,evt):
        self.resized = True
        evt.Skip()

    def onIdle(self, evt):
        #print "Idle runs"
        if self.resized:
            if not self.is_state_flagged(flag_normal):
                # Don't call the big update
                return
            #print "  Idle updates fontViewPanel"
            ps.pub( update_font_view )
            self.resized = False



    def OnAccelKey(self,evt):
        ps.pub( left_or_right_key_pressed, evt ) #fwd this business on-to a func in gui_FontView.py

    def toggleSelectionMenuItem(self, onoff):
        #HIG says to leave top menu alone and only toggle sub-items.
        self.MENUSELECTION.Enable(301,onoff[0])
        self.MENUSELECTION.Enable(302,onoff[0])

    def StatusbarPrint(self, args):
        self.sb.Report(args[0])

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
        self.endApp()

    def onHandleESC(self, e) :
        print strings.done
        self.endApp()

    def endApp(self) :
        """
        Save app's vital statistics and exit.
        See the end of start.py where it's actually saved.
        """
        ## Dec 2007 - I was using the wrong func and the
        ## main window kept getting smaller!
        fpsys.config.size = self.GetSizeTuple()

        ##June 2009 - fetch and record the value of the recurse folders checkbox.
        fpsys.config.recurseFolders = app.GetTopWindow().panelFontSources.nb.recurseFolders.GetValue()
        self.Destroy()

    def open_settings_panel(self):
        """Called from Fitmap on middle click."""
        self.flag_state_exclusive_toggle( flag_settings )
        self.hide_or_show_panels()

    def menuSettings(self, e):
        lastnuminpage = fpsys.config.numinpage
        lastpoints = fpsys.config.points
        lasttext = fpsys.config.text
        lastias = fpsys.config.ignore_adjustments

        ## Did anything change?
        num = int(self.settings_panel.inputPageLen.GetValue())
        points = int(self.settings_panel.inputPointSize.GetValue())
        txt = self.settings_panel.inputSampleString.GetValue()
        ignore_adjust = self.settings_panel.chkAdjust.GetValue() #Sept 2009

        stuffchanged = False
        if num != lastnuminpage:
            fpsys.config.numinpage = int(num)
            stuffchanged = True
        if txt != lasttext:
            if len(txt) > 0: fpsys.config.text =  txt
            stuffchanged = True
        if points != lastpoints:
            fpsys.config.points = int(points)
            stuffchanged = True
        if ignore_adjust != lastias:
            fpsys.config.ignore_adjustments = ignore_adjust #Sept 2009
            stuffchanged = True

            fpsys.config.CMC.SET_CURRENT_APPNAME( self.settings_panel.CHOSEN_CHARACTER_MAP) # Oct 2009

        ## Now to refresh things:
        if stuffchanged: 
            ps.pub( reset_top_left_adjustments ) ##DND : In ScrolledFontView
            ## Will hide the settings_panel too
            ps.pub( update_font_view )
        else:
            ## With no changes, we must hide the settings_panel
            self.ensure_fontview_shown()




    def menuCheckFonts( self, e ):
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

    def menuSelectionALL(self,e):
        if not fpsys.state.cantick: return # Can't tick if this is False.
        fpsys.state.numticks=0
        vo=fpsys.state.filteredViewObject # We want to select what is FILTERED
        for fi in vo:
            if not fi.inactive:
                fi.ticked=True
                fpsys.state.numticks += 1
        ## Now update the view
        ps.pub( update_font_view )

    def menuSelectionNONE(self,e):
        fpsys.state.numticks=0
        vo=fpsys.state.viewobject # We *REALLY* mean select NONE. So ignore filter.
        for fi in vo:
            if not fi.inactive:
                fi.ticked=False
        ## Now update the view
        ps.pub( update_font_view )

    def TogglePurgeMenuItem(self, vis):
        vis=vis[0]
        #print vis
        #print fpsys.state.viewobject.name
        self.MENUPURGE.Enable(103,vis)

        ## July 2016
        ## =========
        ## Make the label of the menu reflect the view Pog's name
        ## so it's clear which selection counts for purging.
        if vis:
            self.MENUPURGE.SetLabel(103, _("&Purge \"%s\"\tCtrl+P" % fpsys.state.viewobject.name ) )
        else:
            self.MENUPURGE.SetLabel(103, _("&Purge Pog\tCtrl+P")) #Reflect original string, as it's got translations already.


    def menuPurgePog(self,e):
        ##The menu item only becomes active for Pogs that are not installed,
        ##so we can purge without further tests:
        pogname = fpsys.state.viewobject.name
        dlg = wx.MessageDialog(self,_("Do you want to purge %s?\n\nPurging means all the fonts in the pog\nthat are not pointing to actual files\nwill be removed from this pog.") % pogname, _("Purge font?"), wx.YES_NO | wx.ICON_INFORMATION )
        if dlg.ShowModal() == wx.ID_YES:
            ## pog.purge() Raises
            ## 	  PogEmpty
            ## 	  PogInstalled
            try:
                fpsys.state.viewobject.purge()
            except(fontybugs.PogEmpty, fontybugs.PogInstalled),e:
                ps.pub(show_error, unicode( e ))
                ps.pub(print_to_status_bar, _("%s has not been purged.") % pogname)
                return

            ## Update GUI
            ps.pub(print_to_status_bar, _("%s has been purged.") % pogname)

            ps.pub(update_font_view)




# Code for debugging:
##http://wiki.wxpython.org/Widget%20Inspection%20Tool
## Use ctrl+alt+i to open it.
import wx.lib.mixins.inspection
## Start the main frame and then show it.
class App(wx.App  , wx.lib.mixins.inspection.InspectionMixin) :
    """
    The main wxPython app starts here
    """
    def OnInit(self):
        self.Init()  # initialize the inspection tool

        ## Initial dialogue to inform user about wx unicode version.
        if not "unicode" in wx.PlatformInfo:
            wx.MessageBox(_("I am sorry, but Unicode is not supported by this " \
            "installation of wxPython. Fonty Python relies on Unicode and will " \
            "simply not work without it.\n\nPlease fetch and install the " \
            "Unicode version of python-wxgtk."),
                caption=_("SORRY: UNICODE MUST BE SUPPORTED"),
                style=wx.OK | wx.ICON_EXCLAMATION )
            raise SystemExit

        ## Probe for delayed errors in PathControl
        ## and show them in message boxes.
        try:
            fpsys.iPC.probeAllErrors()

        ## App stopping errors:
        except (fontybugs.NoFontypythonDir, fontybugs.UpgradeFail) as e:
            wx.MessageBox( e.unicode_of_error(),
                caption=_("FATAL ERROR"),
                style=wx.OK | wx.ICON_ERROR )
            ## This one is unrecoverable:
            raise SystemExit

        ## Warning only
        except fontybugs.NoFontsDir as e:
            ## This looks horrible. I will remark it.
            ## The app deals with it in context.
            #    wx.MessageBox( e.unicode_of_error(),
            #        caption=_("WARNING"),
            #        style=wx.OK | wx.ICON_ERROR )
            pass

        # Start a splash screen - which then starts the main frame
        MySplash = FontySplash()
        MySplash.Show()

        return True

class FontySplash(wx.SplashScreen):
        """
        2016 July
        =========
            Trying a diff way to show the splash screen.
            It's a little better. It shows fast and
            remains there while the frame loads behind it.

            Borrowing from the wxPython demo's code.
        """
        def __init__(self, parent=None):
            splashStyle = wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT
            splashDuration = 1000 # milliseconds

            wx.SplashScreen.__init__(self, wxbmp( "splash" ), splashStyle, splashDuration, parent)
            self.Bind(wx.EVT_CLOSE, self.OnExit)

            # Nice! Kick the show off in x millis.
            self.fc = wx.FutureCall(500,self.showMain)

        def OnExit(self, evt):
            # The program will freeze without this line.
            evt.Skip()	# Make sure the default handler runs too...
            self.Hide()

            # if the timer is still running, force the main frame to start
            if self.fc.IsRunning():
                self.fc.Stop()
                self.showMain()

        def showMain(self):
            ## Oct 2017
            ## Setup my system fonts and colours
            setup_fonts_and_colours()

            frame = MainFrame(None, _("Fonty Python: bring out your fonts!"))
            app.SetTopWindow(frame)

            frame.Show(True)

            if self.fc.IsRunning():
                self.Raise()


#Start the app!
app = App(0)
app.MainLoop()
