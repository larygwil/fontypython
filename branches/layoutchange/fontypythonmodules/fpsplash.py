# --------------------------------------------------------------------------- #
# Based on the:
# ADVANCEDSPLASH Control wxPython IMPLEMENTATION
# Python Code By:
#
# Andrea Gavana, @ 10 Oct 2005
# andrea.gavana@gmail.com
# andrea.gavana@maerskoil.com
# --------------------------------------------------------------------------- #

## Fonty Python Copyright (C) 2017 Donn.C.Ingle
## Contact: donn.ingle@gmail.com - I hope this email lasts.
##
## This file is part of Fonty Python.
## Fonty Python is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Fonty Python is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Fonty Python.  If not, see <http://www.gnu.org/licenses/>.

import wx
import fpsys
import os

class FPS(wx.Frame):
    """
    Much simpler class to address Fonty's use.
    """
    def __init__(self, fn, timeout):
        pos=wx.DefaultPosition
        size=wx.DefaultSize
        style=wx.FRAME_NO_TASKBAR | wx.FRAME_SHAPED | wx.STAY_ON_TOP

        wx.Frame.__init__(self, None, -1, "", pos, size, style)

        img = wx.Image( os.path.join(fpsys.mythingsdir, fn + '.png') )
        img.ConvertAlphaToMask()
        self.bmp = wx.BitmapFromImage(img)

        # Calculate the shape
        self.reg = wx.RegionFromBitmap(self.bmp)

        # works on wx.Platform == "__WXGTK__"
        self.Bind(wx.EVT_WINDOW_CREATE, self.SetSplashShape)

        w = self.bmp.GetWidth() + 1
        h = self.bmp.GetHeight() + 1

        # Set frame to the bitmap size
        self.SetClientSize((w, h))

        self.CenterOnScreen()

        # Starts timer
        self._splashtimer = wx.PyTimer(self.OnNotify)
        self._splashtimer.Start(timeout)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        self.Show()

    def SetSplashShape(self, event=None):
        self.SetShape(self.reg)
        if event is not None:
            event.Skip()

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        # Draw over frame
        dc.DrawBitmap(self.bmp, 0, 0, True)

    def OnNotify(self):
        self.Close()

    def OnCloseWindow(self, event):
        if hasattr(self, "_splashtimer"):
            self._splashtimer.Stop()
            del self._splashtimer

        self.Destroy()
