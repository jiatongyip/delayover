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
flask_url = 'http://127.0.0.1:5000/prediction'
  
#reading the data needed
airport_pairs = pd.read_csv("data/airport_pairs.csv")
with open("data/options_dict.txt", "r") as file:
    options_dict = eval(file.read())

# custom function
def get_distance(orig, dest):
    dist = airport_pairs[(airport_pairs.origin_airport_code == orig) &
    (airport_pairs.dest_airport_code == dest)]['distance_grp'].values[0]
    return dist

app.layout = html.Div(
    children=[
        html.H1("flight delay"),
        html.H2(id='pred'),
        html.H3("Select day of week:"),
        dcc.RadioItems(id='dayofweek',
            options=options_dict['dayofweek'],
            # placeholder="Select day of week"
            ),
        html.H3("Select year:"),            
        dcc.Dropdown(id='year',
            options=options_dict['year']),
        html.H3("Select month:"),            
        dcc.Dropdown(id='month',
            options=options_dict['month'],
        #    placeholder = 'Apr'
            ),
        html.H3("Select departure and arrival time:"),  
        dcc.RangeSlider(
            min=0, max=48, step=1,
            marks={0: '0000', 6: '0600', 12: '1200', 18: '1800',
                24: '0000', 30: '0600', 36: '1200', 42: '1800',
                48: '0000',},
            value=[3, 5], allowCross = False,
            id='time_slider'),
        html.Div(id='time_slider_output'),
        html.H3("Select origin:"),            
        dcc.Dropdown(id='orig'),       
        html.H3("Select destination:"),            
        dcc.Dropdown(id='dest'),  
        html.H3("Select carrier:"),            
        dcc.Dropdown(id='carrier',
                    options=options_dict['carrier']),                                   
    ]
)

# callback to get prediction
@app.callback(
    Output(component_id='pred',
    component_property='children'),
    Input(component_id='dayofweek',
    component_property='value'),
    Input(component_id='year',
    component_property='value'),
    Input(component_id='month',
    component_property='value'),
    [Input('time_slider', 'value')],
    Input(component_id='orig',
    component_property='value'),
    Input(component_id='dest',
    component_property='value'),
    Input(component_id='carrier',
    component_property='value')
)
def get_pred(dayofweek, year, month, time_slider, orig, dest, carrier):
    delay = "unknown"
    if all([dayofweek, year, month, time_slider, orig, dest, carrier]):
        dep , arr = time_slider
        dep = dep%24
        arr = arr%24
        dist = get_distance(orig, dest)
        param1 = {'yr': year, 'mon':month, 'day_of_week': dayofweek, 
        'dep_hour':dep,'arr_hour':arr, 'u_carrier': carrier,
        'origin_airport_code':orig, 'dest_airport_code': dest, 
        'distance_grp':dist}
        delay = requests.get(flask_url, params=param1).json()
    return "your predicted delay is " + delay + " mins"

# callback to display time selection
@app.callback(
    Output('time_slider_output', 'children'),
    [Input('time_slider', 'value')])
def update_output(value):
    if not value: 
        return ""
    dept, arr = value
    dept = "{:02d}".format(dept%24)
    arr = "{:02d}".format(arr%24)
    return ('You are departing at ' + dept + 
    '00 hours, arriving at ' + arr + '00 hours.')

# callback to change destination dropdown
@app.callback(
    Output('dest','options'),
    Input('orig','value'))
def update_dest_dd(orig):
    dest_options = airport_pairs.dest_airport_code.unique()
    if orig:
        dest_options = airport_pairs[airport_pairs.origin_airport_code == orig][
            "dest_airport_code"
        ].tolist()
    return sorted(dest_options)

# callback to change origin dropdown
@app.callback(
    Output('orig','options'),
    Input('dest','value'))

def update_orig_dd(dest):
    orig_options = airport_pairs.origin_airport_code.unique().tolist()
    if dest:
        orig_options = airport_pairs[airport_pairs.dest_airport_code == dest][
            "origin_airport_code"
        ].tolist()
    return sorted(orig_options)

if __name__ == '__main__':
    app.run_server(debug=True)
