jarecli - jaacoppi's Reddit client
##################################

About
=====
jarecli is a python-based reddit client using ncurses and praw. Developed with python 3.4.1 and PRAW 2.1.18. Tested with linux.

The documentation is a work in progress and there might be mistakes.

The UI consists of three parts, listview, readerview and infoview. Listview shows items in a chosen subreddit. Readerview shows the selected item text and comments. Infoview is basically just a box of text for debug & error messages

License
=======
MIT-licensed. See LICENSE for details.

Configuration file
==================
an INI-style Configuration file is in ~/.jarecli. Documentation is scarce at the moment.

Keybindings in listview
=======================
up, down: 	go to next / previous item
pageup / down:	go to first / last item
enter,space:	open the selected item in the reader
r:		choose a subreddit
i:		show subreddit description
g:		open an external app to view the url
q, Q:		Quit
Login required:
1:		Show user Liked 
2:		Show user Disliked 
3:		Show user Saved
4:		Show user hidden
5:		Show user submitted
6:		Show user comments (experimental & slow)

Keybindings in readerview
=========================
up, down:	go to next / previous row
pageup / down:	go to first / last row
enter, space:	close the reader
g:		open an external app to view the url
Login required:
s:		save an item
+, -:		upvote/downvote (like/dislike) a message (not for comments)
h:		hide an item

Keybindings in infoview
=========================
up, down:	go to next / previous row
pageup / down:	go to first / last row
enter, space:	close infoview


Known bugs
==========
* none at the moment

Known limitations
=================
What you see is what you get. The software doesn't have that much features.

Credits
=======
Some documenation used for background knowledge:
* http://www.reddit.com/dev/api
* http://www.pythonforbeginners.com/api/how-to-use-reddit-api-in-python
* https://praw.readthedocs.org/en/v2.1.16/
* http://nullege.com/codes/search/praw.Reddit.get_front_page
* http://cortex.glacicle.org/
+ many others. We stand on the shoulders of giants.

Contacting the author
=====================
IRC, freenode and ircnet: jaacoppi
