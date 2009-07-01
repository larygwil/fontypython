pwd=`pwd`
POFILES=${pwd}/fontypythonmodules/pofiles/
LOCALE=${pwd}/fontypythonmodules/locale/

prep : fp_all.pot
	echo Done
	
fp_all.pot:
	xgettext -o fp_all.pot -L Python fp -L Python fontypython fontypythonmodules/*.py
	mv fp_all.pot ${POFILES}

	msgmerge ${POFILES}fr_all.merged.po ${POFILES}fp_all.pot -o ${POFILES}fr_all.merged.pot
	msgmerge ${POFILES}it_all.merged.po ${POFILES}fp_all.pot -o ${POFILES}it_all.merged.pot
	msgmerge ${POFILES}de_all.merged.po ${POFILES}fp_all.pot -o ${POFILES}de_all.merged.pot
	
	rm ${POFILES}fr_all.merged.po
	rm ${POFILES}it_all.merged.po
	rm ${POFILES}de_all.merged.po

	echo Now edit the new.pot files and then run make renamepot
	
renamepot :
	mv ${POFILES}fr_all.merged.pot ${POFILES}fr_all.merged.po
	mv ${POFILES}it_all.merged.pot ${POFILES}it_all.merged.po
	mv ${POFILES}de_all.merged.pot ${POFILES}de_all.merged.po
	
	echo Now poedit the po files and make mo files. Then run make mos
	
mos :
	msgfmt ${POFILES}fr_all.merged.po -o ${LOCALE}fr/LC_MESSAGES/all.mo
	msgfmt ${POFILES}it_all.merged.po -o ${LOCALE}it/LC_MESSAGES/all.mo
	msgfmt ${POFILES}de_all.merged.po -o ${LOCALE}de/LC_MESSAGES/all.mo
	
	echo mo files have been moved.
	
