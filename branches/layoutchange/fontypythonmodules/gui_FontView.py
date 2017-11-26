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
    max_searches = 5
    def __init__(self, parent, id=-1, value="",
                 pos=wx.DefaultPosition, size=wx.DefaultSize, style=0,
                 search_func = None, 
                 cancel_func = None):

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
        self.SetValue(t)
        self.add_to_history()

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
        icon_open_folder = fpwx.wxbmp("icon_open_folder")
        icon_pog = fpwx.wxbmp("pog16x16")
        icon_pog_installed = fpwx.wxbmp("pog16x16.installed")

        ## Sizer: to hold all the others
        main_view_sizer = wx.BoxSizer( wx.VERTICAL )

        ## Sizer: Icon and Main Label
        icon_and_text_sizer = wx.BoxSizer(wx.HORIZONTAL)

        ## Sizer: Filter and Pager controls
        filter_clear_pager_sizer = wx.BoxSizer(wx.HORIZONTAL)


        ## Icon, Main Font Info label
        view_icon = fpwx.icon(self, 'icon_viewing')
        self.main_font_info_label = fpwx.h1(self, u"..")
        icon_and_text_sizer.Add(view_icon, 0, wx.TOP | wx.BOTTOM | wx.LEFT, border = 4)
        icon_and_text_sizer.Add(self.main_font_info_label, 1, wx.LEFT | wx.BOTTOM | wx.ALIGN_BOTTOM, border = 4)

        ## The SubInfo label
        self.status_text = fpwx.label(self, u"Subinfo" )


        ## The clear filter button: added 10 Jan 2008
        #clear_button = wx.BitmapButton(self, -1, fpwx.wxbmp( "clear" ), style = wx.NO_BORDER)
        #clear_button.SetToolTipString( _("Clear filter") )
        #clear_button.Bind( wx.EVT_BUTTON, self.on_clear_button_click )

        ## The filter text box
        filter_label = fpwx.label(self, _(u"Filter:"))

        # July 5th, 2016: Had to add "|wx.TE_PROCESS_ENTER" to get the input filter's
        # EVT_TEXT_ENTER event to work. Go figure.
        #self.search_filter = wx.ComboBox(self, -1, value="",
        #        choices=[],style=wx.CB_DROPDOWN|wx.TE_PROCESS_ENTER )
        self.search_filter = SearchFilter(self,
                search_func = self.do_search,
                cancel_func = self.on_clear_button_click)
        #self.Bind(wx.EVT_COMBOBOX, self.EvtComboBox, self.search_filter)
        #self.Bind(wx.EVT_TEXT_ENTER, self.EvtTextEnter, self.search_filter)

        self.last_filter_string = ""

        ## The pager pulldown
        pager_label = fpwx.label(self, _(u"Page:"))
        self.pager_combo = wx.ComboBox(self, -1, value="1", choices=["busy"],
                style=wx.CB_DROPDOWN|wx.TE_PROCESS_ENTER )
        self.pager_combo.Bind(wx.EVT_COMBOBOX, self.onPagechoiceClick )
        self.pager_combo.Bind(wx.EVT_TEXT_ENTER, self.onPagerChoiceTextEnter )

        #self.SA=SearchAssistant(self)


        ## Fill the filter_clear_pager_sizer
        filter_clear_pager_sizer.Add(filter_label, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)

        ## Quick search Bold Italic Regular buttons
        ## It occurs to me that these are English words...
        ## Do fonts contain i18n on styles?
        ## See: https://fontforge.github.io/fontstyles.html
        idBold = wx.NewId()
        idItalic = wx.NewId()
        self.idRegular = wx.NewId()
        self.BIR = {
           idBold  : {'style': "bold",   'label': _("b"), 'truth': False, 'instance': None},
           idItalic: {'style': "italic", 'label': _("i"), 'truth': False, 'instance': None},
     self.idRegular: {'style': "regular",'label': _("r"), 'truth': False, 'instance': None}
           }
        for id, dic in self.BIR.iteritems():
            bBIR = wx.ToggleButton( self, id=id, label=dic['label'])
            self.BIR[id]['instance'] =  bBIR
            filter_clear_pager_sizer.Add( bBIR, 0, wx.EXPAND )
            bBIR.Bind( wx.EVT_TOGGLEBUTTON, self.onBIR )


        #filter_clear_pager_sizer.Add( clear_button, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.BU_EXACTFIT ) # Clear button
        #filter_clear_pager_sizer.Add( clear_button, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL ) # Clear button

        filter_clear_pager_sizer.Add( self.search_filter, 1, wx.ALIGN_LEFT | wx.EXPAND )

        filter_clear_pager_sizer.Add( pager_label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL  )
        filter_clear_pager_sizer.Add( self.pager_combo, 1 )#, wx.ALIGN_RIGHT )

        ## The SCROLLED FONT VIEW panel:
        self.scrolledFontView = ScrolledFontView(self)

        ## Sizer: for buttons prev, main, next
        bottom_buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)

        #July 2016
        #=========
        #The stock icon on the button was not showing under gtk3.
        #I have switched to a bitmapbutton. I hope this works...
        #self.previous_button = wx.Button(self, wx.ID_BACKWARD) # Also not in Afrikaans.
        self.previous_button = wx.BitmapButton( self, wx.ID_BACKWARD, 
                wx.ArtProvider.GetBitmap( wx.ART_GO_BACK, wx.ART_BUTTON, (32,32) ))

        self.button_main = wx.Button(self, label=" ")
        self.buttMainLastLabel=" "

        ## This stock button has not been translated into Afrikaans yet. (Dec 2007)
        ## I can't tell you how this fkuced me around!
        # July 2016 - remarked : self.next_button = wx.Button(self, wx.ID_FORWARD)  
        self.next_button = wx.BitmapButton( self, wx.ID_FORWARD, wx.ArtProvider.GetBitmap( wx.ART_GO_FORWARD, wx.ART_BUTTON, (32,32) ))
        self.previous_button.Enable(False)  #Starts out disabled


        bottom_buttons_sizer.Add( self.previous_button, 0, wx.EXPAND)
        bottom_buttons_sizer.Add( (10,1), 0, wx.EXPAND)
        
        #info_and_main_sizer = wx.BoxSizer(wx.VERTICAL)
        #info_and_main_sizer.Add( self.status_text, 0)#1, wx.EXPAND)#, border = 12)
        #info_and_main_sizer.Add( self.button_main, 1, wx.EXPAND)
        #bottom_buttons_sizer.Add( info_and_main_sizer, 1, wx.EXPAND )
        bottom_buttons_sizer.Add( self.button_main, 1, wx.EXPAND )

        bottom_buttons_sizer.Add( (10,1), 0, wx.EXPAND)
        bottom_buttons_sizer.Add( self.next_button, 0, wx.EXPAND)


        ## Start at the top: the icon and label
        main_view_sizer.Add(icon_and_text_sizer, 0, wx.EXPAND )

        ## Sub label
        main_view_sizer.Add(self.status_text,0)

        ## Fill the Choice and Filter
        main_view_sizer.Add(filter_clear_pager_sizer, 1, wx.EXPAND | wx.TOP, border = 12)

        ## Fill the SIZER FOR THE SCROLLED FONT VIEW
        main_view_sizer.Add(self.scrolledFontView, 20, wx.EXPAND )



        ## The Search Assistant
        #main_view_sizer.Add( self.SA, 0, wx.EXPAND)


        ## Fill the SubInfo label
        #main_view_sizer.Add(self.status_text, 0, wx.ALIGN_CENTER | wx.ALL, border = 3 )
        #info_and_main_sizer = wx.BoxSizer(wx.VERTICAL)
        #info_and_main_sizer.Add( self.status_text, 1, wx.TOP, border = 12)

        #main_view_sizer.Add(self.status_text, 0, wx.ALIGN_LEFT | wx.ALL, border = 3 )
        #main_view_sizer.Add(si_sizer, 0, wx.BOTTOM, border = 10 )
        ## Fill the bottom buttons   
        main_view_sizer.Add(bottom_buttons_sizer, 2, wx.EXPAND | wx.TOP, border = 10)

        ## Do the voodoo thang
        self.SetSizer(main_view_sizer)
        self.Fit()

        ## Bind events
        e = wx.EVT_BUTTON #was wx.EVT_LEFT_UP
        self.previous_button.Bind(e,self.navClick)
        self.next_button.Bind(e,self.navClick)
        #self.button_main.Bind(e,self.onMainClick) 
        self.Bind(e, self.onMainClick, self.button_main)#.GetId() ) 

        ## Advertise some local functions:
        ps.sub( left_or_right_key_pressed, self.OnLeftOrRightKey ) ##DND: class FontViewPanel

        ps.sub( toggle_main_button, self.ToggleMainButton ) ##DND: class FontViewPanel
        ps.sub( update_font_view, self.MainFontViewUpdate ) ##DND: class FontViewPanel
        ps.sub( reset_to_page_one, self.ResetToPageOne ) ##DND: class FontViewPanel 



    def on_clear_button_click( self):#, event ):
        #self.search_filter.SetValue("") #was .Clear(), but that does not work for a combo box.
        self.filter = ""

        # Clear the BIR toggle buttons
        self.setAllBIRFalse()

        ## Now command a change of the view.
        ## First, return user to page 1:
        self.pageindex = 1
        self.filterAndPageThenCallCreateFitmaps()
        self.button_main.SetFocus()  #a GTK bug demands this move. Restore the ESC key func.

    def setOneBIR( self, id, truth ):
        self.BIR[id]['truth'] = truth
        self.BIR[id]['instance'].SetValue( truth )

    def setAllBIRFalse( self ):
        for id in self.BIR.keys():
            self.setOneBIR( id, False )

    def onBIR( self, e ):
        id=e.GetId()
        self.BIR[id]['truth']=self.BIR[id]['instance'].GetValue()
        if self.BIR[id]['style'] == "regular":
            # can't have regular with bold/italic
            self.setAllBIRFalse() # switch all off
            self.setOneBIR( id, True )
            ss = "regular|normal"
        else:
            self.setOneBIR( self.idRegular, False )
            ss=""
            for id, dic in self.BIR.iteritems():
                if dic['truth']: ss += "%s%s" % (dic['style']," ") # Builds AND regex (space is and)
            ss = ss[:-1]
        print ss

        #self.search_filter.SetValue( ss )
        self.search_filter.set_BIR(ss)#add_to_history( ss )
        self.startSearch( ss )

    # Capture events when the user types something into the control then
    # hits ENTER.
    #def EvtTextEnter(self, evt):
    #    o=evt.GetEventObject()
    #    #print dir(o)
    #    termsstring = evt.GetString()
    #    history=o.GetItems()
    #    if termsstring not in history:
    #        o.Insert( termsstring,0 ) #record this search in the top of the 'history'
    #    #print termsstring
    #    self.startSearch(termsstring)
    #
    #   self.button_main.SetFocus()
    #    evt.Skip()

    # When the user selects something in the combo pull-down area, we go here.
    #def EvtComboBox(self, evt):
    #    cb = evt.GetEventObject()
    #    termsstring = evt.GetString()
    #    self.startSearch(termsstring)
    #    self.button_main.SetFocus()

    
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
        E
        EN
        lab = _("There are no fonts in here.")
        status = _("Choose a Source Pog or folder.")
        btext = _("Nothing to do")
        fpsys.state.action = "NOTHING_TO_DO"
        fpsys.state.cantick = False
        self.TICKMAP = None

        EP
        lab = _("Source is empty. Active Target is \"{}\"").format( T.name )
        status = _("Please choose a Source.")
        btext = _("Nothing to do")
        fpsys.state.action = "NOTHING_TO_DO"
        fpsys.state.cantick = False
        self.TICKMAP = None

        FN
        lab = _("Viewing Folder \"{}\"").format( V.label() )
        if fpsys.config.recurseFolders: lab = "{} and all sub-folders".format(lab)
        status = ""
        btext = _("Nothing to do")
        fpsys.state.action = "NOTHING_TO_DO"
        fpsys.state.cantick = False
        self.TICKMAP = None

        PrN
        lab = _("Viewing (installed Pog) \"{}\"").format( V.name )
        status = _("You can't change an installed Pog.")
        btext = _("Nothing to do")
        fpsys.state.action = "NOTHING_TO_DO"
        fpsys.state.cantick = False
        self.TICKMAP = None

        PwN
        lab = _("Viewing (editable Pog) \"{}\"").format( V.name )
        status = _("You can remove fonts from the selected Target Pog.")
        btext = _("Remove fonts from %s") % V.name
        fpsys.state.action = "REMOVE" # We will test this in mainframe::OnMainClick
        fpsys.state.cantick = True
        self.TICKMAP = self._CROSS

        FPr
        lab = _("Viewing Folder \"{}\"").format( V.label() )
        if fpsys.config.recurseFolders: lab = "{} and all sub-folders".format(lab)
        status = _("Pog \"{}\" is installed. It cannot be changed.").format(T.name)
        btext = _("Nothing to do")
        fpsys.state.action = "NOTHING_TO_DO"
        fpsys.state.cantick = False
        self.TICKMAP = None

        FPw
        #lab = _("Append from \"{source}\" to \"{target}\"").format(source=V.label(), target=T.name )
        lab = _("Viewing Folder \"{}\"").format( V.label() )
        status = _("You can append fonts to \"{}\".").format(T.name)
        btext = _("Put fonts into %s") % T.name
        fpsys.state.action = "APPEND" # We will test this in mainframe::OnMainClick
        fpsys.state.cantick = True
        self.TICKMAP = self._TICK

        PPr
        lab = _("Viewing Pog \"{}\"").format( V.name)
        status = _("Pog \"{}\" is installed. It cannot be changed.").format(T.name)
        btext = _("Nothing to do")
        fpsys.state.action = "NOTHING_TO_DO"
        fpsys.state.cantick = False
        self.TICKMAP = None

        PPs
        if fpsys.state.samepogs:
        lab = _(u"Source and Target \"{}\" are the same.").format(V.name)
        btext = _("Nothing to do")
        fpsys.state.action = "NOTHING_TO_DO"
        fpsys.state.cantick = True (?)
        self.TICKMAP = None

        PP+w
        if not fpsys.state.samepogs:
        lab = _("Viewing Pog \"{}\"").format( V.name)
        status = _("You can append fonts to \"{}\".").format(T.name)
        btext = _("Put fonts into %s") % T.name
        fpsys.state.action = "APPEND" # We will test this in mainframe::OnMainClick
        fpsys.state.cantick = True
        self.TICKMAP = self._TICK

        These dicts are used in MainFontViewUpdate.
        """

        #nothing add remove samepogs dict
        self.n_a_r_s = { 'n' : {
            'btext': _("Nothing to do"),
           'action': "NOTHING_TO_DO",
        'txtaction': _("There's nothing much to do."),
          'cantick': False,
             'tmap':self._TICK #default, but is not drawn. 
             },
         '-' : {
            'btext': _("Remove fonts from {VIEW}"),
        'txtaction': _("You can remove fonts from the selected Target Pog."),
           'action': "REMOVE",
          'cantick': True,
             'tmap': self._CROSS
             },
         '+' : {
            'btext': _("Put fonts into {TARGET}"),
        'txtaction': _("You can append fonts to \"{TARGET}\"."),
           'action': "APPEND",
          'cantick': True,
             'tmap': self._TICK
            }}
        ## Samepogs, key 's', same as key 'n'
        self.n_a_r_s.update( {'s' : self.n_a_r_s['n']} )

        recurse_test = lambda: _(" (and all sub-folders.)") \
                               if fpsys.config.recurseFolders else ""

        vF = _("Viewing Folder \"{VIEW}\"{{RT}}")
        vP  =_("Viewing Pog \"{VIEW}\"")
        choose_source = _("Choose a Source Pog or folder.")

        self.lbl_d = { 
          'EN' : {
            'lab': _("There are no fonts in here."),
           'info': choose_source,
            'act': 'n'
               },
          'EP' : {
            'lab': _("Source is empty. Active Target is \"{TARGET}\""),
           'info': choose_source,
            'act': 'n'
               },
          'FN' : {
            'lab': vF,
           'info': self.n_a_r_s['n']['txtaction'],
            'act': 'n',
          'rtest': recurse_test
               },
          'PrN' : {
            'lab': _("Viewing (installed Pog) \"{VIEW}\""),
           'info': _("You can't change an installed Pog."),
            'act': 'n'
               },
          'PwN': {
            'lab': _("Viewing (editable Pog) \"{VIEW}\""),
            'info': self.n_a_r_s['-']['txtaction'],
            'act': '-'
               },
          'FPr': {
            'lab': vF,
           'info': _("You can't change an installed Pog."),
            'act': 'n',
          'rtest': recurse_test,
               },
          'FPw': {
            'lab': vF,
           'info': self.n_a_r_s['+']['txtaction'],
            'act': '+',
          'rtest': recurse_test,
              },
          'PPr': {
            'lab': vP,
           'info': _("Pog \"{TARGET}\" is installed. It cannot be changed."),
            'act': 'n'
              },
          'PPs': {
            'lab':  _("Source and Target \"{VIEW}\" are the same."),
           'info': _("Clear the target, or choose another Pog."),
            'act': 's'
              },
          'PPw': {
            'lab': vP,
           'info': self.n_a_r_s['+']['txtaction'],
            'act': '+'
              }
          }

    def xxMainFontViewUpdate(self):
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

        P = VC + TC

        ## [S][rw][T][rws] <-- basic shape
        ## Where S is Source, T is Target:
        ##  E == Empty View/Source - no fonts in chosen Source.
        ##  N == Empty Target - no fonts.
        ##  P is Pog
        ##  F is Folder     
        ## And rw:
        ## r is read (i.e. view)
        ## w is write (i.e. remove or append)
        ## s is same (S/T pogs are the same)

        ## Example:
        ## PrN -> Source pog+read. No target pog.
        #  i.e: We are viewing a pog that is installed (no write)
        ## FPw -> Source folder. Target pog+write
        ## i.e. We are viewing a folder and have a Pog which
        ##      is not installed and so can be written-to.

        #EN -> EN
        #EP -> EP
        #FN -> FN
        if P in ('EN', 'EP', 'FN'):
            key = P
        #PN -> PrN or PwN
        elif P == "PN":
            key = "PrN" if V.isInstalled() else "PwN"
        #FP -> FPr or FPw
        elif P == "FP":
            key = "FPr" if T.isInstalled() else "FPw"
        #PP -> PPr or PPw or PPs
        elif P == "PP":
            if fpsys.state.samepogs:
                key = "PPs"
            else:
                key = "PPr" if T.isInstalled() else "PPw"
        else:
            print _("FontView state error: Pattern is \"{}\"").format( P )
            raise SystemExit

        ## use dict 1
        d = self.lbl_d[key]
        
        lab = d['lab']
        if "VIEW" in lab: lab = lab.format(VIEW=V.label())
        if "TARGET" in lab: lab = lab.format(TARGET=T.label())

        ## Do we add extra text about recursing?
        rtest = d.get('rtest',None)
        if rtest:
            lab = lab.format(RT=rtest()) # yes

        info = d.get('info',"")
        if "TARGET" in info: info = info.format(TARGET=T.label())
        print info

        action = d.get('act','n')
        status = d['info']
        
        ## use dict 2
        nars = self.n_a_r_s[action]
        btext = nars['btext']
        if "VIEW" in btext: btext = btext.format(VIEW=V.label())
        if "TARGET" in btext: btext = btext.format(TARGET=T.label())


        fpsys.state.cantick = nars['cantick']
        print "cantick:", nars['cantick']
        fpsys.state.action = nars['action']
        print "action:", nars['action']
        self.TICKMAP = nars['tmap']


        ## Enable/Disable the Purge menu item
        ## Switch it off, then: if the view is a Pog
        ## and it's *not* installed, we can switch it on.
        ps.pub( toggle_purge_menu_item, False )
        if VC=="P":
            if not fpsys.state.viewobject.isInstalled():
                ps.pub( toggle_purge_menu_item, True )

        self.buttMainLastLabel = btext
        self.main_font_info_label.SetLabel( lab )
        self.main_font_info_label.Show()

        self.status_text.SetLabel( info )

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
                    ps.pub(print_to_status_bar,_("There was an error writing the pog to disk. Nothing has been done."))

        ## APPEND - Copy font to a pog.
        if fpsys.state.action == "APPEND":
            ## We must append the fonts to the Pog
            vo = fpsys.state.viewobject
            to = fpsys.state.targetobject
            print _("Copying fonts from %(source)s to %(target)s") % {"source":vo.label(), "target":to.label()}
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
                    ps.pub(print_to_status_bar,_("Selected fonts are now in %s.") % to.label())
                else:
                    ps.pub(print_to_status_bar,_("There was an error writing the pog to disk. Nothing has been done"))

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
        ps.pub( toggle_selection_menu_item, True )
        self.button_main.SetLabel( self.buttMainLastLabel )
        if fpsys.state.action == "NOTHING_TO_DO":
            self.button_main.Enable( False )
            ps.pub( toggle_selection_menu_item, False )
            return

        if fpsys.state.numticks > 0:
            self.button_main.Enable(True)
        else:
            self.button_main.SetLabel( _("Choose some fonts") )

    def ResetToPageOne(self):
        self.pageindex = 1 # I start here
















    def MainFontViewUpdate(self):
        """
        Vital routine - the heart if the app.

        This decides what to do based on what has been selected.
        It draws the controls and the fonts as appropriate.
        It also sets flags in fpsys.state
        """

        ## If the help panel is open, hide it:
        ps.pub( ensure_fontview_shown )

        ## Get shorter vars to use.
        V = fpsys.state.viewobject
        T = fpsys.state.targetobject

        Vpatt = fpsys.state.viewpattern # View Pattern
        Tpatt = fpsys.state.targetpattern # Target pattern

        Patt = Vpatt + Tpatt

        lab = ""
        status = ""

        ## June 2009: A default value for this:
        self.TICKMAP = self._TICK

        ## E == Empty View - no fonts in chosen Source.
        ## N == Empty Target - no fonts.
        ## P is Pog
        ## F is Folder

        if Vpatt == "E": #NOTE : TESTING VPATT, not PATT - ergo: this covers E, EN, EP
            ## Empty ("E") - when the chosen Folder or Pog has NO FONTS IN IT.
            if Tpatt == "P":
                lab = _("Source is empty. Active Target is \"{}\"").format( T.name )
                status = _("Please choose a Source.")
            else:
                lab = _("There are no fonts in here.")
                status = _("Choose a Source Pog or folder.")
            btext = _("Nothing to do")
            fpsys.state.cantick = False
            fpsys.state.action = "NOTHING_TO_DO" # We will test this in mainframe::OnMainClick

        elif Patt == "FN":
            #View a Folder, no target
            lab = _("Viewing Folder \"{}\"").format( V.label() )
            if fpsys.config.recurseFolders: lab = "{} and all sub-folders".format(lab)
            fpsys.state.cantick = False
            btext = _("Nothing to do")
            fpsys.state.action = "NOTHING_TO_DO" # We will test this in mainframe::OnMainClick
            status = ""#_("Viewing a folder.")

        elif Patt == "PN": #A single Pog in the VIEW
            #View a pog, no target
            if V.isInstalled():
                ## Cannot remove fonts from an installed pog
                lab = _("Viewing (installed Pog) \"{}\"").format( V.name )
                btext = _("Nothing to do")
                fpsys.state.action = "NOTHING_TO_DO"
                fpsys.state.cantick = False
                status = _("You can't change an installed Pog.")
            else:
                lab = _("Viewing (editable Pog) \"{}\"").format( V.name )
                fpsys.state.cantick = True
                btext = _("Remove fonts from %s") % V.name
                self.TICKMAP = self._CROSS
                fpsys.state.action = "REMOVE" # We will test this in mainframe::OnMainClick
                status = _("You can remove fonts from the selected Target Pog.")

        elif Patt == "FP":
            #Folder to Pog
            if T.isInstalled():
                ## We cannot put stuff into an installed pog
                lab = _("Viewing Folder \"{}\"").format( V.label() )
                if fpsys.config.recurseFolders: lab = "{} and all sub-folders".format(lab)
                print fpsys.config.recurseFolders
                btext = _("Nothing to do")
                fpsys.state.action = "NOTHING_TO_DO"
                fpsys.state.cantick = False
                #status = _("You can't change an installed Pog.")
                status = _("Pog \"{}\" is installed. It cannot be changed.").format(T.name)
            else:
                #lab = _("Append from \"{source}\" to \"{target}\"").format(source=V.label(), target=T.name )
                lab = _("Viewing Folder \"{}\"").format( V.label() )
                btext = _("Put fonts into %s") % T.name
                self.TICKMAP = self._TICK
                fpsys.state.cantick = True
                fpsys.state.action = "APPEND" # We will test this in mainframe::OnMainClick
                #status = _("You can append fonts to your target Pog.")
                status = _("You can append fonts to \"{}\".").format(T.name)

        elif Patt == "PP":
            #Pog to Pog
            if T.isInstalled():
                ## We cannot put fonts into an installed pog
                #lab = _("Viewing \"{source}\", but Pog \"{target}\" is installed.").format(
                #        source = V.name, target = T.name )
                lab = _("Viewing Pog \"{}\"").format( V.name)
                btext = _("Nothing to do")
                fpsys.state.action = "NOTHING_TO_DO"
                fpsys.state.cantick = False
                status = _("Pog \"{}\" is installed. It cannot be changed.").format(T.name)
                #status = _("You cannot change an installed Pog.")
            else: #Not installed.
                if fpsys.state.samepogs: #Are the two pogs the same?
                    ## The validate routines determined the samepogs value.
                    lab = _(u"Source and Target \"{}\" are the same.").format(V.name)
                    fpsys.state.cantick = True
                    btext = _("Nothing to do")
                    fpsys.state.action = "NOTHING_TO_DO"
                    status = ""#_("Your Source and Target are the same Pog.")
                else: # Normal pog to pog
                    #lab = _("Append from \"{source}\" into \"{target}\"").format(
                    #        source = V.name, target = T.name )
                    lab = _("Viewing Pog \"{}\"").format( V.name)
                    btext = _("Put fonts into %s") % T.name
                    self.TICKMAP = self._TICK
                    fpsys.state.cantick = True
                    fpsys.state.action = "APPEND" # We will test this in mainframe::OnMainClick
                    status = _("You can append fonts to \"{}\".").format(T.name)

        else:
            print "MOJO ERROR: %s and trouble" % Patt
            raise SystemExit

        ## Enable/Disable the Purge menu item
        ps.pub( toggle_purge_menu_item, False )
        if Vpatt=="P":
            if not fpsys.state.viewobject.isInstalled():
                ps.pub( toggle_purge_menu_item, True )

        self.buttMainLastLabel = btext
        self.main_font_info_label.SetLabel( lab )
        self.main_font_info_label.Show()

        #if True:#status is not "":
        self.status_text.SetLabel( status )
            #ps.pub(print_to_status_bar, status)

        self.ToggleMainButton()

        fpsys.markInactive()
        self.filterAndPageThenCallCreateFitmaps()
