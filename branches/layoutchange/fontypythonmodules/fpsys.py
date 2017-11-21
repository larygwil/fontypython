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

## fpsys : fonty python system.
## I debated calling it fpglobals.
## This is a common-ground for variables and defs that will be used from
## other modules - so they are global to everything.

import sys, os, pickle
import linux_safe_path_library
import fontybugs
import fontcontrol
import charmaps
import subprocess
try:
    ## Sept 2017 - Trying to get XDG compliance going.
    ## ==
    ## I tried to use: wx.StandardPaths
    ## The version I have to work with (3.x) does not support the new Freedesktop stuff.
    ## Therefore, I must employ GLib..
    ##
    ## ===
    ## Freedesktop specs and GLib.
    ## https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
    ## https://developer.gnome.org/glib/2.40/glib-Miscellaneous-Utility-Functions.html#g-get-user-data-dir

    ## >>>from gi.repository import GLib
    ## >>>GLib.get_user_data_dir()
    ## '/home/donn/.local/share'
    from gi.repository import GLib
    XDG_DATA_HOME = GLib.get_user_data_dir() # ?? What kinds of errors can happen here?
    XDG_CONFIG_HOME = GLib.get_user_config_dir()
except:
    ## Bad things happened.
    ## Let's try a direct approach:
    ## I set these to "" (vs None.) 
    ##   When os.path.exists happens (later), None chokes. 
    ##   os.path.exists("") gives False, which is good.
    XDG_DATA_HOME = ""
    XDG_CONFIG_HOME = ""
    try:
        home = os.environ["HOME"] # Is a byte string under Linux.
        try2 = os.path.join(home, ".local", "share")
        if os.path.exists(try2): XDG_DATA_HOME = try2
        try2 = ps.path.join(home, ".config")
        if os.path.exists(try2): XDG_CONFIG_HOME = try2
    except:
        pass
     
#print XDG_DATA_HOME
#print XDG_CONFIG_HOME
#raise SystemExit

## debug test
##XDG_DATA_HOME = ""

## See end of file

class PathControl:
    """
    Instanced here, in fpsys, where it is used globally.

    TASKS:
    ===
    . Sets an error dict and *returns* on failure, does not raise.
    . Switches on whether there exists a valid XDG_DATA_HOME directory.
       No : Falls-back to old ~/.fontypython and ~/.fonts (makes both if needs).
       Yes: Starts an "upgrade"
            Makes new fontypython and fonts (if needs). Yes I am going to 
            put all my shit in data_home.
            Moves all old contents into new fontypython.
            Moves all symlinks that were in ~/.fonts into new fonts.

    . Provides methods to look for what errors happened after __init__
    . Provide paths for fontypython.
    . Provide list of pog names (without the .pog extension).
    """
    __FIRSTRUN = True

    ## All these vars contain/return BYTE STRING paths and files.
    __HOME = os.environ["HOME"] # Is a byte string under Linux.
    __fp_dir = "" # "" vs None. When os.path.exists happens, None chokes. "" gives False.
    __fonts_dir = ""
    __app_conf = ""
    __fontconfig_confd = "NOTSETWRONGBADHORRIBLE"

    def __init__( self, XDG_DATA_HOME, XDG_CONFIG_HOME ):

        self.__ERROR_STATE={}

        ## Class var to detect the very first run of this code:
        if not PathControl.__FIRSTRUN:
            print "PathControl has been instanced twice."
            raise SystemExit
        else:
            PathControl.__FIRSTRUN = False

            ## Fontconfig
            ## ==
            ## According to the spec:
            ## https://www.freedesktop.org/software/fontconfig/fontconfig-user.html
            ## This is the user path I am going to use:
            ## $XDG_CONFIG_HOME/fontconfig/conf.d
            fcp = "fontconfig/conf.d"
            fcp = os.path.join(XDG_CONFIG_HOME, "fontconfig","conf.d")
            if os.path.exists( fcp ):
                PathControl.__fontconfig_confd = fcp
            else:
                ##Prepare an error for later probing
                self.__ERROR_STATE["NoFontconfigDir"] = \
                    fontybugs.NoFontconfigDir( path = fcp )


            ## If the fancy new XDG_DATA_HOME does not actually exist, we want to fall back:
            ## I don't know if this is even a possibility, because the docs are horrible.. :|
            if not os.path.exists(XDG_DATA_HOME):

                ## We are in fallback to the old fonty dirs etc.
                fp_dir = os.path.join(PathControl.__HOME, ".fontypython")
                try:
                    self.__try_test_make_dir(fp_dir, "NoFontypythonDir")
                except:
                    return #Serious error, bail.
                else:
                    PathControl.__fp_dir = fp_dir + "/" # Record it for use.

                fonts_dir = os.path.join(PathControl.__HOME, ".fonts")
                try:
                    self.__try_test_make_dir(fonts_dir, "NoFontsDir")
                except:
                    pass # Not too bad. Fonts dir will be None.
                else:
                    PathControl.__fonts_dir = fonts_dir +"/"
                ## End of old fonty fallback

            else:
                ## We are in valid XDG terrain: ~/.local/share/ (or whatever) exists.

                ## We may hit perm errors within there, I guess..

                x_fp_dir = os.path.join(XDG_DATA_HOME, "fontypython")
                try:
                    self.__try_test_make_dir(x_fp_dir, "NoFontypythonDir")
                    ##TESTER: self.__try_test_make_dir("/root/bar", "NoFontypythonDir")
                except:
                    return #Serious error
                else:
                    PathControl.__fp_dir = x_fp_dir + "/"


                x_fonts_dir = os.path.join(XDG_DATA_HOME, "fonts")
                try:
                    self.__try_test_make_dir(x_fonts_dir, "NoFontsDir")
                    ##TESTER: self.__try_test_make_dir("/root/foo", "NoFontsDir")
                except:
                    pass
                else:   
                    PathControl.__fonts_dir = x_fonts_dir + "/"

                ## Decide on what can be upgraded..
                # If new fp_dir exists *and* old fp_dir exists, then we can upgrade.
                # Since, by now, x_fp_dir does exist, we need only look for the old.

                old_fp_dir = os.path.join(PathControl.__HOME, ".fontypython")
                old_fonts_dir = os.path.join(PathControl.__HOME, ".fonts")

                ## fontypython dir.
                ## After an upgrade, the old_fp_dir will be deleted, making
                ## this a once-off:
                if os.path.exists(old_fp_dir):
                    try:
                        self.__upgrade_fp_dir( old_fp_dir, x_fp_dir )
                    except:
                        return #Any errors are fatal. See upstream for handling of it.

                # if new fonts exists *and* old fonts exists, then we can upgrade
                #  (new fonts *might* not exist...)
                hasnewfontsdir = "NoFontsDir" not in self.__ERROR_STATE #Rather than another exists test.
                if hasnewfontsdir and os.path.exists(old_fonts_dir):
                    ## Okay, both dirs exist.
                    ## This method ignores all errors, hence no try:
                    self.__upgrade_fonts_dir( old_fonts_dir, x_fonts_dir )

            PathControl.__app_conf = os.path.join(PathControl.__fp_dir, "fp.conf")

    ## Private Interface:
    def __try_test_make_dir( self, path, errkey ):
        """
        Path exists? No: make it. Catch and cache errors.
        Returns nothing or raises the error.
        """
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except Exception as associated_err:
                ## Let's decide what to raise
                if errkey=="NoFontypythonDir":
                    e = fontybugs.NoFontypythonDir(path, associated_err)
                elif errkey=="NoFontsDir":
                    e = fontybugs.NoFontsDir(path, associated_err)
                else:
                    # Unknown key
                    print "Bad key in PathControl.__try_test_make_dir on key:", errkey
                    raise SystemExit

                self.__ERROR_STATE[errkey] = e
                raise e # Let's use our error to communicate with the caller.

    def __raiseOrContinue(self, errkey):
        e = self.__ERROR_STATE.get( errkey, False )
        if e: raise e

    def __upgrade_fp_dir(self,  old_fp, new_fp):
        """
        There are quie a few files to move:
          fp.conf
          overlap_counts
          segfonts
          *.pog

        Let's just move all the files!

        Then, rm the old ~/.fontypython dir.

        On any error, it records and raises an UpgradeFail error.
        """

        import errno

        try:
            ## Start out cocky - just up and kill old_fp
            ## Only fails if the dir is not empty
            os.rmdir(old_fp)
            return

        except OSError as old_fp_rm_err:
            ## Ah, it's not empty: ergo upgrade.

            if old_fp_rm_err.errno == errno.ENOTEMPTY:
                import shutil
                try:
                    files = os.listdir(old_fp)
                    f="YetToBegin"
                    for f in files:
                        oldpaf = os.path.join(old_fp, f)
                        newpaf = os.path.join(new_fp, f)
                        ##TESTER: newpaf = os.path.join("/root/", f)
                        shutil.move(oldpaf, newpaf)
                except Exception as e:
                    self.__ERROR_STATE["UpgradeFail"] = fontybugs.UpgradeFail(
                        _("Could not move \"{what}\" from \"{src}\" to \"{dest}\"\n" \
                          "Please resolve the problem and start me again.").format(
                              what=f,
                              src=old_fp,
                              dest=new_fp),
                        e)
                    raise
        except: # unknown sundry
            pass # We repeat the rmdir soon..

        ## Now that we've moved all the guts over to the new fp path..
        try:
            ## Let's, once again, attempt to rm the old fp dir...
            os.rmdir(old_fp)
            ##TESTER: os.rmdir("/root/foo")
        except Exception as e:
            #Just could not kill the beast!
            self.__ERROR_STATE["UpgradeFail"] = \
                    fontybugs.UpgradeFail(
                        _("Could not remove the old \"{oldfontydir}\" directory.\n" \
                          "Please remove it and start me again.").format(
                              oldfontydir = old_fp),
                        e)
            raise

    def __upgrade_fonts_dir(self, old_fonts_dir, new_fonts_dir):
        """
        Find all symlinks in ~/.fonts and re-link them in new_fonts_dir. Delete old link.
        This method ignores all errors.
        
        (I tried to re-link fonts to the new directory for all pogs that are installed, but
        this is still the __init__ of PathControl and I can't make Pog objects yet.)

        The ~/.fonts directory will not be removed.
        """
        def movelink(src, dst):
            try:
                linkto = os.readlink(src)
                os.symlink(linkto, dst)
                os.unlink(src)
            except:
                pass #don't care

        links = [ f for f in os.listdir(old_fonts_dir) if os.path.islink( os.path.join(old_fonts_dir, f) ) ]
        if not links: return

        for f in links:
            movelink( os.path.join(old_fonts_dir, f), os.path.join(new_fonts_dir, f) )


    ## Public Interface:
    def probeNoFontsDirError(self):
        """For outside probing of missing fonts dir. E.g. see fontcontrol.py"""
        self.__raiseOrContinue("NoFontsDir")

    def probeNoFontypythonDirError(self):
        self.__raiseOrContinue("NoFontypythonDir")

    def get_fontconfig_dir_error(self):
        return self.__ERROR_STATE.get( "NoFontconfigDir", None )

    def probeAllErrors(self):
        """
        For outsiders to probe these errors.
        Most serious first. The NoFontsDir one means fonts can 
        be viewed, but not installed.
        """
        self.__raiseOrContinue("NoFontypythonDir")
        self.__raiseOrContinue("UpgradeFail")
        self.__raiseOrContinue("NoFontsDir")
        self.__raiseOrContinue("NoFontconfigDir")

    def appPath(self):
        """Supplies the "fontypython" application directory."""
        return PathControl.__fp_dir

    def appConf(self):
        """Supplies paf of "fp.conf" or empty string."""
        if PathControl.__fp_dir=="": return ""
        return PathControl.__app_conf

    def userFontPath(self):
        """Supplies the user's "fonts" directory."""
        return PathControl.__fonts_dir

    def home(self):
        #Not gonna bother error checking HOME
        return PathControl.__HOME

    def user_fontconfig_confd(self):
        return PathControl.__fontconfig_confd

    def getPogNames(self, someotherpath=None):
        """
        We pass a byte string path to os.listdir therefore this function
        returns a LIST OF BYTE STRINGS.
        """
        p = PathControl.__fp_dir if not someotherpath else someotherpath
        
        # So, it turns out that during startup (in cli.py), there is a place
        # that uses this and __fp_dir may be "" because of an error state.
        # Thus a truthy test helps:
        if not p: return []

        # all okay, make a list:
        return [ f[0:-4] for f in os.listdir(p) if f.endswith(".pog") ]



## Sept 2009
class Overlaperize(object):
    '''
    Used when uninstalling a pog:
    If a single font is in *many* pogs, then we count each 'overlap' and
    control the removal of them until there are no overlaps.
    i.e. When no other installed pogs are using the font, it is safe to
    remove the link (should that last pog be removed by the user).
    '''
    def __init__(self):
        self.OVERLAP_COUNT_DICT = {}
        self.DISABLE_THIS = False # In case all this makes a horrible mess : users can flip this to True....

    def inc(self,key):
        if self.DISABLE_THIS: return True

        if key in self.OVERLAP_COUNT_DICT:
            self.OVERLAP_COUNT_DICT[key] += 1
        else:
            self.OVERLAP_COUNT_DICT[key] = 2 #starts at 2 because there is already one installed.
        #self.report(key)
        return True

    def dec(self,key):
        '''
        Return True means : This font overlaps
        Return False means : This font can be uninstalled
        '''
        if self.DISABLE_THIS: return False

        if key in self.OVERLAP_COUNT_DICT:
            self.OVERLAP_COUNT_DICT[key] -= 1
            if self.OVERLAP_COUNT_DICT[key] == 0:
                del self.OVERLAP_COUNT_DICT[key]
                return False # it does NOT overlap anymore.
            else:
                #self.report(key)
                return True # It still overlaps

        # It gets here if the font is totally unknown to the OVERLAP_COUNT_DICT
        return False #It therefore does NOT overlap.

    def report(self,key):
            print "%s has overlap count of %d" % (key, self.OVERLAP_COUNT_DICT[key])

    def sleep(self):
        '''Save the OVERLAP_COUNT_DICT to a file (if it has content). Called when app closes.'''
        if self.DISABLE_THIS: return

        if not self.OVERLAP_COUNT_DICT:
            self.OVERLAP_COUNT_DICT={} # Ensure there is a blank overlap_counts file!

        ## At app's close, there *must* be a valid appPath. No try/except
        paf = os.path.join(iPC.appPath(),"overlap_counts")
        fr = open( paf, 'wb' ) # pickle says use 'binary' files, but only Windows makes this distinction. I use it to be safe...
        pickle.dump( self.OVERLAP_COUNT_DICT, fr, protocol=pickle.HIGHEST_PROTOCOL )
        fr.close()

    def wakeup(self):
        '''Restore the OVERLAP_COUNT_DICT from a file (if any). Called as app starts.'''
        if self.DISABLE_THIS: return

        ## iPC __init__ may have encountered errors.
        ## Since this method runs soon after, I should be cautious
        ## of those errors: so I do a probe:
        try:
            iPC.probeNoFontsDirError()
        except: 
            return
        
        paf = os.path.join(iPC.appPath(),"overlap_counts")
        try:
            if os.path.exists( paf ):
                fr = open( paf, "rb" )
                self.OVERLAP_COUNT_DICT = pickle.load( fr )
                fr.close()
        except:
            ##TODO ??
            raise



def getSegfontsList():
    """
    On startup, open the 'segfonts' file and keep it handy in a global list.
    This list is written to 'segfonts' file by the 'checkFonts' func in this module.
    """
    global segfonts
    try:
        ## appPath() may be bad.
        iPC.probeNoFontypythonDirError()
    except:
        ## Bail
        return
    
    paf = os.path.join(iPC.appPath(),"segfonts")
    try:
        if os.path.exists( paf ):
            fr = open( paf, 'r' ) # byte string only ascii file
            segfonts = fr.read().split("\n")
            fr.close()
    except:
        ##TODO ??
        raise




def checkFonts( dirtocheck, printer ):
    """
    Jan 18 2008
    Scan a tree for fonts that can cause segfaults.
    Writes a file 'segfonts' and creates a list 'segfonts'
    that gets checked to exclude them.

    printer is a function of some kind.

    Can be called from the cli or the gui.
    """
    global segfonts

    code = """
from PIL import ImageFont
try:
    font=ImageFont.truetype("%s", 24, 0)
    dud=font.getname()
except:
    pass
    """
    def checkForSegfault( pafbytestring ):
        ## Uses Ajaksu's idea : 17 Jan 2008. Thanks!
        segfault_I_hope = False
        ## I have ignored ALL catchable errors (see code var)
        ## This is because I want to (try to) only catch SEGFAULTS
        ## and leave all other flavours of font-related errors to
        ## the fontcontrol module -- where fonts are still useable
        ## if not visible.
        retval = subprocess.call( ["python",  '-c', code %  pafbytestring] )
        if retval != 0:
            segfault_I_hope = True
        return segfault_I_hope
    printer ( _("Checking fonts, this could take some time.") )
    printer ( _("Starting in %s:") % dirtocheck )
    printer ()
    ## dirtocheck comes-in as unicode - let's stick to byte strings:
    dirtocheck = LSP.to_bytes( dirtocheck )
    seglist = [] # our local list of newly found bad fonts
    gotsome = False
    for cwd, dirs, files in os.walk( dirtocheck ):
        printer(_("Looking in %s...") % os.path.basename(cwd) )
        ## We only want certain font files:
        fontfiles = [f for f in files if f.upper().endswith( tuple( fontcontrol.font_file_extensions_list )) ]
        #if len(fontfiles) < 1:
        #    printer (_("No supported fonts found there..."))
        #    printer()
        for file in fontfiles:
            paf = os.path.join( cwd, file )
            bad = checkForSegfault( paf )
            #bad = True #TEST
            if bad:
                gotsome = True
                seglist.append( paf )
                printer ( _(" Bad font: {}".format(file)) ) # show it on-screen somewhere.

    ## Now write the segfonts file:
    if seglist:
        ## Add the new fonts found to the ones in global segfonts list
        for bf in seglist:
            segfonts.append(bf)
        ## Now remove duplicates
        tmp =  list( set( segfonts ) )
        segfonts = tmp
        del (tmp)

        ## Now save it.
        ##TODO ?? try/except on iPC appPath here?
        paf = os.path.join(iPC.appPath(),"segfonts")
        fw = open( paf, "w" ) # byte string ascii
        bytestring = "".join([line + "\n" for line in segfonts if line != ""])
        #print "about to write bytestring:"
        #print [bytestring]
        #print
        fw.write( bytestring )
        fw.close()

    if gotsome:
        printer(_("Bad fonts were found. They have been noted. I will ignore them in future."))
    else:
        printer(_("I could not find any bad fonts."))
    printer()
    printer(_("The process is complete.")) 


def isFolder(thing):
    """True if a folder. False if not - but that does not mean it's a pog."""
    if os.path.isdir(thing): return True
    return False


def isPog(thing):
    """True if a Pog. False if not."""
    ## thing comes in as UNICODE
    ## iPC.getPogNames() is a list of BYTE STRINGS
    ## We must encode thing to a byte string to avoid warnings:
    if LSP.to_bytes( thing ) in iPC.getPogNames(): #getPogNames contains byte strings!
        return True
    if thing == "EMPTY": return True #Special case
    return False


class FPState:
    """The global vars to hold the state of the situation."""
    def __init__(self):
        ## Contains the Pog or Folder being viewed
        self.viewobject = None

        ## Refs the view object *after* the filter has been applied
        self.filteredViewObject= None

        ## Contains a Pog (or None) that is the Target
        self.targetobject = None

        ## Represents the situation in a letter code
        ## P for Pog, F for Folder, E for Empty, N for None
        self.viewpattern = ""
        self.targetpattern = ""

        ## Will be "NOTHING_TO_DO", "REMOVE" or "APPEND" (Add fonts to Pog)
        self.action = ""

        ## Can an item be ticked
        self.cantick = None

        ## The View and Target pogs chosen are the same.
        self.samepogs = False

        ## How many tick marks.
        self.numticks = 0

        ## On start, there's a test for fontconfig dir
        self.fontconfig_confd_exists = False

####
## Save and Load the conf file
class Configure:
    """
    Makes/Loads the conf file.
    Supplies size, pos, numinpage, text string and point size to other objects.
    """
    atoz = _("Jump the lazy dog fox")
    def __init__(self):
        ## Private vars
        self.__dontSaveNumInPage = False

        ## PUBLIC vars :  Set some defaults:
        self.size = (800,600)
        self.pos = (10, 10)
        self.numinpage = 10
        self.text = Configure.atoz
        self.points = 64
        #Nov 2017
        self.max_num_columns = 1 #Beware 0 = divide by zero
        self.lastview = "EMPTY" # a pog name or a folder path.
        self.usegui = "wxgui"
        self.max = True
        self.lastdir = iPC.home()
        ## Added June 2009
        self.recurseFolders = False
        ## Added Sept 2009
        self.ignore_adjustments = False
        ## Added 3 Oct 2009
        self.app_char_map = "UNSET" # A string of an app name.
        ## Nov 2017
        self.hush_pog_name = ""

        self.__setData()

        ## Oct 2009 -- The Character Map Controller.
        self.CMC = charmaps.CharMapController(  self.app_char_map_set )

        try:
            iPC.probeNoFontypythonDirError()
        except:
            ## Can't access the appConf file at all, so bounce.
            return

        if os.path.exists(iPC.appConf()):
            try:
                pf = open(iPC.appConf(), "rb" ) # Binary for new pickle protocol.
                #self.__data = pickle.load( pf )
                ## I want to merge-in what may be in pickle
                self.__data.update( pickle.load( pf ) )
                pf.close()
            except:
                ## Dec 2007 : Let's try erase and rewind
                os.unlink(iPC.appConf())

        if not os.path.exists(iPC.appConf()):
            print _("No config file found, creating it with defaults.")
            self.Save()


        ## Now get them into the instance vars:
        try:
            self.size = self.__data['size']
            self.pos = self.__data['pos']
            self.numinpage = self.__data['numinpage']
            self.text = self.__data['text']
            self.points= self.__data['points']
            self.max_num_columns= self.__data['max_num_columns']
            self.lastview = self.__data['lastview']
            self.usegui = self.__data['usegui']
            self.max = self.__data['max']
            self.lastdir = self.__data['lastdir']
            self.recurseFolders = self.__data['recurseFolders']
            self.ignore_adjustments = self.__data['ignore_adjustments']
            self.hush_pog_name = self.__data['hush_pog_name']
            self.app_char_map = self.__data['app_char_map']
            ## We must also set our instance of the CharMap Controller:
            ##  This can be "UNSET" (default first run) or an appname
            ##  That appname may be valid or not (it may have been uninstalled...)
            self.CMC.set_current_appname(self.app_char_map)

        except KeyError:
            ## The conf file has keys that don't work for this version, chances are it's old.
            ## Let's delete and re-make it.
            try:
                os.unlink(iPC.appConf())
            except:
                print _("The fontypython config file is damaged.\nPlease remove it and start again")
                raise SystemExit
            self.Save()

    def dontSaveNumInPage(self, flag):
        self.__dontSaveNumInPage = flag

    def __setData(self):
        self.__data = {
            "size" : self.size,
            "pos" : self.pos,
            "numinpage" : self.numinpage,
            "text" : self.text,
            "points" : self.points,
            "max_num_columns" : self.max_num_columns,
            "lastview" : self.lastview,
            "usegui" : self.usegui,
            "max" : self.max,
            "lastdir" : self.lastdir,
            "recurseFolders": self.recurseFolders,
            "ignore_adjustments": self.ignore_adjustments,
            "app_char_map" : self.app_char_map,
            "hush_pog_name" : self.hush_pog_name,
         }
    def app_char_map_set( self, x ):
        '''
        A callback from the CharMapController: when the CURRENT_APPNAME is set,
        this gets called to keep the config version of the appname current.
        '''
        self.app_char_map = x

    def Save(self) :
        #If we are NOT to save the numinpage, then fetch it from what was there before.
        if self.__dontSaveNumInPage:
            self.numinpage = self.__data["numinpage"]
        self.__setData()
        try:
            ## At this point, we have a good appPath. No try/except
            pf = open( iPC.appConf(), "wb" )
            pickle.dump(self.__data, pf, protocol = pickle.HIGHEST_PROTOCOL )
            pf.close()
        except IOError:
            print _("Could not write to the config file.")

        Overlap.sleep() #sept 2009 : Save the OVERLAP_COUNT_DICT




def instantiateViewFolder( foldername, recurse=None ):
    """
    Creates a Folder object and fills it with FontItem objects
    according to what's in the folder's path.

    This is the VIEW - i.e. what you are looking at.
    """
    if state.viewobject: del state.viewobject
    ## Default assumptions in case of raised error.
    state.viewobject = fontcontrol.EmptyView()
    state.viewpattern = "E"

    #July 2016
    #=========
    # Made recurse default to None in the def sig.
    # This has the effect of allowing THREE states to enter:
    # None, True, False
    # None means the call came from cli.py
    #  If so, we want to fetch the recurse from config -  
    #  so it becomes either T or F, depending on last state.
    #  This has stopped that initial Schroedinger's Cat state
    #  of the recurse setting.
    if recurse is None:
        recurse=config.recurseFolders
    else:
        config.recurseFolders = recurse
    #print "recurse:", recurse
    ifolder = fontcontrol.Folder(foldername, recurse) #raises : fontybugs.FolderHasNoFonts : BENIGN ERROR.
    ## Only continues if there is no problem.
    state.viewobject = ifolder
    ## Because we have a new view object, we must reset the last filteredViewObject
    state.filteredViewObject = None

    config.lastview = foldername
    state.viewpattern = "F"
    markInactive()
    flushTicks()


def instantiateViewPog( newpog_name ):
    """
    Given a Pog Name string, make a Pog object.

    This is the VIEW - i.e. what you are looking at.

    A VIEW Pog can be EMPTY. This happens on the first run when there is no config file.
    There are other arcane situations too, but I forget.
    """
    if state.viewobject: state.viewobject = None

    if newpog_name == "EMPTY":
        ipog = fontcontrol.EmptyView()
    else:
        ipog = fontcontrol.Pog( newpog_name )
    ## Test TARGETPOG to see if this is the same pogname
    ## The not None test is for first run - there is no targetobject yet just after cli.py calls us, so we
    ## do not want to access it or we get NoneType errors.
    if state.targetobject is not None and state.targetobject.name == newpog_name:
        state.samepogs = True
    else:
        state.samepogs = False
    ## Must gen the Pog to get a count of items:
    ## Errors raised in genList (and company): 
    ## fontybugs.PogInvalid (only valid from cli pov)
    ##
    ## We 'handle' this by NOT catching it, pass it up.
    ipog.genList()

    ## Continue if all ok.
    state.viewobject = ipog
    ## Because we have a new view object, we must reset the last filteredViewObject
    state.filteredViewObject = None

    config.lastview = newpog_name
    if len(state.viewobject) == 0:
        empty = True
        state.viewpattern = "E"
    else:
        empty = False
        state.viewpattern = "P"
        markInactive()
        flushTicks()

    return empty # this return is only used in cli.py


def instantiateTargetPog( newpog_name ):
    """
    The app could begin with NO TARGET POG chosen.
    After that (in the gui) either a pog is chosen or NO POG is chosen (i.e. None)
    Therefore - there can NEVER BE a targetobject called EMPTY

    The CLI install/uninstall/purge DO NOT use this routine.
    """
    if state.targetobject: del state.targetobject
    ipog = fontcontrol.Pog(newpog_name)
    ## Must gen the Pog to get a count of items:
    ipog.genList() # Raises fontybugs.PogInvalid error THIS ENDS THE APP.
    ## TEST the viewobject which is the stuff being 
    ## LOOKED AT IN THE MIDDLE OF THE SCREEN (which could be a Pog OR a Folder)
    ## If it's a Pog then we may have chosen the same Pog (on the right)
    ## that we are looking at, so check that:
    state.samepogs = False
    if isinstance( state.viewobject, fontcontrol.Pog ):
        if state.viewobject.name == newpog_name:
            ## The pog clicked in the TARGET is the same as what's ALREADY selected in the VIEW
            state.samepogs = True

    quickinstalledflag = False
    if ipog.isInstalled(): quickinstalledflag  = True
    state.targetpattern = "P"
    state.targetobject = ipog
    markInactive()
    flushTicks()
    return quickinstalledflag


def markInactive():
    """
    INACTIVE means the font displayed is already inside the
    chosen target pog. So, it's not 'active', not clickable etc.

    Mark each font item as inactive, as needs-be.
    Clear the ticks.
    Sets the message to display in the fontmap.
    """
    if state.viewobject: state.viewobject.clearInactiveflags()

    if state.viewobject and state.targetobject:
        ## What's in TARGET must be inactive in VIEW

        ## pafBlist is a list of UNICODEs
        ## glyphpaf_unicode is UNICODE, so I will use it instead		
        ## because we compare it to pafBlist
        pafBlist = [i.glyphpaf_unicode for i in state.targetobject]

        for iA in state.viewobject:
            if iA.glyphpaf_unicode in pafBlist:
                iA.activeInactiveMsg = _("This font is in %s") % state.targetobject.name
                iA.inactive = True
        del pafBlist


def SetTargetPogToNone():
    state.targetobject = None
    state.targetpattern = "N"


def SetViewPogToEmpty():
    state.viewobject = fontcontrol.EmptyView()
    state.viewpattern = "E"


def flushTicks():
    for fi in state.viewobject:
        fi.ticked = False
    state.numticks = 0


def logSegfaulters( lastPaf ):
    """
    Writes a string to ~/.fontypython/lastFontBeforeSegfault
    """
    ## No need to try/except appPath.
    paf = os.path.join( iPC.appPath(),"lastFontBeforeSegfault")
    try:
        f = open( paf, "w" )
        lastPaf = LSP.ensure_bytes( lastPaf )
        f.write( lastPaf + "\n" )
        f.close()
    except:
        ## TODO ??
        raise

def rm_lastFontBeforeSegfault_file():
    paf = os.path.join( iPC.appPath(),"lastFontBeforeSegfault")
    try:
        os.remove(paf)
    except:
        pass 

##Nov 2017
## Hush code used from clifuncs and wxgui
##
def hush_with_pog( pog, printer ):
    """
    The printer func is under dev - aiming for a way to use this
    same func from the gui and cli

    The existence of the fontconfig conf.d directory must be
    confirmed before code gets here.

    See cli2.py, for example. It happens in a probeAllErrors call.
    """
    bugs = []
    printer(_("Trying to hush..."), key="starting")
    if isPog( pog ):
        hushpog = fontcontrol.Pog( pog )
        ## gen and install it!
        printer( _(u"Installing (%s)") % pog, key="installing")
        try:
            hushpog.genList()
            ## Aside: it is not an error to 
            ## install again ( > once) - hence I don't need
            ## to worry about toggling this hush/unhush
            ## thing.
            hushpog.install()
            ##TESTING: raise fontybugs.PogInvalid
        except (fontybugs.PogInvalid,
                fontybugs.PogEmpty,
                fontybugs.PogAllFontsFailedToInstall,
                fontybugs.PogSomeFontsDidNotInstall,
                fontybugs.NoFontsDir ), e:
            bugs.append(e.get_error_string())
    ## The arg was not a valid pog.
    else:
        bugs.append(_(u"The Pog \"{}\", cannot be found.").format( pog ))
    ## Only if that was 100% do we hush:
    ## This process can accrue new bugs too.
    if not bugs:
        try:
            ## Just because I'm nervous: Is my path actually in "fontconfig"?
            ## This should never happen...
            if not os.path.dirname(iPC.user_fontconfig_confd()).endswith("fontconfig"):
                raise fontybugs.NoFontconfigDir(path="**HUSH_PAF WEIRDO ERROR. Please open a ticket on our bug tracker**")
            ## Write the XML fontconfig .conf file.
            ## don't care if it's already there. Just overwrite.
            f = open( HUSH_PAF, "w" )
            hxml = LSP.ensure_bytes( HUSH_XML )
            f.write( hxml )
            f.close()
        # some new bug..
        except Exception as e:
            bugs.append(unicode(e))
            
    if not bugs:
        printer( _("Done. A hush settles over your fonts. " \
                    "Go: work in silence."), key="success" )
    return bugs

def un_hush( printer ):
    """
    The existence of the fontconfig conf.d directory has
    to be confirmed before code gets here.

    See cli2.py, for example. It happens in a probeAllErrors call.
    """
    if not os.path.exists(HUSH_PAF):
        printer (_("The hush isn't there. Nothing to do."))
        return
    bugs = []
    try:
        printer( _("Trying to unhush..."), key = "starting")
        os.unlink( HUSH_PAF )
    except Exception as e:
        bugs.append(unicode(e))

    if not bugs:
        printer( _("The noise has returned; the hush is gone."),
                key="success")
    return bugs

######      #######
## Setup globals ##
######      #######

LSP = linux_safe_path_library.linuxSafePath()

## Ensure we have "fontypython" and "fonts" dirs.
iPC = PathControl(XDG_DATA_HOME, XDG_CONFIG_HOME)

HUSH_XML_FILE="1.fontypythonhusher.conf"
HUSH_PAF = os.path.join( iPC.user_fontconfig_confd(), HUSH_XML_FILE)
HUSH_XML="""<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
<!--
This file was created by fontypython.
It rejects all fonts in /user/share/fonts
You can delete this file at any time.
-->
<selectfont>
 <rejectfont><glob>/usr/share/fonts/*</glob></rejectfont>
</selectfont>
</fontconfig>"""

## Borrowed from wxglade.py
## The reason for this is to find the path of this file
## when it's called from an import somewhere else.
## There is no sys.argv[0] in this case.
root = __file__
if os.path.islink(root):
    root = os.path.realpath(root)
fontyroot = os.path.dirname(os.path.abspath(root))

## Where my images and things are.
mythingsdir = os.path.join(fontyroot,"things/")


## Instance the Overlaperizer (once)
Overlap = Overlaperize()
Overlap.wakeup()

## Prepare the list of fonts that have caused segfaults.
## Jan 18 2008
segfonts = []# Global var
getSegfontsList()


state = FPState() #The only instance of the state object -- app-wide

## Our config instance - it will have one instance across
## all the modules that use it.
config = Configure()
