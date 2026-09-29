import pandas as pd
from typing import List, Dict

def generate_insights(df: pd.DataFrame) -> Dict[str, str]:
    """Generates rule-based insights from match data."""
    if df.empty or len(df) < 5:
        return {
            'improving': "Not enough data.",
            'strength': "Not enough data.",
            'attention': "Play more matches to generate insights.",
            'recommendation': "Keep playing to build your profile.",
            'trend_val': 0.0
        }
        
    # Sort by date
    df['date'] = pd.to_datetime(df['date'])
    df_sorted = df.sort_values('date')
    
    recent_half = df_sorted.tail(len(df_sorted)//2)
    older_half = df_sorted.head(len(df_sorted)//2)
    
    # Calculate KD trends
    recent_kd = recent_half['kills'].sum() / max(1, recent_half['deaths'].sum())
    older_kd = older_half['kills'].sum() / max(1, older_half['deaths'].sum())
    
    kd_diff_pct = ((recent_kd - older_kd) / older_kd) * 100 if older_kd > 0 else 0
    
    # Improving Insight
    if kd_diff_pct > 5:
        improving = f"Your K/D has improved by {kd_diff_pct:.0f}% over the previous period."
    elif kd_diff_pct < -5:
        improving = f"Your K/D has decreased by {abs(kd_diff_pct):.0f}% recently."
    else:
        improving = "Your performance is relatively consistent across your recent matches."
        
    # Strength Insight
    map_wins = df[df['result'] == 'WIN'].groupby('map').size()
    if not map_wins.empty:
        best_map = map_wins.idxmax()
        win_count = map_wins.max()
        strength = f"Exceptional mastery on {best_map} with {win_count} recent wins."
    else:
        strength = "Need more wins to identify map mastery."
        
    # Attention Insight (Fatigue/Deaths)
    recent_deaths_avg = recent_half['deaths'].mean()
    older_deaths_avg = older_half['deaths'].mean()
    if recent_deaths_avg > older_deaths_avg * 1.1:
        attention = f"Your average deaths have increased over your last {len(recent_half)} matches."
    else:
        attention = "No significant fatigue detected."
        
    # Recommendation Insight
    if recent_deaths_avg > 15:
        recommendation = "Focus on reducing unnecessary engagements. Play more passive angles."
    elif recent_kd > 1.2 and (len(recent_half[recent_half['result'] == 'WIN']) / len(recent_half)) < 0.4:
        recommendation = "Your individual combat is strong, but conversion to wins is low. Focus on team play."
    else:
        recommendation = "Maintain your current pacing, your stats are balanced."
        
    return {
        'improving': improving,
        'strength': strength,
        'attention': attention,
        'recommendation': recommendation,
        'trend_val': round(kd_diff_pct, 1)
    }

def generate_match_analysis(match_row: pd.Series, avg_kd: float) -> List[str]:
    """Generates insights for a specific match."""
    analysis = []
    
    kd = match_row['kills'] / max(1, match_row['deaths'])
    
    if kd > avg_kd * 1.2:
        analysis.append("Strong offensive performance with above-average K/D compared to your baseline.")
    elif kd < avg_kd * 0.8:
        analysis.append("Struggled in combat engagements compared to your recent average.")
        
    if match_row['result'] == 'WIN' and kd < 1.0:
        analysis.append("Optimal utility and teamplay likely compensated for lower combat stats in this win.")
        
    if match_row['deaths'] > 18:
        analysis.append("High death count. Consider reviewing positioning during defense rounds.")
        
    if match_row['headshots'] > (match_row['kills'] * 0.3):
        analysis.append("Excellent crosshair placement and accuracy (high headshot %).")
        
    if not analysis:
        analysis.append("Solid standard performance.")
        
    return analysis
