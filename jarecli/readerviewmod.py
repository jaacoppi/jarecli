# jarecli - jaacoppi's reddit client
# A reddit client using Python & PRAW
# MIT LICENSED. See LICENSE for details

# readerviewmod.py contains all readerview and infoview related code

# we need the jarecli ui code and curses (for keybinds)
from . import uimod
import curses
import praw

# ReaderViewClass shows our content on screen
# topmost is used for scrolling text in readerview. It is the topmost line to show. Bottommost (should be) reader.topmost+uiscreen_maxy
class ReaderViewClass:
	topmost = 0		# topmost line of contents shown
	contents = [] 		# a list of lines to show in readerview / infoview
	# comment variables keep track of which comment to display next
	comment_branch = 0	

	# load all comments in a given branch to self.contents
	# loads a branch master and all nested replies to self.contents[]
	#########################
	def comment_loopreplies(self, comment, parent_item):
	#########################
		if isinstance(comment, praw.objects.MoreComments):
			appendline("Debug: there's a MoreComments instance here...")
		else:
			loadcomment(comment,parent_item)
			# if the comment has nested replies, display them. TODO: show reply branches
			if comment.replies != []:
				for reply in comment.replies:
					self.comment_loopreplies(reply, parent_item)

	# Load next comment to contents[] and display it
	#########################
	def comment_load_nextbranch(self, submission, parent_item):
	#########################
		comment = list(submission.comments)

		# we've shown all comments, do nothing
		if self.comment_branch >= len(comment):
			return

		# print the first item in branch, move reader to top of branch
		self.topmost = len(reader.contents)
		appendline("New comment branch #%d:" % (self.comment_branch + 1), 1)
		self.comment_loopreplies(comment[self.comment_branch], parent_item)

		# print from the top of the branch, with next keypress load the next branch
		print_uiscreen(self.topmost)
		self.comment_branch += 1
		return





reader = ReaderViewClass()

# load a comment to readerview .contents[]
#########################
def loadcomment(comment,parent):
#########################
	# note: we used to check for MoreComments here, but now comment_loopreplies does it.
	# mark original author posts in comments
	if (comment.author == parent.author):
		appendline("comment " + comment.id + " by " + str(comment.author) + " (Original poster)", 1)
	else:
		appendline("comment " + comment.id + " by " + str(comment.author), 1)

	# comment body + a newline before next comment
	appendline(comment.body)
	appendline("")


# append a string to reader.contents line by line
# linestring can be any length. It is spliced/divided here so that each line in readerview
# fits the ncurses UI (uiscreen_maxx).
# format is appended as such
#########################
def appendline(linestring, format = 0):
#########################
	global reader

	# TODO: appendline should detect all newlines. If there's a newline in linestring, append until it and continue from next line.
	linestring = linestring.split("\n")
	for item in linestring:
		linestobewritten = ( int (len(item) / uimod.uiscreen_maxx))
		for x in range(0, linestobewritten +1): 
			if x == linestobewritten:	# last line, add a newline
				reader.contents.append([item[x*uimod.uiscreen_maxx : (x*uimod.uiscreen_maxx + uimod.uiscreen_maxx)] + "\n" , format])
			else: 
				reader.contents.append([item[x*uimod.uiscreen_maxx : (x*uimod.uiscreen_maxx + uimod.uiscreen_maxx)], format])

	return


# the function prints a screenful of text in list reader.contents starting from line
# reader.contents must be of format [text, format]
# text is a uiscreen_maxx long string, format is 0 for nothing, else for bold
#########################
def print_uiscreen(startline = 0):
#########################
	global reader

	uimod.uiscreen.clear()
	# print at most all the lines in reader.contents. 
	# If they don't fit the screen, print at most a screenful
	
	# calculate the proper endline - how long in reader.contents should we go?
	# TODO: simplify code
	# by default, go to the end
	endline = len(reader.contents)
		
	# if the range is more than screensize, cap it to screensize
	if (endline - startline >= uimod.uiscreen_maxy):
		endline = startline + uimod.uiscreen_maxy - 1

	# needed to fix scrolling, probably due to bugs in other functions
	if (len(reader.contents) <= endline):
		endline -= 1

	# print line by line
	for index in range(startline, endline +1):
		item, format = reader.contents[index]

		# the last line must be dealt with separately:
		if (index == endline):
			# strip newline of the last item so we can fill the whole screen
			item = item.strip("\n")

		# bold the selected lines
		try:
			if format == 0:
				uimod.uiscreen.addstr(item)
			else:
				uimod.uiscreen.addstr(item, curses.A_BOLD)

                # this happens if a text body or comments have newlines.
                # appendline doesn't detect them, so printing line by line doesn't work.
                # we circumvent the problem by stopping writing here.
		except uimod.curses.error:
                # TODO: this should never happen. It mostly happens when addstr happens on last row and len(item) == uiscreen_maxx. There would be a newline, but we can't fit it in since it's the last line and an overflow occurs
                # basically we're fine skipping it, but this is lousy coding
			break
  
		
	uimod.uiscreen.refresh()

	return



# load a selected listviewitem from reddit to reader.contents
#########################
def loaditem(redditconnection, selected_listviewitem):
#########################
	global reader, r
	# print readerview info
	uimod.change_topbar("Readerview item at /r/" + str(selected_listviewitem.subreddit),1)
	# clear current screen and give a debug message
	uimod.uiscreen.clear()
	uimod.uiscreen.addstr("Loading content for item, this might take a while..\n")
	uimod.uiscreen.refresh()
	submission = redditconnection.get_submission(submission_id=selected_listviewitem.redditid)

	# empty current readerview
	reader.contents[:] = []
	# append everything to list reader.contents line by line.

	# title and author
	# TODO: figure out a way to unbold "by" inbetween - appendline doesn't allow this atm
	appendline(str(selected_listviewitem.title) + " by " + str(selected_listviewitem.author),1)

	# if the submission is a link instead a selfpost, give the original url
	if (submission.is_self != True):
		appendline("Link to original content: " + submission.url + "\n")
		appendline("")


	# OP selftext
	appendline(str(selected_listviewitem.text) + "\n")
	
	# for debug: skip all comments
	### comments ###
	# set maximum amount of comments
	reader.comment_trees = len(submission.comments)
	appendline("This item has %d comments" % submission.num_comments + " in %d branches. Press 'c' to load the next comment branch. This will take a while for large branches due to Reddit API restrictions.\n" % reader.comment_trees, 1)
	
	print_uiscreen()

	return


# Enters infoview by printing everything in reader enabling infoviewkeys
# infotextlist is [item, format], where item is a string and format is appendline formatting
# TODO: is comingfrom actually needed for anything?
#########################
def enter_infoview(infotextlist, comingfrom):
#########################
	# display the stuff in reader, always starting from line 0

	uimod.change_topbar("Infoview - Press Enter/Space to return",1)

	reader.contents[:] = []
	for item, format in infotextlist:
		appendline(item,format)

	print_uiscreen()
	return infoviewkeys(comingfrom)

# keybinds for infoview. 
# TODO: move these inside the main keyloop
#########################
def infoviewkeys(comingfrom):
#########################
	global reader
	while True:
		input = uimod.uiscreen.getch()

		# return to readerview or listview with enter or space
		if (input == curses.KEY_ENTER or input == 10 or input == 32):
			reader.topmost = 0	# reset reader.topmost
			if (comingfrom == 0): # coming from reader
				return 1
			if (comingfrom == 1):
				return 2
		
		if input == curses.KEY_DOWN:
			if reader.topmost < (len(reader.contents) - uimod.uiscreen_maxy + 1):
				reader.topmost += 1
				print_uiscreen(reader.topmost)

		if input == curses.KEY_UP:
			if reader.topmost > 0: 
				reader.topmost -= 1
				print_uiscreen(reader.topmost)

		# page up - beginning of text 
		if input == curses.KEY_PPAGE:
			reader.topmost = 0	
			print_uiscreen(reader.topmost)

		# page down - end of text 
		if input == curses.KEY_NPAGE:
			reader.topmost = (len(reader.contents) - uimod.uiscreen_maxy + 1)
			print_uiscreen(reader.topmost)
