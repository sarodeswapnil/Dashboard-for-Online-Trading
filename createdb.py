import sqlite3
import requests
import alpha_vantage
import json
import csv



def createdb(seclist):
	con = sqlite3.connect("marketdata.db")
	cur = con.cursor()
	for name in seclist:
		createcom = "CREATE TABLE IF NOT EXISTS "+name+" (timestamp datetime not null primary key, open float, high float, low float, close float, volume int);"
		cur.execute(createcom) 
	

		with open(name+'.csv','rb') as fin: # `with` statement available in 2.5+
		    # csv.DictReader uses first line in file for column headings by default
		    dr = csv.DictReader(fin) # comma is default delimiter
		    print dr
		    to_db = [(i['timestamp'], i['open'], i['high'], i['low'], i['close']) for i in dr]
		#insert data into database
		cur.executemany("INSERT INTO "+name+" (timestamp, open, high, low, close) VALUES (?, ?, ?, ?, ?);", to_db)
		cur.execute("SELECT * FROM "+name)
		rows = cur.fetchall()
 
	        for row in rows:
		     print(row)
	#confirm changes to the database
	con.commit()
	
	con.close()


seclist={'AAPL':'stock', 'GOOGL':'stock', 'BTC':'crypto', 'ETH':'crypto', 'XRP':'crypto'}
createdb(seclist)

