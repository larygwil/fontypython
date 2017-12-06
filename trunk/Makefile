pwd=`pwd`
POFILES=${pwd}/fontypythonmodules/pofiles/
LOCALE=${pwd}/fontypythonmodules/locale/

prep : fp_all.pot
	echo Done
	
fp_all.pot:
	xgettext -o fp_all.pot -L Python fontypython fontypythonmodules/*.py
	mv fp_all.pot ${POFILES}

	# Take the PO files that are there and merge them (afresh) with the new fp_all POT file
	# output new POT files.
	msgmerge ${POFILES}fr_all.merged.po ${POFILES}fp_all.pot -o ${POFILES}fr_all.merged.pot
	msgmerge ${POFILES}it_all.merged.po ${POFILES}fp_all.pot -o ${POFILES}it_all.merged.pot
	msgmerge ${POFILES}de_all.merged.po ${POFILES}fp_all.pot -o ${POFILES}de_all.merged.pot
	
	# Remove the old PO files. We are left with POT files now that will have some
	# translations, but also be missing any new stuff from the app.
	rm ${POFILES}fr_all.merged.po
	rm ${POFILES}it_all.merged.po
	rm ${POFILES}de_all.merged.po

	# Now run make renamepot
	
renamepot :
	# BEFORE adding the new translations -- change the POT files to PO files
	mv ${POFILES}fr_all.merged.pot ${POFILES}fr_all.merged.po
	mv ${POFILES}it_all.merged.pot ${POFILES}it_all.merged.po
	mv ${POFILES}de_all.merged.pot ${POFILES}de_all.merged.po
	
	# Now poedit the PO files. Then run make mos
	
mos :
	# Convert the PO files to MO files.
	msgfmt ${POFILES}fr_all.merged.po -o ${LOCALE}fr/LC_MESSAGES/all.mo
	msgfmt ${POFILES}it_all.merged.po -o ${LOCALE}it/LC_MESSAGES/all.mo
	msgfmt ${POFILES}de_all.merged.po -o ${LOCALE}de/LC_MESSAGES/all.mo
	
	echo mo files have been moved.
	
