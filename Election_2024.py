import numpy as np
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# Initialize Dash app
app = dash.Dash(__name__)

# Define hypothetical states with initial probabilities for Kamala Harris
states = [
    {"name": "California", "votes": 55, "prob_harris": 0.80, "swing_state": False},
    {"name": "Texas", "votes": 38, "prob_harris": 0.45, "swing_state": True},
    {"name": "Florida", "votes": 29, "prob_harris": 0.50, "swing_state": True},
    {"name": "New York", "votes": 29, "prob_harris": 0.70, "swing_state": False},
    {"name": "Pennsylvania", "votes": 20, "prob_harris": 0.48, "swing_state": True},
    {"name": "Ohio", "votes": 18, "prob_harris": 0.50, "swing_state": True},
]

# Total votes needed to win
total_electoral_votes = sum(state["votes"] for state in states)
votes_to_win = total_electoral_votes // 2 + 1
n_simulations = 80000

# Define layout
app.layout = html.Div([
    html.H1("Election Outcome Simulation Dashboard"),
    
    # Swing state probability sliders
    html.Div([
        html.Label(f"{state['name']} Probability for Kamala Harris:"),
        dcc.Slider(
            id=f"slider-{state['name']}",
            min=0, max=1, step=0.01,
            value=state["prob_harris"],
            marks={0: '0%', 0.5: '50%', 1: '100%'},
        ) for state in states if state["swing_state"]
    ]),
    
    # Run Simulation Button
    html.Button("Run Simulation", id="run-simulation-btn", n_clicks=0),
    
    # Display Probability Results
    html.Div(id="results"),
    
    # Outcome Pie Chart
    dcc.Graph(id="outcome-pie-chart"),
    
    # Market Reaction Pie Chart
    dcc.Graph(id="market-reaction-pie-chart")
])

# Helper function to run simulations
def run_simulation(probabilities):
    harris_wins = 0
    trump_wins = 0
    market_reaction = {"Kamala Harris": {"positive": 0, "negative": 0}, "Donald Trump": {"positive": 0, "negative": 0}}

    for _ in range(n_simulations):
        harris_votes = 0
        trump_votes = 0
        swing_states_won = 0

        for i, state in enumerate(states):
            prob_harris = probabilities[i]
            if np.random.rand() < prob_harris:
                harris_votes += state["votes"]
                if state["swing_state"]:
                    swing_states_won += 1
            else:
                trump_votes += state["votes"]

        if harris_votes >= votes_to_win:
            harris_wins += 1
            if swing_states_won >= len([s for s in states if s["swing_state"]]) // 2:
                market_reaction["Kamala Harris"]["positive"] += 1
            else:
                market_reaction["Kamala Harris"]["negative"] += 1
        else:
            trump_wins += 1
            if swing_states_won < len([s for s in states if s["swing_state"]]) // 2:
                market_reaction["Donald Trump"]["positive"] += 1
            else:
                market_reaction["Donald Trump"]["negative"] += 1

    return harris_wins, trump_wins, market_reaction

# Callback to update results based on slider values
@app.callback(
    Output("results", "children"),
    Output("outcome-pie-chart", "figure"),
    Output("market-reaction-pie-chart", "figure"),
    [Input(f"slider-{state['name']}", "value") for state in states if state["swing_state"]] + [Input("run-simulation-btn", "n_clicks")]
)
def update_simulation(*inputs):
    probabilities = list(inputs[:-1]) + [state["prob_harris"] for state in states if not state["swing_state"]]
    harris_wins, trump_wins, market_reaction = run_simulation(probabilities)

    # Calculate winning probabilities
    prob_harris = harris_wins / n_simulations
    prob_trump = trump_wins / n_simulations

    # Update result text
    results_text = f"Probability Kamala Harris wins: {prob_harris:.2%}<br>Probability Donald Trump wins: {prob_trump:.2%}"

    # Outcome Pie Chart
    outcome_fig = go.Figure(data=[go.Pie(labels=["Kamala Harris Wins", "Donald Trump Wins"], 
                                         values=[harris_wins, trump_wins], 
                                         hole=.3)])
    outcome_fig.update_layout(title_text="Election Outcome Simulation")

    # Market Reaction Pie Chart
    market_fig = go.Figure(data=[go.Pie(labels=["Positive Reaction (Kamala Harris)", "Negative Reaction (Kamala Harris)",
                                                "Positive Reaction (Donald Trump)", "Negative Reaction (Donald Trump)"],
                                        values=[market_reaction["Kamala Harris"]["positive"], market_reaction["Kamala Harris"]["negative"],
                                                market_reaction["Donald Trump"]["positive"], market_reaction["Donald Trump"]["negative"]],
                                        hole=.3)])
    market_fig.update_layout(title_text="Market Reaction Based on Election Outcome")

    return results_text, outcome_fig, market_fig

# Run app
if __name__ == "__main__":
    app.run_server(debug=True)
