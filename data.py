from elo import calculate_new_ratings
import requests
from datetime import date, timedelta, datetime
from bs4 import BeautifulSoup

class Team:
    def __init__(self, name, abbreviation, division, initial_rating=1500, icon = ""):
        self.name = name
        self.abbreviation = abbreviation
        self.division = division
        self.rating = initial_rating
        self.games_played = 0
        self.wins = 0
        self.losses = 0
        self.icon = "static/" + icon

class Game:
    def __init__(self, home_team, away_team, home_score, away_score, date):
        self.home_team = home_team
        self.away_team = away_team
        self.home_score = home_score
        self.away_score = away_score
        self.date = date

# Sample MLB Teams
def initialize_teams():
    teams = {
        # AL East
        "Yankees": Team("New York Yankees", "NYY", "AL East", icon = "NYY.png"),
        "Red Sox": Team("Boston Red Sox", "BOS", "AL East", icon = "BOS.png"),
        "Rays": Team("Tampa Bay Rays", "TBR", "AL East", icon = "TB.png"),
        "Blue Jays": Team("Toronto Blue Jays", "TOR", "AL East", icon = "TOR.png"),
        "Orioles": Team("Baltimore Orioles", "BAL", "AL East", icon = "BAL.png"),
        
        # AL Central
        "Guardians": Team("Cleveland Guardians", "CLE", "AL Central", icon = "CLE.png"),
        "Twins": Team("Minnesota Twins", "MIN", "AL Central", icon = "MIN.png"),
        "White Sox": Team("Chicago White Sox", "CHW", "AL Central", icon = "CHW.png"),
        "Tigers": Team("Detroit Tigers", "DET", "AL Central", icon = "DET.png"),
        "Royals": Team("Kansas City Royals", "KCR", "AL Central", icon = "KCR.png"),
        
        # AL West
        "Astros": Team("Houston Astros", "HOU", "AL West", icon = "HOU.png"),
        "Mariners": Team("Seattle Mariners", "SEA", "AL West", icon = "SEA.png"),
        "Angels": Team("Los Angeles Angels", "LAA", "AL West", icon = "LAA.png"),
        "Rangers": Team("Texas Rangers", "TEX", "AL West", icon = "TEX.png"),
        "Athletics": Team("Athletics", "ATH", "AL West", icon = "OAK.png"),
        
        # NL East
        "Braves": Team("Atlanta Braves", "ATL", "NL East", icon = "ATL.png"),
        "Mets": Team("New York Mets", "NYM", "NL East", icon = "NYM.png"),
        "Phillies": Team("Philadelphia Phillies", "PHI", "NL East", icon = "PHI.png"),
        "Marlins": Team("Miami Marlins", "MIA", "NL East", icon = "MIA.png"),
        "Nationals": Team("Washington Nationals", "WSN", "NL East", icon = "WAS.png"),
        
        # NL Central
        "Brewers": Team("Milwaukee Brewers", "MIL", "NL Central", icon = "MIL.png"),
        "Cardinals": Team("St. Louis Cardinals", "STL", "NL Central", icon = "STL.png"),
        "Cubs": Team("Chicago Cubs", "CHC", "NL Central", icon = "CHC.png"),
        "Reds": Team("Cincinnati Reds", "CIN", "NL Central", icon = "CIN.png"),
        "Pirates": Team("Pittsburgh Pirates", "PIT", "NL Central", icon = "PIT.png"),
        
        # NL West
        "Dodgers": Team("Los Angeles Dodgers", "LAD", "NL West", icon = "LAD.png"),
        "Padres": Team("San Diego Padres", "SDP", "NL West", icon = "SD.png"),
        "Giants": Team("San Francisco Giants", "SFG", "NL West", icon = "SF.png"),
        "D-backs": Team("Arizona Diamondbacks", "ARI", "NL West", icon = "AZ.png"),
        "Rockies": Team("Colorado Rockies", "COL", "NL West", icon = "COR.png"),
    }
    
    return teams

# Sample games data (for demonstration)
def sample_games(teams):
    url = "https://plaintextsports.com/mlb/2025/schedule"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    soup = BeautifulSoup(response.text, "html.parser")

    seen_dates = set()
    games = []

    for container in soup.find_all("div"):
        date_tag = container.find("b")
        if date_tag and "2025" in date_tag.get_text(strip=True):
            parsed_date = datetime.strptime(date_tag.get_text(strip=True), "%A, %B %d, %Y").date()
            if parsed_date <= date.today() - timedelta(days=1) and parsed_date not in seen_dates:
                seen_dates.add(parsed_date)
                game_day = container.find("div", class_="day-games")
                if game_day:
                    games_link = game_day.find_all("a")
                    
                    # Check there are at least 3 <a> tags for a full game entry
                    for i in range(0, len(games_link), 3):
                        if i + 2 < len(games_link):  # Ensure there are 3 elements for a full game
                            away_team_name = games_link[i].get_text(strip=True)
                            home_team_name = games_link[i+1].get_text(strip=True)
                            raw_score = games_link[i+2].get_text(strip=True)
                            score_text = raw_score.split("/")[0]

                            if away_team_name in teams and home_team_name in teams:
                                away_team = teams[away_team_name]
                                home_team = teams[home_team_name]
                                
                                score_text = raw_score.split("/")[0]
                                if "Ppd" not in score_text and "Rain" not in score_text:
                                    try:
                                        away_score = int(score_text.split("-")[0])
                                        home_score = int(score_text.split("-")[1])
                                        
                                        games.append(Game(home_team, away_team, home_score, away_score, str(parsed_date)))
                                    except ValueError:
                                        pass
    return games

# Process games and update Elo ratings
def process_games(games, teams):
    for game in games:
        home_team = game.home_team
        away_team = game.away_team
        
        # Update ratings
        new_home_rating, new_away_rating = calculate_new_ratings(
            home_team.rating, away_team.rating, 
            game.home_score, game.away_score
        )
        
        home_team.rating = new_home_rating
        away_team.rating = new_away_rating
        
        # Update win/loss records
        home_team.games_played += 1
        away_team.games_played += 1
        
        if game.home_score > game.away_score:
            home_team.wins += 1
            away_team.losses += 1
        else:
            home_team.losses += 1
            away_team.wins += 1


