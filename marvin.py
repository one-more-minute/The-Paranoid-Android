import praw
import re
import requests
from time import time, sleep
import random
import sys
import configparser
import os
import unicodedata
import spider

config = configparser.ConfigParser()
config.read('praw.ini')
config = config['marvin']

#Comments replied to file, so the username doesn't matter
if not os.path.isfile("comments_replied_to.txt"): 
	open("comments_replied_to.txt", "w").close()
	comments_replied_to = []
else:
	with open("comments_replied_to.txt", "r") as f:
		comments_replied_to = f.read().splitlines()
		comments_replied_to = filter(None, comments_replied_to)

desc = "/r/scp helper by one_more_minute"

r = praw.Reddit(user_agent=desc, client_id=config['client_id'], client_secret=config['secret'], username=config['user'], password=config['pass'])

print("Logged in as: " + str(r.user.me()))

# Get authorisation
# r.get_authorize_url('foo', 'submit read vote', True)
# r.get_access_information(access_token)

def scp_url(num):
	return "http://www.scp-wiki.net/scp-" + num

def scp_link(num):
	return "[SCP-" + num + "](" + scp_url(num) + ")" + spider.scp_title(num)

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

def get_requests(s):
	return re.findall(r"(?i)(?<=Marvin)|((?<=find).*|(?<=get me).*|(?<=search).*)|(?<=\!s).*", s)

def get_scps(s):
	nums = []
	for num in get_nums(s):
		num not in nums and nums.append(num)
	nums = filter(scp_exists, nums)
	nums = list(map(scp_link, nums))
	return nums

def search_wiki(s):
	requests = []
	for sreq in get_requests(s):
		if sreq:
			sreq not in requests and requests.append(sreq)
			s = s.replace(sreq, "") 
	requests = map(spider.has_results, requests)
	requests = filter(None, requests)
	requests += get_scps(s)
	return requests

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

if __name__ == "__main__":
	spider.update_scip_title_list() 	#updates list of Scips on first run
	global scips = spider.scips			#list of scips and their titles
	
	print("Waiting for user comments...")
	while True:
		sub = '+'.join(['scp', 'InteractiveFoundation', 'SCP_Game', 'sandboxtest', 'SCP682', 'DankMemesFromSite19'])
		sleep(10)		
		try:
			for comment in r.subreddit(sub).stream.comments():
				if comment.id not in comments_replied_to and comment.created_utc > (time() - 60): #Reduces server workload (as get_scps is not called for every comment)
					links = search_wiki(comment.body)		#First priority is given to explicitly called for searches, then for interpreted numbers
					if len(links) > 0:
						comment.refresh()
						reply = "* " + "\n* ".join(links)	#Arranges links in a reddit comment list, rather than just seperating by commas, makes for prettier comments
						if len(links) > 10:
							reply += "\n\nYou're not even going to click on all of those, are you? Brain the size of a planet, and this is what they've got me doing..."
						elif random.random() < 1/50.:
							reply += "\n\n" + get_quote()
						print "\nComment posted by " + str(comment.author)
						print "Replying with: "
						print '"' + reply + '"'
						try:
							comment.reply(reply)
							#comment.upvote()		#I think this is illegal under reddit's TOS, tread carefully
							comments_replied_to.append(comment.id)
							with open("comments_replied_to.txt", "a") as f:
								f.write(comment.id + "\n")
							sleep(1)
						except Exception as e:
							print('respond error:')
							print(e)
		except Exception as e:
			print(e)
