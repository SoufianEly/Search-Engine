import urllib2
import requests
from bs4 import BeautifulSoup
import logging
import time
import re
import os.path
from base64 import b16encode
import argparse
#------ Web Crawler --------------

#Union Operation of two lists, q is added to p
def union(p,q):
    for e in q:
        if e not in p:
            p.append(e)

#Get Page Source code, if possible.
def get_page(page):	
	try:
		source = urllib2.urlopen(page)
		val =  source.read()
		source.close()
		return val
	except:
		return ""


#Changes the Keyword score!	
def change_score(index, keyword):
	for url in index[keyword]["url"]:
		old_score = index[keyword]["url"][url]["score"]
		new_score = index[keyword]["url"][url]["total"]/float(index[keyword]["total"])
		index[keyword]["url"][url]["score"] = new_score
		index[keyword]["url"][url]["tscore"] = index[keyword]["url"][url]["tscore"] - old_score + new_score


#Adds an entry to index
def add_to_index(index, keyword, page):
	if keyword in index:
		index[keyword]["total"] += 1
		
		if page not in index[keyword]["url"]:
			index[keyword]["url"][page] = {"total" : 0, "score" : float(0.0), "ctotal" : 0,
			 "cscore" : 0.0, "tscore" : 0.0} 
		index[keyword]["url"][page]["total"] += 1
		change_score(index, keyword)
		
	else:
		index[keyword] = { 
					"url" : 
						{ page : 
							{"total" : 1, 
							"score" : float(1.0), 
							"ctotal" : 0, 
							"cscore" : 0.0, 
							"tscore" : 1.0
							} 
							}, 
					"total" : 1,
					"ctotal" : 0
				}   


#Get Next Link, return None if no More links on Page
#Works by searching for <a href = "....." 
def get_next_target(s) :
	start_link = s.find('<a href=')
	if start_link == -1:
		return None, 0	
	start_quote = s.find('"', start_link)
	end_quote = s.find('"', start_quote + 1)
	url = s[start_quote+1:end_quote]
	return url, end_quote

#Gets the content of page, and split them to get the entry
def add_page_to_index(index, url):
	for word in get_page(url).split():
		if not word.isalpha():
			word = re.sub('[,()<>/.//]', '', word)
		add_to_index(index, word.lower(), url)


#Using Get_next_target, get all links and return the list containing all URL's present in given page
def get_all_links(page):
	url_list = []
	while True:
		url, end_quote = get_next_target(page)
		if url:
			page = page[end_quote:]
			url_list.append(url)
		else:
			break			
	return url_list
#Crawl the Whole Web, AND index it
# generate graph that content all the links :3
#Use two lists : tocrawl and Crawled
#tocrawl: All web-pages still to be visited
#Crawled: All web-pages visited
#breadth-first Approach :D
def crawl_web(seed, max_depth):

	tocrawl = [[seed, 0]]		#This time, we keep track of depth of loop
	crawled = []
	index = {}
	graph = {}
	i = 1
	headers = { 'User-Agent': 'Search in web bot version 0.1'}
	while tocrawl:
		ele = tocrawl[0]
		page = ele[0]
		depth = ele[1]
		tocrawl = tocrawl[1:]
		
		if page not in crawled and depth <= max_depth:
		    print "hna= ",page
		    if page.startswith("/"):
			page = seed + page
		    if re.match('^[a-zA-Z]+', page) is None :
			continue
		    if page.startswith("#") or page.startswith("?") or page.startswith("!"):
			continue
		    r = requests.get(page, headers=headers)
		    html = r.text
		    if len(b16encode(page)) >250:
			continue
		    stored_text_file_name = os.path.join("links", b16encode(page))
		    stored_text_file = open(stored_text_file_name, "w")
		    stored_text_file.write(html.encode('utf8'))
		    stored_text_file.close()
		    time.sleep(2)
		    links = get_all_links(get_page(page))
		    final = []
		    
		    for e in links:
				final.append([e, depth+1])
		
		    #graph[page] = links
			
		    add_page_to_index(index, page)
		    union(tocrawl, final)
		    crawled.append(page)
		    
		    if len(crawled) > 50*i:
		    	print 50*i
		    	i += 1
			
#------ END OF CRAWLER -----------------------------

def main():
	logging.getLogger().setLevel(logging.INFO)
	logging.info("Start Crawling")
	parser = argparse.ArgumentParser(description='Crawl a start url for a depth')
	parser.add_argument("--start_url", dest="start_url")
	parser.add_argument("--max_depth", dest="max_depth")
	args = parser.parse_args()
	print args.start_url,args.max_depth
	print "here ",args.start_url,args.max_depth
	crawl_web(args.start_url,args.max_depth)
	#print "index =", index 
	#print "graph =", graph
if __name__ == "__main__": #are you warking in from cml
	main()
