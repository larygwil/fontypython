##	Fonty Python Copyright (C) 2006, 2007, 2008, 2009 Donn.C.Ingle
##	Contact: donn.ingle@gmail.com - I hope this email lasts.
##
##	This file is part of Fonty Python.
##	Fonty Python is free software: you can redistribute it and/or modify
##	it under the terms of the GNU General Public License as published by
##	the Free Software Foundation, either version 3 of the License, or
##	(at your option) any later version.
##
##	Fonty Python is distributed in the hope that it will be useful,
##	but WITHOUT ANY WARRANTY; without even the implied warranty of
##	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##	GNU General Public License for more details.
##
##	You should have received a copy of the GNU General Public License
##	along with Fonty Python.  If not, see <http://www.gnu.org/licenses/>.

## Message topics : they identify the functions to run from CPubsub
update_font_view = 10
show_error = 20
show_error_and_abort = 30
show_message = 40
reset_to_page_one = 50
add_pog_item_to_source = 60
remove_pog_item_from_source = 70
print_to_status_bar = 80
install_pog = 90
uninstall_pog = 100
main_button_click = 110
toggle_main_button = 120
target_pog_has_been_selected = 130
source_pog_has_been_selected = 135
change_pog_icon = 140
toggle_targetpog_buttons = 150
clear_targetpog_selection = 160
select_no_view_pog = 170

get_font_view_width = 180
menu_settings = 190

toggle_selection_menu_item = 200
toggle_purge_menu_item = 210

##get_sashes_position = 220

left_or_right_key_pressed = 1000

reset_top_left_adjustments = 2000

## A hack to allow values to return from published topics
globRetVal = {}

## The thing that is held in the dictionary inside CListener
class CTopic:
	def __init__(self, function, topic, key):
		self.function = function
		self.topic = topic
		self.key = key
		
## When you have a function you want to make available, sub() it.
## When you want something to happen somewhere else, then pub () it.
class CPubsub:
	def __init__(self):
		self.__ears = {}
		self.__key = 0
	def __del__(self):
		del self.__ears
		
	## Makes a topic object and stores it internally.
	## Keeps a constantly increasing internal key.
	## I used a dictionary, but it prob should just be a list.
	## Ah well.
	def sub(self, topic, function): #SUBSCRIBE (was newEar)
		t = CTopic(function, topic, self.__key)
		self.__ears [ self.__key ] = t
		self.__key += 1
		
	## Go thru all the topics, find any that match and call their functions, passing any args too.
	def pub(self, topic, *args): #PUBLISH (was shout)
		#global globRetVal
		#m = CMessage(topic, messagelist)
		#print "pub called"
		ret = None
		for key, top in self.__ears.iteritems():
			
			if top.topic == topic:
				function = top.function
				#print "pub to run:", topic 
				if args:
					function(args) #Pass the args only.
				else:
					function() 
				#if ret:
					#print "ret causes break."
					#break;
		#print "pub ends."
		#if ret: return ret

## Sample of the use of this stuff:
if __name__ == "__main__":

	def dox(*args):
		print "i run", args
	def detox(*args):
		print "yup de too", args
		
	top_dox = 1
	
	p = CPubsub()
	#we subscribe two handlers to one topic
	p.sub(top_dox, dox)
	p.sub(top_dox, detox)
	
	#we  pretend we are in another class/widget and we want to send a message:
	p.pub(top_dox, 10,20,"AX","BX")
