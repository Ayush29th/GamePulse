from typing import Dict

def calculate_performance_score(kd: float, win_rate: float, avg_kills: float, headshot_pct: float) -> Dict[str, int]:
    """
    Calculates a weighted performance score from 0-100.
    Weights:
    - K/D Ratio: 40% (Maxes out around 2.5)
    - Win Rate: 30% (Maxes out at 100%)
    - Avg Kills: 15% (Maxes out around 25)
    - Headshot %: 15% (Maxes out around 40%)
    """
    
    # Normalize K/D (0 to 2.5 -> 0 to 1)
    norm_kd = min(kd / 2.5, 1.0)
    
    # Normalize Win Rate (0 to 100 -> 0 to 1)
    norm_win = win_rate / 100.0
    
    # Normalize Avg Kills (0 to 25 -> 0 to 1)
    norm_kills = min(avg_kills / 25.0, 1.0)
    
    # Normalize Headshot % (0 to 40 -> 0 to 1)
    norm_hs = min(headshot_pct / 40.0, 1.0)
    
    # Calculate weighted score
    kd_score = norm_kd * 40
    win_score = norm_win * 30
    kills_score = norm_kills * 15
    hs_score = norm_hs * 15
    
    score = kd_score + win_score + kills_score + hs_score
    
    return {
        'total': int(round(score)),
        'kd': int(round((kd_score / 40) * 100)),
        'win': int(round((win_score / 30) * 100)),
        'kills': int(round((kills_score / 15) * 100)),
        'hs': int(round((hs_score / 15) * 100)),
        'consistency': int(round((min(kd_score + win_score, 50) / 50) * 100)) # Derived metric for UI
    }

def calculate_map_score(kd: float, win_rate: float) -> int:
    """Simplified score for map analysis."""
    norm_kd = min(kd / 2.0, 1.0)
    norm_win = win_rate / 100.0
    
    score = (norm_kd * 60) + (norm_win * 40)
    return int(round(score * 100))

def get_status_label(score) -> str:
    """Returns a string label based on score."""
    val = score.get('total', 0) if isinstance(score, dict) else score
    if val >= 85: return "EXCELLENT"
    if val >= 70: return "GOOD"
    if val >= 50: return "AVERAGE"
    return "POOR"
