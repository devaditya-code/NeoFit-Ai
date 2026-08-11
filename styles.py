"""
styles.py
---------
Space-Gym (Cyber-Cosmic Fitness) visual identity:
Deep cosmic void, galactic nebulae, glassmorphism cards, and high-energy neon metrics.
"""

# Space-Gym Neon Palette
PULSAR_CYAN = "#00F2FE"
SUPERNOVA_GOLD = "#FFB700"
HYPERDRIVE_GREEN = "#00FF87"
NEBULA_PINK = "#FF2A85"
COSMIC_PURPLE = "#7B2CBF"
BG_DARK = "#05070E"
BG_CARD = "rgba(18, 14, 46, 0.45)"


def inject_global_css():
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Inter:wght@400;500;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}

        .stApp {{
            background: radial-gradient(circle at 10% 10%, #11092b 0%, {BG_DARK} 55%, #020307 100%);
            color: #E6F1FF;
        }}

        h1, h2, h3, h4 {{
            font-family: 'Space Grotesk', sans-serif !important;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}

        /* Sidebar - Galactic Command Station */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #090B19 0%, #030409 100%);
            border-right: 1px solid rgba(0, 242, 254, 0.2);
            box-shadow: 4px 0 24px rgba(0, 0, 0, 0.5);
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
            margin-bottom: 8px;
        }}

        .neo-badge {{
            display: inline-block;
            padding: 4px 14px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
            background: rgba(0, 255, 135, 0.12);
            color: {HYPERDRIVE_GREEN};
            border: 1px solid rgba(0, 255, 135, 0.4);
            box-shadow: 0 0 10px rgba(0, 255, 135, 0.2);
        }}

        .neo-badge-warn {{
            background: rgba(255, 42, 133, 0.12);
            color: {NEBULA_PINK};
            border: 1px solid rgba(255, 42, 133, 0.4);
            box-shadow: 0 0 10px rgba(255, 42, 133, 0.2);
        }}

        /* High-Velocity Action Buttons */
        div.stButton > button, div.stFormSubmitButton > button {{
            background: linear-gradient(90deg, {PULSAR_CYAN} 0%, {COSMIC_PURPLE} 100%);
            color: #FFFFFF;
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            border: none;
            border-radius: 12px;
            padding: 0.6em 1.4em;
            box-shadow: 0 0 20px rgba(0, 242, 254, 0.35);
            transition: all 0.2s ease-in-out;
        }}
        div.stButton > button:hover {{
            box-shadow: 0 0 30px rgba(0, 242, 254, 0.7);
            transform: translateY(-2px);
        }}

        /* Space Helmet Field Inputs */
        input, textarea, .stTextInput input, .stNumberInput input {{
            background-color: rgba(10, 14, 30, 0.7) !important;
            color: #E6F1FF !important;
            border-radius: 10px !important;
            border: 1px solid rgba(0, 242, 254, 0.3) !important;
        }}

        /* Navigation Tabs */
        button[data-baseweb="tab"] {{
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 600;
            color: #7A8AA5;
        }}
        button[data-baseweb="tab"][aria-selected="true"] {{
            color: {PULSAR_CYAN} !important;
            border-bottom-color: {PULSAR_CYAN} !important;
        }}

        /* Progress ring label styling */
        .ring-wrap {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
        }}
        .ring {{
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }}
        .ring-inner {{
            border-radius: 50%;
            background: #05070E;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.8);
        }}
        .ring-value {{
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            font-size: 20px;
            color: #F2F7FF;
        }}
        .ring-label {{
            font-size: 11px;
            color: #8CA0C0;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 2px;
        }}

        hr {{
            border-color: rgba(123, 44, 191, 0.3) !important;
        }}
    </style>
    """


def render_progress_ring(label: str, value: float, target: float, color: str = PULSAR_CYAN, unit: str = "") -> str:
    """Return HTML for a single conic-gradient progress ring showing value/target."""
    target = max(target, 1)
    pct = max(0.0, min(value / target, 1.0)) * 100
    over = value > target
    ring_color = NEBULA_PINK if over else color
    size = 130
    thickness = 12
    return f"""
    <div class="ring-wrap">
        <div class="ring" style="
            width:{size}px; height:{size}px;
            background: conic-gradient({ring_color} {pct * 3.6}deg, rgba(255,255,255,0.06) {pct * 3.6}deg);
            box-shadow: 0 0 15px {ring_color}44;
        ">
            <div class="ring-inner" style="width:{size - thickness*2}px; height:{size - thickness*2}px;">
                <div class="ring-value">{value:.0f}{unit}</div>
                <div class="ring-label">/ {target:.0f}{unit}</div>
            </div>
        </div>
        <div class="ring-label" style="color:{ring_color}; font-size:12px; font-weight:bold;">{label}</div>
    </div>
    """


def neo_card_open(title: str = None):
    html = '<div class="neo-card">'
    if title:
        html += f'<div class="neo-card-title">{title}</div>'
    return html


NEO_CARD_CLOSE = "</div>"