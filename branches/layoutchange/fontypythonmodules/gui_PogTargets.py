##	Fonty Python Copyright (C) 2017 Donn.C.Ingle
##	Contact: donn.ingle@gmail.com - I hope this email lasts.
##
##	This file is part of Fonty Python.
##	Fonty Python is free software: you can redistribute it and/or modify
##	it under the terms of the GNU General Public License as published by
##	the Free Software Foundation, either version 3 of the License, or
##	(at your option) any later version.
##
##	Fonty Python is distributed in the hope that it will be useful,
##	but WITHOUT ANY WARRANTY; without even the implied warranty of
##	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##	GNU General Public License for more details.
##
##	You should have received a copy of the GNU General Public License
##	along with Fonty Python.  If not, see <http://www.gnu.org/licenses/>.

import wx

## June 25th 2016
## Remarking these two lines because they are causing a segfault:
##  ../src/common/stdpbase.cpp(62): assert "traits" failed in Get(): 
##  create wxApp before calling this
##  Segmentation fault (core dumped)
##
##  I do not know how to test or fix this, hence simply removing it.
##  AFAICT, stock buttons will be in the system language.
##
## Setup wxPython to access translations : enables the stock buttons.
##langid = wx.LANGUAGE_DEFAULT # Picks this up from $LANG
##mylocale = wx.Locale( langid )

from pubsub import *
from wxgui import ps

from gui_PogChooser import *

import fpsys # Global objects
import fontyfilter
import fontybugs

## Fetch the dialogue classes - used for zip dir dialog.
import dialogues
import fpwx
from wxgui import id_zip_pog_button

class TargetPogChooser(wx.Panel):
    """
    Far right-hand side control. Chooses target pogs. Houses control buttons.
    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id = -1)

        target_icon = fpwx.icon( self, 'icon_target' )
        target_label = fpwx.label(self, _("Target Pogs") )

        s = None
        if fpsys.state.targetpattern == "P":
            s = fpsys.state.targetobject.name

        ## The actual list control
        self.pogTargetlist = PogChooser(self, whoami="TARGETPOG", select = s)

        ## Subscriptions:
        ps.sub(target_pog_has_been_selected, self.OnPogTargetClick) ##DND: class TargetPogChooser
        ps.sub(clear_targetpog_selection, self.SelectNoTargetPog) ##DND: class TargetPogChooser

        ## The "no pog" button
        self.idnone = wx.NewId()
        self.buttNoPog = wx.Button(self, label = _("Clear selection"), id = self.idnone)

        self.buttNoPog.SetToolTipString(_("Deselects any chosen Pogs."))
        ## The buttons under the pog list
        ## Giving them all id numbers so my single handler can tell them apart.
        self.idnew = wx.NewId()
        self.idinstall = wx.NewId()
        self.iduninstall = wx.NewId()
        self.iddelete = wx.NewId()
        #Sept 2009
        self.idzip = id_zip_pog_button #Created in wxgui

        self.buttNew = wx.Button(self, label = _("New Pog"), id = self.idnew )
        self.buttNew.SetToolTipString(_("Creates a new, empty Pog"))

        self.buttInstall = wx.Button(self, label = _("Install Pog"), id = self.idinstall )
        self.buttInstall.SetToolTipString(_("Installs all selected Pogs.\nHold SHIFT or CTRL as you select Pogs, if you wish to select many at once."))

        self.buttUninstall = wx.Button(self, label = _("Uninstall Pog"), id = self.iduninstall )
        self.buttUninstall.SetToolTipString(_("Uninstalls all selected Pogs.\nHold SHIFT or CTRL as you select Pogs, if you wish to select many at once."))

        self.buttDelete = wx.Button(self, label = _("Delete Pog") , id = self.iddelete)
        self.buttDelete.SetToolTipString(_("Deletes the selected Pog(s)"))

        self.buttZip = wx.Button(self, label = _("Zip Pog(s)") , id = self.idzip)
        self.buttZip.SetToolTipString(_("Save a zip file of the selected Pogs"))
        self.list_of_pogs_to_zip = None # will be used in wxgui


        mainvs = wx.BoxSizer(wx.VERTICAL)
        self.iconandtext = wx.BoxSizer(wx.HORIZONTAL)
        self.iconandtext.Add(target_icon, 0, wx.TOP | wx.BOTTOM | wx.LEFT, border = 4)
        self.iconandtext.Add(target_label, 1, wx.LEFT | wx.BOTTOM | wx.ALIGN_BOTTOM, border = 4)
        mainvs.Add(self.iconandtext, 0, wx.EXPAND)

        mainvs.Add(self.pogTargetlist, 1, wx.EXPAND)

        ## The buttons under the target:
        gs = wx.GridSizer(3,2)
        gs.AddMany( [
        (self.buttNoPog, 1, wx.EXPAND ),
        (self.buttInstall, 1, wx.EXPAND),
        (self.buttUninstall, 1, wx.EXPAND),
        (self.buttNew, 1, wx.EXPAND),
        (self.buttDelete, 1, wx.EXPAND),
        (self.buttZip, 1, wx.EXPAND)
        ])

        mainvs.Add(gs, 0, wx.EXPAND)

        self.SetSizer(mainvs)


        ## Bind the events:
        e=wx.EVT_BUTTON # was wx.EVT_LEFT_UP
        self.buttNoPog.Bind(e, self.multiClick)
        self.buttNew.Bind(e, self.multiClick)
        self.buttInstall.Bind(e, self.multiClick)
        self.buttUninstall.Bind(e, self.multiClick)
        self.buttDelete.Bind(e, self.multiClick)
        self.buttZip.Bind(e, self.multiClick)

        self.toggleButtons()

    ## Catch all the button clicks on the control.
    def multiClick(self, e):
        ## NEW
        if e.GetId() == self.idnew:
            ## New Pog button pressed
            dlg = wx.TextEntryDialog(
                    self, _("Enter a name for the new Pog"),
                    _("New Pog"), _("Fonty Python"))
            dlg.SetValue("")
            if dlg.ShowModal() == wx.ID_OK:
                nam = dlg.GetValue()
                if nam == "":
                    ps.pub( show_message, _("A Pog with no name won't be created, however it was a good try!") )
                ## Is it unique?
                elif fpsys.isPog(nam):
                    ## Nope, it's there already
                    ps.pub(show_message, _("%s already exists.") % nam)
                else:
                    ## We have a winner.
                    ## Make a pog object and then write it,
                    ipog = fontcontrol.Pog(nam)
                    try:
                        ipog.write()
                    except fontybugs.PogWriteError, e:
                        ps.pub(show_error_and_abort, unicode( e ))
                    del ipog
                    ## Now put it into the list
                    self.pogTargetlist.AddItem(nam)
                    #ps.pub(add_item_to_notebook, nam)
                    ps.pub( add_pog_item_to_source, nam )
                    ps.pub( update_font_view )
            dlg.Destroy()
            return

        ## A list of multiple-selected pog names:
        tl = self.pogTargetlist
        multipogs=[ tl.GetItemText(i) for i in xrange(tl.GetItemCount()) if tl.IsSelected(i)]

        ## DELETE
        if e.GetId() == self.iddelete:
            ## Selected Pog(s) to be deleted:
            tokill = multipogs
            iPogsToKill = []
            ##Is any one of those installed?
            allok=True
            for p in tokill:
                ## Michael Hoeft tested pog delete and noticed the bug. Thanks.
                ## Fixed Oct 2009
                iPog = fontcontrol.Pog(p)
                if iPog.isInstalled():
                    ps.pub( show_error, _("One or more selected Pogs is installed, fix your selection and try again.") )
                    allok=False
                    break
                iPogsToKill.append( iPog )

            if allok:
                ## Build a string for reporting in the dialog
                if len(tokill) > 1:
                    pogname=""
                    for f in tokill[:-1]:
                        pogname += u"%s," % f
                    pogname += tokill[-1] #We want "remove blah,bloop,zoom, are you sure?"
                else:
                    pogname=tokill[0]

                dlg = wx.MessageDialog(self, _("Remove %s, are you sure?") % pogname,
                    _("Are you sure?"), wx.YES_NO | wx.ICON_INFORMATION	)
                if dlg.ShowModal() == wx.ID_YES:
                    ## Let's do them in:
                    for victim in iPogsToKill: #tokill:
                        #fpsys.instantiateTargetPog(victim) #Makes the fpsys.state.targetobject
                        ## Now kill the file on disk:
                        try:
                            victim.delete()
                            #fpsys.state.targetobject.delete()
                        except fontybugs.PogCannotDelete, e:
                            ps.pub(show_error, unicode( e ))
                            return
                        ## Remove from the lists:
                        self.pogTargetlist.RemoveItem(victim.name)
                        ps.pub( remove_pog_item_from_source, victim.name)

                        ## What if it was ALSO our view object?
                        if fpsys.state.viewobject.label() == victim.name:
                            ## It was! We must declare it Empty.
                            fpsys.SetViewPogToEmpty()

                    ## Now re-draw things
                    ps.pub(update_font_view)
                    dlg.Destroy()

                    ## Select no pog.
                    self.SelectNoTargetPog()
            return

        ## NO POG pressed
        if e.GetId() == self.idnone:
            ## Select No Pog button pressed
            if fpsys.state.targetobject is None: return #Already done.
            self.SelectNoTargetPog()
            ps.pub(update_font_view)
            return #No need to tell mainframe about this.



        ## Prepare for Install/Uninstall POG

        ## install or uninstall all selected pogs - caters for multiple pog selections
        ## the instantiateTargetPog must be called on each pog-name in the list
        ## to setup the globals in fpsys. This is new from my previous one-selection only
        ## code which assumed that instantiateTargetPog had been called already (when pog
        ## was selected by the mouse)

        ## Install
        if e.GetId() == self.idinstall:
            wx.BeginBusyCursor()
            for p in multipogs:
                fpsys.instantiateTargetPog(p) # sets up fpsys.state.targetobject

                ok=True
                try:
                    fpsys.state.targetobject.install()
                except (fontybugs.PogSomeFontsDidNotInstall), er:
                    ## Show a warning, but continue.
                    ps.pub( show_error, unicode(er) )
                except (fontybugs.PogEmpty, fontybugs.PogAllFontsFailedToInstall), er:
                    ## Either Pog is empty, or
                    ## not a single font in this pog actually installed.
                    ## It has already been flagged as NOT INSTALLED
                    ps.pub( show_error, unicode(er) )
                    ok=False
                except (fontybugs.NoFontsDir), er:
                    #import pdb; pdb.set_trace()
                    ps.pub( show_error, unicode(er) )
                    ok=False

                if ok:
                    ## Update GUI

                    ## July 2016
                    ## =========
                    ## Added this test to sync view and target
                    ## objects IF they happen to be the samePog
                    if fpsys.state.samepogs:
                        # We installed RHS, so need to set that in RHS
                        # which is a sep object.
                        fpsys.state.viewobject.setInstalledFlag(True)
                    ps.pub( change_pog_icon ) #Causes TWO calls to update BOTH choosers.
                    self.toggleButtons()
                    ps.pub( update_font_view )

            wx.EndBusyCursor()

        ## Uninstall
        if e.GetId() == self.iduninstall:
            wx.BeginBusyCursor()
            for p in multipogs:
                fpsys.instantiateTargetPog(p)

                ok=True
                try:
                    fpsys.state.targetobject.uninstall()
                except (fontybugs.PogEmpty,
                                fontybugs.PogNotInstalled,
                                fontybugs.PogLinksRemain
                    ), er:
                    ## PogNotInstalled is prevented by buttons greying out in the gui.
                    ps.pub( show_error, unicode(er) )
                    ok=False
                if ok:
                    ## Update GUI

                    ## July 2016
                    ## =========
                    ## Added this test to sync view and target
                    ## objects IF they happen to be the samePog
                    if fpsys.state.samepogs:
                        # We uninstalled RHS, so need to set that in RHS
                        # which is a sep object.
                        fpsys.state.viewobject.setInstalledFlag(False)
                    ps.pub( change_pog_icon ) #Causes TWO calls to update BOTH choosers.
                    self.toggleButtons()
                    ps.pub( update_font_view )

            wx.EndBusyCursor()

        ## Sep 2009 : ZIP POGS 
        if e.GetId() == self.idzip:
            ## Nov 2017
            ## ==
            ## Moved the zip code into wxgui MainFrame
            ## it's in a DismissablePanel now.
            self.list_of_pogs_to_zip = multipogs # I want the list of chosen pogs.
            e.Skip() # fwd the event


    def OnPogTargetClick(self, args):
        """
        args[0] pogname
        args[1] is pognochange
        """
        ## Made it so a second click on a target pog will unselect it.
        if args[1]: #pognochange = True, so let's deselect this pog
            self.SelectNoTargetPog()
            ps.pub(update_font_view)
            return
        try:
            fpsys.instantiateTargetPog(args[0])
        except fontybugs.PogInvalid, e:
            ps.pub(show_error_and_abort, unicode( e ))
            return

        ps.pub(update_font_view)
        self.toggleButtons()

    def toggleButtons(self):
        ## If this is a no target pog situation, hide 'em all.
        if fpsys.state.targetobject is None:
            self.buttDelete.Enable(False)
            self.buttInstall.Enable(False)
            self.buttUninstall.Enable(False)
            self.buttZip.Enable(False)
            return
        installed = fpsys.state.targetobject.isInstalled()
        self.buttDelete.Enable(not(installed)) # DELETE button is inverse of installed status
        self.buttInstall.Enable(not(installed)) # INSTALL button is inverse 
        self.buttUninstall.Enable(installed) # UNINSTALL = True if pog is installed.
        self.buttZip.Enable(True)

    def SelectNoTargetPog(self):
        wx.BeginBusyCursor()
        ## Go figure out what item gets what image
        self.pogTargetlist.SortOutTheDamnImages( pognochange = True )
        self.pogTargetlist.ClearSelection() #Select nothing.

        fpsys.SetTargetPogToNone()  # Tell fpsys that we have no pog target selected	
        self.toggleButtons() # Disable the buttons on the bottom right.		
        wx.EndBusyCursor()
