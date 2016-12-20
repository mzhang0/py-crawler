#!/usr/bin/python

import os

def recover_data(frontier, visited, subdomains, filetypes):
	global crawl_counter
	frontier.popleft()
	with open("input" + os.sep + "frontier.txt", 'r') as frontier_f:
		print("Loading frontier...")
		for frontier_url in frontier_f:
			frontier.append(frontier_url.strip('\n'))
	with open("input" + os.sep + "visited.txt", 'r') as visited_f:
		print("Loading visited...")
		for visited_url in visited_f:
			visited.add(visited_url.strip('\n'))
	with open("input" + os.sep + "subdomains.txt", 'r') as subdomains_f:
		print("Loading subdomains...")
		for subdomain in subdomains_f:
			subdomains.add(subdomain.strip('\n'))
	with open("input" + os.sep + "filetypes.txt", 'r') as filetypes_f:
		print("Loading filetypes...")
		for line in filetypes_f:
			filetype_count = line.strip('\n').split(',')
			filetypes[filetype_count[0]] = int(filetype_count[1])
	with open("input" + os.sep + "counter.txt", 'r') as counter_f:
		print("Loading counter...")
		count = counter_f.readline().strip('\n')
	return int(count)