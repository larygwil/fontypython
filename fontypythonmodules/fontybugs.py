# -*- coding: utf-8 -*-

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

##TEST: unremark and run this file to test errors.
import i18n

import locale
import os
import strings
import linux_safe_path_library
LSP = linux_safe_path_library.linuxSafePath()


class Errors ( Exception ):
    checkperms =  _("(Check your file permissions)")
    messages = {

    200 : _("Pog {item} is empty."),

    300 : _("Pog {item} is already installed."),

    500 : _("Pog {item} cannot be written-to. {checkperms}"),

    600 : _("Pog {item} is invalid, please hand-edit it."),

    700 : _("Some fonts in {item} did not install. You should purge or hand-edit it."),

    800 : _("Pog {item} is not installed."),

    900 : _("Some fonts in {item} could not be uninstalled. Please check your user fonts " \
            "folder for broken links. {checkperms}"),

    1000 : _("Cannot delete {item}. {checkperms}"),

    1010 : _("Not a single font in {item} could be installed. The font sources " \
             "have been moved or renamed."),

    1020 : _("Not a single font in {item} could be uninstalled. None of the fonts " \
             "were in your fonts folder. The pog has been marked as \"not installed\"."),

    1030 : _("This folder has no fonts in it."),
    }

    def __unicode__( self ):
        s = self.__class__.messages[self._id]
        i = u'"{}"'.format(self._item) # put quotes around it
        try: # to avoid key errors on format matches of checkperms
            s = s.format(item = i, checkperms = Errors.checkperms)
        except: pass
        return s

    def _format_error(self):
        ## As of Python 2.6 e.message has been deprecated.
        ## Turn 'self' into a 'string like object' by calling __unicode__ above.
        msg = unicode(self)
        msg = LSP.to_bytes( msg )
        return msg

    def unicode_of_error(self):
        """For use in wx gui when I am going to print the error in a messagebox."""
        return self._format_error()

    def print_error(self):
        print self._format_error()

    def print_error_and_quit(self):
        print self._format_error()
        raise SystemExit

    def get_error_string(self):
        return self._format_error()


## Now the classes that use Error:

class PogEmpty ( Errors ):
    def __init__ ( self, item = None):
        self._item = item
        self._id = 200

class PogInstalled ( Errors ):
    def __init__ ( self, item = None):
        self._item = item
        self._id = 300

class PogWriteError ( Errors ):
    def __init__ ( self, item = None):
        self._item = item
        self._id = 500

class PogInvalid ( Errors ):
    def __init__ ( self, item = None):
        self._item = item
        self._id = 600

class PogSomeFontsDidNotInstall ( Errors ): #Some fonts did get installed, but not all
    def __init__ ( self, item = None):
        self._item = item
        self._id = 700

class PogNotInstalled ( Errors ):
    def __init__ ( self, item = None):
        self._item = item
        self._id = 800

class PogLinksRemain ( Errors ):
    def __init__ ( self, item = None):
        self._item = item
        self._id = 900

class PogCannotDelete ( Errors ):
    def __init__ ( self, item = None):
        self._item = item
        self._id = 1000

class PogAllFontsFailedToInstall ( Errors ):
    def __init__ ( self, item = None):
        self._item = item
        self._id = 1010

class PogAllFontsFailedToUninstall ( Errors ):
    def __init__ ( self, item = None):
        self._item = item
        self._id = 1020

class FolderHasNoFonts ( Errors ):
    def __init__ ( self, item = None):
        self._item = item
        self._id = 1030

## Sept 2017
## Some new errors.
## These errors take a path argument so their unicode
## can display that path in the error message.
## They also take an "associated_err" which is an error object
## (Probably an OSError of some kind.)
class NoFontypythonDir(Errors):
    def __init__(self,path, associated_err):
        self.path = path
        self.associated_err = associated_err
    def __unicode__(self):

        #import pdb; pdb.set_trace()
        return _(
        u"The \"{path}\" directory cannot be created or found.\n" \
        "Fonty cannot run until it exists. " \
        "Please create it, and start me again." \
        "\nExample:\n\tcd {subpath}\n\tmkdir fontypython" \
        "\nThe python error was: {assocerr}\n\n"
        ).format(
                path = self.path,
                subpath = os.path.dirname(self.path),
                assocerr = self.associated_err)



class NoFontsDir(Errors):
    def __init__(self,path, associated_err):
        self.path = path
        self.associated_err = associated_err
    def __unicode__(self):
        return _(
        u"WARNING:\nThe \"{path}\" directory cannot be created or found.\n" \
        "Fonts cannot be installed until it exists. " \
        "Please create it, and start me again." \
        "\nExample:\n\tcd {subpath}\n\tmkdir fonts" \
        "\nThe python error was: {assocerr}\n\n"
        ).format(
                path = self.path,
                subpath = os.path.dirname(self.path),
                assocerr = self.associated_err)
    def short_unicode_of_error(self):
        """Used in gui; see the statusbar code."""
        return _(u"Missing fonts directory. See Help.")



class NoFontconfigDir(Errors):
    def __init__(self, path):
        self.path = path
    def __unicode__(self):
        return _(u"WARNING:\nThe fontconfig \"{path}\" directory " \
                  "cannot be created or found.\n").format(
                          path = self.path )
    def short_unicode_of_error(self):
        """Used in gui; see the statusbar code."""
        return _(u"Missing fontconfig \"{}\" directory. " \
                  "See Help.".format(self.path))



class UpgradeFail(Errors):
    """
    Any and all UpgradeFail errors should end the app after being caught.
    Slightly diff in that I pass a message in - because it differs as
    per context called.
    """
    def __init__(self, msg, associated_err):
        self.msg = msg
        self.associated_err = associated_err
    def __unicode__(self):
        return _(u"Failure during upgrade:\n{msg}\n\n" \
                  "The python error was: {assocerr}\n\n"
                  ).format(
                          msg = self.msg,
                          assocerr = self.associated_err)


if __name__ == "__main__":

    # DEC 2017
    # Testing zone
    # I will loop-test them!
    ers = [PogEmpty, PogInstalled, PogWriteError, PogInvalid, PogSomeFontsDidNotInstall, PogNotInstalled, PogLinksRemain,
            PogCannotDelete, PogAllFontsFailedToInstall, PogAllFontsFailedToUninstall, FolderHasNoFonts]
    for e in ers:
        try:
            raise e(u"Fooは最!")
        except Exception, ex:
            print unicode(ex)
    
