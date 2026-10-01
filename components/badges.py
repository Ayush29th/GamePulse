from utils.helpers import render_html

def render_achievement_badge(achievement):
    rarity_colors = {
        "Common": "#8C8F99",
        "Uncommon": "#10B981",
        "Rare": "#00E5FF",
        "Epic": "#9D7BFF",
        "Legendary": "#F59E0B"
    }
    
    color = rarity_colors.get(achievement['rarity'], "#8C8F99")
    
    html = f"""
    <div style="border: 1px solid #1F222A; border-radius: 8px; padding: 16px; background-color: #111318; display: flex; align-items: center; gap: 16px; position: relative; overflow: hidden; margin-bottom: 16px;">
        <div style="position: absolute; top: 0; left: 0; width: 4px; height: 100%; background-color: {color};"></div>
        <div style="font-size: 32px; background-color: rgba(255,255,255,0.03); width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; border-radius: 50%; border: 1px solid rgba(255,255,255,0.05); flex-shrink: 0;">
            {achievement['icon']}
        </div>
        <div style="flex-grow: 1;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 4px;">
                <div style="font-size: 14px; font-weight: 700; color: white; letter-spacing: 0.5px;">{achievement['title']}</div>
                <div style="font-size: 10px; font-weight: 600; text-transform: uppercase; color: {color}; border: 1px solid {color}; padding: 2px 6px; border-radius: 12px; opacity: 0.8;">{achievement['rarity']}</div>
            </div>
            <div style="font-size: 12px; color: #8C8F99; line-height: 1.4;">{achievement['desc']}</div>
        </div>
    </div>
    """
    render_html(html)
