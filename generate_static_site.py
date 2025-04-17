import os
import pytz
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from data import initialize_teams, sample_games, process_games

# Create build directory
os.makedirs('build', exist_ok=True)

# Initialize Jinja environment
env = Environment(loader=FileSystemLoader('templates'))

# Initialize data (similar to app.py)
teams = initialize_teams()
games = sample_games(teams)
process_games(games, teams)

# Sort teams by rating
sorted_teams = sorted(teams.values(), key=lambda x: x.rating, reverse=True)

# Set last_updated for the time at the end
eastern = pytz.timezone('America/New_York')
last_updated = datetime.now(eastern)

# Generate index.html
index_template = env.get_template('index.html')
index_html = index_template.render(teams=sorted_teams, last_updated=last_updated)
with open('build/index.html', 'w') as f:
    f.write(index_html)

# Generate team pages
team_template = env.get_template('team.html')
os.makedirs('build/team', exist_ok=True)
for team_id, team in teams.items():
    team_html = team_template.render(team=team, last_updated=last_updated)
    with open(f'build/team/{team_id}.html', 'w') as f:
        f.write(team_html)

print("Static site generated in 'build' directory")
