# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from pydoc import classname
from dash import Dash, dcc, html, no_update, dash_table
import plotly.express as px
import pandas as pd
import datetime
from datetime import date
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import requests
import plotly.graph_objs as go
from custom_functions import get_distance, get_yr_mon_dow, gen_line_plots, generate_pie_bar, update_delay_type, generate_pred_table, read_upload_data
import cufflinks as cf

flask_url = 'http://127.0.0.1:5000/prediction'
external_stylesheets = ["https://fonts.googleapis.com/css2?family=Poppins&display=swap"]
app = Dash(__name__, external_stylesheets=external_stylesheets)
api_key = 'da5e2fca806ad3496172e27dd9c53916'

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
good_example_df = pd.read_csv("data/good_example.csv")

with open("data/options_dict.txt", "r") as file:
    options_dict = eval(file.read())
with open("data/carrier_dict.txt", "r") as file:
    carrier_dict = eval(file.read())
with open("data/allowable_values.txt", "r") as file:
    allowable_values = eval(file.read())
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
                        html.Div([
                        html.H2(id='pred',style={"font-size":"24px"})
                        ],style={"padding":"5px","text-align":"center",
                        "width":"500px","margin":"30px auto","box-shadow": "0px 2px 6px rgba(0, 38, 83, 0.25)"}
                        ),
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
                        html.H2("Select Departure and Arrival time:",style={"font-family": 'Poppins,sans-serif',"padding-top":"10px"}), 
                        html.Div(
                        dcc.RangeSlider(
                            min=0, max=48, step=1,
                            marks={0: '0000', 6: '0600', 12: '1200', 18: '1800', 24: '0000', 30: '0600', 36: '1200', 42: '1800', 48: '0000',},
                            value=[4, 24], allowCross = False, id='time_slider'
                        ),style={"padding-top":"20px"}),
                        html.Div(id='time_slider_output',style={"font-size":"17px","font-family": 'Poppins,sans-serif',"padding-top":"20px"}),
                    ], style={"font-family": 'Poppins,sans-serif'},
                )
            ,),
            dcc.Tab(className="custom-tab icon2", selected_className='custom-tab--selected', label='Same src and dest',  children=html.Div(
                [
                    html.H1(id = "orig_dest_line_title", style={"text-align":"center","padding-top":"10px","font-family": 'Poppins,sans-serif'}),
                    dcc.Graph(id='orig_dest_line'),
                    html.H1(" Proportion of delays in 2012", style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
                    html.Div(id='orig_dest_pie', style={"display":"flex","align-items":"center","justify-content":"center"}
                    ),
                    html.H1("Proportion of delays by months", style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
                    html.Div(id='orig_dest_bar', style={"display":"flex","align-items":"center","justify-content":"center"}),
                    html.H1("Historical breakdown of delays by years", style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
                    html.Div(id='orig_dest_hist_delay', style={"display":"flex","align-items":"center","justify-content":"center"})
                ]),
            ),
            dcc.Tab(className="custom-tab icon3", selected_className='custom-tab--selected', label='Same carrier', 
            children=html.Div([
                html.Div(html.H1(id = "carrier_line_title"), style={"text-align":"center","padding-top":"10px","font-family": 'Poppins,sans-serif'}),
                dcc.Graph(id='carrier_line'),
                html.Div(html.H1("Proportion of delays in 2012"), style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
                html.Div(id='carrier_pie', style={"display":"flex","justify-content":"center","align-items":"center"}),
                html.Div(html.H1("Proportion of delays by months"), style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
                html.Div(id='carrier_bar', style={"display":"flex","justify-content":"center","align-items":"center"}),
                html.Div(html.H1("Historical breakdown of delays by years"), style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
                html.Div(id='carrier_hist_delay', style={"display":"flex","justify-content":"center","align-items":"center"})
                ,])
            ),
            dcc.Tab(className="custom-tab icon4", selected_className='custom-tab--selected', label='Same departure time', 
            children=html.Div([
                html.Div(html.H1(id = "deph_line_title"), style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
                dcc.Graph(id='deph_line'),
                html.Div(html.H1("Proportion of delays in 2012"),style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
                html.Div(id="deph_pie", style={"display":"flex","align-items":"center","justify-content":"center"}),
                html.Div(html.H1("Proportion of delays in 2012 by months"), style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
                html.Div(id="deph_bar", style={"display":"flex","justify-content":"center","align-items":"center"}),
                html.Div(html.H1("Historical breakdown of delays by years"), style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
                html.Div(id='deph_hist_delay', style={"display":"flex","justify-content":"center","align-items":"center"})
            ])
            ),
            dcc.Tab(className="custom-tab icon5", selected_className='custom-tab--selected', label='Same arrival time', 
            children=html.Div([
                html.Div(html.H1(id = "arrh_line_title"), style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
                dcc.Graph(id='arrh_line'),
                html.Div(html.H1("Proportion of delays in 2012"),style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
                html.Div(id='arrh_pie', style={"display":"flex","align-items":"center","justify-content":"center"}),
                html.Div(html.H1("Proportion of delays by months"),style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
                html.Div(id="arrh_bar", style={"display":"flex","justify-content":"center","align-items":"center"}),
                html.Div(html.H1("Breakdown of historical delays by years"),style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
                html.Div(id="arrh_hist_delay", style={"display":"flex","justify-content":"center","align-items":"center"})
            ])
            ),
            dcc.Tab(className="custom-tab icon6", selected_className='custom-tab--selected', label='Upload files', 
            children=html.Div([

                html.Div([
                    html.Img(src=app.get_asset_url('pin.svg'),style={"padding-right":"20px","width":"20px"}),
                    html.H1("Please upload a .csv or . xls file",style={"font-size":"36px"})
                ],style={"font-family": 'Poppins,sans-serif',"display":"flex","align-items":"center","justify-content":"center"}),

                html.Div([
                    html.H3("Please ensure that your data is in the correct format and input type. Invalid rows will be ignored."),
                    html.H3("You may refer to an example of a valid csv file below."),
                    html.H3("Please do not include headers in the file. The expected columns in order are:"),
                    html.Ol([
                        html.Li("year (integer)"),
                        html.Li("month (integer)",style={"padding-top":"5px"}),
                        html.Li("day (integer)",style={"padding-top":"5px"}),
                        html.Li("origin airport code",style={"padding-top":"5px"}),
                        html.Li("carrier (IATA)",style={"padding-top":"5px"}),
                        html.Li("scheduled hour of departure (24 hour)",style={"padding-top":"5px"})
                        ,]
                    )
                ]
                ,style={"font-family": 'Poppins,sans-serif',"width":"560px","margin":"0 auto",
                "text-align":"left","padding":"20px 30px","box-shadow": "0px 4px 4px rgba(0, 0, 0, 0.25)",'margin-bottom':"40px"
                }),
                
                dcc.Upload(id = "upload_data", 
                children = html.Div([
                    'Drop or Select a file ', 
                ]), 
                style={
                    'textAlign': 'center',"margin":"0 auto"
                    
                },
                
                className="drop",
                multiple = False),
                html.Div([
                    html.Br(),
                ]),
                html.Div(id='output_table'),
                html.Div(id = "output_pie", style={"display":"flex","justify-content":"center","align-items":"center"}),
                html.Hr(),
                html.Div([
                    dash_table.DataTable(
                        good_example_df.to_dict('records'),
                        [{'name': i, 'id': i} for i in good_example_df.columns],
                        style_cell={'textAlign': 'center'},
                        style_header={ 'background-color': 'white',"text-align":"center"}
                    ),
                    html.Hr(),  # horizontal line
                ],style={"padding-top":"40px","width":"500px","margin":"0 auto","text-align":'center'}),
                html.I("An example of a csv you may upload"),
                html.H2("You may refer to the IATA for the supported carriers below.", style={"padding-top":"30px"}),
                html.Div([
                    dash_table.DataTable(
                        options_dict['carrier'],
                        [{'name': 'Carrier name', 'id': "label"}, {'name': 'IATA', 'id': "value"}],
                        style_cell={'textAlign': 'center'},
                        style_data_conditional=[{
                            'if': {'row_index': 'odd'},'backgroundColor': 'rgb(241, 241, 241)'
                            }
                        ],
                        style_header={'fontWeight': 'bold','backgroundColor': 'rgb(241, 241, 241)'},
                        sort_action = 'native'
                    ),
                    html.Hr(),  # horizontal line
                ], style={"textAlign":"center","align-items":"center","width":"700px",'marginLeft': 'auto', 'marginRight': 'auto'})
            ], style={"textAlign":"center","align-items":"center"}),    
            ),
            dcc.Tab(selected_className='custom-tab--selected', label='Real Time API', 
            children=html.Div([
                html.Div(html.H1('Real Time API from AviationStack'), style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
                html.Div([
                    html.Div(html.H2("Select an Airport:"), style={"padding-right":"5px"}),
                    html.Div(dcc.Dropdown(id='orig3', value = "DAB"), style={"padding":"10px 20px","width":"100px"}),
                    html.Div(id = 'airportTable')
                ]),
                html.Div(html.H1("Select the options to start predicting"),style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
                html.Div([
                    html.Div(html.H2("Select Origin:"), style={"padding-right":"5px"}),
                    html.Div(dcc.Dropdown(id='orig2', value = "DAB"), style={"padding":"10px 20px","width":"100px"}),
                    html.Div(html.H2("Select Destination:"), style={"padding-left":"20px","padding-right":"5px"}),
                    html.Div(dcc.Dropdown(id='dest2', value = "ATL"), style={"padding":"10px 20px","width":"100px"}),
                    html.Div(html.H2("Select Carrier:"), style={"padding-left":"20px","padding-right":"5px"}),
                    html.Div(dcc.Dropdown(id='carrier2', value = 'DL', options=options_dict['carrier']),style={"padding":"10px 20px","width":"200px"}),
                    ], style={"display":"flex","padding":"10px 0","align-items":"center","font-family": 'Poppins,sans-serif'}),
                html.Div(html.H2(id='pred2'), style={"font-size":"16px","padding-top":"10px","text-align":"center"}),
                ])
            ),
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
    return_line = "Please fill in all the fields below."
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
        if max(float(delay['arr']), 0) == 0:
            arr_return_line = "The arrival will not delay."
        else: 
            arr_return_line = "The arrival will delay by " + "{:.3f}".format(float(delay['arr'])) + " minutes."
        if max(float(delay['dep']), 0) == 0:
            dep_return_line = "The departure will not delay."
        else: 
            dep_return_line = "The departure will delay by " + "{:.3f}".format(float(delay['dep'])) + " minutes."            

        "{:.3f}".format
        return_line = [dep_return_line , html.Br(), arr_return_line]
    return return_line

# callback to display time selection
@app.callback(
    Output('time_slider_output', 'children'),
    [Input('time_slider', 'value')]
)
def update_output(value):
    if not value: 
        return ""
    dept, arr = value
    dept ="{:02d}".format(dept%24)
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
    Output('orig_dest_pie','children'),
    Output('orig_dest_bar','children'),
    Input('orig', 'value'),
    Input('dest', 'value')
)
def update_orig_dest_pie(orig, dest):
    pie_children = html.Div()
    bar_children = html.Div() 

    if all([orig, dest]):
        pie_plot_dep, pie_plot_arr, bar_plot_dep, bar_plot_arr = generate_pie_bar(orig_dest_dep_df, orig_dest_arr_df, 
                                                                              [("origin_airport_code", orig), ("dest_airport_code", dest)])
        pie_children = [dcc.Graph(figure=pie_plot_dep), dcc.Graph(figure=pie_plot_arr),]
        bar_children = [dcc.Graph(figure=bar_plot_dep), dcc.Graph(figure=bar_plot_arr),]
    return pie_children, bar_children
@app.callback(
    Output('orig_dest_hist_delay','children'),
    Input('orig', 'value'),
    Input('dest', 'value')
    )
    
def update_orig_dest_hist_delay_type(orig, dest):
    children = html.Div()      
    if all([orig, dest]):
        hist_dep, hist_arr = update_delay_type(orig_dest_dep_df, orig_dest_arr_df, [("origin_airport_code", orig), ("dest_airport_code", dest)])
        children = [dcc.Graph(figure=hist_dep), dcc.Graph(figure=hist_arr),]
    return children                                             

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
    Output('carrier_pie','children'),
    Output('carrier_bar','children'),
    Input('carrier', 'value'),
    )
def update_carrier_pie_bar(carrier):
    pie_children = html.Div()
    bar_children = html.Div()         
    if carrier:
        pie_plot_dep, pie_plot_arr, bar_plot_dep, bar_plot_arr = generate_pie_bar(carrier_dep_df, carrier_arr_df, [("u_carrier", carrier)])
        pie_children = [dcc.Graph(figure=pie_plot_dep), dcc.Graph(figure=pie_plot_arr),]
        bar_children = [dcc.Graph(figure=bar_plot_dep), dcc.Graph(figure=bar_plot_arr),]
    return pie_children, bar_children

@app.callback(
    Output('carrier_hist_delay','children'),
    Input('carrier', 'value')
    )
 
def update_carrier_hist_delay_type(carrier):
    children = html.Div()         
    if carrier:
        hist_dep, hist_arr = update_delay_type(carrier_dep_df, carrier_arr_df, 
                                             [("u_carrier", carrier)])
        children = [dcc.Graph(figure=hist_dep), dcc.Graph(figure=hist_arr),]
    return children 

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
    Output('deph_pie','children'),
    Output('deph_bar','children'),
    [Input('time_slider', 'value')]
    )
def update_deph_pie_bar(time_slider):
    pie_children = html.Div()
    bar_children = html.Div()      
    if time_slider:
        dep, arr = time_slider
        dep = dep%24
        pie_plot_dep, pie_plot_arr, bar_plot_dep, bar_plot_arr = generate_pie_bar(deph_dep_df, deph_arr_df, [("dep_hour", dep)])
        pie_children = [dcc.Graph(figure=pie_plot_dep), dcc.Graph(figure=pie_plot_arr),]
        bar_children = [dcc.Graph(figure=bar_plot_dep), dcc.Graph(figure=bar_plot_arr),]
    return pie_children, bar_children

@app.callback(
    Output('deph_hist_delay','children'),
    [Input('time_slider', 'value')]
    )
def update_deph_hist_delay_type(time_slider):
    children = html.Div()      
    if time_slider:
        dep, arr = time_slider
        dep = dep%24
        hist_dep, hist_arr = update_delay_type(deph_dep_df, deph_arr_df, [("dep_hour", dep)])
        children = [dcc.Graph(figure=hist_dep), dcc.Graph(figure=hist_arr),]
    return children

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
    Output('arrh_pie','children'),
    Output('arrh_bar','children'),
    [Input('time_slider', 'value')]
    )

def update_arrh_pie_bar(time_slider):
    pie_children = html.Div()
    bar_children = html.Div()      
    if time_slider:
        dep, arr = time_slider
        arr = arr%24        
        pie_plot_dep, pie_plot_arr, bar_plot_dep, bar_plot_arr = generate_pie_bar(arrh_dep_df, arrh_arr_df, [("arr_hour", arr)])
        pie_children = [dcc.Graph(figure=pie_plot_dep), dcc.Graph(figure=pie_plot_arr),]
        bar_children = [dcc.Graph(figure=bar_plot_dep), dcc.Graph(figure=bar_plot_arr),]
    return pie_children, bar_children
@app.callback(
    Output('arrh_hist_delay','children'),
    [Input('time_slider', 'value')]
    )

def update_arrh_hist_delay_type(time_slider):
    children = html.Div()      
    if time_slider:
        dep, arr = time_slider
        arr = arr%24
        hist_dep, hist_arr = update_delay_type(arrh_dep_df, arrh_arr_df, [("arr_hour", arr)])
        children = [dcc.Graph(figure=hist_dep), dcc.Graph(figure=hist_arr),]
    return children                                             
@app.callback(
    Output("output_pie", "children"),
    Input("upload_data", "contents"), 
    State("upload_data", "filename"),
)

def output_pie(contents, filename):
    children = html.Div()      
    if contents:
        try:
            df = read_upload_data(contents, filename)
        except:
            return children
        pred_df = generate_pred_table(df, airport_pairs, allowable_values)
        if len(pred_df) > 0:
            # generate delay proportion for departure in 2012
            dep_prop = sum(pred_df.dep_delay > 0) / len(pred_df) * 100
            plot_dep = px.pie(pd.DataFrame({"Status": ["delayed", "not delayed"], "Proportion": [dep_prop, 100 - dep_prop]}),
                values = 'Proportion', 
                names = 'Status',
                title = "% of departures predicted to delay",
            )
            plot_dep.update_traces(textposition = 'outside' , textinfo = 'percent+label')
            arr_prop = sum(pred_df.arr_delay > 0) / len(pred_df) * 100
            plot_arr = px.pie(pd.DataFrame({"Status": ["delayed", "not delayed"], "Proportion": [arr_prop, 100 - arr_prop]}),
                values = 'Proportion', 
                names = 'Status',
                title = "% of arrival predicted to delay",
            )
            plot_arr.update_traces(textposition = 'outside' , textinfo = 'percent+label')
            children = html.Div(children = [dcc.Graph(figure=plot_dep), dcc.Graph(figure=plot_arr)],style={"display":"flex","align-items":"center","justify-content":"center"})
    return children

@app.callback(
    Output("output_table", "children"),
    Input("upload_data", "contents"), 
    State("upload_data", "filename"),
)
def output_table(contents, filename):
    table = html.Div()
    if contents:
        try:
            df = read_upload_data(contents, filename)
        except:
            return html.Div(["There was an error processing this file."])    
            
        pred_df = generate_pred_table(df, airport_pairs, allowable_values)
        if len(pred_df) == 0:
            table = html.Div("No valid rows.")
        else:
            table =  html.Div([
                html.H3("Predictions for " + filename),
                dash_table.DataTable(
                    data = pred_df.to_dict('records'),
                    columns = [{'name': i, 'id': i} for i in pred_df.columns],
                    sort_action="native",
                    page_current= 0,
                    page_size= 10,
                ),
            ])
    return table

@app.callback(
    Output(component_id='pred2',
    component_property='children'),
    Input(component_id='orig2',
    component_property='value'),
    Input(component_id='dest2',
    component_property='value'),
    Input(component_id='carrier2',
    component_property='value')
)

def get_pred2(orig2, dest2, carrier2):
    return_line = "Please fill in all the fields below."
    if all([orig2, dest2, carrier2]):
        today = date.today()
        year, month, dayofweek = today.year, today.month, today.weekday()
        
        params = {
            'access_key': api_key,
            'dep_iata': orig2,
            'arr_iata': dest2,
            'airline_iata': carrier2,
        }
        api_result = requests.get('http://api.aviationstack.com/v1/flights', params)
        api_response = api_result.json()
        if len(api_response['data']) == 0:
            return ['No data available', html.Br(), 'No data available']
        else:
            flight = api_response['data'][0]
            dep = int(flight['departure']['scheduled'][11:13])
            arr = int(flight['arrival']['scheduled'][11:13])
            dep = dep%24
            arr = arr%24
            dist = get_distance(airport_pairs, orig2, dest2)
            return_line = [dep, html.Br(), arr]
            param1 = {'yr': year, 'mon':month, 'day_of_week': dayofweek, 
            'dep_hour':dep,'arr_hour':arr, 'u_carrier': carrier2,
            'origin_airport_code':orig2, 'dest_airport_code': dest2, 
            'distance_grp':dist}
            
            
            delay = requests.get(flask_url, params=param1).json()
            if max(float(delay['arr']), 0) == 0:
                arr_return_line = "The arrival will not delay."
            else: 
                arr_return_line = "The arrival will delay by " + "{:.3f}".format(float(delay['arr'])) + " minutes."
            if max(float(delay['dep']), 0) == 0:
                dep_return_line = "The departure will not delay."
            else: 
                dep_return_line = "The departure will delay by " + "{:.3f}".format(float(delay['dep'])) + " minutes."            

            "{:.3f}".format
            return_line = [dep_return_line , html.Br(), arr_return_line]
            
    return return_line

# callback to change destination dropdown
@app.callback(
    Output('dest2','options'),
    Input('orig2','value')
)
def update_dest_dd2(orig2):
    dest_options = airport_pairs.dest_airport_code.unique()
    if orig2:
        dest_options = airport_pairs[airport_pairs.origin_airport_code == orig2][
            "dest_airport_code"
        ].tolist()
    return sorted(dest_options)

# callback to change origin dropdown
@app.callback(
    Output('orig2','options'),
    Input('dest2','value')
)
def update_orig_dd2(dest2):
    orig_options = airport_pairs.origin_airport_code.unique().tolist()
    if dest2:
        orig_options = airport_pairs[airport_pairs.dest_airport_code == dest2][
            "origin_airport_code"
        ].tolist()
    return sorted(orig_options)

@app.callback(
    Output('orig3','options'),
    Input('orig3','value')
)
def update_orig_dd3(d):
    orig_options = airport_pairs.origin_airport_code.unique().tolist()
    return sorted(orig_options)

@app.callback(
    Output("airportTable", "children"),
    Input(component_id='orig3',
    component_property='value'),
)

def airport_table(orig3):
    params = {
        'access_key': api_key,
        'dep_iata': orig3,
    }
    api_result = requests.get('http://api.aviationstack.com/v1/flights', params)
    api_response = api_result.json()
    if len(api_response['data']) == 0:
        return html.Div(["No data available."])    
    else:
        arrival_iata = []
        departure_iata = []
        scheduled_arrival = []
        scheduled_departure = []
        airline_iata = []
        df = pd.DataFrame()

        for flight in api_response['data']:
            arrival_iata.append(flight['arrival']['iata'])
            departure_iata.append(flight['departure']['iata'])
            scheduled_arrival.append(flight['arrival']['scheduled'])
            scheduled_departure.append(flight['departure']['scheduled'])
            airline_iata.append(flight['airline']['name'])
        df['Departure'] = departure_iata
        df['Arrival'] = arrival_iata
        df['Airline Name'] = airline_iata
        df['Scheduled Departure'] = scheduled_departure
        df['Scheduled Arrival'] = scheduled_arrival
        
        table =  html.Div([
                dash_table.DataTable(
                    data = df.to_dict('records'),
                    columns = [{'name': i, 'id': i} for i in df.columns],
                    sort_action="native",
                    page_current= 0,
                    page_size= 10,
                ),
                html.Hr(),  # horizontal line
            ])
        return table


if __name__ == '__main__':
    app.run_server(debug=True)
