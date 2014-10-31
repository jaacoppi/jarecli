# jarecli - jaacoppi's reddit client
# A reddit client using Python & PRAW
# MIT LICENSED. See LICENSE for details

import curses
# uimod.py contains all listview related code

#UI windows:
# prognameline contains version copyright information. It will be initialized once but never modified
# topbar contains info about which view we're in (listview, readerview and so on)
# uiscreen contains everything else: contents
uiscreen = 1
topbar = 0
# TODO: rename these, since in the code they're used for the reader/listview, not whole ui screen
uiscreen_maxx = 1
iscreen_maxy = 1




# init the UI
#########################
def initcurses(PROGNAME, VERSION):
#########################
	global uiscreen, topbar, uiscreen_maxx, uiscreen_maxy

	# mainscreen holds all other windows. Used for nothing else
	mainscreen = curses.initscr()


	curses.noecho()	# don't echo what you type
	curses.curs_set(0)
	curses.cbreak()		# TODO: is this needed?

	# get screen dimensions. Note that uiscreen_maxy and _maxx are set correctly later
	uiscreen_maxy, uiscreen_maxx  = mainscreen.getmaxyx()

	prognameline = mainscreen.subwin(2,uiscreen_maxx,0,0)

	# print top bar in prognameline
	prognameline.addstr(0,0, PROGNAME + " " + VERSION + " - A Reddit client (C) jaacoppi 2014. MIT LICENSED")
	
	# define the outer box
	topbar = mainscreen.subwin(1,uiscreen_maxx,2,0)

	# calculate the size of of uiscreen so it's right below topbar
	uiscreen_maxy = uiscreen_maxy - 3

	# create uiscreen
	# TODO: uiscreen should be a subwin of _box. No effect on anything, but for code cleanness
	uiscreen = mainscreen.subwin(uiscreen_maxy,uiscreen_maxx,3,0)
	uiscreen.keypad(1)

	# Do not allow scrolling. We use our own scrolling code
	uiscreen.scrollok(False)

	# finally, load the ui
	prognameline.refresh()
	topbar.refresh()
	uiscreen.refresh()




# Change the top bar text in topbar
################
def change_topbar(linestring,format = 0):
#################
	global topbar
	topbar.clear()

	if (format == 0): topbar.addstr(linestring)
	else:	topbar.addstr(linestring,curses.A_BOLD)

	topbar.refresh()

################
def topbar_addtext(linestring,format = 0):
################
	global topbar
	y,x = topbar.getyx()
	if (format == 0): topbar.addstr(y,x,linestring)
	else:	topbar.addstr(y,x,linestring,curses.A_BOLD)

	topbar.refresh()

