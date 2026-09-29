import plotly.graph_objects as go
import pandas as pd

def render_performance_trend(df: pd.DataFrame, metric: str = 'kd'):
    """Renders the performance trend bar chart matching the design."""
    if df.empty:
        return None
        
    fig = go.Figure()
    
    # Use the last N periods for the bar chart
    display_df = df.tail(15) if len(df) > 15 else df
    
    # Colors: mostly gray, last two are accented (cyan, purple) like the design
    n = len(display_df)
    colors = ['#111318'] * n
    if n >= 2:
        colors[-2] = '#00E5FF' # Cyan
        colors[-1] = '#9D7BFF' # Violet
    elif n == 1:
        colors[0] = '#9D7BFF'
        
    y_vals = display_df[metric].tolist()
    
    fig.add_trace(go.Bar(
        x=display_df['date'],
        y=y_vals,
        marker_color=colors,
        marker_line_width=0,
        opacity=0.9
    ))
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False, # Hide dates to match the clean look
            zeroline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#1F222A',
            gridwidth=1,
            griddash='solid',
            showline=False,
            tickfont=dict(color='#4A4D57', size=10),
            zeroline=False
        ),
        showlegend=False,
        height=250,
        hovermode="x unified"
    )
    
    return fig

def render_radar_chart(p1_stats, p2_stats, p1_name, p2_name):
    """Radar chart for player comparison."""
    categories = ['K/D Ratio', 'Win Rate', 'Avg Kills', 'Avg Damage', 'Headshot %']
    
    # Normalize values for radar
    def norm(val, max_val):
        return min(val / max_val, 1.0)
        
    p1_vals = [
        norm(p1_stats['kd_ratio'], 2.5),
        norm(p1_stats['win_rate'], 100),
        norm(p1_stats['avg_kills'], 25),
        norm(p1_stats['avg_damage'], 5000),
        norm(p1_stats['headshot_pct'], 40)
    ]
    
    p2_vals = [
        norm(p2_stats['kd_ratio'], 2.5),
        norm(p2_stats['win_rate'], 100),
        norm(p2_stats['avg_kills'], 25),
        norm(p2_stats['avg_damage'], 5000),
        norm(p2_stats['headshot_pct'], 40)
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=p1_vals,
        theta=categories,
        fill='toself',
        name=p1_name,
        line_color='#9A7BFF',
        fillcolor='rgba(154, 123, 255, 0.3)'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=p2_vals,
        theta=categories,
        fill='toself',
        name=p2_name,
        line_color='#00E5FF',
        fillcolor='rgba(0, 229, 255, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=False, range=[0, 1]),
            angularaxis=dict(color='#8C8F99', gridcolor='#1F222A', linecolor='#1F222A')
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        legend=dict(font=dict(color='white'), orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=20, b=20),
        height=350
    )
    
    return fig
