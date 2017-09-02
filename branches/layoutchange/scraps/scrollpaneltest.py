import wx
import wx.lib.scrolledpanel as scrolled

class MyPanel(scrolled.ScrolledPanel):
		def __init__(self, parent):
				scrolled.ScrolledPanel.__init__(self, parent, style=wx.VSCROLL)
				self.SetBackgroundColour('#f8f8f8')
				self.sizer = wx.WrapSizer()
				self.SetupScrolling(scroll_x = False)
				self.parent = parent

				self.addButton(self.sizer , 10)
				self.SetSizer(self.sizer )
				self.Bind(wx.EVT_SIZE, self.onSize)

		def onSize(self, evt):
				size = self.GetSize()
				vsize = self.GetVirtualSize()
				self.SetVirtualSize((size[0], vsize[1]))

				evt.Skip()

		def addButton(self, sizer, num):
				for i in range(1, num):
						btn =wx.Button( self, wx.ID_ANY, "btn"+str(i), wx.DefaultPosition, wx.DefaultSize, 0 )
						sizer.Add(btn, 0, wx.ALL, 10)

if __name__=='__main__':
		app = wx.App(redirect=False)
		frame = wx.Frame(None)
		MyPanel(frame)
		frame.Show()
		app.MainLoop()
