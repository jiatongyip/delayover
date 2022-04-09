# Run this app with `python app.py` and
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
orig_dest_arr_df = pd.read_csv("data/grp_orig_dest_arr.csv")
orig_dest_dep_df = pd.read_csv("data/grp_orig_dest_dep.csv")
carrier_arr_df = pd.read_csv("data/grp_carrier_arr.csv")
carrier_dep_df = pd.read_csv("data/grp_carrier_dep.csv")
deph_arr_df = pd.read_csv("data/grp_deph_arr.csv")
deph_dep_df = pd.read_csv("data/grp_deph_dep.csv")
arrh_arr_df = pd.read_csv("data/grp_arrh_arr.csv")
arrh_dep_df = pd.read_csv("data/grp_arrh_dep.csv")

with open("data/options_dict.txt", "r") as file:
    options_dict = eval(file.read())
with open("data/carrier_dict.txt", "r") as file:
    carrier_dict = eval(file.read())
# custom function
def get_distance(orig, dest):
    dist = airport_pairs[(airport_pairs.origin_airport_code == orig) &
    (airport_pairs.dest_airport_code == dest)]['distance_grp'].values[0]
    return dist


app.layout = html.Div([
    html.H1('Flight delay tabs!'),
    dcc.Tabs(
        children=[
            dcc.Tab(
                label='Predicted delay',
                children=html.Div(
                    children=[
                        html.H1("flight delay"),
                        html.H2(id='pred'),
                        html.H3("Select day of week:"),
                        dcc.RadioItems(id='dayofweek',
                            options=options_dict['dayofweek'],
                            # placeholder="Select day of week"
                            value = 1
                            ),
                        html.H3("Select year:"),            
                        dcc.Dropdown(id='year',
                            options=options_dict['year'],
                            value = 2013
                            ),
                        html.H3("Select month:"),            
                        dcc.Dropdown(id='month',
                            options=options_dict['month'],
                        #    placeholder = 'Apr'
                            value = 1
                            ),
                        html.H3("Select departure and arrival time:"),  
                        dcc.RangeSlider(
                            min=0, max=48, step=1,
                            marks={0: '0000', 6: '0600', 12: '1200', 18: '1800',
                                24: '0000', 30: '0600', 36: '1200', 42: '1800',
                                48: '0000',},
                            value=[4, 24], allowCross = False,
                            id='time_slider'),
                        html.Div(id='time_slider_output'),
                        html.H3("Select origin:"),            
                        dcc.Dropdown(id='orig', value = "ATL"),       
                        html.H3("Select destination:"),            
                        dcc.Dropdown(id='dest', value = "ABE"),  
                        html.H3("Select carrier:"),            
                        dcc.Dropdown(id='carrier',
                                    options=options_dict['carrier'],
                                    value = "AA")
                    ]
                )
            ),
        dcc.Tab(
            label='Same origin and destination', 
            children=html.Div(
                [html.H1(id = "orig_dest_line_title"
                    ),
                dcc.Graph(id='orig_dest_line')]
            )
        ),
        dcc.Tab(
            label='Same carrier', 
            children=html.Div(
                [html.H1(id = "carrier_line_title"
                    ),
                dcc.Graph(id='carrier_line')]
            )
        ),
        dcc.Tab(
            label='Same departure time', 
            children=html.Div(
                [html.H1(id = "deph_line_title"
                    ),
                dcc.Graph(id='deph_line')]
            )
        ),
        dcc.Tab(
            label='Same arrival time', 
            children=html.Div(
                [html.H1(id = "arrh_line_title"
                    ),
                dcc.Graph(id='arrh_line')]
            )
        )        
    ])
])
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
    arr_delay = "unknown"
    dep_delay = "unknown"
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
        arr_delay = delay['arr']
        dep_delay = delay['dep']

    return ("your departure will delay by " + dep_delay + 
    " mins,\nyour arrival will delay by " + arr_delay + " mins"
    )

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

# callback for dest orig time series plot
@app.callback(
    Output('orig_dest_line','figure'),
    Output('orig_dest_line_title','children'),
    Input('orig', 'value'),
    Input('dest', 'value')
    )
def update_orig_dest_plot(orig, dest):
    # handle callback error by retrying
    try:
        line_plot = px.line()
    except ValueError:
        line_plot = px.line()
    line_title = ""
    if all([orig, dest]):
        dep_subset = orig_dest_dep_df[(orig_dest_dep_df.origin_airport_code == orig) &
        (orig_dest_dep_df.dest_airport_code == dest)]
        dep_subset['yr_mon'] = dep_subset.yr.astype(str) + "-" + dep_subset.mon.map("{:02}".format)
        dep_subset['type'] = "departure"
        
        arr_subset = orig_dest_arr_df[(orig_dest_arr_df.origin_airport_code == orig) &
        (orig_dest_arr_df.dest_airport_code == dest)]
        arr_subset['yr_mon'] = arr_subset.yr.astype(str) + "-" + arr_subset.mon.map("{:02}".format)
        arr_subset['type'] = "arrival"
        
        df = pd.concat([dep_subset[["yr_mon", "mean", "type"]], 
                        arr_subset[["yr_mon", "mean", "type"]]])
        line_plot = px.line(
            df, x = "yr_mon", y = "mean", 
            color = "type", markers = True,
            labels = {'yr_mon': "time", 'mean': 'Mean delay (mins)'})
        line_title = "Let's look at the delays for flights from " + orig + " to " + dest + "!"

    return line_plot, line_title

@app.callback(
    Output('carrier_line','figure'),
    Output('carrier_line_title','children'),
    Input('carrier', 'value'),
    )
def update_carrier_plot(carrier):
    # handle callback error by retrying
    try:
        line_plot = px.line()
    except ValueError:
        line_plot = px.line()
    line_title = ""
    if carrier:
        dep_subset = carrier_dep_df[carrier_dep_df.u_carrier == carrier]
        dep_subset['yr_mon'] = dep_subset.yr.astype(str) + "-" + dep_subset.mon.map("{:02}".format)
        dep_subset['type'] = "departure"
        
        arr_subset = carrier_arr_df[carrier_arr_df.u_carrier == carrier]
        arr_subset['yr_mon'] = arr_subset.yr.astype(str) + "-" + arr_subset.mon.map("{:02}".format)
        arr_subset['type'] = "arrival"
        
        df = pd.concat([dep_subset[["yr_mon", "mean", "type"]], 
                        arr_subset[["yr_mon", "mean", "type"]]])
        line_plot = px.line(
            df, x = "yr_mon", y = "mean", 
            color = "type", markers = True,
            labels = {'yr_mon': "time", 'mean': 'Mean delay (mins)'})
        line_title = "Let's look at the delays for flights by " + carrier_dict[carrier] + "!"

    return line_plot, line_title

@app.callback(
    Output('deph_line','figure'),
    Output('deph_line_title','children'),
    [Input('time_slider', 'value')]
    )
def update_deph_plot(time_slider):
    # handle callback error by retrying
    try:
        line_plot = px.line()
    except ValueError:
        line_plot = px.line()
    line_title = ""
    if time_slider:
        dep, arr = time_slider
        dep = dep%24
        dep_subset = deph_dep_df[deph_dep_df.dep_hour == dep]
        dep_subset['yr_mon'] = dep_subset.yr.astype(str) + "-" + dep_subset.mon.map("{:02}".format)
        dep_subset['type'] = "departure"
        
        arr_subset = deph_arr_df[deph_arr_df.dep_hour == dep]
        arr_subset['yr_mon'] = arr_subset.yr.astype(str) + "-" + arr_subset.mon.map("{:02}".format)
        arr_subset['type'] = "arrival"
        
        df = pd.concat([dep_subset[["yr_mon", "mean", "type"]], 
                        arr_subset[["yr_mon", "mean", "type"]]])
        line_plot = px.line(
            df, x = "yr_mon", y = "mean", 
            color = "type", markers = True,
            labels = {'yr_mon': "time", 'mean': 'Mean delay (mins)'})
        line_title = "Let's look at the delays for flights departing at " + "{:02}".format(dep) + "00 hours!"

    return line_plot, line_title

@app.callback(
    Output('arrh_line','figure'),
    Output('arrh_line_title','children'),
    [Input('time_slider', 'value')]
    )
def update_arrh_plot(time_slider):
    # handle callback error by retrying
    try:
        line_plot = px.line()
    except ValueError:
        line_plot = px.line()
    line_title = ""
    if time_slider:
        dep, arr = time_slider
        arr = arr%24
        dep_subset = arrh_dep_df[arrh_dep_df.arr_hour == arr]
        dep_subset['yr_mon'] = dep_subset.yr.astype(str) + "-" + dep_subset.mon.map("{:02}".format)
        dep_subset['type'] = "departure"
        
        arr_subset = arrh_arr_df[arrh_arr_df.arr_hour == arr]
        arr_subset['yr_mon'] = arr_subset.yr.astype(str) + "-" + arr_subset.mon.map("{:02}".format)
        arr_subset['type'] = "arrival"
        
        df = pd.concat([dep_subset[["yr_mon", "mean", "type"]], 
                        arr_subset[["yr_mon", "mean", "type"]]])
        line_plot = px.line(
            df, x = "yr_mon", y = "mean", 
            color = "type", markers = True,
            labels = {'yr_mon': "time", 'mean': 'Mean delay (mins)'})
        line_title = "Let's look at the delays for flights arriving at " + "{:02}".format(arr) + "00 hours!"

    return line_plot, line_title    
if __name__ == '__main__':
    app.run_server(debug=True)
