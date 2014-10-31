# jarecli - jaacoppi's reddit client
# A reddit client using Python & PRAW
# MIT LICENSED. See LICENSE for details

# some defines for version control
PROGNAME = "jarecli"
VERSION = "0.0.3b"

## check for a minimum python version.
## TODO: figure out what version we actually need - 3.0 was just a guess
from sys import hexversion
from sys import exit
if hexversion < 0x03000000: # 3.3. would be 0x03030000 and so on
   exit("Python 3.0 or newer is required to run this program.")

# requires ncurses and PRAW from git://github.com/praw-dev/praw. Development done with version 2.1.8
import curses

from jarecli import listviewmod
from jarecli import uimod
from jarecli import readerviewmod

########################################
# Define classes and initialize defaults
########################################

# external viewers for opening links
class	externapps:
	browser = "elinks"
	textmode = "True"
	imageviewer = "feh"

class	userclass:
	loggedin = False
	loginname = "nologin"	# by default, don't log in
	loginpass = "nopass"
	userstr = "undefined user" 

external_apps = externapps()		
user = userclass()


#####################
# initialize globals
#####################

submissions = 1 # our submission, we them from load_subreddit
keyboardmode = 0 	# 0 = listview, 1 = readerview, 2 = infoview
yourself = 1	# holds get_redditor(user.loginname), used to show liked etc

# open config file. TODO: maybe get config file as a paremeter?
from os.path import expanduser
home = expanduser("~")
conf_file = home + "/.jarecli"

"""
How listview, readerview and infoview work:

Listview takes the items in listviewitems[] and displays them. There's an ability to browse through
items with keys.
	
Readerview displays stuff line by line. There's no items of any kind, only lines of text.

Infoview is readerview for keyup,keydown, pageup & pagedown. It returns to either listview or readerview depending on where it was invoked

All views utilize  printlines() and reader.contents[] to display content
"""



# show user liked in listview
#########################
def show_usersubs(which):
#########################
# values for which:
# 1 = get_liked
# 2 - get_disliked
# 3 - get_saved
# 4 - get_hidden
# 5 - get_submitted
# 6 - get_comments
	global yourself, user, r

	# do nothing if you're not logged in
	if (user.loggedin == False):
		return

	which = int(which)

	# clear current screen and give a debug message
	uimod.uiscreen.clear()
	uimod.uiscreen.addstr("Loading content for item, this might take a while depending on amount of items\n")
	uimod.uiscreen.refresh()

	# start from the beginning of an empty list
	listviewmod.reset_listview()

	# populate listview with our current selection
	if (which == 1):
		uimod.change_topbar("Listview for User Liked",curses.A_BOLD)
		listviewmod.populate_listview(yourself.get_liked())
	if (which == 2):
		uimod.change_topbar("Listview for User Disliked",curses.A_BOLD)
		listviewmod.populate_listview(yourself.get_disliked())
	# saved and hidden are r.user objects, not redditor objects
	if (which == 3):
		uimod.change_topbar("Listview for User Saved",curses.A_BOLD)
		listviewmod.populate_listview(r.user.get_saved())
	if (which == 4):
		uimod.change_topbar("Listview for User Hidden",curses.A_BOLD)
		listviewmod.populate_listview(r.user.get_hidden())
	if (which == 5):
		uimod.change_topbar("Listview for User Submitted",curses.A_BOLD)
		listviewmod.populate_listview(yourself.get_submitted())
	if (which == 6):
		uimod.change_topbar("Listview for User Comments",curses.A_BOLD)
		listviewmod.populate_listview(yourself.get_comments(),1)	# the 1 for iscomment = 1

	# set currentlist.subreddit to a special value so we now 'subreddit info' and some other things will be displayedo
	listviewmod.currentlist.subreddit=None
	# finally, enter listview
	listviewmod.enter_listview()


# load configuration from a file
#########################
def load_config(conf_file):
#########################
	global user, external_apps, listview
	import configparser
	config = configparser.ConfigParser()
	if (config.read(conf_file) == []):
		print("Config file " + conf_file + " not found, using defaults")
		return
	else:
		print("Config file " + conf_file + " found, getting config")

	# TODO: error handling
	# get userinfo
	user.loginname = config['userinfo']['loginname']
	user.loginpass = config['userinfo']['loginpass']
	user.userstr = "/u/" + user.loginname

	# get default subreddit & sort info
	listviewmod.currentlist.showlimit = int((config['sort_criteria']['showlimit']))
	listviewmod.currentlist.type = int(config['sort_criteria']['type'])
	listviewmod.currentlist.time = int(config['sort_criteria']['time'])

	# get external apps
	external_apps.browser = config['external_apps']['browser']
	external_apps.textmode = config['external_apps']['textmode']
	external_apps.imageviewer = config['external_apps']['imageviewer']

	return


# quits the program
#########################
def quit_jarecli():
#########################
	curses.endwin()
	print("\n.." + PROGNAME + " exited succesfully.\n")
	quit()



# open an external program and open link in it
#########################
def goto_url(id):
#########################
	import subprocess
	global r, external_apps, keyboardmode
	# open submission by id
	submission = getsubmission_byid(listviewmod.listviewitems[id].redditid)
	
	# pick the proper app by url
	# TODO: error handling

	# subprocess.PIPE means we put stuff on a pipe and never read them. Putting them in None would mean inheriting from parent -> stdout
	# It can't be used with textmode apps because we need input & output there

	# for textmode (shell access etc), you need to wait for the process to finish and refresh the screen somehow
	
	if (external_apps.textmode == "True"):
		subprocess.call([external_apps.browser, submission.url])
		# redraw listview. TODO: ability to return to readerview as well
		keyboardmode = 0
		listviewmod.enter_listview() 
	else:
		# direct imgur image links
		if (submission.url.find("i.imgur.com/") != -1):
			subprocess.call([external_apps.imageviewer, submission.url], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
		# others
		else:
			subprocess.call([external_apps.browser, submission.url], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
	


#########################
def change_subreddit():
#########################
	global r, user
	import curses

	# ask for the new subreddit. Echo what is typed.
	uimod.uiscreen.clear()
	uimod.uiscreen.addstr("Give a name of subreddit. \"FrontPage\" for Reddit frontpage \"1\" for user frontpage\n")
	uimod.uiscreen.addstr("For user liked, disliked, saved, hidden, submitted and comments, press 1-6 in listview\n")
	uimod.uiscreen.addstr("Subreddit: /r/")
	uimod.uiscreen.refresh()
	curses.echo()
	newsub = str(uimod.uiscreen.getstr().decode(encoding="utf-8")) # decode the byte from getstr to string
	# if user selects empty string, do nothing
	if (newsub == None or newsub == "1"): # selected user front page
		listviewmod.currentlist.subreddit = None
		# TODO: if user is not logged in, display a message and show FrontPage instead
		# if user.loggedin == False:
	elif (newsub == ""):
		uimod.uiscreen.addstr("Selected subreddit left empty, using old value ")
		if (listviewmod.currentlist.subreddit == None): uimod.uiscreen.addstr("User Frontpage\n", curses.A_BOLD)
		else: 	uimod.uiscreen.addstr(listviewmod.currentlist.subreddit + "\n", curses.A_BOLD)
		uimod.uiscreen.refresh()

	else:	# not empty, select it
		listviewmod.currentlist.subreddit = newsub

	curses.noecho()
	uimod.uiscreen.addstr("You chose: ")
	if listviewmod.currentlist.subreddit != None: 	uimod.uiscreen.addstr(listviewmod.currentlist.subreddit + "\n", curses.A_BOLD)
	else:	uimod.uiscreen.addstr("User Frontpage",curses.A_BOLD)

	# ask for type
	uimod.uiscreen.addstr("\nPress 1 for hot, 2 for new, 3 for rising, 4 for controversial, 5 for top. Enter for default (new)\n")
	uimod.uiscreen.refresh()
	while True:
		# TODO: ints, not ascii values
		type = uimod.uiscreen.getch()
		if (chr(type) >= '1'  and chr(type) <= '5'): 
			listviewmod.currentlist.type = type - 48
			break
		if (type == 10):
			listviewmod.currentlist.type = 1
			break

 	#  ask for time (for controversial and top only, others get time = 0
	if (listviewmod.currentlist.type == 4 or listviewmod.currentlist.type == 5):
		uimod.uiscreen.addstr("\nPress 1 for all, 2 for hour, 3 for today, 4 for month, 5 for year. Enter for default (day)\n")
		uimod.uiscreen.refresh()
		while True:
			# TODO: ints, not ascii values
			type = uimod.uiscreen.getch()
			if (chr(type) >= '1'  and chr(type) <= '5'): 
				listviewmod.currentlist.time = type - 48
				break
			if (type == 10):
				listviewmod.currentlist.time = 3
				break
	else:
		listviewmod.currentlist.time = 0

	# Ask for the item showlimit
	uimod.uiscreen.addstr("Give a maximum amount of items: ")
	uimod.uiscreen.refresh()
	curses.echo()
	newlimit = str(uimod.uiscreen.getstr().decode(encoding="utf-8")) # decode the byte from getstr to string
	curses.noecho()
	# if user selects empty string, do nothing
	if (newlimit == ""):
		uimod.uiscreen.addstr("Left empty, using old value ")
		uimod.uiscreen.addstr("%d" % listviewmod.currentlist.showlimit + "\n", curses.A_BOLD)
	else:	# not empty, select it
		listviewmod.currentlist.showlimit = int(newlimit)
		uimod.uiscreen.addstr("Selected %d" % listviewmod.currentlist.showlimit)

	uimod.uiscreen.addstr("\nPRESS ENTER\n")
	uimod.uiscreen.refresh()
	uimod.uiscreen.getch()

	submissions = load_subreddit(listviewmod.currentlist, r)
	listviewmod.enter_listview(submissions) # start with a fresh listview



# load and return items from a selected subreddit to listview
#######################
def load_subreddit(listview, r = None):
#######################
	global uiscreen
	# Get submissions
	import requests
	try:
		if (listview.subreddit == None): # User Frontpage
			submissions = r.get_front_page(limit=listview.showlimit)
		else: # we want listview.subreddit
			## get_hot
			if listview.type == 1: 	submissions = r.get_subreddit(listview.subreddit).get_new(limit=listview.showlimit)

			# get_new
			if listview.type == 2:	submissions = r.get_subreddit(listview.subreddit).get_hot(limit=listview.showlimit)

			# get_new
			if listview.type == 3:	submissions = r.get_subreddit(listview.subreddit).get_rising(limit=listview.showlimit)

			# get_controversial
			if listview.type == 4:
				if listview.time == 1:	submissions = r.get_subreddit(listview.subreddit).get_controversial_from_all(limit=listview.showlimit)
				if listview.time == 2:	submissions = r.get_subreddit(listview.subreddit).get_controversial_from_hour(limit=listview.showlimit)
				if listview.time == 3:	submissions = r.get_subreddit(listview.subreddit).get_controversial_from_day(limit=listview.showlimit)
				if listview.time == 4:	submissions = r.get_subreddit(listview.subreddit).get_controversial_from_month(limit=listview.showlimit)
				if listview.time == 5:	submissions = r.get_subreddit(listview.subreddit).get_controversial_from_year(limit=listview.showlimit)

			# get_top	
			if listview.type == 5:
				if listview.time == 1:	submissions = r.get_subreddit(listview.subreddit).get_top_from_all(limit=listview.showlimit)
				if listview.time == 2:	submissions = r.get_subreddit(listview.subreddit).get_top_from_hour(limit=listview.showlimit)
				if listview.time == 3:	submissions = r.get_subreddit(listview.subreddit).get_top_from_day(limit=listview.showlimit)
				if listview.time == 4:	submissions = r.get_subreddit(listview.subreddit).get_top_from_month(limit=listview.showlimit)
				if listview.time == 5:	submissions = r.get_subreddit(listview.subreddit).get_top_from_year(limit=listview.showlimit)
	
	# these will probably never be triggered because of PRAW lazy loading. Will be removed later.
	except requests.exceptions.HTTPError:
		uimod.uiscreen.addstr("HTTPError: subreddit not found. Check case-sensitive spelling and try again.\n")
		uimod.uiscreen.addstr("PRESS A KEY\n")
		uimod.uiscreen.refresh()
		uimod.uiscreen.getch()
		change_subreddit()

	except praw.errors.RedirectException:
		uimod.uiscreen.addstr("PRAW RedirectException: subreddit not found. Check case-sensitive spelling and try again.\n")
		uimod.uiscreen.addstr("PRESS A KEY\n")
		uimod.uiscreen.refresh()
		uimod.uiscreen.getch()
		change_subreddit()

	# if we used /r/random, we need to adjust listview.subreddit so we know the actual subreddit name, not simply "random" (also affects viewing subreddit info etc)
	if (listview.subreddit == "random"):
		# TODO: find out how to pick one item. submissions[0] doesn't work. Now we just quit the loop on the first item
		for item in submissions:
			listview.subreddit = str(item.subreddit)
			break


	try:
		# turn the generator into a list. A list uses more memory, but we can avoid 
		# slow calls to praw.reddit. Exception handling is here because of Praw lazy loading
		submissions = list(submissions)
	except praw.errors.RedirectException as e:
		uimod.uiscreen.clear()
		uimod.uiscreen.addstr("Received RedirectException, can't find this subreddit.\n")
		uimod.uiscreen.addstr("Tried: " + e.request_url + "\n")
		uimod.uiscreen.addstr("Got: " + e.response_url + "\n")
		uimod.uiscreen.addstr("Press Enter to change subreddit\n")
		uimod.uiscreen.refresh()
		uimod.uiscreen.getch()
		change_subreddit()

	except requests.exceptions.HTTPError:
		uimod.uiscreen.addstr("HTTPError: subreddit not found. Check case-sensitive spelling and try again.\n")
		uimod.uiscreen.addstr("PRESS A KEY\n")
		uimod.uiscreen.refresh()
		uimod.uiscreen.getch()
		change_subreddit()

	return submissions


###############################
def subreddit_info(comingfrom):
###############################
	global keyboardmode
	if (listviewmod.currentlist.subreddit != None):
		submission = r.get_subreddit(listviewmod.currentlist.subreddit)
		readerviewmod.enter_infoview([["Subreddit info for " + listviewmod.currentlist.subreddit + "\n",1],[submission.description, 0]], comingfrom)
	else:
		readerviewmod.enter_infoview([["You are currently something else than a normal subreddit. This could be user frontpage or something similar. Press Enter.", 0]], comingfrom)

	if (comingfrom == 0): 	
		keyboardmode = 1
		readerviewmod.loaditem(r,listviewmod.listviewitems[listviewmod.currentlist.itemid])
	if (comingfrom == 1): 	
		keyboardmode = 0
		listviewmod.enter_listview()






#########################
def keyboardloop():
#########################
	import curses
	global keyboardmode
	while (True):
		input = uimod.uiscreen.getch()
		# listviewkeys
		if (keyboardmode == 0):
			if input == curses.KEY_DOWN:
				listviewmod.list_down(0)

			if input == curses.KEY_NPAGE:
				listviewmod.list_down(1)

			if input == curses.KEY_UP:
				listviewmod.list_up(0)

			if input == curses.KEY_PPAGE:
				listviewmod.list_up(1)

			# quit for q and Q
			if (chr(input) == 'q' or chr(input) == 'Q'):
				quit_jarecli()

			# open the story in readerview with Enter or space
			if (input == curses.KEY_ENTER or input == 10 or input == 32):
				keyboardmode = 1
				readerviewmod.loaditem(r,listviewmod.listviewitems[listviewmod.currentlist.itemid])
				continue

			# show subreddit info - enter_infoview
			if chr(input) == 'i':
				keyboardmode = 3 # keyboard actually handled through subreddit_info
				subreddit_info(1)

			# for opening a subreddit with options
			if chr(input) == 'r':
				change_subreddit()

			# goto - open an external app
			if chr(input) == 'g':
				goto_url(listviewmod.currentlist.itemid)

			# show liked/disliked etc. TODO: change keybindings
			if (chr(input) >= '1' and chr(input) <= '6') :
				show_usersubs(chr(input))

			# post a message to current subreddit.
			if chr(input) == 'm':
				submit_message()
				listviewmod.enter_listview()

		################
		# readerviewkeys
		################
		if (keyboardmode == 1):
			# return from readerview to listviewmod.listview with enter or space
			if (input == curses.KEY_ENTER or input == 10 or input == 32):
				keyboardmode = 0
				readerviewmod.reader.topmost = 0	# reset reader.topmost
				readerviewmod.reader.comment_branch = 0 # reset comment branch
				listviewmod.enter_listview()

			if input == curses.KEY_DOWN:
				if readerviewmod.reader.topmost < (len(readerviewmod.reader.contents) - uimod.uiscreen_maxy + 1):
					readerviewmod.reader.topmost += 1
					readerviewmod.print_uiscreen(readerviewmod.reader.topmost)

			if input == curses.KEY_UP:
				if readerviewmod.reader.topmost > 0: 
					readerviewmod.reader.topmost -= 1
					readerviewmod.print_uiscreen(readerviewmod.reader.topmost)

			# page up - beginning of text 
			if input == curses.KEY_PPAGE:
				readerviewmod.reader.topmost = 0	
				readerviewmod.print_uiscreen(readerviewmod.reader.topmost)

			# page down - end of text 
			if input == curses.KEY_NPAGE:
				if (len(readerviewmod.reader.contents) > uimod.uiscreen_maxy):
					readerviewmod.reader.topmost = (len(readerviewmod.reader.contents) - uimod.uiscreen_maxy + 1)
					readerviewmod.print_uiscreen(readerviewmod.reader.topmost)

			# show subreddit info - enter_infoview
			if chr(input) == 'i':
				keyboardmode = 3
				subreddit_info(0)


			# goto - open an external app
			if chr(input) == 'g':
				goto_url(listviewmod.currentlist.itemid)

		# save
		if chr(input) == 's':
			submission = getsubmission_byid(listviewmod.listviewitems[listviewmod.currentlist.itemid].redditid)
			try:
				submission.save()
				readerviewmod.enter_infoview([["Saved this item!\nPress Enter.",0]],0)
			except 	praw.errors.LoginOrScopeRequired:
				readerviewmod.enter_infoview([["You are not logged in, can't save this item.", 0]], 0)
			
			keyboardmode = 1
			readerviewmod.loaditem(r,listviewmod.listviewitems[listviewmod.currentlist.itemid])
 
		# hide
		if chr(input) == 'h':
			submission = getsubmission_byid(listviewmod.listviewitems[listviewmod.currentlist.itemid].redditid)
			readerviedmod.reader.contents[:] = []
			try:
				submission.hide()
				readerviewmod.enter_infoview([["This item is now hidden.",0]],0)
			except 	praw.errors.LoginOrScopeRequired:
				readerviewmod.enter_infoview([["You are not logged in, can't hide this item.",0]],0)

			keyboardmode = 1
			readerviewmod.loaditem(r,listviewmod.listviewitems[listviewmod.currentlist.itemid])

		# upvote
		if chr(input) == '+':
			submission = getsubmission_byid(listviewmod.listviewitems[listviewmod.currentlist.itemid].redditid)
			try:
				submission.upvote()
				readerviewmod.enter_infoview([["Upvoted/liked this item!",0]],0)
			except 	praw.errors.LoginOrScopeRequired:
				readerviewmod.enter_infoview([["You are not logged in, can't vote.",0]],0)

			keyboardmode = 1
			readerviewmod.loaditem(r,listviewmod.listviewitems[listviewmod.currentlist.itemid])


		# downvote 
		if input == 45: # apparently, chr(input) == '-' doesn't work
			submission = getsubmission_byid(listviewmod.listviewitems[listviewmod.currentlist.itemid].redditid)
			try:
				submission.downvote()
				readerviewmod.enter_infoview([["Downvoted/disliked this item!",0]],0)
			except 	praw.errors.LoginOrScopeRequired:
				readerviewmod.enter_infoview([["You are not logged in, can't vote.",0]],0)

			keyboardmode = 1
			readerviewmod.loaditem(r,listviewmod.listviewitems[listviewmod.currentlist.itemid])



		# load &  more comments
		if chr(input) == 'c':
			sub = getsubmission_byid(listviewmod.listviewitems[listviewmod.currentlist.itemid].redditid)
			readerviewmod.reader.comment_load_nextbranch(sub, listviewmod.listviewitems[listviewmod.currentlist.itemid])




	# pressed quit in listview
	quit_jarecli()



# get submission by id
#########################
def getsubmission_byid(id):
#########################
	global r
	return r.get_submission(submission_id=id)


# submit a message
#########################
def submit_message():
#########################
	global r
	# do nothing if you're not viewing proper subreddit
	if (listviewmod.currentlist.subreddit == None):
		readerviewmod.enter_infoview([["You are not viewing any subreddit, can't submit a message!\nPress Enter", 0]], 1)
		return

	uimod.uiscreen.clear()
	uimod.uiscreen.addstr("Submitting a message to /r/" + listviewmod.currentlist.subreddit + "\nPress 1 for url submission, 2 for selfpost.\n", 0)
	uimod.uiscreen.refresh()
	type = 0
	curses.noecho()
	while (True):
		input = uimod.uiscreen.getch()
		if chr(input) == '1':
			uimod.uiscreen.addstr("Selected url submission.")
			type = 1
			break
		if chr(input) == '2':
			uimod.uiscreen.addstr("Selected selfpost submission.\n")
			type = 2
			break

	# get title
	uimod.uiscreen.addstr("Give a title for submission: ",0)
	uimod.uiscreen.refresh()
	curses.echo()
	title = str(uimod.uiscreen.getstr().decode(encoding="utf-8")) # decode the byte from getstr to string
	# if user selects empty string, do nothing
	if (title == None or title == ""):
		uimod.uiscreen.addstr("No title given, exiting. Press Enter.")
		uimod.uiscreen.refresh()
		uimod.uiscreen.getch()
		return
		
	# get url for url posts
	url = None
	textbody = ""
	if type == 1:
		uimod.uiscreen.addstr("Give url for submission: ",0)
		uimod.uiscreen.refresh()
		url = str(uimod.uiscreen.getstr().decode(encoding="utf-8")) # decode the byte from getstr to string
		if (url == None or url == ""):
			uimod.uiscreen.addstr("No url given, exiting. Press Enter.")
			uimod.uiscreen.refresh()
			uimod.uiscreen.getch()
			return

	# get text
	else:
		uimod.uiscreen.addstr("Give text body for submission (in Markdown format): \n",0)
		while (True):
			line = str(uimod.uiscreen.getstr().decode(encoding="utf-8")) # decode the byte from getstr to string
			if line == "EOF":
				break
			textbody = textbody + line + "\n"

	# print out what you would submit
	# TODO: note that this doesn't support multiple screenfuls. Utilize infoview..
	uimod.uiscreen.clear()
	uimod.uiscreen.addstr("This is what you would submit:\n")
	uimod.uiscreen.addstr("Subreddit: " + listviewmod.currentlist.subreddit + "\n")
	uimod.uiscreen.addstr("Title: " + title + "\n")
	if type == '1':
		uimod.uiscreen.addstr("Url: " + url + "\n")
	else:
		uimod.uiscreen.addstr("Text body:\n" + textbody + "\n")


	uimod.uiscreen.addstr("\nPress 'q' to abort, 'm' to post.\n", 1)
	uimod.uiscreen.refresh()

	# abort if necessary, otherwise post
	while (True):
		abort = uimod.uiscreen.getch()
		if (chr(abort) == 'q'): return
		if (chr(abort) == 'm'): break
	
	if type == '1':
		r.submit(listviewmod.currentlist.subreddit, title, url=url)
	else:
		r.submit(listviewmod.currentlist.subreddit, title, text=textbody)
		


# the main flow of execution.
#########################
if __name__ == "__main__":
#########################
	global r
	print(PROGNAME + " " + VERSION + " starting...")

	print("Importing required module PRAW...")
	import praw

	# 0. Load configuration from file, if any. If not, defaults are used.
	load_config(conf_file)

	# 1. init UI
	uimod.initcurses(PROGNAME,VERSION)

	# 2. initialize the Reddit connection (not sure what this call actually does
	userstr = PROGNAME + " " + VERSION + " " + user.userstr
	uimod.uiscreen.addstr("Initializing Reddit connection for " + userstr + "\n")
	# give Reddit our useragent for common courtesy (and API guidelines)
	r = praw.Reddit(user_agent=userstr)

	# 3. login automatically if found in config file
	if (user.loginname != "nologin"):
		try:
			# this subreddit doesn't actually exist, it's a hack used in load_subreddit
			listviewmod.currentlist.subreddit = None
			# TODO: find and remove urllib 3 InsecureRequestWarning
			# https://urllib3.readthedocs.org/en/latest/security.html
			r.login(user.loginname,user.loginpass)
			uimod.uiscreen.addstr("Logging in as user " + user.loginname + ", this might take a few seconds\n")
			uimod.uiscreen.refresh()
			user.loggedin = True
			yourself = r.get_redditor(user.loginname)

		except praw.errors.InvalidUserPass:
			# TODO: make this an infoview box
			uimod.uiscreen.addstr("Invalid username/password. Currently a fatal problem, start again. (TODO: dont quit the program)\n")
			uimod.uiscreen.refresh()
			uimod.uiscreen.getch()
			quit_jarecli()	


	# 4. load the first subreddit. If logged in, it's the frontpage. This also displays it in listview
	submissions = load_subreddit(listviewmod.currentlist, r)

	# 5. start listview and enter the main loop that changes state to/from listview/readerview/infoview and others
	listviewmod.enter_listview(submissions) # start with a fresh listview
	keyboardloop()
#######################
# EOF

