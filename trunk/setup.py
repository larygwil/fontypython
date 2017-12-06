#!/usr/bin/env python

##  Fonty Python Copyright (C) 2006,2007,2008,2009,2017 Donn.C.Ingle
##  Contact: donn.ingle@gmail.com - I hope this email lasts.
##
##  This file is part of Fonty Python.
##  Fonty Python is free software: you can redistribute it and/or modify
##  it under the terms of the GNU General Public License as published by
##  the Free Software Foundation, either version 3 of the License, or
##  (at your option) any later version.
##
##  Fonty Python is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU General Public License for more details.
##
##  You should have received a copy of the GNU General Public License
##  along with Fonty Python.  If not, see <http://www.gnu.org/licenses/>.

"""
This is the main setup file for fontypython.

Requires a Python less than version 3. Sorry.

You should run:
    python setup.py install --force
..as root in order to use it.
Perhaps: sudo python setup.py install --force

You can also simply run ./fontypython from this
directory and it should work - provided you have
all the dependencies installed.

See the README file.

Much code borrowed from wxPython's setup and 
config files. Thanks to Robin Dunn for the 
suggestions.

"""

#NOTES
#==
#None of the imports touches fpsys in any way.
#Thus, there is no iPC instanced. Thus there should
#be no running of the code that upgrades old fonty
#to new (and makes files/directories), which is good
#because setup is run as root!
import fontypythonmodules.i18n
import fontypythonmodules.sanitycheck
import fontypythonmodules.fpversion

import os, shutil, sys, glob, fnmatch
from distutils.core import setup#, Command#, Extension
import distutils.command.install_data
import distutils.command.install_lib


def opj(*args):
    path = os.path.join(*args)
    return os.path.normpath(path)

# Specializations of some distutils command classes
class wx_smart_install_data(distutils.command.install_data.install_data):
    """
    By Robin Dunn.
    Need to change self.install_dir to the actual library dir.
    """
    def run(self):
        install_cmd = self.get_finalized_command('install')
        self.install_dir = getattr(install_cmd, 'install_lib')
        return distutils.command.install_data.install_data.run(self)

class fp_smart_install_lib(distutils.command.install_lib.install_lib):
    """
    Happens before the files are copied into dist-packages
    I hook in here and rm -fr the entire old fontypythonmodules
    directory. Gulp.
    """
    def run(self):
        install_cmd = self.get_finalized_command('install')
        self.install_dir = getattr(install_cmd, 'install_lib')
        
        last_fpm = opj(self.install_dir, 'fontypythonmodules')
        # Only do this thing if the file is there:
        if os.path.exists( last_fpm ):
            try:
                print "Going to remove tree: {}".format( last_fpm )
                shutil.rmtree( last_fpm )
            except:
                print "Could not remove old fontypythonmodules."

        # Also kick out the old script that might remain in install_dir
        start_fp = opj(self.install_dir, 'start_fontypython')
        if os.path.exists(start_fp):
            try:
                os.unlink(start_fp)
            except:
                print "Failed to remove old start_fontypython script."

        return distutils.command.install_lib.install_lib.run(self)       


def find_data_files(srcdir, *wildcards, **kw):
    """
    Get a list of all files under the srcdir matching wildcards,
    returned in a format to be used for install_data
    """

    ## A list of partials within a filename that would disqualify it
    ## from appearing in the tarball.
    badnames=[ ".pyc", "~", "no_", ".svn", "CVS", ".old", ".swp",
            "who_did_what" ] #has email @ddys in it.

    def walk_helper(arg, dirname, files):
        BL=[ bad for bad in badnames if bad in dirname ]
        L=len( BL )
        if L > 0:
            # There is a bad string in the dirname, so we skip it
            return
        names = []
        lst, wildcards = arg
        for wc in wildcards:
            wc_name = opj(dirname, wc)
            for f in files:
                filename = opj(dirname, f)
                ## This hairy looking line excludes the filename
                ## if any part of one of  badnames is in it:
                L=len([bad for bad in badnames if bad in filename])
                if L == 0:
                    if fnmatch.fnmatch(filename, wc_name) and not os.path.isdir(filename):
                        names.append(filename)
        if names:
            lst.append( (dirname, names ) )

    file_list = []
    recursive = kw.get('recursive', True)
    if recursive:
        os.path.walk(srcdir, walk_helper, (file_list, wildcards))
    else:
        walk_helper((file_list, wildcards),
                    srcdir,
                    [os.path.basename(f) for f in glob.glob(opj(srcdir, '*'))])
    return file_list

## Remove tmp stuff
try:
    os.remove("MANIFEST")
    os.remove("PKG-INFO")
except:
    pass

# Dec 2017
# ==
# I simplified the MANIFEST.in file to contain the minimum.
# It's a pos anyway. It only cares about the 'setup.py sdist'
# command and plays no role in a 'setup.py install'. Ffsks.

# The MANIFEST only bothers with the man page and itself.
# All other files must be explicitly included in the 'files'
# object.

# Everything under fontypythonmodules:
# Update: '*' casts a wider net. It now catches the README
# ======= and COPYING files in the tree. (See badnames too.)
# I must keep the contents of this directory very clean!
# files = find_data_files('fontypythonmodules/', '*.*')
files = find_data_files('fontypythonmodules/', '*')

# Jan 20 2008 - Add an icon and .desktop file
# Unsure about the absolute path to /usr/share
# but this works on my system.
files.append( ('/usr/share/pixmaps',['fontypython.png']) )
files.append( ('/usr/share/applications',['fontypython.desktop']) )

# Leave the man page up to Kartik.
# files.append( ('/usr/share/man/man1',['fontypython.1']) )

# Just put these into the modules dir too.
files.append( ('fontypythonmodules',['README', 'CHANGELOG']) )


##TEST:
debug = False
if debug:
    import pprint
    pprint.pprint (files)
    print


## Off we go!
setup(       name = "fontypython",
          version = fontypythonmodules.fpversion.version,
      description = fontypythonmodules.strings.description,
           author = "Donn.C.Ingle",
     author_email = fontypythonmodules.strings.contact,
          license = "GNU GPLv3",
              url = "https://savannah.nongnu.org/projects/fontypython/",
         packages = ['fontypythonmodules'],
       data_files = files,
         # Borrowed from wxPython too:
         # Causes the data_files to be installed into the modules 
         # directory. 
         # Also hooking the install_lib phase to clean old files
         #  before the install_data happens.
         cmdclass = { 
       'install_lib': fp_smart_install_lib,
      'install_data': wx_smart_install_data,
         },

          # 'fontypython' is in the root and is the only executable:
          scripts = ["fontypython"],
 long_description = fontypythonmodules.strings.long_description,
      classifiers = [
      'Development Status :: 6 - Mature',
      'Environment :: X11 Applications',
      'Intended Audience :: End Users/Desktop',
      'License :: OSI Approved :: GNU General Public License (GPL)',
      'Operating System :: POSIX :: Linux',
      'Programming Language :: Python',
      'Topic :: Desktop Environment',
      'Topic :: Text Processing :: Fonts',
      'Topic :: Multimedia :: Graphics',
      'Topic :: Utilities',
      ]
)
