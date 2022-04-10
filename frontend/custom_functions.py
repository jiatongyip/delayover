import plotly.express as px
import pandas as pd
from datetime import date
import math

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

        if sum(dep_df['count']) == 0:
            pie_plot_dep = px.pie()
            bar_plot_dep = px.bar()
        else:
            # generate delay proportion for departure in 2012
            dep_yr_prop = sum(dep_df['count'] * dep_df['prop']) / sum(dep_df['count']) * 100
            pie_plot_dep = px.pie(pd.DataFrame({"Status": ["delayed", "not delayed"], "Proportion": [dep_yr_prop, 100 - dep_yr_prop]}),
                values = 'Proportion', 
                names = 'Status',
                title = "% of delay in 2012 departures",
            )
            bar_plot_dep = px.bar(dep_df, x="mon", y=["delayed", "not delayed"], title="% breakdown for departure delay in each month",
                            labels = {'mon': "Month in 2012", 'value': 'Proportion', 'variable': 'Status'})
            bar_plot_dep.update_layout(
                xaxis = {"dtick": 1, "ticktext": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                        "tickvals": list(range(1, 13))},
                legend={'title_text':'Status'}
            )
        if sum(arr_df['count']) == 0:
            pie_plot_arr = px.pie()
            bar_plot_arr = px.pie()
        else:
            # generate arrival proportion for departure in 2012        
            arr_yr_prop = sum(arr_df['count'] * arr_df['prop']) / sum(arr_df['count']) * 100
            pie_plot_arr = px.pie(pd.DataFrame({"Status": ["delayed", "not delayed"], "Proportion": [arr_yr_prop, 100 - arr_yr_prop]}),
                values = 'Proportion', 
                names = 'Status',
                title = "% of delay in 2012 arrivals",
            )
            bar_plot_arr = px.bar(arr_df, x="mon", y=["delayed", "not delayed"], title="% breakdown for arrival delay in each month",
                            labels = {'mon': "Month in 2012", 'value': 'Proportion', 'variable': 'Status'})
            bar_plot_arr.update_layout(
                xaxis = {"dtick": 1, "ticktext": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                        "tickvals": list(range(1, 13))},
                legend={'title_text':'Status'}
            )
        return pie_plot_dep, pie_plot_arr, bar_plot_dep, bar_plot_arr

def update_delay_type(dep_df, arr_df, col_list):
        for (col, val) in col_list:
            dep_df = dep_df[dep_df[col] == val]
            arr_df = arr_df[arr_df[col] == val]
        # classify delay types for departure
        dep_df['delay'] = pd.cut(
            x = dep_df['mean'],
            bins = [-1*math.inf, 0, 15, 45, math.inf],
            labels = ["No delay", "Slight delay", "Moderate delay", "Severe delay"]
        )
        hist_dep = px.histogram(dep_df, 
            x='yr', 
            color='delay', 
            barmode='group',
            title = "of departure delays"
        )
        hist_dep.update_layout(xaxis_title="Year")
        # classify delay types for arrival
        arr_df['delay'] = pd.cut(
            x = arr_df['mean'],
            bins = [-1*math.inf, 0, 15, 45, math.inf],
            labels = ["No delay", "Slight delay", "Moderate delay", "Severe delay"]
        )
        hist_arr = px.histogram(arr_df, 
            x='yr', 
            color='delay', 
            barmode='group',
            title = "of arrival delays"
        )
        hist_arr.update_layout(xaxis_title="Year")
        return hist_dep, hist_arr
