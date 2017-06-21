import requests
import logging
import re
from bs4 import BeautifulSoup, SoupStrainer, NavigableString

def html_to_text(html):
    "Creates a formatted text email message from a rendered html template (page)"
    soup = BeautifulSoup(html, 'html.parser')
    # Ignore anything in head
    body, text = soup.body, []
    if body is None:
	return ""
    else:
	    for element in body.descendants:
	        # We use type and not isinstance since comments, cdata, etc are subclasses that we don't want
	        if type(element) == NavigableString:
	            # We use the assumption that other tags can't be inside a script or style
	            if element.parent.name in ('script', 'style'):
	                continue
	            elif element.parent.name == 'a':
	                # replace link text with the link
	                #text += [element.parent['href']]
	                continue
	            # remove any multiple and leading/trailing whitespace
	            string = ' '.join(element.string.split())
	            if string:
	                if element.parent.name == 'p':
	                    # Add extra paragraph formatting newline
	                    string = '\n' + string
	                text += [string]
	    doc = '\n'.join(text) #.encode('utf-8')
	    return doc
