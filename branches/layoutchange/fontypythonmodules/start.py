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

## test modules etc.
import fontypythonmodules.sanitycheck

import fpsys
## The first import means the code in there gets RUN.
## Hence the iPC (single instance of PathControl) is now made.

## Process the command line stuff...
import cli
## What keeps the cli and the gui apart is any 
## "raise SystemExit" inside cli
## between here and ..
## The GUI
import fontypythonmodules.wxgui

## End, clean up
fpsys.config.Save()
