import streamlit as st
import re

def render_html(html: str):
    """Safely renders HTML by stripping all leading whitespace to avoid Streamlit Markdown code block parsing."""
    cleaned_html = re.sub(r'^\s+', '', html, flags=re.MULTILINE)
    st.markdown(cleaned_html, unsafe_allow_html=True)

def set_page_config():
    """Sets the page config and injects global CSS."""
    st.set_page_config(
        page_title="GamePulse | Elite Analytics",
        page_icon="🎮",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    css = """
    <style>
        /* Base Streamlit overrides */
        .stApp {
            background-color: #0A0A0C;
            color: #D1D5DB;
            font-family: 'Inter', sans-serif;
        }
        
        .main .block-container {
            max-width: 1400px;
            padding-top: 2rem;
            padding-bottom: 4rem;
            padding-left: 3rem;
            padding-right: 3rem;
            margin: 0 auto;
        }
        
        /* Hide main menu, header, footer */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #0A0A0C;
            border-right: 1px solid #1F222A;
            width: 240px !important;
            min-width: 240px !important;
            max-width: 240px !important;
        }
        
        section[data-testid="stSidebar"] .block-container {
            padding: 0 !important;
        }
        
        /* Custom Nav Sidebar */
        .nav-container {
            padding: 16px 12px;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        
        .nav-link {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 16px;
            text-decoration: none;
            color: #8C8F99;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .nav-link:hover {
            background-color: rgba(255,255,255,0.03);
            color: white;
            text-decoration: none;
        }
        
        .nav-link.active {
            background-color: rgba(0, 229, 255, 0.05);
            color: #00E5FF;
            font-weight: 600;
        }
        
        .nav-link svg {
            stroke: currentColor;
            opacity: 0.7;
        }
        .nav-link:hover svg, .nav-link.active svg {
            opacity: 1;
        }
        
        .nav-link.active::before {
            content: '';
            position: absolute;
            left: 0;
            top: 10%;
            height: 80%;
            width: 3px;
            background-color: #00E5FF;
            border-radius: 0 4px 4px 0;
        }
        
        .nav-item-wrapper {
            position: relative;
        }
        
        .sidebar-logo-container {
            padding: 24px 28px;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
        }
        
        .sidebar-logo-text {
            color: white;
            font-size: 15px;
            font-weight: 800;
            letter-spacing: 1px;
            margin-left: 12px;
        }
        .sidebar-logo-subtext {
            color: #8C8F99;
            font-size: 9px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: 700;
            margin-left: 12px;
        }
        
        /* Typography overrides */
        h1, h2, h3, h4, h5, h6 {
            color: white;
            font-family: 'Inter', sans-serif;
        }
        
        /* Headers top bar */
        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 24px;
            margin-bottom: 32px;
            border-bottom: 1px solid #1F222A;
        }
        .page-title {
            font-size: 20px;
            font-weight: 700;
            letter-spacing: 0.5px;
            margin: 0;
            color: white;
        }
        .page-subtitle {
            font-size: 13px;
            color: #8C8F99;
            margin-top: 4px;
        }
        .top-filters {
            display: flex;
            align-items: center;
            gap: 16px;
            color: #8C8F99;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }
        .filter-item {
            color: white;
            padding: 6px 12px;
            border-radius: 4px;
            border: 1px solid #1F222A;
            background-color: #111318;
            cursor: pointer;
        }
        .filter-item-cyan {
            color: #00E5FF;
        }
        .live-indicator {
            display: flex;
            align-items: center;
            gap: 6px;
            color: #10B981;
            font-size: 11px;
            font-weight: 700;
            padding: 4px 8px;
            background-color: rgba(16, 185, 129, 0.1);
            border-radius: 4px;
        }
        .live-dot {
            width: 6px;
            height: 6px;
            background-color: #10B981;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.4; }
            100% { opacity: 1; }
        }
        
        .dropdown {
            position: relative;
            display: inline-block;
        }
        .dropdown-content {
            display: none;
            position: absolute;
            background-color: #111318;
            min-width: 140px;
            box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.5);
            z-index: 100;
            border: 1px solid #1F222A;
            border-radius: 4px;
            top: 100%;
            margin-top: 4px;
            right: 0;
            overflow: hidden;
        }
        .dropdown-content a {
            color: #8C8F99;
            padding: 10px 16px;
            text-decoration: none;
            display: block;
            font-size: 11px;
            font-weight: 600;
            text-align: left;
        }
        .dropdown-content a:hover {
            background-color: #1F222A;
            color: white;
            text-decoration: none;
        }
        .dropdown:hover .dropdown-content {
            display: block;
        }
    </style>
    """
    render_html(css)

def render_top_bar(title: str, subtitle: str = "", show_live: bool = False):
    active_page = st.session_state.get('page', 'Overview')
    selected_game = st.session_state.get('selected_game', 'Valorant')
    selected_timeframe = st.session_state.get('selected_timeframe', 'Last 30 Days')
    
    available_games = ["Valorant", "CS2", "Apex Legends", "PUBG", "Fortnite"]
    available_timeframes = ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"]
    
    # Dynamic Animated Map Backgrounds
    game_bg_images = {
        "Valorant": [
            "https://media.valorant-api.com/maps/7eaecc1b-4337-bbf6-6ab9-04b8f06b3319/splash.png",
            "https://media.valorant-api.com/maps/2c9d57ec-4431-9c5e-2939-8f9ef6dd5cba/splash.png",
            "https://media.valorant-api.com/maps/2bee0dc9-4ffe-519b-1cbd-7fbe763a6047/splash.png"
        ],
        "CS2": [
            "https://cdn.akamai.steamstatic.com/steam/apps/730/ss_b8c0e21a221f5fb3d05e3f5decfb1c1c910a3014.1920x1080.jpg",
            "https://cdn.akamai.steamstatic.com/steam/apps/730/ss_7520e5fffc82d6b7975f7823b5d3a5ce3a7593c6.1920x1080.jpg",
            "https://cdn.akamai.steamstatic.com/steam/apps/730/ss_37a1fcf6c77bb85eb66b1a37c98038bdcb1e0413.1920x1080.jpg"
        ],
        "Apex Legends": [
            "https://cdn.akamai.steamstatic.com/steam/apps/1172470/ss_fb3b342416bc26ca9d6600c9dc81e8eb87eb4d80.1920x1080.jpg",
            "https://cdn.akamai.steamstatic.com/steam/apps/1172470/ss_895319803f26deca1f6004dc56768a32bbda2c71.1920x1080.jpg",
            "https://cdn.akamai.steamstatic.com/steam/apps/1172470/ss_5ff92a6b472e3820982bb9007f3531b74823ceea.1920x1080.jpg"
        ],
        "PUBG": [
            "https://cdn.akamai.steamstatic.com/steam/apps/578080/ss_845dbf41ef5e2d634db31d9b307ec3f8bc9cf012.1920x1080.jpg",
            "https://cdn.akamai.steamstatic.com/steam/apps/578080/ss_5dfeb6e1d2346617309ed1d0335eaf5393de5b0b.1920x1080.jpg",
            "https://cdn.akamai.steamstatic.com/steam/apps/578080/ss_9eb1f29871bb596283b7086055d282ee0a9ce567.1920x1080.jpg"
        ],
        "Fortnite": [
            "https://cdn2.unrealengine.com/02-eu-br-29-01-evergreen-24-ebr-s29-keyart-1920x1080-1920x1080-6060c4973307.jpg",
            "https://cdn2.unrealengine.com/13br-evergreen-blue-newsheader-1920x1080-879893542.jpg",
            "https://cdn2.unrealengine.com/tcat-29-00-evergreen-sub-1920x1080-6677f5119be9.jpg"
        ]
    }
    bg_urls = game_bg_images.get(selected_game, game_bg_images["Valorant"])
    
    render_html(f"""
    <style>
        .stApp {{
            background: transparent !important;
        }}
        .bg-layer {{
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            z-index: -1;
            background-size: cover;
            background-position: center;
        }}
        .bg-1 {{
            background-image: linear-gradient(rgba(10, 10, 12, 0.85), rgba(10, 10, 12, 0.95)), url('{bg_urls[0]}');
            animation: fade1 21s infinite;
        }}
        .bg-2 {{
            background-image: linear-gradient(rgba(10, 10, 12, 0.85), rgba(10, 10, 12, 0.95)), url('{bg_urls[1]}');
            animation: fade2 21s infinite;
        }}
        .bg-3 {{
            background-image: linear-gradient(rgba(10, 10, 12, 0.85), rgba(10, 10, 12, 0.95)), url('{bg_urls[2]}');
            animation: fade3 21s infinite;
        }}
        @keyframes fade1 {{
            0%, 25% {{ opacity: 1; }}
            33%, 92% {{ opacity: 0; }}
            100% {{ opacity: 1; }}
        }}
        @keyframes fade2 {{
            0%, 25% {{ opacity: 0; }}
            33%, 58% {{ opacity: 1; }}
            66%, 100% {{ opacity: 0; }}
        }}
        @keyframes fade3 {{
            0%, 58% {{ opacity: 0; }}
            66%, 92% {{ opacity: 1; }}
            100% {{ opacity: 0; }}
        }}
    </style>
    <div class="bg-layer bg-1"></div>
    <div class="bg-layer bg-2"></div>
    <div class="bg-layer bg-3"></div>
    """)
    
    # Generate Game dropdown links
    game_links = ""
    for g in available_games:
        active_style = "background-color: #1F222A; color: white;" if g.upper() == selected_game.upper() else ""
        game_links += f'<a href="/?page={active_page.replace(" ", "%20")}&game={g.replace(" ", "%20")}&timeframe={selected_timeframe.replace(" ", "%20")}" style="{active_style}" target="_self">{g.upper()}</a>'
        
    game_dropdown_html = f"""
    <div class="dropdown">
        <span class="filter-item filter-item-cyan" style="display: inline-block;">{selected_game.upper()} ▾</span>
        <div class="dropdown-content">
            {game_links}
        </div>
    </div>
    """
    
    # Generate Timeframe dropdown links
    timeframe_links = ""
    for t in available_timeframes:
        active_style = "background-color: #1F222A; color: white;" if t.upper() == selected_timeframe.upper() else ""
        timeframe_links += f'<a href="/?page={active_page.replace(" ", "%20")}&game={selected_game.replace(" ", "%20")}&timeframe={t.replace(" ", "%20")}" style="{active_style}" target="_self">{t.upper()}</a>'
        
    timeframe_dropdown_html = f"""
    <div class="dropdown">
        <span class="filter-item" style="display: inline-block;">{selected_timeframe.upper()} ▾</span>
        <div class="dropdown-content">
            {timeframe_links}
        </div>
    </div>
    """

    live_html = """
    <div class="live-indicator">
        <div class="live-dot"></div>
        LIVE DATA
    </div>
    """ if show_live else ""
    
    sub_html = f'<div class="page-subtitle">{subtitle}</div>' if subtitle else ""
    
    html = f"""
    <div class="top-bar">
        <div>
            <h1 class="page-title">{title}</h1>
            {sub_html}
        </div>
        <div class="top-filters">
            {live_html}
            {game_dropdown_html}
            {timeframe_dropdown_html}
        </div>
    </div>
    """
    render_html(html)

def get_lucide_icon(name: str) -> str:
    icons = {
        "overview": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="9"/><rect x="14" y="3" width="7" height="5"/><rect x="14" y="12" width="7" height="9"/><rect x="3" y="16" width="7" height="5"/></svg>',
        "history": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l4 2"/></svg>',
        "performance": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>',
        "insights": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v4"/><path d="M12 18v4"/><path d="M4.93 4.93l2.83 2.83"/><path d="M16.24 16.24l2.83 2.83"/><path d="M2 12h4"/><path d="M18 12h4"/><path d="M4.93 19.07l2.83-2.83"/><path d="M16.24 7.76l2.83-2.83"/></svg>',
        "players": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
        "achievements": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="6"/><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11"/></svg>',
        "settings": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>'
    }
    return icons.get(name, "")

def render_sidebar_nav(active_page: str):
    html = """
    <div class="sidebar-logo-container">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#00E5FF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M2 22h20"/><path d="M12 2l-6 16h12z"/>
        </svg>
        <div>
            <div class="sidebar-logo-text">GAMEPULSE</div>
            <div class="sidebar-logo-subtext">COMPETITIVE INTELLIGENCE</div>
        </div>
    </div>
    
    <div class="nav-container">
    """
    
    pages = [
        ("Overview", "overview"),
        ("Match History", "history"),
        ("Performance", "performance"),
        ("Insights", "insights"),
        ("Players", "players"),
        ("Achievements", "achievements")
    ]
    
    for page, icon in pages:
        active_cls = "active" if active_page == page else ""
        icon_svg = get_lucide_icon(icon)
        html += f"""
        <div class="nav-item-wrapper">
            <a href="/?page={page.replace(' ', '%20')}" target="_self" class="nav-link {active_cls}">
                {icon_svg}
                {page}
            </a>
        </div>
        """
        
    html += """
        <div style="margin-top: 32px;"></div>
    """
    
    settings_active = "active" if active_page == "Settings" else ""
    html += f"""
        <div class="nav-item-wrapper">
            <a href="/?page=Settings" target="_self" class="nav-link {settings_active}">
                {get_lucide_icon('settings')}
                Settings
            </a>
        </div>
    </div>
    """
    
    render_html(html)
