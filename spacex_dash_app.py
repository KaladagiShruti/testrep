# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

site_options = [{"label": "ALL", "value": "ALL"}] + [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]


# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                  dcc.Dropdown(id='input-site',
                                                options=site_options,
                                                value='ALL',
                                                placeholder="place holder here",
                                                searchable=True
                                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='pie-chart')),
                                html.Br(),
                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={i: f'{i}' for i in range(0, 10001, 1000)},
                                                value=[0, 10000]),
                                html.Br(),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])
                                # Callback function to update pie chart based on selected launch site

@app.callback(
    Output(component_id='pie-chart', component_property='figure'),
    Input(component_id='input-site', component_property='value')
)
def get_pie_chart(selected_site):
    print(f"{selected_site}")
    filtered_df = spacex_df
    if selected_site == 'ALL':
        fig = px.pie(spacex_df, 
                        values='class', 
                        names='Launch Site', 
                        title='Total Success Launches by Site')
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        success_count = filtered_df[filtered_df['class'] == 1]['class'].count()
        failed_count = filtered_df[filtered_df['class'] == 0]['class'].count()
        fig = px.pie(names=['Success', 'Failed'], 
                     values=[success_count, failed_count], 
                     title=f'Success vs. Failed Launches for {selected_site}')
        return fig


# TASK 2:
# Add a callback function for `input-site` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    [Input('input-site', 'value')]
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        fig = px.pie(spacex_df, 
                     names='Launch Site', 
                     values='class', 
                     title='Total Success Launches by Site',
                     color_discrete_sequence=px.colors.sequential.RdBu)
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        fig = px.pie(filtered_df, 
                     names='class', 
                     title=f'Success vs. Failed Launches for {selected_site}',
                     color_discrete_sequence=px.colors.sequential.RdBu)
        fig.update_layout(
            legend=dict(
                title='Launch Outcome',
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            ),
            legend_title_text='Outcome',
            legend_traceorder='reversed'
        )
    return fig
# TASK 4:
# Add a callback function for `input-site` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='input-site', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    # Filter DataFrame based on selected launch site
    if selected_site == 'ALL':
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                                (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
    else:
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                                (spacex_df['Payload Mass (kg)'] <= payload_range[1]) &
                                (spacex_df['Launch Site'] == selected_site)]

    # Create scatter plot
    fig = px.scatter(filtered_df, 
                     x='Payload Mass (kg)', 
                     y='class', 
                     color='Booster Version Category', 
                     title='Correlation between Payload and Launch Success',
                     color_discrete_sequence=px.colors.qualitative.Dark24)

    # Update marker size and style
    fig.update_traces(marker=dict(size=12),
                      selector=dict(mode='markers'))

    return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
