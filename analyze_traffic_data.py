"""
Analyze GitHub traffic data and visualize top repositories by views and clones.

This script loads traffic data from a JSON file (exported by app.py), extracts view and clone counts for each repository,
sorts them, and displays bar charts for the top repositories by view and clone counts.

Usage:
    - Ensure 'LiteObject_traffic_data.json' is present in the same directory.
    - Run this script to display bar charts for the top 5 repositories by views and clones.
"""

# Analyze GitHub traffic data and visualize top repositories by views and clones
import json
import matplotlib.pyplot as plt

# Load the JSON data (replace with your actual file path or paste the JSON directly)
with open('LiteObject_traffic_data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Extract view and clone counts, handling missing or None values safely
repo_views = []
repo_clones = []

for repo_name, repo_data in data.items():
    views = repo_data.get('views') or {}
    clones = repo_data.get('clones') or {}
    view_count = views.get('count', 0)
    clone_count = clones.get('count', 0)
    repo_views.append((repo_name, view_count))
    repo_clones.append((repo_name, clone_count))

# Sort and get top 5 for views and clones
# If there are fewer than 5 repos, this will still work
num_top = min(5, len(repo_views))
top_views = sorted(repo_views, key=lambda x: x[1], reverse=True)[:num_top]
top_clones = sorted(repo_clones, key=lambda x: x[1], reverse=True)[:num_top]


def create_bar_chart(chart_data, title, ylabel, color, filename=None):
    """
    Create a bar chart for the given data and optionally save it to a file.

    Parameters
    ----------
    chart_data : list of (str, int)
        List of (repository name, count) tuples.
    title : str
        Title of the chart.
    ylabel : str
        Label for the y-axis.
    color : str
        Bar color.
    filename : str or None
        If provided, save the chart to this file path.
    """
    if not chart_data:
        print(f"No data to plot for: {title}")
        return
    repos, counts = zip(*chart_data)
    plt.figure(figsize=(10, 6))
    plt.bar(repos, counts, color=color)
    plt.title(title)
    plt.xlabel('Repository')
    plt.ylabel(ylabel)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    if filename:
        plt.savefig(filename, bbox_inches='tight')
        print(f"Chart saved to {filename}")
    plt.show()


# Create bar chart for views and save to file
create_bar_chart(top_views, 'Top 5 Repositories by View Count',
                 'View Count', 'skyblue', filename='top_views.png')

# Create bar chart for clones and save to file
create_bar_chart(top_clones, 'Top 5 Repositories by Clone Count',
                 'Clone Count', 'lightgreen', filename='top_clones.png')
