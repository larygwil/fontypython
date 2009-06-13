import wx, os

## Setup wxPython to access translations : enables the stock buttons.
langid = wx.LANGUAGE_DEFAULT # Picks this up from $LANG
mylocale = wx.Locale( langid )


from pubsub import *
from wxgui import ps

from gui_PogChooser import *

import fpsys # Global objects
import fontyfilter
import fontybugs


class DirControl(wx.GenericDirCtrl) :
	"""
	The Directory tree view.
	"""
	def __init__(self, parent):
		if fpsys.state.viewpattern == "F": 
			startdir = fpsys.state.viewobject.path
		else: 
			##Let's get it from the config object
			lastdir = fpsys.config.lastdir
			
			if os.path.exists(lastdir):
				startdir = lastdir
			else:
				startdir = os.environ['HOME']
		wx.GenericDirCtrl.__init__(self, parent, -1, dir = startdir, style=wx.DIRCTRL_DIR_ONLY)

		## NOTE: The click event is bound in the Notebook.

class NoteBook(wx.Notebook):
	"""
	Used in the left part of the splitter in mainframe.
	Has two tabs - Folders and Pogs
	THIS IS THE VIEW or SOURCE of fonts.	
	"""
	def __init__(self, parent):
		wx.Notebook.__init__(self, parent)
		self.imlist = wx.ImageList(16, 16)
		
		pan1 = wx.Panel(self)

		## THE DIR CONTROL
		self.dircontrol = DirControl(pan1) 
		self.recurseFolders = wx.CheckBox(pan1, -1, _("Include sub-folders."))
		self.recurseFolders.SetValue( fpsys.config.recurseFolders )
		self.Bind(wx.EVT_CHECKBOX, self.__onDirCtrlClick, self.recurseFolders) #click on check box same as click on folder item.

		box = wx.BoxSizer(wx.VERTICAL) 
		box.Add( self.recurseFolders,0,wx.EXPAND )
		box.Add( self.dircontrol,1, wx.EXPAND ) 
		pan1.SetSizer(box) 
		box.Layout() 

		self.pogindexselected = 0
		
		pan2 = wx.Panel(self) 
		
		page = 0
		s = None
		if fpsys.state.viewpattern  == "P": 
			s = fpsys.state.viewobject.name
			if s == "EMPTY": s= None #Very first run, the view will be an EMPTY object.
			page = 1
		self.ctrlPogSource = PogChooser(pan2, whoami="SOURCEPOG", select = s)
		
		ps.sub(source_pog_has_been_selected, self.OnViewPogClick) ##DND: class NoteBook
		ps.sub(select_no_view_pog, self.SelectNoView) ##DND: class NoteBook
		ps.sub( add_pog_item_to_source, self.AddItem ) #DND: class NoteBook
		ps.sub( remove_pog_item_from_source, self.RemoveItem ) #DND: class NoteBook

		self.tree = self.dircontrol.GetTreeCtrl()
		
		## Dud tree events, causing bad behaviour:
		## EVT_LIST_ITEM_SELECTED
		## EVT_LEFT_UP
		
		## Bind to another event solve the problem of EVT_LEFT_UP firing when the little
		## open-branch/tree arrow was pressed.
		## 5.3.2009 Michael Hoeft
		self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.__onDirCtrlClick) 	

		self.tree.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

		box2 = wx.BoxSizer(wx.HORIZONTAL) 
		box2.Add(self.ctrlPogSource,1,wx.EXPAND) 
		pan2.SetSizer(box2) 
		box2.Layout() 
		
		self.AddPage(pan1, _("Folders"))
		self.AddPage(pan2, _("Pogs")) 
		
		source_pog_icon = self.imlist.Add\
		(wx.Bitmap(fpsys.mythingsdir + "/icon_source_pog_16x16.png",wx.BITMAP_TYPE_PNG))

		target_pog_icon = self.imlist.Add\
		(wx.Bitmap(fpsys.mythingsdir + "/icon_source_folder_16x16.png",wx.BITMAP_TYPE_PNG))
		
		self.AssignImageList(self.imlist)
		self.SetPageImage(1, source_pog_icon)
		self.SetPageImage(0, target_pog_icon)
		
		self.SetSelection(page)
	
		self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.__onPageChanged) # Bind page changed event
		

	def __onPageChanged(self, e):
		self.ctrlPogSource.ClearLastIndex()
		if self.GetSelection() == 0: # The dircontrol
			## I want to force the dir control to clear the selection.
			## Reason: When you return to this control (from Pog page), the selection
			## from last visit is still there. Clicking on it again does NOT UPDATE
			## the font view. This is wierd. So, clearing the selection makes this moot.
			self.tree.UnselectAll() # Found this method in the wxpython book.

	## ------- JUNE 2009 ------ BEGINS

	def OnContextMenu(self, event):
		# only do this part the first time so the events are only bound once
		if not hasattr(self, "popupID1"):
			self.popupID1 = wx.NewId()
			self.popupID2 = wx.NewId()

			self.Bind(wx.EVT_MENU, self.OnPopupOne, id=self.popupID1)
			self.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupID2)

		# make a menu
		menu = wx.Menu()
		# Show how to put an icon in the menu
		#item = wx.MenuItem(menu, self.popupID1,"One")
		#bmp = images.getSmilesBitmap()
		#item.SetBitmap(bmp)
		#menu.AppendItem(item)
		# add some other items
		menu.Append(self.popupID1, _("Add fonts in this folder to a Pog.") )
		menu.Append(self.popupID2, _("Add fonts in this folder and sub-folders to a Pog.") )

		# Popup the menu.  If an item is selected then its handler
		# will be called before PopupMenu returns.
		self.PopupMenu(menu)
		menu.Destroy()

	def OnPopupOne(self, event):
		print "\n"

	def OnPopupTwo(self, event):
		print "Popup one\n"

	## -------------- JUNE 2009 ----- ENDS

	def __onDirCtrlClick(self, e):
		wx.BeginBusyCursor() #Thanks to Suzuki Alex on the wxpython list!
		p = self.dircontrol.GetPath()
		try:
			fpsys.instantiateViewFolder(p,self.recurseFolders.GetValue() )
			fpsys.config.lastdir = p
		except fontybugs.FolderHasNoFonts, e:
			pass # update_font_view handles this with a std message.
		
		ps.pub(reset_to_page_one)# reset before updating!		  
		ps.pub(update_font_view)
		
		wx.EndBusyCursor()
		wx.CallAfter( self.SetFocus )

	def OnViewPogClick(self, args):
		"""
		args[0] pogname, args[1] is pognochange
		"""
		## Check pognochange, it means this is the same pog as last time.
		if args[1]: return 
		
		## instantiateViewPog calls pog.genList which bubbles:
		## PogInvalid
		## BUT - this error only makes sense from the
		## cli pov. By the time the gui is running, that
		## pog has been renamed .badpog and therefore 
		## won't even appear in the list. So, don't bother
		## catching it.
		fpsys.instantiateViewPog(args[0])

		if fpsys.state.samepogs: #forbid same pogs selection
			ps.pub(clear_targetpog_selection)
		else:
			ps.pub(reset_to_page_one)
		ps.pub(update_font_view)
	
	def AddItem(self, pogname):
		self.ctrlPogSource.AddItem(pogname[0]) #[0] bit is because pogname is a tuple from pubsub.

	def RemoveItem(self, pogname):
		self.ctrlPogSource.RemoveItem(pogname[0])
		
	def SelectNoView(self):
		## Purpose: To select no viewobject and clear view pog list selections
		## Called when a TARGET item is clicked AND samepogs it True
		wx.BeginBusyCursor()
		self.ctrlPogSource.ClearSelection()
		fpsys.SetViewPogToEmpty()
		wx.EndBusyCursor()

