REQUIREMENTS
	
	Python 3.x.x
	BeautifulSoup (pip install beautifulsoup4)
	lxml parser (pip install lxml)

	If lxml cannot be installed, change PARSER in crawler.py to "html.parser"

INSTRUCTIONS
	
	Directory setup:
		py-crawler/
			crawler.py
			recover.py
			input/
				frontier.txt (optional)
				visited.txt (optional)
				count.txt (optional)
				filetypes.txt (optional)
				subdomains.txt (optional)
			output/
				...
	
	To run a fresh crawl,

		$ python crawler.py

	To resume a stopped or crashed crawl,

		Copy the frontier.txt, visited.txt, count.txt, filetypes.txt, and
		subdomains.txt files from the output directory to the input directory

		$ python crawler.py recovery

NOTES

	If the crawler crashes or if you interrupt the program via CTRL+C,
	then the contents of the frontier, visited list, subdomains list, 
	crawl counter, and filetypes dictionary are dumped into .txt files 
	at the output directory.

	Logs are periodically written to log.csv which can also be found in the
	output directory once the crawl begins.