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

import os,  subprocess

class CharMapApp(object):
	'''
	Base class for whatever character viewer apps I may support.
	'''
	def __init__( self, appname ):
		self.appname = appname
		self.is_installed = self.do_i_exist()
	def do_i_exist( self ):	
		for path in os.environ.get('PATH', '').split(':'):
			if os.path.exists(os.path.join(path, self.appname)) and \
					not os.path.isdir(os.path.join(path, self.appname)):
				return True
		return False
	def OpenApp( self, *args ): pass
	def Cleanup( self ): pass
	def Run( self, cmd ):
		proc = subprocess.Popen( cmd, shell=False )

		## gucharmap: Fonty actually holds still and waits here until gucharmap is closed.
		## kfontview: Fonty just runs-through. kfontview is a different beast.
		## Both still work and Fonty stays active. Multiple instances of the viewers can be opened!
		proc.wait()

class UnsetCharMap( CharMapApp ):
	'''
	A dud app -- this is here for convenience.
	'''
	def do_i_exist( self ):
		return True

class Gucharmap( CharMapApp ):
	'''
	The wiring needed to support gucharmap.
	It requires a dodge before and after spawning the app --
	  one must temporarily install the font to be viewed
	  and then remove it again afterwards.
	'''
	def OpenApp( self, *args ):
		src=args[0]
		dest=args[1]
		self.dest = dest
		fam=args[2]
		sz=args[3]

		cmd = [ self.appname, u'--font=%s, %s' % (fam, sz)]
		
		## gucharmap requires the font to be installed already, so fake it:
		self.already_installed = False
		try:
			os.symlink( src, dest )
		except OSError, detail:
			if detail.errno != 17:
				# Not 17 means the link failed, don't open the charmap
				return False
			else:
				# Error 17: file exists.
				# User may have installed it previously (or something).
				self.already_installed = True
		self.Run( cmd )
	def Cleanup( self ):
		# Remove the fake installed font -- if it's a candidate:
		if not self.already_installed:
			try:
				os.unlink( self.dest )
			except:
				# What to do? Start yelling? Nah...
				pass

class Kfontview( CharMapApp ):
	'''
	Wiring for kfontview -- really easy to use.
	'''
	def OpenApp( self, *args ):
		url=args[0]
		dest=args[1]
		fam=args[2]
		sz=args[3]

		cmd = [ self.appname, u'%s' % url]
		self.Run( cmd )


## Oct 2009
class CharMapController(object):
	'''
	Control the character map viewing objects (above) that Fonty supports.
	UNSET is always the initial "chosen app" when this instantiates.
	'''
	def __init__( self, config_callback ):
		self.config_callback = config_callback
		
		SUPPORTED_CHAR_MAP_APPS = { "UNSET": UnsetCharMap, "gucharmap":Gucharmap, "kfontview":Kfontview }
		## Which of the supported apps are actually available?
		self.AVAILABLE_APP_DICT = {}
		for appname, klass in SUPPORTED_CHAR_MAP_APPS.iteritems():
			## Instantiate an app class:
			i = klass( appname )
			## At minimum UnsetCharMap will be in there. len(dict) == 1
			if i.is_installed: self.AVAILABLE_APP_DICT[appname] = i

		## If len is 1 then *only* UnsetCharMap is in there.
		## This means there are no available apps to use.
		self.APPS_ARE_AVAILABLE = False if len(self.AVAILABLE_APP_DICT) == 1 else True

		self.__CURRENT_APPNAME = "UNSET"
		self.QUICK_APPNAME_LIST = self.AVAILABLE_APP_DICT.keys()
		self.QUICK_APPNAME_LIST.remove("UNSET")

	def SET_CURRENT_APPNAME(self, x):
		if x == "UNSET" and self.APPS_ARE_AVAILABLE:
			x = self.QUICK_APPNAME_LIST[0]
		self.__CURRENT_APPNAME = x
		self.config_callback( x ) ## go set the config's app_char_map var too.

	def CURRENT_APPNAME( self ):
		if self.__CURRENT_APPNAME == "UNSET":
			x = self.QUICK_APPNAME_LIST[0]
			return x
		else:
			return self.__CURRENT_APPNAME

	def GetInstance( self ):
		## Fetch an instance from my dict 
		return self.AVAILABLE_APP_DICT[ self.__CURRENT_APPNAME ]

