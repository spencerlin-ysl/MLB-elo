import os
import json
from datetime import datetime
import pytz
from jinja2 import Environment, FileSystemLoader
from data import initialize_teams, sample_games, process_games

def archive_season(year: int):
    
    # Generate a JSON snapshot and static HTML archive page for a given season year.
    # Saves to build/archive/{year}/
    
    archive_dir = f"build/archive/{year}"
    os.makedirs(archive_dir, exist_ok=True)

    snapshot_path = os.path.join(archive_dir, "data.json")

    # Skip if snapshot already exists
    if os.path.exists(snapshot_path):
        print(f"Archive for {year} already exists at {snapshot_path}. Skipping.")
        return

    print(f"Archiving season {year}...")

    # Initialize and process data for the given year
    teams = initialize_teams(year=year)
    games = sample_games(teams, year=year)
    process_games(games, teams)

    # Sort teams by rating
    sorted_teams = sorted(teams.values(), key=lambda x: x.rating, reverse=True)

    eastern = pytz.timezone('America/New_York')
    archived_at = datetime.now(eastern).strftime('%Y-%m-%d %H:%M:%S')

    # Build snapshot data
    snapshot = {
        "year": year,
        "archived_at": archived_at,
        "teams": [
            {
                "rank": i + 1,
                "name": t.name,
                "abbreviation": t.abbreviation,
                "division": t.division,
                "rating": round(t.rating),
                "wins": t.wins,
                "losses": t.losses,
                "icon": t.icon,
            }
            for i, t in enumerate(sorted_teams)
        ]
    }

    # Save JSON snapshot
    with open(snapshot_path, "w") as f:
        json.dump(snapshot, f, indent=2)
    print(f"  Saved snapshot: {snapshot_path}")

    # Generate static HTML archive page from snapshot
    generate_archive_page(year, snapshot)

    # Regenerate the archive index listing all years
    generate_archive_index()


def generate_archive_page(year: int, snapshot: dict):
    """Generate build/archive/{year}/index.html from a snapshot dict."""
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("archive_year.html")

    html = template.render(
        year=year,
        teams=snapshot["teams"],
        archived_at=snapshot["archived_at"],
    )

    out_path = f"build/archive/{year}/index.html"
    with open(out_path, "w") as f:
        f.write(html)
    print(f"  Generated archive page: {out_path}")


def generate_archive_index():
    """Scan build/archive/ for year folders and regenerate build/archive/index.html."""
    archive_root = "build/archive"
    os.makedirs(archive_root, exist_ok=True)

    years = sorted(
        [
            int(d)
            for d in os.listdir(archive_root)
            if d.isdigit() and os.path.isdir(os.path.join(archive_root, d))
        ],
        reverse=True,
    )

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("archive_index.html")
    html = template.render(years=years)

    out_path = os.path.join(archive_root, "index.html")
    with open(out_path, "w") as f:
        f.write(html)
    print(f"  Updated archive index: {out_path}")


def maybe_auto_archive():
    """
    Called from generate_static_site.py.
    If today is March 15 or later and the previous year's archive doesn't exist,
    automatically archive the previous season.
    """
    eastern = pytz.timezone('America/New_York')
    today = datetime.now(eastern)

    # Auto-archive triggers on/after March 15 each year
    if today.month > 3 or (today.month == 3 and today.day >= 15):
        prev_year = today.year - 1
        snapshot_path = f"build/archive/{prev_year}/data.json"
        if not os.path.exists(snapshot_path):
            print(f"Auto-archive triggered: archiving {prev_year} season.")
            archive_season(prev_year)
        else:
            print(f"Auto-archive: {prev_year} archive already exists, skipping.")


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        try:
            year = int(sys.argv[1])
            archive_season(year)
        except ValueError:
            print(f"Invalid year: {sys.argv[1]}")
    else:
        print("Usage: python archive_season.py <year>")
        print("Example: python archive_season.py 2024")
