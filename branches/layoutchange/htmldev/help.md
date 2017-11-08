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

<center><img src="fontypythonmodules/help/common/break.png" border="0"></center>

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
<center><img src="fontypythonmodules/help/common/break.png" border="0"></center>
<a name="layout"></a>
Layout
=====
On the left are the Source (top) and Target (bottom) controls. On the right is the Font View. 

<img src="fontypythonmodules/things/icon_source.png">&nbsp; The Sources
--
Font *Sources* are directories or Pogs. There are tabs for you to choose. 

Beware the **include sub-folders** check box. When checked, Fonty will look for fonts in **all** the sub-directories within your chosen Source directory. If there are lots of fonts in there, she might hang. Use this with caution.

<img src="fontypythonmodules/things/icon_target.png">&nbsp; The Targets
--
*Targets* are Pogs; they are where you gather your fonts.

* You cannot use an already **installed** Pog as a Target. (Uninstall it first.)
* By holding Ctrl you can select many Pogs at once for installing/uninstalling/etc. many at once.

###Pog management buttons
1. **Clear selection:** Will unselect whatever Pogs you selected.
2. **Install:** All the Pogs selected will be installed. i.e. The fonts in them will be available to the system.
3. **Uninstall:** All those selected will be uninstalled.
4. **New Pog:** This will ask you for a name and make a new Pog.
5. **Delete:** All selected Pogs will be deleted. It will ask you if you are sure.
6. **Zip:** All selected Pogs will have their fonts zipped into individual zip files in the directory you choose.

<img src="fontypythonmodules/things/icon_viewing.png">&nbsp; The Font View
--
Fonts in your Source will be visible in the Font View. You can click on the fonts you want to select. At the bottom of the Font View are some controls to help you filter, page and manage the fonts you are looking at.

The Font View will also attempt to display in columns, so you can see many fonts in one go. The columns vary by how big each font is and the width of your window. You can control the number of columns in the Settings.

###Fonts

1. **Point size:** Ctrl + scrolling the mouse wheel (up/down).

2. **Character Map Button:** The little magnifying glass. If you have a character viewing app installed, 
   this button will open it.
   (You can choose which character map viewer to use in the Settings. 
   The choices are gucharmap or kfontview &mdash; but you must install one first.)

3. **Selecting fonts:** Clicking anywhere on a font will select it.
   * **Tick:** means the font can be placed into a Target Pog &mdash; i.e. the one chosen in the right-hand panel.
   * **Cross:** means the font will be removed from the Source Pog (The one you are viewing at the moment)
   &mdash; i.e. the Pog currently chosen on the left-panel.
   * **Neither:** means you have only a Source selected and can only view the fonts.

4. **Font Info:** Under each font you will find the family and style and filename. 
   When you use the filter to search, this is the text that is searched.

5. **Greyed-out:** Fonts that are already in the Pog (i.e. selected as a target) are disabled.

6. **Bad fonts:** An error may appear instead of the expected font glyphs. Such fonts cannot be drawn.
   You can select, enpog, and install them. Most of the time, these fonts will still work in your 
   design apps, like Inkscape.
   (See [Bugs](#bugs) for more information about font errors.)

###Font controls

1. **Filter:** 
  * "i,r,b" mean Italic, Regular and Bold. 
  * The "X" button will clear your current filter.
  * The text box is for custom searching. Type something and hit enter. 
2. **Pager:** On the far right is the pager. Use it to step through the fonts as you like.
3. **Left/Right:** Arrow buttons for paging one forward or back. 

[Top](#top)

<center><img src="fontypythonmodules/help/common/break.png" border="0"></center>

<a name="menus"></a>
Menus
====
1. **Tools menu**
   * **Settings:** Access the settings for the font view. 
     Shortcuts: Ctrl+S or middle-click on the font view.
   * **Purge Pog:** The Pog you are currently viewing may contain fonts that are not there anymore.
     Use purge to remove them. 
     *Explanation:* A Pog contains a list of paths. If a font is somehow moved on your hard drive, 
     then the path in the Pog will be old. Purging will remove these ghost fonts.
   * **Exit:** Guess. :-)
2. **Selection menu**
   * **Select ALL the source fonts:** While only a few fonts are shown in a page at a time, there may 
     be thousands in the selected source. This will select **all** of them, in one go.
   * **Clear ENTIRE selection:** Will clear any selection.

[Top](#top)

<center><img src="fontypythonmodules/help/common/break.png" border="0"></center>

<a name="shortcuts"></a>
Shortcut keys
====
If shortcut keys don't work, click in the filter text box. This seems to kick them back to life. Don't ask me what's going on....

1. **Esc** key will close your app quickly.
2. **Ctrl+LeftArrow/Ctrl+RightArrow** will step through fonts like the Next and Previous buttons do.
3. **Middle-click (the wheel-button)** in the font view (position 3 above) will open the Settings 
   screen (like Ctrl+S does)
4. **Ctrl + Scroll mouse wheel up/down** will increase/decrease the size of your font previews quickly.


[Top](#top)

<center><img src="fontypythonmodules/help/common/break.png" border="0"></center>

<a name="tips"></a>
Tips
===

1. Try to use Fonty from the command-line (from a console). It's easy, simply type:
   fontypython --help
2. Pog files are merely text files. They are very, very simple and this was intentional. Here are some things you can do with them:
   * Open and edit them in any text editor.
   * Append fonts to the end of them, just include the entire path and the font name.
   * *Note for Type1 fonts: Only include the PFA/B file types, not the various metric files that 
     follow them.*
   * If your paths change (say you renamed your folders, or re-installed your O/S) then you can use 
     search/replace to update all the paths to all the fonts in your Pogs. You could do this from 
     the command-line using GNU tools, but any text editor will help you here too.
   * You can backup your Pogs by simply copying them to another folder.
   * One last trick, for those proficient with the Gnu tools, you can do things like this:

        find /home/you/somepath/TTFS/F -iname "Fu*" >> Futura.Pog


[Top](#top)

<center><img src="fontypythonmodules/help/common/break.png" border="0"></center>

<a name="l10n"></a>
Localization Tips
==

If localization is not working it could be there is none for your language; it can also be a
problem with missing packages in your distro. This is what I installed on my system while I 
was developing: (Replace the last two letters with your own language code.)

* language-support-fr
* language-support-en
* language-pack-gnome-fr (This one is very important, it has many stock translations for GTK.)

ENCODING TIP:
Check your LANG variable. Open a console and type:
        echo $LANG
If it reports "C" or "POSIX" or it's blank then you will be running under ANSI (ASCII) encoding only. This means that unusually named fonts and Pogs will likely be invisible to you, function badly, or cause errors. I am putting out fires as fast as I can, but these bugs are hard to find.

To see what other encodings you could be using, type:

        locale -a

You should see a list of locales. If you see one ending in "utf8" that looks like it fits your language, then change your system to use it. You should do this via your system-settings gui, but you can do it temporarily like this:

        LANG=xx_YY.encoding

(Where xx_YY and encoding are replaced by you.) After that, start Fonty again.

If you want to help translate, please drop us a ticket on: https://savannah.nongnu.org/bugs/?group=fontypython

[Top](#top)

<center><img src="fontypythonmodules/help/common/break.png" border="0"></center>

<a name="bugs"></a>
Bugs
===
Fatal crashes and Dangerous Fonts.
--
Some fonts stick in Fonty's throat and crash her. If you wait a moment, a window should appear and tell you which font is to blame. You should move that font entirely away from where it is. Start Fonty again to resume. 

If you are stuck, go into your "fontypython" folder and open the file named "lastFontBeforeSegfault", that will be the culprit!

To find your fontypython directory, look in your home folder for either:

* .fontypython or
* .local/share/fontypython

You can also ask fonty for the path. On the command-line, run:
    
        fontypython -d

Checking Fonts
--
If Fonty will not start, you have a really bad font somewhere. On the command-line, use the -c flag to check all fonts (recursively) on the given path:

        fontypython -c /some/folder

Any fonts that are likely to kill Fonty will be recorded in a file named "segfonts" (look in your fontypython directory). After you do this, Fonty should work again. 

When Fonty starts, she checks your Pog files. If there are any Pogs that cannot be read for whatever reason, then they are renamed to ".badpog". You should go in there and do some sleuthing.

If you are stuck, post a report on https://savannah.nongnu.org/bugs/?group=fontypython. Please run Fonty from the command line so that you can copy any error displayed.

[Top](#top)

<center><img src="fontypythonmodules/help/common/break.png" border="0"></center>

<a name="lic"></a>
Licence
===
<pre>
Fonty Python is Copyright (C) 2006, 2017 Donn.C.Ingle.<br>

This file is part of Fonty Python.<br>
Fonty Python is free software: you can redistribute it and/or modify<br>
it under the terms of the GNU General Public License as published by<br>
the Free Software Foundation, either version 3 of the License, or<br>
(at your option) any later version.<br>

Fonty Python is distributed in the hope that it will be useful,<br>
but WITHOUT ANY WARRANTY; without even the implied warranty of<br>
MERCHANTABIliTY or FITNESS FOR A PARTICULAR PURPOSE. See the<br>
GNU General Public License for more details.<br>

You should have received a copy of the GNU General Public License<br>
along with Fonty Python. If not, see http://www.gnu.org/licenses/ <br>
</pre>
[Top](#top)
