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
This is the main setup files for fontypython.
Required a Python less than version 3. Sorry.

You should run:
    python setup.py install
..as root in order to use it.
(perhaps: sudo python setup.py install)

You can also simply run ./fontypython from this
directory and it should work - provided you have
all the dependencies installed.

See the README file.
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

import os, sys, glob, fnmatch
from distutils.core import setup, Command#, Extension
import distutils.command.install_data


## Code borrowed from wxPython's setup and config files
## Thanks to Robin Dunn for the suggestion.
## I am not 100% sure what's going on, but it works!
def opj(*args):
    path = os.path.join(*args)
    return os.path.normpath(path)


# Two special strucs to explicity list old files
# and dirs to remove during an install.
old_files_to_remove={
  'fontypythonmodules': [
                        'cli.py',
                        'dialogues.py',
                        'gui_Left.py',
                        'gui_Middle.py',
                        'gui_Right.py'],
  'fontypythonmodules/help/common': [
                        'break.png',
                        'fp1.png.cr.png',
                        'fp2.png.cr.png',
                        'fp3.png.cr.png',
                        'fp4.png.cr.png',
                        'fp5.png.cr.png',
                        'fp6.png.cr.png',
                        'fp7.png.cr.png',
                        'fp8.png.cr.png',
                        'fp_already_in_x.png',
                        'fphelplogo.png',
                        'fp_normal_item.png',
                        'fp_removing_a_font.png',
                        'fp_ticking.png',
                        'README',
                        ],
                    '': [
                        'start_fontypython']
}
# And any dirs to remove, once they are empty.
dirs_to_remove=['fontypythonmodules/help/common']


# Specializations of some distutils command classes
class wx_smart_install_data(distutils.command.install_data.install_data):
    """need to change self.install_dir to the actual library dir"""
    def run(self):
        install_cmd = self.get_finalized_command('install')
        self.install_dir = getattr(install_cmd, 'install_lib')

        # Dec 2017
        # Added this to try delete old files from previous versions
        self.rm_old_files()

        # Now it goes and does all the copying into /usr/yadda-yadda
        return distutils.command.install_data.install_data.run(self)

    def rm_old_files(self):# install_dir, filename ):
        """
        Uses the vars above to explicitly seek out old files
        
        Also wipes all pyc files.

        to remove from the installation directory.
        I make (I hope) no assumptions and always test with 
        exists before deleting anything.
        """
        # First the damn pyc files...
        fpr = opj(self.install_dir, 'fontypythonmodules')
        if os.path.exists(fpr):
            print "Cleaning pyc files."
            pycs = opj(fpr, '*.pyc')
            for pyc in glob.glob( pycs ):
                if os.path.exists(pyc):
                    try:
                        os.unlink( pyc )
                    except:
                        print "Failed."

        #import pdb; pdb.set_trace()
        for adir, filez in old_files_to_remove.iteritems():
            path = opj(self.install_dir, adir)
            for kf in filez:
                kpaf = opj(path, kf)
                if os.path.exists(kpaf):
                    print "Cleaning old file: {}".format( kpaf )
                    try:
                        os.unlink( kpaf )
                    except:
                        print "Failed."

        # Now the dirs_to_remove
        for p in dirs_to_remove:
            kpaf = opj(self.install_dir, p)
            if os.path.exists( kpaf ):
                print "Cleaning old DIRECTORY: {}".format( kpaf )
                try:
                    os.rmdir( kpaf )
                except:
                    print "Failed."
        

def find_data_files(srcdir, *wildcards, **kw):
    # get a list of all files under the srcdir matching wildcards,
    # returned in a format to be used for install_data

    ## A list of partials within a filename that would disqualify it
    ## from appearing in the tarball.
    badnames=[ ".pyc","~","no_",".svn","CVS",".old", ".swp",
            "who_did_what" ] # exclude the who_did_what file as it contains email details.

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

# This is a list of files to install, and where:
# The MANIFEST only bothers with the man page and itself.
# All other files must be explicitly included in this files
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

# 
files.append( ('fontypythonmodules',['README', 'CHANGELOG']) )

# I want these two in the 'root' but they are not 'scripts' 
#  I.e. I don't want them to have +x bit set:
#files.append( ('',['fontypython_step_2.py','fontypython_step_3.py']) )

##TEST:
debug = False
if debug:
    import pprint
    pprint.pprint (files)
    print
    version = fontypythonmodules.fpversion.version,
    print version
    print


class CleanCommand(distutils.core.Command):
    """Custom clean command to tidy up the project root."""
    user_options = []
    def initialize_options(self):
        self.cwd = None
    def finalize_options(self):
        self.cwd = os.getcwd()
    def run(self):
        print "foo"
        print self.cwd 
        #e.g. /home/donn/Projects/pythoning/fontyPython/dev.svn/fontypython/trunk
        # which was my cwd.

        assert os.getcwd() == self.cwd, 'Must be in package root: %s' % self.cwd
        #os.system ('rm -rf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')


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
         # directory. Override some of the default distutils 
         # command classes with my own.
         cmdclass = { 
      'install_data': wx_smart_install_data,
             'clean': CleanCommand
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
      ],
  ## Dec 2017: Seems my distutils is too old to know about it. 
  ## I will leave it here for whatever.
  python_requires = '<3',
)
