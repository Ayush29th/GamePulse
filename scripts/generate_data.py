import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import random

def generate_sample_data(num_matches=500):
    np.random.seed(42)
    random.seed(42)

    games = ['Valorant', 'CS2', 'Apex Legends', 'PUBG', 'Fortnite']
    maps = {
        'Valorant': ['Ascent', 'Bind', 'Haven', 'Split', 'Icebox', 'Breeze', 'Pearl', 'Lotus'],
        'CS2': ['Mirage', 'Inferno', 'Nuke', 'Overpass', 'Vertigo', 'Ancient', 'Dust II', 'Anubis'],
        'Apex Legends': ['World\'s Edge', 'Storm Point', 'Olympus', 'Broken Moon', 'Kings Canyon'],
        'PUBG': ['Erangel', 'Miramar', 'Sanhok', 'Vikendi', 'Taego'],
        'Fortnite': ['Battle Royale', 'Zero Build', 'Arena', 'Ranked']
    }
    
    results = ['WIN', 'LOSS', 'DRAW']
    
    # Players
    players = [
        {'id': 'P_ALEX_001', 'name': 'Alex_Main'},
        {'id': 'P_JETT_002', 'name': 'Jett_TTV'},
        {'id': 'P_AIM_003', 'name': 'AimBot_99'},
        {'id': 'P_NOOB_004', 'name': 'CasualGamer'}
    ]
    
    # Base stats for realistic variance
    base_kills = np.random.normal(16, 7, num_matches)
    base_deaths = np.random.normal(15, 6, num_matches)
    
    matches = []
    end_date = datetime.now()
    
    for i in range(num_matches):
        player = np.random.choice(players, p=[0.4, 0.3, 0.2, 0.1])
        pid = player['id']
        pname = player['name']
        
        game = np.random.choice(games, p=[0.3, 0.2, 0.2, 0.15, 0.15])
        game_map = np.random.choice(maps[game])
        
        kills = max(0, int(base_kills[i]))
        deaths = max(1, int(base_deaths[i]))
        
        # Player specific modifiers
        if pid == 'P_AIM_003': 
            kills += np.random.randint(5, 15)
            deaths = max(1, deaths - np.random.randint(2, 6))
        elif pid == 'P_NOOB_004':
            kills = max(0, kills - np.random.randint(2, 8))
            deaths += np.random.randint(3, 10)
            
        assists = max(0, int(np.random.normal(6, 4)))
        
        # Battle Royales tend to have higher damage per kill due to healing/shields
        if game in ['Apex Legends', 'Fortnite']: dmg_mult = 200
        elif game == 'PUBG': dmg_mult = 120
        else: dmg_mult = 145
        
        damage = max(100, (kills * dmg_mult) + (assists * 45) + int(np.random.normal(0, 100)))
        
        kd = kills / deaths
        
        if kd >= 1.6: result_probs = [0.85, 0.10, 0.05]
        elif kd >= 1.2: result_probs = [0.65, 0.30, 0.05]
        elif kd < 0.8: result_probs = [0.15, 0.80, 0.05]
        else: result_probs = [0.45, 0.50, 0.05]
            
        result = np.random.choice(results, p=result_probs)
        
        rounds = np.random.randint(18, 25)
        if result == 'WIN': rounds = np.random.randint(13, 22)
        score = int(damage / rounds) + (kills * 5)
        
        # Placement logic
        if game in ['Apex Legends', 'PUBG', 'Fortnite']:
            if result == 'WIN':
                placement = 1
            else:
                placement = np.random.randint(2, 50) if kd > 1.2 else np.random.randint(10, 100)
        else:
            if result == 'WIN':
                placement = np.random.randint(1, 4) if kd > 1.2 else np.random.randint(3, 6)
            else:
                placement = np.random.randint(1, 5) if kd > 1.2 else np.random.randint(5, 11)
            
        match_duration = int(np.random.normal(35, 10))
        headshots = int(kills * np.random.uniform(0.15, 0.55))
        
        # Space dates out
        date = end_date - timedelta(days=np.random.randint(0, 120), hours=np.random.randint(0, 24))
        
        match = {
            'match_id': f'M{i+1000:04d}',
            'player_id': pid,
            'player_name': pname,
            'date': date.strftime('%Y-%m-%d %H:%M'),
            'game': game,
            'map': game_map,
            'result': result,
            'kills': kills,
            'deaths': deaths,
            'assists': assists,
            'damage': damage,
            'score': score,
            'placement': placement,
            'match_duration': match_duration,
            'headshots': headshots
        }
        matches.append(match)
        
    df = pd.DataFrame(matches)
    
    os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'data'), exist_ok=True)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample_matches.csv')
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df)} sample matches at {out_path}")

if __name__ == "__main__":
    generate_sample_data()
