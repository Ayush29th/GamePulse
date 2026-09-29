import sqlite3
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'gamepulse.db')

def get_connection():
    """Returns a connection to the SQLite database."""
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create players table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS players (
        player_id TEXT PRIMARY KEY,
        player_name TEXT NOT NULL
    )
    ''')
    
    # Create matches table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS matches (
        match_id TEXT PRIMARY KEY,
        player_id TEXT,
        date DATETIME,
        game TEXT,
        map TEXT,
        result TEXT,
        kills INTEGER,
        deaths INTEGER,
        assists INTEGER,
        damage INTEGER,
        score INTEGER,
        placement INTEGER,
        match_duration INTEGER,
        headshots INTEGER,
        FOREIGN KEY (player_id) REFERENCES players (player_id)
    )
    ''')
    
    conn.commit()
    conn.close()

def load_data_from_df(df: pd.DataFrame):
    """Loads a Pandas DataFrame into the database, handling duplicates."""
    conn = get_connection()
    
    # Extract players
    if 'player_id' in df.columns and 'player_name' in df.columns:
        players_df = df[['player_id', 'player_name']].drop_duplicates()
        players_df.to_sql('players', conn, if_exists='append', index=False, method='multi')
    else:
        # Default player if not specified
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO players (player_id, player_name) VALUES ('P_DEFAULT', 'Demo Player')")
        df['player_id'] = 'P_DEFAULT'
        df['player_name'] = 'Demo Player'
        conn.commit()
    
    # Keep only relevant columns for matches
    match_cols = ['match_id', 'player_id', 'date', 'game', 'map', 'result', 'kills', 
                  'deaths', 'assists', 'damage', 'score', 'placement', 'match_duration', 'headshots']
    
    # Ensure all columns exist
    for col in match_cols:
        if col not in df.columns:
            if col == 'player_id': continue # handled above
            # Provide sensible defaults for missing non-critical columns if any (handled in validation usually)
            df[col] = 0 if col not in ['date', 'game', 'map', 'result'] else 'Unknown'
            
    matches_df = df[match_cols]
    
    # We use temporary table to handle ON CONFLICT IGNORE/REPLACE logic smoothly with pandas
    matches_df.to_sql('matches_temp', conn, if_exists='replace', index=False)
    
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO matches 
        SELECT * FROM matches_temp
    ''')
    cursor.execute('DROP TABLE matches_temp')
    
    conn.commit()
    conn.close()

def clear_db():
    """Clears all data from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM matches')
    cursor.execute('DELETE FROM players')
    conn.commit()
    conn.close()

def fetch_all_matches():
    """Fetches all matches from the database into a Pandas DataFrame."""
    conn = get_connection()
    query = '''
        SELECT m.*, p.player_name
        FROM matches m
        LEFT JOIN players p ON m.player_id = p.player_id
        ORDER BY m.date DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
