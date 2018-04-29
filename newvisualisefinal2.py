import requests
import matplotlib.pyplot as plt
import alpha_vantage
import pprint
pp = pprint.PrettyPrinter()
import sqlite3
import pandas as pd
import plotly.plotly as py
import plotly
import dash
from dash.dependencies import Input, Output,Event
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

app = dash.Dash('crypto')


apple = list()
google = list()
bitcoin = list()
ether = list()
ripple = list()
times = list()

data_dict={'AAPL':apple, 'GOOGL':google, 'BTC':bitcoin, 'ETH':ether, 'XRP':ripple}

def extractData(df,axis_points):
	seclist={'AAPL':'stock', 'GOOGL':'stock', 'BTC':'crypto', 'ETH':'crypto', 'XRP':'crypto'}
	
	conn = sqlite3.connect('marketdata.db')
	c = conn.cursor()

	for i in range(0,len(seclist)):
		c.execute('SELECT * FROM ' +seclist.keys()[i])
		df.append(pd.DataFrame(data = c.fetchall()))
		#print 'Stock name : ' , seclist.keys()[i]
		axis_points.append(df[i][0])
	conn.close()

def update_obd_values(apple, google, bitcoin, ether, ripple,value):
	df = list()
	axis_points = list()
	time_list = ['AAPL', 'ETH', 'GOOGL', 'BTC',  'XRP']
	extractData(df,axis_points)
	apple=(df[0])
	ether=(df[1][1]).tolist()
	google=(df[2])
	bitcoin=(df[3][1]).tolist()
	ripple = (df[4][1]).tolist()
	times = list()
	for i in range(0,len(time_list)):
		if time_list[i] == value:
			#print 'Value : ' ,time_list[i]
			times = (axis_points[i]).tolist()
	return apple, google, bitcoin, ether, ripple,times

#apple, google, bitcoin, ether, ripple,times = update_obd_values(apple, google, bitcoin, ether, ripple,times)
colors = {
		'background':'#111111'
			}

app.layout = html.Div([
    html.Div([
        html.H5('Real Time Stock and Cryptocurrencies')],
                style={'textAlign': 'center','color':"rgba(63,127,191,0.95)",'display': 'inline'
                       }),
		html.Img(src="http://gdurl.com/UwZT",
            style={
	                'height': '140px',
	                'float': 'right'
	            }),
		html.Div([
		html.Img(src="http://gdurl.com/eG4jl",
            style={
	                'height': '140px',
	                'float': 'left'
	            })
        ]),
    dcc.Dropdown(id='Stock_Crypto',
                 options=[{'label': s, 'value': s}
                          for s in data_dict.keys()],
                 value=['XRP','BTC','ETH'],
				 multi = True
                 ),
    html.Div(children=html.Div(id='graphs'), className='row'),
    dcc.Interval(
        id='graph-update',
        interval=60000),	#Refresh charts every 60 seconds
    ], className="container",style={'width':'100%','margin-left':5,'margin-right':5,'max-width':50000})



@app.callback(
    dash.dependencies.Output('graphs','children'),
    [dash.dependencies.Input('Stock_Crypto', 'value')],
    events=[dash.dependencies.Event('graph-update', 'interval')]
    )
def update_graph(data_names):
	graphs = []
	#print data_names
	#If no argument selected from dropdown menu
	if len(data_names) == 0:
		exit()
	crypto = ['ETH', 'BTC',  'XRP']		#list of cryptocurrencies
	if len(data_names)>2:
		class_choice = 'col s12 m6 l4'
	elif len(data_names) == 2:
		class_choice = 'col s12 m6 l6'
	else:
		class_choice = 'col l4'

	for data_name in data_names:
		print 'DataBase being used : ', data_name
		apple = list()
		google = list()
		bitcoin = list()
		ether = list()
		ripple = list()
		times = list()
		apple, google, bitcoin, ether, ripple,times = update_obd_values(apple, google, bitcoin, ether, ripple,data_name)
		dataset = list()	#repopulate dataset for each each input field
		
		time_list = ['AAPL', 'GOOGL', 'BTC', 'ETH', 'XRP']
		
		if data_name == 'BTC':
			dataset.append(bitcoin)
		elif data_name == 'ETH':
			dataset.append(ether)
		elif data_name == 'XRP':
			dataset.append(ripple)

		#if data_name == 'XRP':
		#print min(times)
		#print 'MIN : ', min(dataset[0])
		#print len(times)
		if data_name in crypto:
			data = go.Scatter(
				x=times,
				y=dataset[0],
				name='Scatter',
				#fill="tozeroy",
				#fillcolor="#6897bb"
				)
			minTime = min(times)
		elif data_name == 'AAPL':
			data = go.Ohlc(
				    x= times,
				    open= apple[1].tolist(),
				    high= apple[2].tolist(),
				    low= apple[3].tolist(),
				    close= apple[4].tolist(),
				    name = 'Apple'
					)			
			
			minTime = '2018-01-07'

		else:	
			data = go.Ohlc(
				    x= times,
				    open= google[1].tolist(),
				    high= google[2].tolist(),
				    low= google[3].tolist(),
				    close= google[4].tolist(),
				    name = 'GOOGLE'
					)
			
			
			minTime = '2018-01-07'
		
			

		if data_name in crypto:
			graphs.append(html.Div(dcc.Graph(
				id=data_name,
				animate=True,
				figure={'data': [data],'layout' : go.Layout(xaxis=dict(title = 'Time',range=[minTime,max(data['x'])]),
					                                        yaxis=dict(title = 'Price',range=[min(dataset[0]),max(dataset[0])]),
					                                        #margin={'l':50,'r':1,'t':45,'b':1},
					                                        title='{}'.format(data_name))}
				), className=class_choice))

		else:
			if data_name == 'AAPL':
				graphs.append(html.Div(dcc.Graph(
					id=data_name,
					animate=True,
					figure={'data': [data] ,'layout' : go.Layout(width = 600,height = 500,xaxis=dict(title = 'Time',rangeslider = dict(visible = False),range=[minTime,max(data['x'])]),
							                                    yaxis=dict(title = 'Price',range=[150,185]),
							                                    #margin={'l':50,'r':1,'t':45,'b':1},
							                                    title='{}'.format(data_name))}
					), className=class_choice))

			else:	
				graphs.append(html.Div(dcc.Graph(
					id=data_name,
					animate=True,
					figure={'data': [data] ,'layout' : go.Layout(width = 600,height = 500,xaxis=dict(title = 'Time',rangeslider = dict(visible = False),range=[minTime,max(data['x'])]),
							                                    yaxis=dict(title = 'Price',range=[1000,1200]),
							                                    #margin={'l':50,'r':1,'t':45,'b':1},
							                                    title='{}'.format(data_name))}
					), className=class_choice))
		
	return graphs



external_css = ["https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/css/materialize.min.css"]
for css in external_css:
    app.css.append_css({"external_url": css})

external_js = ['https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/js/materialize.min.js']
for js in external_css:
    app.scripts.append_script({'external_url': js})


if __name__ == '__main__':
    app.run_server(debug=True)
