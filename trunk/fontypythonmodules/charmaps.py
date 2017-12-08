## Fonty Python Copyright (C) 2006 - 2017 Donn.C.Ingle
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

import os,  subprocess, errno

class CharMapApp(object):
    '''
    Base class for whatever character viewer apps I may support.
    '''
    def __init__( self, appname ):
        self.appname = appname
        self.is_installed = self.do_i_exist()
    def do_i_exist( self ):
        #return False #test
        for path in os.environ.get('PATH', '').split(':'):
            if os.path.exists(os.path.join(path, self.appname)) and \
                    not os.path.isdir(os.path.join(path, self.appname)):
                return True
        #return True #test
        return False
    def OpenApp( self, *args ): pass
    def Cleanup( self ): pass
    def Run( self, cmd ):
        try:
            proc = subprocess.Popen( cmd, shell=False )
        except:
            ## Just bail.
            return

        ## gucharmap: Fonty actually holds still and waits here until gucharmap is closed.
        ## kfontview: Fonty just runs-through. It's a different beast...
        ## Both still work and Fonty stays active. Multiple instances of the viewers can be opened!
        proc.wait()


class Gucharmap( CharMapApp ):
    '''
    The wiring needed to support gucharmap.
    It requires a dodge before and after spawning the app --
      one must temporarily install the font to be viewed
      and then remove it again afterwards.
    '''
    def OpenApp( self, *args ):
        src=args[0]
        dest=args[1]
        self.dest = dest
        fam=args[2]
        sz=args[3]

        #cmd = [ self.appname, u'--font=%s, %s' % (fam, sz)]
        cmd = [ self.appname, u'--font={}, {}'.format(fam, sz) ]
        
        ## gucharmap requires the font to be installed already, so fake it:
        self.already_installed = False
        try:
            os.symlink( src, dest )
        except OSError, detail:
            if detail.errno != errno.EEXIST:
                # Not EEXIST means the link failed, don't open the charmap
                return False
            else:
                # Error EEXIST: file exists.
                # User may have installed it previously (or something).
                self.already_installed = True
        self.Run( cmd )
    def Cleanup( self ):
        # Remove the fake installed font -- if it's a candidate:
        if not self.already_installed:
            try:
                os.unlink( self.dest )
            except:
                # What to do? Start yelling? Nah...
                pass

class Kfontview( CharMapApp ):
    '''
    Wiring for kfontview -- really easy to use.
    '''
    def OpenApp( self, *args ):
        url=args[0]

        #cmd = [ self.appname, u'%s' % url]
        cmd = [ self.appname, u'{}'.format(url) ]
        self.Run( cmd )


## Oct 2009
class CharMapController(object):
    '''
    Control the character map viewing objects (above) that Fonty supports.
    UNSET is always the initial "chosen app" when this instantiates.
    '''
    def __init__( self, config_callback ):
        self.config_callback = config_callback
        
        supported_char_map_apps = { "gucharmap":Gucharmap, "kfontview":Kfontview }
        self.list_of_suggested_apps=" or ".join('"{}"'.format(n) for n in supported_char_map_apps.keys())

        ## Which of the supported apps are actually available?
        self._available_app_dict = {}
        for appname, klass in supported_char_map_apps.iteritems():
            ## Instantiate an app class:
            i = klass( appname )
            if i.is_installed: self._available_app_dict[appname] = i

        ## Flag to signify if there are available apps to use.
        self.apps_are_available = False if len(self._available_app_dict) == 0 else True

        self.__current_appname = "UNSET"
        self.quick_appname_list = self._available_app_dict.keys()

    def set_current_appname(self, x):
        ## If the new name (x) is UNSET or some appname that is not available
        ## then give x a new value of the first thing in the list of what is
        ## actually available.
        if x not in self.quick_appname_list and self.apps_are_available:
                x = self.quick_appname_list[0]
                
        self.__current_appname = x ## It's possible that x is "UNSET" 
        self.config_callback( x ) ## go set the config's app_char_map var too.

    #def GET_CURRENT_APPNAME( self ):
    #    '''
    #    This is only called when apps_are_available Is True: See dialogues.py
    #    Think of this as raising an error if apps_are_available Is False!
    #    '''
    #    if self.__current_appname == "UNSET":
    #        x = self.quick_appname_list[0]
    #        return x
    #    else:
    #        return self.__current_appname

    def GetInstance( self ):
        '''
        This is only called when apps_are_available Is True: See gui_Fitmap.py
        in can_have_button method.
        Think of this as raising an error if apps_are_available Is False!
        '''
        ## Fetch an instance from my dict 
        return self._available_app_dict[ self.__current_appname ]


