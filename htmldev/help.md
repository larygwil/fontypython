<a name="top"></a>
<font size=40 color="{logotype}"><i><b>Fonty Python</b></i></font>

*Fonty is a font viewer and manager for Gnu/Linux. Use it to view, gather and manage fonts. You can install and uninstall fonts to your user fonts folder for temporary use in other apps.*

[The Idea](#idea) | [User Font Paths](#info) | [The Layout](#layout) | [Menus](#menus) | [Hushing](#hushing) | [Shortcuts](#shortcuts) | [Tips](#tips) | [Localization](#l10n) | [Bugs](#bugs) | [Licence](#lic)

<a name="idea"></a>
Ye Olde Basic Idea
=======
You visually gather fonts into a "Pog", and then install it. All its fonts will be available to other apps. When you finish your work, uninstall the Pog.

I pinched the word "Pog" from "ty**pog**raphy". It means "collection", "group", "bunch", "box", "case", "stack" or "pile" &mdash; you get the picture.

Your fonts never move from where they live, neither are copies made; *only* links to the original files are used to install the fonts into your user fonts directory.

For example, you might have a Pog called "Logos" into which you place all the fonts needed to design a logo. When you want to work, install the "Logos" Pog and start your design app. All those fonts will now appear in Inkscape, the Gimp, etc. 
When you're done, uninstall "Logos" and all those fonts go away. (The links to the original files are removed, **not** the actual font files!)

Fonty is also great for just looking at fonts, wherever they are on your computer, without having to install them first. She also has a command line, allowing very quick use. You can install/uninstall Pogs without having to start the entire gui, which is neat.

If you have any problems, please open a ticket: {TICKET_URL}

[Top](#top)
{SEP}

<a name="info"></a>
User Fonts Paths
===
###Your fontypython directory
Where all your Pogs are kept. 

{FP_DIR}

###Your user fonts directory
{UF_DIR}

If there's a dot in front (like .local) that means the directory is "hidden". You might not see it in your file manager.

Whatever it's called and wherever it is, any fonts listed in here are "installed". Fonty's job is to shuttle fonts in and out of here so you don't have to.

If your fonts are not working, it may be that you don't have a user fonts directory. You'll have to search around and figure it out.

###Your fontconfig directory is
{FC_DIR}

[Top](#top)
{SEP}

<a name="layout"></a>
Layout
=====
On the left are the Source (top) and Target (bottom) controls. On the right is the Font View. 

<img src="fontypythonmodules/things/icon_source.png">&nbsp; The Sources
--
Font *Sources* are directories or Pogs. There are tabs for you to choose. 

(Beware the **include sub-folders** option in Settings. When checked, Fonty will look for fonts in **all** the sub-directories within your chosen Source directory. If there are lots of fonts in there, she might hang. Use this with caution.)

<img src="fontypythonmodules/things/icon_target.png">&nbsp; The Targets
--
These Pogs are the *Targets*: you put fonts into them.

* <img src="fontypythonmodules/things/pog16x16.png">&nbsp; Shows a Pog (which is not installed).
  Such Pogs can be Targets.
* <img src="fontypythonmodules/things/pog16x16.installed.png">&nbsp; Shows an installed Pog.
  You can't use these as targets. (Uninstall them first.)
* <img src="fontypythonmodules/things/pog16x16.target.png">&nbsp; Shows current target Pog.

For Targets, you can select many Pogs at once by holding control (Ctrl) as you select them; this is for installing/uninstalling/etc. many Pogs at once.

###Pog management buttons
The managements buttons all work with the selected **target** Pog(s). It's a little counter-intuitive sometimes. Sorry. It was done because you can select multiple targets. (But not multiple sources.)

* **Clear selection:** Will unselect whatever Pogs you selected.
* **Install:** All the Pogs selected will be installed. I.e. The fonts in them will be available to the system.
* **Uninstall:** All those selected will be uninstalled.
* **New Pog:** This will ask you for a name and make a new Pog.
* **Delete:** All selected Pogs will be deleted. It will ask you if you are sure.
* **Zip:** All selected Pogs will have their fonts zipped into individual zip files in a directory you choose.

<img src="fontypythonmodules/things/icon_viewing.png">&nbsp; The Font View
--
Fonts in your Source will be visible in the Font View. You can click on the fonts you want to select. At the bottom of the Font View are controls to filter, page and manage the fonts you are looking at.

The Font View will also attempt to display in columns, so you can see many fonts at once. The columns vary by point size and the width of your window. You can control the number of columns in the Settings.

###The Fonts themselves
Each font appears with some appropriate information. Here are the basics:

* Change the **Point size** by **Ctrl + scrolling** the mouse wheel up or down.

* <img src="fontypythonmodules/things/button_charmap_over.png">&nbsp;**Character Map Button:** If you have a character viewing app installed, this button will open it. (You can choose which character map viewer to use in the Settings. The choices are gucharmap or kfontview &mdash; but you must install one first.)

* **Selecting fonts:** Clicking anywhere on a font will select it; if it's sensible. For example, if you have only a Source selected, and no Target, then there's no point in selecting fonts.
  * **A tick<img src="fontypythonmodules/things/tick.png" width=18 height=18> :** means the font can be placed into your chosen Target Pog.
  * **A cross <img src="fontypythonmodules/things/cross.png" width=18 height=18> :** means the font will be removed from the Source Pog (The one you are viewing at the moment).

* **Font Info:** Under each font you will find the family and style and filename. 
  When you use the filter to search, this is the text that is searched.

* **Greyed-out:** Fonts that are already in the Pog (i.e. selected as a target) are disabled.

* <img src="fontypythonmodules/things/font_cannot_draw.png">&nbsp;**Bad fonts:** An error may appear instead of the expected font glyphs. Such fonts cannot be drawn.
  You can select, enpog, and install them. Most of the time, these fonts will still work in your 
  design apps, like Inkscape.
  (See [Bugs](#bugs) for more information about font errors.)

###Font controls
* **Filter:** 
  * **i,r,b** are Italic, Regular and Bold. 
  * <img src="fontypythonmodules/things/clear.png">&nbsp; Clears any filter.
  * The text box is for custom searching. Type something and hit enter. 
* **Pager:** On the far right is the pager. Use it to step through the fonts as you like.
* **Left/Right:** Arrow buttons for paging one forward or back. 

[Top](#top)
{SEP}

<a name="hushing"></a>
<img src="fontypythonmodules/things/icon_hush.png">&nbsp;Hushing Fonts
===
On Linux there are often too many fonts installed; it's hard to choose among them. To work with *only* the fonts that you install via Fonty, hit Ctrl+H to **hush**. Your apps will now list **only** your desired fonts. (Until you un-hush.)

Simply install Pogs via Fonty as normal and start a hush. In your other apps, you should see the difference. (For e.g. go into Inkscape and open the "Text & Font" dialogue.)

####The "Hush Pog" and a mild Warning
As you can imagine, a hush could reject many crucial fonts...

In order to make sure that your system has a few it can use, Fonty requires you to choose a Pog that is installed when hushing. Call it a "Hush Pog". 

Create a Pog of your own and put some typical system fonts into it. Good choices are: **DejaVu, Sans, Serif, Mono, Free-, Liberation-, Ubuntu-** and so forth. This depends on your locale and preferences, therefore we leave it to you.

(These kinds of fonts are usually found in "/usr/share/fonts".)

Fonty will ask for a Pog when you start a hush; select the one you prepared.

It's not serious, but **you have been warned.**

###Details
This all requires a working fontconfig setup, which most modern Linux distros have. Fonty looks for the directory:

	{HOME}/.config/fontconfig/conf.d

If it's not found, you can't hush fonts. (If you have more information, please open a ticket.)

Fonty writes a config file which instructs fontconfig to:

* **Reject** all files that start with "/usr/share/fonts"
* **Allow** all fonts installed in the user fonts directory. 

The effect is usually instantaneous, but you may need to restart certain apps for them to notice. (If you find there are still fonts appearing that you do not want to see, please open a ticket.)



###Reversing a hush: the Un-hush
To switch all the system fonts on again, go into the hush screen where you can "Un-hush". 

Your "Hush Pog" is not uninstalled; do this manually,

If there's a problem, you can also manually delete the config file. Look for it on this path, and delete it:
	
	{FC_PAF}


[Top](#top)
{SEP}

<a name="menus"></a>
Menus
====
* **Tools menu**
  * <img src="fontypythonmodules/things/icon_settings.png">&nbsp;**Settings:** Access the settings for 
    the font view. Shortcuts: Ctrl+S or middle-click on the font view.
  * **Purge Pog:** The Pog you are currently viewing may contain fonts that are not there anymore.
    Use purge to remove them.<br>
     *Explanation*: A Pog contains a list of paths. If a font is somehow moved on your hard drive, 
     then the path in the Pog will be old. Purging will remove these ghost fonts.
  * <img src="fontypythonmodules/things/icon_hush.png">&nbsp;**Hush fonts**: See the [section on hushing](#hushing). Shortcut: Ctrl+H
  * **Exit:** Guess. :-)
* **Selection menu**
  * **Select ALL the source fonts:** While only a few fonts are shown in a page at a time, there may 
    be thousands in the selected source. This will select **all** of them, in one go.
  * **Clear ENTIRE selection:** Will clear any selection.

[Top](#top)

{SEP}

<a name="shortcuts"></a>
Shortcut keys
====
If shortcut keys don't work, click in the filter text box. This seems to kick them back to life. Don't ask me what's going on....

* **Esc** The Escape key will close any panels that may be open. Used again, it will close the app. 
  Most of the time.
* **Ctrl + LeftArrow/Ctrl + RightArrow** will step through fonts like the Next and Previous buttons do.
* **Middle-click (the wheel-button) or Ctrl + S** in the font view will open the Settings screen.
* **Ctrl + Scroll mouse wheel up/down** will increase/decrease the size of your font previews quickly.
* **Ctrl + H** will open the hush panel.


[Top](#top)

{SEP}

<a name="tips"></a>
Tips
===

* Try to use Fonty from the command-line (from a console). It's easy, simply type:
   fontypython -h
* Pog files are merely text files. They are very, very simple and this was intentional. Here are some things you can do with them:
   * Open and edit them in any text editor.
   * Append fonts to the end of them, just include the entire path (ends with the font file name).
   * *Note for Type1 fonts: Only include the PFA/B file types, not the various metric files that 
     follow them.*
   * If your paths change (say you renamed your folders, or re-installed your O/S) then you can use 
     search/replace to update all the paths to all the fonts in your Pogs. You could do this from 
     the command-line using GNU tools, but any text editor will help you here too.
   * You can backup your Pogs by simply copying them to another folder.
   * One last trick, for those proficient with the Gnu tools, you can do things like this:

        find /home/you/somepath/TTFS/F -iname "Fu*" >> Futura.Pog


[Top](#top)

{SEP}

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

If you want to help translate, please drop us a ticket on: {TICKET_URL}

[Top](#top)

{SEP}

<a name="bugs"></a>
Bugs
===
<img src="fontypythonmodules/things/font_segfault.png">&nbsp;Fatal crashes and Dangerous Fonts.
--
Some fonts stick in Fonty's throat and crash her. If you wait a moment, a window should appear and tell you which font is to blame. You should move that font entirely away from where it is. Start Fonty again to resume. 

If you are stuck, go into your "fontypython" folder and open the file named "lastFontBeforeSegfault", that will be the culprit!

To find your fontypython directory, see the [Info](#info) section in this help. You can also ask Fonty for the path. On the command-line, run:
    
        fontypython -d

Checking Fonts
--
If Fonty will not start, you have a really bad font somewhere. On the command-line, use the -c flag to check all fonts (recursively) on the given path:

        fontypython -c /some/folder

Any fonts that are likely to kill Fonty will be recorded in a file named "segfonts" (look in your fontypython directory). After you do this, Fonty should work again. 

When Fonty starts, she checks your Pog files. If there are any Pogs that cannot be read for whatever reason, then they are renamed to ".badpog". You should go in there and do some sleuthing.

If you are stuck, post a report on https://savannah.nongnu.org/bugs/?group=fontypython. Please run Fonty from the command line so that you can copy any error displayed.

[Top](#top)

{SEP}

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
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the<br>
GNU General Public License for more details.<br>

You should have received a copy of the GNU General Public License<br>
along with Fonty Python. If not, see http://www.gnu.org/licenses/ <br>
</pre>
[Top](#top)
