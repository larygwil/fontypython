## Fonty Python Copyright (C) 2006, 2017 Donn.C.Ingle
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

## Linux safe "path" library
##  It's really a place to do encode and decode and os.join 
##  I debated calling it linux safe STRING library, but can't decide.

"""
LESSONS
 Linux is Posix and that means all filenames are stored as byte strings
 "Unlike Windows NT/2000/XP, which always store filenames in Unicode format, 
  POSIX systems (including Linux) always store filenames as binary strings. 
  This is somewhat more flexible, since the operating system itself doesn't 
  have to know (or care) what encoding is used for filenames. The downside 
  is that the user is responsible for setting up their environment 
  ("locale") for the proper coding."

 On Linux: os.path.supports_unicode_filename is always == True
 On my system, with LANG=en_ZA.utf8
 >>> locale.getpreferredencoding()
 'UTF-8'
    Return the charset that the user is likely using,
    according to the system configuration.
 With LANG=C it returns "ANSI****"
 On my system:
 >>> sys.getfilesystemencoding()
 'UTF-8'
 This one returns the ENCODING (byte string to unicode) needed to
 convert filenames from the O/S *to* unicode.

os.path.join : 
    If any one part is unicode, it's all unicode. (Order does not matter)
    If all parts are str, it's str
    
>>> import os
>>> a=u"unicode"
>>> b="string"
>>> type(a)
<type 'unicode'>
>>> type(b)
<type 'str'>
>>> p=os.path.join(a,b)
>>> p
u'unicode/string'
>>> p=os.path.join(b,a)
>>> p
u'string/unicode'


"""

import os
import locale

class linuxSafePath( object ):
    def __init__(self):
        self.PREFENC=locale.getpreferredencoding()

    ## I am leaving these without error catches. Let the errors be handled higher-up
    ## or barf to the stdout. Recc. that users run app from the cli if it is 
    ## closing mysteriously.

    def to_bytes( self, u ):
        '''Given a known unicode, return a byte string'''
        return u.encode( self.PREFENC )

    def to_unicode( self, b ):
        '''Given a known byte string, return a unicode'''
        return b.decode( self.PREFENC,"replace" )

    def ensure_bytes( self, anything ):
        '''Given any unknown, return a byte string'''
        if type(anything) is unicode:
            byte_string = self.to_bytes( anything )
        else:
            byte_string = anything
        return byte_string

    def ensure_unicode( self, anything ):
        '''Given any unknown, return a unicode'''
        if type( anything ) is str:
            unicode_obj = self.to_unicode( anything )
        else:
            unicode_obj = anything
        return unicode_obj

    def _safe_path_join( self, want="bytestring", *mixed_list ):
        '''Private worker. Join a path cast to want from mixed_list'''
        list = [] 
        if want == "bytestring":
            for anything in mixed_list:
                list.append( self.ensure_bytes(anything) )
        else:
            for anything in mixed_list:
                list.append( self.ensure_unicode( anything ) )

        return os.path.join( *list )


    def path_join_ensure_bytestring_result( self, *args ):
        '''Return a byte string path from the supplied arguments'''
        return self._safe_path_join( "bytestring", *args)

    def path_join_ensure_unicode_result( self, *args ):
        '''Return a unicode path from the supplied arguments'''
        return self._safe_path_join( "unicode", *args )

