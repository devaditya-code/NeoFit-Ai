"""
styles.py
---------
Central place for the app's "sleek dark mode + neon cyber" visual identity:
custom CSS injection, glassmorphism card helpers, and conic-gradient
progress rings rendered as raw HTML (no extra charting dependency needed
for the core rings).
"""

# Neon accent palette
TURQUOISE = "#00F2FE"
PURPLE = "#4FACFE"
GREEN = "#00FF88"
PINK = "#FF2E9F"
BG_DARK = "#0A0E17"
BG_CARD = "rgba(255, 255, 255, 0.04)"


def inject_global_css():
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}

        .stApp {{
            background: radial-gradient(circle at 15% 0%, #10182b 0%, {BG_DARK} 45%, #05070c 100%);
            color: #E6F1FF;
        }}

        h1, h2, h3, h4 {{
            font-family: 'Space Grotesk', sans-serif !important;
            letter-spacing: 0.3px;
        }}

        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #0B1120 0%, #060A12 100%);
            border-right: 1px solid rgba(0, 242, 254, 0.15);
        }}

        /* Glassmorphism card */
        .neo-card {{
            background: {BG_CARD};
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(0, 242, 254, 0.18);
            border-radius: 18px;
            padding: 22px 24px;
            margin-bottom: 18px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
        }}

        .neo-card-title {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: {TURQUOISE};
            opacity: 0.85;
            margin-bottom: 6px;
        }}

        .neo-badge {{
            display: inline-block;
            padding: 3px 12px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 600;
            background: rgba(0, 255, 136, 0.12);
            color: {GREEN};
            border: 1px solid rgba(0, 255, 136, 0.4);
        }}

        .neo-badge-warn {{
            background: rgba(255, 46, 159, 0.12);
            color: {PINK};
            border: 1px solid rgba(255, 46, 159, 0.4);
        }}

        /* Buttons */
        div.stButton > button, div.stFormSubmitButton > button {{
            background: linear-gradient(90deg, {TURQUOISE} 0%, {PURPLE} 100%);
            color: #04101c;
            font-weight: 700;
            border: none;
            border-radius: 12px;
            padding: 0.55em 1.4em;
            box-shadow: 0 0 18px rgba(0, 242, 254, 0.35);
            transition: all 0.2s ease-in-out;
        }}
        div.stButton > button:hover {{
            box-shadow: 0 0 28px rgba(0, 242, 254, 0.6);
            transform: translateY(-1px);
        }}

        /* Inputs */
        input, textarea, .stTextInput input, .stNumberInput input {{
            background-color: rgba(255,255,255,0.05) !important;
            color: #E6F1FF !important;
            border-radius: 10px !important;
            border: 1px solid rgba(0, 242, 254, 0.25) !important;
        }}

        /* Tabs */
        button[data-baseweb="tab"] {{
            font-family: 'Space Grotesk', sans-serif;
            color: #7A8AA5;
        }}
        button[data-baseweb="tab"][aria-selected="true"] {{
            color: {TURQUOISE} !important;
            border-bottom-color: {TURQUOISE} !important;
        }}

        /* Progress ring */
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
            background: #0A0E17;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
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
            border-color: rgba(0, 242, 254, 0.15) !important;
        }}
    </style>
    """


def render_progress_ring(label: str, value: float, target: float, color: str = TURQUOISE, unit: str = "") -> str:
    """Return HTML for a single conic-gradient progress ring showing value/target."""
    target = max(target, 1)
    pct = max(0.0, min(value / target, 1.0)) * 100
    over = value > target
    ring_color = "#FF2E9F" if over else color
    size = 130
    thickness = 12
    return f"""
    <div class="ring-wrap">
        <div class="ring" style="
            width:{size}px; height:{size}px;
            background: conic-gradient({ring_color} {pct * 3.6}deg, rgba(255,255,255,0.07) {pct * 3.6}deg);
        ">
            <div class="ring-inner" style="width:{size - thickness*2}px; height:{size - thickness*2}px;">
                <div class="ring-value">{value:.0f}{unit}</div>
                <div class="ring-label">/ {target:.0f}{unit}</div>
            </div>
        </div>
        <div class="ring-label" style="color:{ring_color}; font-size:12px;">{label}</div>
    </div>
    """


def neo_card_open(title: str = None):
    html = '<div class="neo-card">'
    if title:
        html += f'<div class="neo-card-title">{title}</div>'
    return html


NEO_CARD_CLOSE = "</div>"
