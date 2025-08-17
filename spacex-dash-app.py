import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Load the data
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create unique launch site options for dropdown
site_options = [
    {'label': 'All Sites', 'value': 'ALL'}
] + [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]

# Create a dash application
app = dash.Dash(__name__)

# Create app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    # Dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=site_options,
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),
    # Pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    html.P("Payload range (Kg):"),
    # Slider
    dcc.RangeSlider(
        id='payload-slider',
        min=int(min_payload),
        max=int(max_payload),
        step=1000,
        marks={int(i): str(int(i)) for i in range(int(min_payload), int(max_payload)+1, 1000)},
        value=[int(min_payload), int(max_payload)]
    ),
    # Scatter chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Pie chart callback
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(selected_site):
    if selected_site == 'ALL':
        fig = px.pie(
            spacex_df,
            names='Launch Site',
            values='class',
            title='Total Success Launches by Site')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        fig = px.pie(
            filtered_df,
            names='class',
            title=f"Success vs Failure for {selected_site}")
        fig.update_traces(labels=['Failure', 'Success'])
    return fig

# Scatter plot callback
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'), Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, selected_payload):
    min_pl, max_pl = selected_payload
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= min_pl) & 
        (spacex_df['Payload Mass (kg)'] <= max_pl)
    ]
    if selected_site == 'ALL':
        fig = px.scatter(
            filtered_df, x='Payload Mass (kg)', y='class',
            color='Booster Version Category',
            title='Correlation between Payload and Outcome for All Sites',
            hover_data=['Launch Site']
        )
    else:
        site_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(
            site_df, x='Payload Mass (kg)', y='class',
            color='Booster Version Category',
            title=f'Correlation between Payload and Outcome for {selected_site}',
            hover_data=['Launch Site']
        )
    return fig

# Run the app
if __name__ == '__main__':
    app.run(port=8051)
