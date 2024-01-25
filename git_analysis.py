from git import Repo, GitCommandError
import os
import logging
from datetime import datetime, timezone

def analyze_git_repo(repo_path, recent_days=60, file_extensions=None):
    """
    Analyze a Git repository for file commit age and change frequency.

    Args:
        repo_path (str): Path to the Git repository.
        recent_days (int, optional): Number of recent days to consider. Defaults to 60.
        file_extensions (list, optional): List of file extensions to filter by. Defaults to None.

    Returns:
        dict, dict: Two dictionaries containing file commit age and change frequency.
    """
    file_commit_age = {}
    file_change_frequency = {}

    try:
        repo = Repo(repo_path)
    except GitCommandError as e:
        logging.error(f"Error accessing repository: {e}")
        return file_commit_age, file_change_frequency

    for commit in repo.iter_commits('HEAD', since=f"{recent_days}.days"):
        for file in commit.stats.files:
            if file_extensions is None or any(file.endswith(ext) for ext in file_extensions):
                file_change_frequency[file] = file_change_frequency.get(file, 0) + 1

    for commit in repo.iter_commits('HEAD'):
        for file in commit.stats.files:
            if file_extensions is None or any(file.endswith(ext) for ext in file_extensions):
                file_commit_age[file] = commit_age_in_days(commit.committed_datetime)

    return file_commit_age, file_change_frequency

def commit_age_in_days(commit_date):
    """
    Calculate the age of a commit in days.
    """
    if commit_date:
        current_date = datetime.now(timezone.utc)
        age_in_days = (current_date - commit_date).days
        return age_in_days
    else:
        return 0

if __name__ == '__main__':
    path = '/home/rik/Documents/github/vale'
    file_exts = ['.py', '.md']  # Example file extensions
    age, frequency = analyze_git_repo(path, file_extensions=file_exts)
    print(age)
    print(frequency)