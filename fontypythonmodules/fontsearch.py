"""
Working on this - May 2009
Michael Hoeft's idea for PANOSE and company 
His implementation was messy and unfinished. But the idea is nice.
"""

import i18n
from fontTools import ttLib, t1Lib
from fontcontrol import TruetypeItem, TruetypeCollectionItem, OpentypeItem, Type1Item
from os import listdir
from os.path import basename


categorys = [_('Name Records'), _('PANOSE Classification'), _('Appearance')]

nameIDs = [_('Copyright'),_('Font Family'),_('Font Subfamily'),_('Font Identifer'),_('Full Name'),
			_('Version'),_('Postscript Name'),_('Trademark'),_('Manufacture Name'),_('Designer'),
			_('Description'),_('URL Vendor'),_('URL Designer'),_('License'),_('License Info URL'),
			_('Unknown'),_('Preferred Family'),_('Preferred Subfamily'),_('Compatible Full (Mac)'),
			_('Sample text'),_('PostScript CID findfont name'),_('WWS Family Name'),_('WWS Subfamily Name'),
			 _('Number of glyphs'),_('PaintType')]

translateIDs = {'Notice': 0, 'FullName': 4, 'FamilyName': 1, 'version': 5, 'Weight': 2, 'FontName': 6,
				'UniqueID': 3}

panoseLTextIDs = ['PANOSE Number','FamilyType','SerifStyle','Weight','Proportion','Contrast',
					'StrokeVariation','ArmStyle','LetterForm','Midline','XHeight']

panoseLTextDict={ _('FamilyType'): [_('Any'),_('No Fit'),_('Latin Text'),_('Latin Hand Written'),_('Latin Decorative'),_('Latin Symbol')],
				_('SerifStyle'): [_('Any'),_('No Fit'),_('Cove'),_('Obtuse Cove'),_('Square Cove'),_('Obtuse Square Cove'),_('Square'),
								  _('Thin'),_('Oval'),_('Exaggerated'),_('Triangle'),_('Normal Sans'),_('Obtuse Sans'),
								  _('Perpendicular Sans'),_('Flared'),_('Rounded')],
				_('Weight'):	 [_('Any'),_('No Fit'),_('Very Light'),_('Light'),_('Thin'),_('Book'),_('Medium'),_('Demi'),_('Bold'),
								  _('Heavy'),_('Black'),_('Extra Black')],
				_('Proportion'): [_('Any'),_('No Fit'),_('Old Style'),_('Modern'),_('Even Width'),_('Extended'),_('Condensed'),
								  _('Very Extended'),_('Very Condensed'),_('Monospaced')],
				_('Contrast'):   [_('Any'),_('No Fit'),_('None'),_('Very Low'),_('Low'),_('Medium Low'),_('Medium'),_('Medium High'),
								  _('High'),_('Very High')],
				_('StrokeVariation'):[_('Any'),_('No Fit'),_('No Variation'),_('Gradual/Diagonal'),_('Gradual/Transitional'),
									_('Gradual/Vertical'),_('Gradual/Horizontal'),_('Rapid/Vertical'),_('Rapid/Horizontal'),
									_('Instant/Vertical'),_('Instant/Horizontal')],
				_('ArmStyle'):   [_('Any'),_('No Fit'),_('Straight Arms/Horizontal'),_('Straight Arms/Wedge'),_('Straight Arms/Vertical'),
								  _('Straight Arms/Single Serif'),_('Straight Arms/Double Serif'),_('Non-Straight/Horizontal'),
								  _('Non-Straight/Wedge'),_('Non-Straight/Vertical'),_('Non-Straight/Single Serif'),
								  _('Non-Straight/Double Serif')],
				_('LetterForm'): [_('Any'),_('No Fit'),_('Normal/Contact'),_('Normal/Weighted'),_('Normal/Boxed'),_('Normal/Flattened'),
								  _('Normal/Rounded'),_('Normal/Off Center'),_('Normal/Square'),_('Oblique/Contact'),_('Oblique/Weighted'),
								  _('Oblique/Boxed'),_('Oblique/Flattened'),_('Oblique/Rounded'),_('Oblique/Off Center'),
								  _('Oblique/Square')],
				_('Midline'):	[_('Any'),_('No Fit'),_('Standard/Trimmed'),_('Standard/Pointed'),_('Standard/Serifed'),_('High/Trimmed'),
								  _('High/Pointed'),_('High/Serifed'),_('Constant/Trimmed'),_('Constant/Pointed'),_('Constant/Serifed'),
								  _('Low/Trimmed'),_('Low/Pointed'),_('Low/Serifed')],
				_('XHeight'):	[_('Any'),_('No Fit'),_('Constant/Small'),_('Constant/Standard'),_('Constant/Large'),_('Ducking/Small'),
								  _('Ducking/Standard'),_('Ducking/Large')]}

appIDs = [_('Shape')]

appShapeDict = {0:_('quite simple'), 1:_('serif/rounded'), 2:_('decorated'), 3:_('fanciful')}

class FontRecords(dict):
	"""Holds all informations extracted from the font in a dict."""
	def __init__(self, font):
		print str(font)
		for c in categorys:
			self[c] = {}

		if isinstance(font, TruetypeItem):
			self.__scanTTF(font)

		elif isinstance(font, OpentypeItem):
			self.__scanOTF(font)
			
		elif isinstance(font, Type1Item):
			self.__scanT1(font)
	
	def __str__(self):
		string = ''
		for category in categorys:
			if not self[category]:
				continue
			string += str(category) + '\n'
			for key in self[category].keys():
				string += '\t'
				string += str(key) + ' = ' + str(self[category][key]) + '\n'
			string += '\n'
		string += '\n'
		return string

	def __scanOTFTTF(self, object_of_study):
		for record in object_of_study['name'].names:
			if record.platformID == 1:
				try:
					self['Name Records'][nameIDs[record.nameID]] = record.string
				except:
					pass
		try:
			self['Name Records'][nameIDs[23]] = str(len(object_of_study.getGlyphNames()))
		except:
			pass
		if object_of_study.has_key('OS/2'):
			number = ''
			for key in panoseLTextIDs:
				try:
					number += str(eval("object_of_study['OS/2'].panose.%s" %('b' + key))) + '/'
				except:
					pass
			
			number = number.strip('/')
			self['PANOSE Classification'][panoseLTextIDs[0]] = number
			number_list = [int(a) for a in number.split('/')]
			iterIDs = iter(panoseLTextIDs[1:])
			number_list = [(iterIDs.next(), a) for a in number_list]

			if number_list[0][1] in (0,1,2):
				for ID, number in number_list:
					self['PANOSE Classification'][ID] = panoseLTextDict[ID][number]

	def __getShape(self, numnodes):
		if numnodes <= 6:
			index = 0
		elif numnodes <= 14:
			index = 1
		elif numnodes <= 55:
			index = 2
		elif numnodes > 55:
			index = 3
		
		return appShapeDict[index]

	def __scanTTF(self, font):
		try:
			object_of_study = ttLib.TTFont(str(font))
		except:
			return
		self.__scanOTFTTF(object_of_study)
		GlyphList = object_of_study['glyf']
		Glyph = GlyphList['I']
		numnodes = len(Glyph.getCoordinates(GlyphList)[0])
		self['Appearance'][appIDs[0]] = self.__getShape(numnodes)


	def __scanOTF(self, font):
		try:
			object_of_study = ttLib.TTFont(str(font))
		except:
			return
		self.__scanOTFTTF(object_of_study)

	def __scanT1(self, font):
		try:
			object_of_study = t1Lib.T1Font(str(font))
		except:
			print "ERROR"
			return
		object_of_study.parse()
		self['Name Records'][nameIDs[translateIDs['FontName']]] = object_of_study.font['FontName']
		self['Name Records'][nameIDs[translateIDs['UniqueID']]] = object_of_study.font['UniqueID']
		for k in object_of_study.font['FontInfo'].keys():
			if translateIDs.has_key(k):
				self['Name Records'][nameIDs[translateIDs[k]]] = object_of_study.font['FontInfo'][k]
		if object_of_study.font['PaintType'] == 0:
			self['Name Records'][nameIDs[24]] = 'fill'
		elif object_of_study.font['PaintType'] == 2:
			self['Name Records'][nameIDs[24]] = 'outline'
		self['Name Records'][nameIDs[23]] = str(len(object_of_study.font['CharStrings']))

def getInfo(font):
	infodict = FontRecords(font)
	return infodict



if __name__=="__main__":
	print 'TTF'
	font = TruetypeItem("/home/donn/06.FontStore/TTFS/numbered/18th Century.ttf")
	print getInfo(font)
	print
	print 'TYPE1'
	font = Type1Item("/home/donn/Projects/pythoning/fontyPython/goodandbadfonts/a010013l.pfb")
	print getInfo(font)
	print
	print 'OTF'
	font = OpentypeItem("/usr/share/texmf-texlive/fonts/opentype/public/iwona/Iwona-Bold.otf")
	print getInfo(font)
	
