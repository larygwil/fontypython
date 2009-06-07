try:
	import pyparsing as PP
except:
	print "You need to install pyparsing: apt-get install python-pyparsing"
	raise SystemExit

## Define the "Grammar" for the chopping-up of search strings.
simple = PP.Word(PP.alphas)
quoted = PP.dblQuotedString.setParseAction(PP.removeQuotes)

# Paul McGuire's suggestion: Thanks Paul!
single = simple | quoted
COLON = PP.Suppress(':')
fieldValue = single + ~PP.FollowedBy(COLON)
field = single + COLON + PP.Group(PP.OneOrMore(fieldValue))
phrase = fieldValue
phrases = PP.ZeroOrMore(phrase)

#To add the dict-style access to the fields, add some results names, and use
#the Dict class to auto-define results names for each field name.
query = PP.Optional(phrases)("phrases") + PP.Dict(PP.ZeroOrMore(PP.Group(field)))("fields")

tests=[
		u"Bold mono aField: aValue", 
		u'aField: "guten tag" bloop AnotherField: one two', 
		u"aField: Someval AnotherField: two" 
]

## Run those tests through the parseString and then inspect the tokens
for test in tests:
	print
	print test
	try:
		tokens=query.parseString(test)
		## Let's see what it found!
		for t in tokens:
			if type(t) is PP.ParseResults:
				print t.asDict()
			else:
				print t
	except:
		print "A BUG"


