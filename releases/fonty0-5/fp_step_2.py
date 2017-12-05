## Fonty Python Copyright (C) 2006-2017 Donn.C.Ingle
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

"""
Dec 2017
==
This is step 2 in the startup process. We get here from:
    fontypython
(Which does a Python 2 test.)
Next is step 3: fp_step_3.py

Dec 2007
==
This wraps 
    fp_step_3.py
and catches any segfaults that kill it.

These segfaults happen in PIL when certain bad fonts just 
break stuff. I can't catch them or stop them in any way - hence 
this wrapper.

A window displays the situation and gives the user some hope.
"""
if __name__=="__main__":
    print "Please run fontypython, not this file."
    raise SystemExit

import subprocess, sys, os


## find the directory from where THIS script 
## is actually being run.
root = __file__
if os.path.islink(root):
    root = os.path.realpath(root)
fontyroot = os.path.dirname(os.path.abspath(root))

import fontypythonmodules.i18n as i18n

## Get the dir to run this from:
#root = os.path.dirname(sys.argv[0]) # note:
# this returns /usr/bin when we run from an installed 
# version of fonty. 
# Since I am testing from my dev directory, and sometimes
# make a link in /usr/bin to fake things:
# (sudo ln -s `pwd`/fontypython /usr/bin/fontypython)
# I want the actual site-root where fontypythonmodules/ is
# so I will use fontyroot from above

##os.chdir( fontyroot ) # note:
# Not changing dir anymore because this makes relative
# directory stuff like:
# fontypython .
# not work properly. User should be able to open a view
# on the current directory.
# Thus:
# Point to the absolute path of the 'fp_step_3.py' script.
#
# Dec 2017
# ==
# Added "python" so fp_step_3.py need not have chmod +x
# which should illustrate that only 'fontypython' is the
# correct file to run.

# Also: Pass a flag to the next step to allow it to run.
# I am trying to dicourage running any other file than
# the main one.
c1 = [ "python", os.path.join(fontyroot,'fp_step_3.py'),'we_say_Ni' ]

## Append any args
for arg in sys.argv[1:]: c1.append( arg )

p1 = subprocess.call( c1 )

##TEST:
#p1=-11 # to test

## Nov 2017: Simpler plan:
if p1 >= 0:
    raise SystemExit

## This actually works!
import fontypythonmodules.fpsys as fpsys
import wx
import fontypythonmodules.fpwx as fpwx
import fontypythonmodules.strings as strings

class SegfaultDialog(wx.Dialog):
    """
    Dec 2007, Nov 2017: Moved into this file from dialogues.py
    Runs from the wrapper script (which runs start_fontypython) so that we
    can tell the user that there was a segfault and why.
    """
    def __init__(self, context, culprit):
        wx.Dialog.__init__(self, None, -1, _("Oh boy..."), pos = wx.DefaultPosition )
        
        fs = wx.FlexGridSizer(cols = 1, vgap = 4)

        labelHeading = fpwx.h1(self, _("Fonty Python, um ... crashed."))
        fs.Add(labelHeading, 0, wx.BOTTOM, border = 8 )

        if context == "SEGFAULT":
            segdir = os.path.dirname(culprit)
            sadStory = _("There's some problem with the font named below.\n" \
                         "You can do one of two things:\n" \
                         "1) Manually move this font somewhere else, or\n" \
                         "2) Use Fonty's command-line (-c) to mark bad fonts.\n" \
                         "   See below for help with this.\n" \
                         "After you've done these, run me again.")
            msg = _('The bad font might be:')
            cmd = "fontypython -c \"{}\"".format(segdir)
        elif context == "NO_LFBS_FILE":
            sadStory = _("There's no lastFontBeforeSegfault file; I can't really help.\n" \
                         "Look at the error (below) for clues." )
            msg = _('The error was:')

        sadStory = fpwx.para( self, sadStory )
        fs.Add(sadStory,  0, wx.BOTTOM, border = 8 )

        msg = fpwx.label( self, msg )
        culprit = wx.TextCtrl(self, -1, culprit, size=(0,80),style = wx.TE_READONLY | wx.TE_MULTILINE )
        fs.Add(msg, 0)
        fs.Add(culprit, 1, wx.EXPAND  )

        if context == "SEGFAULT":
            msg1 = fpwx.label(self,_("The command line to seek and mark bad fonts is:"))
            msgs = fpwx.small_label(self,_("(Copy the text; open a console; paste and press enter.)"))
            msg2 = wx.TextCtrl(self,-1,cmd, size=(0,80), style = wx.TE_READONLY | wx.TE_MULTILINE )
            fs.Add(msg1, 0, wx.TOP, border=8 )
            fs.Add(msg2, 1, wx.EXPAND)
            fs.Add(msgs, 0 )

        tickettxt = fpwx.para(self, _("You can get help by opening a ticket on:"))
        ticketurl = wx.TextCtrl(self, -1, strings.ticket_url, size=(0,40),style = wx.TE_READONLY)
        fs.Add(tickettxt, 0, wx.TOP, border=8 )
        fs.Add(ticketurl, 1, wx.EXPAND )
        
        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        fs.Add(btn, 0, wx.ALIGN_CENTER_VERTICAL| wx.ALIGN_RIGHT | wx.TOP, border = 15 )

        b = wx.BoxSizer( wx.HORIZONTAL )
        b.Add( fs, 0, wx.ALL, border=10 )
        self.SetSizer( b )
        b.Fit(self) 


## Start the App and then show the Segfault dialog.
class App(wx.App):
    def OnInit(self):
        culprit = None
        ## A wide net. Not gonna split hairs.
        try:
            paf = os.path.join( fpsys.iPC.appPath(),"lastFontBeforeSegfault")
            f = open( paf, "r" )
            culprit = f.readline()[:-1]
            f.close()
            if not culprit:# odball situation. file may have been empty:
                raise IOError # force error into except
            else:
                context="SEGFAULT"
        except Exception as e:
            culprit = "{}".format(e)
            context="NO_LFBS_FILE"

        fpwx.setup_fonts_and_colours()
        dlg = SegfaultDialog( context, culprit )
        val = dlg.ShowModal()
        dlg.Destroy()
        return True
app = App(0)
app.MainLoop()
