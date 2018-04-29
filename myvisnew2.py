import requests
import sqlite3
import pandas as pd		#Populating dataframes
import numpy as np
import plotly.plotly as py	#Using plotly api to build plots
import plotly
import plotly.graph_objs as go	#Using plotly grap objects to use inbuilt plotly graph types
import dash		
from dash.dependencies import Input, Output,Event	#Import event,input and output for calbacks
import dash_core_components as dcc
import dash_html_components as html
import time
import datetime


#Read sentiment data from the tweetdata database
def readSentimentData(data):
	con = sqlite3.connect("tweetdata.db")
	cur = con.cursor()
	cur.execute("SELECT * FROM polarity_table")
	rows = cur.fetchall()
	con.close()
	data.append(rows)	#Append data fetched into the data being returned



	
#Extract stock ticker and cryptocurrency data from the database
def extractData(df,axis_points):
	#dictionary of stocks and crypto considered for operation. This list can be extended to include more types
	seclist={'AAPL':'stock', 'GOOGL':'stock', 'BTC':'crypto', 'ETH':'crypto', 'XRP':'crypto'}
	
	conn = sqlite3.connect('marketdata.db')
	c = conn.cursor()
	for i in range(0,len(seclist)):
		c.execute('SELECT * FROM ' +seclist.keys()[i])
		df.append(pd.DataFrame(data = c.fetchall()))
		axis_points.append(df[i][0])
	conn.close()

#Fetch values from database into separate ticker and crypto Lists
def update_obd_values(apple, google, bitcoin, ether, ripple,value):
	df = list()
	axis_points = list()
	time_list = {'AAPL':0, 'ETH':1, 'GOOGL':2, 'BTC':3,  'XRP':4}
	extractData(df,axis_points)
	#Populate stocks with the complete data i.e. open,low,high and close while crypto will be populated with only price
	apple=(df[0])
	ether=(df[1][1]).tolist()
	google=(df[2])
	bitcoin=(df[3][1]).tolist()
	ripple = (df[4][1]).tolist()
	times = list()

	for i in range(0,len(time_list)):
		if time_list.keys()[i] == value:
			times = (axis_points[time_list.values()[i]]).tolist()
	#Return the data created
	return apple, google, bitcoin, ether, ripple,times

#Dashboard function to create the dashboard and register callback events
def dashnew():
	seclist={'AAPL':'stock', 'GOOGL':'stock', 'BTC':'crypto', 'ETH':'crypto', 'XRP':'crypto', 'SENTIMENT':'senti'}
	df = list()
	axis_points = list()
	#populate dataframe df and list axis points	
	extractData(df,axis_points)
	
	#Create a layout of the app which will be displayed
	app.layout = html.Div([
    	html.Div([
		html.H1('Real Time Stock and Cryptocurrencies')],
				style={'textAlign': 'center','verticalALign': 'top','font-size': '0.6em','color':"rgba(63,127,191,0.95)",'display': 'inline'
				       }),
		#Including some iamges to the dashboard
		html.Div([
		html.Img(src="http://gdurl.com/UwZT",
			style={
				    'height': '130px',
				    'float': 'right'
				}),
		html.Img(src="http://gdurl.com/eG4jl",
			style={
				    'height': '130px',
				    'float': 'left'
				})
		]),
		#Including a tab selection in the dashboard i.e. selecting a tab will show different data visualisation
		html.Div([	html.H2('Select a Tab to view the visualization')],
				style={'textAlign': 'center','font-size': '0.7em','color':"rgba(63,127,191,0.95)",'display': 'inline'
				       }),	
		html.Div([
		dcc.Tabs(
        tabs=[
            {'label': seclist.keys()[i],'value': i} for i in range(0, 6)
        ],
        value=0,
        id='tabs'
		)],style={'textAlign': 'center','verticalALign': 'middle','font-size': '1em','color':"rgba(63,127,191,0.95)",'display': 'inline'
				       }),
		html.Div(id='graphs', className='row'),

		#Including a interval component which handles real time update of data
		#this interval generates an event everytime timer crosses interval limit which would be captured by the callback function
		dcc.Interval(
        id='graph-update',
        interval=6000)
		], className="container",style={'width':'100%','margin-left':'5','margin-right':'5','max-width':50000, 'background-color':'rgb(127,178,76,0.5)'})
	
	


	#This is the main function which creates everything
	#1. initate a callback which gets registered. the output for this is the graphs, input would be the value of tab which is selected on the webpage
	#2. event would be the timer i.e. event generation when timer expired in interval component
	#3 every time timer expires or tab value is changed, an event is generated which is captured by callback, which calls the below program.
	
	@app.callback(Output('graphs','children'), [Input('tabs', 'value')],events=[dash.dependencies.Event('graph-update', 'interval')])
	
	#function to call when callback called
	#It takes value (tab value) as input and does logic based on the value	
	
	def display_content(value):
		
		#dictionary of inputs returned from tab selection and the names 
		time_list = {'AAPL':2, 'ETH':4, 'GOOGL':0, 'BTC':3,  'XRP':5, 'Sentiment':1}
		
		apple = list()
		google = list()
		bitcoin = list()
		ether = list()
		ripple = list()
		times = list()
		for i in range(0,len(time_list)):
			if time_list.values()[i] == value:
				keyValue = time_list.keys()[i]
		apple, google, bitcoin, ether, ripple,times = update_obd_values(apple, google, bitcoin, ether, ripple,keyValue)

		#If value (tab) is selected for apple
		if value == time_list['AAPL']:

			data = go.Ohlc(
				    x= times,
				    open= apple[1].tolist(),
				    high= apple[2].tolist(),
				    low= apple[3].tolist(),
				    close= apple[4].tolist(),
				    name = 'Apple'
					)
			data_name = 'Apple'
			minTime = min(data['x'])


		elif value == time_list['ETH']:

			data = go.Scatter(
				x=times,
				y=ether,
				name='Scatter'
				)
			data_name = 'Ether'
			minTime = min(times)


		elif value == time_list['GOOGL']:

			data = go.Ohlc(
				    x= times,
				    open= google[1].tolist(),
				    high= google[2].tolist(),
				    low= google[3].tolist(),
				    close= google[4].tolist(),
				    name = 'GOOGLE'
					)
			data_name = 'Google'
			minTime = min(times)


		elif value == time_list['BTC']:
			data = go.Scatter(
				x=times,
				y=bitcoin,
				name='Scatter'
				)
			data_name = 'Bitcoin'
			minTime = min(times)

		elif value == time_list['XRP']:
			data = go.Scatter(
				x=times,
				y=ripple,
				name='Scatter'
				)
			data_name = 'Ripple'
			minTime = min(times)

		#If tab for sentiment analysis is selected
		else:
			data =[]
			readSentimentData(data)
		
			data = np.array(data[0])
			
			datanew = go.Scatter(
					x=[i for i in range(100)],
					y=data[:,1],
					name='Scatter',
		            mode='markers',
		            opacity=0.7,
		            marker={
		                'size': 15,
		                'line': {'width': 0.5, 'color': 'white'}
		            }
					)
			data_name = 'Sentiment'

		#If value i.e. tab selected is for apple plot the following graph
		if value == time_list['AAPL']:
			return html.Div([
				dcc.Graph(
					id='graph',
					figure={
						'data': [data],
						#minTime,min(data['open'],max(data['open']
						'layout' : go.Layout(xaxis=dict(title = 'Time',rangeslider = dict(visible = False),range=['2017-10-03',max(data['x'])]),
					                                        yaxis=dict(title = 'Price',range=[140,190]),
					                                        title='{}'.format(data_name))
					}
				)
				])

		#If value i.e. tab selected is for Google plot the following graph
		elif value == time_list['GOOGL']:
					return html.Div([
						dcc.Graph(
							id='graph',
							figure={
								'data': [data],
								'layout' : go.Layout(xaxis=dict(title = 'Time',rangeslider = dict(visible = False),range=['2017-10-03',max(data['x'])]),
									                                yaxis=dict(title = 'Price',range=[900,1200]),
									                                title='{}'.format(data_name))
							}
						)
						])
		#else for cryptocurrencies plot the below graph
		elif value == time_list['BTC'] or value == time_list['XRP'] or value == time_list['ETH']:	
			return html.Div([
				dcc.Graph(
					id='graph',
					figure={
						'data': [data],
						'layout' : go.Layout(xaxis=dict(title = 'Time',showgrid=False,range=[minTime,max(data['x'])]),
					                                        yaxis=dict(title = 'Price',range=[min(data['y']),max(data['y'])]),
					                                        title='{}'.format(data_name))
					}
				)
			])
		#If value i.e. tab selected is for sentiment plot the following graph
		else:
			return html.Div([
					dcc.Graph(
						id='graph',
						figure={
							'data': [datanew],
							'layout' : go.Layout(xaxis=dict(title = 'Tweet Number',range=[0,100]),
					                                        yaxis=dict(title = 'Polarity',range=[-1.1,1.1]),
					                                        title='{}'.format(data_name))
						}
					)
				])


#Create an app
app = dash.Dash()

#call the function and run the web server
dashnew()
app.run_server(debug=True)

