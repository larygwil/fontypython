import fpsys # Global objects
import re

def doFilter( filter_string ):
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

		## Go through each font item and match 
		## the regex against certain fields.
		## EXTEND THIS TO PANOSE AND other fontTools criteria.
		for fi in fpsys.state.viewobject:
			## Make sure we don't try fetch info from a bad font.
			if not fi.badfont:
				if test.search( fi.name + fi.family[0] + fi.style[0] ):
					filteredList.append( fi )
			else:
				if test.search( fi.name ):
					filteredList.append( fi )

	## We return the filtered-list
	return filteredList
