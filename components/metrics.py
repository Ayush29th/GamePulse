import streamlit as st
from utils.helpers import render_html

def render_kpi_card(title: str, value: str, trend: str, subtext: str, trend_up: bool = True):
    """Renders a custom HTML KPI card matching the new minimal design."""
    trend_color = "#10B981" if trend_up else "#EF4444"
    arrow = "↑" if trend_up else "↓"
    
    html = f"""
    <div style="
        border-bottom: 1px solid #1F222A;
        padding: 8px 16px 16px 0;
        color: white;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    ">
        <div style="color: #8C8F99; font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600;">
            {title}
        </div>
        <div style="font-size: 28px; font-weight: 700; font-family: 'Inter', sans-serif; letter-spacing: -0.5px; margin: 8px 0;">
            {value}
        </div>
        <div style="font-size: 11px; color: #8C8F99; display: flex; align-items: center; gap: 8px;">
            <span style="color: {trend_color}; font-weight: 600;">{arrow} {trend}</span>
            <span>{subtext}</span>
        </div>
    </div>
    """
    render_html(html)

def render_perf_score_card(score_dict: dict, status: str):
    """Renders the main performance score breakdown."""
    total = score_dict.get('total', 0)
    color = "#10B981" if total >= 70 else ("#F59E0B" if total >= 50 else "#EF4444")
    
    def make_bar(val):
        filled = int((val / 100) * 10)
        return "█" * filled + "░" * (10 - filled)
        
    html = f"""
    <div style="
        background-color: #111318;
        border: 1px solid #1F222A;
        border-radius: 6px;
        padding: 24px;
        color: white;
        height: 100%;
        position: relative;
        overflow: hidden;
    ">
        <div style="position: absolute; top: 0; left: 0; right: 0; height: 3px; background-color: {color};"></div>
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px;">
            <div>
                <div style="color: #8C8F99; font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; margin-bottom: 4px;">PERFORMANCE SCORE</div>
                <div style="font-size: 11px; color: {color}; font-weight: 700; letter-spacing: 1px;">{status}</div>
            </div>
            <div style="font-size: 36px; font-weight: 700; font-family: 'Inter', sans-serif; line-height: 1;">
                {total}<span style="font-size: 14px; color: #8C8F99; margin-left: 2px;">/100</span>
            </div>
        </div>
        
        <div style="font-family: monospace; font-size: 12px; color: #D1D5DB; display: flex; flex-direction: column; gap: 6px; margin-top: 16px;">
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #8C8F99;">K/D</span>
                <span style="color: #00E5FF;">{make_bar(score_dict.get('kd', 0))}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #8C8F99;">WIN RATE</span>
                <span style="color: #00E5FF;">{make_bar(score_dict.get('win', 0))}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #8C8F99;">IMPACT</span>
                <span style="color: #00E5FF;">{make_bar(score_dict.get('kills', 0))}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #8C8F99;">CONSISTENCY</span>
                <span style="color: #00E5FF;">{make_bar(score_dict.get('consistency', 0))}</span>
            </div>
        </div>
    </div>
    """
    render_html(html)

def render_horizontal_stat(label: str, value: str, max_val: float, current_val: float, color: str = "#00E5FF"):
    pct = min((current_val / max_val) * 100, 100)
    html = f"""
    <div style="margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; font-size: 11px; color: #8C8F99; margin-bottom: 6px; font-weight: 600; text-transform: uppercase;">
            <span>{label}</span>
            <span style="color: white;">{value}</span>
        </div>
        <div style="background-color: #1F222A; height: 4px; border-radius: 2px; overflow: hidden;">
            <div style="background-color: {color}; width: {pct}%; height: 100%; border-radius: 2px;"></div>
        </div>
    </div>
    """
    render_html(html)

def render_combat_perf_panel(kills: int, deaths: int, assists: int, damage: float, hs_pct: float):
    render_html("""
    <div style="padding-right: 16px;">
        <h4 style="color: white; font-size: 12px; margin-top: 0; margin-bottom: 24px; text-transform: uppercase; letter-spacing: 1px; color: #8C8F99;">Combat Performance</h4>
    """)
    
    max_k = max(kills, 500)
    max_dmg = max(damage, 200) # Per match approx
    
    render_horizontal_stat("Kills", str(kills), max_k, kills, "#9D7BFF")
    render_horizontal_stat("Deaths", str(deaths), max_k, deaths, "#EF4444")
    render_horizontal_stat("Assists", str(assists), max_k, assists, "#8C8F99")
    render_horizontal_stat("Avg Damage", f"{damage:.0f}", max_dmg, damage, "#00E5FF")
    render_horizontal_stat("Headshot %", f"{hs_pct:.1f}%", 100, hs_pct, "#10B981")
    
    render_html("</div>")

def render_match_perf_panel(win_rate: float, avg_placement: float, avg_duration: float, matches: int):
    render_html("""
    <div style="padding-left: 16px; border-left: 1px solid #1F222A;">
        <h4 style="color: white; font-size: 12px; margin-top: 0; margin-bottom: 24px; text-transform: uppercase; letter-spacing: 1px; color: #8C8F99;">Match Performance</h4>
    """)
    
    render_horizontal_stat("Win Rate", f"{win_rate:.1f}%", 100, win_rate, "#10B981")
    # Placement is inverted (1 is best, max is around 10)
    placement_score = max(0, 11 - avg_placement) 
    render_horizontal_stat("Avg Placement", f"#{avg_placement:.1f}", 10, placement_score, "#9D7BFF")
    render_horizontal_stat("Matches Played", str(matches), max(matches, 50), matches, "#00E5FF")
    render_horizontal_stat("Avg Duration", f"{avg_duration:.0f}m", 60, avg_duration, "#8C8F99")
    
    render_html("</div>")
