import dash
from dash import html, dcc, Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from collections import Counter


app = dash.Dash(__name__)


def run_simulation(n_simulations):
    results = []
    
    
    base_ranges = {
        'kamala': (74000000, 78000000),  
        'trump': (73000000, 77000000)    
    }
    
    
    swing_state_margins = {
        'Pennsylvania': ('normal', 1.2, 0.8), 
        'Georgia': ('normal', 0.8, 0.7),
        'Michigan': ('normal', 1.5, 0.9)
    }
    
    for _ in range(n_simulations):
        
        momentum = np.random.normal(0, 0.7)  
        
        
        kamala_pct = np.random.normal(50 + momentum, 1.5)  
        turnout = np.random.normal(155000000, 2000000)     
        
        kamala_votes = int((kamala_pct / 100) * turnout)
        trump_votes = int(turnout - kamala_votes)
        
        
        swing_states = {}
        state_turnouts = {
            'Pennsylvania': 6900000,
            'Georgia': 5000000,
            'Michigan': 5700000
        }
        
        for state, (dist, mean, std) in swing_state_margins.items():
            state_momentum = momentum + np.random.normal(0, 0.5)  
            state_margin = np.random.normal(mean + state_momentum, std)
            state_turnout = np.random.normal(state_turnouts[state], state_turnouts[state] * 0.03)
            
            kamala_state = int(state_turnout * (50 + state_margin) / 100)
            trump_state = int(state_turnout - kamala_state)
            swing_states[state] = (kamala_state, trump_state)
        
        results.append({
            'simulation': _,
            'kamala_total': kamala_votes,
            'trump_total': trump_votes,
            'margin': kamala_votes - trump_votes,
            'margin_pct': (kamala_votes - trump_votes) / turnout * 100,
            'PA_margin': swing_states['Pennsylvania'][0] - swing_states['Pennsylvania'][1],
            'GA_margin': swing_states['Georgia'][0] - swing_states['Georgia'][1],
            'MI_margin': swing_states['Michigan'][0] - swing_states['Michigan'][1],
            'national_momentum': momentum
        })
    
    return pd.DataFrame(results)


app.layout = html.Div([
    html.H1("2024 Election Simulation Dashboard", className="text-center my-4"),
    
    
    html.Div([
        html.Label("Number of Simulations:"),
        dcc.Slider(
            id='simulation-slider',
            min=100,
            max=10000,
            step=100,
            value=1000,
            marks={i: str(i) for i in range(0, 10001, 2000)}
        ),
        html.Button('Run Simulation', id='run-button', n_clicks=0, 
                   className="btn btn-primary my-3")
    ], className="container mx-auto p-4 border rounded"),
    
    
    html.Div([
        html.Div([
            html.Div([
                html.H3(id='win-rate', className="text-4xl font-bold"),
                html.P("Kamala Win Probability")
            ], className="bg-white p-4 rounded shadow"),
            
            html.Div([
                html.H3(id='avg-margin', className="text-4xl font-bold"),
                html.P("Average Margin")
            ], className="bg-white p-4 rounded shadow"),
            
            html.Div([
                html.H3(id='margin-95', className="text-4xl font-bold"),
                html.P("95% Confidence Interval")
            ], className="bg-white p-4 rounded shadow")
        ], className="grid grid-cols-3 gap-4 mb-4")
    ], className="container mx-auto my-4"),
    

    html.Div([
        html.Div([
            dcc.Graph(id='margin-histogram')
        ], className="col-span-2"),
        html.Div([
            dcc.Graph(id='swing-states-chart')
        ], className="col-span-2")
    ], className="container mx-auto grid grid-cols-2 gap-4"),
    
    
    html.Div([
        dcc.Graph(id='win-probability-by-state')
    ], className="container mx-auto my-4"),
    
    
    dcc.Store(id='simulation-store')
])

@app.callback(
    Output('simulation-store', 'data'),
    Input('run-button', 'n_clicks'),
    State('simulation-slider', 'value'),
    prevent_initial_call=True
)
def update_simulation(n_clicks, n_simulations):
    df = run_simulation(n_simulations)
    return df.to_dict('records')

@app.callback(
    [Output('win-rate', 'children'),
     Output('avg-margin', 'children'),
     Output('margin-95', 'children'),
     Output('margin-histogram', 'figure'),
     Output('swing-states-chart', 'figure'),
     Output('win-probability-by-state', 'figure')],
    Input('simulation-store', 'data')
)
def update_graphs(data):
    if not data:
        return "0%", "0", "0", {}, {}, {}
    
    df = pd.DataFrame(data)
    
    
    win_rate = f"{(sum(df['margin'] > 0) / len(df) * 100):.1f}%"
    avg_margin = f"{df['margin_pct'].mean():+.1f}%"
    ci_95 = f"{df['margin_pct'].quantile(0.025):+.1f}% to {df['margin_pct'].quantile(0.975):+.1f}%"
    
    
    hist_fig = go.Figure()
    hist_fig.add_trace(go.Histogram(
        x=df['margin_pct'],
        nbinsx=50,
        marker_color='rgb(100, 100, 200)',
        opacity=0.7
    ))
    hist_fig.update_layout(
        title="Distribution of Victory Margins",
        xaxis_title="Margin of Victory (%)",
        yaxis_title="Frequency",
        template="plotly_white",
        shapes=[{
            'type': 'line',
            'x0': 0,
            'x1': 0,
            'y0': 0,
            'y1': 1,
            'yref': 'paper',
            'line': {'color': 'red', 'dash': 'dash'}
        }]
    )
    
    
    swing_states_data = pd.DataFrame({
        'State': ['Pennsylvania', 'Georgia', 'Michigan'],
        'Win Probability': [
            (df['PA_margin'] > 0).mean() * 100,
            (df['GA_margin'] > 0).mean() * 100,
            (df['MI_margin'] > 0).mean() * 100
        ],
        'Avg Margin': [
            df['PA_margin'].mean() / 69000,  # Converting to percentage
            df['GA_margin'].mean() / 50000,
            df['MI_margin'].mean() / 57000
        ]
    })
    
    swing_fig = px.bar(
        swing_states_data,
        x='State',
        y='Avg Margin',
        color='Win Probability',
        color_continuous_scale='RdBu',
        title="Swing State Analysis"
    )
    swing_fig.update_layout(
        template="plotly_white",
        yaxis_title="Average Margin (%)"
    )
    
    
    prob_fig = go.Figure(go.Bar(
        x=swing_states_data['State'],
        y=swing_states_data['Win Probability'],
        marker_color='rgb(100, 100, 200)',
    ))
    prob_fig.update_layout(
        title="Win Probability by State",
        yaxis_title="Probability (%)",
        template="plotly_white"
    )
    
    return win_rate, avg_margin, ci_95, hist_fig, swing_fig, prob_fig

if __name__ == '__main__':
    app.run_server(debug=True)