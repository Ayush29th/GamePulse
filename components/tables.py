import streamlit as st
from utils.helpers import render_html
import pandas as pd

def render_map_analysis_table(df: pd.DataFrame):
    """Renders the Map Analysis table matching the dark theme."""
    if df.empty:
        st.write("No map data available.")
        return
        
    html = """
<style>
.custom-table { width: 100%; border-collapse: collapse; font-size: 13px; color: #D1D5DB; font-family: 'Inter', sans-serif; }
.custom-table th { text-align: left; padding: 12px 16px; color: #8C8F99; font-size: 11px; text-transform: uppercase; border-bottom: 1px solid #1F222A; font-weight: 600; }
.custom-table td { padding: 12px 16px; border-bottom: 1px solid #1F222A; }
.custom-table tr:last-child td { border-bottom: none; }
.kd-good { color: #10B981; }
.kd-bad { color: #EF4444; }
.score-val { color: #00E5FF; font-weight: 700; }
</style>
<table class="custom-table">
<tr>
<th>MAP</th>
<th>MATCHES</th>
<th>K/D</th>
<th>WIN RATE</th>
<th style="text-align: right;">SCORE</th>
</tr>
"""
    
    for _, row in df.iterrows():
        kd = row['K/D']
        kd_class = "kd-good" if kd >= 1.0 else "kd-bad"
        win_rate = row['Win Rate']
        score = row['Score']
        
        html += f"""<tr>
<td>{row['Map']}</td>
<td>{row['Matches']}</td>
<td class="{kd_class}">{kd:.2f}</td>
<td>{win_rate}</td>
<td style="text-align: right;" class="score-val">{score}</td>
</tr>"""
        
    html += "</table>"
    render_html(html)

def render_match_history_table(df: pd.DataFrame):
    """Renders the recent matches table with badges."""
    if df.empty:
        st.write("No match history available.")
        return
        
    html = """
<style>
.mh-table { width: 100%; border-collapse: collapse; font-size: 13px; color: #D1D5DB; font-family: 'Inter', sans-serif;}
.mh-table th { text-align: left; padding: 12px 16px; color: #8C8F99; font-size: 11px; text-transform: uppercase; border-bottom: 1px solid #1F222A; font-weight: 600;}
.mh-table td { padding: 16px 16px; border-bottom: 1px solid #1F222A; }
.mh-table tr:last-child td { border-bottom: none; }
.mh-table tr:hover { background-color: rgba(255,255,255,0.02); }
.badge { padding: 4px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; text-transform: uppercase; border: 1px solid transparent; letter-spacing: 0.5px; }
.badge-win { color: #10B981; border-color: rgba(16, 185, 129, 0.2); background-color: rgba(16, 185, 129, 0.05); }
.badge-loss { color: #EF4444; border-color: rgba(239, 68, 68, 0.2); background-color: rgba(239, 68, 68, 0.05); }
.badge-draw { color: #8C8F99; border-color: rgba(140, 143, 153, 0.2); background-color: rgba(140, 143, 153, 0.05); }
.badge-mvp { color: #F59E0B; border-color: rgba(245, 158, 11, 0.2); background-color: rgba(245, 158, 11, 0.05); margin-left: 8px;}
.btn-view { color: #00E5FF; text-decoration: none; font-size: 11px; font-weight: 600; border: 1px solid rgba(0, 229, 255, 0.3); padding: 4px 10px; border-radius: 4px; transition: all 0.2s; }
.btn-view:hover { background-color: rgba(0, 229, 255, 0.1); border-color: #00E5FF; color: white;}
</style>
<table class="mh-table">
<tr>
<th>DATE</th>
<th>GAME</th>
<th>MAP</th>
<th>RESULT</th>
<th>KILLS</th>
<th>DEATHS</th>
<th>K/D ↓</th>
<th>DAMAGE</th>
<th>SCORE</th>
<th style="text-align: right;">ACTION</th>
</tr>
"""
    
    for _, row in df.iterrows():
        kd = row['kills'] / max(1, row['deaths'])
        kd_color = "#10B981" if kd >= 1.0 else "#EF4444"
        
        res_class = f"badge-{row['result'].lower()}"
        mvp_badge = '<span class="badge badge-mvp">MVP</span>' if row['placement'] == 1 else ""
        
        date_str = pd.to_datetime(row['date']).strftime('%Y-%m-%d %H:%M')
        
        html += f"""<tr>
<td style="color: #8C8F99;">{date_str}</td>
<td>{row['game']}</td>
<td>{row['map']}</td>
<td><span class="badge {res_class}">{row['result']}</span>{mvp_badge}</td>
<td>{row['kills']}</td>
<td>{row['deaths']}</td>
<td style="color: {kd_color};">{kd:.2f}</td>
<td>{row['damage']}</td>
<td style="color: #9D7BFF; font-weight: 700;">{row['score']}</td>
<td style="text-align: right;"><a href="/?page=Match%20History&match_id={row['match_id']}" target="_self" class="btn-view">VIEW</a></td>
</tr>"""
        
    html += "</table>"
    render_html(html)
