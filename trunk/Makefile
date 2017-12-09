pwd=`pwd`
POFILES=${pwd}/fontypythonmodules/pofiles/
LOCALE=${pwd}/fontypythonmodules/locale/
VERS=$(shell python2 -c "import fontypythonmodules.fpversion as fpv; print fpv.version")
CH="Copyright (C) 2006,2007,2008,$(shell date +%Y) Donn.C.Ingle"

prep : broken
	# i am fixing this mess. to be continued...
	echo Done
	
init_fp_all.pot:
	# Do this only once. i.e. Never use this. To continue development, use the update target.
	xgettext --package-name="fontypython" --package-version="${VERS}" --copyright-holder=${CH} --msgid-bugs-address="donn.ingle@gmail.com" -p po -o fp_all.pot -L Python fontypython fontypythonmodules/*.py
	

update:
	# Take the PO files that are there and merge them (afresh) with the new fp_all POT file
	# output new POT files.
	msgmerge ${POFILES}fr_all.merged.po po/fp_all.pot -o ${POFILES}fr_all.merged.pot
	msgmerge ${POFILES}it_all.merged.po po/fp_all.pot -o ${POFILES}it_all.merged.pot
	msgmerge ${POFILES}de_all.merged.po po/fp_all.pot -o ${POFILES}de_all.merged.pot
	
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
	
