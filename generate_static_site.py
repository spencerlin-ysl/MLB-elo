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
for team_name, team in teams.items():
    team_games = []
    for game in games:
        if game.home_team == team or game.away_team == team:
            game_info = {
                'date': datetime.strptime(game.date, "%Y-%m-%d").date(),
                'home_team': game.home_team,
                'away_team': game.away_team,
                'home_team_id': game.home_team.abbreviation,
                'away_team_id': game.away_team.abbreviation,
                'home_score': game.home_score,
                'away_score': game.away_score,
                'winner_id': game.home_team.abbreviation if game.home_score > game.away_score else game.away_team.abbreviation,
                'elo_change': game.home_rating_change
            }
            team_games.append(game_info)
    
    # Sort games by date (newest first)
    team_games.sort(key=lambda x: x['date'], reverse=True)
    
    # Add games to team object for template
    team.games = team_games
    team.id = team.abbreviation  # Use abbreviation as ID
    
    # Generate team page
    team_html = team_template.render(team=team, last_updated=last_updated)
    with open(f'build/team/{team.abbreviation}.html', 'w') as f:
        f.write(team_html)

print("Static site generated in 'build' directory")
