# Python 3.x.x

from html.parser import HTMLParser
from urllib.request import urlopen
from urllib.robotparser
from urllib import parse
from bs4 import BeautifulSoup, SoupStrainer # pip install beautifulsoup4

MAX_DEPTH = 10

home_url = "https://www.uky.edu/"
frontier = [url]
visited = [url]
visited_subdomains = []
crawl_counter = 0

rp = urllib.robotparser.RobotFileParser()
rp.set_url(home_url + "robots.txt")

while len(frontier) > 0:
	page = urllib.urlopen





def is_uky_domain(url):
	return ("uky.edu" in url)



