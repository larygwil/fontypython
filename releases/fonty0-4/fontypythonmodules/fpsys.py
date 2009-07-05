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

## fpsys : fonty python system.
## I debated calling it fpglobals.
## This is a common-ground for variables and defs that will be used from
## other modules - so they are global to everything.

import sys, os, pickle, locale
import pathcontrol
import strings
import fontcontrol

## Ensure we have a .fontypython folder and a .fonts folder.
iPC = pathcontrol.PathControl() #Make an instance - hence the small 'i'

##  Borrowed from wxglade.py
## The reason for this is to find the path of this file
## when it's called from an import somewhere else.
## There is no sys.argv[0] in this case.
root = __file__
if os.path.islink(root):
	root = os.path.realpath(root)
fontyroot = os.path.dirname(os.path.abspath(root)) 

## Where my images and things are.
mythingsdir = os.path.join(fontyroot,"things/")

## Jan 18 2008
segfonts = []# Global var

def getSegfontsList():
	"""Runs (below) on startup"""
	## On startup, open the 'segfonts' file and keep a list in RAM
	## This file is written by the 'check' routine.
	global segfonts
	paf = os.path.join(iPC.appPath(),"segfonts")
	try:
		if os.path.exists( paf ):
			fr = open( paf, 'r' ) # byte string only ascii file
			segfonts = fr.read().split("\n")
			fr.close()
	except:
		## CORNER CASE: Some error or other.
		raise
## Call it.		
getSegfontsList()	


def checkFonts( dirtocheck, printer ):
	"""
	Jan 18 2008
	Scan a tree for fonts that can cause segfaults.
	Write a file 'segfonts' and create a list 'segfonts'
	that gets checked to exclude them.
	
	printer is a function of some kind. 
	
	Can be called from the cli or the gui.
	"""
	import subprocess
	global segfonts
	
	code = """
import ImageFont
try:
	font=ImageFont.truetype("%s", 24, 0)
	dud=font.getname()
except:
	pass
	"""
	def checkForSegfault( pafbytestring ):
		## Uses Ajaksu's idea : 17 Jan 2008. Thanks!
		segfault_I_hope = False
		## I have ignored ALL catchable errors (see code var)
		## This is because I want to (try to) only catch SEGFAULTS
		## and leave all other flavours of font-related errors to
		## the fontcontrol module -- where fonts are still useable
		## if not visible.
		retval = subprocess.call( ["python",  '-c', code %  pafbytestring] )
		if retval != 0:
			segfault_I_hope = True
		return segfault_I_hope
   
	printer ( _("Checking fonts, this could take some time.") )
	printer ( _("Starting in %s:") % dirtocheck )
	printer ()
	## dirtocheck comes-in as unicode - let's stick to byte strings:
	dirtocheck = dirtocheck.encode( locale.getpreferredencoding() )
	seglist = [] # our local list of newly found bad fonts
	gotsome = False
	for cwd, dirs, files in os.walk( dirtocheck ):
		printer(_("Looking in %s...") % os.path.basename(cwd) )
		## We only want certain font files:
		fontfiles = [f for f in files if f.upper().endswith( ("TTF","TTC","PFA","PFB","OTF")) ]
		if len(fontfiles) < 1:
			printer (_("No supported fonts found there..."))
			printer()
		for file in fontfiles:
			paf = os.path.join( cwd, file )
			bad = checkForSegfault( paf )
			if bad:
				gotsome = True
				seglist.append( paf )
				printer ( " " + file ) # show it on-screen somewhere.
				
	if not gotsome:
		printer(_("I could not find any bad fonts."))
	## Now write the segfonts file:
	if seglist:
		## Add the new fonts found to the ones in global segfonts list
		for bf in seglist:
			segfonts.append(bf)
		## Now remove duplicates
		tmp =  list( set( segfonts ) )
		segfonts = tmp
		del (tmp)
		## Now save it.
		paf = os.path.join(iPC.appPath(),"segfonts")
		fw = open( paf, "w" ) # byte string ascii
		bytestring = "".join([line + "\n" for line in segfonts if line != ""])
		#print "about to write bytestring:"
		#print [bytestring]
		#print
		fw.write( bytestring )
		fw.close()
		
	printer()
	printer(_("The process is complete."))
	
def isFolder(thing):
	"""True if a folder. False if not - but that does not mean it's a pog."""
	if os.path.isdir(thing): return True
	return False

def isPog(thing):
	"""True if a Pog. False if not."""
	## thing comes in as UNICODE
##	## These come in handy when debugging Unicode errors
##	print "thing:", thing
##	print "type of thing:", type(thing)
##	print
##	print "iPC.getPogNames():", [iPC.getPogNames()]
	## iPC.getPogNames() is a list of BYTE STRINGS
	## We must encode thing to a byte string to avoid warnings:
	if thing.encode(locale.getpreferredencoding()) in iPC.getPogNames(): #getPogNames contains UNICODE elements
		return True
	if thing == "EMPTY": return True #Special case
	return False


class FPState:
	"""The global vars to hold the state of the situation."""
	def __init__(self):
		## Contains the Pog or Folder being viewed
		self.viewobject = None
		
		## Refs the view object *after* the filter has been applied
		self.filteredViewObject= None

		## Contains a Pog (or None) that is the Target
		self.targetobject = None
		
		## Represents the situation in a letter code
		## P for Pog, F for Folder, E for Empty, N for None
		self.viewpattern = ""
		self.targetpattern = ""
		
		## Will be "NOTHING_TO_DO", "REMOVE" or "APPEND" (Add fonts to Pog)
		self.action = "" 
		
		## Can an item be ticked
		self.cantick = None
		
		## The View and Target pogs chosen are the same.
		self.samepogs = False
		
		## How many tick marks.
		self.numticks = 0
		
state = FPState() #The only instance of the state object -- app-wide


####
## Save and Load the conf file
class Configure:
	"""Makes/Loads the conf file.
	Supplies size, pos, numinpage, text string and point size to other objects."""
	def __init__(self) :
		## Private vars
		self.__dontSaveNumInPage = False
		
		## PUBLIC vars :  Set some defaults:
		self.size = (400,600) 
		self.pos = (10, 10)
		self.numinpage = 10
		self.text = _("Jump the lazy dog fox")
		self.points = 64	  
		self.lastview = "EMPTY" # a pog name or a folder path.
		self.usegui = "wxgui"
		self.max = True
		self.lastdir = iPC.home()
		## Added Dec 2007
		self.leftSash = 128
		self.rightSash = 128
		## Added June 2009
		self.recurseFolders = False 

		self.__setData()
		
		if os.path.exists(iPC.appConf()):
			try:
				pf = open(iPC.appConf(), "rb" ) # Binary for new pickle protocol.
				self.__data = pickle.load( pf )
				pf.close() 
			except:
				## Dec 2007 : Let's try erase and rewind
				os.unlink(iPC.appConf())
				
		if not os.path.exists(iPC.appConf()):		
			print _("No config file found, creating it with defaults.")
			self.Save() 
			
		## Now get them into the instance vars:
		try:
			self.size = self.__data['size']
			self.pos = self.__data['pos']
			self.numinpage = self.__data['numinpage']
			self.text = self.__data['text']
			self.points= self.__data['points']
			self.lastview = self.__data['lastview']			
			self.usegui = self.__data['usegui']
			self.max = self.__data['max']
			self.lastdir = self.__data['lastdir']
			self.leftSash = self.__data['leftSash']
			self.rightSash = self.__data['rightSash']
			self.recurseFolders = self.__data['recurseFolders']
			
		except KeyError:
			## The conf file has keys that don't work for this version, chances are it's old.
			## Let's delete and re-make it.
			try:
				os.unlink(iPC.appConf())
			except:
				print _("The fontypython config file is damaged.\nPlease remove it and start again")
				raise SystemExit
			self.Save()
	def dontSaveNumInPage(self, flag):
		self.__dontSaveNumInPage = flag
	def __setData(self):
		self.__data = {"size" : self.size,
								"pos" : self.pos,
								"numinpage" : self.numinpage,
								"text" : self.text,
								"points" : self.points,
								"lastview" : self.lastview,
								"usegui" : self.usegui,
								"max" : self.max,
								"lastdir" : self.lastdir,
								"leftSash" : self.leftSash,
								"rightSash" : self.rightSash,
								"recurseFolders": self.recurseFolders
								}
	def Save(self) :
		#If we are NOT to save the numinpage, then fetch it from what was there before.
		if self.__dontSaveNumInPage:
			self.numinpage = self.__data["numinpage"]
		self.__setData()
		try:
			pf = open( iPC.appConf(), "wb" )
			pickle.dump(self.__data, pf, protocol = pickle.HIGHEST_PROTOCOL ) 
			pf.close() 
		except IOError:
			print _("Could not write to the config file.")


## Our config instance - it will have one instance across
## all the modules that use it.
config = Configure()


def instantiateViewFolder( foldername, recurse=False ):
	"""
	Creates a Folder object and fills it with FontItem objects
	according to what's in the folder's path.
	
	This is the VIEW - i.e. what you are looking at.
	"""
	if state.viewobject: del state.viewobject
	## Default assumptions in case of raised error.
	state.viewobject = fontcontrol.EmptyView()
	state.viewpattern = "E" 
	ifolder = fontcontrol.Folder(foldername, recurse) #raises : fontybugs.FolderHasNoFonts : BENIGN ERROR.
	## Only continues if there is no problem.
	state.viewobject = ifolder
	## Because we have a new view object, we must reset the last filteredViewObject
	state.filteredViewObject = None

	config.lastview = foldername
	state.viewpattern = "F"
	markInactive()
	flushTicks()

def instantiateViewPog( newpog_name ):
	"""
	Given a Pog Name string, make a Pog object.
	
	This is the VIEW - i.e. what you are looking at.

	A VIEW Pog can be EMPTY. This happens on the first run when there is no config file.
	There are other arcane situations too, but I forget.
	"""
##	print "COMES IN to instantiateViewPog:"
##	print "newpog_name:", newpog_name
##	print "type(newpog_name):", type(newpog_name)
	
	#if state.viewobject: del state.viewobject
	if state.viewobject: state.viewobject = None
	
	if newpog_name == "EMPTY":
		ipog = fontcontrol.EmptyView()
	else:
		ipog = fontcontrol.Pog( newpog_name ) 
	## Test TARGETPOG to see if this is the same pogname
	## The not None test is for first run - there is no targetobject yet just after cli.py calls us, so we
	## do not want to access it or we get NoneType errors.
	if state.targetobject is not None and state.targetobject.name == newpog_name:
		state.samepogs = True
	else:
		state.samepogs = False
	## Must gen the Pog to get a count of items:
	## Errors raised in genList (and company): 
	## fontybugs.PogInvalid (only valid from cli pov)
	##
	## We 'handle' this by NOT catching it, pass it up.
	ipog.genList()  

	## Continue if all ok.
	state.viewobject = ipog
	## Because we have a new view object, we must reset the last filteredViewObject
	state.filteredViewObject = None

	config.lastview = newpog_name
	if len(state.viewobject) == 0:
		empty = True
		state.viewpattern = "E"
	else:
		empty = False
		state.viewpattern = "P"
		markInactive()
		flushTicks()
		
	#print "instantiateViewPog says viewpattern is:", state.viewpattern
	
	return empty # this return is only used in cli.py

def instantiateTargetPog( newpog_name ):
	"""
	The app could begin with NO TARGET POG chosen.
	After that (in the gui) either a pog is chosen or NO POG is chosen (i.e. None)
	Therefore - there can NEVER BE a targetobject called EMPTY
	
	The CLI install/uninstall/purge DO NOT use this routine.
	"""
	if state.targetobject: del state.targetobject
	ipog = fontcontrol.Pog(newpog_name) 
	## Must gen the Pog to get a count of items:
	ipog.genList() # Raises fontybugs.PogInvalid error THIS ENDS THE APP.
	## TEST the viewobject which is the stuff being 
	## LOOKED AT IN THE MIDDLE OF THE SCREEN (which could be a Pog OR a Folder)
	## If it's a Pog then we may have chosen the same Pog (on the right)
	## that we are looking at, so check that:
	state.samepogs = False
	if isinstance( state.viewobject, fontcontrol.Pog ):
		if state.viewobject.name == newpog_name:
			## The pog clicked in the TARGET is the same as what's ALREADY selected in the VIEW
			state.samepogs = True
			
	quickinstalledflag = False
	if ipog.isInstalled(): quickinstalledflag  = True
	state.targetpattern = "P" 
	state.targetobject = ipog
	markInactive()
	flushTicks()
	return quickinstalledflag

def markInactive():
	"""
	INACTIVE means the font displayed is already inside the 
	chosen target pog. So, it's not 'active', not clickable etc.
	
	Mark each font item as inactive, as needs-be.
	Clear the ticks.
	Sets the message to display in the fontmap.
	"""	
	if state.viewobject: state.viewobject.clearInactiveflags()
		
	if state.viewobject and state.targetobject:
		## What's in TARGET must be inactive in VIEW

		## glyphpaf is a BYTE STRING... :(
		## pafBlist is a list of UNICODEs
		## glyphpaf_unicode is UNICODE, so I will use it instead		
		## because we compare it to pafBlist
#TO DO : I suspect there will be subtle problems here. Too tired now to test this.		
		pafBlist = [i.glyphpaf_unicode for i in state.targetobject]

		for iA in state.viewobject:
			#print [iA.glyphpaf_unicode]
			if iA.glyphpaf_unicode in pafBlist:
				iA.activeInactiveMsg = _("This font is in %s") % state.targetobject.name
				iA.inactive = True
		del pafBlist

def SetTargetPogToNone():
	state.targetobject = None
	state.targetpattern = "N"
def SetViewPogToEmpty():
	state.viewobject = fontcontrol.EmptyView()
	state.viewpattern = "E"

def flushTicks():
	for fi in state.viewobject:
		fi.ticked = False
	state.numticks = 0

def logSegfaulters( lastPaf ):
	"""
	Writes a string to ~/.fontypython/lastFontBeforeSegfault
	"""
	paf = os.path.join( iPC.appPath(),"lastFontBeforeSegfault")
	try:
		f = open( paf, "w" )
		## Not tested yet....
		if type( lastPaf ) is unicode:
			lastPaf = lastPaf.encode( locale.getpreferredencoding() )
		f.write( lastPaf + "\n" )
		f.close()
	except:
		raise

def logBadStrings( badPaf ):
	"""
	Writes badfiles and appends strings to it.
	
	The usefulness of this routine is questioned. What does it acheive?
	It's really storing names that can't be read under this locale,
	but that does not mean the fonts are really bad in any way.
	
	Because the app may segfault at any time, I won't keep
	this list in RAM - I open and kill duplicate lines and
	sort and write it every time.
	
	This routine fair nearly killed me. Unicode issues! Damn.
	"""
	#print "BADPAF IS:", [badPaf]
	## badPaf comes in BYTE STRING 99% of the time
	## There are some corners where a UNICODE is sent-in
	## I am writing an ASCII file. Oh great FSM, what am I gonna noodle now?
	if type(badPaf) is unicode:
		badPaf = badPaf.encode( locale.getpreferredencoding() )
	
	paf = os.path.join( iPC.appPath(),"badfiles")
	
	try:
		if os.path.exists( paf ):
			#read it
			fr = open( paf, 'r' ) # byte string only ascii file
			tmp = fr.read().split("\n")
			fr.close()
			tmp.append( badPaf )
			uniquelines =  list( set( tmp ) )# remove dupes
		else:
			uniquelines = []
			uniquelines.append( badPaf )
		try:
			uniquelines.sort( cmp = locale.strcoll )
		except:
			print "CORNER CASE ERROR in logBadStrings:"
			print sys.exc_info()
			raise SystemExit
		
		#Remove dupes, write.
		fw = open( paf, "a" ) # byte string ascii
		bytestring = "".join([line + "\n" for line in uniquelines if line != ""])
		fw.write( bytestring )
		fw.close()

	except:
		print "CORNER CASE ERROR in logBadStrings:"
		print sys.exc_info()
		raise SystemExit
		
