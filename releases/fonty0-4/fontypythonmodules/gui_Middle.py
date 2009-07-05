##	Fonty Python Copyright (C) 2006, 2007, 2008, 2009 Donn.C.Ingle
##	Contact: donn.ingle@gmail.com - I hope this email lasts.
##
##	This file is part of Fonty Python.
##	Fonty Python is free software: you can redistribute it and/or modify
##	it under the terms of the GNU General Public License as published by
##	the Free Software Foundation, either version 3 of the License, or
##	(at your option) any later version.
##
##	Fonty Python is distributed in the hope that it will be useful,
##	but WITHOUT ANY WARRANTY; without even the implied warranty of
##	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##	GNU General Public License for more details.
##
##	You should have received a copy of the GNU General Public License
##	along with Fonty Python.  If not, see <http://www.gnu.org/licenses/>.

import wx

## Setup wxPython to access translations : enables the stock buttons.
langid = wx.LANGUAGE_DEFAULT # Picks this up from $LANG
mylocale = wx.Locale( langid )


from pubsub import *
from wxgui import ps

from gui_ScrolledFontView import *

import fontybugs
import fpsys # Global objects
import fontyfilter

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

class FontViewPanel(wx.Panel):
	"""
	Standalone visual control to select TTF fonts.
	The Panel that holds the ScrolledFontView control
	as well as the buttons etc. below and the text above.
	"""
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, id = -1)
		
		self.pageindex = 1 # I start here
		self.total_number_of_pages = 0
		
		self.filter = ""
		
		self.TICKMAP = None
		self.TICK = wx.Bitmap(fpsys.mythingsdir + "tick.png", type=wx.BITMAP_TYPE_PNG)
		self.CROSS = wx.Bitmap(fpsys.mythingsdir + "cross.png", type=wx.BITMAP_TYPE_PNG)
		
		## Main Label on top
		sizerMainLabel = wx.BoxSizer(wx.HORIZONTAL) 
		self.textMainInfo = wx.StaticText(self, -1, " ") 
		self.textMainInfo.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD))
		sizerMainLabel.Add(self.textMainInfo,1,wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT) 
		
		## Page choice and Filter controls
		sizerOtherControls = wx.BoxSizer(wx.HORIZONTAL)

		## The clear filter button: added 10 Jan 2008
		bmp = wx.Bitmap(fpsys.mythingsdir + "clear.png", type=wx.BITMAP_TYPE_PNG)
		self.clearButton = wx.BitmapButton(self, -1, bmp, style = wx.NO_BORDER)
		self.clearButton.SetToolTipString( _("Clear filter") )
		self.clearButton.Bind( wx.EVT_BUTTON, self.OnClearClick )
		
		## The filter text box
		self.textFilter = wx.StaticText(self, -1, _("Filter:"))
		self.inputFilter = wx.ComboBox(self, 500, value="", choices=[],style=wx.CB_DROPDOWN )
		self.Bind(wx.EVT_COMBOBOX, self.EvtComboBox, self.inputFilter)
		self.Bind(wx.EVT_TEXT_ENTER, self.EvtTextEnter, self.inputFilter)

		self.last_filter_string = ""
		
		## The pager pulldown
		self.choicePage = wx.Choice(self, -1, choices = ["busy"]) 
		self.choicePage.Bind(wx.EVT_CHOICE, self.onPagechoiceClick) #Bind choice event

		#self.SA=SearchAssistant(self)

		## put them into the sizer
		sizerOtherControls.Add(self.textFilter, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
		sizerOtherControls.Add( self.clearButton, 0, wx.ALIGN_LEFT| wx.ALIGN_CENTER_VERTICAL ) # Clear button
		sizerOtherControls.Add(self.inputFilter, 1, wx.ALIGN_LEFT | wx.EXPAND)
		sizerOtherControls.Add(( 4,-1), 0, wx.EXPAND)
		sizerOtherControls.Add(( 4,-1), 0, wx.EXPAND)
		sizerOtherControls.Add(self.choicePage, 0 ,wx.EXPAND | wx.ALIGN_RIGHT)  #Added it to the sizer
		
		## The FONT panel:
		self.scrolledFontView = ScrolledFontView(self) 
		
		buttonsSizer = wx.BoxSizer(wx.HORIZONTAL) 
		self.buttPrev = wx.Button(self, wx.ID_BACKWARD) # Also not in Afrikaans.

		self.buttMain = wx.Button(self, label=" ")#, id = 3) 
		self.buttMainLastLabel=" "
		## This stock button has not been translated into Afrikaans yet. (Dec 2007)
		## I can't tell you how this fkuced me around!
		self.buttNext = wx.Button(self, wx.ID_FORWARD)  
		self.buttPrev.Enable(False)  #Starts out disabled
		
		buttonsSizer.Add(self.buttPrev,0,wx.EXPAND) 
		buttonsSizer.Add((10,1) ,0,wx.EXPAND) 
		buttonsSizer.Add(self.buttMain,1,wx.EXPAND) 
		buttonsSizer.Add((10,1) ,0,wx.EXPAND) 
		buttonsSizer.Add(self.buttNext,0,wx.EXPAND) 

		## Now the sizer to hold all the fontview controls
		self.sizerFontView = wx.BoxSizer( wx.VERTICAL )
		## The Main label
		self.sizerFontView.Add(sizerMainLabel, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, border = 5 )
		## The font view
		self.sizerFontView.Add(self.scrolledFontView, 1, wx.EXPAND )

		## The Search Assistant
		#self.sizerFontView.Add( self.SA, 0, wx.EXPAND)

		## Choice and Filter
		self.sizerFontView.Add(sizerOtherControls, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, border = 3)
		## The buttons   
		self.sizerFontView.Add(buttonsSizer,0,wx.EXPAND)	
		
		self.SetSizer(self.sizerFontView)
	
		e = wx.EVT_BUTTON #was wx.EVT_LEFT_UP
		self.buttPrev.Bind(e,self.navClick) 
		self.buttNext.Bind(e,self.navClick) 
		#self.buttMain.Bind(e,self.onMainClick) 
		self.Bind(e,self.onMainClick,self.buttMain)#.GetId() ) 

		## Advertise some local functions:
		ps.sub( left_or_right_key_pressed, self.OnLeftOrRightKey ) ##DND: class FontViewPanel
		ps.sub( toggle_main_button, self.ToggleMainButton ) ##DND: class FontViewPanel
		ps.sub( update_font_view, self.MainFontViewUpdate ) ##DND: class FontViewPanel
		ps.sub( reset_to_page_one, self.ResetToPageOne ) ##DND: class FontViewPanel 

	def OnClearClick( self, event ):
		self.inputFilter.SetValue("") #was .Clear(), but that does not work for a combo box.
		self.filter = ""
		## Now command a change of the view.
		## First, return user to page 1:
		self.pageindex = 1
		self.filterAndPageThenCallCreateFitmaps()
		self.buttMain.SetFocus()  #a GTK bug demands this move. Restore the ESC key func.

	# Capture events when the user types something into the control then
	# hits ENTER.
	def EvtTextEnter(self, evt):
		o=evt.GetEventObject()
		termsstring = evt.GetString()
		history=o.GetItems()
		if termsstring not in history:
			o.Insert( termsstring,0 ) #record this search in the top of the 'history'
		
		self.startSearch(termsstring)
		
		self.buttMain.SetFocus()
		evt.Skip()
	# When the user selects something in the combo pull-down area, we go here.
	def EvtComboBox(self, evt):
		cb = evt.GetEventObject()
		termsstring = evt.GetString()

		self.startSearch(termsstring)
		
		self.buttMain.SetFocus()

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
			#print "total_num_fonts=", total_num_fonts
####		gross = total_num_fonts / float(num_in_one_page)
####		
####		if gross <= 1:
####			## There are less than num_in_one_page fonts to be viewed at all.
####			self.total_number_of_pages = 1
####		else:
####			## Okay, we have at least 1 page, perhaps more.
####			whole_number_of_pages = int(gross)
####			remainder = whole_number_of_pages % num_in_one_page
####			if remainder > 0: whole_number_of_pages += 1
####			self.total_number_of_pages = whole_number_of_pages

			start = current_page * num_in_one_page #leaf thru the pages to the one we are on now.
			fin = start + num_in_one_page
			if fin > len(fpsys.state.filteredViewObject): fin = len(fpsys.state.filteredViewObject) #Make sure we don't overshoot.
			
			## Extract a single page of fonts to display
			sublist = fpsys.state.filteredViewObject[start:fin] 
			
			## Empty the choice control.
			self.choicePage.Clear() 
			## Now refill it
			[self.choicePage.Append(str(n)) for n in xrange(1, self.total_number_of_pages +1)] 
			self.choicePage.SetSelection(self.pageindex-1)
		## The viewobject is empty anyway.
		else: 
			sublist = []

		if self.total_number_of_pages == 1: 
			self.choicePage.Enable(False) #I tried to hide/show the choice, but it would not redraw properly.
		else:
			self.choicePage.Enable(True)
			
		self.scrolledFontView.CreateFitmaps( sublist ) # Tell my child to draw the fonts
		self.EnableDisablePrevNext()


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
					ps.pub(print_to_status_bar,_("There was an error writing the pog to disk. Nothing has been done"))
		
		## APPEND - Copy ttf to a pog.
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
		wx.BeginBusyCursor()
		if self.pageindex != int(event.GetString() ) : #Only redraw if actually onto another page.
			self.pageindex =  int(event.GetString() ) 
			self.filterAndPageThenCallCreateFitmaps() 
		wx.EndBusyCursor()
		
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
		 
		self.buttMain.SetFocus()  #a GTK bug demands this move.
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
			if self.buttNext.IsEnabled():
				self.navClick( evt )
		else:
			if self.buttPrev.IsEnabled():
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
		self.buttNext.Enable(n)		 
		self.buttPrev.Enable(p) 
		
	def ToggleMainButton(self):
		ps.pub( toggle_selection_menu_item, True )
		self.buttMain.SetLabel( self.buttMainLastLabel )
		if fpsys.state.action == "NOTHING_TO_DO":
			self.buttMain.Enable( False )
			ps.pub( toggle_selection_menu_item, False )
			return

		if fpsys.state.numticks > 0: 
			self.buttMain.Enable(True)
		else: 
			self.buttMain.SetLabel( _("Choose some fonts") )

	def MainFontViewUpdate(self):
		"""
		Vital routine - the heart if the app. 
		
		This decides what to do based on what has been selected.
		It draws the controls and the fonts as appropriate. 
		It also sets flags in fpsys.state
		"""
		## Get shorter vars to use.
		V = fpsys.state.viewobject
		T = fpsys.state.targetobject
			
		Vpatt = fpsys.state.viewpattern # View Pattern
		Tpatt = fpsys.state.targetpattern # Target pattern
	
		Patt = Vpatt + Tpatt # Patt = Pattern

		lab = ""
		status = ""
		
		## June 2009: A default value for this:
		self.TICKMAP = self.TICK

		## E == Empty View - no fonts in chosen Source.
		## N == Empty Target - no fonts.
		## P is Pog
		## F is Folder
		
		if Vpatt == "E": #NOTE : TESTING VPATT, not PATT - ergo: this covers E, EN, EP
			## Empty "E" - when the chosen Folder or Pog has NO FONTS IN IT.
			if Tpatt == "P":
				lab = _("Your active Target Pog is:%s") % T.name
				status = _("Please choose a Source.")
			else:
				lab = _("There are no fonts in here.")
				status = _("Please choose a Pog or a Font folder on the left.")
			btext = _("Nothing to do")
			fpsys.state.cantick = False
			fpsys.state.action = "NOTHING_TO_DO" # We will test this in mainframe::OnMainClick
			
		elif Patt == "FN":
			#View a Folder, no target
			lab = _("Viewing Folder:%s") % V.label()
			fpsys.state.cantick = False
			btext = _("Nothing to do")
			fpsys.state.action = "NOTHING_TO_DO" # We will test this in mainframe::OnMainClick
			status = _("Viewing a folder.")
		elif Patt == "PN": #A single Pog in the VIEW
			#View a pog, no target
			if V.isInstalled():
				## Cannot remove fonts from an installed pog
				lab = _("Viewing (installed) Pog: %s") % V.name
				btext = _("Nothing to do")
				fpsys.state.action = "NOTHING_TO_DO"
				fpsys.state.cantick = False
				status = _("You cannot change an installed Pog.")
			else:
				lab = _("Viewing (editable) Pog: %s") % V.name
				fpsys.state.cantick = True
				btext = _("Remove fonts from %s") % V.name
				self.TICKMAP = self.CROSS
				fpsys.state.action = "REMOVE" # We will test this in mainframe::OnMainClick
				status = _("You can remove fonts from the selected Target Pog.")
		elif Patt == "FP":
			#Folder to Pog
			if T.isInstalled():
				## We cannot put stuff into an installed pog
				lab = _("Viewing Folder:%s") % V.label()
				btext = _("Nothing to do")
				fpsys.state.action = "NOTHING_TO_DO"
				fpsys.state.cantick = False
				status = _("You cannot change an installed Pog.")
			else:
				lab = _("Append From: %(source)s To:%(target)s") % { "source":V.label(), "target":T.name }
				btext = _("Put fonts into %s") % T.name
				self.TICKMAP = self.TICK
				fpsys.state.cantick = True
				fpsys.state.action = "APPEND" # We will test this in mainframe::OnMainClick
				status = _("You can append fonts to your target Pog.")
		elif Patt == "PP":
			#Pog to Pog
			if T.isInstalled():
				## We cannot put fonts into an installed pog
				lab = _("Viewing Pog:%(source)s, but Pog:%(target)s is installed.") % {"source":V.name, "target":T.name}
				btext = _("Nothing to do")
				fpsys.state.action = "NOTHING_TO_DO"
				fpsys.state.cantick = False
				status = _("You cannot change an installed Pog.")
			else: #Not installed.
				if fpsys.state.samepogs: #Are the two pogs the same?
					## The validate routines determined the samepogs value.
					lab = _("These two are the same Pog.")
					fpsys.state.cantick = True
					btext = _("Nothing to do")
					fpsys.state.action = "NOTHING_TO_DO"
					status = _("Your Source and Target are the same Pog.")
				else: # Normal pog to pog
					lab = _("Append from Pog:%(source)s into Pog:%(target)s") % {"source":V.name, "target":T.name}
					btext = _("Put fonts into %s") % T.name
					self.TICKMAP = self.TICK
					fpsys.state.cantick = True	 
					fpsys.state.action = "APPEND" # We will test this in mainframe::OnMainClick
					status = _("You can append fonts to your target Pog.")
		else:
			print "MOJO ERROR: %s and trouble" % Patt
			raise SystemExit

		## Enable/Disable the Purge menu item
		ps.pub( toggle_purge_menu_item, False )
		if Vpatt=="P":
			if not fpsys.state.viewobject.isInstalled():
				ps.pub( toggle_purge_menu_item, True )
		

		self.buttMainLastLabel=btext
		self.textMainInfo.SetLabel(lab)
		self.textMainInfo.Show()
		if status is not "":
			ps.pub(print_to_status_bar, status)

		self.ToggleMainButton()

		fpsys.markInactive()
		self.filterAndPageThenCallCreateFitmaps()

	def ResetToPageOne(self):
		self.pageindex = 1 # I start here

