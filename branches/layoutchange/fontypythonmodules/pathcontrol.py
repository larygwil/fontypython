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
	__userfontpath = "unset" # will be in XDG_DATA_HOME/fonts
	__fphomepath = "unset" # will be in XDG_DATA_HOME/fontypython
	__fpconffile = "unset" # will be in XDG_DATA_HOME/fontypython, fuck it.
	__XDG_DATA_HOME = "unset"

	def __init__(self, frm="unknown", make_fontypython_dir=True ):
		## Use Glib to get the XDG data path:
		PathControl.__XDG_DATA_HOME = GLib.get_user_data_dir() # What kinds of errors happen here?
		if not os.path.exists(PathControl.__XDG_DATA_HOME):
			## Well, fuck...
			print _("Your hovercraft is full of eels.\n{} is missing. I don't know what to do.\nTry making that directory yourself; then run me again.".format(PathControl.__XDG_DATA_HOME))
			raise SystemExit

		PathControl.__fphomepath = PathControl.__XDG_DATA_HOME + "/fontypython/" # byte string
		PathControl.__fpconffile = PathControl.__XDG_DATA_HOME + "/fontypython/fp.conf" # byte string
		PathControl.__userfontpath = PathControl.__XDG_DATA_HOME + "/fonts"

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
			if os.path.exists(PathControl.__HOME + "/.fontypython"):
				self.upgrade_to_XDG_std()

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
		self.missingDotFontsDirectory = not os.path.exists( PathControl.__userfontpath )


		## Make XDG_DATA_HOME/fontypython
		if make_fontypython_dir:
			if not os.path.exists(PathControl.__fphomepath):
				try:
					os.makedirs(PathControl.__fphomepath) #using makedirs - just in case.
				except:
					print _("""
Couldn't make the folder in %s
Please check your write permissions and try again.""") % PathControl.__fphomepath
					raise SystemExit

	def appPath(self):
		""" Kind of spastic, but I was in a get/set mode"""
		return PathControl.__fphomepath

	def appConf(self):
		return PathControl.__fpconffile

	def getPogNames(self):
		## We pass a byte string path to os.listdir therefore this function
		## return a LIST OF BYTE STRINGS.
		return [ f[0:-4] for f in os.listdir(PathControl.__fphomepath) if f.endswith(".pog") ]

	def userFontPath(self):
		return PathControl.__userfontpath

	def home(self) :
		return PathControl.__HOME


	def upgrade_to_XDG_std(self):
		"""
		Move Fonty's config files to the new XDG_CONFIG_HOME path.
		Move the old ~/.fonts for to the new XDG_DATA_HOME path.
		"""
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
		## * Must go through all my installed Pogs and relink them into newfonts...
		if os.path.exists(olddotfonts)
		pass
