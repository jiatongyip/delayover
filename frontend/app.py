# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.


from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_html_components as html
import dash_daq as daq


app = Dash(__name__)

df = pd.read_csv('flight_data.csv')

def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])


fig = px.bar(df, x="hour", y="count", barmode="group")

app.layout = html.Div(
        id='forna-body',
        className='app-body',
        children=[
                    dcc.Tabs(id='forna-tabs', value='what-is', children=[
                        dcc.Tab(
                            label='Overview',
                            children=html.Div(className='control-tab', children=[
                                html.H4(className='Overview', children='What are airplanes delay'),
                                dcc.Markdown('''
                                How are these categories defined?

    Air Carrier: The cause of the cancellation or delay was due to circumstances within the airline's control (e.g. maintenance or crew problems, aircraft cleaning, baggage loading, fueling, etc.).
    Extreme Weather: Significant meteorological conditions (actual or forecasted) that, in the judgment of the carrier, delays or prevents the operation of a flight such as tornado, blizzard or hurricane.
    National Aviation System (NAS): Delays and cancellations attributable to the national aviation system that refer to a broad set of conditions, such as non-extreme weather conditions, airport operations, heavy traffic volume, and air traffic control.
    Late-arriving aircraft: A previous flight with same aircraft arrived late, causing the present flight to depart late.
    Security: Delays or cancellations caused by evacuation of a terminal or concourse, re-boarding of aircraft because of security breach, inoperative screening equipment and/or long lines in excess of 29 minutes at screening areas.

                                '''),
                                dcc.Graph(figure=fig),
                            ])
                        ),

                        dcc.Tab(
                            label='Location',
                            children=html.Div(className='control-tab', children=[
                                html.Div(
                                    dcc.Graph(figure=fig),
                                ),
                            ])
                        ),
                        dcc.Tab(
                            label='Weather Delay',
                            children=html.Div(className='control-tab', children=[
                                html.Div(
                                    className='app-controls-block',
                                    children=[
                                        html.Div(
                                         dcc.Graph(figure=fig),
                                        )
                                    ]
                                ),
                            ])
                        ),
                        dcc.Tab(
                            label='Plot 3',
                            children=html.Div(className='control-tab', children=[
                                html.Div(
                                        dcc.Graph(figure=fig),
                                )
                            ])
                        ),
                        dcc.Tab(
                            label='Plot 4',
                            children=html.Div(className='control-tab', children=[
                                html.Div(
                                    className='app-controls-block',
                                    children=[
                                        generate_table(df),
                                    ]
                                ),
                            ])
                        )
                    ])
                ])


if __name__ == '__main__':
    app.run_server(debug=True)
