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

Left-top: The Sources
--
Font *Sources* are directories or Pogs. There are tabs for you to choose. 

Beware the **include sub-folders** check box. When checked, Fonty will look for fonts in **all** the sub-directories within your chosen Source directory. If there are lots of fonts in there, she might hang. Use this with caution.

Left-bottom: The Targets
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

Right: The Font View
--
Fonts in your Source will be visible in the Font View. You can click on the fonts you want to select. At the bottom of the Font View are some controls to help you filter, page and manage the fonts you are looking at.

The Font View will also attempt to display in columns, so you can see many fonts in one go. The columns vary by how big each font is and the width of your window. You can control the number of columns in the Settings.

Areas of interest within each font:

1. **Point size:** Ctrl + scrolling the mouse wheel (up/down).

2. **Character Map Button:** The little magnifying glass. If you have a character viewing app installed, 
   this button will show and when clicked will open it to let you view the full character-set of the font.
   You can choose which character map viewer to use in the Settings. The choices are gucharmap or kfontview.

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

The Controls under the Font View

1. **Filter:** 
  * "i,r,b" mean Italic, Regular and Bold. 
  * The "X" button will clear your current filter.
  * The text box is for custom searching. Type something and hit enter. 
2. **Pager:** On the far right is the pager. Use it to step through the fonts as you like.
3. **Left/Right:** Arrow buttons for paging one forward or back. 

[Top](#top)

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
   * **Exit:** Guess. :)
2. **Selection menu**
   * **Select ALL the source fonts:** While only a few fonts are shown in a page at a time, there may 
     be thousands in the selected source. This will select **all** of them, in one go.
   * **Clear ENTIRE selection:** Will clear any selection.


