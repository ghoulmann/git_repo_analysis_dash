import os
import hashlib
from datetime import datetime
#from dotenv import load_dotenv
from git import Repo
import dash
from dash import html, dcc, Input, Output, State, callback
import pandas as pd
import plotly.express as px
import git_analysis

# Load environment variables
#load_dotenv()
#ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Git Repository Analysis", style={'font-family': 'sans-serif'}),
    dcc.Input(id='repo_path', placeholder='Enter repository path or URL'),
    dcc.Input(id='recent_days', type='number', placeholder='Recent Days', value=30),
    dcc.Input(id='file_extensions', type='text', placeholder='File Extensions (comma-separated)'),
    dcc.Input(id='max_files', type='number', placeholder='Max Files', value=10),
    html.Button('Submit', id='submit_button', n_clicks=0),
    html.Div(id='output_container')
])

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
        if is_remote_repo(repo_path):
            repo_path = clone_repo(repo_path)

        # Process file extensions input
        file_extensions = None
        if file_extensions_input:
            file_extensions = [ext.strip() for ext in file_extensions_input.split(',') if ext.strip()]

        file_commit_age, file_change_frequency = git_analysis.analyze_git_repo(repo_path, recent_days, file_extensions)

        # Define custom color scales
        color_scale_age = ['rgb(255,160,122)', 'rgb(255,69,0)']  # pale red to orange
        color_scale_frequency = ['rgb(255,160,122)', 'rgb(255,69,0)']  # pale red to orange

        # Sort and limit the data
        df_age = pd.DataFrame(sorted(file_commit_age.items(), key=lambda x: x[1])[:max_files], columns=['File', 'Days Since Last Commit'])
        df_frequency = pd.DataFrame(sorted(file_change_frequency.items(), key=lambda x: x[1])[:max_files], columns=['File', 'Commit Frequency'])

        # Create bar charts with color scales
        fig_age = px.bar(df_age, x='File', y='Days Since Last Commit', title="File Commit Age",
                         color='Days Since Last Commit', color_continuous_scale=color_scale_age)
        fig_frequency = px.bar(df_frequency, x='File', y='Commit Frequency', title="File Change Frequency",
                               color='Commit Frequency', color_continuous_scale=color_scale_frequency)

        return html.Div([
            dcc.Graph(figure=fig_age),
            dcc.Graph(figure=fig_frequency)
        ])
    return html.Div()

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
