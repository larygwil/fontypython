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

"""
These classes comprise the "dismissable" panels that appear in the 
gui - over the top of the fontview (hide/show trickery) - to give 
functionality to:
    1. Help
    2. About
    3. Settings
    4. Zip pogs
    5. Hush fonts
"""

import locale, os
import strings
import fontybugs
import fpsys # Global objects
import wx

#For help and about:
import wx.html as html

#I need the various flags and id's defined at top of wxgui:
from wxgui import button_ids, id_from_flag, \
    flag_help, \
    flag_about, \
    flag_settings, \
    flag_choosedir, \
    flag_hush_fonts

# Tree for use in the zip panel
from gui_DirChooser import ATree

import fpwx

## ---
## The two basic classes for the DismissablePanels

class DismissablePanel(wx.Panel):
    """
    Only for subclassing.
    Provides a bar with an icon, title and an X close button.
    Under that is .. whatever: usually a sizer.

    wfunc: Is a function that will return a size. The caller
           must decide whom it trusts to return a sane value.
           We use it to set a sane size on the Panel we will
           soon construct. This, in turn, helps any labels,
           and paragraphs (various text controls) fit and
           helps with those that must wrap.
    """
    def __init__(self, parent, flag,
            someicon = None,
           somelabel ="...",
       extra_padding = 0,
               wfunc = None):

        id = id_from_flag[flag]
        self.id = id
    
        sz = (-1,-1)
        if wfunc: sz = wfunc()# seems work.. was:(wfunc()[0],-1)

        wx.Panel.__init__(self, parent, id,
                size = sz,
               style = wx.NO_FULL_REPAINT_ON_RESIZE )

        #self.SetMinSize(sz) # necc? Meh. Seems not..
        
        self.parent = parent
        self.flag = flag

        ## Go fetch the .. whatever 
        ## Seems I settled on returning a sizer from __post_init__
        whatever = self.__post_init__()
        
        ## Pad the whole thing some
        whatever_sizer = wx.BoxSizer( wx.VERTICAL )
        whatever_sizer.Add( whatever, 1,
                wx.EXPAND | wx.ALL,  border = 8 + extra_padding )

        l = fpwx.h1( self, somelabel )

        x_button = wx.BitmapButton(self, -1, fpwx.wxbmp( "icon_X" ), style = wx.NO_BORDER)
        x_button.SetToolTipString( _("Dismiss") )
        #x_button = wx.Button(self, -1, label="X", 
        #        style = wx.NO_BORDER | wx.BU_EXACTFIT)
        self.Bind(wx.EVT_BUTTON, self.__x_pressed, x_button)

        x_button.SetToolTipString( _("Dismiss") )

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        if someicon:
            hbox.Add( fpwx.icon( self, someicon ), 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border = 12 )
        else:
            hbox.Add( (1,1), 0, wx.EXPAND )
        # push the label down to better align with the X
        hbox.Add( l, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL | wx.TOP, border = 6 ) 
        hbox.Add( x_button, 0, wx.ALIGN_RIGHT  | wx.BOTTOM, 
                border = 4 )
        hbox.Add( (8,8),0)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add( hbox, 0, wx.EXPAND | wx.TOP ,
                border = 16 ) #Wanted more space above.
        self.vbox.Add( whatever_sizer, 1, wx.EXPAND)
        self.SetSizer( self.vbox )
       
        self.Layout()
        #self.Fit()
        self.SetFocus()

        self._firstshow = True
        self.Bind(wx.EVT_SHOW, self.__catch_show_or_hide)

    ## Weirdly public
    def __post_init__(self):
        pass

    ## Private
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

        # merge all the dicts. Missing keys will raise.
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

        def header(t,e):
            return u"<h6>Missing {}</h6>" \
                    "{}".format( 
                            t, 
                            unicode(e).replace("\n","<br>")
                            )

        def pccp(t):
            return u"<pre><code>{}</code></pre>".format(t)

        s_fpdir = pccp(
                fpsys.LSP.to_unicode(fpsys.iPC.appPath()) )

        ## Let's use our fancy error stuff to swap-in 
        ## a message about the user fonts directory, 
        ## should it be missing!
        e = fpsys.iPC.get_error_or_none("NoFontsDir")
        if e:
            s_fontsdir = header(_(u"User Fonts"), e)
        else:
            s_fontsdir = pccp(
                    fpsys.LSP.to_unicode(
                        fpsys.iPC.userFontPath()))

        ## Also fontconfig's directory
        e = fpsys.iPC.get_error_or_none("NoFontconfigDir")
        if e:
            s_fcdir = header(_(u"Fontconfig"), e)
            s_fcpaf = _(u"No path: Fontconfig is not functioning.")
        else:
            s_fcdir = pccp(
                    fpsys.LSP.to_unicode(
                        fpsys.iPC.user_fontconfig_confd()))
            s_fcpaf = pccp(fpsys.HUSH_PAF)

        ## Show the home directory too.
        s_home = fpsys.LSP.to_unicode(fpsys.iPC.home())
        
        d={
            "FP_DIR" : s_fpdir,
            "UF_DIR" : s_fontsdir,
            "FC_DIR" : s_fcdir,
            "FC_PAF" : s_fcpaf,
              "HOME" : s_home,
        "TICKET_URL" : strings.ticket_url,
            } 
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
    The whole thing can be in two states:
    1. Error -> fontconfig/conf.d is not available.
       Fatal. The entire show is off. Go home!
    2. Ok -> Continue to hush/unhush. Other errors can 
       still happen during that process, and they appear
       in the printer.
    
    When ok, there are two states of hush:
    1. Hush on -> offer to turn it on
    2. Hush off-> offer to turn it off.

    Ok state:
    =========
    Displays a large heading of the hush state.
    Shows some help text.
    Offers a choice of pog names to hush with.
    Has a large printer for the call back to report into.
    Button to hush/unhush.

    Error state:
    ============
    Display error title.
    Display some help.
    Display the error itself, in the printer.
    """
    def __init__(self, parent, wfunc):
        #state dict
        self.sd = {
                 "hush_on" :{"h":_("Hushing is on."  ), "b":_("Un-hush fonts")},
                 "hush_off":{"h":_("Hushing is off."  ),"b":_("Hush fonts")},
         "fontconfig_error":{"h": strings.cant_hush    ,"b":_("Cannot hush")}
                  }


        DismissablePanel.__init__(self,parent, flag_hush_fonts,
                somelabel = _("Hush Fonts"),
                someicon = "icon_hush",
                wfunc = wfunc) 

    def __post_init__(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        ## This decides the error vs ok states:
        self.fontconfig_error = fpsys.iPC.get_error_or_none("NoFontconfigDir")

        if not self.fontconfig_error:
            title = u"xx"
        else:
            title = self.sd["fontconfig_error"]["h"]
        
        ## Big header announcing Hushed/Not hushed
        ## Real tortured code to center the fuckin' label text. Jeezuz.
        ## Half the time the text was chopped-off on first draw. :(
        hush_heading_panel = wx.Panel(self,size=(-1,150), style=wx.SUNKEN_BORDER)
        
        f = wx.BoxSizer(wx.HORIZONTAL)
        bsp = wx.BoxSizer(wx.VERTICAL)
        self.hush_state_label = fpwx.h0( hush_heading_panel, title)
        bsp.Add(self.hush_state_label, 1, wx.ALIGN_CENTER_HORIZONTAL )
        f.Add(bsp, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border = 40)
        hush_heading_panel.SetSizer( f )

        sizer.Add( hush_heading_panel, 0, wx.EXPAND | wx.BOTTOM, border = 5)

        if not self.fontconfig_error:
            ## The label to the intro text
            self.chosen_pog_label = fpwx.h1( self, _("The Hush Pog:") )
            sizer.Add( self.chosen_pog_label, 0, wx.ALIGN_TOP)
            
            ## The intro text - is wrappable!
            p1 = fpwx.para( self, _(
                u"Hushing installs a Pog that you must manage. " \
                 "Make sure it contains a few system fonts so that " \
                 "your applications function properly!\n" \
                 "Look in /usr/share/fonts for ideas. " \
                 "Please see help for details."),
                 wrap = True)
                                      
            sizer.Add( p1, 0, wx.TOP, border = 5 )

            h = wx.BoxSizer(wx.HORIZONTAL)

            ## label to the choice box
            self.chosen_pog_label = fpwx.label( self, _("Current Hush Pog: ") )
            h.Add( self.chosen_pog_label, 0, wx.TOP, border = 30)

            ## The pog choice box
            self.pog_choice = wx.Choice(self, -1, choices = ["-"])
            self.pog_choice.SetToolTip( wx.ToolTip( _("Choose your system Pog") ) )
            self.pog_choice.Bind(wx.EVT_CHOICE, self._pog_chosen )
            
            h.Add( self.pog_choice, 0, wx.ALIGN_TOP | wx.TOP, border = 20)

            sizer.Add(h,0, wx.BOTTOM, border = 20)
        else:
            ## Some help re the error - also wrappable!
            p1 = fpwx.para( self, _( 
                u"Fontconfig is not properly installed; thus " \
                 "Fonty cannot hush fonts.\n" \
                 "Consult your distribution's help, or " \
                 "open a ticket so we can try fix it. " \
                 "Please see help for details."),
                 wrap = True)

            sizer.Add( p1, 0, wx.TOP, border = 5 )

        ## Area to print into
        pl = fpwx.label( self, _("Progress report:") )
        sizer.Add( pl, 0, wx.BOTTOM, border = 10)
        self.printer = wx.TextCtrl(self,
            -1, "", style = wx.TE_READONLY | wx.TE_MULTILINE)
        font = self.printer.GetFont()
        font = wx.Font(font.GetPointSize(), wx.TELETYPE,
                       font.GetStyle(),
                       font.GetWeight(), font.GetUnderlined())
        self.printer.SetFont(font)
        sizer.Add (self.printer, 1, wx.EXPAND )

        if self.fontconfig_error:
            ## Dump the initial NoFontconfigDir error into the printer
            self.printout( unicode(self.fontconfig_error), key="ERROR")

        if not self.fontconfig_error:
            ## The hush/unhush button
            self.hb = wx.Button( self, label = self._update_heading("b"),
                    id = button_ids['id_hush_button'] )
            ## Make a button. Click also gets caught in MainFrame.
            self.Bind(wx.EVT_BUTTON, self._do_hushing,
                    id = button_ids['id_hush_button'])
            sizer.Add(self.hb, 0, wx.TOP | wx.BOTTOM | wx.EXPAND, border=10)
            self._update_pog_choice_control()

        return sizer

    def _pog_chosen(self,evt):
        """
        The choice control was changed.
        Forbid index 0 as a valid choice.
        """
        n = evt.GetSelection()
        if n == 0:
            s = ""
            self.hb.Disable()
        else:
            s = evt.GetString()
            self.hb.Enable()
        ## s is a byte string
        fpsys.config.hush_pog_name = s

    def _update_heading(self, key):
        """
        Get strings for either the heading or the button
        depending on state.
        """
        if self.fontconfig_error:
            return self.sd["fontconfig_error"][key]

        if os.path.exists(fpsys.HUSH_PAF):
            return self.sd["hush_on"][key]
        else:
            return self.sd["hush_off"][key]
    
    def _update_pog_choice_control(self):
        """
        In case Pogs were added/deleted, we must refresh this list.
        Refill the choice list, sort and select the last string.

        We also ensure that there's no invalid choice in the control.
        If the hush pog, from config, is *not* in the control's list
        then we set the config to "" and start again.
        """
        ## Empty the choice control.
        self.pog_choice.Clear()
        ## Now refill it
        pl = fpsys.iPC.getPogNames() # pl is all byte strings (encoded)
        pl.sort(cmp=locale.strcoll) # sort according to locale
        ## Let's add a "none" choice in index 0
        self.pog_choice.Append(_(u"None chosen"))
        ## then the pogs:
        self.pog_choice.AppendItems( pl ) # stick it in the control
        ## get the last used hush Pog name - make sure it's a byte, else..
        s = fpsys.LSP.ensure_bytes( fpsys.config.hush_pog_name )
        if s not in pl: # ...we get complaints here.
            # ok - that name was not in the control. Something changed.
            n = 0 # this has the effect of selecting "None chosen" 
            # The choice was invalid, so empty the config too:
            fpsys.config.hush_pog_name = ""
            self.hb.Disable()
        else:
            # s is ok, let's seek its index in the control
            n = self.pog_choice.FindString(s)
            self.hb.Enable()
        # now set it as selected in the control
        self.pog_choice.SetSelection( n )

    def _show_or_hide(self, showing):
        """
        The entire panel hide/show
        If in error state, just bail.
        """
        if self.fontconfig_error: return
        if showing:
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
        self.printer.Clear() # fresh for new data
        fpsys.config.hush_pog_name = self.pog_choice.GetStringSelection()
        ## Skip the event along to the main frame. See Bind there.
        evt.Skip()

    ## Public defs

    def printout(self, msg="\n", key=None):
        """
        A callback for the actual hush code to
        use as a printer.
        The key is meant as a way to alter how
        things display. Only using ERROR really.
        """
        if key:
            key = key.upper()
            c = "="
            if key == "ERROR":
                c = "*"
            self.printer.write(key + "\n")
            self.printer.write(c * len(key) + "\n")

        self.printer.write(fpsys.LSP.ensure_unicode(msg) + "\n")

    def after_do_hushing(self):
        """
        Called after the do_hush_unhush in main frame.
        Switches state and updates the form without 
        clearing the printer.
        """
        self._update_pog_choice_control()
        self.hush_state_label.SetLabel(self._update_heading("h"))
        self.hb.SetLabel(self._update_heading("b"))



class ChooseZipDirPanel(DismissablePanel):
    """
    Deals with all the crap the zip functionality needs.
    """
    def __init__(self, parent, wfunc):
        DismissablePanel.__init__(self,parent, flag_choosedir, 
                somelabel=_("Locate a directory for the zip file(s)"),
                someicon = "icon_zip",
                wfunc = wfunc) 
        self._chosen_path = None

    def __post_init__(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        # A top, shows what pogs are going to be zipped
        # Because it's writable, we send along a layout
        # function. See AutoWrapStaticText
        self.what_pogs_lbl = fpwx.label( self, u"..",
                Layout_func = self.Layout )
        sizer.Add( self.what_pogs_lbl, 0, wx.EXPAND | wx.TOP, border = 10)

        # The tree to find a path
        self.treedir = ATree(self, os.getcwd())
        tree = self.treedir.GetTreeCtrl()
        #Clicks on the control will change the button's label
        tree.Bind(wx.EVT_TREE_SEL_CHANGED, self._on_dir_control_click)
        sizer.Add(self.treedir, 1, wx.EXPAND | wx.TOP, border = 10)

        # Label to show the directory chosen (or the default)
        # Tries to wrap. Paths without spaces don't wrap, so we use
        # ellipses.
        self.what_dir_lbl = fpwx.label( self, 
                self._make_label(),
                ellip = wx.ST_ELLIPSIZE_END,
                Layout_func = self.Layout)  # Layout_func bec. we use SetLabel
        sizer.Add( self.what_dir_lbl, 0, wx.EXPAND | wx.TOP, border=10)

        # A printer that will show when it has to.
        self.printer = wx.TextCtrl(self,
            -1, "", style = wx.TE_READONLY | wx.TE_MULTILINE)
        font = self.printer.GetFont()
        font = wx.Font(font.GetPointSize(), wx.TELETYPE,
                       font.GetStyle(),
                       font.GetWeight(), font.GetUnderlined())
        self.printer.SetFont(font)
        sizer.Add (self.printer, 1, wx.EXPAND | wx.TOP, border=10 )
        self.printer.Hide()

        ## Make a button. Click also gets caught in MainFrame.
        btn = wx.Button(self, label = _("Create the zip file"),
                                id=button_ids['id_do_the_actual_zip'])
        self.Bind(wx.EVT_BUTTON, self._do_actual_zip, id=button_ids['id_do_the_actual_zip'])
        sizer.Add(btn, 0, wx.TOP | wx.BOTTOM | wx.EXPAND, border=10)

        return sizer

    def _show_or_hide(self, showing):
        """The entire panel hide/show"""
        if showing:
            # I am being shown
            wpogs = u", ".join( self.parent.panelTargetPogChooser.list_of_target_pogs_selected )
            self.what_pogs_lbl.SetLabel( u"Pog(s) to zip: {}".format(wpogs) )
            if self.printer.IsEmpty():
                self.printer.Hide()
            else:
                self.printer.Show()
        else:
            # I am being hidden ( esc, or x)
            self.printer.Clear()
            self.printer.Hide()

    def _make_label(self, p=None):
        if not p: p = os.getcwd()
        return _("The zip file(s) will be put into:\n{}").format(p)

    def _on_dir_control_click(self,e):
        cp = self.treedir.GetPath()
        self.what_dir_lbl.SetLabel(self._make_label(cp))

    def _do_actual_zip(self, evt):
        """
        Forwards the click on to MainFrame where it's also bound.
        """
        self._chosen_path = self.treedir.GetPath()
        evt.Skip()

    ## Public defs
    def get_path(self):
        return self._chosen_path

    def printout(self, msg):
        self.printer.write(msg + "\n")
        if not self.printer.IsShown(): 
            self.printer.Show()
            self.Layout()


##Slider code - maybe for settings form
#self.choiceSlider = wx.Slider(self, value=1, minValue=1, maxValue=1, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
#self.choiceSlider.SetTickFreq(1,1)
#self.choiceSlider.Bind(wx.EVT_SCROLL, self.OnSliderScroll)
## ... it sucked!
class SettingsPanel(DismissablePanel):
    def __init__(self, parent, wfunc):
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
                extra_padding = 12,
                wfunc = wfunc) 

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
        c = wx.CheckBox(self, -1, _("Tick to include all\n" \
                                    "sub-folders in\nthe source view.") )
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
            e = fpwx.parar(self, extra, pointsize = "points_tiny" )
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


