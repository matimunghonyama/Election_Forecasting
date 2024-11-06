import dash
from dash import html, dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import datetime
import numpy as np

# Initialize the Dash app
app = dash.Dash(__name__)

# Sample data - replace with your actual data source
def generate_sample_data():
    dates = [datetime.datetime.now() - datetime.timedelta(days=x) for x in range(30, 0, -1)]
    # Sample probabilities - replace with your actual probability calculations
    probabilities = np.clip(50 + np.cumsum(np.random.normal(0, 2, 30)), 0, 100)
    return dates, probabilities

dates, probabilities = generate_sample_data()

app.layout = html.Div([
    html.H1("2024 Election Probability Tracker", 
            style={'textAlign': 'center', 'color': '#2c3e50', 'marginTop': '20px'}),
    
    # Main probability display
    html.Div([
        html.Div([
            html.H2("Current Win Probability", 
                    style={'textAlign': 'center', 'color': '#7f8c8d'}),
            html.H1(f"{probabilities[-1]:.1f}%", 
                    id='current-probability',
                    style={'textAlign': 'center', 'color': '#2c3e50', 'fontSize': '48px'})
        ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'borderRadius': '10px'}),
        
        # Probability trend graph
        dcc.Graph(
            id='probability-graph',
            figure={
                'data': [
                    go.Scatter(
                        x=dates,
                        y=probabilities,
                        mode='lines+markers',
                        name='Win Probability',
                        line=dict(color='#3498db', width=3),
                        marker=dict(size=8)
                    )
                ],
                'layout': go.Layout(
                    title='Win Probability Trend',
                    xaxis={'title': 'Date'},
                    yaxis={'title': 'Probability (%)', 'range': [0, 100]},
                    hovermode='x unified',
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                )
            }
        )
    ], style={'maxWidth': '800px', 'margin': 'auto', 'padding': '20px'}),
    
    # Interval component for updates
    dcc.Interval(
        id='interval-component',
        interval=3600*1000,  # update every hour
        n_intervals=0
    )
])

# Callback to update the probability
@app.callback(
    [Output('current-probability', 'children'),
     Output('probability-graph', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_metrics(n):
    # Replace this with your actual data update logic
    dates, probabilities = generate_sample_data()
    
    new_figure = {
        'data': [
            go.Scatter(
                x=dates,
                y=probabilities,
                mode='lines+markers',
                name='Win Probability',
                line=dict(color='#3498db', width=3),
                marker=dict(size=8)
            )
        ],
        'layout': go.Layout(
            title='Win Probability Trend',
            xaxis={'title': 'Date'},
            yaxis={'title': 'Probability (%)', 'range': [0, 100]},
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
        )
    }
    
    return f"{probabilities[-1]:.1f}%", new_figure

if __name__ == '__main__':
    app.run_server(debug=True)