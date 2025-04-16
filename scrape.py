import requests
from datetime import date, timedelta, datetime
from bs4 import BeautifulSoup


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
                games = game_day.find_all("a")
                
                # Check there are at least 3 <a> tags for a full game entry
                for i in range(0, len(games), 3):
                    if i + 2 < len(games):  # Ensure there are 3 elements for a full game
                        away_team = games[i].get_text(strip=True)
                        home_team = games[i+1].get_text(strip=True)
                        raw_score = games[i+2].get_text(strip=True)
                        score_text = raw_score.split("/")[0]

                        if "Ppd" not in score_text and "Rain" not in score_text:
                            games.append([away_team, home_team, score_text.split("-")[0], score_text.split("-")[1], parsed_date])




print(games)



