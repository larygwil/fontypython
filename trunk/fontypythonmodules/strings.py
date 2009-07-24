# This Python file uses the following encoding: utf-8
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


import pathcontrol 
import fpversion
import os

copyright = "Fonty Python Copyright (C) 2006, 2007, 2008, 2009 Donn.C.Ingle"
contact = "email: donn.ingle@gmail.com"
done = "Done."

## We use PathControl to get some info, BUT we DO NOT WANT TO MAKE
## the ~/.fontypython folder from this module.
## This module (strings) also gets used via setup.py
## and that has the result of making the folder with root ownership! Bad news.
## So, there is a new flag to manage this now:
_pc = pathcontrol.PathControl( makeFolder=False )

version = _("Fonty Python version %s") % fpversion.version

warranty = """This program is distributed in the
hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR
PURPOSE.  See the GNU General Public License for
more details."""

aboutText = "%s\n%s\nWritten on Gnu\Linux, using wxPython.\n\n%s" % (copyright, version, warranty)

options=_("""Options:
  -v --version  Show program's version number and exit.
  -h --help	 Show this help message and exit.
  -e --examples
				Show some %$@#$ examples!
  -i pog --install=pog
				Install the fonts in this pog to your 
				fonts folder.
  -u pog --uninstall=pog
				Uninstall the fonts in this pog.
  -l --list	 List the names of all the pogs.
  -s num --size=num
				Set a new default point size.
  -n num --number=num
				Set a new default for how many fonts 
				to view at one go. Don't overdo this.
  -t "text" --text="text"
				Set a new default sample text.  
				"This is an ex-parrot!", say. 
				Be sure to use the quotes.
  -p pog --purge=pog
				Purge the pog of ttf files that are no
				longer really there.
  -c folder --check=folder
				Check for bad fonts that crash Fonty.
				It will recurse through sub-folders.
				This will build a file:
				~/.fontypython/segfonts
				After using this tool you should be
				able to browse folders that crashed
				Fonty. (The reason it's not done
				by default is that it's very slow.)
				* NOTE: The fonts that crash Fonty
				are probably still perfectly good
				and can be used in other apps. It's
				simply a bug in the library we use to
				access fonts that chokes things. This
				will (hopefully) improve in the future.
  -a folder pog
  --all folder pog
				Puts all fonts in this folder into the pog.
				If the pog already exists, it will add
				only *new* fonts, this means fonts are not
				repeated in that pog.
  -A folder pog
  --all-recurse folder pog
				Puts all fonts in this folder and *all*
				sub-folders into the pog. Rest same as -a.

				""")

use = _("""%(c)s [OPTIONS] [VIEW] [TARGET]
VIEW   : A place where fonts are. (A Pog or a Folder.)
TARGET : A "pog". A place to keep those fonts.

("%(c)s" on it's own will start the GUI.)

NB: Try not to use spaces in pog names. If you must, 
then "quote the name."

Please use -e to see more info.

NEWS : We now support TTF, OTF, Type1 (PFB, PFA) 
and TTC fonts.

%(version)s

The basic idea:
===============
Many designers have collections of font files in big
directory structures or on other media. Fonty Python
will let you gather your fonts and structure them
into collections -- or what I call "pogs" -- a place
to keep tyPOGraphy. Well, why not?

Your fonts never move from where they are
(so don't worry). All that happens is that you select 
fonts visually and place their names into a pog,
then you install or uninstall pogs as you need them.
No copies of your fonts are made, only links to the
original files are used to install the fonts.

For example, you might have a pog called "logos"
into which you place all the ttfs you have of
company logos. After that, when you need to work
with those logos, you simply install the 'logos' pog
and start your design app!

FP is also great for just looking at fonts wherever
they are on your computer, without having to install
them system-wide.

Manage your fonts on Gnu/Linux!
===============================
%(copy)s

%(warranty)s

%(contact)s
""" ) % { "c":"fontypython", "folder":_pc.appPath(), "contact":contact, "copy":copyright, "warranty":warranty, "version":version }

	
examples = _("""The basic format is:
%(c)s [VIEW] [TARGET]
  VIEW   = A place where fonts are. A pog or a folder
		   someplace.
  TARGET = A pog, a place to keep references to fonts
		   If you don't include a target then you are
		   viewing/editing only.

Tips:
=====
* Don't use spaces in pog names. If you absolutely
  must then use quotes around the name, e.g. "Pogs
  of Ni"
* If your design apps (for example The Gimp) do not
  reflect the fonts that you have installed, restart
  the app. Sometimes the system needs a while to
  reflect the new fonts in your fonts folder.

Examples: All using short options, see -h
=========
%(c)s /path/to/fonts/ttfs/a
  This will start off showing the fonts in that path.
 
%(c)s /path/to/fonts/ttfs/b Trouser
  This will let you view and choose fonts from the
  path and it will store them in a pog named "Trouser".
  The pog will be created if it's not already there.

%(c)s Lumberjack
  This will let you see the fonts in the pog named
  "Lumberjack". You can also uninstall individual
  fonts by selecting them. A cross will appear
  indicating the fonts that will be uninstalled.

%(c)s Camelot Spamalot
  This will let you see and choose fonts in
  "Camelot" and it will store them in "Spamalot"
  It lets you copy fonts between pogs.

%(c)s -i Cheese
  Will install the fonts in pog Cheese so you can
  use them in other apps.

%(c)s -u Trouser
  Will uninstall the fonts listed in pog Trouser,
  so you can't use 'em anymore.( You Naughty thing) 

%(c)s -t "Pigs on the wing"
  Will set the text and exit. It's odd that way.
  Restart Fonty again to see the change.
  * You can also do this from the gui, without a
  restart.
  
%(c)s -s 128 
  Will set the point size to 128 - Crazy man!

%(c)s -v 25
  Will show 25 fonts at a time. Beware large numbers!
	
%(c)s -s 64 -v 10 Pimple
  Will set the point size to 64, the number of fonts
  to view is 10 and then display the Pimple pog.

%(c)s -p Glutton
  If there are any fonts in "Glutton" that are not
  really on your drive/media anymore (perhaps you
  deleted them or the cat did) then this will go 
  through your pog and cull them.

%(c)s -c /some/path/to/fonts
  If Fonty keeps crashing on /some/path/to/fonts
  then you should run a check on that folder.
  This will 'mark' the dangerous fonts and let
  you use that folder in the future.

%(c)s -a /some/path HolyHandGrenade
  This will put all the fonts in that path into
  the Pog called HolyHandGrenade.

%(c)s -A /some/path Tutto
  This will do the same as -a above: start in that 
  path, but it will then walk down recursivly 
  through all sub-folders too. The fonts will 
  be placed in Tutto.

Your fontypython folder is:
%(folder)s
If you want to backup your pogs, that's where ya go.
%(contact)s

%(copy)s""") % { "c":"fontypython", "folder":_pc.appPath(), "contact":contact, "copy":copyright }

## These two are used in setup.py
description = _("Fonty Python - view and manage all kinds of fonts on Gnu/Linux")
long_description = _("""Manage your fonts on Gnu/Linux.
NEWS : We now support TTF, OTF, Type1 (PFB, PFA) 
and TTC fonts.

Many designers have collections of font files in big
directory structures or on other media. Fonty Python
will let you gather your fonts and structure them
into collections -- or what I call "Pogs" -- a place
to keep tyPOGraphy. Well, why not?

Your fonts never move from where they are
(so don't worry). All that happens is that you select 
fonts visually and place their names into a Pog,
then you install or uninstall Pogs as you need them.
No copies of your fonts are made, only links to the
original files are used to install the fonts.

For example, you might have a Pog called "logos"
into which you place all the ttfs you have of
company logos. After that, when you need to work
with those logos, you simply install the 'logos' Pog
and start your design app!

FP is also great for just looking at fonts wherever
they are on your computer, without having to install
them system-wide.
	
	%(copy)s
	%(contact)s
	""") % {"copy":copyright, "contact":contact}


wxvers="2.8"
wxVersionError = _("""I cannot find "python-wxversion"
Please install this package - NB: ensure that
you use only the "Unicode build".

TIP
===
On my distro I can search for it like this:
aptitude search python-wx
This returns many results, one of which is:
python-wxversion 
I then install it like this:
sudo aptitude install python-wxversion 

If you get long error messages, you will need to
install python-wxgtk*, where the star means the 
version number and it should be at least %(wxv)s

You can also get the latest version from here:
http://wxpython.org/download.php
""") % {"wxv":wxvers}
	
wxError =_("""I cannot find "python-wxgtkX.Y"
Please install this package - NB: ensure that
you use only the "Unicode build".

TIP
===
On my distro I can search for it like this:
aptitude search python-wx
This returns many results, one of which is:
python-wxgtk%(wxv)s
I then install it like this:
sudo aptitude install python-wxgtk%(wxv)s

Make sure it's at least version %(wxv)s

You can also get the latest version from here:
http://wxpython.org/download.php
""") % {"wxv":wxvers}


PILError = _("""I cannot find "python-imaging"
Please install this package.

TIP
===
On my distro I can search for it like this:
aptitude search python-imag
This returns many results, one of which is:
python-imaging
I then install it like this:
sudo aptitude install python-imaging

Make sure it's at least version 1.1.6-1

You can also get the latest version from here:
http://www.pythonware.com/products/pil/index.htm
""")

## Won't xlate the thanks:
thanks = u"""Many thanks to:
1. Robin Dunn - wxPython and much sundry help.

2. Martin v. Löwis - Essential concepts regarding unicode and files.

3. Pietro Battiston - Italian translation.

4. Baptiste - French translation and many ideas.

5. Jason Yamada-Hanff - For the wiki, at least :)

6. Michael Hoeft - For code, friendship and the German translation.

7. Kartik Mistry - Our esteemed Debian packager!

8. savannah.nongnu.org - For the hosting.

9. And all those I have neglected to include.
"""

## June 2009 : Get the GPL from the COPYING file rather than a copy of it all here again.
try:
	root = __file__                              
	if os.path.islink(root):                     
		root = os.path.realpath(root)            
	fontyroot = os.path.dirname(os.path.abspath(root)) 
	p = os.path.join(fontyroot,'COPYING')
	GPL = open(p,"r").read()
except:
	GPL = """
					GNU GENERAL PUBLIC LICENSE
					   Version 3, 29 June 2007

The file "COPYING" cannot be found. Please check the installation directory for the licence.
"""
