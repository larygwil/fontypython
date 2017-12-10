pwd=`pwd`
POFILES=${pwd}/fontypythonmodules/pofiles/
LOCALE=${pwd}/fontypythonmodules/locale/
VERS=$(shell python2 -c "import fontypythonmodules.fpversion as fpv; print fpv.version")
CH="Copyright (C) 2006,2007,2008,$(shell date +%Y) Donn.C.Ingle"
fpref=${POFILE}/fp_ref.pot

prep : fp_all.pot
	
refpot :
	# Making the ref.pot file. Fresh from the source.
	xgettext --package-name="fontypython" --package-version="${VERS}" --copyright-holder=${CH} --msgid-bugs-address="donn.ingle@gmail.com" -p ${POFILES} -o fp_ref.pot -L Python fontypython fontypythonmodules/*.py

update :
	# Merges the translation files (.po) with the latest .pot made from the source code.
	# If people send me .po files, I should check they are named properly and then
	# run this update recipe.
	
	# Making copies of the trans files; in case...
	cp ${POFILES}/fr_all.merged.po ${POFILES}/fr_all.merged.po.old
	cp ${POFILES}/it_all.merged.po ${POFILES}/it_all.merged.po.old
	cp ${POFILES}/de_all.merged.po ${POFILES}/de_all.merged.po.old

	# Merging the current translation files that exist ("def.po", per the gnu manual)
	# with the fp_ref.pot file. Output OVER the same def.po files.
	msgmerge ${POFILES}fr_all.merged.po ${fpref} -o ${POFILES}fr_all.merged.po
	msgmerge ${POFILES}it_all.merged.po ${fpref} -o ${POFILES}it_all.merged.po
	msgmerge ${POFILES}de_all.merged.po ${fpref} -o ${POFILES}de_all.merged.po
	
	# Now poedit the PO files. When ready, run make mos
	
mos :
	# Converting the PO files to MO files.
	msgfmt ${POFILES}fr_all.merged.po -o ${LOCALE}fr/LC_MESSAGES/all.mo
	msgfmt ${POFILES}it_all.merged.po -o ${LOCALE}it/LC_MESSAGES/all.mo
	msgfmt ${POFILES}de_all.merged.po -o ${LOCALE}de/LC_MESSAGES/all.mo
	
	# mo files have been moved.
	
