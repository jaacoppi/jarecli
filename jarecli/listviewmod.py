# jarecli - jaacoppi's client for reddit
# A client for reddit using Python & PRAW
# MIT LICENSED. See LICENSE for details

# listviewmod.py contains all listview related code

from . import uimod
from . import readerviewmod

"""
Listview takes the items in listviewitems[] and displays them in the ui. There's an ability to browse through items with keys up/down, pageup/down.
Functions here are used to keep track of which item is currently selected / in focus, and how many lines to go up / down when scrolling the screen.
"""

# ListViewItemClass holds the data of a single item: that is, a single submission on reddit
# listviewitems is a list of those submissions.
class	ListViewItemClass:
	redditid = 1	# reddit id, not index!
	title = "title"
	author = "author"
	text = "text"	# selftext, title/topic in this case
	subreddit = "subreddit"	# what subreddit item belongs to. Important for user frontpage

	def __init__(self, redditid, title, author, text, subreddit):
		self.redditid = redditid
		self.title = title
		self.author = author
		self.text = text
		self.subreddit = subreddit


# listviewitems is a list. We'll be populating it with instances of ListViewItemsClass in other functions
listviewitems = []

# ListViewClass keeps info about the items currently shown in the UI, be it a subreddit, user_liked or something else
class ListViewClass:
	# ui specific - what we show on screen
	topmost = 0	# topmost row of reader.contents shown
	itemid = 0	# index to the selected item - the item hilighted. The row the item is in must always be within printlines(start,end)
	# info about subreddit of choice
	subreddit = "worldnews" # default sub to read if not logged in
	showlimit = 30
	type = 2        # hot = 1, new = 2, rising = 3, controversial = 4, top = 5. What's the reddit te$
	time = 0        # 1 for all, 2 for hour, 3 for today, 4 for month, 5 for year. 0 for everything $
	# previous topbar to return to after readerview or infoview
	topbar = 0
	# return the line in uiscreen to be hilighted.
	# this is used by currentlist.movement functions to calculate which item is currently selected
	#########################
	def get_hilightrow(self, id):
	#########################
		global listviewtems
		# calculate the row the item starts on the screen, taking topmostinto account 
		hilightrow = 0
		for index in range(0, id):
			hilightrow += (int) (len(listviewitems[index].title) / uimod.uiscreen_maxx) + 1
		hilightrow -= self.topmost
		return hilightrow

	# return the number of lines listviewitems[id] spawns in listview
	#########################
	def get_listviewlines(self,id):
	#########################
		global listviewitems
		return (int) (len(listviewitems[id].title) / uimod.uiscreen_maxx) + 1


currentlist = ListViewClass()

# reset listviewitems - empty it
#########################
def reset_listview():
#########################
	global listviewitems, listview
	listviewitems = []
	currentlist.itemid = 0
	currentlist.topmost = 0


# populate everything from items to currentlist
#########################
def populate_listview(items):
#########################
	global listviewitems
	for item in items:
		listviewitems.append(ListViewItemClass(item.id, item.title, item.author, item.selftext, item.subreddit))


# display default top bar for listview
#########################
def listview_defaulttopbar():
#########################
	global listview
	# we need some globals from the main file

	# subreddit info on topbar. Differentiate which list is in question
	if currentlist.subreddit == None:
		if (currentlist.topbar == 0): # user frontpage
			uimod.change_topbar("Listview for User Frontpage",1)
		elif (currentlist.topbar == "userliked"):
			uimod.change_topbar("Listview for User Liked", 1)
		elif (currentlist.topbar == "userdisliked"):
			uimod.change_topbar("Listview for User Disliked", 1)
		elif (currentlist.topbar == "usersaved"):
			uimod.change_topbar("Listview for User Saved", 1)
		elif (currentlist.topbar == "userhidden"):
			uimod.change_topbar("Listview for User Hidden", 1)
		elif (currentlist.topbar == "usersub"):
			uimod.change_topbar("Listview for User Submitted", 1)
		elif (currentlist.topbar == "usercom"):
			uimod.change_topbar("Listview for User Comments", 1)
	else: 	# a regular subreddit
		uimod.change_topbar("Listview for /r/" + currentlist.subreddit, 1)

		uimod.topbar_addtext(". Sort criteria: ")
		if (currentlist.type == 1): uimod.topbar_addtext("hot",1)
		if (currentlist.type == 2): uimod.topbar_addtext("new",1)
		if (currentlist.type == 3): uimod.topbar_addtext("rising",1)
		if (currentlist.type == 4): uimod.topbar_addtext("controversial",1)
		if (currentlist.type == 5): uimod.topbar_addtext("top",1)
		# in Reddit, hot and controversial can be queried by date 
		if (currentlist.type == 4 or currentlist.type == 5):
			if (currentlist.time == 1): uimod.topbar_addtext(" by all",1)
			if (currentlist.time == 2): uimod.topbar_addtext(" by hour",1)
			if (currentlist.time == 3): uimod.topbar_addtext(" by day",1)
			if (currentlist.time == 4): uimod.topbar_addtext(" by month",1)
			if (currentlist.time == 5): uimod.topbar_addtext(" by year",1)

	uimod.topbar.refresh()

# bold the listview.itemid in readerviewmod.reader.contents
#########################
def listview_bold(topmost = 0):
#########################
	global currentlist, listviewitems

	# bolding the current item in listview is currently done by clearing all reader contents and rewriting them. This is ineffective.
	readerviewmod.reader.contents[:] = []

	# TODO: how to compare index the python way?
	i = 0
	for item in listviewitems:
		if currentlist.itemid == i: readerviewmod.appendline(item.title, 1)
		else:	readerviewmod.appendline(item.title,0)
		i += 1

	return


#########################
def enter_listview(submissions = None, topbar = None):
#########################
	global currentlist
	# if run as enter_listview(), we simply rewrite current contents.
	# when called with submissions and topbar inf, we change them
	if (topbar == None): # don't change topbar
		donothing = 1
	elif (topbar == "default"):
		listview_defaulttopbar()
	else:
		string, format = topbar
		uimod.change_topbar(string,format)

	if (submissions != None):
		reset_listview()
		populate_listview(submissions)

	# in any case, we need to bold the current item and reprint screen
	listview_bold()
	readerviewmod.print_uiscreen(currentlist.topmost)


# go down in a list, either 1 item or until end of list
#########################
def list_down(pagedown):
#########################
	import curses
	# do nothing if we're on the last item
	if (currentlist.itemid == len(listviewitems) - 1): 
		return

	# unbold current item by rewriting it
	uimod.uiscreen.addstr(currentlist.get_hilightrow(currentlist.itemid),0,listviewitems[currentlist.itemid].title)

	# if pressing page down, set last item as the bottom
	if (pagedown):
		# calculate total lines of all items
		lines = 0
		for index in range(0, (len(listviewitems))):
			lines += currentlist.get_listviewlines(index)
		# calculate which would be the top row 
		#if the last item would be almost at bottom (leave 1 empty line for visual cue)
		lastitemlen = currentlist.get_listviewlines(len(listviewitems) - 1)
		toprow = lines - uimod.uiscreen_maxy + lastitemlen + 1
		# set currentlist.itemid to last item and redraw top row
		currentlist.itemid = len(listviewitems) - 1
		currentlist.topmost = toprow - lastitemlen
		enter_listview()

	else: # simple keydown, go down 1 item
		# advance currentlist.itemid - move down by one item
		currentlist.itemid += 1
		# see if we need to scroll
		# scrolling is required when this item doesn't fit the screen
		currentitemrow = currentlist.get_hilightrow(currentlist.itemid)
		nrlines = currentlist.get_listviewlines(currentlist.itemid)
		if (currentitemrow + nrlines  > uimod.uiscreen_maxy):
			# to scroll, advance currentlist.topmost so this item fits, then redraw
			currentlist.topmost += nrlines
			enter_listview()
			return
		else:
			# if we didn't scroll, bold selected item by rewriting it
			uimod.uiscreen.addstr(currentlist.get_hilightrow(currentlist.itemid),0,listviewitems[currentlist.itemid].title, curses.A_BOLD)
			uimod.uiscreen.refresh()

	return



#########################
def list_up(pageup):
#########################
	global uiscreen, listview
	import curses
	# do nothing if we're on the first item
	if (currentlist.itemid == 0):
		return
	# pageup, go to beginning of list and redraw it
	if pageup:
		currentlist.itemid = 0
		currentlist.topmost = 0
		enter_listview()
		return

	else: # key up, go up 1 item
		# unbold current item
		uimod.uiscreen.addstr(currentlist.get_hilightrow(currentlist.itemid),0,listviewitems[currentlist.itemid].title)

		# decrease the index - move down by one story item
		currentlist.itemid -= 1

		# Scroll up by one item if you need to (note: item, not necessarily row)
		# This happens when we're on topmost row but topmost is not shown
		currentrow = currentlist.get_hilightrow(currentlist.itemid)
		if (currentlist.topmost != 0 and currentrow <= 0):
			currentlist.topmost += currentrow
			if (currentlist.topmost <= 0):
				currentlist.topmost = 0			
			enter_listview()
		else:
			# bold selected item
			uimod.uiscreen.addstr(currentlist.get_hilightrow(currentlist.itemid),0,listviewitems[currentlist.itemid].title,curses.A_BOLD)
			uimod.uiscreen.refresh()
