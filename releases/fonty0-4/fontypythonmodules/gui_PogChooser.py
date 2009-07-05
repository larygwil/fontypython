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

import wx, locale

## Setup wxPython to access translations : enables the stock buttons.
langid = wx.LANGUAGE_DEFAULT # Picks this up from $LANG
mylocale = wx.Locale( langid )

from pubsub import *
from wxgui import ps

import fpsys # Global objects
import fontcontrol
import fontybugs


class PogChooser(wx.ListCtrl) :
	"""
	Basic list control for pogs - instanced by TargetPogChooser and NoteBook
	This single class (being used twice) causes terrible conceptual hardships
	and forces all kinds of twisty tests. I'm sorry for this, we need a better
	solution.
	"""
	## CLASS LEVEL variables - special things these.
	__poglistCopy = {} # To help in sorting.
	__TARGET = None
	__VIEW = None
	
	def __init__(self, parent, whoami, select = None) :
		self.indexselected = 0
		self.lastindexselected = -1
		self.parent = parent
		self.whoami = whoami

		## Use Class-level attributes to record the history of 
		## the instantiation of this class. These vars do not
		## belong to the instances, but to this one class.
		## We keep refs to the two parents of this class.
		if whoami == "SOURCEPOG" :#isinstance( self.parent, wx.Panel ):
			PogChooser.__VIEW = self
			style = wx.LC_LIST | wx.LC_AUTOARRANGE | wx.LC_SORT_ASCENDING | wx.LC_SINGLE_SEL
		else:
			PogChooser.__TARGET = self.parent
			style = wx.LC_LIST | wx.LC_AUTOARRANGE | wx.LC_SORT_ASCENDING

		il = wx.ImageList(16,16,True) 
		png = wx.Bitmap(fpsys.mythingsdir + "/pog16x16.png",wx.BITMAP_TYPE_PNG) 
		il.Add(png) 
		png = wx.Bitmap(fpsys.mythingsdir + "/pog16x16.installed.png",wx.BITMAP_TYPE_PNG) 
		il.Add(png)
		## Dec 2007 : target icon
		png = wx.Bitmap( fpsys.mythingsdir + "/pog16x16.target.png", wx.BITMAP_TYPE_PNG )
		il.Add( png )
		
		wx.ListCtrl.__init__( self,parent,-1, style=style ) 
		
		self.AssignImageList(il, wx.IMAGE_LIST_SMALL) 

		self.__PC = fpsys.iPC # reuse the global pathcontrol object
		
		self.fillPogList() 
		
		## Highlight the pog selected (the last one, or the cli chosen one)
		if select:
			i = self.FindItem(-1, select)
			self.indexselected = i # Set this to help initial icon settings.
			self.Select(i, True)
		else:
			self.Select(0, False)
			self.indexselected = -1


		self.ClearBackground() 
		self.items = None
		
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect) 
		
		## This one is a double click event
		## self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.__onActivate )
		
		#self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
		
		## This subscribe line here will register TWICE since this PogChooser object is instanced
		## twice by the app...
		ps.sub(change_pog_icon, self.ChangeIcon) ##DND: class PogChooser
		
	def Sorter(self, key1, key2):
		"""
		Fetch the strings from our CLASS LEVEL copy of the pognames
		so that we can compare them via locale.
		"""
		s1,s2 = PogChooser.__poglistCopy[key1], PogChooser.__poglistCopy[key2]
		## Since the gui is unicode, I *think* I don't have to worry about errors here.
		return locale.strcoll( s1, s2 )
		
	def onSelect(self, e):
		wx.BeginBusyCursor()
		self.indexselected = e.m_itemIndex
		pognochange = False
		if self.indexselected == self.lastindexselected:
			## We have clicked on the same Pog as last time - ergo do nothing.
			pognochange = True
		self.lastindexselected = self.indexselected # Record this for next time around

		textpogname = self.GetItemText(self.indexselected) # Gets UNICODE !!!

		if self.whoami=="SOURCEPOG":
			ps.pub(source_pog_has_been_selected, textpogname, pognochange)
		else:
			ps.pub(target_pog_has_been_selected, textpogname, pognochange)
		
		self.SortOutTheDamnImages( pognochange )
				
		wx.EndBusyCursor()
		
	def SortOutTheDamnImages( self, pognochange ):
		"""
		Dec 2007 : This took me an entire day to figure out. Man...
		Determines the images of the list items.
		Is called from TargetPogChooser as well (when clear button is clicked)
		"""
		if pognochange is ():
			pognochange = True
			
		c = self.GetItemCount()
		sel = self.indexselected # the actual selection index, does not go to -1
		
		## Which kind of a McList am I?
		iAmTargetList = self.whoami=="TARGETPOG" #isinstance( self.parent, TargetPogChooser )
		## If there is an active selection?
		if sel > -1:
			for x in xrange(0, c):
				i = self.GetItem(x, 0)
				## Must make a tmp Pog before I can test installed status.
				tmpPog = fontcontrol.Pog(i.GetText())
				if tmpPog.isInstalled():
					self.SetItemImage(x, 1)
				else:
					## Handle the other icons (in the target list only)
					## that are not installed.
					if iAmTargetList:
						if x == sel:
							## No change means it *was* selected
							## and now it's been selected again
							## thus it can't be the target anymore.
							if pognochange: n = 0
							else: n = 2
							self.SetItemImage(x, n ) # new target icon
						else:
							self.SetItemImage(x, 0)
		## Tell the VIEW to imitate this picture.
			for x in xrange(0,c):
				ti = self.__TARGET.pogTargetlist.GetItem(x, 0) # the 0 is 'column'. Ignore.
				CLONE = ti.GetImage()# gets the image index, not an image bitmap.
				self.__VIEW.SetItemImage(x, CLONE)
				
	def __del__(self) :
		del self.items

	def fillPogList(self):
		"""
		This is among the very FIRST things we do.
		Fill the list with pogs.
		This will CULL any bad pogs (i.e. those with malformed content)
		Thus the PogInvalid error should not happen any more after a run.
		"""
		pl = self.__PC.getPogNames() # pl will always be a BYTE STRING list
		
		for p in pl: # 'p' is a byte string.
			ipog = fontcontrol.Pog(p)
			try: #catch pogs that are not properly formed
				if ipog.isInstalled(): i = 1 # isInstalled opens the pog file.
				else: i = 0
			except fontybugs.PogInvalid, eInst:
				## An "invalid" pog is one that does not have
				## installed/not installed on the first line.
				print _(u"(%s) skipped. It's an invalid pog.") % [p]
				continue

			## Let's try to make a unicode of p so li.SetText(p) can display it:
			## I think it's easier to do this myself.
			try:
				up = p.decode(locale.getpreferredencoding())
				p = up
			except UnicodeDecodeError:
				## We can't convert it under this locale
				print _(u"(%s) skipped. I can't display this name under your locale.") % [p]
				continue
			## Okay, we have a valid pog name to use:
			li = wx.ListItem() 
			li.SetImage(i) 
			li.SetText(p) 
			id = wx.NewId()
			PogChooser.__poglistCopy[id] = p # record the pog name
			row = self.InsertItem( li ) 
			self.SetItemData( row, id ) # associate back to __poglistCopy

		self.SortItems( self.Sorter )
		
	def AddItem(self, pogname):
		"""
		Add a pogname to myself, then sort.
		"""
		li = wx.ListItem()
		li.SetImage(0)
		li.SetText(pogname)
		id = wx.NewId()
		self.__poglistCopy[id] = pogname 
		row = self.InsertItem(li)
		self.SetItemData( row, id )
		self.SortItems( self.Sorter )
		
	def RemoveItem(self, pogname):
		row = self.FindItem(-1, pogname)
		id = self.GetItemData(row)
		self.DeleteItem(row)
		del( PogChooser.__poglistCopy[id] ) # cull from our private store too.

	def ClearSelection(self):
		# removes all selections, even for multi-selections
		for x in range(self.GetSelectedItemCount()):
			self.Select(self.GetFirstSelected(), False)
		self.lastindexselected = -1
		
	def ChangeIcon(self):
		"""
		Change a single Pog's icon to installed/uninstalled.
		ONLY called from InstallPog and UninstallPog.
		"""
		T = fpsys.state.targetobject
		pn = T.name
		index = self.FindItem(0, pn) 
		if T.isInstalled(): n = 1
		else: n = 0
		self.SetItemImage(index, n) ## Found in wxWidgets documentation!
		
	def ClearLastIndex(self):
		"""
		We need to reset the lastindexselected so that a click on the 
		same item as last time will register. This is used in the Notebook
		when the page changes back to page 1, we want the user to
		be able to re-click the item that was clicked last time.
		"""	
		self.lastindexselected = -1
