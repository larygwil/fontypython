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

class PathControl:
	"""
	1. Makes the .fontypython path
	2. Provide paths for fontypython on Linux
	3. Provide list of pog names (without the .pog extension)
	4. Provide a list of pog FILE names (with .pog extension)
	
	* All these vars contain/return BYTE STRING paths and files.
	"""
	
	def __init__(self, makeFolder=True ):
		## __HOME will be a BYTE STRING (Under Linux)
		self.__HOME = os.environ['HOME']
		
		self.__fphomepath = self.__HOME + "/.fontypython/" # byte string
		self.__fpconffile = self.__HOME + "/.fontypython/fp.conf" # byte string
		
		## Is there a .fonts folder ?
		if not os.path.exists(self.__HOME + "/.fonts"):
			## We gotta make it.
			try:
				os.mkdir(self.__HOME + "/.fonts")
			except:
				print _("""
Couldn't make the .fonts folder in %s
Please check your write permissions and try again.""") % self.__HOME
				raise SystemExit
		self.__userfontpath = self.__HOME + "/.fonts"
		
		## Make ~/.fontypython
		if makeFolder:
			if not os.path.exists(self.__fphomepath):
				try:
					os.makedirs(self.__fphomepath) #using makedirs - just in case.
				except:
					print _("""
Couldn't make the folder in %s
Please check your write permissions and try again.""") % self.__fphomepath
					raise SystemExit
			
	def appPath(self): 
		""" Kind of spastic, but I was in a get/set mode"""
		return self.__fphomepath
		
	def appConf(self): 
		return self.__fpconffile
		
	def getPogNames(self): 
		## We pass a byte string path to os.listdir therefore this function
		## return a LIST OF BYTE STRINGS.
		return [ f[0:-4] for f in os.listdir(self.__fphomepath) if f.endswith(".pog") ]

	def userFontPath(self): 
		return self.__userfontpath
		
	def home(self) : 
		return self.__HOME
