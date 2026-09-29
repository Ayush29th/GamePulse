import pandas as pd
import numpy as np
from typing import Dict, Any

def get_overall_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculates overall metrics for the dashboard."""
    if df.empty:
        return {
            'kd_ratio': 0.0,
            'win_rate': 0.0,
            'avg_kills': 0.0,
            'avg_damage': 0.0,
            'avg_placement': 0.0,
            'matches': 0,
            'total_kills': 0,
            'total_deaths': 0,
            'total_assists': 0,
            'headshot_pct': 0.0,
            'avg_duration': 0.0
        }
        
    total_kills = int(df['kills'].sum())
    total_deaths = int(df['deaths'].sum())
    # avoid div by zero
    total_deaths = total_deaths if total_deaths > 0 else 1
    
    kd_ratio = total_kills / total_deaths
    wins = len(df[df['result'] == 'WIN'])
    win_rate = (wins / len(df)) * 100
    
    avg_kills = df['kills'].mean()
    avg_damage = df['damage'].mean()
    avg_placement = df['placement'].mean()
    
    total_headshots = df['headshots'].sum()
    headshot_pct = (total_headshots / total_kills * 100) if total_kills > 0 else 0
    
    avg_duration = df['match_duration'].mean()
    
    return {
        'kd_ratio': round(kd_ratio, 2),
        'win_rate': round(win_rate, 1),
        'avg_kills': round(avg_kills, 1),
        'avg_damage': round(avg_damage, 0),
        'avg_placement': round(avg_placement, 1),
        'matches': len(df),
        'total_kills': total_kills,
        'total_deaths': total_deaths,
        'total_assists': int(df['assists'].sum()),
        'headshot_pct': round(headshot_pct, 1),
        'avg_duration': round(avg_duration, 0)
    }

def get_map_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates metrics grouped by map."""
    if df.empty:
        return pd.DataFrame()
        
    map_stats = []
    maps = df['map'].unique()
    
    for m in maps:
        mdf = df[df['map'] == m]
        metrics = get_overall_metrics(mdf)
        
        # Calculate a basic map score based on kd and win rate
        from .scoring import calculate_map_score
        map_score = calculate_map_score(metrics['kd_ratio'], metrics['win_rate'])
        
        map_stats.append({
            'Map': m,
            'Matches': len(mdf),
            'K/D': metrics['kd_ratio'],
            'Win Rate': f"{metrics['win_rate']:.0f}%",
            'Score': map_score,
            '_win_rate_val': metrics['win_rate']
        })
        
    map_df = pd.DataFrame(map_stats)
    map_df = map_df.sort_values(by='Score', ascending=False)
    return map_df

def get_trend_data(df: pd.DataFrame, metric: str = 'kd') -> pd.DataFrame:
    """Returns trend data over time (grouped by date)."""
    if df.empty:
        return pd.DataFrame()
        
    # Ensure date is datetime
    df['date'] = pd.to_datetime(df['date'])
    df_sorted = df.sort_values('date')
    
    # Calculate rolling metrics if needed or just daily averages
    daily = df_sorted.groupby(df_sorted['date'].dt.date).agg({
        'kills': 'sum',
        'deaths': 'sum',
        'damage': 'mean',
        'result': lambda x: (x == 'WIN').mean() * 100,
        'score': 'mean'
    }).reset_index()
    
    daily['kd'] = daily['kills'] / daily['deaths'].replace(0, 1)
    
    return daily
