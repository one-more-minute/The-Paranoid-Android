from bs4 import BeautifulSoup
import re
from time import time, sleep
import codecs
import urllib2
import os

regex = re.compile("(?<=SCP-)\d+")
scips = []
titles = False

def isSCP(i):
    if i.contents[0].name == 'a':
        try:
            return regex.search(i.contents[0].string)
        except Exception, e:
            return False
    else:
        return False

def scrape_wiki_page(address):    
    html = urllib2.urlopen(address)
    soup = BeautifulSoup(html, 'html.parser')
    li = soup.find_all('li')
    filteredli = filter(lambda i: isSCP(i), li)
    for f in filteredli:
        scips.append([f.contents[0].string, f.contents[1].strip(" - ")])
    sleep(2)

def update_scip_title_list():
    pages = ['http://www.scp-wiki.net/scp-series', 'http://www.scp-wiki.net/scp-series-2', 'http://www.scp-wiki.net/scp-series-3', 'http://www.scp-wiki.net/scp-series-4']
    global scips
    scips = []
    global titles
    try:
        print "Updating SCP title List"
        for p in pages:
            scrape_wiki_page(p)
        titles = True
        print "Completed succesfully! Using titles"
        f = codecs.open('sciplist.txt', encoding='utf-8', mode='w')
        for l in scips:
            f.write(l[0] + u"|" + l[1] + u"\r\n")
        f.close()
    except Exception, e:
        print 'Unable to scrape wiki for SCP titles - Error: '
        print e
        print 'Trying to recover from backup...'
        if os.path.isfile('sciplist.txt'):
            try:
                f = codecs.open('sciplist.txt', encoding='utf-8', mode='r')
                tlines = f.read().splitlines()
                scips = map(lambda a: a.split('|'), tlines)
                print "Successfully reloaded old SCP title List"
            except Exception, e:
                titles = False
                print "Unable to load from Backup, SCP titles functionality disabled"
        else:
            titles = False
            print "No Backup found, SCP titles functionality disabled"

def scp_title(num):
    if titles:
        s = filter(lambda scip: scip[0].find("SCP-" + str(num)) >= 0, scips)
        if len(s)>0:
            return " - *'" + s[0][1].encode('ascii','ignore') + "'*"
        else:
            return ""
    else:        
        return ""

def has_results(tale):
    address = "http://scp-wiki.wikidot.com/search:site/a/p/q/" + tale.lstrip()
    address = r"%20".join(address.split(" "))    
    try:
        html = urllib2.urlopen(address)
        soup = BeautifulSoup(html, 'html.parser')
        divs = soup.find_all('div')
        divs = filter(lambda d: d.has_attr('class'), divs)
        divs = filter(lambda d: d['class'][0] == u'search-results', divs)
        divs = filter(lambda d: d['class'][0] == u'title', divs[0].find_all('div'))
        divs = divs[0].find_all('a')
        alink = divs[0]['href'].encode('ascii', 'ignore')
        astr = []
        for tag in divs[0].contents:
            astr.append(tag.string)
        astr = "".join(astr)
        return '[' + astr + '](' + alink + ')'
    except Exception, e:
        return "No Results"
