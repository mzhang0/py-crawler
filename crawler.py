# Python 3.x.x

from html.parser import HTMLParser
import urllib.request
import urllib.robotparser
from bs4 import BeautifulSoup # pip install beautifulsoup4
from urllib.parse import urljoin, urlparse, urlunparse
import re
from collections import deque
import ssl

FILETYPES = [".html", ".htm", ".asp", ".aspx", ".php", ".jsp", ".jspx", "/"]

home_url = "https://www.uky.edu/"
frontier = deque([home_url]) # Queue of URLs to crawl
visited = [] # List of visited URLs
visited_subdomains = [] # List of visited subdomains

# Regex checking if URL is absolute
abs_url_regex = re.compile("^(?:[a-z]+:)?", re.IGNORECASE)

# Regex checking if URL scheme of link depends on the scheme of current page
cur_protocol_regex = re.compile("^(//)", re.IGNORECASE)

rp = urllib.robotparser.RobotFileParser()
rp.set_url(home_url + "robots.txt")
rp.read()

# Fix //english.as.uky.edu/ - use urlparse?? followed by urlunparse??

def crawl():
	crawl_counter = 0
	context = ssl._create_unverified_context()
	while len(frontier) > 0:
		url = frontier.popleft()
		url_no_scheme = urlunparse(urlparse(url)._replace(scheme=""))
		if not was_visited(url_no_scheme):
			try:
				with urllib.request.urlopen(url, context=context) as response:
				   html = response.read()
			except Exception as e:
				print("ERROR while fetching " + url)
				print(e)
			else:
				page_links = parse_links(html, urlparse(url).scheme)
				frontier.extend(page_links)
				crawl_counter += 1
				print(str(crawl_counter) + ": " + url)
			visited.append(url_no_scheme)

def was_visited(link):
	for visited_link in visited:
		if visited_link == link:
			return True
	return False

def rel_to_abs_url(url, protocol):
	url_scheme = urlparse(url).scheme

	if abs_url_regex.match(url) is None: # URL is relative
		return urljoin(home_url, url)
	elif cur_protocol_regex.match(url) is not None:
		return urljoin(protocol + ":", url)
	elif url_scheme != "http" and url_scheme != "https": # HTTP(S) schemes only
		return None
	elif "uky.edu" in url:
		return url
	else: # URL is NOT part of the UKY domain
		return None

def parse_links(html, protocol):
	links = []
	soup = BeautifulSoup(html, 'html.parser')
	for element in soup.find_all('a', href=True):
		link = rel_to_abs_url(element.get('href'), protocol)
		if link is not None and len(link) <= 200:
			for filetype in FILETYPES:
				if link.endswith(filetype) and rp.can_fetch("*", link):
					links.append(link)
					break
	return links

crawl()