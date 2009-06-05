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

import os, sys, locale, glob
import Image, ImageFont, ImageDraw 
import fontybugs, fpsys
from pathcontrol import *

class FontItem( object ):
	"""
	Represents a single font file. It has the ability to provide a font image
	and query a font file for the family name and style.
	
	Ancestor to the specific classes per font type.
	Never instantiate one directly.
	"""
	def __init__(self, glyphpaf ):
		## glyphpaf must be whatever it is. unicode or a byte string
		## This is used to access files themselves.
		## When the LANG encoding is utf8, its Unicode.

		self.glyphpaf = glyphpaf
		#print "FontItem init, glyphpaf:", [glyphpaf]
		## I want to have a var I can use when I display the glyphpaf
		## either in the gui or onto the cli. This should be a unicode
		## object, so I must make sure of it's type before I do so.
		if type(glyphpaf) is str:
			## It's a byte string, not unicode. Convert it.
			self.glyphpaf_unicode = glyphpaf.decode(locale.getpreferredencoding(), "replace")
		else:
			self.glyphpaf_unicode = glyphpaf

		## The same goes for name. It *must* be unicode.
		self.name = os.path.basename ( glyphpaf )
		if type(self.name) is str:
			self.name = self.name.decode(locale.getpreferredencoding(), "replace")
			
		self.ticked = False # State of the tick/cross symbol.
		self.inactive = False # Set in fpsys.markInactive()
		self.msg = "" #Say something unique when I draw this item.  
		
		## These are lists to cater for sub-faces
		self.family, self.style =  [], []
		self.numFaces = 0
		self.pilheight, self.pilwidth = 0,0
		
		## I'm not bad in any way, until I turn bad that is :)
		self.badfont = False
		## If I'm bad, what should I say?
		self.badfontmsg = ""
		## What kind of bad to the bone am I?
		## One of FILE_NOT_FOUND, PIL_IO_ERROR, PIL_UNICODE_ERROR, PIL_CANNOT_RENDER
		self.badstyle = "" 
		
		## We need the family name and style to be fetched
		## because we have that filter thingy in the gui
		## and it uses those strings to search for terms.
		##
		## We also want to know what flavour of bad this item will be
		## and we must open the file and query it to know that.
		self.__queryFontFamilyStyleFlagBad()
		
	def __queryFontFamilyStyleFlagBad( self ):
		"""
		Get the family, style and size of entire font.
		
		If this font has a problem (PIL can't read it) then we set the
		badfont flag, along with the badstyle & badfontmsg vars.
		
		badstyle: FILE_NOT_FOUND, PIL_IO_ERROR, PIL_UNICODE_ERROR
		
		The last kind of badstyle is set in generatePilFont() and is
		set to: PIL_CANNOT_RENDER
		
		This is tricky because FontImage.getname() is fragile
		and apt to segfault. As of Dec 2007 I have reported
		the bug, and a patch has been written but I don't
		know how it will be implemented yet.
		
		NB: InfoFontItem overrides this so it does not happen
		in that case. This is why I made this a method and not
		simply part of the __init__ above.
		"""
		
		i = 0
		## Step through all subfaces.
		#print "BUILDING:", [self.glyphpaf]
		while True:
			try:
				fileDoesExist = os.path.exists( self.glyphpaf )
				if not fileDoesExist:
					fpsys.logBadStrings( self.glyphpaf )
					self.badfont = True
					self.badfontmsg = _("Font cannot be found, you should purge it.")
					self.badstyle = "FILE_NOT_FOUND"
					## If the multi face font is damaged after the
					## first face, then this won't catch it...
					break # it's at the end of the sub-faces 
			except:
				print _("Unhandled error:\nPlease move (%s) away from here and report this to us.") % self.glyphpaf
				raise
			try:
				font = ImageFont.truetype(self.glyphpaf, 16, index=i, encoding="unicode" )  
			except IOError: 
				"""
				Means the ttf file cannot be opened or rendered by PIL !
				NOTE: Sets badfont
				"""
				if i == 0: # fubar on the first face:
					self.badfont = True
					self.badfontmsg = _("Font may be bad and it cannot be drawn.")
					self.badstyle = "PIL_IO_ERROR"
					## If the multi face font is damaged after the
					## first face, then this won't catch it...
				break # it's at the end of the sub-faces
			except UnicodeEncodeError:
				"""
				NOTE: Sets badfont
				"""				
				## Aw man! I thought I had this taped. This error does not *seem* to
				## be related to the encoding param passed to ImageFont. I have
				## mailed the PIL list about this.
				##
				## In the meantime, this will have to be flagged as a bad font.
				fpsys.logBadStrings( self.glyphpaf )
				self.badfont = True
				self.badfontmsg = _("Font may be bad and it cannot be drawn.")
				self.badstyle = "PIL_UNICODE_ERROR"
				break

			except:
				## What next on the error pile?
				print "CORNER CASE in FontItem.__queryFontFamilyStyleFlagBad:", [self.glyphpaf]
				print sys.exc_info()
				raise
				## Abort the app because this is an unhandled PIL error of some kind.
			if not self.badfont:
				## *If* 'check' is run, there will be a file containing pafs of the
				## fonts that segfault PIL. (To my best knowledge, at least.)
				## This file is held in the 'segfonts' list - opened in fpsys
				
				## So, before we do a getname and cause a segfault, let's
				## see whether that font is in segfonts, and if so, skip it.
				if self.glyphpaf not in fpsys.segfonts:
					## No point Try-ing here, this segfaults when style/family is Null.
					fpsys.logSegfaulters( self.glyphpaf ) # record the potential destroyer of apps!
					self.family.append( font.getname()[0] )
					self.style.append( font.getname()[1] )
					i += 1
				else:
					## It WAS in the list! So, we can flag it and get on with life :)
					#print "SKIPPING:",[self.glyphpaf]
					self.badfont = True
					self.badfontmsg = _("Font causes a segfault. Fix or remove it.")
					self.badstyle = "PIL_SEGFAULT_ERROR"
					break
				
		self.numFaces = i
				
	#def generatePilFont( self, width, maxHeight, enc="unicode" ):
	def generatePilFont( self, maxHeight, enc="unicode" ):
		"""
		This function seems too similar to the __queryFontFamilyStyleFlagBad one
		and in many ways it is. I am forced to work with PIL and it's not ideal
		at the moment.
		
		This function is called from the GUI in a tight loop. It provides (generates)
		pilimage objects with the font's text rendered onto them.
		
		Fonts that cause errors are marked 'badfont' and provide no image.
		They can then be 'displayed' and can be put into Pogs etc., but they cannot
		be seen.
		
		"""
		## text gets extra spaces at the end to cater for cut-off characters.
		paf, points, text = self.glyphpaf, fpsys.config.points, " " + fpsys.config.text + "  "
		i = 0
		while (True):
			try:
				font = ImageFont.truetype(paf, points,index=i, encoding=enc) 
				w,h = font.getsize( text )
				## Some fonts (50SDINGS.ttf) return a 0 width.
				## I don't know exactly why, it could be it could not render
				## any of the chars in text.
				if int(w) == 0: 
					w = 1
				pilheight = int(h)
				pilwidth = int(w)
				pilheight = min( pilheight, maxHeight )
				pilimage = Image.new("RGB", (pilwidth, pilheight), (255,255,255)) 
				
				if self.inactive:
					col = (230, 230, 230) 
				else:
					col = 0
					
				## text = os.path.basename(self.glyphpaf)
				
				## Well, I have since discovered that some fonts
				## cause a MemoryError on the next command:
				drawnFont = ImageDraw.Draw( pilimage ) # Draws INTO pilimage
				drawnFont.text((0,0) , text, font=font, fill=col) 
				
				## All is well, so we step ahead to the next *potential* sub-face
				## and return the font image data.
				i += 1
				yield pilimage, pilheight, pilwidth

			except MemoryError:
				"""
				NOTE: Sets badfont

				This one CAN ONLY BE CAUGHT HERE.
				**IDEALLY**, it should have been caught in __queryFontFamilyStyleFlagBad
				but for reasons explained below, it cannot.
				So, we have a badfont flag being set here too :(
				"""
				## I found a font throwing a MemoryError (Onsoku Seinen Plane.ttf)
				## that only happens upon the .text() command.
				##
				## UPDATE: Clever tricks don't work. Onsoku *only* barfs on "TE" and not
				## "A" or even chr(0) to chr(255) all in a string...
				## So, it's virtually impossible to know at this point what will
				## cause the MemoryError in the rendering step.
				self.badfontmsg = _("Font cannot be drawn.")
				self.badstyle = "PIL_CANNOT_RENDER"
				fpsys.logBadStrings( self.glyphpaf )
				self.badfont = True
				break
			## These two must be caught, but are already known about 
			## from the exact same test in __queryFontFamilyStyleFlagBad
			except IOError: 
				## The font at index (i==0) cannot be opened.
				break				
			except UnicodeEncodeError:
				## Already handled in __queryFontFamilyStyleFlagBad
				break
				
	def __str__( self ):
		return self.glyphpaf
		
## Create some subclasses to represent the fonts that we support:		
class InfoFontItem( FontItem ):
	"""
	This class is only instantiated in wxgui.CreateFitmaps 
	It's used to indicate when a Folder or Pog is EMPTY and
	if a single font is bad in some way.
	
	It's the only Font Item in the target or source view list
	at that time.
	"""
	def __init__( self, TYPE, glyphpaf="" ):
		## TYPE is: EMPTY (no fonts to display)
		FontItem.__init__( self, glyphpaf )
		self.TYPE = TYPE
	def __queryFontFamilyStyleFlagBad( self ):
		"""
		Overridden so that it does not happen for this class.
		"""
		pass
	def errorText ( self ):
		if self.TYPE == "EMPTY":
			l1 = _("There are no fonts to see here, move along.")
			l2 = _("(Check your filter!)")
			return ( l1, l2 )

class TruetypeItem( FontItem ):
	def __init__( self, glyphpaf ):
		FontItem.__init__( self, glyphpaf )
		
class TruetypeCollectionItem( FontItem ):
	def __init__( self, glyphpaf ):
		FontItem.__init__( self, glyphpaf )

class OpentypeItem( FontItem ):
	def __init__( self, glyphpaf ):
		FontItem.__init__( self, glyphpaf )
	  
class Type1Item( FontItem ):
	def __init__( self, glyphpaf, metricpaf=None ):
		FontItem.__init__( self, glyphpaf )
		self.metricpaf = metricpaf
		
def itemGenerator( fromObj, sourceList ):
	"""
	Prepare for hell...
	This is a *generator* function that yields a FontItem 
	instantiated according to the type of the font.
	Call it once-off, or in a loop, to get one FontItem after another.
	Pass it a sourceList that contains pafs.
	
	VERY NB:
	When the app is run from a utf8 locale, this func generates 
	UNICODE glyphpaf vars.
	When run from C/POSIX/None it generates BYTE STRING glyphpaf vars.
	
	sourceList is not a predictable beast. It comes in mixed strings/unicode
	"""
	#print "sourceList comes in:",[sourceList]
	#print
	
	def ext(s): return s.split(".")[-1].upper()
	def stripExt(s): return s[:s.rfind(".")]
	
	listOfItemsGenerated = []
	
	## So, [paf,paf,paf,paf,paf] comes in.
	
	## If it comes from FOLDER then it's full of ALL the files in a single dir.
	##  NB: It may or may not include 'type1' files and their 'metrics'
	
	## If it comes from POG then it's just pafs of the basic glyph files
	## thus it does not include the afm/pfm files.
	##  So: this is a special case.
	##  We must "fill-up" the list with the 'metric' files that are matched
	##  to Type1 files - i.e. AFM and PFM files that belong to the fonts 
	##  of type 'type1' which we are detecting by extension as ".pfb" and ".pfa"
	if isinstance( fromObj, Pog ):
		tmp = []
		for paf in sourceList:
			## paf : /some/path/somefont.pfb (or .ttf, or whatever. Do them all.)
			tmp.append( paf ) # add it to what will replace sourceList
			dir = os.path.dirname( paf ) # /some/path
			filename = os.path.basename( paf ) # somefont.pfb
			## Find metric files with his name in his dir
			wild = os.path.join( dir, stripExt(filename) + ".[PpAa][Ff][Mm]" )
			metricfiles = glob.glob( wild )
			## Add what we find (if anything) to the tmp list
			for metric in metricfiles:
				tmp.append( metric ) # merge them in
		## Replace the sourceList
		del( sourceList )
		sourceList = tmp
	
	## Now we have a sourceList that is complete - full of files
	
	## TYPE1 stuff. 10 Jan 2008
	## Jump through hoops to find the 'metric' files (AFM then PFM)
	## for each Type1 font that's in the list
	##
	## As per advice on the freetype list I am doing this:
	## For every PFA/PFB file, I look for a matching path and filename
	## starting with AFM extensions, then trying PFM extensions.
	## AFM is preferred over PFM.
	## Make Type1Item objects and associate the 'metric' file found (or none)
	
	## Filter some lists from sourceList to step through:
	PFABs= [[stripExt(e),e] for e in sourceList if ext(e) in ("PFA","PFB")] # all type1 files
	AFMs = [[stripExt(e),e] for e in sourceList if ext(e) in ("AFM")] # all AFM metric files
	PFMs = [[stripExt(e),e] for e in sourceList if ext(e) in ("PFM")] # all PFM metric files
	
	## Those lists look like this:
	##  ["/some/path/file", "/some/path/file.pfa"]
	##  [0] is paf sans extension, [1] is all of it (*)
	##  (*) We have to worry about case sensitivity, so I store more data.

	## Go through the (maybe empty) list of PFA and FPB files
	for pfab_tup in PFABs:
		foundAFM = False
		## Looking for AFM files
		for afm_tup in AFMs:
			if afm_tup[0] == pfab_tup[0]:
				## We have found an afm file for this pfa/pfb file
				## so make an object
				fi = Type1Item( pfab_tup[1], metricpaf = afm_tup[1] )
				listOfItemsGenerated.append( fi )
				foundAFM = True
				break
		## If we found no AFM then try find a PFM
		foundPFM = False
		if not foundAFM:
			## Looking for PFM files
			for pfm_tup in PFMs:
				if pfm_tup[0] == pfab_tup[0]:
					## We have found pfm file for it, make an object
					fi = Type1Item( pfab_tup[1], metricpaf = pfm_tup[1] )
					listOfItemsGenerated.append( fi )
					foundPFM = True
					break
		## If we found neither:
		if not foundAFM and not foundPFM:
			## Just make an object without a metric file associated.
			fi = Type1Item( pfab_tup[1], metricpaf = None )
			listOfItemsGenerated.append( fi )

	## Do the other font types
	TTFList = [ paf for paf in sourceList if ext(paf) == "TTF" ]
	if len(TTFList) > 0:
		for paf in TTFList:
			fi = TruetypeItem( paf )
			listOfItemsGenerated.append( fi )
				
	OTFList = [ paf for paf in sourceList if ext(paf) == "OTF" ]
	if len(OTFList) > 0:
		for paf in OTFList:
			fi = OpentypeItem( paf )
			listOfItemsGenerated.append(fi)
			
	TTCList = [ paf for paf in sourceList if ext(paf) == "TTC" ]
	if len(TTCList) > 0:
		for paf in TTCList:
			fi = TruetypeCollectionItem( paf )
			listOfItemsGenerated.append(fi)
	
	## NB: listOfItemsGenerated can contain MIXED byte strings/unicode
	
	## Sort the list: I use the glyphpaf_unicode var becuase it's unicode only.
	listOfItemsGenerated.sort( cmp=locale.strcoll, key=lambda obj:obj.glyphpaf_unicode ) # Try to sort on that field.

	## Supply it: This is pure magic!
	for fi in listOfItemsGenerated:
		yield fi


class BasicFontList(list):
	"""
	Ancestor to the Pog and Folder classes.
	"""
	def clear(self):
		del self[:] # works. It was real touch and go there for a while.
	def clearInactiveflags(self):
		for fi in self:
			fi.inactive = False

class EmptyView(BasicFontList):
	"""
	Imitates an empty Pog or an empty Folder.
	"""
	def __init__(self): 
		BasicFontList.__init__(self)
		
		## Public properties:
		self.name = "EMPTY"
		self.installed = False
		self.empty = True
		
	def label(self):
		return str(self.name)
	####
	## generate the list
	def genList(self):
		return 
		
	def isInstalled(self):
		return False


class Folder(BasicFontList):
	"""
	Represents an entire Folder (from a path given by user clicking on the
	GenericDirCtrl or from a commanline string.)
	
	This is called from fpsys.instantiateViewFolder
	
	Contains a list of various FontItem Objects.
	Supply the path
	"""
	def __init__(self, path):
		BasicFontList.__init__(self)
		#print "path:",[path]
		
		## I still have to verify this, but:
		## I reckon path is always coming in as unicode.
		## From the gui, it's unicode anyway cos of the dir control.
		## From the cli, I converted args to unicode there.
		self.path = os.path.abspath(path) # fix relative paths

		## NEW INFO : DEC 2007
		## Linux is Posix and that means all filenames are stored as byte strings
		## "Unlike Windows NT/2000/XP, which always store filenames in Unicode format, 
		##  POSIX systems (including Linux) always store filenames as binary strings. 
		##  This is somewhat more flexible, since the operating system itself doesn't 
		##  have to know (or care) what encoding is used for filenames. The downside 
		##  is that the user is responsible for setting up their environment 
		##  ("locale") for the proper coding."
		##
		## On Linux: os.path.supports_unicode_filename is always == True
		## On my system, with LANG=en_ZA.utf8
		## >>> locale.getpreferredencoding()
		## 'UTF-8'
		##	Return the charset that the user is likely using,
		##	according to the system configuration.
		## With LANG=C it returns "ANSI****"
		## On my system:
		## >>> sys.getfilesystemencoding()
		## 'UTF-8'
		## This one returns the ENCODING (byte string to unicode) needed to
		## convert filenames from the O/S *to* unicode.
		
		listOfFilenamesOnly = []
		## If self.path is unicode, return will be list of unicode objects (with some slip-ups...)
		## self.path comes from the GenericDirCtrl, which is part of a Unicode wxPython build
		## therefore it always emits Unicode objects. (Or it comes from cli, which also converted)
		
		## Note: If self.path DOES NOT EXIST then this raises and OSError
		##	   This can happen when we use the --all cli argument (see cli.py)
		listOfFilenamesOnly = os.listdir (  self.path  ) # Get the unicode list
		
		## I could use this:
		## sourceList = [ os.path.join( self.path, f ) for f in listOfFilenamesOnly ]
		## But I won't know (when there's an error) which element of the listOfFilenamesOnly was
		## the culprit, so I'm gonna loop this one.
		sourceList = []
		for f in listOfFilenamesOnly:
			try:
				paf = os.path.join( self.path, f )
				sourceList.append( paf )
			except:
				## Okay, 'f' was not able to join to self.path
				## This is because 'f' is a byte string, not a unicode
				## That means that os.listdir couldn't figure it out...
				## I will revert to byte strings and try again:
				#print "Could not join to path name:"
				#print [self.path], " + ", [f]
				try:
					paf = os.path.join( self.path.encode( locale.getpreferredencoding()), f )
					sourceList.append( paf )
				except:
					## No, could not get a hold of that file.
					## In theory, this should never happen.
					print "CORNER CASE in Folder.__init__:", [self.path], " + ", [f]
					fpsys.logBadStrings(f) # I'm keeping a list of bad names.

		## Now employ the generator magic:
		## Makes FontItem objects for each paf in the list.
		for fi in itemGenerator( self, sourceList ):
			#print "fi:",[fi]
			self.append(fi)
		
		if len(self) == 0:
			print "EMPTY FOLDER"
			raise fontybugs.FolderHasNoFonts(self.path)

	def __str__(self):
		return str(self.path)
		
	def label( self ):
		"""
		A handy way to refer to Folders & Pogs in certain circumstances.
		See around line 1296 wxgui.OnMainClick()
		Pog.label returns the name
		Folder.label returns the path
		"""
		return os.path.basename( self.path )
		
class Pog(BasicFontList):
	"""
	Represents an entire Pog. 
	Contains a list of various FontItems.
	Dec 2007 - adding OTF and Type 1
	Supply the pog name.
	Must call genList() if you want actual font items in the list.
	"""
	def __init__(self, name ): #, progressCallback = None):
		BasicFontList.__init__(self)
		self.__pc = fpsys.iPC # A hack to pathcontrol.
		
		## Public properties:
		##
		## name always comes in as a byte string because
		## we built the path up to .fontypython from byte strings
		
		#print "Pog create"
		#print "name coming in as:", [name] # So far, for all locales, this is always str.
		## Make a unicode of that name:
		if type(name) is str:
			uname = name.decode(locale.getpreferredencoding(),"replace")
		else:
			uname = name
		## Stores a unicode for access from other places:
		self.name = uname
		
		self.__installed = "dirty" #am I installed?
		
		## Note, name (not self.name) is used here. 
		## We are continuing to use pure byte strings for the paf
		self.paf = os.path.join( self.__pc.appPath(),name + ".pog")

		self.badpog = False #To be used mainly to draw icons and ask user to purge.
		
	def label(self):
		"""
		A handy way to refer to Folders & Pogs in certain circumstances.
		See around line 1296 wxgui.OnMainClick()
		Pog.label returns the name (in unicode)
		Folder.label return the path
		These are both the full paf of the font.
		"""		
		return self.name
	
	def __openfile(self):
		"""
		Open my pog file. Raise PogInvalid error or return a file handle.
		"""
		## NB: NO error is raised if an empty file is opened and read...
		## If there is some chronic hard drive problem, I assume Python will quit anyway...
		try:
			#print "Trying to open:", [self.paf]
			## In theory, any file can *always* be opened - no matter what
			## locale. POSIX deals only in byte strings. So, this next
			## line will never fail.
			
			## I am going to open it as an ASCII file:
			f = open( self.paf, 'r' ) # ASCII byte string file only.
		except:
			print "CORNER CASE in __openfile on paf:", [self.paf]
			print sys.exc_info()
			raise SystemExit

		## Let's see what kind of line 1 we have
		line1 = f.readline()[:-1]

		self.__installed = "dirty" # unsure as to the status

		if line1.upper() == "INSTALLED": self.__installed = "yes"

		if line1.upper() == "NOT INSTALLED": self.__installed = "no"

		if self.__installed == "dirty":
			## We have a bad pog.
			#print "ABOUT TO RENAME POG"
			self.__renameBadPog()
			raise fontybugs.PogInvalid( self.paf )

		## At this point, we have a valid pog file:
		## It has a valid line 1
		## It may or may not have paf lines below it.
		return f
		
		
	def isInstalled(self):
		"""
		Passes a raise PogInvalid error through. Any other will abort app.
		"""
		if self.__installed == "yes": return True
		if self.__installed == "no": return False
		## Else it == "dirty" and:
		## We must open the file to discover the status:
		## Will raise an error, so don't handle it, let it propogate upwards.
		f = self.__openfile() #sets __installed flag
		f.close()
		if self.__installed == "yes": return True
		if self.__installed == "no": return False		
		
	def __renameBadPog(self):
		"""
		This is a bad pog, My plan is to rename it out of the .pog namespace.
		No error detection ... yet
		"""
		newpaf =  self.paf[:-4] + ".badpog" #kick out the .pog and append .badpog
		#print "Invalid Pog : \"%s\"\nRenaming it to \"%s\"" % (self.paf, newpaf)
		os.rename(self.paf, newpaf) #just going to hope this works...
		self.paf = newpaf
		
	def genList(self):
		"""
		Generate the list of font items within myself.
		Access the disk. Build the object up. All attribs and the list of fonts.
		
		Passes any PogInvalid error directly through.
		"""
		f = self.__openfile() #sets install flag, raises PogInvalid error.
		self.clear() #clear is in basicfontlist.py

		sourceList = []
		## Right,
		## If a line of the CONTENT of f is encoded differently to what the locale is
		## then the for paf in f: line throws a UnicodeDecodeError
		## This means that paf can't be read, but perhaps others can be...
		try:
			for paf in f: #This continues from line 2 onwards ...
				paf = paf[:-1] #Strip the damn \n from the file
				sourceList.append(paf)
			f.close()  
		except UnicodeDecodeError:
			## I can't even display the paf because it's not been set
			## (paf is the last value that was read, since this is an error condition)
			## I don't think I have a choice here but to simply pass
			pass
			## Not using this anymore.
			#raise fontybugs.PogContentEncodingNotMatched( self.paf )
			
		## Now to make Fontitems out of sourceList
		for fi in itemGenerator( self, sourceList):
			self.append(fi) # store them in myself.
			
	def purge(self):
		"""
		Purge method - remove fonts in the pog that are not on disk.

		Raises
				 PogEmpty
				 PogInstalled
		"""
		## can't purge an empty pog
		if len(self) == 0:
			raise fontybugs.PogEmpty # RAISED :: PogEmpty
		## can't purge an installed pog
		if self.__installed == "yes":
			raise fontybugs.PogInstalled # RAISED :: PogInstalled
		else:
			## Let's build a new list of all the bad font items.
			badfonts = []
			for i in self:
				try: #prevent weird errors on path test...
					if not os.path.exists(i.glyphpaf) :
						badfonts.append(i) 
				except:
					pass # it's bad through-and-through! It'll be axed too.
			## Now go thru this list and remove the bad items.
			for bi in badfonts:
				#print "purging:", bi.name
				self.remove(bi) 
			self.write() 

	def install(self):
		"""
		Install the fonts in myself to the user's fonts folder.
		NOTE:
		Even if ONLY ONE font out of a gigazillion in the pog 
		actually installs, the POG == INSTALLED.
		If we have a font that cannot be sourced, flag BADPOG

		For Type1 fonts - 
			The choice I have made is:
			I will ONLY reference the PFA/B in the Pog file.
			When we install a Pog, the metric file must be sought
			in the original folder and linked.

		Raises:
			PogEmpty
			PogAllFontsFailedToInstall
			PogSomeFontsDidNotInstall
		"""		
		## We start thinking all is rosey:
		self.__installed = "yes"

		## Now we make sure ...
		if len(self) == 0: 
			self.__installed = "no"
			raise fontybugs.PogEmpty(self.name) # RAISED :: PogEmpty
		## Now we go through the guts of the pog, font by font:
		bugs = 0
		for fi in self:
			
			dirname = os.path.basename( fi.glyphpaf )
			linkDestination = os.path.join(self.__pc.userFontPath(), dirname )

			## Link it if it ain't already there.
			## I am not checking for errors on os.symlink ...
			if not os.path.exists(linkDestination):  
				if os.path.exists(fi.glyphpaf):
					os.symlink(fi.glyphpaf, linkDestination)  #Should do the trick.
					## Now, the Type1 special case, link the metric file.
					if isinstance( fi, Type1Item ):
						## It's a Type 1, does it have a metricpaf?
						if fi.metricpaf:
							linkDestination = \
							os.path.join( self.__pc.userFontPath(), os.path.basename( fi.metricpaf ) )
							os.symlink( fi.metricpaf, linkDestination )
				else:
					bugs += 1
		if bugs == len(self): # There was 100% failure to install fonts.
			## We flag ourselves as NOT INSTALLED
			self.__installed = "no"
			self.write()
			raise fontybugs.PogAllFontsFailedToInstall(self.name) # RAISED :: PogAllFontsFailedToInstall
		elif bugs > 0: 
			## Some fonts did get installed, but not all. so, we are INSTALLED
			self.write()
			raise fontybugs.PogSomeFontsDidNotInstall(self.name) # RAISED :: PogSomeFontsDidNotInstall
		self.write()

	def uninstall(self):
		"""
		Uninstall the fonts.
		NOTE:
		If any font is NOT removed POG = INSTALLED
		Any links that are not found = just ignore: They could have been removed by another pog, or this
		could have been a bad pog anyway.
		NO BAD POG flag EVER.

		Raises:
				 PogEmpty
				 PogLinksRemain
				 PogNotInstalled
		"""		
		if len(self) == 0: raise fontybugs.PogEmpty # RAISED :: PogEmpty
		bugs = 0
		if self.__installed == "yes":
			for fi in self:
				dirname = os.path.basename( fi.glyphpaf )
				link = os.path.join(self.__pc.userFontPath(), dirname )
				## Step one - look for the actual file (link)
				if os.path.exists(link):
					try:
						os.unlink(link) 
						## The Type1 special case - its AFM/PFM may be here...
						if isinstance( fi, Type1Item ):
							## It's a Type 1, does it have a metricpaf?
							## It may be None (if this pfb happens not to have had a afm/pfm.)
							if fi.metricpaf:
								pfmlink = os.path.join(self.__pc.userFontPath(), os.path.basename(fi.metricpaf))
								if os.path.exists( pfmlink ):
									os.unlink( pfmlink )					 
					except: # e.g. Permission denied [err 13]
						## Only bugs that imply that the file is THERE but CANNOT BE REMOVED
						## are classified as bugs. We are making a sweeping assumption here.
						bugs += 1
			## Okay, we are currently INSTALLED, so what is the result of the loop?
			if bugs > 0:
				## We still have fonts in the pog that could NOT be removed, ergo we stay INSTALLED
				raise fontybugs.PogLinksRemain(self.name)  # RAISED :: PogLinksRemain
			else:
				## Okay - there were no problems, so we are now done.
				self.__installed = "no"
				self.write() #save to disk
		else:
			## self.__installed says we are not installed:
			raise fontybugs.PogNotInstalled(self.name) # RAISED :: PogNotInstalled
			

	def write(self) :
		"""
		Write a pog to disk.
		"""
		try:
			f = open( self.paf, 'w' ) # Going to make the contents ASCII only. Byte strings.
			i = "not installed\n"
			if self.__installed == "yes":
				i = "installed\n"
			f.write(i) 
			#Now write the font pafs
			for i in self:
				## since the glyphpaf can vary it's type
				## we must encode it to a byte string if it's unicode.
				if type(i.glyphpaf) is unicode:
					gpaf = i.glyphpaf.encode( locale.getpreferredencoding() )
				else:
					gpaf = i.glyphpaf
				f.write( gpaf + "\n") 
			f.close() 
		except:
			raise
			raise fontybugs.PogWriteError(self.paf)

	def delete(self):
		"""
		Delete my pogfile, then clean myself up, ready to be destroyed.		
		"""
		try:
			os.unlink(self.paf)
		except:
			raise fontybugs.PogCannotDelete(self.paf)
		self.clear()
		self.__installed = "no"
