"""
styles.py
---------
Space-Gym (Cyber-Cosmic Fitness) visual identity adapted for Dash.
"""
from dash import html

PULSAR_CYAN = "#00F2FE"
SUPERNOVA_GOLD = "#FFB700"
HYPERDRIVE_GREEN = "#00FF87"
NEBULA_PINK = "#FF2A85"
COSMIC_PURPLE = "#7B2CBF"
BG_DARK = "#05070E"
BG_CARD = "rgba(18, 14, 46, 0.45)"

def get_dash_global_css():
    return f"""
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Inter:wght@400;500;700&display=swap');

    body, html {{
        margin: 0;
        padding: 0;
        font-family: 'Inter', sans-serif;
        background: radial-gradient(circle at 10% 10%, #11092b 0%, {BG_DARK} 55%, #020307 100%);
        color: #E6F1FF;
        min-height: 100vh;
    }}

    h1, h2, h3, h4 {{
        font-family: 'Space Grotesk', sans-serif;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-top: 0;
    }}

    /* Layout Helpers */
    .app-container {{
        display: flex;
        min-height: 100vh;
    }}
    .sidebar {{
        width: 280px;
        background: linear-gradient(180deg, #090B19 0%, #030409 100%);
        border-right: 1px solid rgba(0, 242, 254, 0.2);
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.5);
        padding: 24px;
        display: flex;
        flex-direction: column;
        gap: 16px;
    }}
    .main-content {{
        flex: 1;
        padding: 40px;
        overflow-y: auto;
    }}

    /* Space-Gym Glassmorphism Card */
    .neo-card {{
        background: {BG_CARD};
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(123, 44, 191, 0.35);
        border-radius: 18px;
        padding: 22px 24px;
        margin-bottom: 18px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5), inset 0 0 12px rgba(0, 242, 254, 0.05);
    }}

    .neo-card-title {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: {PULSAR_CYAN};
        opacity: 0.9;
        margin-bottom: 16px;
    }}

    /* Badges */
    .neo-badge {{
        display: inline-block;
        padding: 4px 14px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        background: rgba(0, 255, 135, 0.12);
        color: {HYPERDRIVE_GREEN};
        border: 1px solid rgba(0, 255, 135, 0.4);
    }}
    .neo-badge-warn {{
        display: inline-block;
        padding: 4px 14px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        background: rgba(255, 42, 133, 0.12);
        color: {NEBULA_PINK};
        border: 1px solid rgba(255, 42, 133, 0.4);
    }}

    /* Inputs & Buttons */
    .neo-input, .dash-input, select, textarea {{
        background-color: rgba(10, 14, 30, 0.7) !important;
        color: #E6F1FF !important;
        border-radius: 10px !important;
        border: 1px solid rgba(0, 242, 254, 0.3) !important;
        padding: 10px 14px;
        width: 100%;
        box-sizing: border-box;
        font-family: 'Inter', sans-serif;
        margin-bottom: 12px;
    }}
    
    .neo-btn {{
        background: linear-gradient(90deg, {PULSAR_CYAN} 0%, {COSMIC_PURPLE} 100%);
        color: #FFFFFF;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        cursor: pointer;
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.35);
        transition: all 0.2s ease-in-out;
        width: 100%;
        margin-top: 8px;
    }}
    .neo-btn:hover {{
        box-shadow: 0 0 30px rgba(0, 242, 254, 0.7);
        transform: translateY(-2px);
    }}
    .neo-btn-nav {{
        background: transparent;
        color: #8CA0C0;
        box-shadow: none;
        text-align: left;
        padding: 10px 16px;
        border-radius: 8px;
    }}
    .neo-btn-nav:hover, .neo-btn-nav.active {{
        background: rgba(0, 242, 254, 0.1);
        color: {PULSAR_CYAN};
        transform: none;
        box-shadow: none;
    }}

    /* Rings */
    .ring-wrap {{ display: flex; flex-direction: column; align-items: center; gap: 8px; }}
    .ring {{ border-radius: 50%; display: flex; align-items: center; justify-content: center; }}
    .ring-inner {{ border-radius: 50%; background: #05070E; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: inset 0 0 10px rgba(0,0,0,0.8); }}
    .ring-value {{ font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 20px; color: #F2F7FF; }}
    .ring-label {{ font-size: 11px; color: #8CA0C0; text-transform: uppercase; letter-spacing: 1px; margin-top: 2px; }}
    """

# --- Dash Layout Helpers ---

def Row(children, style=None):
    return html.Div(children, style={"display": "flex", "flexDirection": "row", "gap": "16px", **(style or {})})

def Col(children, style=None):
    return html.Div(children, style={"flex": 1, "display": "flex", "flexDirection": "column", **(style or {})})

def render_progress_ring(label: str, value: float, target: float, color: str = PULSAR_CYAN, unit: str = ""):
    target = max(target, 1)
    pct = max(0.0, min(value / target, 1.0)) * 100
    over = value > target
    ring_color = NEBULA_PINK if over else color
    size = 130
    thickness = 12
    return html.Div(className="ring-wrap", children=[
        html.Div(className="ring", style={
            "width": f"{size}px", "height": f"{size}px",
            "background": f"conic-gradient({ring_color} {pct * 3.6}deg, rgba(255,255,255,0.06) {pct * 3.6}deg)",
            "boxShadow": f"0 0 15px {ring_color}44"
        }, children=[
            html.Div(className="ring-inner", style={"width": f"{size - thickness*2}px", "height": f"{size - thickness*2}px"}, children=[
                html.Div(f"{value:.0f}{unit}", className="ring-value"),
                html.Div(f"/ {target:.0f}{unit}", className="ring-label")
            ])
        ]),
        html.Div(label, className="ring-label", style={"color": ring_color, "fontSize": "12px", "fontWeight": "bold"})
    ])

def neo_card(children, title=None):
    content = []
    if title:
        content.append(html.Div(title, className="neo-card-title"))
    content.extend(children if isinstance(children, list) else [children])
    return html.Div(content, className="neo-card")

def header(title: str, subtitle: str = ""):
    return html.Div([
        html.H2(title),
        html.Div(subtitle, style={'color': '#8CA0C0', 'marginTop': '-10px', 'marginBottom': '18px'})
    ])