import fontypythonmodules.i18n as i18n

import sys, os, locale
##import pathcontrol
import strings
import fpsys # Global objects
import fontybugs
import fontcontrol
import fpversion

## Now, bring in all those big modules
import wx
import wx.lib.scrolledpanel
import wx.lib.statbmp

## Setup wxPython to access translations : enables the stock buttons.
langid = wx.LANGUAGE_DEFAULT # Picks this up from $LANG
mylocale = wx.Locale( langid )

## Fetch my own pubsub stuff
##from pubsub import *
##ps = CPubsub()

## Fetch the dialogue classes *About, Settings, Help, etc.*
import dialogues


## Start the main frame and then show it.
class App(wx.App) :
	def OnInit(self) :


		dlg = dialogues.DialogCheckFonts( None, "/home/donn" )
		val = dlg.ShowModal()
		dlg.Destroy()	

		return True
		
## app
app = App(0) 
		
## start 
app.MainLoop() 

