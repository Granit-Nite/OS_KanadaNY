from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
 
# Skapa en DataFrame
dff = pd.read_csv("athlete_events.csv")
# dff["Age"].fillna(dff["Age"].median(), inplace= True)

dff = dff.drop(["Height", "Weight"], axis= 1)
 
 
# Initiera Dash-applikationen
app = Dash(__name__)
 
# Layout för Dash-applikationen
app.layout = html.Div([
    html.H1(
        children = "Landanalys i OS historia",
         style= {"textAlign": "center"} ),
   
    # Dropdown för val av land
    dcc.Dropdown(
        id='land_d',
        options=[{'label': land, 'value': land} for land in dff['NOC'].unique()],
        value='SWE',
        clearable=False,
        style = {"width": "50%"}
    ),
    dcc.Dropdown(
        id='medal_d',
        options=[
            {"label": "De sporter landet fått flest medaljer i", "value": "De sporter landet fått flest medaljer i"},
            {"label": "Antal medaljer per OS", "value": "Antal medaljer per OS"},
            {"label": "Histogram över åldrar", "value": "Histogram över åldrar"}],
        value='What do you want to know?',
        clearable=False,
        style = {"width": "50%"}
    ),
   
    # Diagram över de sporter landet fått flest medaljer i
    dcc.Graph(id='sporter-graf')
])
 
@app.callback(
    Output('sporter-graf', 'figure'),
    [Input('land_d', 'value'), Input("medal_d", "value")]
)
def update_sporter_graf(land, medal):
    fig = go.Figure()
   
    if medal == "De sporter landet fått flest medaljer i":
       canada_os = dff[dff["NOC"] == land]
       medal_sport = canada_os.pivot_table(index = "Sport", columns= "Medal", aggfunc= "size")
       number_medals1 = medal_sport.sum(axis= 1)
       number_medals1 = number_medals1.astype(int)
       number_medals1 = number_medals1.sort_values(ascending= True)
 
       fig = px.bar(number_medals1,
                    orientation='h',
                    labels={'Sport': 'Sporter', 'value': 'Antal Medaljer'},
                    title='Antal Medaljer per sport')
       
       fig.update_layout(
        plot_bgcolor='white',   # Plotområdet
        paper_bgcolor='white',  # Hela diagrammets bakgrund
        font_color='black')
       
       return fig
   
    return fig
       
 
if __name__ == '__main__':
    app.run_server(debug=True, port  = 352)
 