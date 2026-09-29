import pandas as pd
from typing import Tuple
from . import database

REQUIRED_COLUMNS = [
    'match_id', 'date', 'game', 'map', 'result', 
    'kills', 'deaths', 'assists', 'damage', 'score', 
    'placement', 'match_duration', 'headshots'
]

def validate_csv(file_obj) -> Tuple[bool, str, pd.DataFrame]:
    """Validates the uploaded CSV and returns (is_valid, error_msg, dataframe)."""
    try:
        df = pd.read_csv(file_obj)
    except Exception as e:
        return False, f"Failed to read CSV file: {str(e)}", None

    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        return False, f"Missing required columns: {', '.join(missing_cols)}", None
    
    # Ensure numeric types for relevant columns
    numeric_cols = ['kills', 'deaths', 'assists', 'damage', 'score', 'placement', 'match_duration', 'headshots']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
    # Prevent division by zero for deaths
    df['deaths'] = df['deaths'].apply(lambda x: 1 if x == 0 else x)
    
    return True, "", df

def load_and_process_csv(file_obj) -> Tuple[bool, str]:
    """Validates, processes, and loads a CSV into the database."""
    is_valid, msg, df = validate_csv(file_obj)
    if not is_valid:
        return False, msg
    
    try:
        database.load_data_from_df(df)
        return True, "Data successfully loaded."
    except Exception as e:
        return False, f"Database error: {str(e)}"
