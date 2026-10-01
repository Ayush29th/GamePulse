import pandas as pd

def compute_achievements(df: pd.DataFrame):
    """Computes a list of unlocked achievements for the given player dataframe."""
    achievements = []
    
    if df.empty:
        return achievements
        
    total_matches = len(df)
    total_wins = len(df[df['result'] == 'WIN'])
    total_kills = df['kills'].sum()
    
    # 1. First Blood (First Match Played)
    if total_matches >= 1:
        achievements.append({"title": "First Blood", "desc": "Play your first match", "icon": "🎯", "rarity": "Common"})
        
    # 2. Winner (10 Wins)
    if total_wins >= 10:
        achievements.append({"title": "Winner", "desc": "Win 10 matches", "icon": "🏆", "rarity": "Uncommon"})
        
    # 3. Veteran (50 Matches)
    if total_matches >= 50:
        achievements.append({"title": "Veteran", "desc": "Play 50 matches", "icon": "🎖️", "rarity": "Rare"})
        
    # 4. Sharpshooter (Max Kills in a game >= 30)
    if df['kills'].max() >= 30:
        achievements.append({"title": "Sharpshooter", "desc": "Get 30+ kills in a single match", "icon": "🔫", "rarity": "Epic"})
        
    # 5. Untouchable (Win a game with < 5 deaths and > 15 kills)
    untouchable_games = df[(df['result'] == 'WIN') & (df['deaths'] < 5) & (df['kills'] > 15)]
    if not untouchable_games.empty:
        achievements.append({"title": "Untouchable", "desc": "Win a match with >15 kills and <5 deaths", "icon": "🛡️", "rarity": "Legendary"})
        
    # 6. Assassin (High headshot count in a game >= 15)
    if 'headshots' in df.columns and df['headshots'].max() >= 15:
         achievements.append({"title": "Assassin", "desc": "Hit 15+ headshots in one match", "icon": "💀", "rarity": "Epic"})
         
    # 7. Damage Dealer (Damage >= 5000 in a match)
    if df['damage'].max() >= 5000:
        achievements.append({"title": "Damage Dealer", "desc": "Deal 5000+ damage in a single match", "icon": "🔥", "rarity": "Rare"})
        
    return achievements
