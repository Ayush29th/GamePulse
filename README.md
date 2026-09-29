# GamePulse — Elite Analytics

GamePulse is a fully functional web application designed for gaming performance analysis, analyzing match-history data to provide insights on combat performance, map mastery, and player consistency. 

This project aims to deliver a high-fidelity analytical dashboard using Python and Streamlit, recreating a modern, dark-themed UI (inspired by a provided Stitch design).

## Features

- **Performance Overview:** Dashboard displaying K/D ratio, Win Rate, Average Damage, and a dynamic Performance Score (0-100).
- **Match History:** Paginated table of recent matches with filtering (Game, Map, Result) and search capabilities.
- **Data-Driven Insights:** Rule-based analysis text generation pointing out improvements, map strengths, session fatigue, and recommendations based on the user's data.
- **Player Comparison:** Head-to-Head radar charts and stats comparison.
- **Local Storage:** SQLite database for fast access, paired with CSV import capabilities.

## Technology Stack

- **Backend:** Python 3.11+, Pandas, SQLite (`sqlite3`)
- **Frontend:** Streamlit (with extensive custom CSS overrides for styling)
- **Data Visualization:** Plotly

## Project Structure

```text
gamepulse/
├── app.py                   # Main Streamlit application and routing
├── data/
│   ├── sample_matches.csv   # Generated demo data
│   └── gamepulse.db         # SQLite database
├── scripts/
│   └── generate_data.py     # Script to generate synthetic match data
├── modules/
│   ├── data_loader.py       # CSV validation and processing
│   ├── analytics.py         # K/D, win rate, and metric calculations
│   ├── scoring.py           # Algorithm for performance scores
│   ├── insights.py          # Rule-based text generation
│   └── database.py          # SQLite initialization and operations
├── components/
│   ├── metrics.py           # Custom HTML metric cards
│   ├── charts.py            # Plotly dark-themed charts
│   └── tables.py            # Custom HTML/CSS styled tables
└── utils/
    └── helpers.py           # Global Streamlit overrides and UI layout helpers
```

## Dataset Format

The application expects a CSV with the following columns:
`match_id, date, game, map, result, kills, deaths, assists, damage, score, placement, match_duration, headshots`
*(Optional: `player_id`, `player_name`)*

## Installation

1. Ensure Python 3.11+ is installed.
2. Clone this repository and navigate to the project root.
3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Generate demo data (if you don't have your own CSV):
```bash
python scripts/generate_data.py
```
2. Start the Streamlit application:
```bash
streamlit run app.py
```
3. Open your browser to the URL provided in the terminal (usually `http://localhost:8501`).

## How Analytics Are Calculated

- **K/D Ratio:** Total Kills / Total Deaths.
- **Win Rate:** Wins / Total Matches * 100.
- **Pulse Score:** A weighted aggregate of normalized K/D (40%), Win Rate (30%), Average Kills (15%), and Headshot % (15%). Maxes out at 100.
- **Map Mastery:** Combines Map Win Rate and K/D to rank best maps.
- **Session Fatigue:** Analyzes the death count and K/D differences between the older half and recent half of matches.
