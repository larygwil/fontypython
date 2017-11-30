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
import wx.lib.stattext
import wx.lib.buttons as buttons

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
##langid = wx.LANGUAGE_DEFAULT # Picks this up from $LANG
##mylocale = wx.Locale( langid )


from pubsub import *
from wxgui import ps

from gui_ScrolledFontView import *

import fpsys # Global objects
import fontyfilter
import fontybugs

#from fpwx import label, icon, wxbmp
import fpwx

##The SearchAssistant idea was to have a panel that opens to give tips and interactive
##help for searching. We were going to have field and PANOSE access via fontTools but
##this dev. has paused -- until someone else with a clue can help....
##So, this code will just remain as a remark:
#class SearchAssistant(wx.CollapsiblePane):
#	def __init__(self, parent):
#		self.label1=_("Click for Search Assistant")
#		self.label2=_("Close Search Assistant")
#		wx.CollapsiblePane.__init__(self,parent, label=self.label1,style=wx.CP_DEFAULT_STYLE)#|wx.CP_NO_TLW_RESIZE)
#		self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnPaneChanged)
#		self.MakePaneContent(self.GetPane())
#		
#	def OnToggle(self, evt):
#		self.Collapse(self.IsExpanded())
#		self.OnPaneChanged()
#		
#	def OnPaneChanged(self, evt=None):
#		#if evt:
#		   # self.log.write('wx.EVT_COLLAPSIBLEPANE_CHANGED: %s' % evt.Collapsed)
#
#		# redo the layout
#		self.GetParent().Layout()
#
#		# and also change the labels
#		if self.IsExpanded():
#			self.SetLabel(self.label2)
#		else:
#			self.SetLabel(self.label1)
#		
#
#	def MakePaneContent(self, pane):
#		nameLbl = wx.StaticText(pane, -1, _("Search Assistance.") )
#		border = wx.BoxSizer()
#		border.Add(nameLbl, 1, wx.EXPAND|wx.ALL, 5)
#		pane.SetSizer(border)

class SearchFilter(wx.SearchCtrl):
    """
    Borrowed, as always, from the superb wxPython demo.
    This new control replaces my old combo box
    for the filtering of font items.

    Uses two callbacks.
    """
    max_searches = 25
    def __init__(self, parent, id=-1, value="",
                 pos=wx.DefaultPosition, size=wx.DefaultSize, style=0,
                 search_func = None, 
                 cancel_func = None):

        # wx.TE_PROCESS_ENTER is required for
        # EVT_TEXT_ENTER event to work.
        style |= wx.TE_PROCESS_ENTER

        wx.SearchCtrl.__init__(self, parent, id, value, pos, size, style)

        self.ShowCancelButton(True)
        self.SetCancelBitmap(fpwx.wxbmp("clear"))

        self.Bind(wx.EVT_TEXT_ENTER, self.OnTextEntered)
        self.Bind(wx.EVT_MENU_RANGE, self.OnMenuItem,
                id=1, id2=self.max_searches)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.on_cancel)
        
        ## Callbacks
        self.do_search_func = search_func
        self.do_clear_func = cancel_func

        ## History
        self.searches = []

    def on_cancel(self,e):
        self.do_clear_func()
        self.SetValue("")

    def OnTextEntered(self, evt):
        if self.do_search_func( self.GetValue() ):
            self.add_to_history()
        #self.SetValue("")

    def set_BIR(self,t):
        """
        When one of the 
        Bold, Italic, Regular 
        are clicked, we call this.
        """
        if t:
            self.SetValue(t)
            if t not in self.searches:
                self.add_to_history()
        else:
            self.SetValue("")

    def add_to_history(self):
        self.searches.append( self.GetValue() )
        if len(self.searches) > self.max_searches:
            del self.searches[0]
        self.SetMenu( self.make_new_menu() )

    def OnMenuItem(self, evt):
        text = self.searches[evt.GetId()-1]
        self.SetValue(text)
        self.do_search_func(text)
        
    def make_new_menu(self):
        menu = wx.Menu()
        item = menu.Append(-1, _("Recent Filters"))
        item.Enable(False)
        for idx, txt in enumerate(self.searches):
            menu.Append( 1+idx, txt )
        return menu


class FontViewPanel(wx.Panel):
    """
    Standalone visual control to select fonts.
    The Panel that holds the ScrolledFontView control
    as well as the buttons etc. below and the text above.
    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id = -1)
        self.firstrun = True

        self.pageindex = 1 # I start here
        self.total_number_of_pages = 0

        self.filter = ""

        self.TICKMAP = None
        self._TICK = fpwx.wxbmp( 'tick' )
        self._CROSS = fpwx.wxbmp( 'cross' )

        #Sept 2009
        ## Bitmaps to be used in the Fitmap drawing.
        ## Fetched from there as dict items. It got weird.
        self.SEGFAULT  = fpwx.wxbmp( 'font_segfault' )
        self.NO_DRAW   = fpwx.wxbmp( 'font_cannot_draw' )
        self.NOT_FOUND = fpwx.wxbmp( 'font_not_found' )
        self.INFO_ITEM = fpwx.wxbmp( 'font_info_item' )
        self.TICKSMALL = fpwx.wxbmp( 'ticksmall' )
        self.BUTTON_CHARMAP = fpwx.wxbmp( 'button_charmap' )
        self.BUTTON_CHARMAP_OVER = fpwx.wxbmp( 'button_charmap_over' )

        ## --
        ## Dicts for use in state
        ##
        self._setup_state_dicts()

        ##
        ## START GUI
        ## ===
        #icon_open_folder = fpwx.wxbmp("icon_open_folder")
        #icon_pog = fpwx.wxbmp("pog16x16")
        #icon_pog_installed = fpwx.wxbmp("pog16x16.installed")

        ## Sizer: to hold all the others
        main_view_sizer = wx.BoxSizer( wx.VERTICAL )

        ## Sizer: Icon and Main Label
        icon_and_text_sizer = wx.BoxSizer(wx.HORIZONTAL)

        ## Sizer: Filter and Pager controls
        filter_and_pager_sizer = wx.BoxSizer(wx.HORIZONTAL)

        ## Icon
        view_icon = fpwx.icon(self, 'icon_viewing')

        # Main heading
        self.main_font_info_label = fpwx.h1(self, u"..",
                ellip = wx.ST_ELLIPSIZE_END, Layout_func = self.Layout )

        icon_and_text_sizer.Add(view_icon, 0,
                wx.TOP | wx.ALIGN_CENTER_HORIZONTAL,
                border = 8)

        icon_and_text_sizer.Add(self.main_font_info_label, 1,
           wx.LEFT | wx.TOP | wx.ALIGN_CENTER_HORIZONTAL,
           border = 4)

        ## The status label
        self.status_text = fpwx.label(self, u"Subinfo",
                ellip = wx.ST_ELLIPSIZE_END, Layout_func = self.Layout )

        ## Quick search Bold Italic Regular buttons
        ## It occurs to me that these are English words...
        ## Do fonts contain i18n on styles?
        ## See: https://fontforge.github.io/fontstyles.html
        idBold = wx.NewId()
        idItalic = wx.NewId()
        self.idRegular = wx.NewId()
        self.BIR = {
           idBold  : {'style': "bold",    'truth': False, 'instance': None},
           idItalic: {'style': "italic",  'truth': False, 'instance': None},
     self.idRegular: {'style': "regular", 'truth': False, 'instance': None}
           }
        toggle_sizer = wx.BoxSizer(wx.HORIZONTAL)
        for idy, dic in self.BIR.iteritems():
            bBIR = wx.ToggleButton( self, idy, size=(32,-1), style=wx.NO_BORDER )
            #Remarked label to show icons instead, label=dic['label'])
            bBIR.Bind( wx.EVT_TOGGLEBUTTON, self.onBIR )

            bmp = fpwx.wxbmp( 'icon_{}'.format(dic['style']) )
            bBIR.SetBitmap( bmp )
            
            bBIR.SetToolTipString( _("Filter {} fonts").format(dic['style']) )

            self.BIR[idy]['instance'] =  bBIR
            
            toggle_sizer.Add( bBIR, 1, wx.EXPAND )

        filter_and_pager_sizer.Add(toggle_sizer, 1,
                wx.EXPAND )

        # Search box - has two callbacks
        self.search_filter = SearchFilter(self,
                search_func = self.do_search,
                cancel_func = self.on_clear_button_click)

        self.last_filter_string = ""

        filter_and_pager_sizer.Add( self.search_filter, 5,
                wx.ALIGN_LEFT | wx.EXPAND \
                | wx.RIGHT, border = 6)

        ## The pager pulldown
        pager_label = fpwx.label(self, _(u"Page:"))
        self.pager_combo = wx.ComboBox(self, -1,
                value="1", choices=["busy"],
                style = wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER )

        self.pager_combo.Bind(wx.EVT_COMBOBOX, self.onPagechoiceClick )
        self.pager_combo.Bind(wx.EVT_TEXT_ENTER, self.onPagerChoiceTextEnter )

        filter_and_pager_sizer.Add( pager_label, 0,
                wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT,
                border = 6  )
        filter_and_pager_sizer.Add( self.pager_combo, 1 )#, wx.ALIGN_RIGHT )

        ## The SCROLLED FONT VIEW panel:
        self.scrolledFontView = ScrolledFontView(self)

        ## Sizer: for buttons prev, main, next
        bottom_buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)

        #July 2016
        #=========
        # The stock icon on the button was not showing under gtk3.
        # This stock button has not been translated into Afrikaans yet. (Dec 2007)
        # I can't tell you how this fkuced me around!
        # July 2016 - remarked : self.next_button = wx.Button(self, wx.ID_FORWARD)  
        # I have switched to a bitmapbutton. I hope this works...
        ###
        # For future:
        # example = wx.BitmapButton(self, -1, fpwx.wxbmp( "xxx" ),
        #  style = wx.NO_BORDER)

        # Previous button
        #self.previous_button = wx.BitmapButton( self, wx.ID_BACKWARD, 
        #        wx.ArtProvider.GetBitmap( 
        #            wx.ART_GO_BACK, wx.ART_BUTTON, (32,32) ))

        self.previous_button = wx.BitmapButton( self, wx.ID_BACKWARD,
                fpwx.wxbmp( 'icon_prev_page'))
        # Main button
        self.button_main = wx.Button(self, label=" ")
        self.buttMainLastLabel=" "

        # Next button
        #self.next_button = wx.BitmapButton( self, wx.ID_FORWARD,
        #        wx.ArtProvider.GetBitmap( 
        #            wx.ART_GO_FORWARD, wx.ART_BUTTON, (32,32) ))

        self.next_button = wx.BitmapButton( self, wx.ID_FORWARD,
                fpwx.wxbmp( 'icon_next_page'))
        self.previous_button.Enable( False ) # Starts out disabled


        bottom_buttons_sizer.Add( self.previous_button, 0, 
                wx.EXPAND | wx.RIGHT,
                border = 8)

        bottom_buttons_sizer.Add( self.button_main, 1,
                wx.EXPAND | wx.RIGHT,
                border = 8)

        bottom_buttons_sizer.Add( self.next_button, 0,
                wx.EXPAND)


        ## Start at the top: the icon and label
        main_view_sizer.Add(icon_and_text_sizer, 0,
                wx.EXPAND )

        ## Sub label
        main_view_sizer.Add(self.status_text, 0, 
                wx.EXPAND | wx.TOP,
                border = 4)

        ## Fill the Choice and Filter
        main_view_sizer.Add(filter_and_pager_sizer, 0,
                wx.EXPAND | wx.TOP,
                border = 8 )

        ## Fill the SIZER FOR THE SCROLLED FONT VIEW
        main_view_sizer.Add(self.scrolledFontView, 1,
                wx.EXPAND | wx.TOP,
                border = 8 )

        ## Fill the bottom buttons   
        main_view_sizer.Add(bottom_buttons_sizer, 0,
                wx.EXPAND | wx.TOP, border = 10)

        ## Do the voodoo thang
        self.SetSizer(main_view_sizer)
        self.Fit()

        ## Bind events
        self.previous_button.Bind(wx.EVT_BUTTON, self.navClick)
        self.next_button.Bind(wx.EVT_BUTTON, self.navClick)
        self.Bind(wx.EVT_BUTTON, self.onMainClick, self.button_main)#.GetId() ) 

        ## Advertise some local functions:
        ps.sub( left_or_right_key_pressed, self.OnLeftOrRightKey ) ##DND: class FontViewPanel

        ps.sub( toggle_main_button, self.ToggleMainButton ) ##DND: Called in gui_Fitmap
        ps.sub( update_font_view, self.MainFontViewUpdate ) ##DND: class FontViewPanel
        ps.sub( reset_to_page_one, self.ResetToPageOne ) ##DND: class FontViewPanel 

    # Tried to implement wrapping on some of the labels.
    # It flickers and fails. Fuck it.
    #def on_evt_size(self,e):
        #w = e.GetSize()[0]
        #w = max(w+5,200)
        #self.status_text.Wrap(w)
     #   e.Skip()

    def on_clear_button_click( self):#, event ):
        self.filter = ""

        # Clear the BIR toggle buttons
        self.setAllBIRFalse()

        ## Now command a change of the view.
        ## First, return user to page 1:
        self.pageindex = 1
        self.filterAndPageThenCallCreateFitmaps()
        self.button_main.SetFocus()  #a GTK bug demands this move. Restore the ESC key func.

    def setOneBIR( self, idy, truth ):
        self.BIR[idy]['truth'] = truth
        self.BIR[idy]['instance'].SetValue( truth )

    def setAllBIRFalse( self ):
        for idy in self.BIR.keys():
            self.setOneBIR( idy, False )

    def onBIR( self, e ):
        idy=e.GetId()
        toggstate = self.BIR[idy]['instance'].GetValue()

        self.BIR[idy]['truth'] = toggstate

        ss=""
        if self.BIR[idy]['style'] == "regular":
            # only if this is toggle on, do we want
            # action anything:
            if toggstate is True:
                # can't have regular with bold/italic
                self.setAllBIRFalse() # switch all off
                self.setOneBIR( idy, True )
                ss = "regular|normal"
        else:
            self.setOneBIR( self.idRegular, False )
            for idy, dic in self.BIR.iteritems():
                # Builds AND regex (space is and)
                if dic['truth']: ss += "%s%s" % (dic['style']," ")
            ss = ss[:-1]
        # Go alter the search text box
        self.search_filter.set_BIR(ss)

        # Start the process
        self.startSearch( ss )

    
    def do_search(self, sstring):
        """
        SearchFilter control will call this with
        sstring being the filter term.
        """
        self.startSearch(sstring)
        self.button_main.SetFocus()
        return True # to store in history

    def startSearch(self, terms):
        self.filter = terms
        ## First, return user to page 1:
        self.pageindex = 1

        ## Now command a change of the view.
        self.filterAndPageThenCallCreateFitmaps()


    def filterAndPageThenCallCreateFitmaps(self):
        """
        Figure out what list of fonts to draw, divide them into pages,
        then go make Fitmaps out of them.
        """

        self.total_number_of_pages = 1 # A default

        ## Is there anything there to view?
        if len(fpsys.state.viewobject) > 0:

        ## JUNE 2009 : Changes made

            ## If the filter string changed from last time, signal so.
            filter_changed = False
            if self.filter != self.last_filter_string: filter_changed = True
            self.last_filter_string = self.filter

            ## If the filter did change OR we have a blank filteredViewObject, then make a new one.
            if not fpsys.state.filteredViewObject or filter_changed:
                fpsys.state.filteredViewObject = fontyfilter.doFilter( self.filter ) # Uses the external module to filter.

            ## STEP 2 : Figure out how many pages we have to display
            current_page = self.pageindex - 1
            num_in_one_page = fpsys.config.numinpage
            total_num_fonts = len(fpsys.state.filteredViewObject)

            ## Many thanks to Michael Hoeft for this fix! I suck at math :)
            # I miss the right words to explain this step, therefore an example:
            # 	23 / 10 = 2
            # 	23 % 10 = 3 > modulo > bool(3) = True = 1
            # 	-----------------------------------------
            # 	2 + 1 = 3 >  3 pages
            #
            #	40 / 10 = 4
            # 	40 % 10 = 0 > modulo > bool(0) = False = 0
            #	------------------------------------------
            # 	4 + 0 = 4 >	4 pages
            self.total_number_of_pages = (total_num_fonts / num_in_one_page) + bool(total_num_fonts % num_in_one_page)

            start = current_page * num_in_one_page #leaf thru the pages to the one we are on now.
            fin = start + num_in_one_page
            if fin > len(fpsys.state.filteredViewObject): fin = len(fpsys.state.filteredViewObject) #Make sure we don't overshoot.

            ## Extract a single page of fonts to display
            sublist = fpsys.state.filteredViewObject[start:fin]

            ## Empty the choice control.
            self.pager_combo.Clear()

            ## Now refill it
            [self.pager_combo.Append(str(n)) for n in xrange(1, self.total_number_of_pages +1)]
            self.pager_combo.SetSelection(self.pageindex-1)
            #self.choiceSlider.SetRange(1,self.total_number_of_pages+1)

        ## The viewobject is empty anyway.
        else:
            sublist = []

        if self.total_number_of_pages == 1:
            self.pager_combo.Enable(False) #I tried to hide/show the choice, but it would not redraw properly.
            #self.choiceSlider.Enable(False)
        else:
            self.pager_combo.Enable(True)
            #self.choiceSlider.Enable(True)

        self.scrolledFontView.MinimalCreateFitmaps( sublist ) # Tell my child to draw the fonts

        self.EnableDisablePrevNext()




    def _setup_state_dicts(self):
        """
        These dicts are used in MainFontViewUpdate.
        They hold the variables and such for various
        states of the app i.t.o Source/View and Target.
        """
        # Some common strings
        nadatd = _("There's nothing much to do.")
        ntd = _("Choose some fonts")
        # The "nothing add remove samepogs" dict
        # Will be used in the main dict below.
        n_a_r_s = { 
         'n' : { #Nothing
            'btext': ntd,
           'action': "NOTHING_TO_DO",
             'info': nadatd,
          'cantick': False,
             'tmap': self._TICK #default, but is not drawn. 
             },
         's' : { #Same
            'btext': ntd,
           'action': "NOTHING_TO_DO",
             'info': nadatd,
          'cantick': False,
             'tmap': self._TICK
             },
         '-' : { #Remove
            'btext': _("Remove fonts from {VIEW}"),
             'info': _("You can remove fonts from this source Pog."),
           'action': "REMOVE",
          'cantick': True,
             'tmap': self._CROSS
             },
         '+' : { #Append
            'btext': _("Put fonts into {TARGET}"),
             'info': _("You can append fonts to the active target Pog \"{TARGET}\"."),
           'action': "APPEND",
          'cantick': True,
             'tmap': self._TICK
            }}

        # A way to test for recurse flag later
        recurse_test = lambda: _(" (and all sub-folders.)") \
                               if fpsys.config.recurseFolders else ""

        # Some common strings
        vF = _("Viewing source Folder \"{VIEW}\"{{RT}}")
        vP  =_("Viewing source Pog \"{VIEW}\"")
        choose_source = _("Choose a Source Pog or Folder.")
        nochangetarget = _("The target Pog \"{TARGET}\" is installed. "\
                        "It can't be changed.")

        # The main "label" dict.
        # See remarks in MainFontViewUpdate for details.
        self.lbl_d = { 
          ## Empty to Nothing
          'EN' : {
            'lab': _("There are no fonts in here."),
            'tip': choose_source,
           'nars': n_a_r_s['n']
               },

          ## Empty to Pog
          'EP' : {
            'lab': _("Source is empty. The active target Pog is \"{TARGET}\""),
            'tip': choose_source,
           'nars': n_a_r_s['n']
               },

          ## Folder to Nothing  
          'FN' : {
            'lab': vF,
           'nars': n_a_r_s['n'],
          'rtest': recurse_test
               },

          ## Pog to Nothing  
          'PrN': {
            'lab': _("Viewing (installed Pog) \"{VIEW}\""),
            'tip': _("You can't change an installed Pog."),
           'nars': n_a_r_s['n']
               },
          'PwN': { # '-' Remove from source pog
            'lab': _("Viewing (editable Pog) \"{VIEW}\""),
            'tip': _("There is no active target."),
           'nars': n_a_r_s['-']
               },

          ## Folder to Pog
          'FPr': {
            'lab': vF,
            'tip': nochangetarget,
           'nars': n_a_r_s['n'],
          'rtest': recurse_test,
               },
          'FPw': { # Add to target Pog
            'lab': vF,
           'nars': n_a_r_s['+'],
          'rtest': recurse_test,
              },

          ## Pog to Pog
          'PPr': {
            'lab': vP,
            'tip': nochangetarget,
           'nars': n_a_r_s['n'],
              },
          'PPs': {
            'lab':  _("Source and Target \"{VIEW}\" are the same."),
            'tip': _("Clear the target, or choose another Pog."),
           'nars': n_a_r_s['s'],
              },
          'PPw': { # Add to target Pog
            'lab': vP,
           'nars': n_a_r_s['+'],
              }
          }

    def MainFontViewUpdate(self):
        """
        Vital routine - the heart if the app.

        This decides what to do based on what has been selected.
        It draws the controls and the fonts as appropriate.
        It also sets flags in fpsys.state
        """

        ## If any DismissablePanels are open, hide them:
        ps.pub( ensure_fontview_shown )

        ## Get shorter vars to use.
        V = fpsys.state.viewobject
        T = fpsys.state.targetobject

        VC = fpsys.state.viewpattern # View Char
        TC = fpsys.state.targetpattern # Target Char

        P = VC + TC # a two-char flag

        ## Okay, let's make a key:..

        ## [S][rw][T][rws] <-- key's basic shape
        ## Where S is Source, T is Target:
        ##  E == Empty View/Source - no fonts in chosen Source.
        ##  N == Empty Target - no fonts.
        ##  P is Pog
        ##  F is Folder     
        ## And rw:
        ## r is read (i.e. only can view)
        ## w is write (i.e. remove or append)
        ## s is same (S/T pogs are the same)
        ## Example:
        ## PrN -> Source pog+read. No target pog.
        ##     i.e: We are viewing a pog that is installed
        ##     (no write.)
        ## FPw -> Source folder. Target pog+write
        ##     i.e. We are viewing a folder and have a Pog
        ##     which is *not* installed, so can be 'written'
        ##     i.e. have fonts appended.

        # EN -> EN (Empty source, No target)
        # EP -> EP (Empty source, Pog target (weird) )
        # FN -> FN (Folder source, No target)
        if P in ('EN', 'EP', 'FN'):
            key = P

        # PN -> PrN or PwN
        # Pog source, No target. 
        # Because 1) source is a Pog
        #     and 2) there's no target,
        # the Pog can be:
        #  r = view it only (i.e. it's installed)
        #  w = remove fonts
        elif P == "PN":
            key = "PrN" if V.isInstalled() else "PwN"

        # FP -> FPr or FPw
        # Folder source, Pog target. Target r or w.
        # Similar logic. If target pog is installed
        # it can't be added-to, i.e. it's 'r' only.
        # else it can be 'w'
        elif P == "FP":
            key = "FPr" if T.isInstalled() else "FPw"

        # PP -> PPr or PPw or PPs
        # Target pog is either 'r' or 'w' or ...
        # Target pog 's' means source and target are same.
        elif P == "PP":
            if fpsys.state.samepogs:
                key = "PPs"
            else:
                key = "PPr" if T.isInstalled() else "PPw"
        # Some kind of error
        else:
            print _("FontView state error: Pattern is \"{}\"").format( P )
            raise SystemExit

        ## ..and use it to fetch from dict self.lbl_d
        d = self.lbl_d[key]
        
        # Little func to replace substrings.
        def rep(s):
            if "VIEW"   in s: s = s.format(VIEW=V.label())
            if "TARGET" in s: s = s.format(TARGET=T.label())
            return s

        lab = rep(d['lab'])

        ## Do we add extra text about recursing?
        rtest = d.get('rtest',None)
        if rtest:
            lab = lab.format(RT=rtest()) # yes

        
        ## using dict n_a_r_s
        nars = d['nars']

        fpsys.state.cantick = nars['cantick']
        fpsys.state.action = nars['action']
        self.TICKMAP = nars['tmap']


        ## Enable/Disable the Purge menu item
        ## Switch it off, then: if the view is a Pog
        ## and it's *not* installed, we can switch it on.
        ## (Because you can't purge an installed font.)
        ## This has nothing to do with whatever target
        ## may be selected.
        ps.pub( toggle_purge_menu_item, False )
        if VC=="P" and not V.isInstalled():
                ps.pub( toggle_purge_menu_item, True )

        self.buttMainLastLabel = rep(nars['btext'])

        self.main_font_info_label.SetLabel( lab )
        self.main_font_info_label.Show()

        i = nars['info']
        t = d.get('tip',"")
        st = rep( u"{} {}".format(i,t) )
        self.status_text.SetLabel( st )

        self.ToggleMainButton()

        fpsys.markInactive()
        self.filterAndPageThenCallCreateFitmaps()





    def onMainClick(self, evt) :
        """
        Removes fonts, or Appends fonts. Depends on situation in fpsys.state
        """
        xPos, yPos = self.scrolledFontView.GetViewStart() #Saved by Robin Dunn, once again ! ! !
        wx.BeginBusyCursor()
        doupdate = False

        ## Let's determine what kind of thing to do:
        if fpsys.state.action == "REMOVE":
            ## We have a pog in viewobject and we must remove the selected fonts from it.
            vo = fpsys.state.viewobject
            victims = []
            dowrite = False
            for fi in vo:
                if fi.ticked:
                    victims.append(fi) #Put it into another list
                    dowrite = True
            for fi in victims:
                vo.remove(fi) #Now remove it from the vo
            del victims

            if dowrite:
                fpsys.flushTicks()
                bug = False
                try:
                    vo.write()
                except (fontybugs.PogWriteError), e:
                    bug = True
                    ps.pub( show_error, unicode( e ) )

                doupdate = True

                if not bug:
                    ps.pub(print_to_status_bar,_("Selected fonts have been removed."))
                else:
                    ps.pub(print_to_status_bar,_("There was an error writing the pog "\
                        "to disk. Nothing has been done."))

        ## APPEND - Copy font to a pog.
        if fpsys.state.action == "APPEND":
            ## We must append the fonts to the Pog
            vo = fpsys.state.viewobject
            to = fpsys.state.targetobject
            print _("Copying fonts from %(source)s to %(target)s") % {
                    "source":vo.label(), "target":to.label()}
            dowrite = False
            for fi in vo:
                if fi.ticked:
                    to.append(fi)
                    dowrite = True
            if dowrite:
                fpsys.flushTicks() #Ensure we have no more ticks after a succ xfer.
                bug = False
                try:
                    to.write()
                except (fontybugs.PogWriteError), e:
                    bug = True
                    ps.pub( show_error, unicode( e ) )

                doupdate = True

                if not bug:
                    ps.pub(print_to_status_bar,_(
                        "Selected fonts are now in %s.") % to.label())
                else:
                    ps.pub(print_to_status_bar,_(
                        "There was an error writing the pog to disk. Nothing has been done"))

        wx.EndBusyCursor()
        self.scrolledFontView.Scroll(xPos, yPos)

        if doupdate: self.MainFontViewUpdate()

    def onPagechoiceClick(self,event) :
        ##cb = event.GetEventObject()
        n = int( event.GetString() )
        wx.BeginBusyCursor()
        if self.pageindex != n: #Only redraw if actually onto another page.
            self.pageindex =  n
            self.filterAndPageThenCallCreateFitmaps()
        wx.EndBusyCursor()

    def onPagerChoiceTextEnter(self, evt):
        o=evt.GetEventObject()
        #print dir(o)
        try:
            n = int(evt.GetString())
        except:
            n = 1
        #n = n if n <= self.total_number_of_pages else self.total_number_of_pages
        n = min(n, self.total_number_of_pages)
        n = max(1,n)
        o.SetValue(str(n))
        wx.BeginBusyCursor()
        if self.pageindex != n: #Only redraw if actually onto another page.
            self.pageindex =  n
            self.filterAndPageThenCallCreateFitmaps()
        wx.EndBusyCursor()

    def xxonPagechoiceClick(self,event) :
        wx.BeginBusyCursor()
        if self.pageindex != int(event.GetString() ) : #Only redraw if actually onto another page.
            self.pageindex =  int(event.GetString() )
            self.filterAndPageThenCallCreateFitmaps()
        wx.EndBusyCursor()

    #def OnSliderScroll(self, event):
    #	"""
    #		July 2016: Tried a slider to move through pages. It sucked.
    #		This code not in use.
    #	"""
    #	obj = event.GetEventObject()
    #	val = obj.GetValue()
    #	wx.BeginBusyCursor()
    #	if self.pageindex != val: #Only redraw if actually onto another page.
    #		self.pageindex = val
    #		self.filterAndPageThenCallCreateFitmaps()
    #	wx.EndBusyCursor()


    def navClick(self,event) :
        wx.BeginBusyCursor()
        if event.GetId()  == wx.ID_FORWARD:
            self.pageindex += 1
        else: #wx.ID_BACKWARD
            self.pageindex -= 1
        if self.pageindex > self.total_number_of_pages:
            self.pageindex = self.total_number_of_pages
        if self.pageindex == 0:
            self.pageindex = 1

        self.button_main.SetFocus()  #a GTK bug demands this move.
        self.filterAndPageThenCallCreateFitmaps()
        wx.EndBusyCursor()

    def OnLeftOrRightKey(self, evt):
        ## This comes along from MainFrame via the AcceleratorTable events.
        evt=evt[0] # just get around pubsub tuple.
        id=evt.GetId()
        ## We can't just pass on to navClick yet because we don't know if
        ## the button (left/right) is enabled or not. So determine that and then
        ## pass on to the other handler.
        if id==wx.ID_FORWARD: #right arrow was pressed
            if self.next_button.IsEnabled():
                self.navClick( evt )
        else:
            if self.previous_button.IsEnabled():
                self.navClick( evt )
        #evt.Skip() # If this is here, the keyboard shortcuts get really buggy....

    def EnableDisablePrevNext(self) :
        """
        Enabled state of PREV/NEXT buttons
        """
        n = True
        p = True
        if self.pageindex == self.total_number_of_pages:
            n = False
        if self.pageindex == 1:
            p = False
        self.next_button.Enable(n)
        self.previous_button.Enable(p)

    def ToggleMainButton(self):

        # both on, then off .. if
        ps.pub( toggle_selection_menu_item, True )
        self.button_main.Enable( True )

        self.button_main.SetLabel( self.buttMainLastLabel )
        #print "In ToggleMainButton, testing action:", fpsys.state.action
        if fpsys.state.action == "NOTHING_TO_DO":
            self.button_main.Enable( False )
            ps.pub( toggle_selection_menu_item, False )
            return

        if fpsys.state.numticks == 0:
            self.button_main.Enable( False )
            #self.button_main.SetLabel( _("Choose some fonts") )

    def ResetToPageOne(self):
        self.pageindex = 1 # I start here


