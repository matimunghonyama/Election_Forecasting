import dash
from dash import html, dcc, Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from joblib import load

# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        'https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css'
    ]
)

# Load the ML model
ml_model = load('election_model.joblib')

# Define Dash layout
app.layout = html.Div([
    # Header
    html.H1(
        "2024 Election ML-Enhanced Probability Dashboard",
        className="text-3xl font-bold mb-6 px-4"
    ),
    
    # Main content container
    html.Div([
        # Left column - Input controls
        html.Div([
            # Economic Indicators Section
            html.Div([
                html.H2("Economic Indicators", className="text-xl font-semibold mb-4"),
                
                # Unemployment Rate Slider
                html.Div([
                    html.Label("Unemployment Rate (%):", className="font-medium"),
                    dcc.Slider(
                        id='unemployment-slider',
                        min=3,
                        max=8,
                        step=0.1,
                        value=5.2,
                        marks={i: f"{i}%" for i in range(3, 9)}
                    ),
                    html.Div(id="unemployment-value", className="mt-2 text-gray-600"),
                ], className="mb-6"),
                
                # GDP Growth Slider
                html.Div([
                    html.Label("GDP Growth (%):", className="font-medium"),
                    dcc.Slider(
                        id='gdp-slider',
                        min=-2,
                        max=6,
                        step=0.1,
                        value=2.1,
                        marks={i: f"{i}%" for i in range(-2, 7)}
                    ),
                    html.Div(id="gdp-value", className="mt-2 text-gray-600"),
                ], className="mb-6"),
            ], className="mb-8"),
            
            # Political Indicators Section
            html.Div([
                html.H2("Political Indicators", className="text-xl font-semibold mb-4"),
                
                # Presidential Approval Slider
                html.Div([
                    html.Label("Presidential Approval (%):", className="font-medium"),
                    dcc.Slider(
                        id='approval-slider',
                        min=30,
                        max=70,
                        step=1,
                        value=43,
                        marks={i: f"{i}%" for i in range(30, 71, 5)}
                    ),
                    html.Div(id="approval-value", className="mt-2 text-gray-600"),
                ], className="mb-6"),
                
                # Generic Ballot Margin Slider
                html.Div([
                    html.Label("Generic Ballot Margin (%):", className="font-medium"),
                    dcc.Slider(
                        id='ballot-slider',
                        min=-10,
                        max=10,
                        step=0.5,
                        value=1.5,
                        marks={i: f"{i}%" for i in range(-10, 11, 5)}
                    ),
                    html.Div(id="ballot-value", className="mt-2 text-gray-600"),
                ], className="mb-6"),
            ], className="mb-8"),
            
            # Update Button
            html.Button(
                "Update Prediction",
                id="update-button",
                className="w-full bg-blue-600 text-white py-3 rounded-md hover:bg-blue-700"
            ),
        ], className="w-full lg:w-1/2 p-4"),
        
        # Right column - Results
        html.Div([
            # Results Cards
            html.Div([
                html.Div([
                    html.Div(
                        id="win-probability",
                        className="text-4xl font-bold text-center mb-2"
                    ),
                    html.Div(
                        "Win Probability",
                        className="text-gray-600 text-center"
                    )
                ], className="bg-white rounded-lg shadow-lg p-6 mb-4"),
                
                html.Div([
                    html.Div(
                        id="predicted-margin",
                        className="text-4xl font-bold text-center mb-2"
                    ),
                    html.Div(
                        "Predicted Margin",
                        className="text-gray-600 text-center"
                    )
                ], className="bg-white rounded-lg shadow-lg p-6 mb-4"),
            ]),
            
            # Distribution Graph
            html.Div([
                dcc.Graph(
                    id='margin-distribution',
                    config={'displayModeBar': False}
                )
            ], className="bg-white rounded-lg shadow-lg p-4 mb-4"),
            
            # Feature Importance Graph
            html.Div([
                dcc.Graph(
                    id='feature-importance',
                    config={'displayModeBar': False}
                )
            ], className="bg-white rounded-lg shadow-lg p-4"),
            
        ], className="w-full lg:w-1/2 p-4"),
    ], className="flex flex-wrap"),
])

# Callbacks
@app.callback(
    [
        Output("unemployment-value", "children"),
        Output("gdp-value", "children"),
        Output("approval-value", "children"),
        Output("ballot-value", "children")
    ],
    [
        Input("unemployment-slider", "value"),
        Input("gdp-slider", "value"),
        Input("approval-slider", "value"),
        Input("ballot-slider", "value")
    ]
)
def update_slider_values(unemployment, gdp, approval, ballot):
    return [
        f"{unemployment}%",
        f"{gdp}%",
        f"{approval}%",
        f"{ballot}%"
    ]

@app.callback(
    [
        Output("win-probability", "children"),
        Output("predicted-margin", "children"),
        Output("margin-distribution", "figure"),
        Output("feature-importance", "figure")
    ],
    [Input("update-button", "n_clicks")],
    [
        State("unemployment-slider", "value"),
        State("gdp-slider", "value"),
        State("approval-slider", "value"),
        State("ballot-slider", "value")
    ]
)
def update_predictions(n_clicks, unemployment, gdp, approval, ballot):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate
    
    # Calculate win probability (simplified example)
    win_prob = 50 + (approval - 50) * 0.5 + gdp * 2 - (unemployment - 5) * 3 + ballot * 2
    win_prob = max(min(win_prob, 99), 1)
    
    # Calculate predicted margin
    margin = (win_prob - 50) / 5
    
    # Create distribution plot
    margin_dist = go.Figure()
    x = np.linspace(-10, 10, 50)
    y = np.exp(-(x - margin)**2 / 2)
    
    margin_dist.add_trace(go.Bar(
        x=x,
        y=y,
        marker_color='rgb(66, 135, 245)',
    ))
    
    margin_dist.update_layout(
        title="Distribution of Predicted Margins",
        showlegend=False,
        margin=dict(l=40, r=40, t=40, b=40),
        plot_bgcolor='white'
    )
    
    # Create feature importance plot
    importance_data = pd.DataFrame({
        'Feature': ['Presidential Approval', 'Generic Ballot', 'GDP Growth', 
                   'Unemployment Rate', 'Previous Margin'],
        'Importance': [0.35, 0.25, 0.20, 0.15, 0.05]
    })
    
    feature_importance = px.bar(
        importance_data,
        x='Importance',
        y='Feature',
        orientation='h',
        color_discrete_sequence=['rgb(66, 135, 245)']
    )
    
    feature_importance.update_layout(
        title="Feature Importance",
        showlegend=False,
        margin=dict(l=40, r=40, t=40, b=40),
        plot_bgcolor='white'
    )
    
    return [
        f"{win_prob:.1f}%",
        f"{margin:.1f}%",
        margin_dist,
        feature_importance
    ]

if __name__ == '__main__':
    app.run_server(debug=True)
