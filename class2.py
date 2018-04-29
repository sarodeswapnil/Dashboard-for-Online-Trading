import tweepy
import time
import pprint
from tweepy import OAuthHandler
from tweepy import streaming
from tweepy.streaming import StreamListener
from tweepy import Stream
import textblob
from textblob import TextBlob
import nltk 
from nltk.corpus import state_union 
from nltk import word_tokenize 
from nltk.util import ngrams 
import csv
import sklearn
from pyroc import ROCData
import numpy as np
from nltk.probability import *
from nltk.corpus import stopwords
import matplotlib.pyplot as plt

# Bring in the default English NLTK stop words
stoplist = stopwords.words('english')

# Define additional stopwords in a string
additional_stopwords = "@%"

additional_stopwords = additional_stopwords.lower()

# Split the the additional stopwords string on each word and then add
# those words to the NLTK stopwords list
stoplist += additional_stopwords.split()
pos_tweets=[]
neg_tweets=[]

with open('test1.csv','rb') as fin: 
    # csv.DictReader uses first line in file for column headings by default
    dr = csv.DictReader(fin) # comma is default delimiter
    print dr
    for i in dr:
	    temptw=''
	    #To check and remove words from the stoplist
	    for word in str(i['tweet']).split():
		if word not in stoplist:
		    temptw = temptw + word + ' '  
	    pos_tweets.append([temptw, i['sentiment']])
with open('test0.csv','rb') as fin: 
    # csv.DictReader uses first line in file for column headings by default
    dr = csv.DictReader(fin) # comma is default delimiter
    print dr
    for i in dr:
	    temptw=''
	    #To check and remove words from the stoplist
	    for word in str(i['tweet']).split():
		if word not in stoplist:
		    temptw = temptw + word + ' '  
	    neg_tweets.append([temptw, i['sentiment']])

tweets = []
#Create consolidated list of tweets
for (words, sentiment) in pos_tweets + neg_tweets:
    words_filtered = [e.lower() for e in words.split() if len(e) >= 3]
    tweets.append((words_filtered, sentiment))
    

def get_words_in_tweets(tweets):
	all_words = []
	for (words, sentiment) in tweets:
        	all_words.extend(words)
        return all_words

def get_word_features(wordlist):
	wordlist = nltk.FreqDist(wordlist)
	word_features = wordlist.keys()
	return word_features


word_features = get_word_features(get_words_in_tweets(tweets))

def extract_features(document):
	document_words = set(document)
	features = {}
	for word in word_features:
	        features['contains(%s)' % word] = (word in document_words)
	return features




def calc_positive_rates(roc_table, target):	
	threshold = 0.0
	#arrays to store true positive and false positive rates	
	tpr= []
	fpr = []
	
	for i in range(len(roc_table)):
		#arrays to store count of true positives and false positives		
		true_pos = []
		false_pos = []
		threshold = roc_table[i][0]
		for j in range(0,len(roc_table)):
			if roc_table[j][0] >= threshold:
				if roc_table[j][1]==1:
					true_pos.append(1)
				else:
					false_pos.append(1)
		#true positive rate = number of true positives / actual positives
		tpr.append(float(sum(true_pos))/float(sum(target)))
		#false positive rate = number of false positives / actual negatives
		fpr.append(float(sum(false_pos))/float(len(target)-sum(target)))

	return tpr, fpr

def print_roc(tpr, fpr):
	#print the ROC curve using the true positive rate and false positive rate
	plt.plot(fpr, tpr,color='blue')
	plt.xlabel("False Positive Rate")
	plt.ylabel("True Positive Rate")
	plt.title("Curve of True Positive Rate vs False Positive Rate")
	
	plt.gca().set_xlim([-0.01,1.01])
	plt.gca().set_ylim([-0.01,1.01])
	plt.plot(plt.gca().get_xlim(),plt.gca().get_ylim(),color = 'green')
	plt.show()

training_set = nltk.classify.apply_features(extract_features, tweets)

#Create a Naive Bayes classifier using the NLTK library
classifier = nltk.NaiveBayesClassifier.train(training_set)


# the feature that show most info...we can build a chart to show this
#print classifier.show_most_informative_features(32)

testdata=[]
prob_array=[]
with open('test data.csv','rb') as fin: 
    # csv.DictReader uses first line in file for column headings by default
    dr = csv.DictReader(fin) # comma is default delimiter
    for i in dr:
	    temptw=''
	    #To check and remove words from the stoplist
	    for word in str(i['tweet']).split():
		if word not in stoplist:
		    temptw = temptw + word + ' '  
	    testdata.append([temptw, i['sentiment']])
	    #print classifier.classify(extract_features(temptw.split()))
roc_table=[]
target=[]
for i in range(len(testdata)):
	#create ROC Table using probabilities from the classifier
	roc_table.append([])
	roc_table[i].append(classifier.prob_classify(extract_features(str(testdata[i][0]).split())).prob('1'))
	roc_table[i].append(int(testdata[i][1]))
	target.append(int(testdata[i][1]))
#sort the ROC table in increasing order of probabilities
roc_table = sorted(roc_table, key = lambda x:(x.__getitem__(0)))

tpr, fpr = calc_positive_rates(roc_table, target)
print_roc(tpr,fpr)


