#!/usr/bin/python

from html.parser import HTMLParser
import urllib.request
import urllib.robotparser
from bs4 import BeautifulSoup # pip install beautifulsoup4
from urllib.parse import urljoin, urlparse, urlunparse
import re, ssl, csv, time, os, sys, recover
from collections import deque

HOME_URL = "https://www.python.org/"
TOP_LVL = "python.org"
CONTENT_TYPES = ["text/html", "application/xhtml+xml", "application/xml"]
PARSER = "lxml" # Use "html.parser" if lxml parser is not installed
ALLOWED_SCHEMES = ["http", "https"]
LOG_LIST_LENGTH = 1000

frontier = deque([HOME_URL]) # Queue of URLs to crawl
visited = set() # Set of unique visited URLs
filetypes = {} # Dictionary where a filetype is the key and the corresponding
			# value is its frequency
log_entries = []
subdomains = set() # Set of unique crawled subdomains
crawl_counter = 0

# Regex checking if URL is absolute
abs_url_regex = re.compile("^(?:[a-z]+:)?", re.IGNORECASE)

# Regex checking if URL scheme of link depends on the scheme of current page
cur_protocol_regex = re.compile("^(//)", re.IGNORECASE)

# Robots.txt parser
rp = urllib.robotparser.RobotFileParser()
rp.set_url(HOME_URL + "robots.txt")
rp.read()

if len(sys.argv) == 2 and sys.argv[1] == "recovery":
	print("RECOVERING FROM DUMP...")
	crawl_counter = recover.recover_data(frontier, visited, subdomains, filetypes)

csvfile = open("output" + os.sep + "log.csv", 'w')
log_writer = csv.writer(csvfile, delimiter=',')

# Main crawling function
def crawl():
	global crawl_counter
	context = ssl._create_unverified_context()
	print("\n\nSTARTING CRAWL\n\n")
	while len(frontier) > 0:
		url = frontier.popleft()
		url_parse = urlparse(url)
		url_no_scheme = urlunparse(url_parse._replace(scheme="", fragment=""))
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
				if url_parse.netloc not in subdomains:
					subdomains.add(url_parse.netloc)
				try:
					content_type = content_type.lower()
					increment_filetype(content_type)
					log_entry(time.strftime('%a %H:%M:%S'), url, content_type, None)
				except TypeError:
					print("Error with content-type")
			visited.add(url_no_scheme)
	print("\n\nCRAWL COMPLETED SUCCESSFULLY\n\n")
	print_stats()

# Extracts the content-type from the HTTP response headers
def process_headers(headers):
	try:
		header_dict = { key.lower() : val for key, val in headers.items() }
		if 'content-type' in header_dict:
			content_type = header_dict['content-type'].partition(';')[0]
			return content_type
		else:
			return None
	except Exception as e:
		print(e)
		return None

# Converts any relative URLs to absolute URLs
def rel_to_abs_url(url, protocol):
	url_scheme = urlparse(url).scheme
	if not is_in_domain(url):
		return None

	if abs_url_regex.match(url) is None: # URL is relative
		return urljoin(HOME_URL, url)
	elif cur_protocol_regex.match(url) is not None:
		return urljoin(protocol + ":", url)
	elif url_scheme in ALLOWED_SCHEMES:
		return url
	else:
		return None

# Checks if a given URL is within TOL_LVL, the specified top level domain
def is_in_domain(url):
	url_netloc = urlparse(url).netloc
	if TOP_LVL in url_netloc:
		return True
	else:
		return False

# Extracts links from crawled webpage.
# Avoids links to calendars, links prohibited by robots.txt, links longer
# than 200 characters in length, and links with query parameters
def parse_links(html, protocol):
	links = []
	soup = BeautifulSoup(html, PARSER)
	for element in soup.find_all('a', href=True):
		link = rel_to_abs_url(element.get('href'), protocol)
		if link is not None and len(link) <= 200 and rp.can_fetch("*", link):
			parsed_link = urlparse(link)
			if len(parsed_link.query) == 0 and "calendar" not in parsed_link.path:
				links.append(link)
	return links

# Increments the filetype counter
def increment_filetype(content_type):
	if content_type in list(filetypes.keys()):
		filetypes[content_type] += 1;
	else:
		filetypes[content_type] = 1;

# Logs the transaction. Logs are flushed to disk every LOG_LIST_LENGTH entries.
def log_entry(timestamp, url, content_type, error):
	if error is None:
		print(str(crawl_counter) + ": " + url + " " + content_type + " #" + str(filetypes[content_type]))
		log_entries.append([timestamp, url, "", str(crawl_counter), content_type, str(filetypes[content_type])])
	else:
		print("ERROR while fetching " + url)
		print(error)
		log_entries.append([timestamp, url, "Error", "", "", ""])

	if len(log_entries) >= LOG_LIST_LENGTH:
		for entry in log_entries:
			log_writer.writerow(entry)
		log_entries.clear()

# Dumps important contents in memory into .txt files for later recovery.
# Pickle can be used instead at the cost of human-readability.
def dump_info():
	with open("output" + os.sep + "frontier.txt", 'w') as frontier_f:
		for url in frontier:
			frontier_f.write(url + '\n')
	with open("output" + os.sep + "visited.txt", 'w') as visited_f:
		for url in visited:
			visited_f.write(url + '\n')
	with open("output" + os.sep + "subdomains.txt", 'w') as subdomain_f:
		for subdomain in subdomains:
			subdomain_f.write(subdomain + '\n')
	with open("output" + os.sep + "counter.txt", 'w') as counter_f:
		counter_f.write(str(crawl_counter) + '\n')
	with open("output" + os.sep + "filetypes.txt", 'w') as filetypes_f:
		for ft in list(filetypes.keys()):
			filetypes_f.write(ft + ',' + str(filetypes[ft]) + '\n')

def print_stats():
	counter_msg = "Resources crawled: " + str(crawl_counter)
	subdomains_msg = "Unique subdomains: " + str(len(subdomains))
	print(counter_msg)
	print(subdomains_msg)
	print("Filetypes:")
	with open("output" + os.sep + "stats.txt", 'w') as stats_f:
		stats_f.write(counter_msg + '\n')
		stats_f.write(subdomains_msg + '\n\n')
		for ft in list(filetypes.keys()):
			ft_msg = ft + ": " + str(filetypes[ft])
			print("\t" + ft_msg)
			stats_f.write(ft_msg + '\n')

try:
	crawl()
except KeyboardInterrupt:
	print("\nDETECTED KEYBOARD INTERRUPTION!")
finally:
	for entry in log_entries:
		log_writer.writerow(entry)
	csvfile.close()
	print_stats()
	dump_info()
	sys.exit()
