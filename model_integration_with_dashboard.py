import dash
from dash import html, dcc, Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import pickle
from datetime import datetime, timedelta


with open('election_model.pkl', 'rb') as f:
    ml_model = pickle.load(f)

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("2024 Election ML-Enhanced Probability Dashboard", className="text-center my-4"),
    
    # Model Controls
    html.Div([
        html.Div([
            html.Label("Economic Indicators"),
            html.Div([
                html.Label("Unemployment Rate (%)"),
                dcc.Slider(id='unemployment-slider', min=3, max=8, step=0.1, value=5.2),
            ]),
            html.Div([
                html.Label("GDP Growth (%)"),
                dcc.Slider(id='gdp-slider', min=-2, max=6, step=0.1, value=2.1),
            ]),
        ], className="col"),
        
        html.Div([
            html.Label("Political Indicators"),
            html.Div([
                html.Label("Presidential Approval (%)"),
                dcc.Slider(id='approval-slider', min=30, max=70, step=1, value=43),
            ]),
            html.Div([
                html.Label("Generic Ballot Margin (%)"),
                dcc.Slider(id='ballot-slider', min=-10, max=10, step=0.5, value=1.5),
            ]),
        ], className="col"),
        
        html.Button('Update Prediction', id='predict-button', className="btn btn-primary my-3")
    ], className="container grid grid-cols-2 gap-4 p-4 border rounded"),
    
    # Results Display
    html.Div([
        html.Div([
            html.H3(id='win-probability', className="text-4xl font-bold"),
            html.P("Win Probability (ML Model)")
        ], className="bg-white p-4 rounded shadow"),
        
        html.Div([
            html.H3(id='predicted-margin', className="text-4xl font-bold"),
            html.P("Predicted Margin")
        ], className="bg-white p-4 rounded shadow"),
        
        html.Div([
            html.H3(id='confidence-interval', className="text-4xl font-bold"),
            html.P("95% Confidence Interval")
        ], className="bg-white p-4 rounded shadow")
    ], className="container grid grid-cols-3 gap-4 my-4"),
    
    # Graphs
    html.Div([
        dcc.Graph(id='prediction-distribution'),
        dcc.Graph(id='feature-importance')
    ], className="container grid grid-cols-2 gap-4"),
    
    dcc.Store(id='simulation-results')
])

@app.callback(
    [Output('simulation-results', 'data'),
     Output('win-probability', 'children'),
     Output('predicted-margin', 'children'),
     Output('confidence-interval', 'children'),
     Output('prediction-distribution', 'figure'),
     Output('feature-importance', 'figure')],
    [Input('predict-button', 'n_clicks')],
    [State('unemployment-slider', 'value'),
     State('gdp-slider', 'value'),
     State('approval-slider', 'value'),
     State('ballot-slider', 'value')]
)
def update_prediction(n_clicks, unemployment, gdp, approval, ballot):
    # Prepare current conditions
    current_data = pd.DataFrame({
        'unemployment_rate': [unemployment],
        'gdp_growth': [gdp],
        'presidential_approval': [approval],
        'generic_ballot': [ballot],
        'fundraising_difference': [5.2],  # Could add more sliders for these
        'incumbent_party': [1],
        'days_to_election': [(datetime(2024, 11, 5) - datetime.now()).days],
        'previous_margin': [4.4]
    })
    
    # Run simulation
    simulation_df = ml_model.simulate_with_uncertainty(current_data, n_simulations=1000)
    base_prediction = ml_model.predict_probability(current_data)
    
    # Create distribution plot
    dist_fig = px.histogram(
        simulation_df,
        x='predicted_margin',
        title='Distribution of Predicted Margins',
        nbins=50
    )
    dist_fig.add_vline(x=0, line_dash="dash", line_color="red")
    
    # Create feature importance plot
    importance_df = pd.DataFrame({
        'feature': ml_model.features,
        'importance': ml_model.rf_model.feature_importances_
    }).sort_values('importance', ascending=True)
    
    imp_fig = px.bar(
        importance_df,
        x='importance',
        y='feature',
        orientation='h',
        title='Feature Importance'
    )
    
    return (
        simulation_df.to_dict('records'),
        f"{base_prediction['win_probability']:.1f}%",
        f"{base_prediction['predicted_margin']:.1f}%",
        f"{base_prediction['confidence_interval'][0]:.1f}% - {base_prediction['confidence_interval'][1]:.1f}%",
        dist_fig,
        imp_fig
    )

if __name__ == '__main__':
    app.run_server(debug=True)