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

import sys
import strings

## Quick tests - which is there?
## Using imp will find a module very quickly, faster than import x
import imp

## PIL : Is it there?
try:
    from PIL import Image, ImageFont, ImageDraw
except:
    print strings.PILError
    raise SystemExit

try:
    import wxversion ## Dec 2007: noticed that it may not be installed along with wxPython....
    wxversion.ensureMinimal("3.0")
        ## June 25, 2016 - wxversion is now 3.0
        ## I am remarking out the old line:
    ##wxversion.ensureMinimal("2.8") 
except:
    print strings.wxVersionError
    print
try:
    imp.find_module("wx")
except:
    print strings.wxError
    raise SystemExit

## 2017 - Using GLib to detect the XDG_DATA_HOME stuff.
## Not fatal if it's missing - will fall-back to old fonty paths.
try:
    from gi.repository import GLib
except:
    print strings.giError

