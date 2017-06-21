# 3ndna two types of indexing
# forward indexing w inverted indexing
# l forward indexing howa hada :
# doc 1 = (learning,python,how,to)
# doc 2 = (learning,c++)
# l inverted indexing howa hada 
# learning -> (doc1,doc2)
# how -> (doc1)
# bach nfhem kter
# http://stackoverflow.com/questions/7727686/whats-the-difference-between-an-#inverted-index-and-a-plain-old-index
#
from base64 import b16decode
from util import *
import argparse
import os
import pickle
from util import *
from collections import defaultdict
from lang_proc import to_doc_terms
import ipywidgets

class Indexer(object):
	def __init__(self):
		self.inverted_index = dict()
		self.forward_index  = dict()
		self.url_to_id      = dict()
		self.doc_count      = 0

	def add_document(self, url, parsed_text):
		self.doc_count +=1
		assert url not in self.url_to_id
		current_id = self.doc_count
		self.url_to_id[url] = current_id
		self.forward_index[current_id] = parsed_text
		for position,term in enumerate(parsed_text):
			if term not in self.inverted_index:
				self.inverted_index[term] = []
			self.inverted_index[term].append((position,current_id))

	#def dump_file(self,o_dict,o_dir,file_path):
		

	def store_on_desk(self, index_dir):

		def dump_pickle_to_file(source,file_name):
			file_path = os.path.join(index_dir,file_name)
			pickle.dump(source,open(file_path,"w"))

		dump_pickle_to_file(self.inverted_index,"inverted_index")
		dump_pickle_to_file(self.forward_index,"forward_index")
		dump_pickle_to_file(self.url_to_id,"url_to_id")

class Searcher(object):
	def __init__(self, index_dir):
		self.inverted_index = dict()
		self.forward_index  = dict()
		self.url_to_id      = dict()

		def load_pickle_from_file(file_name):
			file_path = os.path.join(index_dir,file_name)
			dst = pickle.load(open(file_path))
			#print "LOADED ", len(dst)
			return dst

		self.inverted_index = load_pickle_from_file("inverted_index")
		#print "HAVE ", len(self.inverted_index)
		self.forward_index = load_pickle_from_file("forward_index")
		#print "HAVE ", len(self.forward_index)		
		self.url_to_id = load_pickle_from_file("url_to_id")
		#print "HAVE ", len(self.url_to_id)

		self.id_to_url = {v : k for k,v in self.url_to_id.iteritems()} 	
		
	# ghadi ndir hna function to get all the docs that contain dikchi dl user
	#def find_documents(self, query_words):
	#	return sum([self.inverted_index[word] for word in query_words],[])
	# 1) n9raw ga3 les words query [word1,word2,...]
	# 2) njbdo les docs li fihom les words li fl query [inverted index]
	# 3) ngado l'algo dyal snippets :D
	# 4) mansawch nchofo le min des docs li fihom ga3 les mots fl query dl user
	# 5) traitement dyal les stopwords :/
	
	def generate_snippet(self, query_terms , doc_id):
		query_terms_in_window = []
		best_window_len = 1000500 # l'infini ykon 7sen
		terms_in_best_window = 0
		best_window = []
		for pos, term in enumerate(self.forward_index[doc_id]):
			if term in query_terms:
				query_terms_in_window.append((term, pos))
				if len(query_terms_in_window) > 1 and query_terms_in_window[0][0] == term:
					query_terms_in_window.pop(0)
				current_window_len = pos - query_terms_in_window[0][1] +1
				tiw = len(set(map(lambda x: x[0],query_terms_in_window)))
				if tiw > terms_in_best_window or ( tiw == terms_in_best_window and current_window_len < best_window_len):
					terms_in_best_window = tiw
					best_window = query_terms_in_window[:]
					best_window_len = current_window_len

		#return self.forward_index[unicode(doc_id)][best_window[0][1]:(best_window[len(best_window) -1][1] + 1)]
		doc_len = len(self.forward_index[doc_id])
		snippet_start = max(best_window[0][1] - 8, 0)
		snippet_end = min(doc_len,best_window[len(best_window) -1][1] + 1 + 8)
		return [(term.full_word, term in query_terms) for term in self.forward_index[doc_id][snippet_start:snippet_end]]


	# find les terms kolhom bl AND
	def find_documents_AND(self, query_terms):
		query_term_count = defaultdict(set)
		for query_term in query_terms:
			for (pos, docid) in self.inverted_index.get(query_term, []):
				query_term_count[docid].add(query_term)

		return  [doc_id for doc_id,unique_hits in query_term_count.iteritems() if len(unique_hits) == len(query_terms)]

	# find les terms kolhom bl OR
	def find_documents_OR(self, query_terms):
		docids = set()
		for query_term in query_terms:
			for (pos, docid) in self.inverted_index.get(query_term, []):
				docids.add(docid)

		return docids

	def get_docs_text(self, doc_id):
		return self.forward_index[doc_id]

	def get_url(self, doc_id):
		return self.id_to_url[doc_id]
			

def create_index_from_dir(stored_docs_dir,index_dir):
	indexer = Indexer()
	for filename in os.listdir(stored_docs_dir):
		opened_file = open(os.path.join(stored_docs_dir,filename))
		doc_raw = html_to_text(opened_file.read())
		parsed_doc = to_doc_terms(doc_raw)
		indexer.add_document(b16decode(filename),parsed_doc)
	
	indexer.store_on_desk(index_dir)
		

def main():
	#logging.getLogger().setLevel(logging.INFO)
	#logging.info("some messgae")
	parser = argparse.ArgumentParser(description='Indexing')
	parser.add_argument("--stored_docs_dir", dest="stored_docs_dir", required=True)
	parser.add_argument("--index_dir", dest="index_dir", required=True)
	args = parser.parse_args()
	create_index_from_dir(args.stored_docs_dir,args.index_dir)
	#print args.start_url args.storage_dir
	

if __name__ == "__main__": #are you warking in from cml
	main()










