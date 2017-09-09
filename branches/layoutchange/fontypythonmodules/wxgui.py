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

import locale
import strings
import fpsys # Global objects
import fpversion

## Now, bring in all those big modules
import wx

#Sept 2017
from wx.lib.splitter import MultiSplitterWindow

## AUG 2017
## Massive gui hacking. See wxgui.orig.py if you need to roll back.






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

## DND: NB--Comments that have DND: in them mean DO NOT DELETE. They are used by me via grep on the cli.


from gui_FontSources import *
from gui_FontView import *
from gui_PogTargets import *


class StatusBar(wx.StatusBar):
	"""
	The status bar
	"""
	def __init__(self, parent):
		wx.StatusBar.__init__(self, parent, -1) # default style is good

		##The last field is the gripper (32px)
		self.SetFieldsCount( 4 if fpsys.iPC.missingDotFontsDirectory else 3 )

		self.SetStatusText( _("Welcome to Fonty Python, vers %s") % fpversion.version, 0)

		if fpsys.iPC.missingDotFontsDirectory:
			self.SetStatusText( strings.missingDotFontsMessages["statusbar"], 2)
			self.SetStatusWidths([300,-2,-1,32])
			#self.SetStatusStyles([wx.SB_SUNKEN]*3) #SB_SUNKEN is not available to me. 
		else:
			self.SetStatusWidths([300,-2,32])
			#self.SetStatusStyles([wx.SB_SUNKEN]*2)


	def Report(self, msg):
		self.SetStatusText(msg, 1)

class MainFrame(wx.Frame):
	"""
	The main frame for the app. Has some functionality for menu items.
	"""
	def __init__(self,parent,title) :
		## Draw the frame
		title = title + "   -   " + locale.getpreferredencoding()
		wx.Frame.__init__(self,parent,-1,title,fpsys.config.pos,fpsys.config.size)

		framewidth = self.GetSizeTuple()[0]
		
		## Try to show an icon
		try:
			image = wx.Image(fpsys.mythingsdir + 'fplogo.png', wx.BITMAP_TYPE_PNG)
			image = image.ConvertToBitmap()
			icon = wx.EmptyIcon()
			icon.CopyFromBitmap(image)
			self.SetIcon(icon)
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
		menu1.Append(101, _("&Settings\tCtrl+S"), _("Change settings"))
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
		menu2.Append(201, _("H&elp\tF1"))
		menu2.Append(202, _("&About"))
		self.menuBar.Append(menu2, _("&Help"))

		self.SetMenuBar(self.menuBar)

		## Setup the ESC key and the LEFT / RIGHT keys
		accel = wx.AcceleratorTable([
			(wx.ACCEL_NORMAL, wx.WXK_ESCAPE, self.exit.GetId()),
			(wx.ACCEL_CTRL, wx.WXK_RIGHT, wx.ID_FORWARD),
			(wx.ACCEL_CTRL, wx.WXK_LEFT, wx.ID_BACKWARD)
			])
		self.SetAcceleratorTable(accel)

		## Bind the Left and Right key shortcuts.	
		self.Bind(wx.EVT_MENU, self.OnAccelKey, id=wx.ID_FORWARD )
		self.Bind(wx.EVT_MENU, self.OnAccelKey, id=wx.ID_BACKWARD )

		## The X close window button.
		self.Bind( wx.EVT_CLOSE, self.onHandleESC )

		## Bind events for the menu items
		self.Bind(wx.EVT_MENU, self.onHandleESC, self.exit)
		self.Bind(wx.EVT_MENU, self.menuSettings, id = 101)
		self.Bind(wx.EVT_MENU, self.menuCheckFonts, id = 102 )
		self.Bind(wx.EVT_MENU, self.menuPurgePog, id = 103 )
		self.Bind(wx.EVT_MENU, self.menuAbout, id = 202)
		self.Bind(wx.EVT_MENU, self.menuHelp, id = 201)
		# June 2009
		self.Bind(wx.EVT_MENU, self.menuSelectionALL, id=301)
		self.Bind(wx.EVT_MENU, self.menuSelectionNONE, id=302)


		## THE MAIN GUI
		## ------------------------------------------------------------------

		## A temporary switch to test out various ideas
		self.whatgui = 4

		MINSCREENWIDTH = 800

		if self.whatgui == 1:
			## Sept 2017: Using a multi splitter window
			self.msw = MultiSplitterWindow(self, style=wx.SP_LIVE_UPDATE)
			self.msw.SetMinimumPaneSize(150)

			## SASHZERO is the left-most sash, it's x pixels from the left:
			SASHZERO = fpsys.config.leftSash # Has a minimum val in that code


			## LEFT HAND SIDE GUI
			## -------------------------------------------------------------------
			## The Font Source notebook, etc.
			self.panelFontSources = FontSourcesPanel(self.msw)
			self.panelFontSources.SetMinSize(wx.Size(SASHZERO,100))
			## Put the panelNotebook into the first pane of the splitter
			self.msw.AppendWindow(self.panelFontSources, SASHZERO)


			## CENTRE GUI
			## -------------------------------------------------------------------
			## Font View Panel Control. No sizer.
			self.fontViewPanel = FontViewPanel(self.msw)
			## Have a minimum for the fontviewpanel
			minfontvwidth = framewidth/3 #randomly set it as a third.
			self.fontViewPanel.SetMinSize(wx.Size(minfontvwidth,1))
			## To get it to display, don't set that min in AppendWindow!
			self.msw.AppendWindow(self.fontViewPanel)


			## THE FAR RIGHT HAND SIDE GUI
			## --------------------------------------------------------------------
			## The TargetPogChooser. No sizer.
			self.panelTargetPogChooser = TargetPogChooser(self.msw)

			## Set the minimum width between the strict minimum in the config
			## and the actual size the panel happens to be right now.
			rightminwidth = max(fpsys.config.rightSash, self.panelTargetPogChooser.GetBestSize()[0])

			## SASHONE is the right-hand splitter (it's index 1)
			## It's the whole window minus the left panel (SASHZERO) minus the right panel.
			## It's x pixels across from SASHZERO, not the left-edge of the frame!
			SASHONE = framewidth - SASHZERO - rightminwidth

			# Sept 2017: Adding sizer to the right causes a SEGFAULT. H.A.N.D.
			# Without a sizer, I don't think I can properly control the width
			# of the right hand side. It tends to go off the window.
			# Hence all the other stuff to try constraining it.
			#self.sizerRight = wx.BoxSizer(wx.HORIZONTAL)
			#self.sizerRight.Add(self.panelTargetPogChooser, 1, wx.EXPAND)

			## Stick the rhs into the splitter window:
			self.msw.AppendWindow(self.panelTargetPogChooser, rightminwidth )

			## Forcibly set the sashes - which forcibly splits and sizes stuff
			self.msw.SetSashPosition(0,SASHZERO)
			self.msw.SetSashPosition(1,SASHONE)

			# Thanks to the multiSplitterWindow code from the demo:
			self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, self.onSplitterPosChanging)#present tense
			self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.onSplitterChanged)#past tense

		if self.whatgui == 2:
			#splitter window of 2 across
			#left: a panel with sizer of two across of: source, then target guis
			#right: fontview
			self.spw = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
			self.spw.SetMinimumPaneSize(300)


			p1 = wx.Panel(self.spw)
			self.panelFontSources = FontSourcesPanel(p1)
			self.panelTargetPogChooser = TargetPogChooser(p1)

			twosizer = wx.BoxSizer(wx.HORIZONTAL)
			twosizer.Add(self.panelFontSources, 1, wx.EXPAND)
			twosizer.Add(self.panelTargetPogChooser, 1, wx.EXPAND)

			p1.SetSizer(twosizer)

			self.fontViewPanel = FontViewPanel(self.spw)

			self.spw.SplitVertically( p1, self.fontViewPanel)#, self.initpos)

		if self.whatgui == 3:
			#splitter window of 2 across
			#left: a panel with sizer of two high of: source, then target guis
			#right: fontview
			##This one freezes the app when you resize to the right... :(
			## Hard to reproduce. I used gdb and got it to crash, then
			## did a 'bt' and saw some complaints about get text extents
			## might be a bug in my font drawing code..?
			self.spw = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
			self.spw.SetMinimumPaneSize(300)

			p1 = wx.Panel(self.spw)
			self.panelFontSources = FontSourcesPanel(p1)
			self.panelTargetPogChooser = TargetPogChooser(p1)

			twosizer = wx.BoxSizer(wx.VERTICAL)
			twosizer.Add(self.panelFontSources, 1, wx.EXPAND)
			twosizer.Add(self.panelTargetPogChooser, 1, wx.EXPAND)

			p1.SetSizer(twosizer)

			self.fontViewPanel = FontViewPanel(self.spw)

			self.spw.SplitVertically( p1, self.fontViewPanel)#, self.initpos)
			# Thanks to the multiSplitterWindow code from the demo:
			self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, self.onSplitterPosChanging)
			self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.onSplitterPosChanged)

		if self.whatgui == 4:
			#No splitters at all.
			# box across two
			# left box down two (source/target), right = fontview
			# :- kind of shape.

			minw = 320
			fvminw = MINSCREENWIDTH - minw
			ms = wx.Size(minw,1)

			self.panelFontSources = FontSourcesPanel(self)
			self.panelFontSources.SetMinSize(ms)

			self.panelTargetPogChooser = TargetPogChooser(self)
			self.panelTargetPogChooser.SetMinSize(ms)

			self.fontViewPanel = FontViewPanel(self)
			self.fontViewPanel.SetMinSize(wx.Size(fvminw,1))

			stsizer = wx.BoxSizer(wx.VERTICAL)
			stsizer.Add( self.panelFontSources, 1, wx.EXPAND|wx.ALL,border = 5 )
			stsizer.Add( self.panelTargetPogChooser, 1, wx.EXPAND|wx.ALL,border = 5 )


			lrsizer = wx.BoxSizer(wx.HORIZONTAL)
			lrsizer.Add( stsizer, 0, wx.EXPAND)
			lrsizer.Add( self.fontViewPanel, 1, wx.EXPAND|wx.ALL, border = 5 )

			self.SetSizer(lrsizer)

			## Idle/resize idea from here:
			##https://stackoverflow.com/questions/13479831/what-is-the-simplest-way-of-monitoring-when-a-wxpython-frame-has-been-resized
			self.resized = False
			self.Bind(wx.EVT_IDLE, self.onIdle)
			self.Bind(wx.EVT_SIZE, self.onFrameSize)




		## GUI ENDS
		## =============

		self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

		## Now to subscribe to have my various def called from other places:
		ps.sub(show_error, self.ErrorBox) ##DND: class MainFrame
		ps.sub(show_error_and_abort, self.ErrorAbort) ##DND: class MainFrame
		ps.sub(show_message, self.MessageBox) ##DND: class MainFrame
		ps.sub(print_to_status_bar, self.StatusbarPrint) ##DND: class MainFrame
		## Dec 2007 - Used on middle click in gui_Fitmap.py
		ps.sub( menu_settings, self.menuSettings ) ##DND: class MainFrame
		ps.sub( toggle_selection_menu_item, self.toggleSelectionMenuItem ) ##DND: class MainFrame

		ps.sub( toggle_purge_menu_item, self.TogglePurgeMenuItem ) ##DND: class MainFrame


		## call the big one - the big chief, the big cheese:
		## This eventually draws all the Fitmaps - giving the middle a width.
		ps.pub( update_font_view ) #DND: It's in gui_FontView.py under class FontViewPanel


		self.SetMinSize(wx.Size(MINSCREENWIDTH,600)) #Old Skool: Assuming monitor size...
		self.Layout()




		## This is to draw the correct icons depending on cli params.
		self.panelTargetPogChooser.pogTargetlist.SortOutTheDamnImages(False)


	def onSplitterPosChanging(self,evt):
		"""
		A Splitter is moving - PRESENT TENSE. Let's do the least work poss.
		"""
		if self.whatgui == 1:
			## Filter the second splitter - the right hand side:
			if evt.GetSashIdx() == 1:
				## Let's (at least) try to constrain the width of the rhs panel
				esp = evt.GetSashPosition()

				framewidth = self.GetSizeTuple()[0]
				rightminwidth = self.panelTargetPogChooser.GetBestSize()[0]
				sashzero = self.msw.GetSashPosition(0)

				# esp is pixels relative to sashzero, thus we must
				# subtract sashzero away to get it relative to 0.

				# So, if the second splitter is too far across, then veto the event.
				# This has the effect of stopping the drag when the rhs panel
				# is getting smaller than its minimum.
				# Again, taken from the wx-demo code.
				if esp > framewidth - rightminwidth - sashzero:
					evt.Veto()
				return

		if self.whatgui == 3:
			esp = evt.GetSashPosition()
			if esp > 300:
				evt.Veto()
			return

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
			#print "  Idle updates fontViewPanel"
			ps.pub (update_font_view )
			self.resized = False

	def getSashesPos( self, args=None ):
		## For saving/restoring the sashes to where we bloody left them :\
		if self.whatgui == 1:
			return ( self.msw.GetSashPosition(0), self.panelTargetPogChooser.GetClientSize()[0])
		return (200,200)






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

		#Sept 2017
		fpsys.config.leftSash, fpsys.config.rightSash = self.getSashesPos()

		##June 2009 - fetch and record the value of the recurse folders checkbox.
		fpsys.config.recurseFolders = app.GetTopWindow().panelFontSources.nb.recurseFolders.GetValue()
		self.Destroy()

	def menuSettings(self, e):
		lastnuminpage, lastpoints, lasttext = fpsys.config.numinpage ,fpsys.config.text, fpsys.config.points
		dlg = dialogues.DialogSettings(self)
		val = dlg.ShowModal()
		if val == wx.ID_OK:
			## Did anything change?
			num = int(dlg.inputPageLen.GetValue())
			points = int(dlg.inputPointSize.GetValue())
			txt = dlg.inputSampleString.GetValue()
			ignoreAdjust = dlg.chkAdjust.GetValue() #Sept 2009
			if (num, txt, points) != (lastnuminpage, lastpoints, lasttext):
				fpsys.config.numinpage = int(num)
				fpsys.config.points = int(points)
				if len(txt) > 0: fpsys.config.text =  txt

			fpsys.config.ignore_adjustments = ignoreAdjust #Sept 2009
			fpsys.config.CMC.SET_CURRENT_APPNAME( dlg.CHOSEN_CHARACTER_MAP) # Oct 2009

			## Now to refresh things:
			## Sept 2009 : size change means we need new values for fitmaps
			ps.pub( reset_top_left_adjustments ) ##DND : In ScrolledFontView
			ps.pub( update_font_view )
		dlg.Destroy()

	def menuAbout(self, e):
		dlg =dialogues.DialogAbout(self)
		val = dlg.ShowModal()
		dlg.Destroy()

	def menuHelp(self, e):
		# July 2016
		# =========
		# Made the initial size of the help dialog smaller
		# Was requested by a user who has a small screen
		# ~600px wide is about as narrow as I can get it...
		dlg = dialogues.DialogHelp(self, size=(676, 400))
		val = dlg.ShowModal()
		dlg.Destroy()

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
			##		  PogEmpty
			##		  PogInstalled
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
class App(wx.App , wx.lib.mixins.inspection.InspectionMixin) :
	"""
	The main wxPython app starts here
	"""
	def OnInit(self):
		self.Init()  # initialize the inspection tool

		## Initial dialogue to inform user about their potential fate:
		if not "unicode" in wx.PlatformInfo:
			wx.MessageBox(_("I am sorry, but Unicode is not supported by this installation of wxPython. Fonty Python relies on Unicode and will simply not work without it.\n\nPlease fetch and install the Unicode version of python-wxgtk."), caption=_("SORRY: UNICODE MUST BE SUPPORTED"), style=wx.OK | wx.ICON_EXCLAMATION )
			raise SystemExit

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
			aBitmap = wx.Bitmap( fpsys.mythingsdir + "splash.png", wx.BITMAP_TYPE_PNG )
			splashStyle = wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT
			splashDuration = 3000 # milliseconds

			wx.SplashScreen.__init__(self, aBitmap, splashStyle, splashDuration, parent)
			self.Bind(wx.EVT_CLOSE, self.OnExit)

			# Nice! Kick the show off in 1 second's time
			self.fc = wx.FutureCall(1000,self.showMain)

		def OnExit(self, evt):
			# The program will freeze without this line.
			evt.Skip()	# Make sure the default handler runs too...
			self.Hide()

			# if the timer is still running, force the main frame to start
			if self.fc.IsRunning():
				self.fc.Stop()
				self.showMain()

		def showMain(self):
			## Oct 2009
			##  this is the only place I can get the system font family
			fpsys.DFAM = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT).GetFamily()

			frame = MainFrame(None, _("Fonty Python: bring out your fonts!"))
			app.SetTopWindow(frame)

			frame.Show(True)

			if self.fc.IsRunning():
				self.Raise()


#Start the app!
app = App(0)
app.MainLoop()
