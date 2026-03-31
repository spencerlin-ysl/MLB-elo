from flask import Flask, render_template, request, jsonify
import json
import os
from data import initialize_teams
from data import sample_games
from data import process_games
from datetime import date, datetime
from elo import calculate_new_ratings
from data import Game
import pytz

app = Flask(__name__)

# Initialize data
teams = initialize_teams()
games = sample_games(teams, date.today().year)
process_games(games, teams)

@app.route('/')
def index():
    # Sort teams by rating
    sorted_teams = sorted(teams.values(), key=lambda x: x.rating, reverse=True)

    archive_root = "build/archive"
    archive_years = sorted(
        [int(d) for d in os.listdir(archive_root)
         if d.isdigit() and os.path.isdir(os.path.join(archive_root, d))],
        reverse=True,
    ) if os.path.exists(archive_root) else []

    global last_updated
    last_updated = datetime.now(pytz.timezone('America/New_York'))
    
    return render_template('index.html', teams=sorted_teams, last_updated=last_updated, archive_years=archive_years)

@app.route('/archive')
def archive_index():
    archive_root = "build/archive"
    years = sorted(
        [int(d) for d in os.listdir(archive_root)
         if d.isdigit() and os.path.isdir(os.path.join(archive_root, d))],
        reverse=True,
    ) if os.path.exists(archive_root) else []
    
    return render_template('archive_index.html', years=years)

@app.route('/archive/<int:year>')
def archive_year(year):
    import json
    snapshot_path = f"build/archive/{year}/data.json"
    
    if not os.path.exists(snapshot_path):
        return "Archive not found", 404
    
    with open(snapshot_path) as f:
        snapshot = json.load(f)
    
    return render_template('archive_year.html', 
                         year=year, 
                         teams=snapshot['teams'], 
                         archived_at=snapshot['archived_at'])    

@app.route('/team/<team_abbrev>')
def team_detail(team_abbrev):
    # Find team by abbreviation
    team = None
    for team_obj in teams.values():
        if team_obj.abbreviation == team_abbrev:
            team = team_obj
            break

    if team:
        return render_template('team.html', team=team, teams=teams)
    return "Team not found", 404

@app.route('/add_game', methods=['GET', 'POST'])
def add_game():
    if request.method == 'POST':
        home_team_id = request.form['home_team']
        away_team_id = request.form['away_team']
        home_score = int(request.form['home_score'])
        away_score = int(request.form['away_score'])
        date = request.form['date']
        
        home_team = teams.get(home_team_id)
        away_team = teams.get(away_team_id)
        
        if home_team and away_team:
            new_game = Game(home_team, away_team, home_score, away_score, date)
            games.append(new_game)
            
            # Upd ate ratings - FIXED: Pass scores directly
            new_home_rating, new_away_rating = calculate_new_ratings(
                home_team.rating, away_team.rating, 
                home_score, away_score  # Fixed here
            )
            
            home_team.rating = new_home_rating
            away_team.rating = new_away_rating
            
            # Update records
            home_team.games_played += 1
            away_team.games_played += 1
            
            if home_score > away_score:
                home_team.wins += 1
                away_team.losses += 1
            else:
                home_team.losses += 1
                away_team.wins += 1
                
            return "Game added successfully"
        
    
    return render_template('add_game.html', teams=teams)
    

if __name__ == '__main__':
    app.run(debug=True)

