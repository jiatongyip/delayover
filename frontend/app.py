# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, dcc, html, no_update, dash_table
import plotly.express as px
import pandas as pd
import datetime
from datetime import date
import requests
#from dash.dependencies import Input, Output, State
from dash_extensions.enrich import Output, DashProxy, Input, MultiplexerTransform, State
from custom_functions import (get_distance, get_yr_mon_dow, gen_line_plots, generate_pie_bar, 
update_delay_type, generate_pred_table, read_upload_data, get_tab_children, predict_delay, 
preprocess_date, generate_predictions)

external_stylesheets = ["https://fonts.googleapis.com/css2?family=Poppins&display=swap"]
app = DashProxy(transforms=[MultiplexerTransform()], external_stylesheets=external_stylesheets,
suppress_callback_exceptions=True)
app.title = 'De-Layover'


#app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
api_key = '4ee0ec95bc02b71af0bade456c730005'

#reading the data needed
airport_pairs = pd.read_csv("data/airport_pairs.csv")
orig_dest_arr_df = pd.read_csv("data/grp_orig_dest_arr.csv")
orig_dest_dep_df = pd.read_csv("data/grp_orig_dest_dep.csv")
orig_dest_arr_mon_df = pd.read_csv("data/grp_orig_dest_arr_mon.csv")
orig_dest_dep_mon_df = pd.read_csv("data/grp_orig_dest_dep_mon.csv")
carrier_arr_df = pd.read_csv("data/grp_carrier_arr.csv")
carrier_dep_df = pd.read_csv("data/grp_carrier_dep.csv")
carrier_arr_mon_df = pd.read_csv("data/grp_carrier_arr_mon.csv")
carrier_dep_mon_df = pd.read_csv("data/grp_carrier_dep_mon.csv")
deph_arr_df = pd.read_csv("data/grp_deph_arr.csv")
deph_dep_df = pd.read_csv("data/grp_deph_dep.csv")
deph_arr_mon_df = pd.read_csv("data/grp_deph_arr_mon.csv")
deph_dep_mon_df = pd.read_csv("data/grp_deph_dep_mon.csv")
arrh_arr_df = pd.read_csv("data/grp_arrh_arr.csv")
arrh_dep_df = pd.read_csv("data/grp_arrh_dep.csv")
arrh_arr_mon_df = pd.read_csv("data/grp_arrh_arr_mon.csv")
arrh_dep_mon_df = pd.read_csv("data/grp_arrh_dep_mon.csv")
good_example_df = pd.read_csv("data/good_example.csv")

with open("data/options_dict.txt", "r") as file:
    options_dict = eval(file.read())
with open("data/carrier_dict.txt", "r") as file:
    carrier_dict = eval(file.read())
with open("data/allowable_values.txt", "r") as file:
    allowable_values = eval(file.read())
with open("data/default_values.txt", "r") as file:
    default_values = eval(file.read())

# app
app.layout = html.Div(
    [
        html.Div(
            [
            html.Div([
                html.Img(src=app.get_asset_url('plane.svg'),style={"padding-right":"30px"}),
                html.H1('De-Layover' ,style={"font-size":"48px","text-align":"center"}),
            ],style={"display":"flex","justify-content":"center","align-items":"center"}),

            html.Div([
                 html.H2("Fret no more, the delay is over!", style={"font-size":"36px"}), 
                  html.P("De-layover is here to help you predict and visualise flight delays. You can navigate to the other tabs to check out past delays with the same origin, destination, carrier, departure or arrival time.",style={"font-size":"16px"}),

            ],style={"width":"600px","margin":"0 auto"}),
            ],style={"background-color":"#013E87","padding":"10px 0","color":"#fff","font-family": 'Poppins,sans-serif',"text-align":"center"}
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
                        "width":"650px","margin":"30px auto","box-shadow": "0px 3px 6px rgba(0, 38, 83, 0.25)"}
                        ),
                        html.Div([
                            html.H2("Please fill in your flight details below.",style={"text-align":"center","font-size":"30px"}),

                        ]),
                        html.Div(
                            [
                            html.Div(html.H2("Select Date:"), style={"padding-right":"5px"}),
                            html.Div(
                                dcc.DatePickerSingle(
                                    id='date_picker',
                                    min_date_allowed=date(2013, 1, 1),
                                    max_date_allowed=date(2022, 12, 31),
                                    initial_visible_month=date(default_values['year'], default_values['month'], default_values['day']),
                                    date=date(default_values['year'], default_values['month'], default_values['day']),
                                    month_format = "MMMM YYYY",
                                    display_format = "DD-MMM-YYYY"
                                    ),
                                style={"padding":"10px 20px"}
                            ),
                            html.Div(html.H2("Select Origin:"), style={"padding-right":"5px"}),
                            html.Div(dcc.Dropdown(id='orig', value = default_values['orig']), style={"padding":"10px 20px","width":"100px"}),
                            html.Div(html.H2("Select Destination:"), style={"padding-left":"20px","padding-right":"5px"}),
                            html.Div(dcc.Dropdown(id='dest', value = default_values['dest']), style={"padding":"10px 20px","width":"100px"}),
                            html.Div(html.H2("Select Carrier:"), style={"padding-left":"20px","padding-right":"5px"}),
                            html.Div(dcc.Dropdown(
                                id='carrier', value = default_values['carrier'],
                                options=options_dict['carrier']),
                                style={"padding":"10px 20px","width":"200px"})
                            ], style={"display":"flex","padding":"10px 0","justify-content":"center","align-items":"center"}
                        ),
                        html.Div([
                            html.H2("Select Departure and Arrival time:",style={"padding":"0 40px"}), 
                            html.Div(id='time_slider_output',style={"font-size":"18px","border":"2px solid #003676","border-radius":"4px","padding":"10px 60px"}),     

                        ],style={"display":"flex","align-items":"center","justify-content":'center',"padding":"20px 0"}),
                        
                        html.Div(
                        dcc.RangeSlider(
                            min=0, max=48, step=1,
                            marks={0: '0000', 6: '0600', 12: '1200', 18: '1800', 24: '0000', 30: '0600', 36: '1200', 42: '1800', 48: '0000',},
                            value=default_values['time_slider'], allowCross = False, id='time_slider'
                        ),style={"width":"1500px","padding":"50px","margin":"0 auto"}),
                    ], style={"font-family": 'Poppins,sans-serif'},
                )
            ,),
            dcc.Tab(className="custom-tab icon2", selected_className='custom-tab--selected', label='Same Airports',  
            children=html.Div(get_tab_children("orig_dest")),
            ),
            dcc.Tab(className="custom-tab icon3", selected_className='custom-tab--selected', label='Same Carrier', 
            children=html.Div(get_tab_children("carrier"))
            ),
            dcc.Tab(className="custom-tab icon4", selected_className='custom-tab--selected', label='Same Departure Time', 
            children=html.Div(get_tab_children("deph"))
            ),
            dcc.Tab(className="custom-tab icon5", selected_className='custom-tab--selected', label='Same Arrival Time', 
            children=html.Div(get_tab_children("arrh"))
            ),
            dcc.Tab(className="custom-tab icon6", selected_className='custom-tab--selected', label='File Upload', 
            children=html.Div([

                html.Div([
                    html.Img(src=app.get_asset_url('pin.svg'),style={"padding-right":"20px","width":"25px"}),
                    html.H1("To view predictions for multiple flights",style={"font-size":"30px","text-align":"center"})
                ],style={"display":"flex","align-items":"center","justify-content":"center"}),

                html.Div([
                    html.H3("Want to view predictions for multiple flights? Upload your file!"),
                    html.Div([
                        html.Img(src=app.get_asset_url('caution.svg'),style={"padding-right":"10px"}),
                        html.H3("Only .csv or .xls filetypes are supported.",style={"color":"#F24E1E"}),

                    ],style={"display":"flex"}),
                    html.H3("Please ensure that your data is in the correct format and input type. Invalid rows will be ignored."),
                    
                    html.P("You may refer to an example of a valid csv file below."),
                    html.P("Please do not include headers in the file. The expected columns in order are:",style={"color":"#F24E1E"}),
                    
                    html.Ol([
                        html.Li("Year (integer)"),
                        html.Li("Month (integer)",style={"padding-top":"5px"}),
                        html.Li("Day (integer)",style={"padding-top":"5px"}),
                        html.Li("Origin airport code",style={"padding-top":"5px"}),
                        html.Li("Destination airport code",style={"padding-top":"5px"}),
                        html.Li("Carrier (IATA)",style={"padding-top":"5px"}),
                        html.Li("Scheduled hour of departure (24 hour)",style={"padding-top":"5px"}),
                        html.Li("Scheduled hour of arrival (24 hour)",style={"padding-top":"5px"})
                        ]
                    ),
                    html.H3("Interested to know more about one particular row ? You may select that row and visit the other tabs."),
                ] ,style={"width":"600px","margin":"0 auto",
                "text-align":"left","padding":"20px 50px","box-shadow": "0px 4px 4px rgba(0, 0, 0, 0.25)",'margin-bottom':"40px"}),
               

                dcc.Upload(id = "upload_data", 
                children = html.Div(['Drop or Select a file ',]), 
                style={'textAlign': 'center',"margin":"0 auto"}, className="drop", multiple = False
                ),
                html.Br(),
                html.Div(id='output_table',style={"margin" :"10px 80px"}),
                html.H3("Summary of the flights you uploaded:",style={"font-size":"24px","padding-top":"20px"}),
                html.Div(id = "output_pie", style={"display":"flex","justify-content":"center","align-items":"center"}),
                # html.Hr(),
                html.Div([
                    html.Div([
                        html.Img(src=app.get_asset_url('file2.svg'),style={"padding":"0 30px"}),
                        html.H3("An example of a csv file you may upload",style={"font-size":"30px"}),

                    ],style={"display":"flex","align-items":"center","justify-content":"center"}),
                    
                    dash_table.DataTable(
                        good_example_df.to_dict('records'),
                        [{'name': i, 'id': i} for i in good_example_df.columns],
                        style_cell={'textAlign': 'center',"padding":"10px"},
                        style_header={ 'background-color': 'white',"text-align":"center","padding":"10px"}
                    ),
                    html.Br(),
                    html.Br(),
                    # html.Hr(),  # horizontal line
                ], style={"padding-top":"40px","margin":"0 auto","text-align":'center',"width":"800px","font-size":"14px","margin-top":"150px"}),
                
                html.H2("Not sure about the IATA for your carrier? Here's a list of supported carriers.", style={"font-size":"30px","padding-top":"40px","padding-bottom":"20px","width":"800px","margin":"0 auto"}),
                html.Div([
                    dash_table.DataTable(
                        options_dict['carrier'],
                        [{'name': 'Carrier name', 'id': "label"}, {'name': 'IATA', 'id': "value"}],
                        style_cell={'textAlign': 'center',"padding":"10px"},
                        style_data_conditional=[{
                            'if': {'row_index': 'odd'},'backgroundColor': 'rgb(241, 241, 241)'
                            }
                        ],
                        style_header={'fontWeight': 'bold','backgroundColor': 'rgb(241, 241, 241)',"padding":"10px"},
                        sort_action = 'native'
                    ),
                    html.Hr(),  # horizontal line
                ], style={"textAlign":"center","align-items":"center","margin":"0 auto","width":"800px","font-size":"14px"})
            ], style={"textAlign":"center","align-items":"center"}),    
            ),
            dcc.Tab(className="custom-tab icon7",selected_className='custom-tab--selected', label='Real-Time API', 
            children=html.Div([
                html.H1("Real-Time API from AviationStack",style={"text-align":"center"}),
                html.P("Fetching the latest flights from AviationStack's real-time API for your easy access. Select your airport of interest below: ",
                style={"text-align":"center","width":"500px","margin":"0 auto"}),
                    html.Div([ 
                    html.H3("Please choose an origin and a destination.",style={"width":"500px","margin":"0 auto"}),
                    html.P("Interested to know more about one particular row ? You may select that row and visit the other tabs.",style={"width":"500px","margin":"0 auto","font-weight":"500"}),
                    ], 
                style={"text-align":"center","box-shadow": "0px 3px 6px rgba(0, 38, 83, 0.25)","padding":"20px 10px","color":"#001E42","width":"600px","margin":"20px auto"}),
                
                html.Div([
                    html.Div(html.H2("Select Origin:"), style={"padding-right":"5px"}),
                    html.Div(dcc.Dropdown(id='orig2', value = ""), style={"padding":"10px 20px","width":"100px"}),
                    html.Div(html.H2("Select Destination:"), style={"padding-left":"20px","padding-right":"5px"}),
                    html.Div(dcc.Dropdown(id='dest2', value = ""), style={"padding":"10px 20px","width":"100px"}),
                ], style={"display":"flex","justify-content":"center","align-items":"center","padding":"10px 0","align-items":"center"}),
                html.Div(id = 'airportTable', style={"text-align":"center"}),
                ])
            ),
        ])
    ]
,style={"font-family": 'Poppins,sans-serif'})

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
    return_line = "No predictions generated."
    if all([date_picker, time_slider, orig, dest, carrier]):
        year, month, dayofweek = get_yr_mon_dow(date_picker)
        dep , arr = time_slider
        dep, arr = dep%24, arr%24

        delay = predict_delay(year, month, dayofweek, dep, arr, carrier, orig, dest)
        if delay['arr'] == 0:
            arr_return_line = "The arrival will not delay."
        else: 
            arr_return_line = "The arrival will delay by " + "{:.3f}".format(delay['arr']) + " minutes."
        if delay['dep'] == 0:
            dep_return_line = "The departure will not delay."
        else: 
            dep_return_line = "The departure will delay by " + "{:.3f}".format(delay['dep']) + " minutes."            

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
    return ['Departure time selected: ' + dept + '00 hours', html.Br(),
    'Arrival time selected: ' + arr + '00 hours']

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
        line_title = "Past flights from " + orig + " to " + dest

    return line_plot, line_title

@app.callback(
    Output('orig_dest_bar','children'),
    Input('orig', 'value'),
    Input('dest', 'value')
)
def update_orig_dest_pie(orig, dest):
    bar_children = html.Div() 

    if all([orig, dest]):
        bar_plot_dep, bar_plot_arr = generate_pie_bar(orig_dest_dep_df, orig_dest_arr_df, 
                                                                              [("origin_airport_code", orig), ("dest_airport_code", dest)])
        bar_children = [dcc.Graph(figure=bar_plot_dep), dcc.Graph(figure=bar_plot_arr),]
    return bar_children
@app.callback(
    Output('orig_dest_hist_delay','children'),
    Input('orig', 'value'),
    Input('dest', 'value')
    )
    
def update_orig_dest_hist_delay_type(orig, dest):
    children = html.Div()      
    if all([orig, dest]):
        hist_dep, hist_arr = update_delay_type(orig_dest_dep_mon_df, orig_dest_arr_mon_df, [("origin_airport_code", orig), ("dest_airport_code", dest)])
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
        line_title = "Past flights by " + carrier_dict[carrier]

    return line_plot, line_title

@app.callback(
    Output('carrier_bar','children'),
    Input('carrier', 'value'),
    )
def update_carrier_pie_bar(carrier):
    bar_children = html.Div()         
    if carrier:
        bar_plot_dep, bar_plot_arr = generate_pie_bar(carrier_dep_df, carrier_arr_df, [("u_carrier", carrier)])
        bar_children = [dcc.Graph(figure=bar_plot_dep), dcc.Graph(figure=bar_plot_arr),]
    return bar_children

@app.callback(
    Output('carrier_hist_delay','children'),
    Input('carrier', 'value')
    )
 
def update_carrier_hist_delay_type(carrier):
    children = html.Div()         
    if carrier:
        hist_dep, hist_arr = update_delay_type(carrier_dep_mon_df, carrier_arr_mon_df, 
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
        line_title = "Past flights departing at " + "{:02}".format(dep) + "00 hours"

    return line_plot, line_title

@app.callback(
    Output('deph_bar','children'),
    [Input('time_slider', 'value')]
    )
def update_deph_pie_bar(time_slider):
    bar_children = html.Div()      
    if time_slider:
        dep, arr = time_slider
        dep = dep%24
        bar_plot_dep, bar_plot_arr = generate_pie_bar(deph_dep_df, deph_arr_df, [("dep_hour", dep)])
        bar_children = [dcc.Graph(figure=bar_plot_dep), dcc.Graph(figure=bar_plot_arr),]
    return bar_children

@app.callback(
    Output('deph_hist_delay','children'),
    [Input('time_slider', 'value')]
    )
def update_deph_hist_delay_type(time_slider):
    children = html.Div()      
    if time_slider:
        dep, arr = time_slider
        dep = dep%24
        hist_dep, hist_arr = update_delay_type(deph_dep_mon_df, deph_arr_mon_df, [("dep_hour", dep)])
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
        line_title = "Past flights arriving at " + "{:02}".format(arr) + "00 hours"

    return line_plot, line_title

@app.callback(
    Output('arrh_bar','children'),
    [Input('time_slider', 'value')]
    )

def update_arrh_pie_bar(time_slider):
    bar_children = html.Div()      
    if time_slider:
        dep, arr = time_slider
        arr = arr%24        
        bar_plot_dep, bar_plot_arr = generate_pie_bar(arrh_dep_df, arrh_arr_df, [("arr_hour", arr)])
        bar_children = [dcc.Graph(figure=bar_plot_dep), dcc.Graph(figure=bar_plot_arr),]
    return bar_children
@app.callback(
    Output('arrh_hist_delay','children'),
    [Input('time_slider', 'value')]
    )

def update_arrh_hist_delay_type(time_slider):
    children = html.Div()      
    if time_slider:
        dep, arr = time_slider
        arr = arr%24
        hist_dep, hist_arr = update_delay_type(arrh_dep_mon_df, arrh_arr_mon_df, [("arr_hour", arr)])
        children = [dcc.Graph(figure=hist_dep), dcc.Graph(figure=hist_arr),]
    return children                                             
@app.callback(
    Output("output_pie", "children"),
    Input("upload_data", "contents"), 
    State("upload_data", "filename"),
)

def output_pie(contents, filename):
    children = html.Div(["No file uploaded yet!"])      
    if contents:
        try:
            df = read_upload_data(contents, filename)
        except:
            return children
        pred_df = generate_pred_table(df, airport_pairs, allowable_values)
        if len(pred_df) > 0:
            # generate delay proportion for departure in 2012
            dep_prop = sum(pred_df['Predicted Departure Delay'] > 0) / len(pred_df) * 100
            plot_dep = px.pie(pd.DataFrame({"Status": ["Delayed", "Not delayed"], "Proportion": [dep_prop, 100 - dep_prop]}),
                values = 'Proportion', 
                names = 'Status',
                title = "For departures",
            )
            plot_dep.update_traces(textposition = 'outside' , textinfo = 'percent+label', marker = {'colors': ['#003676', '#FFC90B']})
            arr_prop = sum(pred_df['Predicted Arrival Delay'] > 0) / len(pred_df) * 100
            plot_arr = px.pie(pd.DataFrame({"Status": ["Delayed", "Not delayed"], "Proportion": [arr_prop, 100 - arr_prop]}),
                values = 'Proportion', 
                names = 'Status',
                title = "For arrivals",
            )
            plot_arr.update_traces(textposition = 'outside' , textinfo = 'percent+label', marker = {'colors': ['#003676', '#FFC90B']})
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
             html.H3("Predictions for " + filename, style={"font-size":"26px","padding-top":"20px"}),
                # html.I("Interested to know more about one particular row? You may select that row and visit the other tabs."),
                html.Div([
                    dash_table.DataTable(
                    id = "output_table_datatable",
                    data = pred_df.to_dict('records'),
                    columns = [{'name': i, 'id': i} for i in pred_df.columns],
                    sort_action="native",
                    page_current= 0,
                    page_size= 10,
                    row_selectable='single',
                    style_header={
                        'backgroundColor': '#013E87',
                        'color': '#fff',
                        'padding':"10px",
                        "font-size":"14px"
                        },
                    style_cell={ 'border':"1px solid #393939","text-align":'center',"font-size":"14px",'padding':"10px"}

                    ),

                ]),
              
            ])
    return table

@app.callback(
    Output('date_picker', 'date'),
    Output('time_slider', 'value'),
    Output('orig', 'value'),
    Output('dest', 'value'),
    Output('carrier', 'value'),
    Input('output_table_datatable', 'data'),
    Input("output_table_datatable", "selected_rows"), 
    prevent_initial_call=True
)

def autofill_from_upload(data, selected_row):
    (datepicker, timeslider, orig, dest, carrier) = (
        datetime.date(default_values['year'], default_values['month'], default_values['day']).isoformat(),
        default_values['time_slider'], default_values['orig'], default_values['dest'], default_values['carrier'])
    if selected_row:
        selected_row = data[selected_row[0]]
        year, month, day, orig, dest, carrier, deph, arrh = list(selected_row.values())[:8]
        datepicker = datetime.date(year, month, day).isoformat()
        if deph > arrh:
            arrh += 24
        timeslider = [deph, arrh]
    return datepicker, timeslider, orig, dest, carrier


@app.callback(
    Output('orig2','options'),
    Input('orig2','value')
)
def update_orig_dd2(d):
    orig_options = airport_pairs.origin_airport_code.unique().tolist()
    return sorted(orig_options)

@app.callback(
    Output('dest2','options'),
    Input('dest2','value')
)
def update_dest_dd2(orig):
    dest_options = airport_pairs.dest_airport_code.unique()
    return sorted(dest_options)

@app.callback(
    Output("airportTable", "children"),
    Input(component_id='orig2',
    component_property='value'),
    Input(component_id='dest2',
    component_property='value'),
)

def airport_table(orig2, dest2):
    try:
        if orig2 == '':
            if dest2:
                params = {
                'access_key': api_key,
                'arr_iata': dest2,
                }
            else:
                return html.Div(["No query selected."]) 
        elif orig2:
            if dest2:
                params = {
                'access_key': api_key,
                'arr_iata': dest2,
                'dep_iata': orig2
                }
            else:
                params = {
                        'access_key': api_key,
                        'dep_iata': orig2,
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
            arr_delay_lst = []
            dep_delay_lst = []
            df = pd.DataFrame()

            for flight in api_response['data']:
                arr_delay, dep_delay = generate_predictions(flight)
                if arr_delay != "No data available" and flight['airline']['iata'] in allowable_values['carrier'] :
                    arr_delay_lst.append(arr_delay)
                    dep_delay_lst.append(dep_delay)
                    arrival_iata.append(flight['arrival']['iata'])
                    departure_iata.append(flight['departure']['iata'])
                    scheduled_arrival.append(preprocess_date(flight['arrival']['scheduled']))
                    scheduled_departure.append(preprocess_date(flight['departure']['scheduled']))
                    airline_iata.append(flight['airline']['iata'])

            if len(departure_iata) == 0:
                return html.Div(["No data available"])

            df['Origin'] = departure_iata
            df['Destination'] = arrival_iata
            df['Carrier'] = airline_iata
            df['Departure Time'] = scheduled_departure
            df['Arrival Time'] = scheduled_arrival
            df['Predicted Departure Delay'] = dep_delay_lst
            df['Predicted Arrival Delay'] = arr_delay_lst
            
            
            table =  html.Div([
                    dash_table.DataTable(
                        id = "api_datatable",
                        data = df.to_dict('records'),
                        columns = [{'name': i, 'id': i} for i in df.columns],
                        sort_action="native",
                        page_current= 0,
                        page_size= 10,
                        row_selectable='single',
                        style_cell={ 'border':"1px solid #393939","text-align":'center',"font-size":"14px",'padding':"10px"},
                        style_header={
                        'backgroundColor': '#013E87',
                        'color': '#fff',
                        'padding':"10px",
                        "font-size":"14px"
                        },
                        

                    ),
                ])
            return table
    except:
        return html.Div(["No data available"])  

@app.callback(
    Output('date_picker', 'date'),
    Output('time_slider', 'value'),
    Output('orig', 'value'),
    Output('dest', 'value'),
    Output('carrier', 'value'),
    Input('api_datatable', 'data'),
    Input("api_datatable", "selected_rows"), 
    prevent_initial_call=True
)

def autofill_from_api(data, selected_row):
    (datepicker, timeslider, orig, dest, carrier) = (
        datetime.date(default_values['year'], default_values['month'], default_values['day']).isoformat(),
        default_values['time_slider'], default_values['orig'], default_values['dest'], default_values['carrier'])
    print("hi")
    try:
        if selected_row:
            selected_row = data[selected_row[0]]
            orig, dest, carrier, dep, arr = list(selected_row.values())[:5]
            depTime = datetime.datetime.strptime(dep, '%d/%m/%Y %H:%M')
            arrTime = datetime.datetime.strptime(arr, '%d/%m/%Y %H:%M')
            datepicker = datetime.date(depTime.year, depTime.month, depTime.day).isoformat()
            deph = depTime.hour
            arrh = arrTime.hour
            if deph > arrh:
                arrh += 24
            timeslider = [deph, arrh]
    except:
        return datepicker, timeslider, orig, dest, carrier
    return datepicker, timeslider, orig, dest, carrier

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
