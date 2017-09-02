	def CreateFitmaps(self, viewobject) :
		"""
		Creates fitmaps (which draws them) of each viewobject FontItem down the control.
		viewobject: is a sub-list of fitems to display - i.e. after the page number math.
			** See filterAndPageThenCallCreateFitmaps in gui_Middle.py
		"""

		## Ensure we destroy all old fitmaps -- and I mean it.
		for f in self.fitmaps:
			f.Destroy()  #Ah, nailed ya! You bastard! I fart in your general direction!

		## Yes, die. Die!
		del self.fitmaps
		self.fitmaps = []

		## If our viewobject has NO FONTS inside it (i.e. it's an EmptyView object)
		## then setup a fake FontItem so we can have a dud Fitmap to show.
		if len(viewobject) == 0:
			empty_fitem = fontcontrol.InfoFontItem()
			fm = Fitmap( self, empty_fitem )
			self.fitmaps.append(fm) # I MUST add it to the list so that it can get destroyed when this func runs again next round.
			self.mySizer.Add( fm )
		else:

			## Okay - let's make fonts!
			self.mySizer.Clear() # Wipe all items out of the sizer.
			self.Scroll(0,0) # Immediately scroll to the top. This fixed a big bug.

			w = []

			yld = fpsys.config.numinpage > 20
			for fitem in viewobject:
				## Create a Fitmap out of the FontItem we have at hand.
				fm = Fitmap( self, fitem )
				self.fitmaps.append( fm )
				w.append(fm.DoGetBestSize()[0])
				## July 2016: Add it to the amazing WrapSizer
				## wx.RIGHT specifies we want border on the right!
				#self.mySizer.Add( fm, 0, wx.ALIGN_LEFT|wx.ALIGN_BOTTOM|wx.RIGHT, border=10)

				## Added Oct 2009 to let app live on loooong lists.
				if yld: wx.Yield()

			mw = min(w)
			#print w
			#print mw

			for fm in self.fitmaps:
				## July 2016: Add it to the amazing WrapSizer
				## wx.RIGHT specifies we want border on the right!
				#if fm.GetBestSize()[0] > mw: fm.bitmap.Resize((mw,fm.GetBestSize()[1]),(0,0))
				if fm.GetBestSize()[0] > mw:
					#import pdb; pdb.set_trace()
					#fm.SetMaxSize( (mw,fm.GetBestSize()[1]) )
					#img = fm.bitmap.GetImage().Resize( (mw,fm.GetBestSize()[1]),(0,0) )
					img = fm.bitmap.ConvertToImage().Resize( (mw,fm.GetBestSize()[1]),(0,0) )
					fm.bitmap = img.ConvertToBitmap()
				self.mySizer.Add( fm, 0, wx.ALIGN_LEFT|wx.ALIGN_BOTTOM|wx.RIGHT, border=10)
				if yld: wx.Yield()

		#import pdb; pdb.set_trace()

		# Layout should be called after adding items.
		self.mySizer.Layout()
		self.mySizer.FitInside(self) # Iterative hacking leaves this one standing. self.Fit(), not so much.
