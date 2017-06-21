from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from indexer import Searcher
import requests
from lxml.html import fromstring
import ipywidgets
import logging
from lang_proc import to_query_terms
import urllib2
import time
from base64 import b16decode
from bs4 import BeautifulSoup
from lang_proc import stem_and_tokenize_text,remove_stopwords
from datetime import datetime

app = Flask(__name__)
Bootstrap(app)
searcher = Searcher("indexes")

class SearchForm(Form):
	user_query = StringField('Looking for: ', validators=[DataRequired()])
	search_button = SubmitField("Search")

@app.route("/", methods=["GET", "POST"])
def index():
	search_form = SearchForm(csrf_enabled=False)
	if search_form.validate_on_submit():
		return redirect(url_for("search_results", query=search_form.user_query.data))
	return render_template("index.html", form=search_form)

@app.route("/search_results/<query>")
def search_results(query):
	#bach n7ssbo le temps de reponse :D
	start_time = datetime.now()
	#n7eydo dok le stops words francais w anglais :D
	query1 = remove_stopwords(query)
	query_terms = to_query_terms(query1)
	#app.logger.info("Requested [{}]".format(" ".join(map(str, query_terms))))
	docids = searcher.find_documents_AND(query_terms)
	total_doc_num = 0
    	for docid in docids:
    		total_doc_num += 1
	urls = [searcher.get_url(docid) for docid in docids]
	#for url in urls:
	#	r = requests.get(url)
	#	html_content = r.text
	#	soup = BeautifulSoup(html_content,'lxml')
	#	titles[url] = soup.title.string
	#	time.sleep(2)
	#titles = "abcdef"	
	texts = [searcher.generate_snippet(query_terms, docid) for docid in docids]
	finish_time = datetime.now()
	return render_template("search_results.html", processing_time=(finish_time-start_time),total_doc_num=total_doc_num,query=query, titles_texts_and_urls=zip(urls,texts))

if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0')


