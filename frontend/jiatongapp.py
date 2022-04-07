# Run this app with `python jiatongapp.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, dcc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_html_components as html
import dash_daq as daq
import requests

app = Dash(__name__)
url1 = 'http://127.0.0.1:5000/prediction'


app.layout = html.Div(
    children=[
        html.H1("flight delay"),
        html.H2(id='pred'),
        html.H3("Select day of week:"),
        dcc.Dropdown(id='dayofweek',
            options=[{'label':'Mon', 'value':1},
            {'label':'Tue','value':2},
            {'label':'Wed','value':3},
            {'label':'Thu','value':4},
            {'label':'Fri','value':5},
            {'label':'Sat','value':6},
            {'label':'Sun','value':7}],
            placeholder="Select day of week"),
        html.H3("Select year:"),            
        dcc.Dropdown(id='year',
            options=[2022, 2021, 2020, 2019, 2018, 2017, 
            2016, 2015, 2014, 2013, 2012],
            value = 2022),
        html.H3("Select month:"),            
        dcc.Dropdown(id='month',
            options=[
                {'label':'Jan', 'value':1},
                {'label':'Feb','value':2},
                {'label':'Mar','value':3},
                {'label':'Apr','value':4},
                {'label':'May','value':5},
                {'label':'Jun','value':6},
                {'label':'Jul','value':7},
                {'label':'Aug','value':8},
                {'label':'Sep','value':9},
                {'label':'Oct','value':10},
                {'label':'Nov','value':11},
                {'label':'Dec','value':12},                
            ],
            placeholder = 'Apr'),
        html.H3("Select arrival time:"),            
        dcc.Dropdown(id='arr',
            options=["{:02d}".format(h) for h in range(0,25)]),
        html.H3("Select departure time:"),            
        dcc.Dropdown(id='dep',
            options=["{:02d}".format(h) for h in range(0,25)]),           
    ]
)
@app.callback(
    Output(component_id='pred',
    component_property='children'),
    Input(component_id='dayofweek',
    component_property='value'),
    Input(component_id='year',
    component_property='value'),
    Input(component_id='month',
    component_property='value'),
    Input(component_id='arr',
    component_property='value'),
    Input(component_id='dep',
    component_property='value')
)
def get_pred(dayofweek, year, month, arr, dep):
    delay = "unknown"
    if all([dayofweek, year, month, arr, dep]):
        param1 = {'yr': year, 'mon':month, 'day_of_week': dayofweek, 
        'dep_hour':dep,'arr_hour':arr, 'u_carrier': 'AA',
        'origin_airport_code':'JFK', 'dest_airport_code': 'LAX', 
        'distance_grp':10}
        r1 = requests.get(url1, params=param1)
        delay = r1.json()
    return "your predicted delay is " + delay + " mins"


if __name__ == '__main__':
    app.run_server(debug=True)
