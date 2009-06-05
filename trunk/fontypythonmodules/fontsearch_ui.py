"""
Working on this - May 2009
Michael Hoeft's idea for PANOSE and company 
His implementation was messy and unfinished. But the idea is nice.
"""

import wx.lib.foldpanelbar as fpb

class SearchControl(wx.Panel):
	def __init__(self, parent):
		"""Search tab on the left part notebook."""
		wx.Panel.__init__(self, parent, style=wx.NO_BORDER)
		self._vsizer = wx.BoxSizer(wx.VERTICAL)
		self._fpb = fpb.FoldPanelBar(self, extraStyle=fpb.FPB_SINGLE_FOLD)
		self._vsizer.Add(self._fpb, 1, wx.EXPAND)

		# Controls for Name Record Search
		self._nr = self._fpb.AddFoldPanel(_("Name Records"), collapsed=True)
		self._fpb.AddFoldPanelWindow(self._nr, wx.StaticText(self._nr, -1, _("Search Name Records")))
		panel0 = wx.Panel(self._nr, style=wx.NO_BORDER)
		grid0 = wx.GridSizer(1,2,3,3)
		panel0.SetSizer(grid0)
		self._txtNR  = wx.TextCtrl(self._nr)
		self._buttNR = wx.Button(panel0, 0, _("Compile"), style=1)
		grid0.Add(self._buttNR,3, wx.EXPAND)
		self._helpNR = wx.Button(panel0, wx.ID_HELP, style=1)
		self._helpNR.Bind(wx.EVT_BUTTON, self._HelpNR)
		grid0.Add(self._helpNR, 1, wx.ALIGN_RIGHT)
		panel0.SetSize(grid0.GetMinSize())
		grid0.Layout()
		self._fpb.AddFoldPanelWindow(self._nr, self._txtNR, fpb.FPB_ALIGN_WIDTH)
		self._fpb.AddFoldPanelWindow(self._nr, panel0, fpb.FPB_ALIGN_WIDTH)

		# Controls for PANOSE Search
		self._pn = self._fpb.AddFoldPanel(_("PANOSE Classification"), collapsed=False)
		self._fpb.AddFoldPanelWindow(self._pn, wx.StaticText(self._pn, -1, _("Search PANOSE")))
		panel1 = wx.Panel(self._pn, style=wx.NO_BORDER)
		grid1 = wx.GridSizer(1,2,3,3)
		panel1.SetSizer(grid1)
		self._txtPAN  = wx.TextCtrl(self._pn)
		self._buttPAN = wx.Button(panel1, 0, _("Compile"), style=1)
		grid1.Add(self._buttPAN,3, wx.EXPAND)
		self._helpPAN = wx.Button(panel1, wx.ID_HELP, style=1)
		self._helpPAN.Bind(wx.EVT_BUTTON, self._HelpPAN)
		grid1.Add(self._helpPAN, 1, wx.ALIGN_RIGHT)
		panel1.SetSize(grid1.GetMinSize())
		grid1.Layout()
		self._fpb.AddFoldPanelWindow(self._pn, self._txtPAN, fpb.FPB_ALIGN_WIDTH)
		self._fpb.AddFoldPanelWindow(self._pn, panel1, fpb.FPB_ALIGN_WIDTH)

		# Controls for Appereance Search
		self._ap = self._fpb.AddFoldPanel(_("Appereance"), collapsed=True)
		self._fpb.AddFoldPanelWindow(self._ap, wx.StaticText(self._ap, -1, _("Search Appereance")))

		# Start the search in 4 different ways
		buttGrid = wx.GridSizer(4,1,0,0)
		buttActualPog = wx.Button(self, 0, _("Search actual Pog"))
		buttActualPog.Bind(wx.EVT_BUTTON, self._startSearch)
		buttAllPogs = wx.Button(self, 1, _("Search all Pogs"))
		buttAllPogs.Bind(wx.EVT_BUTTON, self._startSearch)
		buttActualFolder = wx.Button(self, 2, _("Search actual Folder"))
		buttActualFolder.Bind(wx.EVT_BUTTON, self._startSearch)
		buttFolder = wx.Button(self, 3, _("Search selected Folder"))
		buttFolder.Bind(wx.EVT_BUTTON, self._startSearch)
		buttGrid.AddMany([(buttActualPog, 1, wx.EXPAND),
						 (buttAllPogs  , 1, wx.EXPAND),
						 (buttActualFolder , 1, wx.EXPAND),
						 (buttFolder , 1, wx.EXPAND)])

		self._vsizer.Add(buttGrid, 0, wx.ALIGN_BOTTOM|wx.EXPAND)
		self.SetSizer(self._vsizer)
		self._vsizer.Layout()
		self.SetSize(self._vsizer.GetMinSize())

	def _HelpNR(self, event):
		dlg = wx.MessageDialog(None, strings.helpNR, _("Name Records"), wx.OK)
		dlg.ShowModal()

	def _HelpPAN(self, event):
		dlg = wx.MessageDialog(None, strings.helpPAN, _("PANOSE Classification"), wx.OK)
		dlg.ShowModal()

	def _startSearch(self, event):
		clime = event.GetEventObject().GetId()
		n = [x for x in range(3) if self._fpb.GetFoldPanel(x).IsExpanded()]
		pattern = "NPA"[n[0]]
		if clime == 3:
			dlg = wx.DirDialog(None)
			dlg.ShowModal()
			print dlg.GetPath()
			dlg.Destroy()
		dlg = wx.ProgressDialog(_("Searching..."), str(clime) + " " + pattern, parent = app.GetTopWindow(),
								style=wx.PD_APP_MODAL|wx.PD_CAN_ABORT|wx.PD_REMAINING_TIME|wx.PD_SMOOTH)
		for x in range(101):
			dlg.Update(x)

