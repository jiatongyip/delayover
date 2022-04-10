# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from pydoc import classname
from dash import Dash, dcc
import plotly.express as px
import pandas as pd
from datetime import date
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import Dash, html, dcc
import requests
from custom_functions import get_distance, get_yr_mon_dow, gen_line_plots, generate_pie_bar

app = Dash(__name__)
flask_url = 'http://127.0.0.1:5000/prediction'
external_stylesheets = ["https://fonts.googleapis.com/css2?family=Poppins&display=swap"]

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

# app
app.layout = html.Div(
    [
        html.Div(
            [html.H1('Flight Delay'),
            html.Img(src=app.get_asset_url('plane.svg')),
            html.P(html.I("Dashboard designed to predict and visualise airplane delays. You can check for flights delays that are coming from the same origin and destination , same carrier, same departure time and arrival time !"),style={"font-size":"12px","width":"650px","margin":"0 auto","padding":"10px 0"}),],
            style={"background-color":"#013E87","padding":"10px 0","color":"#fff","text-align":"center","font-family": 'Poppins,sans-serif',"font-size":"20px"}
        ),
        dcc.Tabs(className='custom-tabs-container', children=[
            dcc.Tab(
                className="custom-tab icon1",
                selected_className='custom-tab--selected',
                label='Predicted Delay',
                children=html.Div(
                    children=[
                        html.Div(html.H2(id='pred'), style={"font-size":"16px","padding-top":"10px"}),
                        html.Div(
                            [html.Div(html.H2("Select Date:"), style={"padding-right":"5px"}),
                            html.Div(
                                dcc.DatePickerSingle(
                                    id='date_picker',
                                    min_date_allowed=date(2013, 1, 1),
                                    max_date_allowed=date(2015, 12, 31),
                                    initial_visible_month=date(2014, 1, 1),
                                    date=date(2014, 1, 1),
                                    month_format = "MMMM YYYY",
                                    display_format = "DD-MMM-YYYY"
                                    ),
                                style={"padding":"10px 20px"}
                            ),
                            html.Div(html.H2("Select Origin:"), style={"padding-right":"5px"}),
                            html.Div(dcc.Dropdown(id='orig', value = "ATL"), style={"padding":"10px 20px","width":"100px"}),
                            html.Div(html.H2("Select Destination:"), style={"padding-left":"20px","padding-right":"5px"}),
                            html.Div(dcc.Dropdown(id='dest', value = "ABE"), style={"padding":"10px 20px","width":"100px"}),
                            html.Div(html.H2("Select Carrier:"), style={"padding-left":"20px","padding-right":"5px"}),
                            html.Div(dcc.Dropdown(
                                id='carrier', value = 'AA',
                                options=options_dict['carrier']),
                                style={"padding":"10px 20px","width":"200px"})
                            ], style={"display":"flex","padding":"10px 0","align-items":"center","font-family": 'Poppins,sans-serif'}
                        ),
                        html.Div(children=[], style={"display":"flex","padding":"10px 0","align-items":"center","font-family": 'Poppins,sans-serif'}),
                        html.H2("Select Departure and Arrival time:"), 
                        dcc.RangeSlider(
                            min=0, max=48, step=1,
                            marks={0: '0000', 6: '0600', 12: '1200', 18: '1800', 24: '0000', 30: '0600', 36: '1200', 42: '1800', 48: '0000',},
                            value=[4, 24], allowCross = False, id='time_slider'
                        ),
                        html.Div(id='time_slider_output',style={"font-size":"17px","font-family": 'Poppins,sans-serif'}),
                    ], style={"font-family": 'Poppins,sans-serif'},
                )
            ),
            dcc.Tab(className="custom-tab icon2", selected_className='custom-tab--selected', label='Same src and dest',  children=html.Div(
                [
                    html.H1(id = "orig_dest_line_title", style={"text-align":"center","padding-top":"10px"}),
                    dcc.Graph(id='orig_dest_line'),
                    html.H1(" Proportion of delays in 2012", style={"text-align":"center"}),
                    html.Div([
                        dcc.Graph(id='orig_dest_pie_dep'),
                        dcc.Graph(id='orig_dest_pie_arr'),
                    ], style={"display":"flex","width":"200px"}
                    ),
                    html.H1("Proportion of delays by months", style={"text-align":"center"}),
                    html.Div([
                        dcc.Graph(id='orig_dest_bar_dep'),
                        dcc.Graph(id='orig_dest_bar_arr'),
                    ], style={"display":"flex","width":"200px"})
                ]),
            ),
            dcc.Tab(className="custom-tab icon3", selected_className='custom-tab--selected', label='Same carrier', 
            children=html.Div(
                [html.Div(html.H1(id = "carrier_line_title"), style={"text-align":"center","padding-top":"10px"}),
                dcc.Graph(id='carrier_line'),
                html.Div(html.H1("Proportion of delays in 2012"), style={"text-align":"center"}),
                html.Div([
                    dcc.Graph(id='carrier_pie_dep'),
                    dcc.Graph(id='carrier_pie_arr'),
                ], style={"display":"flex","justify-content":"center","align-items":"center"}),
                html.Div(html.H1("Proportion of delays by months"), style={"text-align":"center"}),
                html.Div([
                    dcc.Graph(id='carrier_bar_dep'),
                    dcc.Graph(id='carrier_bar_arr'),
                ], style={"display":"flex","justify-content":"center","align-items":"center"}),])
            ),
            dcc.Tab(className="custom-tab icon4", selected_className='custom-tab--selected', label='Same departure time', 
            children=html.Div([
                html.Div(html.H1(id = "deph_line_title"), style={"text-align":"center"}),
                dcc.Graph(id='deph_line'),
                html.Div(html.H1("Proportion of delays in 2012"),style={"text-align":"center"}),
                html.Div([
                    dcc.Graph(id='deph_pie_dep'),
                    dcc.Graph(id='deph_pie_arr'),
                ], style={"display":"flex"}),
                html.Div(html.H1("Proportion of delays in 2012 by months"), style={"text-align":"center"}),
                html.Div([
                    dcc.Graph(id='deph_bar_dep'),
                    dcc.Graph(id='deph_bar_arr'),
                ], style={"display":"flex","justify-content":"center","align-items":"center"}),
            ])
            ),
            dcc.Tab(className="custom-tab icon5", selected_className='custom-tab--selected', label='Same arrival time', 
            children=html.Div([
                html.Div(html.H1(id = "arrh_line_title"), style={"text-align":"center"}),
                dcc.Graph(id='arrh_line'),
                html.Div(html.H1("Proportion of delays in 2012"),style={"text-align":"center"}),
                html.Div([
                    dcc.Graph(id='arrh_pie_dep'),
                    dcc.Graph(id='arrh_pie_arr'),
                ], style={"display":"flex"}),
                html.Div(html.H1("Proportion of delays by months"),style={"text-align":"center"}),
                html.Div([
                    dcc.Graph(id='arrh_bar_dep'),
                    dcc.Graph(id='arrh_bar_arr'),
                ], style={"display":"flex","justify-content":"center","align-items":"center"}),
            ])
            )        
        ])
    ]
)

# callback to get prediction
@app.callback(
    Output(component_id='pred',
    component_property='children'),
    Input('date_picker', 'date'),
    [Input('time_slider', 'value')],
    Input(component_id='orig',
    component_property='value'),
    Input(component_id='dest',
    component_property='value'),
    Input(component_id='carrier',
    component_property='value')
)
def get_pred(date_picker, time_slider, orig, dest, carrier):
    arr_delay = "unknown"
    dep_delay = "unknown"
    if all([date_picker, time_slider, orig, dest, carrier]):
        year, month, dayofweek = get_yr_mon_dow(date_picker)
        dep , arr = time_slider
        dep = dep%24
        arr = arr%24
        dist = get_distance(airport_pairs, orig, dest)
        param1 = {'yr': year, 'mon':month, 'day_of_week': dayofweek, 
        'dep_hour':dep,'arr_hour':arr, 'u_carrier': carrier,
        'origin_airport_code':orig, 'dest_airport_code': dest, 
        'distance_grp':dist}

        delay = requests.get(flask_url, params=param1).json()        
        arr_delay = delay['arr']
        dep_delay = delay['dep']

    return ["The departure will delay by " + dep_delay + " mins" , html.Br(),
    "The arrival will delay by " + arr_delay + " mins"]

# callback to display time selection
@app.callback(
    Output('time_slider_output', 'children'),
    [Input('time_slider', 'value')]
)
def update_output(value):
    if not value: 
        return ""
    dept, arr = value
    dept = "{:02d}".format(dept%24)
    arr = "{:02d}".format(arr%24)
    return ('Checking for departure time at ' + dept + '00 hours, checking for arrival time at ' + arr + '00 hours.')

# callback to change destination dropdown
@app.callback(
    Output('dest','options'),
    Input('orig','value')
)
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
    Input('dest','value')
)
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
        line_plot = gen_line_plots(orig_dest_dep_df, orig_dest_arr_df, [("origin_airport_code", orig), ("dest_airport_code", dest)])
        line_title = "Delays for flights from " + orig + " to " + dest + "!"

    return line_plot, line_title

@app.callback(
    Output('orig_dest_pie_dep','figure'),
    Output('orig_dest_pie_arr','figure'),
    Output('orig_dest_bar_dep','figure'),
    Output('orig_dest_bar_arr','figure'),   
    Input('orig', 'value'),
    Input('dest', 'value')
)
def update_orig_dest_pie(orig, dest):
    try:
        pie_plot_dep = px.pie()
        pie_plot_arr = px.pie()
        bar_plot_dep = px.bar()
        bar_plot_arr = px.bar()
    except ValueError:
        pie_plot_dep = px.pie()
        pie_plot_arr = px.pie()
        bar_plot_dep = px.bar()
        bar_plot_arr = px.bar() 

    if all([orig, dest]):
        pie_plot_dep, pie_plot_arr, bar_plot_dep, bar_plot_arr = generate_pie_bar(orig_dest_dep_df, orig_dest_arr_df, 
                                                                              [("origin_airport_code", orig), ("dest_airport_code", dest)])
    return pie_plot_dep, pie_plot_arr, bar_plot_dep, bar_plot_arr

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
        line_plot = gen_line_plots(carrier_dep_df, carrier_arr_df, [("u_carrier", carrier)])
        line_title = "Delays for flights by " + carrier_dict[carrier] + "!"

    return line_plot, line_title

@app.callback(
    Output('carrier_pie_dep','figure'),
    Output('carrier_pie_arr','figure'),
    Output('carrier_bar_dep','figure'),
    Output('carrier_bar_arr','figure'),   
    Input('carrier', 'value'),
)
def update_carrier_pie(carrier):
    try:
        pie_plot_dep = px.pie()
        pie_plot_arr = px.pie()
        bar_plot_dep = px.bar()
        bar_plot_arr = px.bar()
    except ValueError:
        pie_plot_dep = px.pie()
        pie_plot_arr = px.pie()
        bar_plot_dep = px.bar()
        bar_plot_arr = px.bar()        
    if carrier:
        pie_plot_dep, pie_plot_arr, bar_plot_dep, bar_plot_arr = generate_pie_bar(carrier_dep_df, carrier_arr_df, [("u_carrier", carrier)])
    return pie_plot_dep, pie_plot_arr, bar_plot_dep, bar_plot_arr

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
        line_plot =  gen_line_plots(deph_dep_df, deph_arr_df, [("dep_hour", dep)])
        line_title = "Delays for flights departing at " + "{:02}".format(dep) + "00 hours!"

    return line_plot, line_title

@app.callback(
    Output('deph_pie_dep','figure'),
    Output('deph_pie_arr','figure'),
    Output('deph_bar_dep','figure'),
    Output('deph_bar_arr','figure'),   
    [Input('time_slider', 'value')]
    )
def update_deph_pie(time_slider):
    try:
        pie_plot_dep = px.pie()
        pie_plot_arr = px.pie()
        bar_plot_dep = px.bar()
        bar_plot_arr = px.bar()
    except ValueError:
        pie_plot_dep = px.pie()
        pie_plot_arr = px.pie()
        bar_plot_dep = px.bar()
        bar_plot_arr = px.bar()        
    if time_slider:
        dep, arr = time_slider
        dep = dep%24
        pie_plot_dep, pie_plot_arr, bar_plot_dep, bar_plot_arr = generate_pie_bar(deph_dep_df, deph_arr_df, [("dep_hour", dep)])
    return pie_plot_dep, pie_plot_arr, bar_plot_dep, bar_plot_arr

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
        line_plot = gen_line_plots(arrh_dep_df, arrh_arr_df, [("arr_hour", arr)])
        line_title = "Delays for flights arriving at " + "{:02}".format(arr) + "00 hours!"

    return line_plot, line_title

@app.callback(
    Output('arrh_pie_dep','figure'),
    Output('arrh_pie_arr','figure'),
    Output('arrh_bar_dep','figure'),
    Output('arrh_bar_arr','figure'),   
    [Input('time_slider', 'value')]
)
def update_arrh_pie(time_slider):
    try:
        pie_plot_dep = px.pie()
        pie_plot_arr = px.pie()
        bar_plot_dep = px.bar()
        bar_plot_arr = px.bar()
    except ValueError:
        pie_plot_dep = px.pie()
        pie_plot_arr = px.pie()
        bar_plot_dep = px.bar()
        bar_plot_arr = px.bar()        
    if time_slider:
        dep, arr = time_slider
        arr = arr%24        
        pie_plot_dep, pie_plot_arr, bar_plot_dep, bar_plot_arr = generate_pie_bar(arrh_dep_df, arrh_arr_df, [("arr_hour", arr)])
    return pie_plot_dep, pie_plot_arr, bar_plot_dep, bar_plot_arr

if __name__ == '__main__':
    app.run_server(debug=True)
