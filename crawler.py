# Python 3.x.x

from html.parser import HTMLParser
import urllib.request
import urllib.robotparser
from bs4 import BeautifulSoup # pip install beautifulsoup4
from urlparse import urljoin
import hashlib
import re

MAX_DEPTH = 10
FILETYPES = [".html", ".htm", ".asp", ".aspx", ".php", ".jsp", ".jspx", "/"]

home_url = "https://www.uky.edu/"
frontier = [url]
visited = [url]
visited_subdomains = []
crawl_counter = 0

rp = urllib.robotparser.RobotFileParser()
rp.set_url(home_url + "robots.txt")
rp.read()

while len(frontier) > 0:

	with urllib.request.urlopen('http://python.org/') as response:
	   html = response.read()
	parse_links(html)


def is_uky_domain(url):
	# Regex checking if URL is absolute
	regex = re.compile("^(?:[a-z]+:)?//", re.IGNORECASE)

	if regex.match(url) is None: # URL is relative
		return True
	elif "uky.edu" in url:
		return True
	else: 
		return False


def parse_links(html):
	links = []
	soup = BeautifulSoup(html, 'html.parser')
	for link in soup.find_all('a', href=True):
	    links.append(link.get('href'))

def filter_links(links):
	filtered = []
	for link in links:
		for filetype in FILETYPES:
			if link.endswith(filetype) and rp.can_fetch(link):
				filtered.append(link)
				break
	return filtered



