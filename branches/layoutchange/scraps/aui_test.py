import	wx
import	wx.aui

"""Aug	2017
http://xoomer.virgilio.it/infinity77/wxPython/aui/wx.aui.html
A	test	to	use	the	aui	module	to	handle	the	panels	and	splits.	Works	ok.
The	panel	can	bind	to	EVT_SIZE	and	this	redraw."""

class	DemoFontView(wx.Panel):
	def	__init__(self,	*args,	**kwargs):
		wx.Panel.__init__(self,	*args,	**kwargs)
		self.Bind(wx.EVT_SIZE,	self.OnResize)

	def	OnResize(self,	*args,	**kwargs):
		print	"Resizing"

	def	Layout(self):
		print	"Layout"

class	MyFrame(wx.Frame):
	def	__init__(self,	*args,	**kwargs):
		wx.Frame.__init__(self,	*args,	**kwargs)

		self._mgr	=	wx.aui.AuiManager(self, wx.aui.AUI_MGR_DEFAULT | wx.aui.AUI_MGR_LIVE_RESIZE)

		#leftpanel	=	wx.Panel(self,	-1)#,	size	=	(200,	150))
		#rightpanel	=	wx.Panel(self,	-1)#,	size	=	(200,	150))
		#bottompanel	=	wx.Panel(self,	-1)#,	size	=	(200,	150))

		#self.mgr.AddPane(leftpanel,	wx.aui.AuiPaneInfo().Bottom(),	caption="leftpanel")
		#self.mgr.AddPane(rightpanel,	wx.BOTTOM,	caption="rightpanel")

		#self.mgr.AddPane(leftpanel,	wx.aui.AuiPaneInfo().Bottom())
		#self.mgr.AddPane(rightpanel,	wx.aui.AuiPaneInfo().Left().Layer(1))
		#self.mgr.AddPane(bottompanel,	wx.aui.AuiPaneInfo().Center().Layer(2))

		#	create	several	text	controls
		text1	=	wx.TextCtrl(self,	-1,	'Pane	1	-	source',
							wx.DefaultPosition,	wx.Size(200,150),
							wx.NO_BORDER	|	wx.TE_MULTILINE)

		text2	=	wx.TextCtrl(self,	-1,	'Pane	2	-	target',
							wx.DefaultPosition,	wx.Size(200,150),
							wx.NO_BORDER	|	wx.TE_MULTILINE)

		p	=	DemoFontView(self,-1)

		text3	=	wx.TextCtrl(p,	-1,	'fontview',
							wx.DefaultPosition,	wx.Size(200,150),
							wx.NO_BORDER	|	wx.TE_MULTILINE)

		#	add	the	panes	to	the	manager
		self._mgr.AddPane(text1,	wx.LEFT,	'Pane1')
		self._mgr.AddPane(p,	wx.CENTER	)	#No	caption	means	no	drag/close
		self._mgr.AddPane(text2,	wx.RIGHT,	"Pane3")

		self._mgr.Update()

		self.Bind(wx.EVT_CLOSE,	self.OnClose)

	def	OnClose(self,	event):
		#	deinitialize	the	frame	manager
		self._mgr.UnInit()
		#	delete	the	frame
		self.Destroy()

# Code for debugging:
##http://wiki.wxpython.org/Widget%20Inspection%20Tool
## Use ctrl+alt+i to open it.
import wx.lib.mixins.inspection
## Start the main frame and then show it.
class MyApp(wx.App , wx.lib.mixins.inspection.InspectionMixin) :
#class	MyApp(wx.App):
	def	OnInit(self):
		self.Init() #init the inspector

		frame	=	MyFrame(None,	-1,	'07_wxaui.py')
		frame.Show()
		self.SetTopWindow(frame)
		return	1

if	__name__	==	"__main__":
	app	=	MyApp(0)
	app.MainLoop()
