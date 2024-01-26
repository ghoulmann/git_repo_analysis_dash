import os
import hashlib
from datetime import datetime
#from dotenv import load_dotenv
from git import Repo
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table, Input, Output, State, callback
import pandas as pd
import plotly.express as px
import git_analysis

# Load environment variables
#load_dotenv()
#ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# Initialize the Dash app


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout of the app
# Define the layout of the app using Bootstrap components
app.layout = dbc.Container([
    html.H1("Git Repository Analysis", style={'font-family': 'sans-serif'}),
    dbc.Row([
        dbc.Col(dcc.Input(id='repo_path', placeholder='Enter repository path or URL')),
        dbc.Col(dcc.Input(id='recent_days', type='number', placeholder='Recent Days', value=30)),
        dbc.Col(dcc.Input(id='file_extensions', type='text', placeholder='File Extensions (comma-separated)')),
        dbc.Col(dcc.Input(id='max_files', type='number', placeholder='Max Files', value=10)),
        dbc.Col(html.Button('Submit', id='submit_button', n_clicks=0)),
    ]),
    html.Div(id='output_container')
], fluid=True)
def clone_repo(github_url, base_local_path="path/to/cloned/tmp/clones"):
    # Generate a unique directory name using a hash of the URL
    url_hash = hashlib.md5(github_url.encode()).hexdigest()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_dir = f"{url_hash}_{timestamp}"

    local_repo_path = os.path.join(base_local_path, unique_dir)

    #if not os.path.exists(local_repo_path):
    #    os.makedirs(local_repo_path)  # Create the directory if it doesn't exist
    #    Repo.clone_from(github_url, local_repo_path, env={"GIT_ASKPASS": ACCESS_TOKEN})

    return local_repo_path

def is_remote_repo(repo_path):
    return repo_path.startswith("http://") or repo_path.startswith("https://")

@app.callback(
    Output('output_container', 'children'),
    [Input('submit_button', 'n_clicks')],
    [State('repo_path', 'value'), State('recent_days', 'value'), State('file_extensions', 'value'), State('max_files', 'value')]
)

def update_output(n_clicks, repo_path, recent_days, file_extensions_input, max_files):
    if n_clicks > 0 and repo_path:
        # Clone the repo if it's a remote repository
        if is_remote_repo(repo_path):
            repo_path = clone_repo(repo_path)

        # Process file extensions input
        file_extensions = None
        if file_extensions_input:
            file_extensions = [ext.strip() for ext in file_extensions_input.split(',') if ext.strip()]

        # Analyze the Git repository
        file_commit_age, file_change_frequency = git_analysis.analyze_git_repo(repo_path, recent_days, file_extensions)

        # Sort and limit the data for df_age and df_frequency
        df_age = pd.DataFrame(sorted(file_commit_age.items(), key=lambda x: x[1], reverse=True)[:max_files], columns=['File', 'Days Since Last Commit'])
        df_frequency = pd.DataFrame(sorted(file_change_frequency.items(), key=lambda x: x[1], reverse=True)[:max_files], columns=['File', 'Commit Frequency'])

        # Define custom color scales
        color_scale_age = ['rgb(255,160,122)', 'rgb(255,69,0)']  # pale red to orange
        color_scale_frequency = ['rgb(255,160,122)', 'rgb(255,69,0)']  # pale red to orange

        # Create bar charts with color scales
        fig_age = px.bar(df_age, x='File', y='Days Since Last Commit', title="File Commit Age",
                         color='Days Since Last Commit', color_continuous_scale=color_scale_age)
        fig_frequency = px.bar(df_frequency, x='File', y='Commit Frequency', title="File Change Frequency",
                               color='Commit Frequency', color_continuous_scale=color_scale_frequency)

        # Create interactive striped tables for the data
        table_age = dash_table.DataTable(
            id='table-age',
            columns=[{"name": i, "id": i} for i in df_age.columns],
            data=df_age.to_dict('records'),
            sort_action='native',
            filter_action='native',
            page_action='native',
            page_size=10,
            style_table={'overflowX': 'auto'},  # Horizontal scrolling
            style_data_conditional=[
                {'if': {'row_index': 'odd'},
                 'backgroundColor': 'rgb(248, 248, 248)'}
            ],
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            }
        )
        table_frequency = dash_table.DataTable(
            id='table-frequency',
            columns=[{"name": i, "id": i} for i in df_frequency.columns],
            data=df_frequency.to_dict('records'),
            sort_action='native',
            filter_action='native',
            page_action='native',
            page_size=10,
            style_table={'overflowX': 'auto'},
            style_data_conditional=[
                {'if': {'row_index': 'odd'},
                 'backgroundColor': 'rgb(248, 248, 248)'}
            ],
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            }
        )

        # Return graphs and tables
        return html.Div([
            dcc.Graph(figure=fig_age),
            table_age,
            dcc.Graph(figure=fig_frequency),
            table_frequency
        ])

    return html.Div()

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
