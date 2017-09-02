
#!/usr/bin/python


import wx
from wx.lib.stattext import GenStaticText


				
class Link(GenStaticText):
					 
		def __init__(self, *args, **kw):
				super(Link, self).__init__(*args, **kw)				 

				self.font1 = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD, True, 'Verdana')
				self.font2 = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD, False, 'Verdana')

				self.SetFont(self.font2)
				self.SetForegroundColour('#0000ff')

				self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvent)
				self.Bind(wx.EVT_MOTION, self.OnMouseEvent)
				
		def SetUrl(self, url):
				
				self.url = url


		def OnMouseEvent(self, e):
				
				if e.Moving():
						
						self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
						self.SetFont(self.font1)

				elif e.LeftUp():
						
						print "goes to:", self.url

				else:
						self.SetCursor(wx.NullCursor)
						self.SetFont(self.font2)

				e.Skip()


class Example(wx.Frame):
					 
		def __init__(self, *args, **kw):
				super(Example, self).__init__(*args, **kw) 
				
				self.InitUI()
				
		def InitUI(self):		

				panel = wx.Panel(self)
				lnk = Link(panel, label='ZetCode', pos=(10, 60))
				lnk.SetUrl('http://www.zetcode.com')
				
				motto = GenStaticText(panel, label='Knowledge only matters', pos=(10, 30))
				motto.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD, False, 'Verdana'))

				self.SetSize((220, 150))
				self.SetTitle('A Hyperlink')
				self.Centre()
				self.Show(True)


def main():
		
		ex = wx.App()
		Example(None)
		ex.MainLoop()		


if __name__ == '__main__':
		main()	 
