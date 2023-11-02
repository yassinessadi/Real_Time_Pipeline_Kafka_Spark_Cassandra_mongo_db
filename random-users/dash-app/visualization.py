from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
from pymongo import MongoClient
import pandas as pd
import datetime

app = Dash(__name__)


client = MongoClient()
client = MongoClient("mongodb://localhost:27017/")
db = client['users_profiles']
collection = db["user_collection"]
data_from_mongo = list(collection.find())
df = pd.DataFrame(data_from_mongo)

gender_per_nat = df.groupby(["nationality","gender"])["nationality"].apply(lambda x:x.count()).reset_index(name="count")

fig = px.bar(gender_per_nat, x="nationality", y="count", color="gender", barmode="group")

app.layout = html.Div([
    html.H1(children='Users Information', style={'textAlign':'center'}),
    dcc.Graph(
        id='nat-gender-graph',
        figure=fig),
    html.Div(id="live-update-text"),

    dcc.Interval(
            id='interval-component',
            interval=1000,
            n_intervals=0
        )
    ])

@callback(Output('live-update-text', 'children'),
              Input('interval-component', 'n_intervals'))
def update_metrics(n_intervals):
    style = {'padding': '5px', 'fontSize': '16px'}
    return [
        html.Span(''.format(datetime.datetime.now()), style=style),
    ]

if __name__ == '__main__':
    app.run(debug=True)
