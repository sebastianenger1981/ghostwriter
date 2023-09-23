# -*- coding: utf-8 -*-
#!/usr/bin/env python
import os
import re
#import uuid
#import string
#import numpy as np
#import gensim
#import nltk
import os, sys
import time
import json
import MySQLdb as mdb
from MySQLdb import escape_string
import sys, unicodedata, re
from pprint import pprint  # pretty-printer
from pprint import PrettyPrinter
pp=PrettyPrinter(indent=7)

from collections import deque
from collections import namedtuple

from pprint import pprint  # pretty-printer
from pprint import PrettyPrinter
pp=PrettyPrinter(indent=7)

import math
from textblob import TextBlob as tb
from textblob_de import TextBlobDE as tbde

import spacy  # See "Installing spaCy"

from nltk.corpus import stopwords
from stop_words import get_stop_words

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words as stopW

from textblob_de.packages import pattern_de as pd

import spacy  # See "Installing spaCy"

"""
Author: Sebastian Enger, M.Sc.
Date: 2023-09-22
Topic: Simplify Sentences for Ghostwriter Artikelschreiber.com and AI Text Generator http://www.unaique.net/
Web: http://www.unaique.net/ - http://www.artikelschreiber.com/

SEO Optimizer: Ghost Writer - Hausarbeiten schreiben mit KI|http://www.artikelschreiber.com/
SEO Tool: SEO Optimizer for Content Writing with Strong AI|http://www.artikelschreiber.com/en/
English ArtikelSchreiber Blog|http://www.unaique.net/blog/
ArtikelSchreiber Marketing Tools|http://www.artikelschreiber.com/marketing/
Text Generator deutsch - KI Text Generator|http://www.unaique.net/	
CopyWriting: Generator for Marketing Content by AI|http://www.unaique.net/en/
Recht Haben - Muster und Anleitung fuer Verbraucher|http://rechthaben.net/	
AI Writer|http://www.unaique.com/
"""

nlp 			= spacy.load('de')
nlp.max_length 	= 1000000

# https://www.tutorialspoint.com/How-to-trim-down-non-printable-characters-from-a-string-in-Python
# Get all unicode characters
stopwordsDEv2 	= stopW('german')
stopwordsDE 	= get_stop_words('de')
stop_wordsMyDE  = stopwords.words('german')

all_chars 		= (chr(i) for i in range(sys.maxunicode))

# Get all non printable characters
control_chars 	= ''.join(c for c in all_chars if unicodedata.category(c) == 'Cc')
# Create regex of above characters
control_char_re = re.compile('[%s]' % re.escape(control_chars))
re_pattern 		= re.compile(u'[^\u0000-\uD7FF\uE000-\uFFFF]', re.UNICODE)

nlp 			= spacy.load('de')
Token 			= namedtuple("Token", ["id", "form", "lemma", "plemma", "pos", "ppos", "feat", "pfeat", "head", "phead", "deprel", "pdeprel", "fillpred", "pred", "apreds"])
t               = Token

#os.system('cls' if os.name == 'nt' else 'clear')

def _is_wordlike(tok):
	return tok.orth_ and tok.orth_[0].isalpha()

def sentence_division_suppresor(doc):
	"""Spacy pipeline component that prohibits sentence segmentation between two tokens that start with a letter.
	Useful for taming overzealous sentence segmentation in German model, possibly others as well."""
	for i, tok in enumerate(doc[:-1]):
		if _is_wordlike(tok) and _is_wordlike(doc[i + 1]):
			doc[i + 1].is_sent_start = False
	return doc

nlp.add_pipe(sentence_division_suppresor, name='sent_fix', before='parser')

def encodeToLatin1(text):
	encResults  = text.encode('utf-8', "ignore")
	#encResults = text.encode('utf-8', "ignore")
	s_string	= str(encResults.decode('latin-1', "ignore"))
	#textv1 	= re_pattern.sub(u'\uFFFD', s_string)
	return s_string

def encodeToUTF8Adv(text):
	encResults 	= text.encode('utf-8', "ignore")
	#return str(encResults.decode('latin-1', "ignore"))
	s_string	= str(encResults.decode('utf-8', "remove"))
	#textv1 		= re_pattern.sub(u'\uFFFD', s_string)
	return s_string
	
#d = findIT(verb_lemmatized_org, verb_alt)
def findVerbTense(verb_lemma, verb_tense):
	# pd.conjugate(verb_neu, tense, person, singular, mood=stimmung)
	resList = []
	pers 	= [1,2,3]
	numb 	= [pd.SG, pd.PL]
	mood 	= [pd.INDICATIVE,pd.IMPERATIVE,pd.SUBJUNCTIVE]
	tens 	= [pd.PRESENT,pd.PAST]
	
	for t in tens:
		# tense -> präsenz oder past
		for m in mood:
		# Stimmung:
			for n in numb:
			#	# anzahl
				for p in pers:
					# personen
					#print(conjugate(verb_lema, t, p, n, mood=m))
					c = pd.conjugate(verb_lemma, t, p, n, mood=m)
					#print(c, " -> tense:", t, " person:", p, " mehrzahl:", n, " stimmung:", m)
					#print(c, " -> tense:", t, " person:", p, " mehrzahl:", n, " findmatchverb:", f_findVerb)
					#print(c == f_findVerb)
					if c is not None and c == verb_tense:
						#resList.append([c, t, p, n, m])
						tel = {'c':c, 't':t, 'p':p, 'n':n,'m':m}
						resList.append(tel)
	return resList

def conjugateVerb(verb_tense, verb_neu):
	if not isinstance(verb_tense, str):
		return False
	if not isinstance(verb_neu, str):
		return False
	
	nlp.max_length 	= len(verb_tense) + 1
	doc 			= nlp(verb_tense)
	for token in doc:
		#print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,token.shape_, token.is_alpha, token.is_stop)
		verb_lemma	= token.lemma_ 
	
	#verb_lemma	= treeTaggerLemmatizer(verb_tense)
	newlist		= findVerbTense(verb_lemma, verb_tense)
	vn			= verb_lemma
	
	for e in newlist:
		tense		= e['t']
		person		= e['p']
		singular	= e['n']
		stimmung	= e['m']
		
	#for ele in d:
	#	#for pele in ele:
	#	tense = ele[1]
	#	person = ele[2]
	#	singular = ele[3]
	#	stimmung = ele[4]
		neu = pd.conjugate(verb_neu, tense, person, singular, mood=stimmung)
		#print("Algorithmisch berechnete Zielform des 'Zielverbs':", neu)
		#print("Zielsatz:", "Ich "+neu+" den Weg entlang.")
		#vn=u""+neu+""
		vn	= neu
	return vn

def split_sentences(text):
	rList 			= list()
	nlp.max_length 	= len(text) + 1
	doc 			= nlp(text)	
	for sent in doc.sents:
		rList.append(str(sent))
	
	#return TAG_RE.sub('', text)
	#return re.split(r'(?<=[^A-Z].[.!?]) +(?=[A-Z])', text)#, re.MULTILINE)
	#####DER WAR DER BESTE: return re.split(r'(?<=[^A-Z\{\}].[.!?]) +(?=[A-Z])', text)#, re.MULTILINE)
	#return [s.strip() for s in re.split('[\.\?!]' , text) if s]
	return rList
	
def remove_control_chars(s):
	return control_char_re.sub('', s)

def getSynonyms(search):
	db 			= mdb.connect(host="localhost",user="root", passwd="rouTer99", db="UNAIQUE", use_unicode=True, charset="utf8mb4")
	cursor 		= db.cursor()
	search 		= str(search)
	search 		= remove_control_chars(search)
	search 		= re_pattern.sub(u'\uFFFD', search)
	search 		= search.encode('unicode_escape').decode('unicode_escape')
	search 		= search.replace("\"", "")
	search 		= search.replace("'", "")
	searchLen	= len(search)
	st			= set()
	returnData 	= list()
	
	try:
		#cursor.execute("SET NAMES 'utf8mb4'");
		#cursor.execute("SET CHARACTER SET utf8");
		# Execute the SQL command
		# Eventuell einbauen, dass Term Level nicht DERB oder VULGÄR ist (
		# SELECT synonym FROM `unaique_synonym_de` WHERE `meaning` = 'Fahrzeug' ORDER BY RAND() LIMIT 25
		
		sql 			= "SELECT synonym FROM `unaique_synonym_de` WHERE `meaning` = \""+search+"\" LIMIT 25;"
		#sql 			= "SELECT synonym FROM `unaique_synonym_de` WHERE `meaning` = \""+search+"\" ORDER BY RAND() LIMIT 25;"
		#sql = "SELECT DISTINCT term.word FROM term, synset, term term2 WHERE synset.is_visible = 1 AND synset.id = term.synset_id AND term2.synset_id = synset.id AND term2.word = \""+search+"\" AND term2.word NOT LIKE \"%)%\" AND term.word NOT LIKE \""+search+"\" LIMIT 12;"
		#args=[[search]]
		cursor.execute(sql)
		data			= cursor.fetchall()
		returnData 		= [x[0] for x in data]
		rTmp 			= set()
		for r in returnData:
			synLen = len(r)
			if searchLen > synLen and search != r:
				rTmp.add(r)
		
		#if len(rTmp) < 1:
		#	for r in returnData:
		#		rTmp.add(r)
				
		returnData 	= list(set(rTmp))
		#print(sql)
		#print(cursor._last_executed)
		#cursor.execute(sql, (text, b_text, score, lang))
		#db.commit()
	except mdb.Error as e:
		print("Error %d: %s" % (e.args[0],e.args[1]))
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, fname, exc_tb.tb_lineno)
		return returnData
	except:
		# Rollback in case there is any error
		db.rollback()
	# disconnect from server
	cursor.close()
	return sorted(returnData, key=len)

## String -> Sentence
def string2sentence(plain_s):
    """Parse the string with a dependency parser and return a Sentence."""
    """
	def fn_for_token(t):
		... t.id         # String
			t.form       # String
			t.lemma      # String
			t.plemma     # String
			t.pos        # String
			t.ppos       # String
			t.feat       # String
			t.pfeat      # String
			t.head       # String
			t.phead      # String
			t.deprel     # String
			t.pdeprel    # String
			t.fillpred   # String
			t.fillpred   # String
			t.apreds     # String
    """

    nlp.max_length 	= len(plain_s) + 1
    doc4431 = nlp(plain_s)
    return tuple(t(str(tt.i),
                                  tt.orth_,
                                  tt.lemma_,
                                  '_',
                                  tt.tag_,
                                  '_',
                                  '_',
                                  '_',
                                  str(tt.head.i),
                                  '_',
                                  tt.dep_.upper(),
                                  '_',
                                  '_',
                                  '_',
                                  '_') for tt in doc4431)

## Integer (generator Sentence) -> (generator Sentence)
def take_n(n, generator):
    """Take at most n items from the generator."""
    i = 0
    while i < n:
        try:
            yield next(generator)
            i += 1
        except StopIteration:
            raise StopIteration

## Sentence -> String
def s2string(s):
	"""Produce a one-line string with forms from s."""
	"""
	print("s2string:",type(s))
	if isinstance(s, str):
		return str(s)
	else:
		return " ".join(token.form for token in s)
	return str(s)
	"""
	return " ".join(token.form for token in s)

## Token Sentence -> Boolean
def head_of_deletable_subtree(t, s):
    """Produce True if token is the head of a deletable subtree of the sentence."""
    ## Followed [Cetinoglu et al. (2013)]
    DELETABLE_SUBTREES = ['AG', 'APP', 'DA', 'JU', 'MNR', 'MO', 'NG', 'PAR', 'PG', 'PH', 'PNC', 'RC', 'RE', 'SBP', 'UC', 'VO', 'NK']
	#t.pos = t.tag_
	#t.head = t.head.i
	#t.deprel = t.dep_.upper()
    if t.deprel in DELETABLE_SUBTREES:
        if t.deprel == 'NK':
            if t.pos in ['ADJA', 'ADJD', 'ADV', 'KOUS']:
                return True
            elif t.pos == 'NN' and s[int(t.head) - 1].pos == 'NN':  # TODO: consider adding a dummy ROOT at index 0
                                                                    # to each sentence and storing t.head as integer
                return True
            else:
                return False
        else:
            return True
    else:
        return False

## Sentence -> Sentence
def remove_all(s):
    """Remove all deletable subtrees."""
    orig = s
    for t in orig:
        if head_of_deletable_subtree(t, orig):
           s = remove_subtree_starting_with(t.id, s)
    return s

## String Sentence -> Sentence
def remove_subtree_starting_with(id, s):
    """Return a new sentence with token with given id and all its children removed."""
    shorter_s = s
    to_delete = [id]
    for id in to_delete:
        to_delete.extend(children(id, s))
        shorter_s = remove_t_with_id(id, shorter_s)
    return shorter_s
	
## Sentence Sentence -> (generator Sentence)
def one_subtree_shorter(s, original_s):
    """Generate sentences one deletable subtree shorter than s."""
    if not s:
         return original_s
    else:
        for t in s:
            #print("one_subtree:",head_of_deletable_subtree(t, original_s), t)
            if head_of_deletable_subtree(t, original_s):
                #yield remove_subtree_starting_with(t.id, s)
                return remove_subtree_starting_with(t.id, s)

## String Sentence -> Sentence
def remove_subtree_starting_with(id, s):
	"""Return a new sentence with token with given id and all its children removed."""
	shorter_s = s
	to_delete = [id]
	for id in to_delete:
		to_delete.extend(children(id, s))
		shorter_s = remove_t_with_id(id, shorter_s)
		#print("shortest():", s2string(shorter_s))
	
	return shorter_s

## String -> String
def get_id(complex_id):
	"""Return token id.
	ASSUME: - 'id' field of tokens is of the form "number_number", where the second number is actual token id.
	"""
	#pp.pprint(complex_id)
	#return complex_id.split('_')[1]
	return complex_id

## String Sentence -> (listof String)
def children(id, s):
    #Return id's of children of token with given id.
    #return [t.id for t in s if t.head == token.get_id(id)]
	return [t.id for t in s if t.head == get_id(id)]

## String Sentence -> Sentence
def remove_t_with_id(id, s):
    """Return a new sentence with token having id 'id' removed.
    ASSUME: - sentence actually contains the token with given id and id is unique
    """
    return tuple(t for t in s if t.id != id)

def removeStopwords(text):
	words	= list()
	a		= text.split()
	for t in a:
		if t.lower() in stopwordsDEv2:
			continue
		if t.lower() in stop_wordsMyDE:
			continue
		if t.lower() in stopwordsDE:
			continue
		if t in stop_wordsMyDE:
			continue
		if t in stopwordsDEv2:
			continue
		if t in stopwordsDE:
			continue
		if len(t)<1:
			continue
		
		if not t.isalnum():
			continue
	
		words.append(t)
	return " ".join(words)

def removeADJ_ADV(sent):
	if len(sent) < 1:
		return str("")
	
	nlp.max_length 	= len(sent) + 1
	doc321 			= nlp(sent)
	short			= str("")
	for token in doc321:
        #print(token.text, token.pos_, token.nbor().pos_)
		#print("token:", token.text)
		if (token.pos_ in ["ADJ"] and token.nbor().pos_ in ["ADJ"]):
			short += str("")
		elif (token.pos_ in ["ADJ"] and token.nbor().pos_ in ["NOUN"]):
			short += str("")
			#short += str(token.nbor().text) + str(" ")
		#	print("token short:", str(token.nbor().text))
		else:
			if (token.pos_ not in ["ADV"]):
				short += str(token.text) + str(" ")
			
	#print("orginal:", encodeToLatin1(str(sent)))
	#print("short  :", encodeToLatin1(str(short)))
	#print("################################")
	return str(short)

def sentenceUppercase(sS):
	sentence	= str("")
	shorter_s 	= str(sS)
	if len(shorter_s) > 0:
		firstchar 	= shorter_s[0]
		if firstchar == firstchar.upper():
			shorter_s = shorter_s.replace(" .",".")
			shorter_s = shorter_s.replace(" !","!")
			shorter_s = shorter_s.replace(" ?","?")
			shorter_s = shorter_s.replace(" ,",",")
			shorter_s = shorter_s.replace(" ;",";")
			return ' '.join(shorter_s.split())
		else:
			newSent	= str("")
			l		= shorter_s.split()
			count	= 0
			for word in l:
				if count == 0:
					word = word.capitalize()
				newSent+=str(word)+str(" ")
				count+=1
				
			newSent = newSent.replace(" .",".")
			newSent = newSent.replace(" !","!")
			newSent = newSent.replace(" ?","?")
			newSent = newSent.replace(" ,",",")
			newSent = newSent.replace(" ;",";")
			return ' '.join(newSent.split())
			
	sentence = sentence.replace(" .",".")
	sentence = sentence.replace(" !","!")
	sentence = sentence.replace(" ?","?")
	sentence = sentence.replace(" ,",",")
	sentence = sentence.replace(" ;",";")
	return ' '.join(sentence.split())

def synReplace(text):
	if len(text) < 1:
		return str("")
	
	nlp.max_length 	= len(text) + 1
	doc121211213 	= nlp(text)
	finalSent		= str("")
	
	for t in doc121211213:
	#for t in sent214:
		if t.pos_ in ["NOUN"] and len(t.text) >= 2:
			s1 = getSynonyms(t.text)
			if len(s1) >= 1:
				for b in s1:
					if len(b) > 0:
						ss=nlp(b)
						#print("Similarity:",t.similarity(ss),"\t:\t",encodeToLatin1(t.text),"\t->\t",b)
						mySyn = b
						if t.similarity(ss) > 0.65:		# cosine similarity of >0.7 is nearly equal words
							finalSent += str(mySyn)+str(" ")
							# exit the for b in s1 loop
							break
				finalSent += str(t.text)+str(" ")
			else:
				# if len(s1) >= 1:
				finalSent += str(t.text)+str(" ")
				
		elif t.pos_ in ["VERB"] and len(t.text) >= 2:
			s2 = getSynonyms(t.text)
			if len(s2) >= 1:
				for b in s2:
					if len(b) > 0:
						ss=nlp(b)
						#print("Similarity:",t.similarity(ss),"\t:\t",encodeToLatin1(t.text),"\t->\t",b)
						mySyn = b
						if t.similarity(ss) > 0.65:
							o = conjugateVerb(t.text, mySyn)
							finalSent += str(o)+str(" ")
							# exit the for b in s1 loop
							break
				finalSent += str(t.text)+str(" ")
			else:
				# if len(s2) >= 1:
				finalSent += str(t.text)+str(" ")
			
		else:
			finalSent += str(t.text)+str(" ")
	
	finalSent = finalSent.replace(" .",".")
	finalSent = finalSent.replace(" !","!")
	finalSent = finalSent.replace(" ?","?")
	return str(finalSent).rstrip()

def doLsaSummarizer1(text):
	#SENTENCES_COUNT= 3
	#if "en" in Language.lower():
	#	#LANGUAGE_DE = "german"
	#	LANGUAGE =	 "english"
	
	LANGUAGE 				= "german"
	textLen					= len(split_sentences(text))
	myFloatLen  			= float("{0:.5f}".format((textLen/100)*65)) # auf 70 % des Textes soll zusammengefasst werden
	SENTENCES_COUNT			= round(myFloatLen)
	parser 					= PlaintextParser.from_string(text, Tokenizer(LANGUAGE))
	myStopwordsDE			= list(stopwordsDEv2) + list(stopwordsDE) + list(stop_wordsMyDE)

	# or for plain text files
	# parser = PlaintextParser.from_file("document.txt", Tokenizer(LANGUAGE))
	stemmer 				= Stemmer(LANGUAGE)
	summarizer 				= Summarizer(stemmer)
	summarizer.stop_words 	= myStopwordsDE	#get_stop_words(LANGUAGE)
	summarizer.null_words 	= myStopwordsDE	# get_stop_words(LANGUAGE)
	#summarizer.bonus_words = [MainKeyword,SubKeywords]
	summarizer.stigma_words = myStopwordsDE
	
	contentText		= str("")
	s_count			= 0
	for sentence in summarizer(parser.document, SENTENCES_COUNT):
		#if s_count <= SENTENCES_COUNT:
		#s_count+=1
		contentText += str(sentence)+str(" ")
		
	contentText = contentText.replace(" .",".")
	contentText = contentText.replace(" !","!")
	contentText = contentText.replace(" ?","?")
	
	return contentText

def LIX(text):
	#http://www.readabilityformulas.com/the-LIX-readability-formula.php
	word_count 	= 1.0
	sent_count 	= 1.0
	
	text		= str(text)
	if len(text) > 0:
		words		= text.split(" ")
		word_count 	= float(len(words))
		sent_count1	= split_sentences(text)
		sent_count	= float(len(sent_count1))
		longwords 	= 0.0
		score 		= 0.0 
		if word_count > 0:
			for word in words:
				if len(word) >= 7:
					longwords += 1.0
			score = word_count / sent_count + float(100 * longwords) / word_count
		return float(score)
	return float(0.0)
	
def simplifySentences(text):	
	text2			= doLsaSummarizer1(text)
	nlp.max_length 	= len(text2) + 1
	doc 			= nlp(text2)

	finSents		= list()
	#print(len(text1.split(".")))
	#print()
	#print(len(text2.split(".")))

	for sent in doc.sents:
		#sentString 	= encodeToLatin1(str(sent))
		sentString 	= str(sent)
		sent0 		= removeADJ_ADV(sentString)	# Remove ADJ+NOUN, ADV, ADJ+ADJ
		s			= string2sentence(sent0)	# Apply Dependency Sentence Simplifier
		sS			= one_subtree_shorter(s, s)
		
		if sS is None:
			aB 		= str("")
			if len(sentString) > len(sent0):
				aB = str(sent0)
			else:
				aB = str(sentString)
			sS 	= string2sentence(aB)
			
		myText		= s2string(sS)
		sentSht 	= sentenceUppercase(myText)
		sentSht2	= synReplace(sentSht)
		
		if len(sentSht) <= len(sentSht2):
			#print("Winner is sentSht -> shortlen")
			finSents.append(sentSht)
		else:
			finSents.append(sentSht2)
		
		"""
		print("orginal 	:",sentString)
		print("org REPL	:",sent0)
		print("shortest	:",sentSht)
		print("shortest2	:",sentSht2)
		print("\t#######")
		print("org len :\t",len(sentString))
		print("shortlen:\t",len(sentSht))
		print("shortlen2:\t",len(sentSht2))
		if len(sentSht) <= len(sentSht2):
			print("\t#######")
			print("Winner is sentSht -> shortlen")
		print("\t#######")
		print("org LIX	:\t",LIX(sentString))
		print("short LIX:\t",LIX(sentSht2))
		print()
		"""
	return " ".join(finSents)

#https://stevenloria.com/tf-idf/
def tf(word, blob):
    return blob.words.count(word) / len(blob.words)

def n_containing(word, bloblist):
    return sum(1 for blob in bloblist if word in blob.words)

def idf(word, bloblist):
    return math.log(len(bloblist) / (1 + n_containing(word, bloblist)))

def tfidf(word, blob, bloblist):
    return tf(word, blob) * idf(word, bloblist)

text1 = '''\
Counter-Strike-Erfinder ging leer aus - Dumm gelaufen: »Ich könnte heute Millionär sein«
Der als »Gooseman« bekannte Erfinder von Counter-Strike, Minh Le, beklagt im GameStar-Interview sein schlechtes Timing beim Verlassen von Entwickler Valve, das ihn um die millionenschweren Früchte für seine Arbeit an der erfolgreichen Half-Life-Mod gebracht hat.

Minh Le, besser bekannt als Gooseman, erfand vor 20 Jahren Counter-Strike. Doch der Erfolg von CS hat ihm keinen Reichtum beschert. Immerhin: Seine damaligen Studiengebühren konnte er dank des Deals mit Valve abbezahlen.Minh Le, besser bekannt als Gooseman, erfand vor 20 Jahren Counter-Strike. Doch der Erfolg von CS hat ihm keinen Reichtum beschert. Immerhin: Seine damaligen Studiengebühren konnte er dank des Deals mit Valve abbezahlen.

Wenn einer die weltweit erfolgreichste und in ihren unterschiedlichen Versionen über 30 Millionen Mal verkaufte Mod entwickelt, möchte man meinen, dass dieser Mensch auch wirtschaftlich von diesem globalen Siegeszug profitiert. Für Minh Le, der zusammen mit Jess Cliffe  aus der Taufe hob, war dies jedoch nicht so:  verrät der als »Gooseman« bekannte Modder, dass er mit CS nicht reich geworden ist.

Am meisten bedauere ich wohl, dass ich nicht mehr finanzielle Vorteile aus Counter-Strike gezogen habe. Ich arbeitete rund sechs Jahre bei Valve und ging 2006 zur falschen Zeit, denn wäre ich länger geblieben, hätte ich Millionär sein können - Steam wurde so erfolgreich für die Firma.

Minh Le und sein Partner Jess Cliffe nahmen ihm Jahr 2000 die Arbeit bei Valve auf; da hatte die Firma gerade das bereits in der Beta sehr erfolgreiche Counter-Strike aufgekauft. Minh Le, , bedauert im Rückblick seine Naivität bei den Verhandlungen über Gehalt und Tantiemen. Bis heute erhält Le keinen Anteil an den immensen Gewinnen, welche die Marke Counter-Strike (aktuell in der Variante ) für Steam-Besitzer Valve generiert.

Wenn ich länger verhandelt hätte, wäre sicher ein besserer Deal dabei rausgekommen. Aber zu der Zeit war ich Anfang zwanzig und wusste nichts vom Business. Ich war total ehrfürchtig und wollte nichts riskieren, also sagte ich mir: Nimm, was immer sie dir bieten.

Ob Jess Cliffe, der nach Minh Les Abschied 2006 bei Valve blieb, den besseren Deal bekommen hat, bleibt indes fraglich: Cliffe wurde im Februar 2018  beurlaubt.\
'''
	
s=simplifySentences(text1)
print(encodeToUTF8Adv(s))
print()
print(encodeToLatin1(s))
print()
print("LIX ORG:",LIX(text1))
print("LIX SHT:",LIX(s))


