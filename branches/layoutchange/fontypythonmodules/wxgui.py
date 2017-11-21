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
from gui_DirChooser import ATree
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

## ids
## These are needed here, and to pass it into TargetPogChooser
id_x_button=wx.NewId()
id_zip_pog_button = wx.NewId() 
id_do_the_actual_zip = wx.NewId() # button is in the DismissablePanel
id_hush_button = wx.NewId()

# got a flag? get an id.
id_from_flag = {
        flag_help       : wx.NewId(),
        flag_about      : wx.NewId(),
        flag_settings   : wx.NewId(),
        flag_choosedir  : id_zip_pog_button,
        flag_hush_fonts : wx.NewId()
        }
# got an id? get a flag.
flag_from_id = {v:k for k,v in id_from_flag.iteritems()} #invert it!


## ---
## The two basic classes for the DismissablePanels

class DismissablePanel(wx.Panel):
    """
    Only for subclassing.
    Provides a bar with an icon, title and an X close button.
    Under that is .. whatever: usually a sizer.
    """
    def __init__(self, parent, flag, someicon=None, somelabel="...", extra_padding=0):
        id = id_from_flag[flag]
        self.id = id
        wx.Panel.__init__(self, parent, id, style=wx.NO_FULL_REPAINT_ON_RESIZE)# | wx.SIMPLE_BORDER)
        self.parent = parent
        self.flag = flag

        ## Go fetch the .. whatever 
        whatever = self.__post_init__()
        
        ## Pad the whole thing some
        whatever_sizer = wx.BoxSizer( wx.VERTICAL )
        whatever_sizer.Add( whatever, 1,
                wx.EXPAND | wx.ALL,  border = 8 + extra_padding )

        l = fpwx.h1( self, somelabel )

        x_button = wx.Button(self, -1, label="X", 
                style = wx.NO_BORDER | wx.BU_EXACTFIT)
        self.Bind(wx.EVT_BUTTON, self.__x_pressed, x_button)

        x_button.SetToolTipString( _("Dismiss") )

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        if someicon:
            hbox.Add( fpwx.icon( self, someicon ), 0, wx.EXPAND | wx.RIGHT, border = 12 )
        else:
            hbox.Add( (1,1), 0, wx.EXPAND )
        # push the label down to better align with the X
        hbox.Add( l, 1, wx.EXPAND | wx.TOP, border = 8 ) 
        hbox.Add( x_button, 0, wx.ALIGN_RIGHT  | wx.BOTTOM, 
                border = 4 )
        hbox.Add( (8,8),0)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add( hbox, 0, wx.EXPAND | wx.TOP ,
                border = 16 ) #Wanted more space above.
        self.vbox.Add( whatever_sizer, 1, wx.EXPAND)
        self.SetSizer( self.vbox )
        self.Layout()
        self.SetFocus()

        self._firstshow = True
        self.Bind(wx.EVT_SHOW, self.__catch_show_or_hide)

    ## Private
    def __post_init__(self):
        pass

    def __x_pressed(self,evt):
        ## I don't want the button's id skipping-on, but the panel's
        evt.SetId(self.id)
        evt.Skip()

    def __catch_show_or_hide(self,evt):
        if self._firstshow: 
            self._firstshow = False
            return
        self._show_or_hide( self.IsShown() )

    def _show_or_hide(self, showing):
        pass




class DismissableHTMLPanel(DismissablePanel):
    """
    Collects common stuff that both HTML-based panels use.
    """
    class AnHtmlWindow(html.HtmlWindow):
        def __init__(self, parent):
            html.HtmlWindow.__init__(self, parent)
            if "gtk2" in wx.PlatformInfo or "gtk3" in wx.PlatformInfo:
                self.SetStandardFonts() 

    def __init__(self, parent, flag,
            somelabel = "...",
            someicon = None):
        DismissablePanel.__init__(self, parent, flag,
                somelabel = somelabel,
                someicon = someicon)

    def __post_init__(self):
        ## call one: get the HTML paf
        self.paf = self.post_init_set_paf()
        
        self.html = DismissableHTMLPanel.AnHtmlWindow(self)
        try:
            f = open( self.paf, "r" )
            h = f.read()
            f.close()       
        except Exception as e:
            h = u"<h1>Error reading {} file</h1><p>{}</p>".format(self.paf, e)
        
        ##provide a separator thing
        sep = "~/~"
        sep = u"<center><font size=5 color=\"{medium}\">" \
                   "<b>{sep}</b></font></center>".format(
                      sep = sep,
                      medium = fpwx.HTMLCOLS["heading1"] )
        sd = {"SEP":sep}

        ## call two: get the replace strings in a dict
        d = self.post_init_setup_replace_dict()

        # merge all the dicts
        sd.update(**d)
        sd.update(**fpwx.HTMLCOLS)
        
        ## Make sure the HTML is unicode
        h = fpsys.LSP.to_unicode(h)

        ## Format the HTML
        h = h.format(**sd)

        self.html.SetPage( h )        
        return self.html

    ## Public
    def post_init_set_paf(self):
        """Override and return a paf to an html file."""
        pass

    def post_init_setup_replace_dict(self):
        """Override and return a dict of keys to replace in the html."""
        pass

## Ends basic classes
## --



class HelpPanel(DismissableHTMLPanel):
    """Help moved to HTML in Oct/Nov 2017"""
    def __init__(self, parent):
        DismissableHTMLPanel.__init__(self, parent, flag_help, 
                somelabel=_("Help! Help! I'm being repressed!"),
                someicon="fplogo") 

    def post_init_set_paf(self):
        ## langcode = locale.getlocale()[0] # I must not use getlocale...
        ## This is suggested by Martin:
        # use *one* of the categories (not LC_ALL)
        loc = locale.setlocale(locale.LC_CTYPE)
        ## returns something like 'en_ZA.UTF-8'
        if loc is None or len(loc) < 2:
            langcode = 'en'
        else:
            langcode = loc[:2].lower()# May cause bugs
        ## Find localized help, or default to English.
        packpath = fpsys.fontyroot
        helppaf = os.path.join(packpath, "help", langcode, "help.html")
        if not os.path.exists( helppaf ):
            helppaf = os.path.join(packpath, "help", "en", "help.html")
        return helppaf

    def post_init_setup_replace_dict(self):
        ## Drop some last-minute info into the html string
        s_fpdir = fpsys.LSP.to_unicode(fpsys.iPC.appPath())

        ## Let's use our fancy error stuff to swap-in a message about
        ## the user fonts directory, should it be missing!
        try:
            fpsys.iPC.probeNoFontsDirError()
            s_fontsdir = fpsys.LSP.to_unicode(fpsys.iPC.userFontPath())
        except Exception as e:
            s_fontsdir = u"<h1>Missing User Fonts</h1><b>{}</b>".format( unicode(e).replace("\n","<br>") )

        d={"STATS_1":s_fpdir, "STATS_2":s_fontsdir} 
        return d


class AboutPanel(DismissableHTMLPanel):
    """About moved to HTML in Nov 2017"""
    def __init__(self, parent):
        DismissableHTMLPanel.__init__(self, parent, flag_about, 
                somelabel=_("About Fonty"),
                someicon="fplogo") 

    def post_init_set_paf(self):
        packpath = fpsys.fontyroot
        return os.path.join(packpath, "about", "about.html")

    def post_init_setup_replace_dict(self):
        return {
             "warranty": strings.warranty.replace("\n","<br>"),
            "copyright": strings.copyright,
              "contact": strings.contact,
              "version": strings.version,
              "ticket" : strings.ticket_url,
              "GPL"    : strings.GPL.replace("\n","<br>")}


class HushPanel(DismissablePanel):
    """
    Shows the form for hushing and unhushing fonts.
    """
    def __init__(self, parent):
         self.sd = {
                 "hush_on" :{"h":_("Hushing is on."), "b":_("Un-hush fonts")},
                 "hush_off":{"h":_("Hushing is off."),"b":_("Hush fonts")}
                  }
         DismissablePanel.__init__(self,parent, flag_hush_fonts,
                somelabel = _("Hush fonts"),
                someicon = "fplogo" ) 


    def __post_init__(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        ## Big header announcing Hushed/Not hushed
        ## Real tortured code to center the fuckin' label text. Jeezuz.
        hush_heading_panel = wx.Panel(self,size=(-1,150), style=wx.SUNKEN_BORDER)
        
        f = wx.BoxSizer(wx.HORIZONTAL)
        bsp = wx.BoxSizer(wx.VERTICAL)
        self.hush_state_label = fpwx.h0( hush_heading_panel, u"xxx")
        bsp.Add(self.hush_state_label, 1, wx.ALIGN_CENTER_HORIZONTAL )# | wx.ALL)#, border = 60)
        f.Add(bsp, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border = 40)
        hush_heading_panel.SetSizer(f)#bsp)

        sizer.Add( hush_heading_panel, 0, wx.EXPAND | wx.BOTTOM, border = 10)

        ## The label to the intro text
        self.chosen_pog_label = fpwx.h1( self, _("The Hush Pog:") )
        sizer.Add( self.chosen_pog_label, 0 )
        
        ## The intro text
        p1 = fpwx.para( self, _( u"Hushing installs a Pog that you must manage. " \
                                  "Make sure it contains a few system fonts. " \
                                  "Look in /usr/share/fonts for ideas." \
                                  "\nPlease read the help for details."))
        sizer.Add( p1, 0, wx.TOP, border = 5 )

        h = wx.BoxSizer(wx.HORIZONTAL)

        ## label to the choice box
        self.chosen_pog_label = fpwx.label( self, _("Current Hush Pog: ") )
        h.Add( self.chosen_pog_label, 0, wx.TOP, border = 30)

        ## The pog choice box
        self.pog_choice = wx.Choice(self, -1, choices = ["-"])
        self.pog_choice.SetToolTip( wx.ToolTip( _("Choose your system Pog") ) )
        self._update_pog_choice_control()
        self.pog_choice.Bind(wx.EVT_CHOICE, self._pog_chosen )
        
        h.Add( self.pog_choice, 0, wx.ALIGN_TOP | wx.TOP, border = 20)

        sizer.Add(h,0)

        ## Area to print into
        pl = fpwx.label( self, _("Progress report:") )
        sizer.Add( pl, 0, wx.TOP, border = 30)
        self.printer = wx.TextCtrl(self,
            -1, "", style = wx.TE_READONLY | wx.TE_MULTILINE)
        sizer.Add (self.printer, 1, wx.EXPAND )

        ## The hush/unhush button
        self.hb = wx.Button( self, label = self._update_heading("b"), id = id_hush_button )
        ## Make a button. Click also gets caught in MainFrame.
        self.Bind(wx.EVT_BUTTON, self._do_hushing, id = id_hush_button)
        sizer.Add(self.hb, 0, wx.TOP | wx.BOTTOM | wx.EXPAND, border=10)

        return sizer

    def _pog_chosen(self,evt):
        """The choice was changed."""
        s = evt.GetString()
        ## s is a byte string
        fpsys.config.hush_pog_name = s

    def _update_heading(self, key):
        if os.path.exists(fpsys.HUSH_PAF):
            return self.sd["hush_on"][key]
        else:
            return self.sd["hush_off"][key]
    
    def _update_pog_choice_control(self):
        """
        In case Pogs were added/deleted, we must refresh this list.
        Refill the choice list, sort and select the last string.
        """
        ## Empty the choice control.
        self.pog_choice.Clear()
        ## Now refill it
        pl = fpsys.iPC.getPogNames() # pl is all byte strings (encoded)
        pl.sort(cmp=locale.strcoll) # sort accroding to locale
        self.pog_choice.Append(_(u"None chosen"))
        self.pog_choice.AppendItems( pl ) # stick it in the control
        ## get the last Pog - make sure it's a byte, else..
        s = fpsys.LSP.ensure_bytes( fpsys.config.hush_pog_name )
        if s not in pl: # ...we get complaints here.
            n = 0
            # This means the choice is invalid, so:
            fpsys.config.hush_pog_name = ""
        else:
            # s is ok, let's seek its index in the control
            n = self.pog_choice.FindString(s)
        # now set it as selected
        self.pog_choice.SetSelection( n )

    def _show_or_hide(self, showing):
        """The entire panel hide/show"""
        if showing:
            print "showing"
            # I am being shown, so let's update shit:
            self._update_pog_choice_control()
            self.hush_state_label.SetLabel(self._update_heading("h"))
            self.hb.SetLabel(self._update_heading("b"))
        else:
            # I am being hidden ( esc, or x)
            self.printer.Clear()

    def _do_hushing(self, evt):
        """
        Forward the click on to MainFrame where it's also bound.
        """
        if self.pog_choice.GetCurrentSelection() == 0:
            return
        fpsys.config.hush_pog_name = self.pog_choice.GetStringSelection()
        #something 
        evt.Skip()

    def printout(self, msg, key=None):
        if key: 
            self.printer.write(key + "\n")
            self.printer.write("----" + "\n")
        self.printer.write(fpsys.LSP.ensure_unicode(msg)+ "\n")
        if not self.printer.IsShown(): 
            self.printer.Show()
            self.Layout()



class ChooseZipDirPanel(DismissablePanel):
    """
    Deals with all the crap the zip functionality needs.
    """
    def __init__(self, parent):
        DismissablePanel.__init__(self,parent, flag_choosedir, 
                somelabel=_("Locate a directory for the zip file(s)"),
                someicon = "icon_zip")
        self._chosen_path = None

    def __post_init__(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.treedir = ATree(self, os.getcwd())
        tree = self.treedir.GetTreeCtrl()
        #Clicks on the control will change the button's label
        tree.Bind(wx.EVT_TREE_SEL_CHANGED, self._on_dir_control_click)
        sizer.Add(self.treedir, 1, wx.EXPAND)
        
        self.lbl = fpwx.label( self, self._make_label() ) 
        sizer.Add( self.lbl, 0, wx.EXPAND | wx.TOP, border=10)

        self.printer = wx.TextCtrl(self,
            -1, "", style = wx.TE_READONLY | wx.TE_MULTILINE)
        sizer.Add (self.printer, 1, wx.EXPAND | wx.TOP, border=10 )
        self.printer.Hide()

        ## Make a button. Click also gets caught in MainFrame.
        btn = wx.Button(self, label = _("Create the zip file"),
                                id=id_do_the_actual_zip)
        self.Bind(wx.EVT_BUTTON, self._do_actual_zip, id=id_do_the_actual_zip)
        sizer.Add(btn, 0, wx.TOP | wx.BOTTOM | wx.EXPAND, border=10)

        return sizer

    def _show_or_hide(self, showing):#evt):
        """The entire panel hide/show"""
        if showing:#self.IsShown():
            # I am being shown
            if self.printer.IsEmpty():
                self.printer.Hide()
            else:
                self.printer.Show()
        else:
            # I am being hidden ( esc, or x)
            self.printer.Clear()
            self.printer.Hide()

    def printout(self, msg):
        self.printer.write(msg + "\n")
        if not self.printer.IsShown(): 
            self.printer.Show()
            self.Layout()

    def _make_label(self, p=None):
        if not p: p = os.getcwd()
        return _("The zip file(s) will be put into:\n{}").format(p)

    def _on_dir_control_click(self,e):
        cp = self.treedir.GetPath()
        #self.btn.SetLabel(self._make_label(cp))
        self.lbl.SetLabel(self._make_label(cp))

    def _do_actual_zip(self, evt):
        """
        Forwards the click on to MainFrame where it's also bound.
        """
        self._chosen_path = self.treedir.GetPath()
        evt.Skip()

    def get_path(self):
        return self._chosen_path




class SettingsPanel(DismissablePanel):
    def __init__(self, parent):
        """The settings form.
        I went a little mad. It started simple, the old code. A few gets,
        a few sets. Then I thought, "I can make this generic! Shit yeah!"
        And so I abstracted and factored and fuck. Now it's this thing.

        Sorry about that.
        """
        ## This dict is a way to handle the actual form in a
        ## loopy kind of way
        self.form = {}
        self._force_redraw = False
        self.settings_sizer = wx.FlexGridSizer( cols = 2, hgap = 5, vgap = 20 )
        
        DismissablePanel.__init__(self, parent, flag_settings,
                somelabel = _("Settings"),
                someicon = "icon_settings",
                extra_padding = 12)

    def __post_init__(self):
        """
        Happens only once. Draws all the controls, with values *from* config.
        After this, the panel only hides/shows. The controls all persist.
        """
        ## Sample text 
        k="text"
        c = wx.TextCtrl( self, -1, self.gv(k), size = (200, -1) )
        self.entry( k, _("Sample text:"), c,
                default = fpsys.Configure.atoz
                )

        ## Point size
        k = "points"
        c = self.spinner(k, (1, 500))
        self.entry( k, _("Point size:"), c )

        ## Page length
        k = "numinpage"
        c = self.spinner(k, (1, 5000), 
                tip=_("Beware large numbers!"))# It's your funeral!
        self.entry( k, _("Page length:"), c )

        ## Sept 2009 - Checkbox to ignore/use the font top left adjustment code
        k = "ignore_adjustments"
        c = wx.CheckBox(self, -1, _("Tick to disable") )
        c.SetValue( self.gv(k) )
        self.entry( k, _("Disable top-left correction:"), c,
                extra = _("Disabling this speeds-up\n" \
                          "font drawing but can\n" \
                          "cause bad positioning."))

        # The Character map choice
        # CMC is an instance of CharMapController
        self.CMC = fpsys.config.CMC
        k = "app_char_map"
        ## Do we have some char viewer apps?
        if self.CMC.apps_are_available:
            app = self.gv(k)
            c = wx.RadioBox( self, -1, _("Available"), 
                    wx.DefaultPosition, wx.DefaultSize,
                    self.CMC.quick_appname_list, 1, wx.RA_SPECIFY_COLS
                    )
            c.SetSelection(self.CMC.quick_appname_list.index(app))
            ## Prefer explicit "poke" (in dict) to this event:
            ##  self.Bind(wx.EVT_RADIOBOX, self.EvtRadioBox, c)
            c.SetToolTip(wx.ToolTip(_("Choose which app to use" \
                    " as a character map viewer.")))
            dud_control = False
        ## No apps, just print a string:
        else:
            app = None
            c = fpwx.para(self, 
                    _("None found.\nYou could install: {}".format(
                        self.CMC.list_of_suggested_apps)) )
            dud_control = True
        self.entry( k, _("Character map viewer:"), c, 
                dud = dud_control,
                redraw = False,
                peek = lambda c: c.GetStringSelection(),
                poke = self.poke_app_char_map
                )

        ## Max columns
        k = "max_num_columns"
        c = self.spinner(k, (1, 20))# It's your funeral!        
        self.entry( k, _("Max number of columns:"), c,
                extra = _("The font viewing area\n" \
                          "will divide into columns\n" \
                          "which you can control here.") )

        ## Nov 2017 - Moving the recurse check box into settings
        k = "recurseFolders"
        c = wx.CheckBox(self, -1, _("Tick to include all " \
                                    "sub-folders in source view.") )
        c.SetValue( self.gv(k) )
        self.entry( k,_("Include sub-folders."), c,
                extra = _("Caution: This will crash Fonty if\n" \
                          "your Source folder (directory)\n" \
                          "is deep."),
                redraw = True)

        ## Make an "apply" button. Click also gets caught in MainFrame.
        btn = wx.Button(self, wx.ID_APPLY)
        self.Bind(wx.EVT_BUTTON, self.apply_pressed, id=wx.ID_APPLY)
        #btn.SetDefault() # no joy...

        self.settings_sizer.Add((1,1),0) #a blank cell
        self.settings_sizer.Add(btn, 0, wx.ALL | wx.ALIGN_RIGHT, border=10)

        return self.settings_sizer

    def settings_force_redraw(self):
        """Do I have to redraw fitmaps?
        Used externally in MainFrame"""
        return self._force_redraw

    def has_changed(self, key):
        """Has a thing changed?
        Used externally in MainFrame"""
        return self.form[key]["changed"]

    def _show_or_hide(self, showing):#evt):
        """
        Fires when I hide or show.
        NOTE: Since __post_init__ only happens once, I need a way
        to alter the form as it comes and goes.
        """
        if showing:#self.IsShown():
            # Most of the controls will "remember" their last setting.
            # (This is all a show/hide game anyway.)
            # The only one that can change outside the settings is
            # point size - by the mouse wheel - hence I update it:
            self.form["points"]["control"].SetValue( self.gv("points") )

    def entry(self, key, title, ctrl, extra = None, dud = False,
              default = None,
              redraw = True,
              peek = None,
              poke = None ):
        """
        Makes the label. Puts it and the control into the sizer.
        
        Manages the form dict:

        Keys:
        ==
        default: for when a value is bad, use this instead.
        redraw : signals if a change to this value would require 
                 a fitmap redraw
        peek   : func to get value from the form control
        poke   : func to put the value into fpsys.config
        dud    : is a control that plays no real part

        """
        self.form[key] = {}
        self.form[key]["control"] = ctrl
        self.form[key]["dud"] = dud # some ctrls are just info.
        self.form[key].update({"default":default, 
                               "redraw" : redraw,
                               "peek"   : peek, 
                               "poke"   : poke})

        lbl = fpwx.boldlabel( self, title ) 
        if extra:
            ## We have some extra text to stuff in somewhere.
            sb = wx.BoxSizer(wx.VERTICAL)
            sb.Add( lbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_TOP )
            e = fpwx.parar(self, extra, size="points_smaller" )
            sb.Add( e, 0, wx.ALIGN_RIGHT | wx.ALIGN_TOP )
            self.settings_sizer.Add( sb, 0, wx.ALIGN_RIGHT | wx.ALIGN_TOP)
        else:
            self.settings_sizer.Add(lbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_TOP)
        ## text controls need more width.
        if isinstance(ctrl, wx._controls.TextCtrl):
            self.settings_sizer.Add(ctrl, 1, wx.EXPAND )
        else:
            self.settings_sizer.Add(ctrl, 1 )

    def gv(self, key):
        """Get a value for the key. It's less typing."""
        return fpsys.config.__dict__[key]

    def spinner(self, key, rnge, tip=None):
        """There were several, so I did a thing."""
        c = wx.SpinCtrl(self, -1, "")
        c.SetRange(rnge[0], rnge[1])
        c.SetValue( self.gv(key) ) 
        if tip: c.SetToolTip( wx.ToolTip( tip ) )
        return c

    def apply_pressed(self,evt):
        """
        Loop through the form dict and connect the dots.
        Put new values into fpsys.config, and set flags
        for MainFrame to test when it catches the event.
        """
        redraw = False
        for key,d in self.form.iteritems():
            # A 'dud' is a control that plays no part
            if not d["dud"]:
                changed=False
                # Is there a special func to get value?
                peek = d.get("peek",None)
                if peek: # yes
                    ctrlval = peek(d["control"])
                else:
                    ctrlval = d["control"].GetValue()
                # is there a default?
                getdef = d.get("default", None)
                if getdef:
                    # truthy test for "no value" (or empty string)
                    if not ctrlval: 
                        ctrlval = getdef # so, use default instead
                        # Since the value in the control just failed
                        # and we have to use a default, let's
                        # also plug the fixed value back into the
                        # control.
                        # This one may fail if ctrl has no SetValue
                        # method. I'm not worried right now.
                        d["control"].SetValue(getdef)

                # now I have the value from the control
                # Is it different from the config's version?
                # If so, update config.
                if ctrlval != self.gv(key):
                    changed=True
                    # If there's a special poke func, use it.
                    poke = d.get("poke",None)
                    if poke:
                        poke(ctrlval)
                    else:
                        fpsys.config.__dict__[key] = ctrlval
                    redraw = d["redraw"]
                d["changed"]=changed

        self._force_redraw = redraw
        ## Pass the event on to the MainFrame, where I use it
        ## to hide this panel.
        evt.Skip()

    def poke_app_char_map(self, v):
        """poke func. I could have use the event system,
        but I wanted to keep it all in the apply_pressed
        method."""
        self.CMC.set_current_appname( v )






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
            print shorterr
            self.SetStatusWidths([300,-2,-1,32])
            #self.SetStatusStyles([wx.SB_SUNKEN]*3) #SB_SUNKEN is not available to me. 
        else:
            self.SetStatusWidths([300,-2,32])
            #self.SetStatusStyles([wx.SB_SUNKEN]*2)

    def Report(self, msg):
        self.SetStatusText(msg, 1)
        print msg

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
        menu1.Append( self.id_purge, _("&Purge Pog.See TogglePurgeMenuItem for actual string."), _("Remove all ghost fonts from the selected Pog.") )

        self.MENUPURGE = menu1

        ## Nov 2017: Hush fonts
        menu1.Append( id_from_flag[flag_hush_fonts], _("&Hush fonts\tCtrl+H"), _("Silence all the noisy system fonts and focus only on those you want,"))
        
        menu1.AppendSeparator()

        self.id_exit = wx.NewId()
        self.exit = menu1.Append(self.id_exit, _("&Exit"), _("Close the app"))

        ## Tools
        self.menuBar.Append(menu1, _("&Tools"))


        ## SELECT MENU: June 2009
        menu3 = wx.Menu()
        self.id_selall = wx.NewId()
        menu3.Append( self.id_selall, _("&Select ALL the source fonts"), _("Select ABSOLUTELY ALL the fonts in the chosen source."))
        self.id_selnone = wx.NewId()
        menu3.Append( self.id_selnone, _("&Clear ENTIRE selection"), _("Clear the selection completely.") )
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

        ## Bind events for the menu items
        self.Bind(wx.EVT_MENU, self.onHandleESC, self.exit)
        
        #NOV 2017: Retiring this menu
        #I think PILLOW is more stable and I don't want to support the
        #extra code for the gui of this. The command line already does
        #a good job (-c) and my crash dialogue tells the user what to do.
        ##self.Bind(wx.EVT_MENU, self.menuCheckFonts, id = 102 )

        self.Bind(wx.EVT_MENU, self.menuPurgePog, id = self.id_purge )

        # June 2009
        self.Bind(wx.EVT_MENU, self.menuSelectionALL, id=self.id_selall)
        self.Bind(wx.EVT_MENU, self.menuSelectionNONE, id=self.id_selnone)

        ## Catch the Apply button *in* the settings panel.
        self.Bind(wx.EVT_BUTTON, self.apply_settings, id=wx.ID_APPLY)

        ## Catch the Zip button *in* the choose_zipdir_panel 
        self.Bind(wx.EVT_BUTTON, self.do_pog_zip, id=id_do_the_actual_zip)

        ## Catch the Hush buttons - Second handler, after toggle_dismissable_panel runs.
        ## The order was:
        ## 1. TargetPogChooser.multiClick --> Skip() to
        ## 2. Here.toggle_dismissable_panel --> Skip() to
        ## 3. Here:
        ## See the Bind to toggle_dismissable_panel just below.
        self.Bind(wx.EVT_BUTTON, self.do_hush_unhush, id=id_hush_button)
        #self.Bind(wx.EVT_BUTTON, self.do_hush_unhush, id=id_unhush_button)

        ## Nov 2017
        ## Vague Bind. Not specific to id. Happens FIRST, even though it's
        ## last in the code.
        ## 1. The close (X) button of the DismissablePanels
        ## 2. The ZIP button (Skipped to here from TargetPogChooser)
        self.Bind(wx.EVT_BUTTON,self.toggle_dismissable_panel )

        ## THE MAIN GUI
        ## ------------------------------------------------------------------

        ## A temporary switch to test out various ideas
        self.whatgui = 1

        MINSCREENWIDTH = 800 #old skool
        minw = 360
        fvminw = MINSCREENWIDTH - minw
        ms = wx.Size(minw,1)
        if self.whatgui == 1:

            ## PRIMARY GUI
            ## ===========
            ## No splitters at all.
            ## Box across: two
            ## Left box: Box vertical: two (source/target)
            ## Right box: Fontview
            ## :- kind of shape.

            self.panelFontSources = FontSourcesPanel(self)
            self.panelFontSources.SetMinSize(ms)

            self.panelTargetPogChooser = TargetPogChooser(self, id_zip_pog_button)#, id_hush_button, id_unhush_button)
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

            ## The Settings
            self.settings_panel = SettingsPanel(self)
            #self.settings_panel.Hide()

            ## Zip Pog panel
            self.choose_zipdir_panel = ChooseZipDirPanel(self)
            #self.choose_zipdir_panel.Hide()

            ## Hush panel
            self.hush_panel = HushPanel(self)


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
            #lrsizer.Add( self.unhush_panel, 1, wx.EXPAND )

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
        elif self.whatgui == 3:
            #Very out of date. Left for future maybes.
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
            fvminw = MINSCREENWIDTH
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
        self.Layout()

        ## This is to draw the correct icons depending on cli params.
        self.panelTargetPogChooser.pogTargetlist.SortOutTheDamnImages(False)

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
        print "toggleSelectionMenuItem runs."
        print evt.GetId()
        flag = flag_from_id.get(evt.GetId(),None)
        print "got flag:", flag
        if flag:
            self.flag_state_exclusive_toggle(flag)
            self.hide_or_show_panels()

        ## NB: I have more bindings after this handler is done:
        evt.Skip()


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
            ## If it's showing the normal (font) view, then:
            if self.is_state_flagged(flag_normal):
                ps.pub( update_font_view )

            self.resized = False

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
                ps.pub( fake_click_the_source_dir_control, None )
                # bail! So we don't do another re-draw.
                return

            ## Redraw the fitmaps (Will also hide the settings_panel)
            ps.pub( update_font_view )
        else:
            ## With no changes, we must hide the settings_panel
            self.ensure_fontview_shown()
        return




    def do_hush_unhush(self, e):
        id = e.GetId()
        print "do_hush_unhush {}".format(id)
        print fpsys.config.hush_pog_name
        #.. probeNoFontconfigDirError
        #.. then report the fail
        return

        buglist = []
        if id == id_hush_button:
            printer = self.hush_panel.printout 
            pogs = self.panelTargetPogChooser.list_of_target_pogs_selected
            #printer( u"".join(pogs) )
            buglist = fpsys.hush_with_pogs( pogs, printer )

        elif id == id_unhush_button:
            printer = self.unhush_panel.printout 
            buglist = fpsys.un_hush( printer )

        if buglist: 
            ## All errors end with this text:
            printer( strings.cant_hush, key="title")
            for bug in buglist: printer( bug )
            printer()
            printer( strings.see_help_hush, key="Help" )


    def do_pog_zip(self, e):
        """
        The button in the choose_zipdir_panel was clicked.
        """
        czd = self.choose_zipdir_panel
        todir = czd.get_path()
        emsg = ""
        if todir:
            wx.BeginBusyCursor()
            for p in self.panelTargetPogChooser.list_of_target_pogs_selected:
                ipog = fontcontrol.Pog(p)
                (bugs, fail, emsgs) = ipog.zip( todir )
                    
                if fail: 
                    czd.printout(
                       _("I could not create the zip for {}").format(ipog) )
                    czd.printout( emsgs[0])
                    czd.printout( "" )
                else:
                    czd.printout( 
                       _("Zipped as \"%s.fonts.zip\" in the \"%s\" directory.") % (p, todir) )
                    czd.printout( "" )
                    if bugs:
                        czd.printout( _("Some bugs happened:") )
                        for m in emsgs: czd.printout( m )
                        czd.printout( "" )
            wx.EndBusyCursor()

            if bugs:
                czd.printout(_("Some fonts were skipped, try purging the Pog(s) involved."))
                ps.pub(print_to_status_bar,_("Something went wrong."))
            else:
                czd.printout(_("Zip file(s) have been created."))
                ps.pub(print_to_status_bar,_("Zip file(s) have been created.") )

                #self.ensure_fontview_shown()


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

            wx.SplashScreen.__init__(self, fpwx.wxbmp( "splash" ), splashStyle, splashDuration, parent)
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
            fpwx.setup_fonts_and_colours()

            frame = MainFrame(None, _("Fonty Python: bring out your fonts!"))
            app.SetTopWindow(frame)

            frame.Show(True)

            if self.fc.IsRunning():
                self.Raise()


#Start the app!
app = App(0)
app.MainLoop()
