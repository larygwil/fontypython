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
"""
Dec 2017
==
This is step 3 in the startup process. We got here from
    fp_step_2.py
Step 4 is next: fontypythonmodules/fp_step_4.py

This file serves to get us down into the fontypythonmodules
directory where all the modules live.
"""

import fontypythonmodules.i18n

import os
## Just clear up some sad facts:
if os.name != "posix": sys.exit(_("Sorry, only Gnu/Linux is supported at the moment."))
## start the show!
import fontypythonmodules.fp_step_4
