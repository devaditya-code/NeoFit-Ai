"""
styles.py
---------
Space-Gym (Cyber-Cosmic Fitness) visual identity adapted for Dash.
Includes high-contrast typography, starry night cosmos background, and image styles.
"""
from dash import html

PULSAR_CYAN = "#00F2FE"
SUPERNOVA_GOLD = "#FFB700"
HYPERDRIVE_GREEN = "#00FF87"
NEBULA_PINK = "#FF2A85"
COSMIC_PURPLE = "#7B2CBF"
BG_DARK = "#05070E"
BG_CARD = "rgba(18, 14, 46, 0.65)"

def get_dash_global_css():
    return f"""
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Inter:wght@400;500;700&display=swap');

    body, html {{
        margin: 0;
        padding: 0;
        font-family: 'Inter', sans-serif;
        background-color: {BG_DARK};
        color: #FFFFFF !important;
        min-height: 100vh;
    }}

    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Space Grotesk', sans-serif;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-top: 0;
        color: #FFFFFF !important;
    }}

    /* Global Text Contrast Rules */
    p, span, div, label {{
        color: #E0E6ED;
    }}

    label {{
        color: #FFFFFF !important;
        font-weight: 600;
        font-size: 13px;
        margin-bottom: 6px;
        display: block;
        letter-spacing: 0.5px;
    }}

    /* Starry Night Cosmos Background */
    .starry-bg {{
        background: radial-gradient(ellipse at bottom, #1B1235 0%, #05070E 100%);
        min-height: 100vh;
        width: 100%;
        position: relative;
        overflow-y: auto;
    }}

    .starry-bg::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image: 
            radial-gradient(2px 2px at 20px 30px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(2px 2px at 40px 70px, {PULSAR_CYAN}, rgba(0,0,0,0)),
            radial-gradient(1px 1px at 90px 40px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(2px 2px at 160px 120px, {HYPERDRIVE_GREEN}, rgba(0,0,0,0)),
            radial-gradient(1.5px 1.5px at 230px 190px, {NEBULA_PINK}, rgba(0,0,0,0)),
            radial-gradient(2px 2px at 310px 250px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(2px 2px at 370px 150px, {SUPERNOVA_GOLD}, rgba(0,0,0,0));
        background-repeat: repeat;
        background-size: 400px 400px;
        opacity: 0.8;
        pointer-events: none;
        animation: starTwinkle 8s infinite ease-in-out alternate;
    }}

    @keyframes starTwinkle {{
        0% {{ opacity: 0.5; transform: translateY(0px); }}
        100% {{ opacity: 0.95; transform: translateY(-5px); }}
    }}

    /* Layout Helpers */
    .app-container {{
        display: flex;
        min-height: 100vh;
        background: {BG_DARK};
    }}

    .sidebar {{
        width: 290px;
        background: linear-gradient(180deg, #0D0B21 0%, #030409 100%);
        border-right: 1px solid rgba(0, 242, 254, 0.25);
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.7);
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
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
        border: 1px solid rgba(123, 44, 191, 0.45);
        border-radius: 18px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6), inset 0 0 15px rgba(0, 242, 254, 0.08);
    }}

    .neo-card-title {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: {PULSAR_CYAN} !important;
        margin-bottom: 16px;
    }}

    /* Badges */
    .neo-badge {{
        display: inline-block;
        padding: 6px 14px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        background: rgba(0, 255, 135, 0.15);
        color: {HYPERDRIVE_GREEN} !important;
        border: 1px solid rgba(0, 255, 135, 0.5);
    }}

    .neo-badge-warn {{
        display: inline-block;
        padding: 6px 14px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        background: rgba(255, 42, 133, 0.15);
        color: {NEBULA_PINK} !important;
        border: 1px solid rgba(255, 42, 133, 0.5);
    }}

    /* Inputs, Selects & High-Contrast Controls */
    .neo-input, input[type="text"], input[type="password"], input[type="number"], input[type="date"], select, textarea {{
        background-color: rgba(10, 14, 30, 0.95) !important;
        color: #FFFFFF !important;
        border-radius: 10px !important;
        border: 1px solid rgba(0, 242, 254, 0.4) !important;
        padding: 12px 14px;
        width: 100%;
        box-sizing: border-box;
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        margin-bottom: 14px;
    }}

    .neo-input:focus, input:focus, select:focus, textarea:focus {{
        border-color: {PULSAR_CYAN} !important;
        outline: none;
        box-shadow: 0 0 10px rgba(0, 242, 254, 0.4);
    }}

    /* Dash Dropdown Contrast Overrides */
    .Select-control {{
        background-color: rgba(10, 14, 30, 0.95) !important;
        border: 1px solid rgba(0, 242, 254, 0.4) !important;
        border-radius: 10px !important;
    }}
    .Select-value-label, .Select-placeholder {{
        color: #FFFFFF !important;
    }}
    .Select-menu-outer {{
        background-color: #0A0E1E !important;
        border: 1px solid {COSMIC_PURPLE} !important;
    }}
    .Select-option {{
        background-color: #0A0E1E !important;
        color: #FFFFFF !important;
    }}
    .Select-option:hover {{
        background-color: rgba(0, 242, 254, 0.2) !important;
        color: {PULSAR_CYAN} !important;
    }}

    /* Radio Items Visibility Fix */
    .radio-group label {{
        display: inline-flex !important;
        align-items: center;
        color: #FFFFFF !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        margin-right: 20px !important;
        cursor: pointer;
    }}
    .radio-group input[type="radio"] {{
        margin-right: 8px !important;
        accent-color: {PULSAR_CYAN};
        transform: scale(1.2);
    }}

    /* Buttons */
    .neo-btn {{
        background: linear-gradient(90deg, {PULSAR_CYAN} 0%, {COSMIC_PURPLE} 100%);
        color: #FFFFFF !important;
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
        color: #A0B0D0 !important;
        box-shadow: none;
        text-align: left;
        padding: 12px 16px;
        border-radius: 10px;
    }}
    .neo-btn-nav:hover, .neo-btn-nav.active {{
        background: rgba(0, 242, 254, 0.15);
        color: {PULSAR_CYAN} !important;
        border-left: 3px solid {PULSAR_CYAN};
        transform: none;
        box-shadow: none;
    }}

    /* Gym Banner Image Styling */
    .gym-hero-img {{
        width: 100%;
        height: 160px;
        object-fit: cover;
        border-radius: 14px;
        margin-bottom: 18px;
        border: 1px solid rgba(0, 242, 254, 0.3);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }}

    /* Rings */
    .ring-wrap {{ display: flex; flex-direction: column; align-items: center; gap: 8px; }}
    .ring {{ border-radius: 50%; display: flex; align-items: center; justify-content: center; }}
    .ring-inner {{ border-radius: 50%; background: #05070E; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: inset 0 0 10px rgba(0,0,0,0.8); }}
    .ring-value {{ font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 20px; color: #FFFFFF !important; }}
    .ring-label {{ font-size: 11px; color: #A0B0D0 !important; text-transform: uppercase; letter-spacing: 1px; margin-top: 2px; }}
    """

def Row(children, style=None):
    return html.Div(children, style={"display": "flex", "flexDirection": "row", "gap": "16px", "flexWrap": "wrap", **(style or {})})

def Col(children, style=None):
    return html.Div(children, style={"flex": 1, "minWidth": "200px", "display": "flex", "flexDirection": "column", **(style or {})})

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
        html.H2(title, style={"color": "#FFFFFF"}),
        html.Div(subtitle, style={'color': '#A0B0D0', 'marginTop': '-8px', 'marginBottom': '20px', 'fontSize': '14px'})
    ])