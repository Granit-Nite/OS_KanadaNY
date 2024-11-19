from dash import Dash, dcc, html, Input, Output

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Skapa en DataFrame
df = pd.read_csv("athlete_events.csv")
df["Age"].fillna(df["Age"].median(), inplace= True)
df = df.drop(["Height", "Weight"], axis= 1)

# Initiera Dash-applikationend
app = Dash(__name__)

# Layout för Dash-applikationen
app.layout = html.Div([
    html.H1(
        children = "Landanalys i OS historia",
         style= {"textAlign": "center", "color": "#FFFFFF", "backgroundColor": '#D80621'} ),
    
    html.Div([
        # Första dropdown för val av land
        html.Label("Välj ett land"),
        dcc.Dropdown(
            id='land_d',
            options=[{'label': land, 'value': land} for land in df['NOC'].unique()],
            value='CAN',
            clearable=False,
            style={"width": "45%", "display": "inline-block", "margin-right": "5px"}
        ),                                                    #Lägger till lite avstånd mellan de två dropdown
        
        # Andra dropdown för val av analys
        html.Label("Välj ett alternativ"),
        dcc.Dropdown(
            id='medal_d',
            options=[
                {"label": "Antal medaljer per sport", "value": 'Antal medaljer per sport'},
                {"label": "Antal medaljer och medaljtyp per OS", "value": "Antal medaljer och medaljtyp per OS"},
                {"label": "Åldersfördelning deltagare", "value": "Åldersfördelning deltagare"},
                {"label": 'Medaljfördelning', "value": 'Medaljfördelning'}, 
                {"label": "Medaljfördelning mellan länder i fyra sporter", "value": "Medaljfördelning mellan länder i fyra sporter"},
                {"label": "Åldersfördelning per sport", "value": "Åldersfördelning per sport"},
                {"label": "Könsfördelning topp 10", "value": "Könsfördelning topp 10"}
            ],
            value="Åldersfördelning deltagare",
            clearable=False,
            style={"width": "45%", "display": "inline-block"} #Gör att varje dropdown visas på samma rad
        )
    ],
    style={"display": "flex", "justify-content": "center"}),
    # Använder Flexbox för att centrera hela raden med dropdown-menyer
    
    # Diagram över de sporter landet fått flest medaljer i
    dcc.Graph(id='sporter-graf',
              config={'displayModeBar': True})  # Hides the toolbar 
])

@app.callback(
    Output('sporter-graf', 'figure'),
    [Input('land_d', 'value'), Input("medal_d", "value")]
)
def update_sporter_graf(land, alternativ):
    fig = go.Figure()
    def fi(fig):
        re = fig.update_layout(
                plot_bgcolor='white',   # Plotområdet
                paper_bgcolor='white',  # Hela diagrammets bakgrund
                font_color='black',
                title={'x': 0.5})
        return re
   
    if alternativ == 'Antal medaljer per sport':
       canada_os = df[df["NOC"] == land]
       medal_sport = canada_os.pivot_table(index = "Sport", columns= "Medal", aggfunc= "size")
       number_medals1 = medal_sport.sum(axis= 1)
       number_medals1 = number_medals1.astype(int)
       number_medals1 = number_medals1.sort_values(ascending= False)

       fig = px.bar(x=number_medals1.index,
                    y=number_medals1.values,
                    labels={'x': 'Sporter', 'y': 'Antal Medaljer'},
                    title='Antal medaljer per sport', # orientation= "h",
                    color=number_medals1.values,  # Color bars based on the number of medals
                    color_continuous_scale='Plasma' ) #Cividis or Inferno,Viridis, plasma, 'RdBu
       
       return fi(fig)
       
    
    elif alternativ == "Antal medaljer och medaljtyp per OS":
        canada_os = df[df["NOC"] == land]
        tabell = canada_os.pivot_table(index= "Year", columns= "Medal", aggfunc= "size")

        fig = px.bar(
                    tabell,
                    color_discrete_map={'Bronze': 'brown', 'Gold': 'gold', 'Silver': '#330C73'},
                    title="Antal medaljer och medaljtyp per OS",
                    labels={'Sport': 'Sporter', 'value': 'Antal medaljer'},
                    barmode='group')  # Gör diagrammet icke-staplat)

        return fi(fig)
    
    elif alternativ == "Åldersfördelning deltagare":
        canada_os = df[df["NOC"] == land]
        age_can = canada_os.drop_duplicates(subset= "ID")
        age = age_can["Age"]
        
        fig = px.histogram(
                           age,
                           nbins=30,
                           labels= {"value": "ålder"},
                           title='Åldersfördelning deltagare')
        
        fig.update_traces(marker_color='#D80621')
        fig.update_yaxes(title_text="Antal athleter")

        return fi(fig)
    
    elif alternativ == 'Medaljfördelning':
        sport = df[df["Sport"].isin(["Swimming", "Tennis", "Football", "Gymnastics"])&df["NOC"].isin([land, "USA", "SWE", "CHN", "GER"])]
        sport_länder = sport.pivot_table(index = "NOC", columns= ["Sport"], aggfunc= "size")

        fig = px.bar(
                    sport_länder,
                    color_discrete_map={"Swimming": 'lightblue', "Tennis": 'blue', "Football": '#330C73', "Gymnastics": "pink" },
                    title="Medaljfördelning mellan valt land & CHN, GER, SWE, USA",
                    labels={'NOC': 'Länder', 'value': 'Antal Medaljer'},
                    barmode='group')  # Gör diagrammet icke-staplat)

        return fi(fig)
    
    elif alternativ == "Medaljfördelning mellan länder i fyra sporter":
        fyra_sport = df[df["Sport"].isin(["Swimming", "Tennis", "Football", "Gymnastics"])]
        sport_pivot = fyra_sport.pivot_table(index = "NOC", columns= ["Sport", "Medal"], aggfunc= "size")
        
        medal_sums = sport_pivot.groupby(level="Sport", axis=1).sum()
        sum_medal = medal_sums.sum(axis= 1)
        sorterade_länder = sum_medal.sort_values(ascending= False)
        top_30 = sorterade_länder.head(30)
        top_länder = medal_sums.loc[list(top_30.index)]

        fig = px.bar(top_länder,
                     text_auto = True,
                    labels={'value': 'Antal medaljer i sporter', 'NOC': 'Top 30 länder'},
                    color_discrete_map={"Swimming": 'lightblue', "Tennis": 'blue', "Football": '#330C73', "Gymnastics": "pink" },
                    title="Medaljfördelning mellan länder i fyra sporter") 
       
        return fi(fig)
    
    elif alternativ == "Åldersfördelning per sport":
        valda_sporter = df[df["Sport"].isin(["Swimming", "Tennis", "Football", "Gymnastics"])]
        four_sports = valda_sporter.pivot_table(index = "Age", columns= ["Sport"],aggfunc= "size")

        fig = px.bar(four_sports,
                    text_auto='.2s', #True
                    labels={'value': 'Antal personer', 'Age': 'Ålder'},
                    color_discrete_map={"Swimming": 'lightblue', "Tennis": 'blue', "Football": '#330C73', "Gymnastics": "pink" },
                    title='Åldersfördelning per sport'
                    ) 
       
        return fi(fig)
    
    elif alternativ == "Könsfördelning topp 10":
        pivot_table = df.pivot_table( index="NOC", columns=["Sex"], aggfunc="size")
        sum_sex = pivot_table.sum(axis= 1)
        sort_sex = sum_sex.sort_values(ascending= False).head(10)
        top_10 = sort_sex.index
        vald = pivot_table.loc[top_10]

        fig = px.bar(vald,
                    text_auto='.2s', #True
                    labels={'value': 'Antal personer', 'NOC': 'Länder'},
                    color_discrete_map={"M": 'lightblue', "F": 'orange'},
                    title="Könsfördelning topp 10"
                    ) 
       
        return fi(fig)
       
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port = 358)