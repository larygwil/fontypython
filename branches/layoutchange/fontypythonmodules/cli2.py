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


import sys, locale, os
import strings
import fontybugs
import fpsys
import fontcontrol
import clifuncs #Split out the hard work to shorten this file

## replaced optparse with this one because optparse chokes on 
## Unicode strings.
import getopt


class situation(object):
    """
    A class that won't instantiate. It's a small packet of
    values that are set as-per the command line's arguments.
    """
    version = False
    help = None
    ls = False
    lsfonts = False
    showdir = False
    points = None
    numinpage = None
    text = None
    purge = False
    install = None
    uninstall = None
    checkdir = False
    allfromfolder = None
    alltargetpog=[]
    allrecurse = None
    cat = None
    hush = False
    unhush = False
    zip = None

## If non-ascii chars get entered on the cli, say a Japanese word for
## a pog's name, we may have a problem. 
## So, I am going to (try to) decode those byte strings into Unicode first:
tmp = []
for a in sys.argv[1:]:
    ## It seems that a is always a BYTE STRING, but I'll just test anyway:
    #print [a]
    if type(a) is str:
        ## This happens when text is PASTED onto the cli when that cli
        ## is in a LANG that can't handle that text.
        ## I don't know what other cases may cause this.
        try:
            a = fpsys.LSP.to_unicode( a )
        except:
            print _(u"I can't decode your argument(s). Please check your LANG variable. Also, don't paste text, type it in.")
            raise SystemExit
    tmp.append(a)
uargs = tmp

try:
    opts, remaining_cli_arguments = getopt.gnu_getopt(uargs, "h:vldfc:i:u:s:n:p:a:A:z:",
    ["help=", "version", "list", "dir", "lsfonts", "check=","install=",
    "uninstall=","size=","number=","purge=","all=","all-recurse=","zip=", 
    "cat=", "hush=", "unhush" # these have no short opts.
    ])
except getopt.GetoptError, err:
    ## Specific help on the help command
    if err.opt in ("h", "help"): 
        print strings.use
        print
        print _("For more help use:  \"-h b\" for basic help, \"-h e\" for examples," \
                "\nor \"-h hush\" for help with hushing fonts.")
        raise SystemExit
    print strings.arguments_amuse

    print str(err) # will print something like "option -foob not recognized"
    raise SystemExit

## A context flag so we can determine which code path is going to be
## command line output, and which is going to be the wxgui.
strictly_cli_context_only = False

for option, argument in opts:

    if option in ("-v", "--version"):
        strictly_cli_context_only = True
        situation.version = True

    ## Nov 2017
    ## Help gets an argument.
    elif option in ("-h", "--help"):
        if not argument:
            print strings.arguments_amuse
            raise SystemExit
        strictly_cli_context_only = True
        situation.help = argument

    ## Checkdir will break the loop, skipping other args. It's a big job.
    elif option in (u"-c", u"--check"):
        strictly_cli_context_only = True
        # Turns-out that "check=" on it's own, sans an argument
        # does not trigger the error test above. Here's a manual one:
        if not argument:
            print strings.arguments_amuse
            raise SystemExit
        situation.checkdir = os.path.abspath( argument )
        break

    elif option in ("-l", "--list"):
        strictly_cli_context_only = True
        situation.ls = True

    elif option in ("-f", "--lsfonts"):
        strictly_cli_context_only = True
        situation.lsfonts = True

    elif option in ("-d", "--dir"):
        strictly_cli_context_only = True
        situation.showdir = True

    elif option in ("-i","--install"):
        strictly_cli_context_only = True
        if not argument:
            print strings.arguments_amuse
            raise SystemExit
        situation.install = [argument]
        if remaining_cli_arguments:
            ## Any trailing 'words' are taken to be other pognames
            ## and added to the list. Valid or not.
            situation.install += remaining_cli_arguments
        del remaining_cli_arguments[:] #erase contents, now that they're used.

    elif option in ("-u", "--uninstall"):
        strictly_cli_context_only = True
        if not argument:
            print strings.arguments_amuse
            raise SystemExit
        situation.uninstall = [argument]
        if remaining_cli_arguments:
            ## Same as install.
            situation.uninstall += remaining_cli_arguments
        del remaining_cli_arguments[:]

    elif option in ("-p", "--purge"):
        strictly_cli_context_only = True
        if not argument:
            print strings.arguments_amuse
            raise SystemExit
        situation.purge = argument

    ## This is for a gui context, hence no strictly_cli_context_only
    elif option in ("-s", "--size"):
        try:
            n = int(argument)
        except:
            print strings.please_use_arg % option
            raise SystemExit
        situation.points = n

    ## Also a gui context
    elif option in ("-n", "--number"):
        try:
            n = int(argument)
        except:
            print strings.please_use_arg % option
            raise SystemExit
        situation.numinpage = n

    elif option in ("-a", "--all", "-A","--all-recurse"):
        if not argument:
            print strings.arguments_amuse
            raise SystemExit
        strictly_cli_context_only = True
        situation.allfromfolder = argument
        isituation.allrecurse = option in ("-A","--all-recurse")
        if len(remaining_cli_arguments) != 1:
            print _("%s takes two arguments: SOURCE(folder) TARGET(pog)") % option
            print _("NB: If you have spaces in the Pog or Folder names, put \"quotes around the names.\"")
            raise SystemExit
        situation.alltargetpog = remaining_cli_arguments[0]
        del remaining_cli_arguments[:]

    elif option in ("-z","--zip"):
        if not argument:
            print strings.arguments_amuse
            raise SystemExit
        strictly_cli_context_only = True
        # argument is the Pog name we must zip.
        # This only does one pog, not several at once.
        # (due to the limits of gnu_getopt)
        # TODO Unsure why, exactly. Must recheck..
        situation.zip = True
        situation.pog = argument
    
    elif option == "--cat":
        if not argument:
            print strings.arguments_amuse
            raise SystemExit
        strictly_cli_context_only = True
        situation.cat = True
        situation.pog = argument

    elif option == "--hush":
        if not argument:
            print strings.arguments_amuse
            raise SystemExit
        strictly_cli_context_only = True
        situation.hush = True
        situation.pog = argument

    elif option == "--unhush":
        strictly_cli_context_only = True
        situation.unhush = True

    else:
        ## We should not reach here at all.
        print _("Weirdo error. Keep calm and panic.")
        raise SystemExit
    
    #print [(k,s) for k,s in situation.__dict__.iteritems()]

##Switch on the cli context
if strictly_cli_context_only:

    ## Probe for any delayed fpsys pathcontrol errors
    ## As it's CLI-only, we can print errors in the normal way.
    ## Surviving this test means fpsys.PathControl is in a trusted state
    ## and can be used without worrying about these kinds of errors.
    try:
        fpsys.iPC.probeAllErrors()

    ## These stop the app.
    except (fontybugs.NoFontypythonDir, fontybugs.UpgradeFail) as e:
        e.print_error_and_quit()

    ## This one is a warning only.
    except fontybugs.NoFontsDir as e:
        ## Hushing requires installing a certain POG, hence 
        ## must have fonts dir.
        if situation.hush:
            print strings.cant_hush
            e.print_error()
            print strings.see_help_hush
            raise SystemExit
        e.print_error()

    except fontybugs.NoFontconfigDir as e:
        if situation.hush or situation.unhush:
            ## Hushing requires fontconfig etc.
            if situation.hush:
                print strings.cant_hush
            else:
                print strings.cant_unhush
            e.print_error()
            print strings.see_help_hush
            raise SystemExit
        ## don't print any error here.

    if situation.version:
        print strings.version

    elif situation.help:
        # basics
        if situation.help == "b":
            print strings.use
            print
            print strings.options
        # examples
        elif situation.help == "e":
            print strings.examples
        # hushing
        elif situation.help == "hush":
            ## Format-in some paths to help user:
            if fpsys.iPC.user_fontconfig_confd() == "":
                fcpaf = _("unknown, try: {}").format(
                        os.path.join(fpsys.iPC.home(),
                            ".config/fontconfig/conf.d"))
            else:
                fcpaf = fpsys.iPC.user_fontconfig_confd()
            print strings.hush_howto.format(fcpaf = fcpaf)
        else:
            print strings.use
        print "---"
        print strings.copy_warranty_contact
        raise SystemExit

    elif situation.showdir:
        ## E.g. of PathControl being trusted: we don't need to test appPath for errors here.
        print strings.fontyfolder.format(fpsys.LSP.to_unicode(fpsys.iPC.appPath()))

    ## Check fonts
    elif situation.checkdir: clifuncs.checkfonts( situation.checkdir )

    ## List
    elif situation.ls: clifuncs.listpogs()

    ## Sep 2017
    elif situation.lsfonts: clifuncs.lsfonts()

    ## Sep 2009: ZIP
    elif situation.zip: clifuncs.zip( situation.pog )

    ## Purge
    elif situation.purge: clifuncs.purgepog( situation.purge )

    ## Install - .install is actually a list in this case
    elif situation.install: clifuncs.installpogs( situation.install )

    ## Uninstall - ditto
    elif situation.uninstall: clifuncs.uninstallpogs( situation.uninstall )

    ## Install ALL fonts in folder to given pog.
    ## the def wants: 1=foldername, 2=pogname. 3=recurseflag
    elif situation.allfromfolder: clifuncs.installall( 
            situation.allfromfolder,
            situation.alltargetpog,
            situation.allrecurse )

    elif situation.cat: clifuncs.cat( situation.pog )

    elif situation.hush:   clifuncs.hush_unhush( situation.pog, switch = "hush" )
    elif situation.unhush: clifuncs.hush_unhush( None, switch = "unhush" )

    ## Arguments for the final, right-hand side, [VIEW] [TARGET] in pure cli 
    ## context has no meaning, so we'll simply ignore them.

    ## Nothing left for the strictly command line only context to do, so:
    raise SystemExit



## At this point:
## This is a mixed zone: "fontypython" is being run either from 
## the cli or from the gui (via a .desktop file).
##
## All flags that trigger a *strictly_cli_context_only* have been dealt with, this leaves
## only some gui options and the remaining_cli_arguments [VIEW] and/or [TARGET] to handle.
##
## Fonty is:
## 1. Definitely from the cli (e.g. fontypython /fonts BAR) if there ARE remaining_cli_arguments
## 2. Possibly * from an icon (.desktop file), if there ARE NO remaining_cli_arguments.
## 
## * It's possible to run "fontypython" naked on the cli, thus I can't make assumptions
## about where Fonty is really coming from. For this reason, I will leave all print 
## statements (below) to stdout to cover cli useage.


## If there are many remaining_cli_arguments, it's chaos:
if len(remaining_cli_arguments) > 2:
    ## The user may have chosen a pogname with spaces and no quotes
    print _("Please check your arguments, there seem to be too many.\n(Remember: it's one pound for a five minute argument, but only eight pounds for a course of ten.)\n\nNB: If you use spaces in a Pog or Folder name then put \"quotes around the names.\"")
    raise SystemExit

## Args that only have meaning in gui context:
## Size of fonts
if situation.points > 0:
    fpsys.config.points = situation.points
## Number in a page
if situation.numinpage > 1:
    fpsys.config.numinpage = situation.numinpage


#### VIEW TARGET tests
## These last tests decide the last two [VIEW][TARGET] arguments on the
## command line. (If there isn't a VIEW, one is faked!)

## If there are no arguments, make one:
if not remaining_cli_arguments:
    lv = fpsys.config.lastview
    # if it's not a valid folder or pog, make it "EMPTY"
    if not fpsys.isFolder(lv) and not fpsys.isPog(lv): lv = "EMPTY"
    # A is: the last pog used (from config) or "EMPTY"
    A = lv
    B = None
else:
    ## Get the remaining_cli_arguments into simple vars:
    A = remaining_cli_arguments[0]
    B = remaining_cli_arguments[1] if len(remaining_cli_arguments) == 2 else None

## Let's ensure that, should A be a pog, that it's valid:
if not fpsys.isFolder(A):
    # If it's not a pog and it's not "EMPTY",then it's a weirdo.
    if not fpsys.isPog(A) and A != "EMPTY":
        print _("Sorry, (%s) does not exist. Try --list") % A
        raise SystemExit

## Disallow Folder in arg B
if B and fpsys.isFolder(B):
    print _("You cannot use a folder as the target argument. Try --help")
    raise SystemExit

## Let's ensure that B exists, else we must make it.
## This is because when you call VIEW TARGET and
## TARGET gets created (the file) if it's not there.
##TODO: Why? FIXME
if B and not fpsys.isPog(B):
    ipog = fontcontrol.Pog(B)
    try:
        ipog.write()
    except fontybugs.PogWriteError, e:
        e.print_error_and_quit()
    del ipog

## Build the fpsys structure
## Calls to instantiateXYZ are vital. They are where the View or Target Objects get 
## generated - i.e. where all their fontItems are built-up.
## One arg:
if A and not B:
    if fpsys.isFolder(A):
        try:
            fpsys.instantiateViewFolder(A) # creates a state.viewobject globally.
        except fontybugs.FolderHasNoFonts, e:
            e.print_error()
            ## Let it continue
            fpsys.config.lastdir = os.path.abspath(A)

    ## The possible "EMPTY" A is a special case: it's a valid Pog.
    if fpsys.isPog(A):
        try:
            fpsys.instantiateViewPog(A)# creates state.targetobject globally
        except fontybugs.PogInvalid, e:
            e.print_error_and_quit()
    ## Because we are catering for a potential full gui,
    ## we must make an official "targetobject" set to None
    fpsys.SetTargetPogToNone()

## Two remaining_cli_arguments:
if A and B:
    if fpsys.isFolder(A)and fpsys.isPog(B):
        ## "FP"
        try:
            fpsys.instantiateViewFolder(A)
        except fontybugs.FolderHasNoFonts, e:
            ## Let it continue
            fpsys.config.lastdir = os.path.abspath(A)
        try:
            installed = fpsys.instantiateTargetPog(B)
        except fontybugs.PogInvalid, e:
            e.print_error_and_quit()
        if installed:
            print _("The target pog (%s) is currently installed, you can't use it as a target.") % B
            raise SystemExit

    if fpsys.isPog(A)and fpsys.isPog(B):
        ## "PP"
        if A == B:
            print _("Your pogs are the same! Try -e")
            raise SystemExit
        try:
            empty = fpsys.instantiateViewPog(A)
        except fontybugs.PogInvalid, e:
            e.print_error_and_quit()
        if empty:
            print _("This pog is empty")
            raise SystemExit

        try:
            installed = fpsys.instantiateTargetPog(B)
        except fontybugs.PogInvalid, e:
            e.print_error_and_quit()
        if installed:
            print _("The target pog (%s) is currently installed, you can't use it as a target.") % B
            raise SystemExit

## As we're going to run the wxgui, I will do the pathcontrol 
## error probes there, and open msgboxes or something to print the errors.
