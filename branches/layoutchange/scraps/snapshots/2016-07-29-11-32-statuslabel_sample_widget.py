# StatusLabel.py -- Multi-state label that changes on left- and right-click of mouse
import wx
 
myEVT_STATUS_LABEL_CHANGED = wx.NewEventType()
EVT_STATUS_LABEL_CHANGED = wx.PyEventBinder(myEVT_STATUS_LABEL_CHANGED, 1)
 
myEVT_LABEL_MOUSE_IN = wx.NewEventType()
EVT_LABEL_MOUSE_IN = wx.PyEventBinder(myEVT_LABEL_MOUSE_IN, 1)
 
myEVT_LABEL_MOUSE_OUT = wx.NewEventType()
EVT_LABEL_MOUSE_OUT = wx.PyEventBinder(myEVT_LABEL_MOUSE_OUT, 1)
 
 
from wx.lib.stattext import GenStaticText

class StatusLabelEvent(wx.PyCommandEvent):
		def __init__(self, evtType, id):
				wx.PyCommandEvent.__init__(self, evtType, id)
				self._state = -1
 
		def GetState(self):
				return self._state
# end class
 
class StatusLabel(GenStaticText):
		def __init__(self, *args, **kwds):
				GenStaticText.__init__(self, *args, **kwds)
				self.stateValues = []
				self.stateColors = []
				self.tooltips = []
				self.curState = -1
 
				self.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseIn, self)
				self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseOut, self)
				self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp, self)
				self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp, self)
		# end __init__
 
		def OnMouseIn(self, event):
				print "in here"
				self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
				evt = StatusLabelEvent(myEVT_LABEL_MOUSE_IN, self.GetId())
				evt._state = self.curState
				self.GetEventHandler().ProcessEvent(evt)
		# end OnMouseIn
 
		def OnMouseOut(self, event):
				self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
				evt = StatusLabelEvent(myEVT_LABEL_MOUSE_OUT, self.GetId())
				evt._state = self.curState
				self.GetEventHandler().ProcessEvent(evt)
		# end
 
		def OnLeftUp(self, event):
				self.curState += 1
				if self.curState >= len(self.stateValues):
						self.curState = 0
 
				self.SetState(self.curState)
 
				evt = StatusLabelEvent(myEVT_STATUS_LABEL_CHANGED, self.GetId())
				evt._state = self.curState
				self.GetEventHandler().ProcessEvent(evt)
		# end OnLeftUp
 
		def OnRightUp(self, event):
				self.curState -= 1
				if self.curState < 0:
						self.curState = len(self.stateValues) - 1
 
				self.SetState(self.curState)
				evt = StatusLabelEvent(myEVT_STATUS_LABEL_CHANGED, self.GetId())
				evt._state = self.curState
				self.GetEventHandler().ProcessEvent(evt)
		# end OnRightUp
 
		def SetTooltips(self, tips):
				self.tooltips = tips
		# end SetTooltips
 
		def GetState(self):
				return self.curState
		# end GetState
 
		def SetStateText(self, vals):
				self.stateValues = vals
		# end SetStateText
 
		def SetStateColors(self, colors):
				self.stateColors = colors
		# end SetStateColors
 
		def SetState(self, state):
				self.SetLabel(self.stateValues[state])
				if state - 1 < len(self.stateColors):
						try:
								self.SetForegroundColour(self.stateColors[state])
						except:
								self.SetForegroundColour(wx.Colour(0,0,0))
 
				if state - 1 < len(self.tooltips):
						try:
								self.SetToolTipString(self.tooltips[state])
						except:
								self.SetToolTipString('')
 
				self.Update()
				self.curState = state
		# end SetState
 
# end class
 
 
class TestAppFrame(wx.Frame):
		def __init__(self, *args, **kwds):
				kwds["style"] = wx.DEFAULT_FRAME_STYLE
				wx.Frame.__init__(self, *args, **kwds)
				self.panel = wx.Panel(self, -1)
 
				self.ctrl = StatusLabel(self.panel, -1, "MY LABEL")
				self.ctrl.SetStateText(["UNSIGNED","SIGNED", "IN PROCESS"])
				self.ctrl.SetStateColors( [wx.Colour(0,0,0), wx.Colour(0, 139, 0), wx.Colour(33, 70, 243) ] )
				self.ctrl.SetState(0)
 
				self.Bind(EVT_LABEL_MOUSE_IN, self.OnLabelIn, self.ctrl) 
				self.Bind(EVT_LABEL_MOUSE_OUT, self.OnLabelOut, self.ctrl) 
				self.Bind(EVT_STATUS_LABEL_CHANGED, self.OnStatusChange, self.ctrl) 
 
				self.__set_properties()
				self.__do_layout()
 
		def __set_properties(self):
				self.SetTitle("Testbed Framework")
				self.SetSize( (800, 600) )
				self.ctrl.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
 
		def __do_layout(self):
				sizer = wx.BoxSizer(wx.VERTICAL)
				sizer.Add(self.panel, 0, wx.ALL|wx.EXPAND, 0)
				self.SetSizer(sizer)
				sizer.Fit(self)
				self.Layout()
		# end __do_layout
 
		def OnLabelIn(self, event):
				print "OnLabelIn..."
 
		def OnLabelOut(self, event):
				print "OnLabelOut..."
 
		def OnStatusChange(self, event):
				print "State changed to %d" % event.GetState()
 
# end of class MyFrame
 
 
if __name__ == "__main__":
		app = wx.App(0)
		#wx.InitAllImageHandlers()
		frame_1 = TestAppFrame(None, -1, "")
		app.SetTopWindow(frame_1)
		frame_1.Show()
		app.MainLoop()
