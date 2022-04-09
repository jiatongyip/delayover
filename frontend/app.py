# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from pydoc import classname
from dash import Dash, dcc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import Dash, html, dcc
import requests

external_stylesheets = ["https://fonts.googleapis.com/css2?family=Poppins&display=swap"]

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

def gen_line_plots(dep_df, arr_df, col_list):
        for (col, val) in col_list:
            dep_df = dep_df[dep_df[col] == val]
            arr_df = arr_df[arr_df[col] == val]

        dep_df['yr_mon'] = dep_df.yr.astype(str) + "-" + dep_df.mon.map("{:02}".format)
        dep_df['type'] = "departure"
        
        arr_df['yr_mon'] = arr_df.yr.astype(str) + "-" + arr_df.mon.map("{:02}".format)
        arr_df['type'] = "arrival"
        
        df = pd.concat([dep_df[["yr_mon", "mean", "type"]], 
                        arr_df[["yr_mon", "mean", "type"]]])
        line_plot = px.line(
            df, x = "yr_mon", y = "mean", 
            color = "type", markers = True,
            labels = {'yr_mon': "Time", 'mean': 'Mean delay', 'type': 'Type'})

        return line_plot

def generate_pie_bar(dep_df, arr_df, col_list):
        col_list += [("yr", 2012)]
        for (col, val) in col_list:
            dep_df = dep_df[dep_df[col] == val]
            arr_df = arr_df[arr_df[col] == val]
        
        # generate delay proportion for departure in 2012
        dep_yr_prop = sum(dep_df['count'] * dep_df['prop']) / sum(dep_df['count']) * 100
        pie_plot_dep = px.pie(pd.DataFrame({"Status": ["delayed", "not delayed"], "Proportion": [dep_yr_prop, 100 - dep_yr_prop]}),
            values = 'Proportion', 
            names = 'Status',
            title = "% of delay in 2012 departures",
        )
        # generate arrival proportion for departure in 2012        
        arr_yr_prop = sum(arr_df['count'] * arr_df['prop']) / sum(arr_df['count']) * 100
        pie_plot_arr = px.pie(pd.DataFrame({"Status": ["delayed", "not delayed"], "Proportion": [arr_yr_prop, 100 - arr_yr_prop]}),
            values = 'Proportion', 
            names = 'Status',
            title = "% of delay in 2012 arrivals",
        )
        

        dep_df["delayed"] = dep_df["prop"] * 100
        dep_df["not delayed"] = 100 - dep_df["delayed"]
        arr_df["delayed"] = arr_df["prop"] * 100
        arr_df["not delayed"] = 100 - arr_df["delayed"]
        bar_plot_dep = px.bar(dep_df, x="mon", y=["delayed", "not delayed"], title="% breakdown for departure delay in each month",
                         labels = {'mon': "Month in 2012", 'value': 'Proportion', 'variable': 'Status'})
        bar_plot_dep.update_layout(
            xaxis = {"dtick": 1, "ticktext": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                    "tickvals": list(range(1, 13))},
            legend={'title_text':'Status'}
        )
        bar_plot_arr = px.bar(arr_df, x="mon", y=["delayed", "not delayed"], title="% breakdown for arrival delay in each month",
                         labels = {'mon': "Month in 2012", 'value': 'Proportion', 'variable': 'Status'})
        bar_plot_arr.update_layout(
            xaxis = {"dtick": 1, "ticktext": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                    "tickvals": list(range(1, 13))},
            legend={'title_text':'Status'}
        )

        return pie_plot_dep, pie_plot_arr, bar_plot_dep, bar_plot_arr


# app
app.layout = html.Div([
    html.Div([html.H1('Flight Delay'),
    html.Img(src=app.get_asset_url('plane.svg'))
    ],style={"background-color":"#013E87","padding":"10px 0","color":"#fff","text-align":"center","font-family": 'Poppins,sans-serif',"font-size":"20px"}),
    dcc.Tabs(className='custom-tabs-container',
        children=[
            dcc.Tab(className="custom-tab",
            selected_className='custom-tab--selected',
                label='Predicted Delay',
                children=html.Div(
                    children=[
                        html.Div(html.H2(id='pred'),style={"font-size":"16px","padding-top":"10px"}),
                        html.Div([
                                html.Div(html.H3("Select Day of Week:"),style={"padding-right":"5px"}),
                                html.Div( dcc.RadioItems(id='dayofweek',
                                options=options_dict['dayofweek'],
                                # placeholder="Select day of week"
                                value = 1
                                ),style={"padding":"10px 0"}),
    
                                html.Div(html.H3("Select Year:"),style={"padding-left":"20px","padding-right":"5px"}),          
                                html.Div(dcc.Dropdown(id='year',
                                options=options_dict['year'],
                                value = 2013
                                ),style={"padding":"10px 20px","width":"100px"}),

                                html.Div( html.H3("Select Month:"),style={"padding-left":"20px","padding-right":"5px"}),
                                html.Div( dcc.Dropdown(id='month',
                                options=options_dict['month'],
                                value = 1
                                 ),style={"padding":"10px 20px","width":"100px"})

                        ],style={"display":"flex","padding":"10px 0","align-items":"center","font-family": 'Poppins,sans-serif'}),
                        html.H3("Select Departure and Arrival time:"),  
                        dcc.RangeSlider(
                            min=0, max=48, step=1,
                            marks={0: '0000', 6: '0600', 12: '1200', 18: '1800',
                                24: '0000', 30: '0600', 36: '1200', 42: '1800',
                                48: '0000',},
                            value=[4, 24], allowCross = False,
                            id='time_slider'),
                        html.Div(id='time_slider_output'),

                        html.Div(children=[
                            html.Div(html.H3("Select Origin:"),
                            style={"padding-right":"5px"}),
                            html.Div(dcc.Dropdown(id='orig', value = "ATL"),
                            style={"padding":"10px 20px","width":"100px"}),

                            html.Div(html.H3("Select Destination:"),
                            style={"padding-left":"20px","padding-right":"5px"} ),
                            html.Div(dcc.Dropdown(id='dest', value = "ABE"),
                            style={"padding":"10px 20px","width":"100px"}),

                            html.Div(html.H3("Select Carrier:"),
                            style={"padding-left":"20px","padding-right":"5px"}),
                            html.Div(dcc.Dropdown(id='carrier', value = 'AA',
                                    options=options_dict['carrier']),
                                    style={"padding":"10px 20px","width":"200px"})


                        ],style={"display":"flex","padding":"10px 0","align-items":"center","font-family": 'Poppins,sans-serif'}),
                       
                    ],style={"font-family": 'Poppins,sans-serif'},
                )
            ),
        dcc.Tab(className="custom-tab",
        selected_className='custom-tab--selected',
            label='Same origin and destination', 
            children=html.Div(
                [html.H1(id = "orig_dest_line_title"),
                dcc.Graph(id='orig_dest_line'),
                html.H1("let's look at the proportion of delays in 2012"),
                dcc.Graph(id='orig_dest_pie_dep'),
                dcc.Graph(id='orig_dest_pie_arr'),
                html.H1("breaking down by months"),
                dcc.Graph(id='orig_dest_bar_dep'),
                dcc.Graph(id='orig_dest_bar_arr'),
                ]
            )
        ),
        dcc.Tab(className="custom-tab",
        selected_className='custom-tab--selected',
            label='Same carrier', 
            children=html.Div(
                [html.H1(id = "carrier_line_title"),
                dcc.Graph(id='carrier_line'),
                html.H1("let's look at the proportion of delays in 2012"),
                dcc.Graph(id='carrier_pie_dep'),
                dcc.Graph(id='carrier_pie_arr'),
                html.H1("breaking down by months"),
                dcc.Graph(id='carrier_bar_dep'),
                dcc.Graph(id='carrier_bar_arr'),
                ]
            )
        ),
        dcc.Tab(className="custom-tab",
        selected_className='custom-tab--selected',
            label='Same departure time', 
            children=html.Div(
                [html.H1(id = "deph_line_title"),
                dcc.Graph(id='deph_line'),
                html.H1("let's look at the proportion of delays in 2012"),
                dcc.Graph(id='deph_pie_dep'),
                dcc.Graph(id='deph_pie_arr'),
                html.H1("breaking down by months"),
                dcc.Graph(id='deph_bar_dep'),
                dcc.Graph(id='deph_bar_arr'),
                ]
            )
        ),
        dcc.Tab(className="custom-tab",
        selected_className='custom-tab--selected',
            label='Same arrival time', 
            children=html.Div(
                [html.H1(id = "arrh_line_title"),
                dcc.Graph(id='arrh_line'),
                html.H1("let's look at the proportion of delays in 2012"),
                dcc.Graph(id='arrh_pie_dep'),
                dcc.Graph(id='arrh_pie_arr'),
                html.H1("breaking down by months"),
                dcc.Graph(id='arrh_bar_dep'),
                dcc.Graph(id='arrh_bar_arr'),]
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

    return ["The departure will delay by " + dep_delay + " mins" , html.Br(),
    "The arrival will delay by " + arr_delay + " mins"
    ]

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
        line_plot = gen_line_plots(orig_dest_dep_df, orig_dest_arr_df, [("origin_airport_code", orig), ("dest_airport_code", dest)])
        line_title = "Let's look at the delays for flights from " + orig + " to " + dest + "!"

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
        line_title = "Let's look at the delays for flights by " + carrier_dict[carrier] + "!"

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
        line_title = "Let's look at the delays for flights departing at " + "{:02}".format(dep) + "00 hours!"

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
        line_title = "Let's look at the delays for flights arriving at " + "{:02}".format(arr) + "00 hours!"

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
