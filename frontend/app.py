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
import plotly.graph_objs as go
from custom_functions import get_distance, get_yr_mon_dow, gen_line_plots, generate_pie_bar, update_delay_type

import base64
import datetime
import io
import plotly.graph_objs as go
import cufflinks as cf
from dash import no_update, dash_table, dcc, html
from dash.dependencies import Input, Output, State
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
                        html.Div(html.H2(id='pred'), style={"font-size":"16px","padding-top":"10px","text-align":"center"}),
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
                    html.Div([
                        dcc.Graph(id='orig_dest_pie_dep'),
                        dcc.Graph(id='orig_dest_pie_arr'),
                    ], style={"display":"flex","align-items":"center","justify-content":"center"}
                    ),
                    html.H1("Proportion of delays by months", style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
                    html.Div([
                        dcc.Graph(id='orig_dest_bar_dep'),
                        dcc.Graph(id='orig_dest_bar_arr'),
                    ], style={"display":"flex","align-items":"center","justify-content":"center"}),
                    html.H1("Historical breakdown of delays by years", style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
                    html.Div([
                        dcc.Graph(id='orig_dest_hist_delay_dep'),
                        dcc.Graph(id='orig_dest_hist_delay_arr'),
                    ], style={"display":"flex","align-items":"center","justify-content":"center"})
                ]),
            ),
            dcc.Tab(className="custom-tab icon3", selected_className='custom-tab--selected', label='Same carrier', 
            children=html.Div([
                html.Div(html.H1(id = "carrier_line_title"), style={"text-align":"center","padding-top":"10px","font-family": 'Poppins,sans-serif'}),
                dcc.Graph(id='carrier_line'),
                html.Div(html.H1("Proportion of delays in 2012"), style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
                html.Div([
                    dcc.Graph(id='carrier_pie_dep'),
                    dcc.Graph(id='carrier_pie_arr'),
                ], style={"display":"flex","justify-content":"center","align-items":"center"}),
                html.Div(html.H1("Proportion of delays by months"), style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
                html.Div([
                    dcc.Graph(id='carrier_bar_dep'),
                    dcc.Graph(id='carrier_bar_arr'),
                ], style={"display":"flex","justify-content":"center","align-items":"center"}),
                html.Div(html.H1("Historical breakdown of delays by years"), style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
                html.Div([
                    dcc.Graph(id='carrier_hist_delay_dep'),
                    dcc.Graph(id='carrier_hist_delay_arr'),
                ], style={"display":"flex","justify-content":"center","align-items":"center"})
                ,])
            ),
            dcc.Tab(className="custom-tab icon4", selected_className='custom-tab--selected', label='Same departure time', 
            children=html.Div([
                html.Div(html.H1(id = "deph_line_title"), style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
                dcc.Graph(id='deph_line'),
                html.Div(html.H1("Proportion of delays in 2012"),style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
                html.Div([
                    dcc.Graph(id='deph_pie_dep'),
                    dcc.Graph(id='deph_pie_arr'),
                ], style={"display":"flex"}),
                html.Div(html.H1("Proportion of delays in 2012 by months"), style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
                html.Div([
                    dcc.Graph(id='deph_bar_dep'),
                    dcc.Graph(id='deph_bar_arr'),
                ], style={"display":"flex","justify-content":"center","align-items":"center"}),
                html.Div(html.H1("Historical breakdown of delays by years"), style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
                html.Div([
                    dcc.Graph(id='deph_hist_delay_dep'),
                    dcc.Graph(id='deph_hist_delay_arr'),
                ], style={"display":"flex","justify-content":"center","align-items":"center"})
            ])
            ),
            dcc.Tab(className="custom-tab icon5", selected_className='custom-tab--selected', label='Same arrival time', 
            children=html.Div([
                html.Div(html.H1(id = "arrh_line_title"), style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
                dcc.Graph(id='arrh_line'),
                html.Div(html.H1("Proportion of delays in 2012"),style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
                html.Div([
                    dcc.Graph(id='arrh_pie_dep'),
                    dcc.Graph(id='arrh_pie_arr'),
                ], style={"display":"flex"}),
                html.Div(html.H1("Proportion of delays by months"),style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
                html.Div([
                    dcc.Graph(id='arrh_bar_dep'),
                    dcc.Graph(id='arrh_bar_arr'),
                ], style={"display":"flex","justify-content":"center","align-items":"center"}),
                html.Div(html.H1("Breakdown of historical delays by years"),style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
                html.Div([
                    dcc.Graph(id='arrh_hist_delay_dep'),
                    dcc.Graph(id='arrh_hist_delay_arr'),
                ], style={"display":"flex","justify-content":"center","align-items":"center"})
            ])
            ),
            dcc.Tab(className="custom-tab icon6", selected_className='custom-tab--selected', label='Upload files', 
            children=html.Div([
                html.Div(html.H1("Please upload a .csv or . xls file"),style={"font-family": 'Poppins,sans-serif'}),
                html.Div([dcc.Upload(html.Button('Upload File'))], style={"textAlign":"center","align-items":"center"}),
                html.Br(),
                dcc.Upload(['Drag and Drop or ', html.A(html.B('Select a File'))], 
                           style={
                               'width': '100%','height': '60px',
                               'lineHeight': '60px','borderWidth': '1px',
                               'borderStyle': 'dashed','borderRadius': '20px',
                               'textAlign': 'center',"align-items":"center",
                               "display":"flex", "justify-content":"center"},
                           multiple = False),
                html.Div(id='output-div'),
                html.Div(id='output-datatable')],
                              style={"textAlign":"center","align-items":"center"})
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
        
        arr_delay = "{:.3f}".format(max(float(delay['arr']), 0))
        dep_delay = "{:.3f}".format(max(float(delay['dep']), 0))
        
        return_line = ["The departure will delay by " + dep_delay + " mins" , html.Br(),
        "The arrival will delay by " + arr_delay + " mins"]
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
    Output('orig_dest_hist_delay_dep','figure'),
    Output('orig_dest_hist_delay_arr','figure'),
    Input('orig', 'value'),
    Input('dest', 'value')
    )
def update_orig_dest_hist_delay_type(orig, dest):
    try:
        hist_dep = px.histogram()
        hist_arr = px.histogram()
    except ValueError:
        hist_dep = px.histogram()
        hist_arr = px.histogram()       
    if all([orig, dest]):
        hist_dep, hist_arr = update_delay_type(orig_dest_dep_df, orig_dest_arr_df,
                                             [("origin_airport_code", orig), ("dest_airport_code", dest)])
    return hist_dep, hist_arr

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
    Output('carrier_hist_delay_dep','figure'),
    Output('carrier_hist_delay_arr','figure'),
    Input('carrier', 'value')
    )
def update_carrier_hist_delay_type(carrier):
    try:
        hist_dep = px.histogram()
        hist_arr = px.histogram()
    except ValueError:
        hist_dep = px.histogram()
        hist_arr = px.histogram()       
    if carrier:
        hist_dep, hist_arr = update_delay_type(carrier_dep_df, carrier_arr_df, 
                                             [("u_carrier", carrier)])
    return hist_dep, hist_arr

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
    Output('deph_hist_delay_dep','figure'),
    Output('deph_hist_delay_arr','figure'),
    [Input('time_slider', 'value')]
    )
def update_deph_hist_delay_type(time_slider):
    try:
        hist_dep = px.histogram()
        hist_arr = px.histogram()
    except ValueError:
        hist_dep = px.histogram()
        hist_arr = px.histogram()       
    if time_slider:
        dep, arr = time_slider
        dep = dep%24
        hist_dep, hist_arr = update_delay_type(deph_dep_df, deph_arr_df,
                                             [("dep_hour", dep)])
    return hist_dep, hist_arr

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

@app.callback(
    Output('arrh_hist_delay_dep','figure'),
    Output('arrh_hist_delay_arr','figure'),
    [Input('time_slider', 'value')]
    )
def update_arrh_pie_delay_type(time_slider):
    try:
        hist_dep = px.histogram()
        hist_arr = px.histogram()
    except ValueError:
        hist_dep = px.histogram()
        hist_arr = px.histogram()      
    if time_slider:
        dep, arr = time_slider
        arr = arr%24
        hist_dep, hist_arr = update_delay_type(arrh_dep_df, arrh_arr_df,
                                             [("arr_hour", arr)])
    return hist_dep, hist_arr

@app.callback(Output('Mygraph', 'figure'), [
Input('upload-data', 'contents'),
Input('upload-data', 'filename')
])
def update_graph(contents, filename):
    x = []
    y = []
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)
        df = df.set_index(df.columns[0])
        x=df['DATE']
        y=df['TMAX']
    fig = go.Figure(
        data=[
            go.Scatter(
                x=x, 
                y=y, 
                mode='lines+markers')
            ],
        layout=go.Layout(
            plot_bgcolor=colors["graphBackground"],
            paper_bgcolor=colors["graphBackground"]
        ))
    return fig


def parse_data(contents, filename):
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        if "csv" in filename:
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif "xls" in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif "txt" or "tsv" in filename:
            # Assume that the user upl, delimiter = r'\s+'oaded an excel file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), delimiter=r"\s+")
    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])

    return df


@app.callback(
    Output("output-data-upload", "children"),
    [Input("upload-data", "contents"), Input("upload-data", "filename")],
)


def update_table(contents, filename):
    table = html.Div()

    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_data(contents, filename)

        table = html.Div(
            [
                html.H5(filename),
                dash_table.DataTable(
                    data=df.to_dict("rows"),
                    columns=[{"name": i, "id": i} for i in df.columns],
                ),
                html.Hr(),
                html.Div("Raw Content"),
                html.Pre(
                    contents[0:200] + "...",
                    style={"whiteSpace": "pre-wrap", "wordBreak": "break-all"},
                ),
            ]
        )

    return table

@app.callback(Output('output-div', 'children'),
              Input('submit-button','n_clicks'),
              State('stored-data','data'),
              State('xaxis-data','value'),
              State('yaxis-data', 'value'))
def make_graphs(n, data, x_data, y_data):
    if n is None:
        return no_update
    else:
        bar_fig = px.bar(data, x=x_data, y=y_data)
        # print(data)
        return dcc.Graph(figure=bar_fig)

if __name__ == '__main__':
    app.run_server(debug=True)
