##	Fonty Python Copyright (C) 2006, 2007, 2008, 2009 Donn.C.Ingle
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


import sys, locale, os
import strings
import pathcontrol
import fpsys
import fontybugs
import fontcontrol

## replaced optparse with this one because optparse chokes on 
## Unicode strings.
import getopt

class options(object):
	"""
	Imitate the previous optparse thing that could
	not handle unicode properly, coz I've got all this
	code written and don't want to hack it.
	"""
	list = False
	points = None
	numinpage = None
	text = None
	purge = False
	install = None
	uninstall = None
	check = False
	all = None
	allrecurse = None
	
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
			a = a.decode( locale.getpreferredencoding() )
		except:
			print _(u"I can't decode your argument(s). Please check your LANG variable. Also, don't paste text, type it in.")
			raise SystemExit
	tmp.append(a)
uargs = tmp

try:
	opts, args = getopt.gnu_getopt(uargs, "hvlc:ei:u:s:n:t:p:a:A:",\
	["help", "version", "list", "check=","examples","install=",\
	"uninstall=","size=","number=","text=","purge=","all=","all-recurse="])
except getopt.GetoptError, err:
	print str(err) # will print something like "option -a not recognized"
	raise SystemExit

for o, a in opts:
	if o in (u"-c", u"--check"):
		dirtocheck = os.path.abspath( a )
		options.check = True
		break
	if o in ("-v", "--version"):
		print strings.version
		raise SystemExit

	if o in ("-e", "--examples"):
		print strings.examples
		raise SystemExit
		
	elif o in ("-h", "--help"):
		print strings.use
		print strings.options
		raise SystemExit
		
	elif o in ("-l", "--list"):
		options.list = True

	elif o in ("-i","--install"):
		options.install = [a]
		if args:
			## Any trailing 'words' are taken to be other pognames
			## and added to the list. If they are not, they simply won't
			## be installed.
			options.install += args

	elif o in ("-u", "--uninstall"):
		options.uninstall = [a]
		if args:
			## Same as install.
			options.uninstall += args

	elif o in ("-p", "--purge"):
		options.purge = a

	elif o in ("-s", "--size"):
		try:
			n = int(a)
		except:
			print _("Please use a number for %s") % o
			raise SystemExit 
		options.points = n

	elif o in ("-n", "--number"):
		try:
			n = int(a)
		except:
			print _("Please use a number for %s") % o
			raise SystemExit			
		options.numinpage = n

	elif o in ("-t", "--text"):
		## The quotes gets stripped out, so I can't tell the
		## end of the text param and the start of other params
		## therefore I stick to the 'report and restart' idea.
		options.text = a
		fpsys.config.text = a

	elif o in ("-a", "--all", "-A","--all-recurse"):
		## var a is whatever comes after the -a flag.
		options.all = a # save to flag a test later (line 310)
		if o in ("-a","--all"):
			options.allrecurse = False
		else:
			options.allrecurse = True

		if len(args) != 1:
			print _("%s takes two arguments: SOURCE(folder) TARGET(pog)") % o
			print _("""NB: If you wanted to use spaces in a pogname or folder then please put "quotes around them."  """)
			raise SystemExit
	else:
		## We should not reach here at all.
		print "Your arguments amuse me :) Please read the help."
		raise SystemExit

####
## Ensure we have a .fontypython folder and a .fonts folder.
iPC = pathcontrol.PathControl()


####
## Let's handle those options that DO NOT require args.

## Check fonts
if options.check:
	if not os.path.exists( dirtocheck ):
		print _("I can't find %s") % dirtocheck
		raise SystemExit	
		
	def printer( pstr = "" ):
		"""A func to print strings to cli, called back from checkFonts."""
		if type(pstr) is str:
			pstr = unicode(pstr,locale.getpreferredencoding(),errors="replace")
		print pstr
		
	fpsys.checkFonts( dirtocheck, printer )
	raise SystemExit


## List -  Quick and dirty. 
if options.list:
	poglist = iPC.getPogNames()
	poglist.sort( cmp=locale.strcoll, key=lambda obj:obj) #28 May 2009. Hope this works for other locales...
	if len(poglist) == 0:
		print _("There are no pogs available.")
		raise SystemExit
	print _("Listing %d pog(s)") % len(poglist)
	print _(" * indicates installed pogs")
	for pog in poglist:
		paf = iPC.appPath() + pog + ".pog"
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
	raise SystemExit

####
## Size
## This one can mix with other args, so don't exit.
if options.points > 0:
	fpsys.config.points = options.points
	
####
## View
## This one can mix with other args, so don't exit.
if options.numinpage > 1:
	fpsys.config.numinpage = options.numinpage

####
## Text
## This one has potential to screw-up badly
## if the user forgets the quotes.
## For now, I will exit app.
if options.text:
	fpsys.config.text = options.text
	fpsys.config.Save()		
	print _("""Your text has been set to "%s"
Tip: Did you use quotes to surround your text?

Please start FontyPython again to see the result.""") % options.text
	raise SystemExit

	
####
##Handle purge
if options.purge:
	pogtopurge = options.purge # for clarity
	
	if fpsys.isPog(pogtopurge):
		pog = fontcontrol.Pog(pogtopurge)
		try:
			pog.genList()
		except fontybugs.PogInvalid, e:
			sys.exit(unicode( e ))
		try:
			## pog.purge() Raises
			##		  PogEmpty
			##		  PogInstalled			
			pog.purge()
		except(fontybugs.PogEmpty, fontybugs.PogInstalled), e:
			print unicode( e )
	else:
		print _("(%s) cannot be found. Try -l to see the names.") % pogtopurge
		raise SystemExit
	fpsys.config.Save()
	print strings.done
	raise SystemExit

####	
## Install:
if options.install:
	for pogtoinstall in options.install:
		if fpsys.isPog(pogtoinstall):
			pog = fontcontrol.Pog( pogtoinstall )
			try:
				pog.genList()
			except fontybugs.PogInvalid, e:
				sys.exit(unicode( e ))
			try:
			## pog.install() Raises:
			##		  PogEmpty
			##		  PogAllFontsFailedToInstall
			##		  PogSomeFontsDidNotInstall			
				print _("Installing (%s)") % pogtoinstall
				pog.install()
			except (fontybugs.PogEmpty, 
							fontybugs.PogAllFontsFailedToInstall,
							fontybugs.PogSomeFontsDidNotInstall,
					   ), e:
				print unicode( e )
		else: # not a pogname
			print _("(%s) cannot be found. Try -l to see the names.") % pogtoinstall
			raise SystemExit
	fpsys.config.Save()
	print strings.done
	raise SystemExit
	
####
## uninstall
if options.uninstall:
	for pogtouninstall in options.uninstall:
		if fpsys.isPog(pogtouninstall):
			pog = fontcontrol.Pog(pogtouninstall )
			try:
				pog.genList()
			except fontybugs.PogInvalid, e:
				sys.exit(unicode( e ))
			try:
			## Raises:
			##		  PogEmpty
			##		  PogLinksRemain
			##		  PogNotInstalled			
				print _("Removing (%s)") % pogtouninstall
				pog.uninstall()
			except (fontybugs.PogEmpty,
				fontybugs.PogNotInstalled,
				fontybugs.PogLinksRemain), e:
				print unicode( e )
		else:
			print _("Sorry, can't find (%s). Try -l to see the names.") % pogtouninstall
			raise SystemExit
	fpsys.config.Save()
	print strings.done
	raise SystemExit

## Install all fonts in folder to given pog.
## May 2009 : Based on code by another author (names lost in email crash).
if options.all:
	count = 0
	existingPog = False
	POGNAME = args[0]
	FOLDERNAME = options.all
	try:
		folder = fontcontrol.Folder(FOLDERNAME, recurse=options.allrecurse)
	except fontybugs.FolderHasNoFonts, e:
		print unicode( e )
		raise SystemExit
	except OSError, e: # Catches other errors in Folder
		print e.strerror
		raise SystemExit

	ipog = fontcontrol.Pog( POGNAME ) # whether it exists or not.

	## If it's an unknown POGNAME, make it and write it:
	if not fpsys.isPog(POGNAME):
		print _("Creating a new pog: %s") % POGNAME
		try:
			ipog.write()
		except fontybugs.PogWriteError, e:
			sys.exit( unicode( e ) )
	
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
		sys.exit( unicode( e ) )
	del ipog, folder

	if count:
		print _("I have placed %(count)s fonts from %(folder)s into %(pog)s.") % {"count":str(count), "folder":FOLDERNAME, "pog":POGNAME }
	else:
		print _("The fonts from %(folder)s are *already* in %(pog)s.") % {"folder": FOLDERNAME, "pog":POGNAME  }
	raise SystemExit

####
## If there are > 2 args then there is chaos:
if len(args) > 2:
	## The user may have chosen a pogname with spaces and no quotes
	print _("""Please check your arguments, there seem to be too many.\n(Remember: it's one pound for a five-minute argument, but only eight pounds for a course of ten.)\n\nNB: If you wanted to use spaces in a pogname or folder then please put "quotes around them." """)
	raise SystemExit
	
####
## Handle Cases :
A = None
B = None

fakearg = False 

## If there are no arguments, then we should fetch the last ones used from
## the config file.
if not args:
	args = []
	fakearg = True
	lv = fpsys.config.lastview
	#print "last one:",lv
	if not fpsys.isFolder(lv) and not fpsys.isPog(lv): lv = "EMPTY"
	args.append(lv)#Fakes an arg, will be last pog used (recovered from config) or "EMPTY"

## Get the args into simple vars:
A = args [0]
if len(args) == 2: B = args [1]

## Let's ensure that, should A be a pog, that it exists, BUT only if it was not a fakearg:
if not fpsys.isFolder(A) and not fpsys.isPog(A) and not fakearg:
	## It's a non starter:
	print _("Sorry, (%s) does not exist. Try --list") % A
	raise SystemExit

## Disallow Folder in arg B
if B and fpsys.isFolder(B):
	print _("You cannot use a folder as the target argument. Try --help")
	raise SystemExit
	
## Let's ensure that B exists, else we must make it.
## This is because when you call ./fp VIEW TARGET and
## TARGET gets created (the file) if it's not there.
if B and not fpsys.isPog(B):
	ipog = fontcontrol.Pog(B)
	try:
		ipog.write()
	except fontybugs.PogWriteError, e:
		sys.exit( unicode( e ) )
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
			print unicode( e ) # warn cli
			## Let it continue
			fpsys.config.lastdir = os.path.abspath(A)
			
	if fpsys.isPog(A): 
		try:
			fpsys.instantiateViewPog(A)# creates state.targetobject globally
		except fontybugs.PogInvalid, e:
			print repr( e )
			sys.exit()
	## Because we are catering for a potential full gui,
	## we must make an official "targetobject" set to None
	fpsys.SetTargetPogToNone()
	
## Two args:
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
			 sys.exit(unicode( e ))
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
			sys.exit(unicode( e ))
		if empty: 
			print _("This pog is empty")
			raise SystemExit
 
		try:
			installed = fpsys.instantiateTargetPog(B)
		except fontybugs.PogInvalid, e:
			sys.exit(unicode( e ))
		if installed:
			print _("The target pog (%s) is currently installed, you can't use it as a target.") % B
			raise SystemExit

## Your arguments amuse me :) Please try -h
