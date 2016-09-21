# Python 3.x.x

from html.parser import HTMLParser
import urllib.request
import urllib.robotparser
from bs4 import BeautifulSoup # pip install beautifulsoup4
from urllib.parse import urljoin, urlparse, urlunparse
import re, ssl, csv, time, os
from collections import deque

#FILETYPES = [".html", ".htm", ".asp", ".aspx", ".php", ".jsp", ".jspx", "/"]
CONTENT_TYPES = ["text/html", "application/xhtml+xml", "application/xml"]

home_url = "https://www.uky.edu/"
frontier = deque([home_url]) # Queue of URLs to crawl
visited = set() # List of visited URLs
visited_subdomains = [] # List of visited subdomains
filetypes = {}
log_entries = []
crawl_counter = 0

# Regex checking if URL is absolute
abs_url_regex = re.compile("^(?:[a-z]+:)?", re.IGNORECASE)

# Regex checking if URL scheme of link depends on the scheme of current page
cur_protocol_regex = re.compile("^(//)", re.IGNORECASE)

rp = urllib.robotparser.RobotFileParser()
rp.set_url(home_url + "robots.txt")
rp.read()

csvfile = open('log.csv', 'w')
log_writer = csv.writer(csvfile, delimiter=',')

def crawl():
	global crawl_counter
	context = ssl._create_unverified_context()
	while len(frontier) > 0:
		url = frontier.popleft()
		url_no_scheme = urlunparse(urlparse(url)._replace(scheme=""))
		if url_no_scheme not in visited:
			try:
				with urllib.request.urlopen(url, context=context, timeout=2) as response:
					content_type = process_headers(dict(response.info()))
					if content_type in CONTENT_TYPES:
						html = response.read()
						page_links = parse_links(html, urlparse(url).scheme)
						frontier.extend(page_links)
			except Exception as e:
				log_entry(time.strftime('%a %H:%M:%S'), url, None, e)
			else:
				crawl_counter += 1
				increment_filetype(content_type.lower())
				log_entry(time.strftime('%a %H:%M:%S'), url, content_type.lower(), None)

			visited.add(url_no_scheme)
	print_stats()

def print_stats():
	print("Pages crawled: " + str(crawl_counter))
	print("Filetypes:")
	for filetype in list(filetypes.keys()):
		print("\t" + filetype + ": " + str(filetypes[filetype]))

def process_headers(headers):
	try:
		header_dict = {key.lower() : val for key, val in headers.items()}
		content_type = header_dict["content-type"].partition(";")[0]
	except Exception as e:
		print(e)
		return None
	else:
		return content_type

def increment_filetype(content_type):
	if content_type in list(filetypes.keys()):
		filetypes[content_type] += 1;
	else:
		filetypes[content_type] = 1;

def log_entry(timestamp, url, content_type, error):
	if error is None:
		print(str(crawl_counter) + ": " + url + " " + content_type + " #" + str(filetypes[content_type]))
		log_entries.append([timestamp, url, "", str(crawl_counter), content_type, str(filetypes[content_type])])
	else:
		print("ERROR while fetching " + url)
		print(error)
		log_entries.append([timestamp, url, "Error", "", "", ""])

	if len(log_entries) > 999:
		for entry in log_entries:
			log_writer.writerow(entry)
		log_entries.clear()

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
		if link is not None and len(link) <= 200 and rp.can_fetch("*", link):
			parsed_link = urlparse(link)
			if len(parsed_link.query) == 0 and len(parsed_link.fragment) == 0:
				links.append(link)
	return links

try:
	crawl()
except KeyboardInterrupt:
	print("\nDETECTED KEYBOARD INTERRUPTION!")
finally:
	for entry in log_entries:
		log_writer.writerow(entry)
	csvfile.close()
	print_stats()
