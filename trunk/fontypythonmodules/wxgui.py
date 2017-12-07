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


## Nov 15, 2017
## --
## Coding while there's a Coup d'etat in Zimbabwe; our neighbour. 
## Feeling of doom in our SA politics. Ruinous criminals in ANC gov;
## my health declining and no income.
## Just keeping my head down and trying to get Fonty working and
## out the door. Good luck Zimbabwe. I hope you kick out the Prick!
## Zuma next. Somehow. Without blood.

"""
This is the main gui. A good place to start. Look at the bottom of
the file first.
"""

import locale
import strings
import fontybugs
import fpsys # Global objects
import fpversion
## Now, bring in all those big modules
import wx
import wx.html as html


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

from gui_FontSources import *
from gui_FontView import *
from gui_PogTargets import *

import fpwx

## Variables to do with the DismissablePanels
## and to map the close (X) button id to the
## state flags we use to show/hide the panels
flag_normal = 1
flag_help = 2
flag_about = 4
flag_settings = 8
flag_choosedir = 16
flag_hush_fonts = 32

## button ids
# I put them in a dict so I could more easily import them over in
# gui_dismissable_panels
button_ids = {
          'id_x_button' : wx.NewId(), # close a dism. panel (top right)
    'id_zip_pog_button' : wx.NewId(), # the button is in TargetPogChooser
 'id_do_the_actual_zip' : wx.NewId(), # button is in the ChooseZipDirPanel
       'id_hush_button' : wx.NewId(), # button is in the HushPanel
}

# Got a flag? get an id.
id_from_flag = {
        flag_help       : wx.NewId(),
        flag_about      : wx.NewId(),
        flag_settings   : wx.NewId(),
        flag_choosedir  : button_ids['id_zip_pog_button'],
        flag_hush_fonts : wx.NewId()
        }
# Got an id? get a flag.
flag_from_id = {v:k for k,v in id_from_flag.iteritems()} #invert it!



from gui_dismissable_panels import *


class StatusBar(wx.StatusBar):
    """
    The status bar
    """
    def __init__(self, parent):
        wx.StatusBar.__init__(self, parent, -1) # default style is good

        ##Sept2017
        ## Test if there's a need to warn about missing .fonts dir.

        no_fonts_dir = False
        e = fpsys.iPC.get_error_or_none("NoFontsDir")
        if e:
            no_fonts_dir = True
            shorterr = e.short_unicode_of_error()

        ## Field 1 is Welcome...
        ## Field 2 is normal conversation.
        ## Field 3 <if missing user fonts dir> is the warning message.
        ## Last field "gripper" (32px)
        self.SetFieldsCount( 4 if no_fonts_dir else 3 )

        self.SetStatusText( _("Welcome to Fonty Python, vers %s") % fpversion.version, 0)

        if no_fonts_dir:
            self.SetStatusText( shorterr, 2)
            print shorterr
            self.SetStatusWidths([300,-2,-2,32])
            #self.SetStatusStyles([wx.SB_SUNKEN]*3) #SB_SUNKEN is not available to me. 
        else:
            self.SetStatusWidths([300,-2,32])
            #self.SetStatusStyles([wx.SB_SUNKEN]*2)

    def Report(self, msg):
        self.SetStatusText(msg, 1)
        print msg




class MainFrame(wx.Frame):

    """
    The main frame for the app. Start at the bottom of this file.
    """
    def __init__(self, parent, title) :
        ## Draw the frame
        title = u"{} - {}".format( title, locale.getpreferredencoding() )
        wx.Frame.__init__( self, parent, -1,
                title,
                fpsys.config.pos,
                fpsys.config.size,
                name = "fontypython")

        #print "Main frame:", self.GetSizeTuple()[0]

        ## Try to show an icon
        ## Oct 2017: Seems Unity (at least) doesn't even bother...
        try:
            i = wx.EmptyIcon()
            i.CopyFromBitmap( fpwx.wxbmp('fplogo'))
            self.SetIcon(i)
        except:
            pass


        ## STATUS BAR
        ## ---------------------------------------
        self.sb = StatusBar(self)
        self.SetStatusBar(self.sb)

        ## MENUS
        ## ---------------------------------------
        # tools selection help

        self.menuBar = wx.MenuBar()

        ## FILE MENU : Changed to "Tools" menu Sep 2009
        menu1 = wx.Menu()
        menu1.Append( id_from_flag[flag_settings],
                _("&Settings\tCtrl+S"), _("Change settings"))
        ## Jan 18 2008
        ## Nov 2017: retired: menu1.Append( 102, 
        ##        _("&Check fonts"), _("Find those fonts that crash Fonty.") )
        self.id_purge = wx.NewId()
        menu1.Append( self.id_purge, 
            _("&Purge Pog.See TogglePurgeMenuItem for actual string."),
            _("Remove all ghost fonts from the selected Pog.") )

        self.MENUPURGE = menu1

        ## Nov 2017: Hush fonts
        menu1.Append( id_from_flag[flag_hush_fonts],
            _("&Hush fonts\tCtrl+H"),
            _("Silence all the noisy system fonts and focus only on those you want,"))
        
        menu1.AppendSeparator()

        self.id_exit = wx.NewId()
        self.exit = menu1.Append(self.id_exit,
                _("&Exit"),
                _("Close the app"))

        ## Tools
        self.menuBar.Append(menu1, _("&Tools"))


        ## SELECT MENU: June 2009
        menu3 = wx.Menu()
        self.id_selall = wx.NewId()
        menu3.Append( self.id_selall,
            _("&Select ALL the source fonts"),
            _("Select ABSOLUTELY ALL the fonts in the chosen source."))
        self.id_selnone = wx.NewId()
        menu3.Append( self.id_selnone,
                _("&Clear ENTIRE selection"),
                _("Clear the selection completely.") )
        self.menuBar.Append(menu3, _("&Selection"))
        self.MENUSELECTION = menu3

        ## HELP MENU
        menu2 = wx.Menu()
        menu2.Append(id_from_flag[flag_help], _("H&elp\tF1"))
        menu2.Append(id_from_flag[flag_about], _("&About"))
        self.menuBar.Append(menu2, _("&Help"))

        self.SetMenuBar(self.menuBar)

        ## Setup the ESC key and the LEFT / RIGHT keys
        escape_key_id = wx.NewId() # Get a unique id for the ESC key
        accel = wx.AcceleratorTable([
            (wx.ACCEL_NORMAL, wx.WXK_ESCAPE, escape_key_id), # use ESC id here
            (wx.ACCEL_CTRL, wx.WXK_RIGHT, wx.ID_FORWARD),
            (wx.ACCEL_CTRL, wx.WXK_LEFT, wx.ID_BACKWARD)
            ])
        self.SetAcceleratorTable(accel)


        ## Do this generic bind for all MENU EVENTS now.
        ## Then specific ones afterwards; else this one supercedes them.
        ## This is for the menus that open DismissablePanels:
        ## Help, About, Settings
        self.Bind(wx.EVT_MENU, self.toggle_dismissable_panel)


        ## Bind the Left and Right key shortcuts.
        self.Bind(wx.EVT_MENU, self.OnAccelKey, id=wx.ID_FORWARD )
        self.Bind(wx.EVT_MENU, self.OnAccelKey, id=wx.ID_BACKWARD )

        ## The frame's close window button.
        self.Bind( wx.EVT_CLOSE, self.endApp )

        ## Bind events for the exit menu
        self.Bind(wx.EVT_MENU, self.endApp, self.exit)

        ## Bind the ESCAPE key
        self.Bind(wx.EVT_MENU, self.onHandleESC, id = escape_key_id)# And ESC id here!
        
        #NOV 2017: Retiring this menu
        #I think PILLOW is more stable and I don't want to support the
        #extra code for the gui of this. The command line already does
        #a good job (-c) and my crash dialogue tells the user what to do.
        ##self.Bind(wx.EVT_MENU, self.menuCheckFonts, id = 102 )

        self.Bind(wx.EVT_MENU, self.menuPurgePog, id = self.id_purge )

        # June 2009
        self.Bind(wx.EVT_MENU, self.menuSelectionALL, id=self.id_selall)
        self.Bind(wx.EVT_MENU, self.menuSelectionNONE, id=self.id_selnone)

        ## Catch buttons in various panels. The panels have not been
        ## declared yet. See below.
        ## NB: THESE BINDS HAPPEN SECOND, *AFTER* toggle_dismissable_panel 
        ##     has Skipped.
        ##     The first Bind EVT_BUTTON is last in the code, see just below.
        ## 1. .toggle_dismissable_panel --> Does a Skip() to
        ## 2. Here:
        ## Catch the Apply button in the settings panel.
        self.Bind(wx.EVT_BUTTON, self.apply_settings, id=wx.ID_APPLY)
        ## Catch the Zip button in the choose_zipdir_panel 
        self.Bind(wx.EVT_BUTTON, self.do_pog_zip, id=button_ids['id_do_the_actual_zip'])
        ## Catch the Huch button in hush_panel
        self.Bind(wx.EVT_BUTTON, self.do_hush_unhush, id=button_ids['id_hush_button'])

        ## Vague Bind. Not specific to id. 
        ## HAPPENS FIRST even though it's last in the code.
        ## 1. The close (X) button of the DismissablePanels
        ## 2. The ZIP button (Skipped to here from TargetPogChooser)
        self.Bind(wx.EVT_BUTTON, self.toggle_dismissable_panel )

        ## THE MAIN GUI
        ## ------------------------------------------------------------------

        MINSCREENWIDTH = 800 #old skool
        minw = 360 # pretty much the width of the left hand side.
        fvminw = MINSCREENWIDTH - minw # The width of the rhs.
        ms = wx.Size( minw, 1 )

        ## PRIMARY GUI
        ## ===========
        ## No splitters at all.
        ## Box across: two
        ## Left box: Box vertical: two (source/target)
        ## Right box: Fontview
        ## :- kind of shape.

        self.panelFontSources = FontSourcesPanel(self)
        self.panelFontSources.SetMinSize(ms)

        self.panelTargetPogChooser = TargetPogChooser(self, button_ids['id_zip_pog_button'])
        self.panelTargetPogChooser.SetMinSize(ms)

        self.fontViewPanel = FontViewPanel(self)
        self.fontViewPanel.SetMinSize(wx.Size(fvminw,1))

        ## Oct/Nov 2017
        ## Moved some dialogues into the app as panels:

        ## Help
        self.help_panel = HelpPanel(self)
        #self.help_panel.Hide()

        ## About
        self.about_panel = AboutPanel(self)
        #self.about_panel.Hide()
        
        ## I will use fontViewPanel as the standard to 
        ## measure widths in these DismissablePanels
        wfunc = self.fontViewPanel.GetSize
        
        ## The Settings
        self.settings_panel = SettingsPanel( self, wfunc )
        #self.settings_panel.Hide()

        ## Zip Pog panel
        self.choose_zipdir_panel = ChooseZipDirPanel( self, wfunc )
        #self.choose_zipdir_panel.Hide()

        ## Hush panel
        self.hush_panel = HushPanel( self, wfunc )


        stsizer = wx.BoxSizer(wx.VERTICAL)
        stsizer.Add( self.panelFontSources, 1, wx.EXPAND|wx.ALL,border = 5 )
        stsizer.Add( self.panelTargetPogChooser, 1, wx.EXPAND|wx.ALL,border = 5 )

        lrsizer = wx.BoxSizer(wx.HORIZONTAL)
        lrsizer.Add( stsizer, 0, wx.EXPAND)
        lrsizer.Add( self.fontViewPanel, 1, wx.EXPAND|wx.ALL, border = 5 )
        lrsizer.Add( self.help_panel, 1, wx.EXPAND )
        lrsizer.Add( self.about_panel, 1, wx.EXPAND )
        lrsizer.Add( self.settings_panel, 1, wx.EXPAND )
        lrsizer.Add( self.choose_zipdir_panel, 1, wx.EXPAND )
        lrsizer.Add( self.hush_panel, 1, wx.EXPAND )

        self.SetSizer(lrsizer)

        ## A system to control the hide/show of these panels.
        self.panel_state = flag_normal
        self.panel_dict={
                flag_normal  : self.fontViewPanel, 
                flag_help    : self.help_panel,
                flag_about   : self.about_panel,
               flag_settings : self.settings_panel,
              flag_choosedir : self.choose_zipdir_panel,
             flag_hush_fonts : self.hush_panel,
        }
        ##
        ## Very out of date. Left for future maybes.
        ##
        ##splitter window of 2 across
        ##left: a panel with sizer of two high of: source, then target guis
        ##right: fontview
        ##This one freezes the app when you resize to the right... :(
        ## Hard to reproduce. I used gdb and got it to crash, then
        ## did a 'bt' and saw some complaints about get text extents
        ## might be a bug in my font drawing code..?
        ## self.spw = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        ## This line seems less crashy, but not much less:
        ## self.spw = wx.SplitterWindow(self)
        #fvminw = MINSCREENWIDTH
        #self.spw = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        #self.spw.SetMinimumPaneSize(minw)
        #p1 = wx.Panel(self.spw)
        #self.panelFontSources = FontSourcesPanel(p1)
        #self.panelTargetPogChooser = TargetPogChooser(p1)
        #stsizer = wx.BoxSizer(wx.VERTICAL)
        #stsizer.Add( self.panelFontSources, 1, wx.EXPAND|wx.ALL,border = 5 )
        #stsizer.Add( self.panelTargetPogChooser, 1, wx.EXPAND|wx.ALL,border = 5 )
        #p1.SetSizer(stsizer)
        #self.fontViewPanel = FontViewPanel(self.spw)
        #self.fontViewPanel.SetMinSize(wx.Size(fvminw,1))
        #self.spw.SplitVertically( p1, self.fontViewPanel)#, self.initpos)
        ## Thanks to the multiSplitterWindow code from the demo:
        #self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, self.onSplitterPosChanging)
        #self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.onSplitterPosChanged)
        ##Only used if whatgui != 1
        #def onSplitterPosChanging(self,evt):
        #    """
        #    A Splitter is moving - PRESENT TENSE. Let's do the least work poss.
        #    """
        #    esp = evt.GetSashPosition()
        #    print esp
        #    if esp > 500:
        #        evt.Veto()
        #    return
        ##Only used if whatgui != 1
        #def onSplitterPosChanged( self, evt ):
        #    """
        #    A Splitter has been moved - PAST TENSE.
        #    We only want to redraw the fonts when the splitter dragging is over.
        #    """
        #    ps.pub( update_font_view ) # starts a HUGE chain of calls.

        ## Frame resizing sanity code
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

        # Don't do Fit. 
        # It makes the FRAME size DOWN to the minimum children's size!
        ## self.Fit() 

        self.Layout()

        ## This is to draw the correct icons depending on cli params.
        self.panelTargetPogChooser.pogTargetlist.toggle_list_icons_according_to_selection(False)

    ## State stuff to manage the DismissablePanels
    def flag_state_on(self, flag):
        self.panel_state |= flag

    def flag_state_off(self, flag):
        self.panel_state &= ~flag

    def flag_state_exclusive_toggle(self, flag):
        """
        Toggle this flag's bit.
        All other flags will be turned off.
        """
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
                pan.SetFocus()
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
        #print evt.GetId()
        flag = flag_from_id.get(evt.GetId(),None)
        #print "got flag:", flag
        if flag:
            self.flag_state_exclusive_toggle(flag)
            self.hide_or_show_panels()

        ## NB: I have more bindings after this handler is done:
        evt.Skip()

    def onFrameSize(self,evt):
        self.resized = True
        evt.Skip()

    def onIdle(self, evt):
        if self.resized:
            ## If it's showing the normal (font) view, then:
            if self.is_state_flagged(flag_normal):
                # I place this fact into fpsys.state so
                # that I can read it again down in the
                # fitmap assemble_bitmap code.
                fpsys.state.main_frame_resized = True
                # Go re-draw shit.
                ps.pub( update_font_view )
            # Flag it off
            self.resized = False
            # Flag it off in fpsys.state too
            fpsys.state.main_frame_resized = False

    def OnAccelKey(self,evt):
        ps.pub( left_or_right_key_pressed, evt ) #fwd this business on-to a func in gui_FontView.py

    def toggleSelectionMenuItem(self, onoff):
        #HIG says to leave top menu alone and only toggle sub-items.
        self.MENUSELECTION.Enable(self.id_selall,onoff[0])
        self.MENUSELECTION.Enable(self.id_selnone,onoff[0])

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

    def onHandleESC( self, e ):
        """
        ESC key wired to this.
        
        If we have a DismissablePanel open, let's close
         it instead of the app.
        """
        if not self.is_state_flagged(flag_normal):
            self.ensure_fontview_shown()
        else:
            self.endApp(None)

    def endApp( self, e ) :
        """
        Frame's X is wired to this.
        Save app's vital statistics and exit.
        See the end of start.py where it's actually saved.
        """
        ## Dec 2007 - I was using the wrong func and the
        ## main window kept getting smaller!
        fpsys.config.size = self.GetSizeTuple()
        fpsys.config.pos = self.GetScreenPosition()
        
        ## Nov 2017: We got here, so there are no segfaults, thus
        ## we have no need for this file.
        fpsys.rm_lastFontBeforeSegfault_file()

        print strings.done
        self.Destroy()

    def open_settings_panel(self):
        """Called from Fitmap on middle click."""
        self.flag_state_exclusive_toggle( flag_settings )
        self.hide_or_show_panels()

    def apply_settings(self, e):
        """
        The second stage of the Apply button on the settings panel.
        (Stage one is within the SettingsPanel class.)
        We get here after all the values have been checked and 
        recorded into fpsys.config
        Here we only need to decide on what to redraw.
        """
        #print "apply settings?"
        if self.settings_panel.settings_force_redraw():

            ## If the ignore adjustments checkbos changed:
            if self.settings_panel.has_changed("ignore_adjustments"):
                ps.pub( reset_top_left_adjustments )

            ## This recurse checkbox is more complex.
            ## I have to hand over control to that class:
            if self.settings_panel.has_changed("recurseFolders"):
                ## This does a redraw, and there it does a 
                ## force-close of the settings panel.

                ## We have to imitate a click on the dir control
                ## to kick stuff into gear.
                ps.pub( fake_click_the_source_dir_control )
                # bail! So we don't do another re-draw.
                return

            ## Redraw the fitmaps (Will also hide the settings_panel)
            ps.pub( update_font_view )
        else:
            ## With no changes, we must hide the settings_panel
            self.ensure_fontview_shown()
        return




    def do_hush_unhush(self, e):
        """
        Use the code in fpsys to hush or unhush.
        """
        ## Just paranoid - want to make sure it's the correct button id
        ## Only want to fire on press of button in the hush_panel:
        if e.GetId() == button_ids['id_hush_button']:
            buglist = []
            if not os.path.exists(fpsys.HUSH_PAF):
                ## Hush
                hush_pog = fpsys.config.hush_pog_name
                printer = self.hush_panel.printout 
                buglist = fpsys.hush_with_pog( hush_pog, printer )
            else:
                ## Un hush
                printer = self.hush_panel.printout 
                buglist = fpsys.un_hush( printer )

            if buglist: 
                ## All errors end with this text:
                printer( strings.cant_hush, key="title")
                for bug in buglist: printer( bug, key="ERROR" )
                
            ## Go refresh the panel to update state
            self.hush_panel.after_do_hushing()


    def do_pog_zip(self, e):
        """
        The button in the choose_zipdir_panel was clicked.
        """
        czd = self.choose_zipdir_panel
        todir = czd.get_path()
        emsg = ""
        printer = czd.printout
        if todir:
            wx.BeginBusyCursor()
            for p in self.panelTargetPogChooser.list_of_target_pogs_selected:
                ipog = fontcontrol.Pog(p)
                (bugs, fail, emsgs) = ipog.zip( todir )
                    
                if fail: 
                    printer(
                       _("I could not create the zip for {}").format(ipog) )
                    printer( emsgs[0])
                    printer( "" )
                else:
                    printer( 
                       _("Zipped as \"{}.fonts.zip\" in the \"{}\" directory.").format( p, todir) )
                    printer( "" )
                    if bugs:
                        printer( _("Some bugs happened:") )
                        for m in emsgs: printer( m )
                        printer( "" )
            wx.EndBusyCursor()

            if bugs:
                printer(_("Some fonts were skipped, try purging the Pog(s) involved."))
                ps.pub(print_to_status_bar,_("Something went wrong."))
            else:
                printer(_("Zip file(s) have been created."))
                ps.pub(print_to_status_bar,_("Zip file(s) have been created.") )



    ##Retired NOV 2017
    #def menuCheckFonts( self, e ):
    #    """
    #    Added Jan 18 2008
    #    User can visit suspicious directories with this tool
    #    to gather a list of fonts that kill the app. They will be
    #    marked as such and hereafter be safe to use.
    #    """
    #    ## Set startdir to the one our own dircontrol is in
    #    if fpsys.state.viewpattern == "F":
    #        startdir = fpsys.state.viewobject.path
    #    else:
    #        ##Let's get it from the config object
    #        startdir = fpsys.config.lastdir
    #    dlg = dialogues.DialogCheckFonts( self, startdir )
    #    val = dlg.ShowModal()
    #    dlg.Destroy()

    def menuSelectionALL(self,e):
        """
        Select all the fonts that are FILTERED.
        Note: This does not do a test for ghost fonts. TODO
        """
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
        """
        Deselcts all the fonts.
        """
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
        self.MENUPURGE.Enable(self.id_purge, vis)

        ## July 2016
        ## =========
        ## Make the label of the menu reflect the view Pog's name
        ## so it's clear which selection counts for purging.
        if vis:
            self.MENUPURGE.SetLabel(self.id_purge, _("&Purge \"%s\"\tCtrl+P" % fpsys.state.viewobject.name ) )
        else:
            self.MENUPURGE.SetLabel(self.id_purge, _("&Purge Pog\tCtrl+P")) #Reflect original string, as it's got translations already.


    def menuPurgePog(self,e):
        ##The menu item only becomes active for Pogs that are not installed,
        ##so we can purge without further tests:
        pogname = fpsys.state.viewobject.name
        dlg = wx.MessageDialog(self,_("Do you want to purge %s?\n\nPurging means all the fonts in the pog\nthat are not pointing to actual files\nwill be removed from this pog.") % pogname, _("Purge font?"), wx.YES_NO | wx.ICON_INFORMATION )
        if dlg.ShowModal() == wx.ID_YES:
            ## pog.purge() Raises
            ##   PogEmpty
            ##   PogInstalled
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
#import wx.lib.mixins.inspection
## Start the main frame and then show it.
class App( wx.App ):# , wx.lib.mixins.inspection.InspectionMixin) :
    """
    The main wxPython app starts here
    """
    def OnInit(self):
        #self.Init()  # initialize the inspection tool

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
        except (fontybugs.NoFontypythonDir,
                fontybugs.UpgradeFail ) as e:
            wx.MessageBox( e.unicode_of_error(),
                caption=_("FATAL ERROR"),
                style=wx.OK | wx.ICON_ERROR )
            ## This one is unrecoverable:
            raise SystemExit
        except fontybugs.NoFontconfigDir as e:
            fpsys.state.fontconfig_confd_exists = False
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

        return True

class FontySplash(wx.Frame):
    """
    Show the splash screen; it's fast and
    remains there while the frame loads behind it.

    Borrowing from the wxPython-demo's code.
    
    (Code hacked from AdvancedSplash by
    Andrea Gavana.)
    """
    def __init__( self ):
        
        timeout = 2000
        # A smaller number then the first timeout
        mainframetimeout = 500

        wx.Frame.__init__(self, None, -1, "",
                wx.DefaultPosition,
                wx.DefaultSize,
                wx.FRAME_NO_TASKBAR | wx.FRAME_SHAPED | wx.STAY_ON_TOP)

        # Load the FP logo
        img = wx.Image( os.path.join(fpsys.mythingsdir, 'splash.png') )
        img.ConvertAlphaToMask()
        self.bmp = wx.BitmapFromImage(img)

        # Calculate the shape
        self.reg = wx.RegionFromBitmap(self.bmp)

        # Works on wx.Platform == "__WXGTK__"
        self.Bind(wx.EVT_WINDOW_CREATE, self.SetSplashShape)

        w = self.bmp.GetWidth() + 1
        h = self.bmp.GetHeight() + 1

        # Set frame to the bitmap size
        self.SetClientSize((w, h))

        self.CenterOnScreen()

        # Starts timer
        self._splashtimer = wx.PyTimer(self.OnNotify)
        self._splashtimer.Start(timeout)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        # Nice! Kick the MainFrame off in x milliseconds
        self.fc = wx.FutureCall( mainframetimeout, self.showMain )
        
        self.Show()

    def SetSplashShape(self, event=None):
        self.SetShape(self.reg)
        if event is not None:
            event.Skip()

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        # Draw over frame
        dc.DrawBitmap(self.bmp, 0, 0, True)

    def OnNotify(self):
        self.Close()

    def OnCloseWindow(self, event):
        if hasattr(self, "_splashtimer"):
            self._splashtimer.Stop()
            del self._splashtimer
            self.Destroy()
        
        event.Skip() # Make sure the default handler runs too...

    def showMain(self):
        ## Oct 2017
        ## Setup my system fonts and colours
        fpwx.setup_fonts_and_colours()

        frame = MainFrame(None, _("Fonty Python: bring out your fonts!"))
        app.SetTopWindow(frame)

        frame.Show(True)


#Start the app!
app = App(0)
app.MainLoop()
