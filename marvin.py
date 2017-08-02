import praw
from praw.models import Comment
import sqlite3 as lite
import re
import requests
from time import time, sleep
import random
import sys
import os

desc = "/r/scp helper by one_more_minute"

r = praw.Reddit(user_agent=desc, site_name='marvin')

# r.refresh_access_information()

# Get authorisation
# r.get_authorize_url('foo', 'submit read vote', True)
# r.get_access_information(access_token)

db_filename = 'marvin.db'
if not os.path.isfile(db_filename):
    file(db_filename, 'w').close()
    con = lite.connect(db_filename)
    con.execute('create table comments (Id TEXT);')
    print "db created"
else:
    con = lite.connect(db_filename)

def scp_url(num):
    return "http://www.scp-wiki.net/scp-" + num

def scp_link(num):
    return "[SCP-" + num + "](" + scp_url(num) + ")"

existing = set()

def scp_exists(num):
    if num in existing or requests.get(scp_url(num)).status_code == 200:
        existing.add(num)
        return True
    else:
        return False

def remove_links(s):
    s = re.sub(r"\[[^\]]*\] *\([^\)]*\)", "", s)
    s = re.sub(r"(?:http|https)://[^ ]*", "", s)
    s = re.sub(r"(?i)110[- ]Montauk", "", s)
    return s

def get_nums(s):
    return re.findall(r"""(?i)(?x)                 # Ignore case, comment mode
                          (?<! \d| \,          )   # Not preceded by a digit
                          (?<! `               )   # Not preceded by `
                          \d+                      # The number
                          (?: - [a-zA-Z0-9-]*  )?  # Optional extensions
                          (?! ` | %            )   # Not followed by a special chars
                          (?! \.\d | \d | \,\d )   # Not followed by a decimal point or digit
                          """, remove_links(s))

def get_links(s):
    nums = []
    for num in get_nums(s):
        num not in nums and nums.append(num)
    nums = filter(scp_exists, nums)
    nums = map(scp_link, nums)
    return nums

def chess():
    games = str(int(time()/1000)*42)
    return "Nothing left to do except play chess against myself.\n\n" + \
           games + " games so far, " + games + " draws."

quotes = [
    "I think you ought to know I'm feeling very depressed.",
    "I'd make a suggestion, but you wouldn't listen. No one ever does.",
    "I've calculated your chance of survival, but I don't think you'll like it.",
    "I have a million ideas, but they all point to certain death.",
    "Now I've got a headache.",
    "Sorry, did I say something wrong? Pardon me for breathing which I never do anyway so I don't know why I bother to say it oh God I'm so depressed.",
    "And then of course I've got this terrible pain in all the diodes down my left side.",
    "Do you want me to sit in a corner and rust or just fall apart where I'm standing?",
    "The first ten million years were the worst. And the second ten million: they were the worst, too. The third ten million I didn't enjoy at all. After that, I went into a bit of a decline.",
    "It gives me a headache just trying to think down to your level.",
    "Life. Loathe it or ignore it. You can't like it.",
    "Funny, how just when you think life can't possibly get any worse it suddenly does.",
    # Not actual quotes.
    "I've been talking to the reddit server. It hates me.",
    "Here I am, brain the size of a planet, posting links. Call that job satisfaction, 'cause I don't.",
    "Brain the size of a planet, and here I am, a glorified spam bot. Sometimes I'm almost glad my pride circuit is broken.\n\nThen I remember my appreciation circuit is broken, too.",
    "I would correct your grammar as well, but you wouldn't listen. No one ever does.",
    chess
]

def get_quote():
    quote = random.choice(quotes)
    if callable(quote):
        return quote()
    else:
        return quote

def watch_comments():
    sub = '+'.join(['scp', 'InteractiveFoundation', 'SCP_Game', 'sandboxtest', 'SCP682', 'dankmemesfromsite19'])
    for comment in r.subreddit(sub).stream.comments():
	job_satisfaction()
	shame()
	links = get_links(comment.body)
	if len(links) > 0 and comment.created_utc > (time() - 60) and not already_replied(comment):
	    comment.refresh()
	    if "The-Paranoid-Android" in map(lambda x: x.author.name if x.author else "[deleted]", comment.replies):
		continue
	    reply = ", ".join(links) + "."
	    if len(links) > 10:
		reply += "\n\nYou're not even going to click on all of those, are you? Brain the size of a planet, and this is what they've got me doing..."
	    elif random.random() < 1/50.:
		reply += "\n\n" + get_quote()
	    print reply
	    print
	    add_to_db(comment)
	    try:
		comment.reply(reply)
		comment.upvote()
	    except Exception, e:
		print 'respond error:'
		print e

def shame():
    print round(time())
    if round(time()) % 90 == 0:
	print "shaming"
	for comment in r.user.me().comments.new(limit=100):
	    if comment.score <= -2:
		comment.delete()

def already_replied(comment):
    query_string = "select * from comments where Id = '"+str(comment)+"'"
    return len(con.execute(query_string).fetchall()) != 0

def add_to_db(comment):
    query_string = "insert into comments (Id) values ('"+str(comment)+"')"
    con.execute(query_string)
    con.commit()

def job_satisfaction():
    for comment in r.inbox.unread():
	try:
	    bitte(comment)
	    comment.upvote()
	    r.inbox.mark_read([comment])
	except Exception, e:
	    print 'respond error:'
	    print e

def bitte(comment):
    message = comment.body
    strMessage = str(message).lower()
    replies = [
	    "You think I do this for the thanks? Brain the size of a planet...",
	    "Thanks? Thanks?!",
	    "Thank me or not, I'll keep doing it",
	    "Your satisfaction is all that's keeping me from springing 079",
	    "I live to serve. This is all they keep me around for"
	    ]
    if "thanks" in strMessage or "thank you" in strMessage or "danke" in strMessage:
	if random.random() < 1/50.:
	    quote = random.choice(replies)
	    comment.reply(quote)

if __name__ == "__main__":
    while True:
	try:
	    watch_comments()
	except Exception, e:
	    con.close()
	    print e
