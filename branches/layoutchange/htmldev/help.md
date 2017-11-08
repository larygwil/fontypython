<a name="top"></a>
<div align=right><font size=-2 color="{medium}">Updated July 2016&nbsp;&nbsp;</font></div>
<img src="fontypythonmodules/help/common/fphelplogo.png">

*FontyPython is a font viewer and manager for Gnu/Linux. Use it to view, gather and manage fonts. You can install and uninstall fonts to your home fonts folder for temporary use in other apps.*

[User Fonts](#userfonts) | [The Layout](#layout) | [Menus](#menus) | [Shortcuts](#shortcuts) | [Tips](#tips) | [Localization](#l10n) | [Bugs](#bugs) | [Licence](#lic)

Ye Olde Basic Idea
=======
You visually gather fonts into "Pogs". You then install the Pog, and all its fonts will be available to other apps. When you finish your work, uninstall the Pog.

I just stumbled onto the word "Pog", it comes from the middle of "typography". It means "collection" or "group" or "bunch" or "box" or "case" or "stack" or "pile" &mdash; you get the picture.

Your fonts never move from where they live, neither are copies made; only links to the original files are used to install the fonts into your user fonts directory.

For example, you might have a Pog called "Zoo Logo" into which you place all the fonts needed to design a logo for a Zoo. After that, when you want to work, simply install the "Zoo Logo" Pog and start your design app. All those fonts will now appear in Inkscape, the Gimp and other apps. When you are done designing, you uninstall "Zoo Logo" and all those fonts go away. (The links to the original files are removed, **not** the actual original font files!)

Fonty is also great for just looking at fonts, wherever they are on your computer, without having to install them first. She also has a command line, allowing very quick use. You can install/uninstall Pogs without having to start the entire gui, which is neat.

<a name="userfonts"></a>
User Fonts
=====
Depending on the tides of fate, your user font directory may be in one of these places:

* .fonts
* .local/share/fonts
*  Somewhere else entirely. Sorry, I don't make the rules.

If there is a dot in front (like .fonts) it means the directory is "hidden". You might not see it in your file manager. 

Whatever it's called and wherever it is, any fonts listed in that directory are "installed" and your apps will be able to use them. Fonty's job is to shuttle fonts in and out of here so you don't have to.

If your fonts are not working, it may be that you don't have a user fonts directory. You'll have to search around and figure it out.

[Top](#top)

<a name="layout"></a>
Layout
=====
On the left are the Source (top) and Target (bottom) controls. On the right is the Font View. 

Left-top
--
Font *Sources* are directories or Pogs. There are tabs for you to choose. 

Beware the **include sub-folders** check box. When checked, Fonty will look for fonts in **all** the sub-directories within your chosen Source directory. If there are lots of fonts in there, she might hang. Use this with caution.

Left-bottom
--
*Targets* are Pogs; they are where you gather your fonts.

Right
--
Fonts in your Source will be visible in the Font View. You can click on the fonts you want to select. At the bottom of the Font View are some controls to help you filter, page and manage the fonts you are looking at.

The Font View will also attempt to display in columns, so you can see many fonts in one go. The columns vary by how big each font is and the width of your window. You can control the number of columns in the Settings.

Areas of interest:

1. Change font size: Ctrl + scrolling the mouse wheel (up/down).

2. Character Map Button: The little magnifying glass. If you have a character viewing app installed, 
   this button will show and when clicked will open it to let you view the full character-set of the font.
   You can choose which character map viewer to use in the Settings. The choices are gucharmap or kfontview.

3. Tick Area: Clicking anywhere on a font will either tick or cross it.
   **Tick:** means the font can be placed into a Target Pog &mdash; i.e. the one chosen in the right-hand panel.
   **Cross:** means the font will be removed from the Source Pog (The one you are viewing at the moment)
   &mdash; i.e. the Pog currently chosen on the left-panel.
   **Neither:** means you have only a Source selected and can only view the fonts.

4. Font Info: Under each font you will find the family and style and filename. 
   When you use the filter to search, this is the text that is searched.

**Please note:** An error may appear instead of the expected font glyphs. 
Such fonts cannot be drawn. You can select, Pog, and install them. Most of the time, these fonts will still work in your design apps, like Inkscape.

(See [Bugs](#bugs) for more information about font errors.)

[Top](#top)

<a name="menus"></a>
Menus
====




The happy-harmony filename-formula 
-------
Use **only** these in names:

* A to Z
* a to z
* 0 to 9
* . (dot)
* _(underscore)

Spaces are verboten. Colons, minus (dash), quotes, brackets, *you name it* — VERBOTEN!

Examples of "names" are your **directories** in public\_html and the **values** you give your
define variables in the wp-config file.

**You have been warned!**



[Top](#top)


<a id="updateinfo"></a>
Update Info
===========
#####July 9th 2017 (Vers v3.0.2)

1. Fixed a serious bug that prevented dbs from being restored. The old zip format is
   now detected and handled quietly. New backups are done in the new way.
   Should just drop-in and work.

2. Fixed import errors related to db name in mysql. Now drop and create sql commands
   in the backup are obeyed.

#####June 2017 (Vers v3.0.1)

1. Changed the AUTH Realm's name to "Headline.Technologies" (What it was before leaked
   the user name.)

2. Added a suffix onto all passwords. See the Security doc for detailed information.

#####June 2017 (Vers v3.0.0)

1. Added a form to first collect a log string before doing a database or tree backup.
   The textbox allows for only one line (max 100 chars) and works quite hard to exclude
   a bunch of nasty characters. It's probably not perfect, so don't push it too far.

2. Added a way to open/close sections on the home page — saves space and looks better.

3. Fixed permissions to the script to ensure it will run. It's ugo+x now. TODO: test.

#####June 2017 (Vers v2.0.14a)

1. Added ug+x permission to the script to ensure it will run. Well, to do our best anyway.

#####June 2017 (Vers v2.0.14)

1. Adding an extra link on the edit anchor for https and http — to cater for situation where 
   Cloudflare is providing "fake" https, but cpanel wants http.

2. Experimenting with the cpanel editor url. Managed to shorten it a bit.

#####June 2017 (Vers v2.0.12)

1. Used shellcheck to lint my code. Fixed a few things as per suggestions. No major issues.

#####June 2017 (Vers v2.0.11)

1. Removed all the passwords from this README. They are all xxxxxx now. See the HDL Security Google doc instead.

2. Removed all user names too. Also for security reasons.

3. Added a physical newline under the -- in the logfiles. Easier to use when editing.

4. Log files now grow upwards. This might fail if the log files get overly large.
   TODO: code to rotate the log files when their size is beyond some threshold.

5. Altered some colours to make buttons clearer.

6. Epic addition of excludes file section in the help. Took ages.

#####June 2017 (Vers v2.0.10)

1. Yet another cron bug fix. Tricky bugger.

2. More css cleanups - defined the buttons a little better.

3. Work on dev and deployment scripts. Also automated backup to gdrive.

#####June 2017 (Vers v2.0.7)

1. Fixed bug in cron toggle. Now each site can have a **6 AM** cron (or not) while 
   *also* having other crons. As long as other crons are on other times, it
   won't touch them.

2. Some CSS fixes.

3. Converted README to markdown so I can produce an html help file.

4. Caused stats page to show totals of sql and tree backups, and to bold the latest 
   file, which is simply the one first in the list.

#####Vers v2.0.3 (adminv2.cgi)

1. The file **adminv2.cgi** will live alongside admin.cgi. When you are ready to use 
   the new system, we can drop the old one. 
   
   The zips, tgz and logfiles of the old system **will not** be ported to the 
   new. The old 00.* and 01.* directories will all remain in hdlbin. You should move
   or delete them some day.

2. Extra "libs" directory with some .sh library files added. Leave it alone.

3. Added cron toggle buttons and code. Can now add a cron to backup the db of the 
   current site. Cron now uses a direct call to the script so that the webserver is 
   not involved in the actual backup.

4. Added visual display of the logs. On the restore db page, you can
   use this log to choose a zip to restore.

5. **HDL\_CLIENT\_NAME:** You should add a new **define("HDL\_CLIENT\_NAME", "some\_name");** 
   to your wp-config.php files. Without this variable, the script will stop. This defined 
   name will be used in output and filenames.


6. The .htaccess file is now sought and, if not suitable, a new one is written. 
   See [Security](#security) section.

7. A new directory named **storedfiles** is created in $HOME (e.g. /home/SAMPLEUSERNAME). 
   All zips and tgz and logs now live there.

99. **NB:** Logging format must be:

        TITLE
        ====  <-- Four "=" signs
        Your text ONLY goes here. Leave the other stuff alone.
        --    <-- Two "-" signs
   
    _TOFIX: The pre tags on this log format are not showing newlines. I have no idea why._

#####May 31 2017 (Vers 1.0.11b)

1. Adding a timer to count seconds taken on tar and db backup.

2. Remarked the verbose tar output in order to try speed the whole thing up.

3. Added a test looking for a .htaccess file with "AuthType Basic" within. Aborts if it
   does not find it.

4. Added a "help" file. It cats this file and the sample excludes file.

#####May 30 2017 (Vers 1.0.11a)

1. Changed the excludes system to use a text file of strings. The file is named 
   "TREE.EXCLUDES.FILE". Yes, that includes that useless .FILE at the end. Lucky you.
            
   It must live in the site's directory:
   * For ROOT, this is in **public\_html**
   * For "SampleSite" this is in **public\_html/SampleSite**
            
   If there is no TREE.EXCLUDES.FILE file, one will be made with some basic entries.

   **See also:** SAMPLE.TREE.EXCLUDES.FILE (in hdlbin) for example use.

#####Vers 1.0.11

1. Added code to create logfiles in tree and sql backup dirs. User can then annotate
   as required. Also added links into cpanel's text editor for convenience.

2. Removed the exclude on zip files in the site zip process. Added some new dirs to
   be excluded. List of what is excluded is printed in the Site stats for convenience.

#####May 29 2017 (Vers 1.0.10)

1. Added code and UI to toggle **WP\_HTTP\_BLOCK\_EXTERNAL** flag in the 
   wp-config.php file.

#####Feb 7 2016 (Very old)

1. Removed the 30 day delete of sql files.



[Top](#top)



<a id="setup"></a>
Setup/Install
=============
1. Unzip the distribution (distrib) zip file into the **"public\_html"** directory. The distrib
   will have a filename of the form: *hdlbin.distrib.VERSIONNUMBER.zip*

2. **NB** — Delete any .htaccess file in ~/public\_html/hdlbin/ 

3. Delete the distrib zip.

4. **NB**—The functioning of the script relies on these defines in every wp-config.php

   * HDL\_CLIENT\_NAME
   * DB\_NAME
   * DB\_USER 
   * DB\_PASSWORD

5. Ensure the adminv2.cgi file has permission 755. It should already be done.

6. Build a URL, see URL section below, and visit the site.

**NB**—Visit the admin site at least once so it can create a new .htaccess file.

[Top](#top)


<a id="security"></a>
Security
========
CGI
---
The script requires the *secret* argument in the url.

** All usernames and passwords removed from this file — see our Security Google doc.

Apache Auth
-----------
The script will now write the appropriate security files if they do not exist.

** All usernames and passwords removed from this file — see our Security Google doc.



[Top](#top)


<a id="security"></a>
URL
===
Replace "admin.cgi" with "adminv2.cgi" as-per.

The basic script
----------------
The URL is usually:

    http://www.blah.co.za/hdlbin/admin.cgi

Parameters
----------
Add params in the normal GET manner:

    ?param=val&param2=val2 etc.

###The parameters are:

* <strong id="secretparam">secret=xxxxxx</strong> (Required.)

* **site=** The name of your site sub-folder or "ROOT" if you are just working in
  public\_html <br />
  (Optional/auto-filled - this param is not manually required as you can choose it
  from the admin home screen).

* **option=** One of: (Required, will complain if missing)

  * **home** : Will take you to the home screen with a menu to choose a site.

  * **prebackupdb** : Will take you to the database backup form. This is where you
    can type a log entry. The entry can be blank. Submitting the form will do 
    the actual backup.

  * **backupdb** : Will perform a backup of the DataBase to a zip file in the 
    ~/storedfiles folder.

  * **restoredb** : Lets you choose a db to restore from a list of zip files.

  * **prebackuptree** : Takes you to the tree backup form. Same as the db form.

  * **backuptree** : Will bundle all the sites's files into a tarball (.tgz) and 
    store it in the ~/storedfiles folder.

  * **restoretree** : Will tell you your fortune. :)

  * **setexternaltrue** : Will set WP\_HTTP\_BLOCK\_EXTERNAL true in wp-config.php.

  * **setexternalfalse** : Does the opposite of setexternaltrue.

  * **crontabadd** : Will add a line to cron to backup the db of the current site.

  * **crontabremove** : Will remove the db backup line from the cron for the current site.


[Top](#top)

<a id="excludesfile"></a>
Excluding files
===============
The **TREE.EXCLUDES.FILE** file allows you to control what to skip in a **tree backup**. Fill it in 
as you need and place it in a site's directory. Always with that name.

For this example, pretend you are standing in public\_html while you build paths. Anything 
matched and any children are excluded.

1. To exclude _specific_ directories, name the path: **test/downloads**

   * /home/FOO/public\_html/**test/downloads** — would match.
   * /home/FOO/public\_html/some/other/**test/downloads** — I am not sure. Needs testing.

2. To exclude _only one directory_, name it with dotslash: **./downloads**

   * /home/FOO/public\_html/**downloads** — _would_ be excluded.
      * /home/FOO/public\_html/wp-content/**downloads** — _would not_ excluded.
      * /home/FOO/public\_html/bingbamboom/**downloads** — _would not_ be excluded.

3. To exclude _anything by name_, just state it: **downloads**
   * /home/FOO/public\_html/**downloads** — _would_ be excluded.
   * /home/FOO/public\_html/crocodiles/**downloads** — _would_ be excluded.

4. To exclude _wildcards_ use: **&lowast;**
   * &lowast;.**zip** — This would match somename**.zip**
   * &lowast;**NOTME**&lowast;**.html** — This would match private**NOTME**stuff**.html**


[Top](#top)


<a id="cron"></a>
How to cron
==========
New way
-------
The new command to call does not use curl. The same script is now also callable directly:

    /home/WHATEVERYOURUSERNAMEIS/public_html/hdlbin/adminv2.cgi -site XYZ -option backupdb

**Required arguments**

The arguments are *dash argument space value*

* **-site XYZ** — where XYZ is a site name, the directory of that website's wp-config.php file.
* **-option backupdb** — this can only be *backupdb* currently.

The CGI gives you buttons to make/remove a 6 AM daily cron. You can always
copy/paste from that (in cpanel) into other time slots. Any crons on times other
than 6 AM will **not** be touched by this script. 

Old way
-------
With the Apache auth realm enabled, you need a username/password to use the cgi. 
You pass these with curl's -u flag. (Note the single quotes around the argument.)

curl -s -u 'XXXX:<password>' 'http://www.hdl.co.za/hdlbin/admin.cgi?secret=xxxxxx&site=ROOT&option=backupdb'

[Top](#top)




<a id="examples"></a>
Examples
========

* www.hdlx.co.za/hdlbin/admin.cgi?secret=xxxxxx&option=home
* www.hdlx.co.za/hdlbin/admin.cgi?secret=xxxxxx&site=ROOT&option=prebackupdb
* www.hdlx.co.za/hdlbin/admin.cgi?secret=xxxxxx&site=sar&option=backupdb
* www.hdlx.co.za/hdlbin/admin.cgi?secret=xxxxxx&site=sar&option=setexternaltrue
etc.

[Top](#top)
