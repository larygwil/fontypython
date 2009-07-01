"""
Working on this - May 2009

	## in class Fitmap.__init__
	self.Bind(wx.EVT_RIGHT_UP, self.__onRightClick)

	## In class Fitmap
	def __onRightClick(self, event):
		fitmap =  event.GetEventObject()
		win = dialogues.PopupInfo(self, -1, '', fitmap)
		win.CentreOnScreen()
		win.Show()
"""


