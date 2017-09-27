# This Python file uses the following encoding: utf-8
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


import fpversion
import os

##copyright = "Fonty Python Copyright (C) 2006, 2007, 2008, 2009, 2016, 2017 Donn.C.Ingle"
copyright = "Fonty Python Copyright (C) 2017 Donn.C.Ingle"
contact = "email: donn.ingle@gmail.com"
done = "Done."



version = _("Fonty Python version %s") % fpversion.version

warranty = """This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
PURPOSE.  See the GNU General Public License for more details."""

copy_warranty_contact = u"{}\n\n{}\n\n{}".format(copyright, warranty, contact)


aboutText = "%s\n%s\nWritten on Gnu\Linux, using wxPython.\n\n%s" % (copyright, version, warranty)

fonts_supported = _("""Fonts supported: TTF, OTF, TTC, WOFF, Type1 (PFB, PFA).""")

yaddayadda = _("""The basic format is:
%(c)s [OPTIONS] || [VIEW] [TARGET]
OPTIONS: Various flags for use on the command-line. See -h or --help for more.
Or:
Two arguments which will determine what you see in the graphical user interface:
VIEW   : A place where fonts are. A Pog or a folder where fonts are located.
TARGET : A Pog. If this Pog does not exist, it will be created.

Neither argument is required. When there's only one it's assumed to be a VIEW. 
When there are two, it's VIEW then TARGET.

NB: Try not to use spaces in Pog names. If you must, then "quote the name"."""
) % { "c":"fontypython" }




basic_idea = _("""Manage your fonts on GNU/Linux
==============================
Many designers have collections of font files in big directories. Fonty Python
will help you gather these fonts and structure them into collections we'll call
"Pogs" -- a place to keep tyPOGraphy. Well, why not?

Fonty lets you you select fonts visually and put them into Pogs which you can
install or remove as you require.

(Your font files never move from where they are. No copies of your fonts
are made. Only links to them are used.)

For example, you might have a Pog called 'logos' into which you place fonts of
company logos. Thereafter, when you want to use those logos, simply install the
'logos' Pog and start your design app!

When you're done, remove the 'logos' Pog, and the fonts will go away.

Fonty is also great for just looking at fonts, wherever they are, without having 
to install them.""")


use = _("""%(yadda)s
Please use -e to see more info.

%(fonts_supported)s

%(basic_idea)s""" ) % { "yadda":yaddayadda, "basic_idea":basic_idea, "fonts_supported":fonts_supported }

options=_("""Options:
  -v, --version Show program's version number and exit.
  -h, --help    Show this help message and exit.
  -d, --dir     Show the "fontypython" path. Add this to your backup process!
  -e, --examples
                Show some %$@#$ examples!
  -i Pog, --install=Pog
                Install the fonts in this Pog.
  -u Pog, --uninstall=Pog
                Uninstall the fonts in this Pog.
  -l, --list
                List the names of all your Pogs.
  -f, --lsfonts
                Lists the contents of your user fonts directory. Here, you'll
                find the links that Fonty is managing for you.
  -s num, --size=num
                Set a new default point size (you'll see it in the gui).
  -n num, --number=num
                Set a new default for how many fonts to view at one go in the gui.
                (Don't overdo this.)
  -p Pog, --purge=Pog
                Clean the Pog of fonts that are missing.
  -c folder, --check=folder
                Check for bad fonts that crash Fonty. After using this tool you 
                should be able to use Fonty again.
                * NOTE: The fonts that crash Fonty are probably still perfectly
                useable in other apps. 
  -a Folder Pog, --all Folder Pog
                Puts all fonts in Folder into Pog.
  -A Folder Pog, --all-recurse Folder Pog
                Puts all fonts in Folder and *all* sub-folders into Pog.
  -z Pog, --zip=Pog
                All the fonts inside Pog will be zipped and the zipfile will be 
                named after the Pog. The file will be placed in the current
                directory.""")



examples = _("""%(yadda)s
Examples: All using short options, see -h
=========
%(c)s /path/to/fonts/ttfs/a
  This will start off showing the fonts in that path.

%(c)s /path/to/fonts/ttfs/b Trouser
  This will let you view and choose fonts from the path and it will store them 
  in a Pog named Trouser. The Pog will be created if it's not already there.

%(c)s Lumberjack
  This will let you see the fonts in the Pog named Lumberjack. You can also 
  uninstall individual fonts by selecting them. A cross will appear indicating 
  the fonts that will be uninstalled.

%(c)s Camelot Spamalot
  This will let you see and choose fonts in Camelot and it will store them 
  in "Spamalot". It lets you copy fonts between Pogs.

%(c)s -i Cheese
  Will install the fonts in Cheese so you can use them in other apps.

%(c)s -u Trouser
  Will uninstall the fonts listed in Trouser.

%(c)s -s 128
  Will set the point size in the gui to 128 - Crazy man!

%(c)s -n 25
  Will show 25 fonts at a time, in the gui. Beware large numbers!

%(c)s -s 64 -v 10 Pimple
  Will set the point size to 64, paging to 10 and display Pimple.

%(c)s -p Glutton
  Purging a font. If there are any fonts in Glutton that are not really on your 
  drive/media anymore (perhaps you deleted them or the cat did) this will go 
  through the Pog and cull them.

%(c)s -c /some/path/to/fonts
  If Fonty keeps crashing on /some/path/to/fonts then you should run a check on
  that folder. This will mark the dangerous fonts and let you view that folder 
  in the future.

%(c)s -a /some/path HolyHandGrenade
  This will put all the fonts in that path into the Pog called HolyHandGrenade.

%(c)s -A /some/path Tutto
  This will do the same as -a: starting in some path, but it will then walk 
  down through *all* sub-folders too. The fonts will be placed in Tutto.

%(contact)s

%(copy)s""") % { "yadda":yaddayadda, "c":"fontypython", "contact":contact, "copy":copyright }

fontyfolder = _("""Your fontypython folder is:
{}""")

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
giError = _("""I cannot find "Python-gi"
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
