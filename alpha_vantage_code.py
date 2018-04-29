import requests
import alpha_vantage
import pprint
pp = pprint.PrettyPrinter()
import sqlite3
#import cryptocompare
import time
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
		y=(data["text"]).lower()
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


def populateDB():
	API_URL = "https://www.alphavantage.co/query"

	seclist={'AAPL':'stock', 'GOOGL':'stock', 'BTC':'crypto', 'ETH':'crypto', 'XRP':'crypto'}



	conn = sqlite3.connect('marketdata.db')
	c = conn.cursor()

	listToPush = list()
	for stockname in seclist:
		listToPush = []
		print stockname

		if seclist[stockname] == 'stock':
			#continue
			data = {
				"function": "TIME_SERIES_INTRADAY",	#TIME_SERIES_DAILY
				"symbol": stockname,
				"outputsize": "full",
				"interval": "1min",
				"apikey": "N7EK7OL60O781XV8"
				}
			response = requests.get(API_URL, data)

		else:
			response = requests.get("https://min-api.cryptocompare.com/data/histominute?fsym="+stockname+"&tsym=USD&limit=6000&aggregate=3&e=CCCAGG")
			pp.pprint(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(response.json()[u'Data'][0][u'time'])))
		

		
		x = response.json()
		#'''
		if seclist[stockname] == 'stock':
			#continue
			for key in x[u'Time Series (1min)'].keys():
				listToPush.append(key)
				listToPush.append(float(x[u'Time Series (1min)'][key][u'1. open']))
				listToPush.append(float(x[u'Time Series (1min)'][key][u'2. high']))
				listToPush.append(float(x[u'Time Series (1min)'][key][u'3. low']))
				listToPush.append(float(x[u'Time Series (1min)'][key][u'4. close']))
				listToPush.append(int(x[u'Time Series (1min)'][key][u'5. volume']))
			
				#print listToPush
			
				c.execute('INSERT or Replace INTO ' +stockname+' VALUES(?,?,?,?,?,?)',listToPush)
				listToPush = []
		else:
			for key in x[u'Data']:
				listToPush.append(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(key[u'time'])))
				listToPush.append(float(key[u'open']))
				listToPush.append(float(key[u'high']))
				listToPush.append(float(key[u'low']))
				listToPush.append(float(key[u'close']))
				listToPush.append(int(key[u'volumeto']))
			
				#print listToPush
			

				c.execute('INSERT or Replace INTO ' +stockname+' VALUES(?,?,?,?,?,?)',listToPush)
				listToPush = []	
		'''
		#initial popuation 
		if seclist[stockname] == 'stock':
			for key in x[u'Time Series (Daily)'].keys():
				listToPush.append(key)
				listToPush.append(float(x[u'Time Series (Daily)'][key][u'1. open']))
				listToPush.append(float(x[u'Time Series (Daily)'][key][u'2. high']))
				listToPush.append(float(x[u'Time Series (Daily)'][key][u'3. low']))
				listToPush.append(float(x[u'Time Series (Daily)'][key][u'4. close']))
				listToPush.append(int(x[u'Time Series (Daily)'][key][u'5. volume']))
			
				#print listToPush
			
				c.execute('INSERT or Replace INTO ' +stockname+' VALUES(?,?,?,?,?,?)',listToPush)
				listToPush = []
		else:
			for key in x[u'Data']:
				listToPush.append(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(key[u'time'])))
				listToPush.append(float(key[u'open']))
				listToPush.append(float(key[u'high']))
				listToPush.append(float(key[u'low']))
				listToPush.append(float(key[u'close']))
				listToPush.append(int(key[u'volumeto']))
			
				#print listToPush

				c.execute('INSERT or Replace INTO ' +stockname+' VALUES(?,?,?,?,?,?)',listToPush)
				listToPush = []
		'''
		
		c.execute('SELECT * FROM ' +stockname)
		pp.pprint(c.fetchall())  

	conn.commit()
	conn.close()	

while(1):
	populateDB()

	#This handles Twitter authetification and the connection to Twitter Streaming API
	l = StdOutListener()
	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	stream = Stream(auth, l)

	# specify which s
	stream.filter(track=['bitcoin'])

	time.sleep(5)




#pp.pprint(x[u'Time Series (15min)'].keys())
#print x[u'Meta Data'][u'3. Last Refreshed']

