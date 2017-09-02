#!/usr/bin/python

import wx
from wx.lib.stattext import GenStaticText


class Link(GenStaticText):

		def __init__(self, *args, **kw):
				super(Link, self).__init__(*args, **kw)
				self.parent = args[0]
				self.font1 = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD, True, 'Verdana')
				self.font2 = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD, False, 'Verdana')

				self.SetFont(self.font2)
				self.SetForegroundColour('#0000ff')

				self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvent)
				self.Bind(wx.EVT_MOTION, self.OnMouseEvent)
				self.Bind(wx.EVT_MOUSE_EVENTS, self.parent.OnMouseEvent, self)

		def SetUrl(self, url):

				self.url = url


		def OnMouseEvent(self, e):

				if e.Moving():

						self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
						self.SetFont(self.font1)

				elif e.LeftUp():

						print "goes to:", self.url
						wx.CallAfter(self.Foo, self)
						#self.parent.clickypoo(self)

				else:
						self.SetCursor(wx.NullCursor)
						self.SetFont(self.font2)
				print "e ends"
				e.Skip()

		def Foo(self,obj):
			print "call after for:", obj
			obj.Destroy()


from random import randint

class CPU(wx.Panel):
		def __init__(self, parent, id):
			wx.Panel.__init__(self, parent, id) #, size=(80, 110))

			self.range = None
			self.currpage = 1

			self.links = []

			self.parent = parent
			self.SetBackgroundColour('white')
			self.Bind(wx.EVT_PAINT, self.OnPaint)

			self.hbox = wx.BoxSizer(wx.HORIZONTAL)

			self.SetSizer(self.hbox)

			#lnk = Link(self, label='ZetCode', pos=(10, 60))
			#lnk.SetUrl('http://www.zetcode.com')

		def addPages(self, n):
			self.range = n
			for p in xrange(1,n):
				#self.links.append("link to %i" % p)
				lnk = Link(self, label=str(p), pos=(p*12,20))
				lnk.SetUrl(str(p))

		def OnMouseEvent(self,e):
			print e
			if e.LeftUp():
				print dir(e)
				L = e.GetEventObject()
				L.Hide()
				#L.Destroy()
			e.Skip()
			return
			c=self.GetChildren()[7]
			print type(c)
			self.RemoveChild(c)
			c.Destroy()
			del c
			#print self.sizer.DeleteWindows()

		def OnPaint(self, event):

				dc = wx.PaintDC(self)

				dc.SetDeviceOrigin(0, 100)
				dc.SetAxisOrientation(True, True)

				pos = randint(0,100) #self.parent.GetParent().GetParent().sel
				rect = pos / 5

				for i in range(1, 21):
						if i > rect:
								dc.SetBrush(wx.Brush('#075100'))
								dc.DrawRectangle(10, i*4, 30, 5)
								dc.DrawRectangle(41, i*4, 30, 5)
						else:
								dc.SetBrush(wx.Brush('#36ff27'))
								dc.DrawRectangle(10, i*4, 30, 5)
								dc.DrawRectangle(41, i*4, 30, 5)





class Example(wx.Frame):

		def __init__(self, *args, **kw):
				super(Example, self).__init__(*args, **kw)

				self.InitUI()

		def InitUI(self):

				cpu = CPU(self,-1)
				cpu.addPages(10)

				self.Centre()
				self.Show(True)


def main():
		ex = wx.App()
		Example(None)
		ex.MainLoop()


if __name__ == '__main__':
		main()
