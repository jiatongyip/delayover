import plotly.express as px
import pandas as pd
from datetime import date
import math
import datetime
import requests
import base64
import io
from dash import Dash, dcc, html, no_update, dash_table

flask_url = 'http://127.0.0.1:5000/prediction'

with open("data/allowable_values.txt", "r") as file:
    allowable_values = eval(file.read())

# custom function
def get_distance(airport_pairs, orig, dest):
    dist = airport_pairs[(airport_pairs.origin_airport_code == orig) &
    (airport_pairs.dest_airport_code == dest)]['distance_grp'].values[0]
    return dist

def get_yr_mon_dow(date_value): 
    date_object = date.fromisoformat(date_value)
    yr = date_object.year
    mon = date_object.month
    dayofweek = date_object.weekday()
    return yr, mon, dayofweek

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

        dep_df["delayed"] = dep_df["prop"] * 100
        dep_df["not delayed"] = 100 - dep_df["delayed"]
        arr_df["delayed"] = arr_df["prop"] * 100
        arr_df["not delayed"] = 100 - arr_df["delayed"]

        try:
#            pie_plot_dep = px.pie()
            bar_plot_dep = px.bar()
#            pie_plot_arr = px.pie()
            bar_plot_arr = px.bar()
        except:
#            pie_plot_dep = px.pie()
            bar_plot_dep = px.bar()
#            pie_plot_arr = px.pie()
            bar_plot_arr = px.bar()

        if not sum(dep_df['count']) == 0:
            # generate delay proportion for departure in 2012
            # dep_yr_prop = sum(dep_df['count'] * dep_df['prop']) / sum(dep_df['count']) * 100
            # pie_plot_dep = px.pie(pd.DataFrame({"Status": ["delayed", "not delayed"], "Proportion": [dep_yr_prop, 100 - dep_yr_prop]}),
            #     values = 'Proportion', 
            #     names = 'Status',
            #     title = "% of delay in 2012 departures",
            # )
            bar_plot_dep = px.bar(dep_df, x="mon", y=["delayed", "not delayed"], title="% breakdown for departure delay in each month",
                            labels = {'mon': "Month in 2012", 'value': 'Proportion', 'variable': 'Status'})
            bar_plot_dep.update_layout(
                xaxis = {"dtick": 1, "ticktext": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                        "tickvals": list(range(1, 13))},
                legend={'title_text':'Status'}
            )
        if not sum(arr_df['count']) == 0:
            # generate arrival proportion for departure in 2012        
            # arr_yr_prop = sum(arr_df['count'] * arr_df['prop']) / sum(arr_df['count']) * 100
            # pie_plot_arr = px.pie(pd.DataFrame({"Status": ["delayed", "not delayed"], "Proportion": [arr_yr_prop, 100 - arr_yr_prop]}),
            #     values = 'Proportion', 
            #     names = 'Status',
            #     title = "% of delay in 2012 arrivals",
            # )
            bar_plot_arr = px.bar(arr_df, x="mon", y=["delayed", "not delayed"], title="% breakdown for arrival delay in each month",
                            labels = {'mon': "Month in 2012", 'value': 'Proportion', 'variable': 'Status'})
            bar_plot_arr.update_layout(
                xaxis = {"dtick": 1, "ticktext": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                        "tickvals": list(range(1, 13))},
                legend={'title_text':'Status'}
            )
        # pie_plot_dep.update_traces(textposition = 'outside' , textinfo = 'percent+label')
        # pie_plot_arr.update_traces(textposition = 'outside' , textinfo = 'percent+label')
        return (
            # pie_plot_dep, pie_plot_arr, 
            bar_plot_dep, bar_plot_arr)

def update_delay_type(dep_df, arr_df, col_list):
        for (col, val) in col_list:
            dep_df = dep_df[dep_df[col] == val]
            arr_df = arr_df[arr_df[col] == val]

        try: 
            hist_dep = px.histogram()
            hist_arr = px.histogram() 
        except:
            hist_dep = px.histogram()
            hist_arr = px.histogram()         
        # classify delay types for departure
        dep_df['Delay'] = pd.cut(
            x = dep_df['mean'],
            bins = [-1*math.inf, 15, 45, math.inf],
            labels = ["No/Slight delay: < 15 min", "Moderate delay: 15 - 45 min", "Severe delay: > 45 min"]
        )
        hist_dep = px.histogram(dep_df, 
            x='yr', 
            color='Delay', 
            barmode='group',
            title = "Number of departure delays over the years",
            category_orders={"Delay": ["No/Slight delay: < 15 min", "Moderate delay: 15 - 45 min", "Severe delay: > 45 min"]},
            labels = {'yr': 'Year', 'count': 'Count'}
        )
        hist_dep.update_layout(yaxis_title="Count")
        # classify delay types for arrival
        arr_df['Delay'] = pd.cut(
            x = arr_df['mean'],
            bins = [-1*math.inf, 15, 45, math.inf],
            labels = ["No/Slight delay: < 15 min", "Moderate delay: 15 - 45 min", "Severe delay: > 45 min"]
        )
        hist_arr = px.histogram(arr_df, 
            x='yr', 
            color='Delay', 
            barmode='group',
            title = "Number of arrival delays over the years",
            category_orders={"Delay":["No/Slight delay: < 15 min", "Moderate delay: 15 - 45 min", "Severe delay: > 45 min"]},
            labels = {'yr': 'Year', 'count': 'Count'}
        )
        hist_dep.update_layout(yaxis_title="Count", xaxis_title="Year", xaxis = dict(tickmode = 'linear'))
        hist_arr.update_layout(yaxis_title="Count", xaxis_title="Year", xaxis = dict(tickmode = 'linear'))
        return hist_dep, hist_arr

def check_date(year, month, day):
    try:
        newDate = datetime.datetime(year, month, day)
        correctDate = True
    except (ValueError, TypeError, NameError):
        correctDate = False
    return correctDate

def get_pred_for_upload(year, month, day, orig, dest, carrier, dep, arr, dist):
    dayofweek = datetime.date(year, month, day).weekday()

    param1 = {'yr': year, 'mon':month, 'day_of_week': dayofweek, 
    'dep_hour':dep,'arr_hour':arr, 'u_carrier': carrier,
    'origin_airport_code':orig, 'dest_airport_code': dest, 
    'distance_grp':dist}

    delay = requests.get(flask_url, params=param1).json()
    return [max(float(delay['dep']), 0), max(float(delay['arr']),0)]

def generate_pred_table(df, airport_pairs, allowable_values):
    pred_df = pd.DataFrame(columns = ['year', 'month', 'day', 'origin', 'dest', 'carrier', 'dep_hour', 'arr_hour',
                                    'dep_delay', 'arr_delay'])
    for index, row in df.iterrows():
        # check for additional columns
        if len(row.dropna()) != 8:
            continue
        year, month, day, origin, dest, carrier, deph, arrh = row[0:8]
        try: 
            year = int(year)
            month = int(month)
            day = int(day)
            deph = int(deph)
            arrh = int(arrh)
        except:
            continue
        if year not in allowable_values['year']:
            continue
        if not check_date(year, month, day):
            continue
        if (
            (origin not in allowable_values['airport']) or 
            (dest not in allowable_values['airport']) or
            (carrier not in allowable_values['carrier']) or
            (deph not in range(0, 24)) or
            (arrh not in range(0, 24))
        ):
            continue
        try:
            dist = get_distance(airport_pairs, origin, dest)
        except:
            continue
        row = [year, month, day, origin, dest, carrier, deph, arrh] + get_pred_for_upload(
            year, month, day, origin, dest, carrier, deph, arrh, dist)
        
        pred_df.loc[len(pred_df)] = row

    return pred_df

def read_upload_data(contents, filename):
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    if "csv" in filename:
        # Assume that the user uploaded a CSV file
        df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), header=None)
    elif "xls" in filename:
        # Assume that the user uploaded an excel file
        df = pd.read_excel(io.BytesIO(decoded), header=None)
    return df

def get_tab_children(tab):
    ls = [
        html.H1(id = tab + "_line_title", style={"text-align":"center","padding-top":"10px","font-family": 'Poppins,sans-serif'}),
        html.H3("The plot below shows how the delays vary in 2011 and 2012."),
        dcc.Graph(id=tab + '_line'),
        html.H3("Let's break it down to observe the patterns in different months."),
        # html.H1(" Proportion of delays in 2012", style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
        # html.Div(id=tab + '_pie', style={"display":"flex","align-items":"center","justify-content":"center"}),
        html.H1("Proportion of delays by months", style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
        html.Div(id=tab + '_bar', style={"display":"flex","align-items":"center","justify-content":"center"}),
        html.H1("Historical breakdown of delays by years", style={"text-align":"center","font-family": 'Poppins,sans-serif'}),
        html.Div(id=tab + '_hist_delay', style={"display":"flex","align-items":"center","justify-content":"center"})
        ]
    return ls