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
import fontybugs
import fpversion

## Now, bring in all those big modules
import wx

## Setup wxPython to access translations : enables the stock buttons.
langid = wx.LANGUAGE_DEFAULT # Picks this up from $LANG
mylocale = wx.Locale( langid )

## Fetch my own pubsub stuff
from pubsub import *
ps = CPubsub()

## Fetch the dialogue classes *About, Settings, Help, etc.*
import dialogues

## DND: NB--
## Comments that have DND: in them mean DO NOT DELETE. They are used by me via grep on the cli.


#from gui_PogChooser import *

from gui_Left import *
from gui_Middle import *
from gui_Right import *


class Splitter(wx.SplitterWindow):
	"""
	The splitter used twice in mainframe.
	"""
	def __init__(self, parent) :
		wx.SplitterWindow.__init__(self, parent, -1, style = wx.SP_LIVE_UPDATE | wx.SP_3D) 

class StatusBar(wx.StatusBar):
	"""
	The status bar
	"""
	def __init__(self, parent):
		wx.StatusBar.__init__(self, parent, -1)
		self.SetFieldsCount(1)
		self.SetStatusText( _("Welcome to Fonty Python version %s") % fpversion.version, 0)
	def Report(self, msg):
		self.SetStatusText(msg, 0)

class MainFrame(wx.Frame):
	def __init__(self,parent,title) :
		## Draw the frame
		title = title + "   -   " + locale.getpreferredencoding()
		wx.Frame.__init__(self,parent,-1,title,fpsys.config.pos,fpsys.config.size) 
		
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
		self.sb = StatusBar(self)
		self.SetStatusBar(self.sb)
		
		## Prepare the menu bar
		self.menuBar = wx.MenuBar()

		## FILE MENU
		menu1 = wx.Menu()
		menu1.Append(101, _("&Settings\tCtrl+S"), _("Change settings"))
		menu1.AppendSeparator()
		## Jan 18 2008
		menu1.Append( 102, _("&Check fonts"), _("Find those fonts that crash Fonty.") )
		
		self.exit = menu1.Append(103, _("&Exit"), _("Close the app"))
		## Add menu to the menu bar
		self.menuBar.Append(menu1, _("&File"))


		## SELECT MENU: June 2009
		menu1 = wx.Menu()
		menu1.Append( 301, _("&Select ALL the fonts"), _("Select ABSOLUTELY ALL the fonts in the chosen source."))
		menu1.Append( 302, _("&Clear ENTIRE selection"), _("Clear the selection completely.") )
		## Add menu to the menu bar
		self.menuBar.Append(menu1, _("&Selection"))


		## HELP MENU
		menu2 = wx.Menu() 
		menu2.Append(201, _("H&elp\tF1"))
		menu2.Append(202, _("&About"))
		## Append 2nd menu
		self.menuBar.Append(menu2, _("&Help"))

		## Tell the frame the news
		self.SetMenuBar(self.menuBar)

		## Setup the ESC key trap
		accel = wx.AcceleratorTable([(wx.ACCEL_NORMAL, wx.WXK_ESCAPE, self.exit.GetId())])
		self.SetAcceleratorTable(accel)
		
		## The X close window button.
		self.Bind( wx.EVT_CLOSE, self.__onHandleESC )
	
		## Bind events for the menu items
		self.Bind(wx.EVT_MENU, self.__onHandleESC, self.exit)
		self.Bind(wx.EVT_MENU, self.__menuSettings, id = 101)
		self.Bind(wx.EVT_MENU, self.__menuCheckFonts, id = 102 )
		self.Bind(wx.EVT_MENU, self.__menuAbout, id = 202)
		self.Bind(wx.EVT_MENU, self.__menuHelp, id = 201)
		# June 2009
		self.Bind(wx.EVT_MENU, self.__menuSelectionALL, id=301)
		self.Bind(wx.EVT_MENU, self.__menuSelectionNONE, id=302)
		
		## Create a splitter 
		self.splitter = Splitter(self) 
	
		## The notebook
		self.panelNotebook = wx.Panel(self.splitter) 
		
		## Notebook label and icon
		self.viewIcon = wx.StaticBitmap\
		(self.panelNotebook, -1, wx.Bitmap\
		(fpsys.mythingsdir + 'icon_source_16x16.png', wx.BITMAP_TYPE_PNG))		
		self.viewLabel = wx.StaticText\
		(self.panelNotebook, -1, _("Source Folder, or Pog"), style = wx.ALIGN_LEFT)
		self.viewLabel.SetFont\
		(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD))
		
		## A horiz sizer to hold the icon and text
		self.sizer_iconandtext = wx.BoxSizer(wx.HORIZONTAL)
		self.sizer_iconandtext.Add((4,1),0)
		self.sizer_iconandtext.Add\
		(self.viewIcon, 0, wx.TOP | wx.BOTTOM, border = 4)
		self.sizer_iconandtext.Add\
		(self.viewLabel, 1, wx.EXPAND | wx.TOP | wx.BOTTOM | wx.LEFT, border = 4)
		
		## Now the actual notebook
		self.nb = NoteBook(self.panelNotebook)

		## Make a Vertical sizer to hold them.
		self.sizerNotebook = wx.BoxSizer(wx.VERTICAL)
		
		## Add them to the sizer.
		self.sizerNotebook.Add(self.sizer_iconandtext, 0, wx.EXPAND)
		self.sizerNotebook.Add(self.nb,1,wx.EXPAND) 
		
		self.panelNotebook.SetSizer(self.sizerNotebook) 
		self.sizerNotebook.Layout() 
		
		## dec 2007 : Added a second splitter. It was a bitch!
		self.splitter2 = Splitter(self.splitter) # gets the second slot of splitter
		
		## Font View Panel Control:
		self.panelFontView = FontViewPanel(self.splitter2) # first slot in splitter2
		
		self.sizerFontView  = wx.BoxSizer(wx.VERTICAL) 
		self.sizerFontView.Add(self.panelFontView, 1, wx.EXPAND)
		self.panelFontView.Layout()
	   
		## THE FAR RIGHT HAND SIDE
		## The TargetPogChooser
		self.panelTargetPogChooser = TargetPogChooser(self.splitter2) # last slot of splitter2

		self.sizerRight = wx.BoxSizer(wx.HORIZONTAL)
		self.sizerRight.Add(self.panelTargetPogChooser, 1, wx.EXPAND)
		self.panelTargetPogChooser.Layout()
		
		self.splitter.SetMinimumPaneSize(64) 
		self.splitter.SplitVertically\
		(self.panelNotebook, self.splitter2, fpsys.config.leftSash )
		self.splitter2.SetMinimumPaneSize(128)
		# Negative here means pixels from the right edge.
		self.splitter2.SplitVertically\
		(self.panelFontView, self.panelTargetPogChooser, -fpsys.config.rightSash )

		self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
		
		## Now to subscribe to have my various def called from other places:
		ps.sub(update_font_view, self.UpdateFontViewPanel) ##DND: class MainFrame
		ps.sub(show_error, self.ErrorBox) ##DND: class MainFrame
		ps.sub(show_error_and_abort, self.ErrorAbort) ##DND: class MainFrame
		ps.sub(show_message, self.MessageBox) ##DND: class MainFrame
		ps.sub(reset_to_page_one, self.ResetToPageOne) ##DND: class MainFrame
		ps.sub(add_item_to_notebook, self.NotebookAddItem) ##DND: class MainFrame
		ps.sub(remove_item_from_notebook, self.NotebookRemoveItem) ##DND: class MainFrame
		ps.sub(print_to_status_bar, self.StatusbarPrint) ##DND: class MainFrame
		ps.sub(install_pog, self.InstallPog) ##DND: class MainFrame
		ps.sub(uninstall_pog, self.UninstallPog) ##DND: class MainFrame
		ps.sub(main_button_click, self.OnMainClick) ##DND: class MainFrame
		
		
		## Dec 2007 - Actually this one does not function.
		ps.sub(menu_settings, self.__menuSettings) ##DND: class MainFrame
		
		## When splitter is changed (after the drag), we want to redraw
		## the fonts to the new width.
		self.splitter.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.__onSize)
		
		self.Layout()

		## call the big one - the big chief, the big cheese:
		self.UpdateFontViewPanel() #Go and fill in the font view and surrounding controls
		
		## A nasty looking line to call the SortOutTheDamnImages function
		## This is to draw the right icons dep on the params from cli.
		self.panelTargetPogChooser.pogTargetlist.SortOutTheDamnImages(False)
		
	def __onSize( self, evt ):
		"""
		The splitter has been moved. Don't ask me why splitter and not splitter2
		is the one we have to use. Go figure.
		"""
		ps.pub( update_font_view ) # starts a chain of calls.
		
	def GetSashesPos( self, args=None ):
		## For saving/restoring the sashes to where we bloody left them :\
		return ( self.splitter.GetSashPosition(), self.panelTargetPogChooser.GetClientSize()[0])
		
	def StatusbarPrint(self, args):
		self.sb.Report(args[0])
	def NotebookAddItem(self,args):
		self.nb.AddItem(args[0])
	def NotebookRemoveItem(self, args):
		self.nb.RemoveItem(args[0])
	def ResetToPageOne(self, args):
		"""
		Calls ResetToPageOne in the FontViewPanel
		"""
		self.panelFontView.ResetToPageOne()
		
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
		self.__endApp()
		
	def UpdateFontViewPanel(self, args = None):
		self.panelFontView.MainFontViewUpdate()
		self.Refresh()
	
	def InstallPog(self, args):
		"""
		pog.install() Raises:
				PogEmpty
				PogAllFontsFailedToInstall
				PogSomeFontsDidNotInstall
		"""
		try:
			fpsys.state.targetobject.install()
		except (fontybugs.PogSomeFontsDidNotInstall), e:
			## Show a warning, but continue.
			self.ErrorBox([unicode( e ),]) #send it as a list
		except (fontybugs.PogEmpty, fontybugs.PogAllFontsFailedToInstall), e:
			## Either Pog is empty, or
			## not a single font in this pog actually installed.
			## It has already been flagged as NOT INSTALLED
			self.ErrorBox([unicode( e ),])
			return # Make no changes to the display or icon - yet... badpog icon ?
		## Update GUI
		self.sb.Report(_("%s has been installed.") % fpsys.state.targetobject.name)
		ps.pub(change_pog_icon)
		ps.pub(toggle_targetpog_buttons) # Update the greying of the buttons
		self.UpdateFontViewPanel()

	def UninstallPog(self, args):
		"""
		pog.uninstall() Raises:
				PogEmpty
				PogLinksRemain
				PogNotInstalled		
		"""
		try:
			fpsys.state.targetobject.uninstall()
		except (fontybugs.PogEmpty, 
						fontybugs.PogNotInstalled, 
						fontybugs.PogLinksRemain
					 ), e:
			## PogNotInstalled is prevented by buttons greying out in the gui.
			self.ErrorBox([unicode( e ),])
			return
		## Update GUI
		self.sb.Report(_("%s has been uninstalled.") % fpsys.state.targetobject.name)
		ps.pub(change_pog_icon)
		ps.pub(toggle_targetpog_buttons) #Update the greying of the buttons
		self.UpdateFontViewPanel()

			
	def OnMainClick(self, args) :
		"""
		Removes fonts, or Appends fonts. Depends on situation in fpsys.state
		
		It's odd to have these routines in mainframe. I am using dialogues that
		parent to the wx.Frame but I suppose I could shift this to panelFontView.
		"""
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
				except(fontybugs.PogWriteError), e:
					bug = True
					self.errorBox([unicode( e ),])
				## Now, let's redraw the vo
				self.UpdateFontViewPanel()
				if not bug:
					self.sb.Report(_("Selected fonts have been removed."))
				else:
					self.sb.Report(_("There was an error writing the pog to disk. Nothing has been done"))
		
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
				except(fontybugs.PogWriteError), e:
					bug = True
					self.ErrorBox( [repr( e )] )
				self.UpdateFontViewPanel()
				if not bug:
					self.sb.Report(_("Selected fonts are now in %s.") % to.label())
				else:
					self.sb.Report(_("There was an error writing the pog to disk. Nothing has been done"))
		
		## After pressing the button, the focus goes ... away ...
		## I don't know where and I'm trying to get it to go someplace
		## so that the ESC key continues working.
		## Forget it. I can't fix this. Onwards... other stuff to do!
		## self.menuBar.SetFocus()
		
	def __onHandleESC(self, e) :
		print strings.done
		self.__endApp() 

	def __endApp(self) :
		"""
		Save app's vital statistics and exit.
		See the end of start.py where it's actually saved.
		"""
		fpsys.config.pos = self.GetPositionTuple() 
		## Dec 2007 - I was using the wrong func and the
		## main window kept getting smaller!
		fpsys.config.size = self.GetSizeTuple()
		fpsys.config.leftSash, fpsys.config.rightSash = self.GetSashesPos()
		##June 2009 - fetch and record the value of the recurse folders checkbox.
		fpsys.config.recurseFolders = app.GetTopWindow().nb.recurseFolders.GetValue()
		self.Destroy() 
   
	def __menuSettings(self, e):
		lastnuminpage, lastpoints, lasttext = fpsys.config.numinpage ,fpsys.config.text, fpsys.config.points
		dlg = dialogues.DialogSettings(self)
		val = dlg.ShowModal()
		if val == wx.ID_OK:
			## Did anything change?
			num = int(dlg.inputPageLen.GetValue())
			points = int(dlg.inputPointSize.GetValue())
			txt = dlg.inputSampleString.GetValue()
			if (num, txt, points) != (lastnuminpage, lastpoints, lasttext):
				fpsys.config.numinpage = int(num)
				fpsys.config.points = int(points)
				if len(txt) > 0: fpsys.config.text =  txt
			## Now to refresh things:
			self.UpdateFontViewPanel()
		dlg.Destroy()

	def __menuAbout(self, e):
		dlg =dialogues.DialogAbout(self)
		val = dlg.ShowModal()
		dlg.Destroy()
		
	def __menuHelp(self, e):
		dlg = dialogues.DialogHelp(self, size=(800, 600))
		val = dlg.ShowModal()
		dlg.Destroy()

	def __menuCheckFonts( self, e ):
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

	def __menuSelectionALL(self,e):
		if not fpsys.state.cantick: return # Can't tick if this is False.
		fpsys.state.numticks=0
		vo=fpsys.state.filteredViewObject # We want to select what is FILTERED
		for fi in vo:
			if not fi.inactive:
				fi.ticked=True
				fpsys.state.numticks += 1
		## Now update the view
		ps.pub( update_font_view )	

	def __menuSelectionNONE(self,e):
		fpsys.state.numticks=0
		vo=fpsys.state.viewobject # We *REALLY* mean select NONE. So ignore filter.
		for fi in vo:
			if not fi.inactive:
				fi.ticked=False
		## Now update the view
		ps.pub( update_font_view )	




## Start the main frame and then show it.
class App(wx.App) :
	def OnInit(self) :
		## Initial dialogue to inform user about their potential fate:
		if not "unicode" in wx.PlatformInfo:
			wx.MessageBox(_("I am sorry, but Unicode is not supported by this installation of wxPython. Fonty Python relies on Unicode and will simply not work without it.\n\nPlease fetch and install the Unicode version of python-wxgtk."), caption=_("SORRY: UNICODE MUST BE SUPPORTED"), style=wx.OK | wx.ICON_EXCLAMATION )
			raise SystemExit
		frame = MainFrame(None, _("Fonty Python: bring out your fonts!"))
		self.SetTopWindow(frame) 
		frame.Show(True) 
		return True
		
## app
app = App(0) 
		
## start 
app.MainLoop() 
