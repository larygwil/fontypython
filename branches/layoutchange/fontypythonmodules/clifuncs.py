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

import os, locale
import strings
import fontybugs
import fpsys
import fontcontrol

def checkfonts( dirtocheck ):
    # Check fonts
    if not os.path.exists( dirtocheck ):
        print _("I can't find %s") % dirtocheck
        return

    def printer( pstr = "" ):
        """A func to print strings to cli, called back from checkFonts."""
        if type(pstr) is str:
            pstr = fpsys.LSP.to_unicode( pstr )
        print pstr

    ##TODO ?? SHOULD this TRY/EXC
    fpsys.checkFonts( dirtocheck, printer )


def listpogs():
    ## List -  Quick and dirty. 
    poglist = fpsys.iPC.getPogNames()

    poglist.sort( cmp=locale.strcoll, key=lambda obj:obj) #28 May 2009. Hope this works for other locales...
    if len(poglist) == 0:
        print _("There are no pogs available.")
        return
    print _("Listing %d pog(s)") % len(poglist)
    print _(" * indicates installed pogs")
    for pog in poglist:
        paf = fpsys.iPC.appPath() + pog + ".pog"
        try:
            f = open(paf, "r" ) #  It's a plain byte-string ascii file.
            installed = f.readline()[:-1] #Strips the \n off the end
            f.close()
        except:
            print _("Could not open (%s).") % paf
        s = " "
        if installed.upper() == "INSTALLED":
            s = "*"
        print "%s %s" % (s,pog)


## Sept 2017: Added this because I was doing ls in testing so much.
def lsfonts():
    import subprocess
    try:
        p = fpsys.iPC.userFontPath()
        ls = subprocess.check_output(['ls','--color=always', '-l', p ])
    except:
        print _("Could not ls the font path.")
        raise
    print _("Contents of {}:").format(fpsys.LSP.to_unicode(p))
    print ls ## is this already unicode?


## Nov 2017 - also helps with dev
def cat( pog ):
    import subprocess
    try:
        p = os.path.join(fpsys.iPC.appPath(), "{}.pog".format(pog))
        cat_res = subprocess.check_output(['cat', p])
    except:
        print _("Could not cat that pog.")
        return
    print cat_res


def hush( pog ):
    """
    Called from cli2.py
    A test for XDG_CONFIG_HOME as well as fontconfig/conf.d/
    has been done there, and errors were shown, etc.
    Thus we know fontconfig is installed and we can proceeed.
    """
    def printer( pstr = "", key = None ):
        pstr = fpsys.LSP.ensure_unicode(pstr)
        print pstr

    buglist = fpsys.hush_with_pogs([pog], printer)

    if buglist: 
        ## All errors end with this text:
        print strings.cant_hush
        for bug in buglist: print bug
        print
        print strings.hush_howto

def hush( pog ):
    """
    Called from cli2.py
    A test for XDG_CONFIG_HOME as well as fontconfig/conf.d/
    has been done there, and errors were shown, etc.
    Thus we know fontconfig is installed and we can proceeed.
    """
    def printer( pstr = "", key = None ):
        pstr = fpsys.LSP.ensure_unicode(pstr)
        print pstr

    buglist = fpsys.hush_with_pogs([pog], printer)

    if buglist: 
        ## All errors end with this text:
        print strings.cant_hush
        for bug in buglist: print bug
        print
        print strings.hush_howto

def unhush():
    def printer( pstr = "", key = None ):
        pstr = fpsys.LSP.ensure_unicode(pstr)
        print pstr

    buglist = fpsys.un_hush( printer )

    if buglist: 
        ## All errors end with this text:
        print strings.cant_unhush
        for bug in buglist: print bug
        print
        print strings.hush_howto

def zip( pog ):
    ## Sep 2009 : ZIP
    ## Nov 2017: Much fixing of error handling.
    if fpsys.isPog( pog ):
        todir = os.curdir #always where we run this
        ipog = fontcontrol.Pog( pog )
        (bugs, fail, emsgs) = ipog.zip( todir )

        if fail: 
            print _("I could not create the zip at all.")
            print emsgs[0]
        else:
            print _("Zipped as \"%s.fonts.zip\" in the \"%s\" directory.") % (pog,os.getcwd())
            if bugs:
                print _("Some bugs happened:")
                for m in emsgs: print m
    else:
        print _("I can't find a pog named %s") % pog

def purgepog(pogtopurge):
    ##Handle purge
    if fpsys.isPog(pogtopurge):
        pog = fontcontrol.Pog(pogtopurge)
        try:
            #raise fontybugs.PogInvalid #testing
            pog.genList()
        except fontybugs.PogInvalid, e:
            e.print_error_and_quit()
        try:
            ## pog.purge() Raises
            ## 	  PogEmpty
            ## 	  PogInstalled			
            pog.purge()
        except (fontybugs.PogEmpty, fontybugs.PogInstalled), e:
            e.print_error()
    else:
        print _("(%s) cannot be found. Try -l to see the names.") % pogtopurge
        return
    fpsys.config.Save()
    print strings.done



def installpogs( listofpogs ):
    #### 
    ## Install:
    for pogtoinstall in listofpogs:
        if fpsys.isPog(pogtoinstall):
            pog = fontcontrol.Pog( pogtoinstall )
            try:
                pog.genList()
            except fontybugs.PogInvalid, e:
                e.print_error_and_quit()
            try:
            ## pog.install() Raises:
            ## 	  PogEmpty
            ## 	  PogAllFontsFailedToInstall
            ## 	  PogSomeFontsDidNotInstall			
            ## 	  NoFontsDir
                print _("Installing (%s)") % pogtoinstall
                pog.install()
            except ( fontybugs.PogEmpty,
                    fontybugs.PogAllFontsFailedToInstall,
                    fontybugs.PogSomeFontsDidNotInstall,
                    fontybugs.NoFontsDir ), e:
                e.print_error()
        else: # not a pogname
            print _("(%s) cannot be found. Try -l to see the names.") % pogtoinstall
            return
    fpsys.config.Save()
    print strings.done

def uninstallpogs( listofpogs ):
    ## uninstall
    for pogtouninstall in listofpogs:
        if fpsys.isPog(pogtouninstall):
            pog = fontcontrol.Pog(pogtouninstall )
            try:
                pog.genList()
            except fontybugs.PogInvalid, e:
                e.print_error_and_quit()
            try:
            ## Raises:
            ## 	  PogEmpty
            ## 	  PogLinksRemain
            ## 	  PogNotInstalled			
                print _("Removing (%s)") % pogtouninstall
                pog.uninstall()
            except (fontybugs.PogEmpty,
                fontybugs.PogNotInstalled,
                fontybugs.PogLinksRemain), e:
                e.print_error()
        else:
            print _("Sorry, can't find (%s). Try -l to see the names.") % pogtouninstall
            return
    fpsys.config.Save()
    print strings.done


def installall( FOLDERNAME, POGNAME, recurseflag ):
    ## Install all fonts in folder to given pog.
    ## May 2009 : Based on code by another author (names lost in email crash).
    count = 0
    existingPog = False
    try:
        folder = fontcontrol.Folder(FOLDERNAME, recurse=allrecurse)
    except fontybugs.FolderHasNoFonts, e:
        e.print_error_and_quit()

    ipog = fontcontrol.Pog( POGNAME ) # whether it exists or not.

    ## If it's an unknown POGNAME, make it and write it:
    if not fpsys.isPog(POGNAME):
        print _("Creating a new pog: %s") % POGNAME
        try:
            ipog.write()
        except fontybugs.PogWriteError, e:
            e.print_error_and_quit()

    ## Fill it with fontitems.
    ipog.genList()

    ## get a list of what (in the folder) is NOT already in the ipog (assuming it's non-empty)
    fl = [fi for fi in folder if str(fi) not in [str(fi2) for fi2 in ipog]] #str(fontItem) returns glyphpaf which has been decoded already.

    ## Add those fresh items to ipog
    for f in fl:
        ipog.append( f )
        count += 1
    try:
        ipog.write()
    except fontybugs.PogWriteError, e:
        e.print_error_and_quit()
    del ipog, folder

    if count:
        print _("I have placed %(count)s fonts from %(folder)s into %(pog)s.") % {"count":str(count), "folder":FOLDERNAME, "pog":POGNAME }
    else:
        print _("The fonts from %(folder)s are *already* in %(pog)s.") % {"folder": FOLDERNAME, "pog":POGNAME  }

