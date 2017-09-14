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

import os

##Sept 2017 - Trying to get XDG compliance going.
from gi.repository import GLib


class PathControl:
	"""
	1. Makes the .fontypython path - in $XDG_DATA_HOME (GLib will supply this)
	2. Provide paths for fontypython on Linux
	3. Provide list of pog names (without the .pog extension)
	4. Provide a list of pog FILE names (with .pog extension)

	* All these vars contain/return BYTE STRING paths and files.

	NOTE We use PathControl in strings.py (which is also used in setup.py)
	These are situations in which we do not want to create the "fontypython"
	folder from this module. Hence, the make_fontypython_dir flag.

	Sept 2017: Freedesktop specs being used now:
	https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
	#>>>from gi.repository import GLib
	#>>>GLib.get_user_data_dir()
	#'/home/donn/.local/share'

	GLib:
	https://developer.gnome.org/glib/2.40/glib-Miscellaneous-Utility-Functions.html#g-get-user-data-dir
	"""
	__FIRSTRUN = True
	__HOME = os.environ["HOME"] # Is a byte string under Linux.
	__xdgdatahome_fonts = "unset" # will be in XDG_DATA_HOME/fonts
	__xdgdatahome_fontypython = "unset" # will be in XDG_DATA_HOME/fontypython
	__xdgdatahome_fpconf = "unset" # will be in XDG_DATA_HOME/fontypython, fuck it.
	__XDG_DATA_HOME = "unset" #Supposed to be preset to "$HOME/.local/share"

	def __init__(self, frm="unknown", make_fontypython_dir=True ):

		## Use Glib to get the XDG data path:
		PathControl.__XDG_DATA_HOME = GLib.get_user_data_dir() # What kinds of errors happen here?

		if not os.path.exists(PathControl.__XDG_DATA_HOME):
			## XDG_DATA_HOME has a value, but it's not actually on the file system...
			## Let's make .local/share. Fuck it:
			hack = PathControl.__XDG_DATA_HOME
			try:
				os.makedirs( hack )
			except e:
				return {"XDG_STATUS":"FAIL", "REASON":_(u"Couldn't make the directory \"{}\". Please check your write permissions, or create it yourself, and try again.\n{}".format( hack, unicode(e) ))}


		## At this point we defs have ~/.local/share/


		# byte strings
		PathControl.__xdgdatahome_fontypython = PathControl.__XDG_DATA_HOME + "/fontypython/"
		PathControl.__xdgdatahome_fpconf = PathControl.__XDG_DATA_HOME + "/fontypython/fp.conf"
		PathControl.__xdgdatahome_fonts = PathControl.__XDG_DATA_HOME + "/fonts"

		## Now have a better way to detect the very first run of this code:
		## by using a class variable. The tests and creation of the 
		## fontypython directory are sane now.
		## 
		## FYI: Instantiations of PathControl in order:
		##  PathControl instanced from: strings
		##  PathControl instanced from: fpsys
		##  PathControl instanced from: cli
		if PathControl.__FIRSTRUN:
			PathControl.__FIRSTRUN = False

			## (I can't access the config object from here because it's in fpsys
			## which imports this code, so it's all loopy. Instead of saving some
			#  XDG_compliance_vers in config, I will just repeat the test for the old 
			## ~/.fontypython path every time. Yay! \o/
			## If found = old system; move shit.
			self.XFG_upgrade_status_dict = self.upgrade_to_XDG_std()

		## April 2012 - Kartik Mistry (kartik@debian.org)
		## informed me there was a bug in some esoteric build
		## of some voodoo Debian process and that I should
		## simply skip the check and creation of .fonts directory.

		## EDIT
		## August 2012
		## If there is no .fonts dir, install pog fails. The cursor keeps busy and nothing
		## further happens. Here my suggestion: only perform a test, without creating the dir.

		## June 25, 2016
		## Some distros do not have the .fonts directory by default. :( :O
		## This is a disaster. 
		## Remarked Michael's edit. Moved the test for missing .fonts dir to
		## fontcontrol.py in the install() function

		## Sept 2017
		## ===
		## Added this flag so I can test in wxgui when I draw the status bar,so
		## it can warn user about the situation.
		self.no_fonts_dir_found = not os.path.exists( PathControl.__xdgdatahome_fonts )


		## Make XDG_DATA_HOME/fontypython
		if make_fontypython_dir:
			if not os.path.exists(PathControl.__xdgdatahome_fontypython):
				try:
					os.makedirs(PathControl.__xdgdatahome_fontypython) #using makedirs - just in case.
				except:
					print _("""
Couldn't make the folder in %s
Please check your write permissions and try again.""") % PathControl.__xdgdatahome_fontypython
					raise SystemExit

	def appPath(self):
		""" Kind of spastic, but I was in a get/set mode"""
		return PathControl.__xdgdatahome_fontypython

	def appConf(self):
		return PathControl.__xdgdatahome_fpconf

	def getPogNames(self):
		## We pass a byte string path to os.listdir therefore this function
		## return a LIST OF BYTE STRINGS.
		return [ f[0:-4] for f in os.listdir(PathControl.__xdgdatahome_fontypython) if f.endswith(".pog") ]

	def userFontPath(self):
		return PathControl.__xdgdatahome_fonts

	def home(self) :
		return PathControl.__HOME


	def upgrade_to_XDG_std(self):
		"""
		Move Fonty's config files to the new XDG_CONFIG_HOME path.
		Move the old ~/.fonts for to the new XDG_DATA_HOME path.
		"""
		if not os.path.exists(PathControl.__HOME + "/.fontypython"):
			return {"XDG_STATUS":"OK"}

		## fpsys.config.XDG_compliance_vers = 1 # goddam. Can't reach config from here.
		print _("Detected an old version of Fonty.\nMoving files to new locations in {}. This should only happen once.")
		import shutil
		olddotfonty = PathControl.__HOME + "/.fontypython"
		newfonty = PathControl.__XDG_DATA_HOME + "/fontypython"
		## I am not going to catch the error. Let it barf and quit.
		shutil.move( olddotfonts, newfonty )

		olddotfonts = PathControl.__HOME + "/.fonts"
		newfonts = PathControl.__XDG_DATA_HOME + "/fonts"

		## newfonts may already exist...
		if not os.path.exists( newfonts ):
			## It's not there...
			## Do I make it? Complain to user? Shit...
			return {"XDG_STATUS":"FAIL","REASON":_("There is no \"fonts\" directory in {}. Please make it yourself and start me again.".format( newfonts ))}


		## * Must go through all my installed Pogs and relink them into newfonts...
		if os.path.exists(olddotfonts):
			blah
		else:
		#pass
		"""
		This is among the very FIRST things we do.
		Fill the list with pogs.
		This will CULL any bad pogs (i.e. those with malformed content)
		Thus the PogInvalid error should not happen any more after a run.
		"""
		pl = self.__PC.getPogNames() # pl will always be a BYTE STRING list

		for p in pl: # 'p' is a byte string.
			ipog = fontcontrol.Pog(p)
			try: #catch pogs that are not properly formed
				if ipog.isInstalled(): i = 1 # isInstalled opens the pog file.
				else: i = 0
			except fontybugs.PogInvalid, eInst:
				## An "invalid" pog is one that does not have
				## installed/not installed on the first line.
				print _(u"(%s) skipped. It's an invalid pog.") % [p]
				continue

			## Let's try to make a unicode of p so li.SetText(p) can display it:
			try:
				p = fpsys.LSP.to_unicode( p )
			except UnicodeDecodeError:
				## We can't convert it under this locale
				print _(u"(%s) skipped. I can't display this name under your locale.") % [p]
				continue
			## Okay, we have a valid pog name to use:


		return {"XDG_STATUS":"OK"}



