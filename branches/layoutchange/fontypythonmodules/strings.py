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


import fpversion
import os

copyright = "Fonty Python Copyright (C) 2006, 2007, 2008, 2009, 2016, 2017 Donn.C.Ingle"
contact = "email: donn.ingle@gmail.com"
done = "Done."


## Sept 2017
## The "missing .fonts directory" speech. I am repeating it too much, time
## to bring it all here.
TODO FIXME
missingDotFontsMessages = {
"statusbar": _("Missing \"~\.fonts\" directory. See Help.")
}


version = _("Fonty Python version %s") % fpversion.version

warranty = """This program is distributed in the
hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR
PURPOSE.  See the GNU General Public License for
more details."""

copy_warranty_contact = u"{}\n\n{}\n\n{}".format(copyright, warranty, contact)


aboutText = "%s\n%s\nWritten on Gnu\Linux, using wxPython.\n\n%s" % (copyright, version, warranty)

fonts_supported = _("""Fonts supported: TTF, OTF, TTC, WOFF, Type1 (PFB, PFA).""")

basic_idea = _("""Manage your fonts on GNU/Linux
==============================
Many designers have collections of font files in big
directories. Fonty Python will help you gather these
fonts and structure them into collections that I call
"Pogs" -- a place to keep tyPOGraphy. Well, why not?

Fonty lets you you select fonts visually and place
links to them in a Pog, which you can install or
remove as you require.

(Your font files never move from where they are. No
copies of your fonts are made. Only links to the
original files are used.)

For example, you might have a Pog called 'logos'
into which you place fonts of company logos.
Thereafter, when you want to use those logos, simply
install the 'logos' Pog and start your design app!

When you are done, remove the 'logos' Pog, and all
those linked-fonts will go away.

FP is also great for just looking at fonts wherever
they are on your computer, without having to install
them system-wide.""")

options=_("""Options:
  -v --version  Show program's version number and exit.
  -h --help  Show this help message and exit.
	-d --dir Shows you where the fontypython directory is
				on your drive.
  -e --examples
				Show some %$@#$ examples!
  -i Pog --install=Pog
				Install the fonts in this Pog to your
				fonts folder.
  -u Pog --uninstall=Pog
				Uninstall the fonts in this Pog.
  -l --list
				List the names of all the Pogs.
  -s num --size=num
				Set a new default point size.
  -n num --number=num
				Set a new default for how many fonts
				to view at one go. Don't overdo this.
  -p Pog --purge=Pog
				Purge the Pog of font files that are no
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
  -a Folder Pog --all Folder Pog
				Puts all fonts in this folder into the Pog.
				If the Pog already exists, it will add
				only *new* fonts, this means fonts are not
				repeated in that Pog.
  -A Folder Pog --all-recurse Folder Pog
				Puts all fonts in this folder and *all*
				sub-folders into the Pog. Rest same as -a.
  -z Pog --zip=Pog
				All the fonts inside Pog will be zipped
				and the zipfile will be named after the Pog.
				The file will be placed in the current
				directory.""")

use = _("""%(c)s [OPTIONS] [VIEW] [TARGET]
%(version)s

VIEW   : A place where fonts are. (A Pog or a Folder.)
TARGET : A "Pog". A place to keep those fonts.

("%(c)s" on its own will start the GUI.)

NB: Try not to use spaces in Pog names. If you must,
then "quote the name."

Please use -e to see more info.

%(fonts_supported)s

%(basic_idea)s""" ) % { "c":"fontypython", "version":version, "basic_idea":basic_idea, "fonts_supported":fonts_supported }


examples = _("""The basic format is:
%(c)s [OPTIONS] | [VIEW] [TARGET]
	OPTIONS = Various flags for use on the command-line.
						See -h or --help for more.

	Or:
	Two arguments which will determine what you see in the
	graphical user interface:

  VIEW = A place where fonts are. A Pog or a folder
				where fonts are located.

  TARGET = A Pog.	If this Pog does not exist, it will
					be created.

	Neither argument is required. When there's only one
	it's assumed to be a VIEW. When there are two, the
	second is assumed to be a TARGET.

Tips:
=====
* Don't use spaces in Pog names. If you absolutely
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
  path and it will store them in a Pog named "Trouser".
  The Pog will be created if it's not already there.

%(c)s Lumberjack
  This will let you see the fonts in the Pog named
  "Lumberjack". You can also uninstall individual
  fonts by selecting them. A cross will appear
  indicating the fonts that will be uninstalled.

%(c)s Camelot Spamalot
  This will let you see and choose fonts in
  "Camelot" and it will store them in "Spamalot"
  It lets you copy fonts between Pogs.

%(c)s -i Cheese
  Will install the fonts in Pog Cheese so you can
  use them in other apps.

%(c)s -u Trouser
  Will uninstall the fonts listed in Pog Trouser,
  so you can't use 'em anymore.( You Naughty thing)

%(c)s -s 128
  Will set the point size to 128 - Crazy man!

%(c)s -n 25
  Will show 25 fonts at a time. Beware large numbers!

%(c)s -s 64 -v 10 Pimple
  Will set the point size to 64, the number of fonts
  to view is 10 and then display the Pimple Pog.

%(c)s -p Glutton
  Purging a font. If there are any fonts in "Glutton"
	that are not really on your drive/media anymore
	(perhaps you deleted them or the cat did) this
	will go through the Pog and cull them.

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

%(contact)s

%(copy)s""") % { "c":"fontypython", "contact":contact, "copy":copyright }

fontyfolder = _("""Your fontypython folder is:
%(folder)s
If you want to backup your Pogs, that's where ya go.
""")

## These two are used in setup.py
description = _("Fonty Python - view and manage all kinds of fonts on Gnu/Linux")
long_description = "%(basic_idea)s\n\n%(fonts_supported)s\n\n%(copy)s\n\n%(contact)s" % {"copy":copyright, "contact":contact, "basic_idea":basic_idea, "fonts_supported":fonts_supported }


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


PILError = _("""I cannot find "python-pil"
Please install this package.

NOTE
===
PIL has been forked by Pillow.
The old package was "python-imaging",
the new one is "python-pil".

TIP
===
On my distro I can search for it like this:
aptitude search python-pil
This returns many results, one of which is:
python-pil
I then install it like this:
sudo aptitude install python-pil

Make sure it's at least version 1.1.6-1

You can also get the latest version from here:
http://www.pythonware.com/products/pil/index.htm
""")

##Sept 2017
giError = _("""I cannot fond "Python-gi"
Please install this package.

TIP
===
Look for "python-gi" in your package manager.
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
