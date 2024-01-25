# Import necessary libraries
import dash
from dash import html, dcc, Input, Output, State, callback
import plotly.express as px
import pandas as pd
import json
import git_analysis

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Git Repository Analysis"),
    
    # Configuration form
    html.Div([
        dcc.Input(id='repo_path', type='text', placeholder='Repository Path'),
        dcc.Input(id='recent_days', type='number', placeholder='Recent Days', value=30),
        dcc.Input(id='file_extensions', type='text', placeholder='File Extensions (comma-separated)'),
        dcc.Input(id='max_files', type='number', placeholder='Max Files', value=10),
        html.Button('Submit', id='submit_button', n_clicks=0),
    ]),
    
    # Placeholders for visualizations
    html.Div(id='output_container')
])

# Callback for handling the form submission
@app.callback(
    Output('output_container', 'children'),
    [Input('submit_button', 'n_clicks')],
    [State('repo_path', 'value'),
     State('recent_days', 'value'),
     State('file_extensions', 'value'),
     State('max_files', 'value')]
)
def update_output(n_clicks, repo_path, recent_days, file_extensions, max_files):
    if n_clicks > 0 and repo_path:
        # Process the input data
        file_extensions_list = [ext.strip() for ext in file_extensions.split(',')] if file_extensions else []
        results = git_analysis.analyze_git_repo(repo_path, recent_days, file_extensions_list)

        # Create visualizations
        df_age = pd.DataFrame(list(results[0].items()), columns=['File', 'Days Since Last Commit'])
        df_frequency = pd.DataFrame(list(results[1].items()), columns=['File', 'Commit Frequency'])

        fig_age = px.bar(df_age, x='File', y='Days Since Last Commit', title="File Commit Age")
        fig_frequency = px.bar(df_frequency, x='File', y='Commit Frequency', title="File Change Frequency")

        return html.Div([
            dcc.Graph(figure=fig_age),
            dcc.Graph(figure=fig_frequency)
        ])
    return html.Div()

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
