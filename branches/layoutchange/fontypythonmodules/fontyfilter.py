import fpsys # Global objects
import re

"""
June 2009
Created this file with the intention of more complex searching using the 
FontTools module. This has not come to fruition, but I will keep this
module just in-case.
"""
def doFilter( filter_string ):
	print "filter:", filter_string
	##filter_string is a unicode object

	## STEP 1 : get the current view object (pog or folder)
	filteredList = fpsys.state.viewobject
	
	## if filter is not empty	
	if filter_string is not "":
		## Okay, we have some kind of filter.
		## This idea was suggested by user Chris Mohler.

		filteredList = []
		
		## We allow regex in the string. Is this wise?
		test = re.compile(filter_string, re.IGNORECASE)

		#L=set([set(i.style[0].split(u" ")) for i in fpsys.state.viewobject])
		#print L
		import pdb; pdb.set_trace()
		## Go through each font item and match 
		## the regex against certain fields.
		## EXTEND THIS TO PANOSE AND other fontTools criteria.
		for fi in fpsys.state.viewobject:
			#print fi.name, fi.family, fi.style
			## July 2016
			## =========
			## There was a None slipping in via fi.style!
			## Fixed this up-stream in fontcontrol.py
			##  print fi.name, fi.family, fi.style

			## Make sure we don't try fetch info from a bad font.
			if not fi.badfont:
				if test.search( fi.name + fi.family[0] + fi.style[0] ):
					filteredList.append( fi )
			else:
				if test.search( fi.name ):
					filteredList.append( fi )

	## We return the filtered-list
	return filteredList
