pwd=`pwd`
P=${pwd}/fontypythonmodules/pofiles/
M=${pwd}/fontypythonmodules/locale/

prep : fp_all.pot
	echo Done
	
fp_all.pot:
	xgettext -o fp_all.pot -L Python fp -L Python fontypython fontypythonmodules/*.py
	mv fp_all.pot ${P}

	msgmerge ${P}fr_all.merged.po ${P}fp_all.pot -o ${P}fr_all.merged.pot
	msgmerge ${P}it_all.merged.po ${P}fp_all.pot -o ${P}it_all.merged.pot
	msgmerge ${P}de_all.merged.po ${P}fp_all.pot -o ${P}de_all.merged.pot
	
	rm ${P}fr_all.merged.po
	rm ${P}it_all.merged.po
	rm ${P}de_all.merged.po

	echo Now edit the new.pot files and then run make renamepot
	
renamepot :
	mv ${P}fr_all.merged.pot ${P}fr_all.merged.po
	mv ${P}it_all.merged.pot ${P}it_all.merged.po
	mv ${P}de_all.merged.pot ${P}de_all.merged.po
	
	echo Now poedit the po files and make mo files. Then run make mos
	
mos :
	msgfmt ${P}fr_all.merged.po -o ${M}fr/LC_MESSAGES/all.mo
	msgfmt ${P}it_all.merged.po -o ${M}it/LC_MESSAGES/all.mo
	msgfmt ${P}de_all.merged.po -o ${M}de/LC_MESSAGES/all.mo
	
	echo mo files have been moved.
	
