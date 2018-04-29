#twittersentiment.py
# we download the dependecies for the script
import json 
import sqlite3
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
import requests
from collections import Counter
from nltk.corpus import stopwords

# create lists that we will be populating later

bitcoin_tweet_data =[]
etherium_tweet_data =[]
sentiment_bitcoin =[]
sentiment_etherium  = []
# we set a starting point for the polarity for bitcoin and etherium tweets
polarity_bitcoin=0.0
polarity_etherium=0.0

# Bring in the default English NLTK stop words
stoplist = stopwords.words('english')

# Define additional stopwords in a string
additional_stopwords = """rt i @%"""

additional_stopwords = additional_stopwords.lower()

# Split the the additional stopwords string on each word and then add
# those words to the NLTK stopwords list
stoplist += additional_stopwords.split()

# enter the identifier for Twitter data.
# we enter details that will be picked up every time we intialize twitter.

consumer_key = 'zlVV6TY5X4b9av2ljjHBL42pT'
consumer_secret = 'qmsmK5T9e2iMTBguiBzyN2zeGxMnxiV1Af3aSge7c3KIMyNiW0'
access_token ='71796681-p0g4WfYoHo59oQfGFvj6tFaWK138Qa2JSwUueO79C'
access_token_secret ='3flfruHjLCSxklPJhcBVV2F4eMp7kJrA0VYo2O8p7VGEw'

# authorise your credentials via Auth Handler
auth = OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


# using the stream option we are able to pull in real time tweets. 

class StdOutListener(StreamListener):
    # we define data that is loaded from the twitter feed.
    
    def on_data(self, data):
       etherium ='0'
       ctr1=0
       # save the data to top5.json file in the append format 
       with open("top5.json" ,"a") as f:
            f.write(data)
            f.close()
            
       # read data from the json file .
       # discard the tweet data and only consider the text part of it
       # clean data by removing stoplist and other custom definition 
       with open("top5.json" ,"r") as f:
             for line in f:
                  y=(json.loads(line)["text"]).lower()
                  clean_tweet =[ word for word in y.split() if word not in stoplist]
                  
                  z=Counter(clean_tweet)
                  rejoin_tweet= ' '.join(clean_tweet)
                  
                  # evaluate which tweet belongs to the bitcoin cluster and which belongs to the ether cluster
                  
                  if z['bitcoin']+z['btc']>=z['ether']+z['ethereum']+z['etc']:
                      bitcoin_tweet_data.append(rejoin_tweet)
                      bitcoin = rejoin_tweet
                      
                    
                  else:
                      etherium_tweet_data.append(rejoin_tweet)
                      etherium = rejoin_tweet
                  
                  # using Textblob to get sentiment into a database using sqlite
                  
		  if TextBlob(bitcoin).sentiment.polarity !=0.00:
		          con = sqlite3.connect("tweetdata.db")
			  cur = con.cursor()
		          cur.execute("INSERT OR REPLACE INTO polarity_table (twid, pol) VALUES (?,?)",[ctr1,TextBlob(bitcoin).sentiment.polarity])
			  con.commit()
			  con.close()
			  ctr1=(ctr1+1)%100
       return True     
     # to display error message   
    def on_error(self, status):
        print status
        
     # this helps us select the timeout that we want for the entire code. 
    def select(self, timeout=1):
        return True

if __name__ == '__main__':

    #This handles Twitter authetification and the connection to Twitter Streaming API
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)

    # specify which s
    stream.filter(track=['bitcoin'])


