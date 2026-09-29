import streamlit as st
import pandas as pd
from utils.helpers import render_html, set_page_config, render_top_bar, render_sidebar_nav
from modules.database import init_db, fetch_all_matches
from modules.analytics import get_overall_metrics, get_map_analysis, get_trend_data
from modules.scoring import calculate_performance_score, get_status_label
from modules.insights import generate_insights, generate_match_analysis
from components.metrics import render_kpi_card, render_perf_score_card
from components.charts import render_performance_trend, render_radar_chart
from components.tables import render_map_analysis_table, render_match_history_table

set_page_config()

# Initialize DB on startup
init_db()

# Load data
@st.cache_data(ttl=60)
def load_data():
    try:
        df = fetch_all_matches()
        # Fallback to demo data if DB is empty
        if df.empty:
            try:
                import os
                base_dir = os.path.dirname(os.path.abspath(__file__))
                sample_path = os.path.join(base_dir, 'data', 'sample_matches.csv')
                
                df = pd.read_csv(sample_path)
                from modules.data_loader import load_and_process_csv
                with open(sample_path, 'rb') as f:
                    load_and_process_csv(f)
                df = fetch_all_matches()
            except Exception as e:
                print(f"Error loading sample data: {e}")
                pass
        return df
    except Exception:
        return pd.DataFrame()

df = load_data()

# Navigation state via query parameters
query_params = st.query_params
if 'page' in query_params:
    st.session_state.page = query_params['page']
elif 'page' not in st.session_state:
    st.session_state.page = 'Overview'
    
# Game filtering state via query parameters
if 'game' in query_params:
    st.session_state.selected_game = query_params['game']
elif 'selected_game' not in st.session_state:
    st.session_state.selected_game = 'Valorant'

# Timeframe filtering state via query parameters
if 'timeframe' in query_params:
    st.session_state.selected_timeframe = query_params['timeframe']
elif 'selected_timeframe' not in st.session_state:
    st.session_state.selected_timeframe = 'Last 30 Days'
    
# Keep query param in sync when initializing
if 'page' not in query_params:
    st.query_params['page'] = st.session_state.page
if 'game' not in query_params:
    st.query_params['game'] = st.session_state.selected_game
if 'timeframe' not in query_params:
    st.query_params['timeframe'] = st.session_state.selected_timeframe

selected_game = st.session_state.selected_game
selected_timeframe = st.session_state.selected_timeframe

# Filter global dataframe by selected game
if not df.empty and 'game' in df.columns:
    df = df[df['game'].str.lower() == selected_game.lower()]

# Filter global dataframe by selected timeframe
if not df.empty and 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])
    max_date = df['date'].max()
    if pd.notna(max_date):
        if selected_timeframe == 'Last 7 Days':
            df = df[df['date'] >= (max_date - pd.Timedelta(days=7))]
        elif selected_timeframe == 'Last 30 Days':
            df = df[df['date'] >= (max_date - pd.Timedelta(days=30))]
        elif selected_timeframe == 'Last 90 Days':
            df = df[df['date'] >= (max_date - pd.Timedelta(days=90))]

# Sidebar
with st.sidebar:
    agent_img = "https://media.valorant-api.com/agents/add6443a-41bd-e414-f6ad-e58d267f4e95/displayicon.png"
    render_html(f"""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 24px; padding: 8px 0;">
        <div style="width: 48px; height: 48px; border-radius: 50%; overflow: hidden; border: 2px solid #00E5FF; box-shadow: 0 0 10px rgba(0, 229, 255, 0.2); padding: 2px; background-color: #111318; flex-shrink: 0;">
            <div style="width: 100%; height: 100%; border-radius: 50%; overflow: hidden; background-color: #1A1C23;">
                <img src="{agent_img}" style="width: 100%; height: 100%; object-fit: cover;" />
            </div>
        </div>
        <div style="display: flex; flex-direction: column;">
            <div style="font-weight: 700; color: white; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px;">Alex_Main</div>
            <div style="color: #00E5FF; font-size: 10px; font-weight: 600; text-transform: uppercase; margin-top: 2px; letter-spacing: 0.5px;">Pro Player</div>
        </div>
    </div>
    """)
    render_sidebar_nav(st.session_state.page)

# Default to P_ALEX_001 if multiple players exist, otherwise take all
current_player_df = df
if not df.empty and 'player_id' in df.columns:
    players = df['player_id'].unique()
    if len(players) > 0:
        player = players[0]
        # In a real app we'd have a dropdown, hardcode to first player for main dashboard
        current_player_df = df[df['player_id'] == player]

# Game specific rank mapping
def get_rank_info(game, player_idx=0):
    ranks = {
        "Valorant": [("DIAMOND III", "#9D7BFF"), ("IMMORTAL 3", "#9D7BFF"), ("ASCENDANT 2", "#00E5FF")],
        "CS2": [("GLOBAL ELITE", "#FBBF24"), ("SUPREME", "#9D7BFF"), ("LEM", "#00E5FF")],
        "Apex Legends": [("APEX PREDATOR", "#EF4444"), ("MASTER", "#9D7BFF"), ("DIAMOND II", "#00E5FF")],
        "PUBG": [("CONQUEROR", "#F59E0B"), ("MASTER", "#9D7BFF"), ("GRANDMASTER", "#00E5FF")],
        "Fortnite": [("UNREAL", "#A855F7"), ("CHAMPION", "#9D7BFF"), ("ELITE", "#00E5FF")]
    }
    game_ranks = ranks.get(game, ranks["Valorant"])
    return game_ranks[player_idx % len(game_ranks)]

# ROUTING
if st.session_state.page == 'Overview':
    render_top_bar("Performance Overview", "Track your competitive performance", show_live=True)
    
    # Background is now handled globally via render_top_bar using the slider in helpers.py
    
    if current_player_df.empty:
        st.warning("No data available. Please upload a CSV in Settings or ensure demo data is generated.")
    else:
        metrics = get_overall_metrics(current_player_df)
        score = calculate_performance_score(metrics['kd_ratio'], metrics['win_rate'], metrics['avg_kills'], metrics['headshot_pct'])
        status = get_status_label(score)
        
        rank_name, rank_color = get_rank_info(selected_game, 0)
        
        # Player form header
        player_name = current_player_df['player_name'].iloc[0] if 'player_name' in current_player_df.columns else "Player"
        render_html(f"""
        <div style="margin-bottom: 32px; display: flex; align-items: flex-end; justify-content: space-between;">
            <div>
                <div style="color: #8C8F99; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;">Player Profile</div>
                <div style="font-size: 28px; font-weight: 700; color: white; line-height: 1;">{player_name}</div>
            </div>
            <div style="display: flex; gap: 32px; text-align: right;">
                <div>
                    <div style="color: #8C8F99; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;">Rank</div>
                    <div style="font-size: 14px; font-weight: 700; color: {rank_color};">{rank_name}</div>
                </div>
                <div>
                    <div style="color: #8C8F99; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;">Matches</div>
                    <div style="font-size: 14px; font-weight: 700; color: white;">{metrics['matches']}</div>
                </div>
                <div>
                    <div style="color: #8C8F99; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;">Form</div>
                    <div style="display: flex; gap: 3px; height: 14px; align-items: flex-end;">
                        <div style="width: 6px; height: 30%; background-color: #1F222A;"></div>
                        <div style="width: 6px; height: 50%; background-color: #1F222A;"></div>
                        <div style="width: 6px; height: 60%; background-color: #00E5FF;"></div>
                        <div style="width: 6px; height: 80%; background-color: #00E5FF;"></div>
                        <div style="width: 6px; height: 100%; background-color: #10B981;"></div>
                    </div>
                </div>
            </div>
        </div>
        """)
        
        # Main Dashboard Layout
        col_left, col_right = st.columns([7, 3], gap="large")
        
        with col_left:
            # Metrics Grid
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            with kpi1: render_kpi_card("K/D Ratio", f"{metrics['kd_ratio']:.2f}", "+12%", "30d avg", True)
            with kpi2: render_kpi_card("Win Rate", f"{metrics['win_rate']:.0f}%", "-4%", "30d avg", False)
            with kpi3: render_kpi_card("Avg Kills", f"{metrics['avg_kills']:.1f}", "+2.1", "per match", True)
            with kpi4: render_kpi_card("Avg Damage", f"{metrics['avg_damage']:.0f}", "+140", "per match", True)
            
            render_html("<div style='margin-top: 32px;'></div>")
            
            # Trend Chart
            render_html("""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                    <h3 style="margin:0; font-size: 13px; text-transform: uppercase; color: #8C8F99; letter-spacing: 1px;">Performance Trend (K/D)</h3>
                </div>
            """)
            trend_data = get_trend_data(current_player_df, 'kd')
            fig = render_performance_trend(trend_data)
            if fig: st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            render_html("<div style='margin-top: 32px;'></div>")
            
            # 2-Column Lower Section
            render_html("""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; border-bottom: 1px solid #1F222A; padding-bottom: 16px;">
                    <h3 style="margin:0; font-size: 13px; text-transform: uppercase; color: white; letter-spacing: 1px;">Combat & Match Analytics</h3>
                </div>
            """)
            bot_left, bot_right = st.columns(2)
            with bot_left:
                from components.metrics import render_combat_perf_panel
                render_combat_perf_panel(metrics['total_kills'], metrics['total_deaths'], metrics['total_assists'], metrics['avg_damage'], metrics['headshot_pct'])
            with bot_right:
                from components.metrics import render_match_perf_panel
                render_match_perf_panel(metrics['win_rate'], metrics['avg_placement'], metrics['avg_duration'], metrics['matches'])
                
        with col_right:
            # Score Breakdown
            render_perf_score_card(score, status)
            
            render_html("<div style='margin-top: 24px;'></div>")
            
            # Map Analysis Top 3
            render_html("""<div style="border: 1px solid #1F222A; border-radius: 6px; padding: 24px; background-color: #111318;">
                <h3 style="margin: 0 0 16px 0; font-size: 11px; text-transform: uppercase; color: #8C8F99; letter-spacing: 1px;">Top Maps</h3>
            """)
            map_df = get_map_analysis(current_player_df)
            render_map_analysis_table(map_df.head(3))
            render_html("</div>")

elif st.session_state.page == 'Match History':
    render_top_bar("Match History", "Analyze past performance data")

    match_id = query_params.get('match_id')
    if match_id:
        # Detailed Match View
        match_data = df[df['match_id'] == match_id]
        if not match_data.empty:
            match = match_data.iloc[0]
            # Top navigation for detail view
            render_html(f"""
            <div style="margin-bottom: 24px;">
                <a href="/?page=Match%20History" target="_self" style="color: #8C8F99; text-decoration: none; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; display: inline-flex; align-items: center; gap: 4px;">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
                    Back to History
                </a>
            </div>
            
            <div style="border: 1px solid #1F222A; border-radius: 6px; background-color: #111318; padding: 32px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 32px; border-bottom: 1px solid #1F222A; padding-bottom: 24px;">
                    <div>
                        <div style="display: flex; gap: 12px; align-items: center; margin-bottom: 8px;">
                            <span style="color: white; font-size: 24px; font-weight: 700; letter-spacing: 0.5px;">{match['map']}</span>
                            <span class="badge badge-{match['result'].lower()}" style="padding: 4px 10px; font-size: 11px;">{match['result']}</span>
                        </div>
                        <div style="color: #8C8F99; font-size: 12px;">{match['date']} &bull; {match['game']} &bull; {match['match_duration']} Min</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: #8C8F99; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;">Match Score</div>
                        <div style="color: #9D7BFF; font-size: 28px; font-weight: 700; font-family: 'Inter', sans-serif;">{match['score']}</div>
                    </div>
                </div>
                
                <h4 style="margin: 0 0 16px 0; color: white; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">Combat Performance</h4>
                <div style="display: flex; gap: 48px;">
                    <div>
                        <div style="color: #8C8F99; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;">K / D / A</div>
                        <div style="color: white; font-size: 20px; font-weight: 700;">{match['kills']} / {match['deaths']} / {match['assists']}</div>
                    </div>
                    <div>
                        <div style="color: #8C8F99; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;">K/D Ratio</div>
                        <div style="color: {'#10B981' if (match['kills']/max(1, match['deaths'])) >= 1.0 else '#EF4444'}; font-size: 20px; font-weight: 700;">{(match['kills']/max(1, match['deaths'])):.2f}</div>
                    </div>
                    <div>
                        <div style="color: #8C8F99; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;">Damage</div>
                        <div style="color: white; font-size: 20px; font-weight: 700;">{match['damage']}</div>
                    </div>
                    <div>
                        <div style="color: #8C8F99; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;">Headshots</div>
                        <div style="color: #00E5FF; font-size: 20px; font-weight: 700;">{match['headshots']}</div>
                    </div>
                    <div>
                        <div style="color: #8C8F99; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;">Placement</div>
                        <div style="color: white; font-size: 20px; font-weight: 700;">#{match['placement']}</div>
                    </div>
                </div>
            </div>
            """)
        else:
            st.error("Match not found.")
            
    else:
        # Main History View
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            game = st.selectbox("GAME", ["Valorant", "All Games"])
        with col2:
            map_filter = st.selectbox("MAP", ["All Maps"] + list(df['map'].unique()))
        with col3:
            res_filter = st.selectbox("RESULT", ["Any", "WIN", "LOSS", "DRAW"])
        with col4:
            st.text_input("SEARCH", placeholder="Enter ID...")
            
        filtered_df = df.copy()
        if map_filter != "All Maps":
            filtered_df = filtered_df[filtered_df['map'] == map_filter]
        if res_filter != "Any":
            filtered_df = filtered_df[filtered_df['result'] == res_filter]
            
        render_html("<div style='border: 1px solid #1F222A; border-radius: 6px; margin-top: 24px; background-color: #111318; overflow: hidden;'>")
        render_match_history_table(filtered_df)
        render_html(f"<div style='padding: 16px; color: #8C8F99; font-size: 11px; border-top: 1px solid #1F222A; text-transform: uppercase; font-weight: 600; letter-spacing: 1px;'>Showing {len(filtered_df)} matches</div>")
        render_html("</div>")

elif st.session_state.page == 'Insights':
    render_top_bar("Performance Insights", "What your recent matches are telling you")
    
    insights = generate_insights(current_player_df)
    
    col1, col2 = st.columns(2, gap="large")
    with col1:
        # Trend
        trend = f"+{insights['trend_val']}%" if insights['trend_val'] > 0 else f"{insights['trend_val']}%"
        arrow = "↑" if insights['trend_val'] > 0 else "↓"
        color = "#10B981" if insights['trend_val'] > 0 else "#EF4444"
        render_html(f"""
        <div style="border: 1px solid #1F222A; border-radius: 6px; padding: 24px; margin-bottom: 24px; background-color: #111318;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 8px; height: 8px; border-radius: 50%; background-color: {color};"></div>
                    <span style="font-size: 11px; text-transform: uppercase; color: #8C8F99; font-weight: 600; letter-spacing: 1px;">TREND ANALYSIS</span>
                </div>
                <span style="color: {color}; font-size: 11px; font-weight: 700; background-color: rgba({('16,185,129' if insights['trend_val'] > 0 else '239,68,68')}, 0.1); padding: 4px 8px; border-radius: 4px;">{trend} MoM</span>
            </div>
            <div style="font-size: 32px; font-weight: 700; font-family: 'Inter', sans-serif; display: flex; align-items: center; margin-bottom: 12px; color: white;">
                {(current_player_df['kills'].sum() / max(1, current_player_df['deaths'].sum())):.2f} 
                <span style="font-size: 14px; color: {color}; margin-left: 8px;">{arrow}</span>
            </div>
            <div style="font-size: 13px; color: #D1D5DB; line-height: 1.6;">{insights['improving']}</div>
        </div>
        """)
        
        # Attention
        render_html(f"""
        <div style="border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 6px; padding: 24px; background-color: rgba(239, 68, 68, 0.05); position: relative; overflow: hidden;">
            <div style="position: absolute; top: 0; left: 0; width: 4px; height: 100%; background-color: #EF4444;"></div>
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 16px;">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>
                <span style="font-size: 11px; text-transform: uppercase; color: #EF4444; font-weight: 700; letter-spacing: 1px;">ATTENTION REQUIRED</span>
            </div>
            <div style="font-size: 14px; font-weight: 600; color: white; margin-bottom: 8px;">Session Fatigue Detected</div>
            <div style="font-size: 13px; color: #D1D5DB; line-height: 1.6;">{insights['attention']}</div>
        </div>
        """)

    with col2:
        # Strength
        render_html(f"""
        <div style="border: 1px solid #1F222A; border-radius: 6px; padding: 24px; margin-bottom: 24px; background-color: #111318; border-top: 2px solid #00E5FF;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
                <span style="font-size: 11px; text-transform: uppercase; color: #00E5FF; font-weight: 700; letter-spacing: 1px;">CORE STRENGTH</span>
                <span style="color: #8C8F99; font-size: 11px; font-weight: 600;">TOP 8%</span>
            </div>
            <div style="font-size: 32px; font-weight: 700; font-family: 'Inter', sans-serif; display: flex; align-items: baseline; margin-bottom: 12px; color: white;">
                68% <span style="font-size: 12px; color: #8C8F99; margin-left: 8px; font-weight: 600;">WIN RATE</span>
            </div>
            <div style="font-size: 13px; color: #D1D5DB; line-height: 1.6;">{insights['strength']}</div>
        </div>
        """)
        
        # Recommendation
        render_html(f"""
        <div style="border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 6px; padding: 24px; background-color: rgba(245, 158, 11, 0.05); position: relative; overflow: hidden;">
             <div style="position: absolute; top: 0; left: 0; width: 4px; height: 100%; background-color: #F59E0B;"></div>
             <div style="display: flex; justify-content: space-between; align-items: center; font-size: 11px; text-transform: uppercase; color: #F59E0B; margin-bottom: 16px; font-weight: 700; letter-spacing: 1px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2"><path d="M12 2v4"/><path d="M12 18v4"/><path d="M4.93 4.93l2.83 2.83"/><path d="M16.24 16.24l2.83 2.83"/><path d="M2 12h4"/><path d="M18 12h4"/><path d="M4.93 19.07l2.83-2.83"/><path d="M16.24 7.76l2.83-2.83"/></svg>
                    <span>RECOMMENDATION</span>
                </div>
            </div>
            <div style="font-size: 14px; font-weight: 600; color: white; margin-bottom: 8px;">Adjust Pacing</div>
            <div style="font-size: 13px; color: #D1D5DB; line-height: 1.6;">{insights['recommendation']}</div>
        </div>
        """)
            
elif st.session_state.page == 'Players':
    render_top_bar("Player Comparison", "Comparing core metrics across competitive queue.")

    
    players = df['player_name'].unique() if not df.empty and 'player_name' in df.columns else []
    
    if len(players) < 2:
        st.warning("Need at least 2 players in the dataset to compare. The demo dataset contains multiple players. Make sure it is loaded.")
    else:
        col_s1, col_s2, _ = st.columns([1, 1, 2])
        with col_s1: p1_sel = st.selectbox("Player 1", players, index=0)
        with col_s2: p2_sel = st.selectbox("Player 2", players, index=1 if len(players)>1 else 0)
        
        p1_df = df[df['player_name'] == p1_sel]
        p2_df = df[df['player_name'] == p2_sel]
        
        m1 = get_overall_metrics(p1_df)
        m2 = get_overall_metrics(p2_df)
        s1 = calculate_performance_score(m1['kd_ratio'], m1['win_rate'], m1['avg_kills'], m1['headshot_pct'])
        s2 = calculate_performance_score(m2['kd_ratio'], m2['win_rate'], m2['avg_kills'], m2['headshot_pct'])
        
        p1_rank, p1_color = get_rank_info(selected_game, 1)
        p2_rank, p2_color = get_rank_info(selected_game, 2)
        
        render_html("<br>")
        col1, col2, col3 = st.columns([1.2, 1, 1.2])
        
        with col1:
            render_html(f"""
            <div style="border: 1px solid #1F222A; border-top: 3px solid {p1_color}; border-radius: 6px; padding: 32px; text-align: center; background-color: #111318; height: 100%;">
                <div style="width: 80px; height: 80px; border-radius: 50%; background-color: rgba(157, 123, 255, 0.1); margin: 0 auto 16px auto; display: flex; align-items: center; justify-content: center; font-size: 24px; color: {p1_color};">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                </div>
                <div style="font-size: 20px; font-weight: 700; color: white;">{p1_sel}</div>
                <div style="color: {p1_color}; font-size: 11px; text-transform: uppercase; margin-top: 4px; margin-bottom: 24px; font-weight: 600;">{p1_rank}</div>
            </div>
            """)
            
        with col2:
            def cmp(v1, v2, higher_is_better=True, formatter="{:.2f}"):
                w1 = w2 = "color: white;"
                if v1 > v2:
                    w1 = f"color: {'#10B981' if higher_is_better else '#EF4444'}; font-weight: 700;"
                    w2 = "color: #8C8F99;"
                elif v2 > v1:
                    w2 = f"color: {'#10B981' if higher_is_better else '#EF4444'}; font-weight: 700;"
                    w1 = "color: #8C8F99;"
                return f'<span style="{w1}">{formatter.format(v1)}</span>', f'<span style="{w2}">{formatter.format(v2)}</span>'
                
            kd1, kd2 = cmp(m1['kd_ratio'], m2['kd_ratio'])
            wr1, wr2 = cmp(m1['win_rate'], m2['win_rate'], formatter="{:.0f}%")
            ak1, ak2 = cmp(m1['avg_kills'], m2['avg_kills'], formatter="{:.1f}")
            ad1, ad2 = cmp(m1['avg_damage'], m2['avg_damage'], formatter="{:.0f}")
            hs1, hs2 = cmp(m1['headshot_pct'], m2['headshot_pct'], formatter="{:.1f}%")
            
            s1_val = s1.get('total', 0) if isinstance(s1, dict) else s1
            s2_val = s2.get('total', 0) if isinstance(s2, dict) else s2
            ps1, ps2 = cmp(s1_val, s2_val, formatter="{:.0f}")

            render_html(f"""
            <div style="padding: 24px 0; text-align: center; height: 100%;">
                <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #1F222A; padding-bottom: 12px; margin-bottom: 16px;">
                    {kd1}
                    <span style="color: #8C8F99; font-size: 11px; font-weight: 600; text-transform: uppercase;">K/D RATIO</span>
                    {kd2}
                </div>
                
                <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #1F222A; padding-bottom: 12px; margin-bottom: 16px;">
                    {wr1}
                    <span style="color: #8C8F99; font-size: 11px; font-weight: 600; text-transform: uppercase;">WIN RATE</span>
                    {wr2}
                </div>
                
                <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #1F222A; padding-bottom: 12px; margin-bottom: 16px;">
                    {ak1}
                    <span style="color: #8C8F99; font-size: 11px; font-weight: 600; text-transform: uppercase;">AVG KILLS</span>
                    {ak2}
                </div>
                
                <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #1F222A; padding-bottom: 12px; margin-bottom: 16px;">
                    {ad1}
                    <span style="color: #8C8F99; font-size: 11px; font-weight: 600; text-transform: uppercase;">ADR</span>
                    {ad2}
                </div>
                
                 <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #1F222A; padding-bottom: 12px; margin-bottom: 24px;">
                    {hs1}
                    <span style="color: #8C8F99; font-size: 11px; font-weight: 600; text-transform: uppercase;">HEADSHOT %</span>
                    {hs2}
                </div>
                
                <div style="display: flex; justify-content: space-between; align-items: center; background-color: rgba(255,255,255,0.02); border-radius: 6px; padding: 12px 16px;">
                    {ps1}
                    <span style="color: #00E5FF; font-size: 11px; text-transform: uppercase; font-weight: 700;">PERFORMANCE SCORE</span>
                    {ps2}
                </div>
            </div>
            """)
            
        with col3:
            render_html(f"""
            <div style="border: 1px solid #1F222A; border-top: 3px solid {p2_color}; border-radius: 6px; padding: 32px; text-align: center; background-color: #111318; height: 100%;">
                <div style="width: 80px; height: 80px; border-radius: 50%; background-color: rgba(0, 229, 255, 0.1); margin: 0 auto 16px auto; display: flex; align-items: center; justify-content: center; font-size: 24px; color: {p2_color};">
                     <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                </div>
                <div style="font-size: 20px; font-weight: 700; color: white;">{p2_sel}</div>
                <div style="color: {p2_color}; font-size: 11px; text-transform: uppercase; margin-top: 4px; margin-bottom: 24px; font-weight: 600;">{p2_rank}</div>
            </div>
            """)
            
        render_html("<br><br>")
        
        c_col1, c_col2 = st.columns([1, 1], gap="large")
        with c_col1:
            render_html("<h3 style='font-size: 12px; text-transform: uppercase; color: #8C8F99; letter-spacing: 1px; margin-bottom: 24px;'>Combat Signature</h3>")
            fig = render_radar_chart(m1, m2, p1_sel, p2_sel)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
        with c_col2:
            render_html("<h3 style='font-size: 12px; text-transform: uppercase; color: #8C8F99; letter-spacing: 1px; margin-bottom: 24px;'>Key Differences</h3>")
            
            p1_win = m1['kd_ratio'] > m2['kd_ratio']
            kd_diff = abs(m1['kd_ratio'] - m2['kd_ratio'])
            win_name = p1_sel if p1_win else p2_sel
            
            render_html(f"""
            <div style="display: flex; gap: 16px; margin-bottom: 24px; align-items: flex-start;">
                <div style="color: #10B981; margin-top: 2px;"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20"/><path d="m17 7-5-5-5 5"/></svg></div>
                <div>
                    <div style="color: white; font-weight: 600; font-size: 14px; margin-bottom: 4px;">{win_name} holds better survivability</div>
                    <div style="color: #8C8F99; font-size: 13px; line-height: 1.5;">Maintains a +{kd_diff:.2f} K/D advantage in direct comparison, indicating more disciplined engagements.</div>
                </div>
            </div>
            
            <div style="display: flex; gap: 16px; margin-bottom: 24px; align-items: flex-start;">
                <div style="color: #00E5FF; margin-top: 2px;"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg></div>
                <div>
                    <div style="color: white; font-weight: 600; font-size: 14px; margin-bottom: 4px;">Mechanical Parity</div>
                    <div style="color: #8C8F99; font-size: 13px; line-height: 1.5;">Headshot percentages ({m1['headshot_pct']:.1f}% vs {m2['headshot_pct']:.1f}%) indicate identical raw mechanical aim capability.</div>
                </div>
            </div>
            
            <div style="display: flex; gap: 16px; margin-bottom: 24px; align-items: flex-start;">
                <div style="color: #F59E0B; margin-top: 2px;"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" x2="4" y1="22" y2="15"/></svg></div>
                <div>
                    <div style="color: white; font-weight: 600; font-size: 14px; margin-bottom: 4px;">Objective Impact</div>
                    <div style="color: #8C8F99; font-size: 13px; line-height: 1.5;">{"Both players exhibit similar win conversions." if abs(m1['win_rate'] - m2['win_rate']) < 5 else f"Despite stats, {p1_sel if m1['win_rate'] > m2['win_rate'] else p2_sel} converts stats into wins {abs(m1['win_rate'] - m2['win_rate']):.0f}% more frequently."}</div>
                </div>
            </div>
            """)
        
elif st.session_state.page == 'Performance':
    render_top_bar("Deep Performance Metrics", "Detailed statistical breakdown of your combat footprint")
    
    if current_player_df.empty:
        st.warning("No data available.")
    else:
        # Consistency & Averages
        render_html("""
        <div style="margin-bottom: 32px;">
            <h3 style="margin: 0 0 24px 0; font-size: 13px; text-transform: uppercase; color: #8C8F99; letter-spacing: 1px;">Core Distributions</h3>
        </div>
        """)
        
        c1, c2, c3, c4 = st.columns(4)
        
        # Calculate consistency metrics (lower std = higher consistency)
        k_std = current_player_df['kills'].std()
        d_std = current_player_df['deaths'].std()
        dmg_std = current_player_df['damage'].std()
        
        # Determine string representation
        def get_consistency_label(std, threshold):
            if std < threshold: return "HIGH", "#10B981"
            if std < threshold * 1.5: return "MODERATE", "#F59E0B"
            return "ERRATIC", "#EF4444"
            
        k_lbl, k_col = get_consistency_label(k_std, 4)
        d_lbl, d_col = get_consistency_label(d_std, 3.5)
        dmg_lbl, dmg_col = get_consistency_label(dmg_std, 600)
        
        with c1:
            render_html(f"""
            <div style="border: 1px solid #1F222A; border-radius: 6px; padding: 24px; background-color: #111318;">
                <div style="color: #8C8F99; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">Kill Volatility</div>
                <div style="font-size: 24px; font-weight: 700; color: white; margin-bottom: 4px;">±{k_std:.1f}</div>
                <div style="color: {k_col}; font-size: 11px; font-weight: 600;">{k_lbl}</div>
            </div>
            """)
        with c2:
            render_html(f"""
            <div style="border: 1px solid #1F222A; border-radius: 6px; padding: 24px; background-color: #111318;">
                <div style="color: #8C8F99; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">Death Volatility</div>
                <div style="font-size: 24px; font-weight: 700; color: white; margin-bottom: 4px;">±{d_std:.1f}</div>
                <div style="color: {d_col}; font-size: 11px; font-weight: 600;">{d_lbl}</div>
            </div>
            """)
        with c3:
            render_html(f"""
            <div style="border: 1px solid #1F222A; border-radius: 6px; padding: 24px; background-color: #111318;">
                <div style="color: #8C8F99; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">Damage Volatility</div>
                <div style="font-size: 24px; font-weight: 700; color: white; margin-bottom: 4px;">±{dmg_std:.0f}</div>
                <div style="color: {dmg_col}; font-size: 11px; font-weight: 600;">{dmg_lbl}</div>
            </div>
            """)
        with c4:
            peak_kills = current_player_df['kills'].max()
            render_html(f"""
            <div style="border: 1px solid #00E5FF; border-radius: 6px; padding: 24px; background-color: rgba(0,229,255,0.05);">
                <div style="color: #00E5FF; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">Peak Performance</div>
                <div style="font-size: 24px; font-weight: 700; color: white; margin-bottom: 4px;">{peak_kills} Kills</div>
                <div style="color: #8C8F99; font-size: 11px; font-weight: 600;">Season High</div>
            </div>
            """)
            
        render_html("<br><br>")
        
        tc1, tc2 = st.columns(2, gap="large")
        trend_data = get_trend_data(current_player_df, 'kd')
        
        with tc1:
            render_html("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <h3 style="margin:0; font-size: 13px; text-transform: uppercase; color: #8C8F99; letter-spacing: 1px;">K/D Trajectory</h3>
            </div>
            """)
            fig = render_performance_trend(trend_data, 'kd')
            if fig: st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
        with tc2:
            render_html("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <h3 style="margin:0; font-size: 13px; text-transform: uppercase; color: #8C8F99; letter-spacing: 1px;">Damage Output</h3>
            </div>
            """)
            fig2 = render_performance_trend(trend_data, 'damage')
            if fig2: 
                # Repaint damage chart purple
                fig2.data[0].marker.color = ['#111318'] * (len(fig2.data[0].marker.color) - 2) + ['#9D7BFF', '#9D7BFF']
                st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
    
elif st.session_state.page == 'Settings':
    render_top_bar("Application Settings", "Manage your account and data connections")
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        render_html("""
        <div style="border: 1px solid #1F222A; border-radius: 6px; padding: 24px; background-color: #111318; margin-bottom: 24px;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 16px;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#9D7BFF" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>
                <h3 style="margin: 0; font-size: 13px; text-transform: uppercase; color: white; letter-spacing: 1px;">Data Management</h3>
            </div>
            <div style="color: #8C8F99; font-size: 12px; line-height: 1.5; margin-bottom: 24px;">
                Upload a CSV file containing your match history. Data will be processed and added to your local analytical database.
            </div>
        """)
        
        uploaded_file = st.file_uploader("Upload Match History (CSV)", type=['csv'], label_visibility="collapsed")
        if uploaded_file is not None:
            from modules.data_loader import load_and_process_csv
            with st.spinner("Processing data..."):
                success, msg = load_and_process_csv(uploaded_file)
                if success:
                    st.success(msg)
                    st.cache_data.clear()
                    st.button("Refresh Data", on_click=lambda: st.rerun())
                else:
                    st.error(msg)
        render_html("</div>")
                
    with col2:
        render_html("""
        <div style="border: 1px solid #1F222A; border-radius: 6px; padding: 24px; background-color: #111318;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 16px;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#00E5FF" stroke-width="2"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 21v-5h5"/></svg>
                <h3 style="margin: 0; font-size: 13px; text-transform: uppercase; color: white; letter-spacing: 1px;">System Controls</h3>
            </div>
            <div style="color: #8C8F99; font-size: 12px; line-height: 1.5; margin-bottom: 24px;">
                Regenerate the demo dataset to populate the application with realistic, correlated match history.
            </div>
        """)
        
        if st.button("Regenerate Demo Data", use_container_width=True):
            with st.spinner("Generating..."):
                import os
                base_dir = os.path.dirname(os.path.abspath(__file__))
                script_path = os.path.join(base_dir, 'scripts', 'generate_data.py')
                sample_path = os.path.join(base_dir, 'data', 'sample_matches.csv')
                
                os.system(f'python "{script_path}"') 
                
                from modules.database import clear_db
                clear_db()
                import pandas as pd
                df_new = pd.read_csv(sample_path)
                from modules.data_loader import load_and_process_csv
                with open(sample_path, 'rb') as f:
                    load_and_process_csv(f)
                st.cache_data.clear()
                st.success("Demo data regenerated and loaded!")
                st.rerun()
                
        render_html("<div style='margin-bottom: 16px;'></div>")

        if st.button("Clear All Data", type="primary", use_container_width=True):
            from modules.database import clear_db
            clear_db()
            st.cache_data.clear()
            st.success("Database cleared.")
            st.rerun()
            
        render_html("</div>")
