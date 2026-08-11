"""
app.py
------
NeoFit AI - Space Gym Meal Tracking & AI Nutrition Buddy
Dash Framework Implementation
"""

import os
import base64
from datetime import datetime, date

import dash
from dash import dcc, html, Input, Output, State, callback_context

import database as db
import calculations as calc
import ai_engine
import notifications
from auth_utils import detect_identifier_type, normalize_identifier, is_valid_password
from styles import (
    get_dash_global_css, render_progress_ring, neo_card, header, Row, Col,
    PULSAR_CYAN, COSMIC_PURPLE, HYPERDRIVE_GREEN, NEBULA_PINK, SUPERNOVA_GOLD
)

# --------------------------------------------------------------------------- #
# Image Assets (Gym & Cosmos Themed)
# --------------------------------------------------------------------------- #
IMG_CYBER_GYM = "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=1000&q=80"
IMG_SPACE_WORKOUT = "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=1000&q=80"
IMG_MEAL_PREP = "https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=1000&q=80"

# --------------------------------------------------------------------------- #
# App config & bootstrap
# --------------------------------------------------------------------------- #
app = dash.Dash(__name__, suppress_callback_exceptions=True, title="NeoFit AI — Space Gym")
server = app.server

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
''' + get_dash_global_css() + '''
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

db.init_db()
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

MEAL_TYPES = ["Breakfast", "Lunch", "Dinner", "Snack"]

# --------------------------------------------------------------------------- #
# Main Layout Container
# --------------------------------------------------------------------------- #
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    
    # Client-side session storage
    dcc.Store(id='session-store', storage_type='session', data={}),
    dcc.Store(id='ai-result-store', storage_type='session', data={}),
    
    html.Div(id='page-container', className='app-container')
])


# --------------------------------------------------------------------------- #
# Shared Helpers
# --------------------------------------------------------------------------- #
def display_targets(profile: dict) -> dict:
    return {
        "calories": profile.get("calorie_target") or 2000,
        "protein": profile.get("protein_target") or 120,
        "carbs": profile.get("carb_target") or 200,
        "fats": profile.get("fat_target") or 60,
    }


# --------------------------------------------------------------------------- #
# Page Layout Generators
# --------------------------------------------------------------------------- #
def render_auth_page(error_msg=""):
    return html.Div(className="starry-bg", style={"display": "flex", "justifyContent": "center", "alignItems": "center", "minHeight": "100vh", "padding": "20px"}, children=[
        html.Div(style={"width": "100%", "maxWidth": "440px"}, children=[
            html.Img(src=IMG_CYBER_GYM, className="gym-hero-img"),
            html.H1("🚀 NeoFit AI", style={
                "textAlign": "center", "background": f"linear-gradient(90deg,{PULSAR_CYAN},{COSMIC_PURPLE})",
                "WebkitBackgroundClip": "text", "WebkitTextFillColor": "transparent", "fontSize": "40px", "marginBottom": "4px"
            }),
            html.P("Zero-Gravity AI Nutrition & Cosmic Gym Companion", style={"textAlign": "center", "color": "#A0B0D0", "marginBottom": "24px", "fontWeight": "500"}),
            neo_card([
                dcc.Tabs(id='auth-tabs', value='login', children=[
                    dcc.Tab(label='Log In', value='login', children=[
                        html.Br(),
                        html.Label("EMAIL OR PHONE"),
                        dcc.Input(id='login-id', type='text', placeholder='cadet@spacegym.io', className='neo-input'),
                        html.Label("SECURITY PASSCODE"),
                        dcc.Input(id='login-pw', type='password', placeholder='••••••••', className='neo-input'),
                        html.Button('Launch Session 🚀', id='btn-login', n_clicks=0, className='neo-btn'),
                    ]),
                    dcc.Tab(label='Create Account', value='signup', children=[
                        html.Br(),
                        html.Label("EMAIL OR PHONE"),
                        dcc.Input(id='signup-id', type='text', placeholder='cadet@spacegym.io', className='neo-input'),
                        html.Label("CREATE PASSCODE"),
                        dcc.Input(id='signup-pw', type='password', placeholder='At least 6 characters', className='neo-input'),
                        html.Label("CONFIRM PASSCODE"),
                        dcc.Input(id='signup-pw2', type='password', placeholder='Repeat passcode', className='neo-input'),
                        html.Button('Initiate Account ✨', id='btn-signup', n_clicks=0, className='neo-btn'),
                    ])
                ]),
                html.Div(error_msg, id='auth-error', style={"color": NEBULA_PINK, "marginTop": "14px", "textAlign": "center", "fontWeight": "bold"})
            ])
        ])
    ])

def render_onboarding_page():
    return html.Div(className="starry-bg", style={"padding": "40px 20px", "display": "flex", "justifyContent": "center"}, children=[
        html.Div(style={"width": "100%", "maxWidth": "700px"}, children=[
            header("Welcome Cadet! Calibrating Physical Metrics 🚀", "30-second setup to calculate your gravity-defying macro targets."),
            html.Img(src=IMG_SPACE_WORKOUT, className="gym-hero-img", style={"height": "200px"}),
            neo_card(title="Biometric Baseline", children=[
                html.Label("WEIGHT & MEASUREMENT FORMAT"),
                dcc.RadioItems(
                    id='unit-pref',
                    options=[
                        {'label': ' Metric Format (kg / cm)', 'value': 'metric'},
                        {'label': ' Imperial Format (lbs / inches)', 'value': 'imperial'}
                    ],
                    value='metric',
                    inline=True,
                    className='radio-group'
                ),
                html.Br(),
                Row([
                    Col([
                        html.Label("AGE (YEARS)"),
                        dcc.Input(id='ob-age', type='number', min=13, max=100, value=25, className='neo-input'),
                        html.Label("GENDER IDENTIFIER"),
                        dcc.Dropdown(id='ob-gender', options=['Male', 'Female', 'Other'], value='Male', clearable=False)
                    ]),
                    Col([
                        html.Label("CURRENT WEIGHT (kg or lbs)"),
                        dcc.Input(id='ob-weight', type='number', value=70.0, className='neo-input'),
                        html.Label("HEIGHT (cm or inches)"),
                        dcc.Input(id='ob-height', type='number', value=170.0, className='neo-input'),
                    ])
                ]),
                html.Br(),
                html.Label("ACTIVITY LEVEL"),
                dcc.Dropdown(id='ob-activity', options=list(calc.ACTIVITY_MULTIPLIERS.keys()), value='Sedentary', clearable=False),
                html.Br(),
                html.Label("PRIMARY ORBITAL GOAL"),
                dcc.Dropdown(id='ob-goal', options=calc.GOALS, value='Maintenance', clearable=False),
                html.Br(),
                html.Button("Complete Calibration & Enter Space Station 🛰️", id='btn-onboard', n_clicks=0, className='neo-btn')
            ])
        ])
    ])

def render_dashboard(user_id, profile):
    today_str = date.today().isoformat()
    totals = db.get_daily_totals(user_id, today_str)
    targets = display_targets(profile)
    logged_types = db.get_logged_meal_types(user_id, today_str)

    alerts = []
    reminders = notifications.get_missed_meal_reminders(logged_types)
    hint = notifications.get_upcoming_meal_hint(logged_types)
    if reminders:
        alerts = [html.Span(f"🛰️ ALERT: {r}", className='neo-badge-warn', style={"marginRight": "8px"}) for r in reminders]
    elif hint:
        alerts = [html.Span(f"💡 MISSION HINT: {hint}", className='neo-badge')]

    meals = db.get_meals_by_date(user_id, today_str)
    meal_list = [html.Div("No fuel logged yet today.", style={"color": "#A0B0D0"})] if not meals else [
        html.Div([
            html.H4(f"🚀 {m['meal_type']} · {m['log_time']} — {m['calories']:.0f} kcal"),
            html.P(m["description"] or "(logged via search)", style={"color": "#E0E6ED"}),
            Row([
                Col(html.B(f"Cal: {m['calories']:.0f}", style={"color": PULSAR_CYAN})),
                Col(html.B(f"Pro: {m['protein']:.1f}g", style={"color": HYPERDRIVE_GREEN})),
                Col(html.B(f"Carb: {m['carbs']:.1f}g", style={"color": SUPERNOVA_GOLD})),
                Col(html.B(f"Fat: {m['fats']:.1f}g", style={"color": NEBULA_PINK})),
            ]),
            html.Div(f"🤖 Space AI Coach: {m['ai_feedback']}" if m.get('ai_feedback') else "", style={"color": HYPERDRIVE_GREEN, "fontSize": "13px", "marginTop": "8px", "fontWeight": "500"}),
            html.Hr(style={"borderColor": "rgba(123, 44, 191, 0.3)"})
        ]) for m in meals
    ]

    return html.Div(className='main-content', children=[
        header("Orbital Dashboard", datetime.now().strftime("%A, %B %d, %Y")),
        html.Div(alerts, style={"marginBottom": "16px"}),
        neo_card(title="Daily Fuel Status", children=[
            Row([
                Col(render_progress_ring("Calories", totals["calories"], targets["calories"], PULSAR_CYAN)),
                Col(render_progress_ring("Protein", totals["protein"], targets["protein"], HYPERDRIVE_GREEN, "g")),
                Col(render_progress_ring("Carbs", totals["carbs"], targets["carbs"], SUPERNOVA_GOLD, "g")),
                Col(render_progress_ring("Fats", totals["fats"], targets["fats"], NEBULA_PINK, "g")),
            ])
        ]),
        neo_card(title=f"Logged Fuel Intake — Mission: {profile.get('goal', 'Maintenance')}", children=meal_list)
    ])

def render_log_meal():
    return html.Div(className='main-content', children=[
        header("Log Fuel Intake", "Upload a photo or describe your meal — AI Vision computes macro vectors."),
        html.Img(src=IMG_MEAL_PREP, className="gym-hero-img"),
        neo_card(title="Fuel Entry", children=[
            Row([
                Col([
                    html.Label("MEAL CATEGORY"),
                    dcc.Dropdown(id='lm-type', options=MEAL_TYPES, value='Breakfast', clearable=False)
                ]),
                Col([
                    html.Label("DATE"),
                    dcc.Input(id='lm-date', type='date', value=date.today().isoformat(), className='neo-input')
                ])
            ]),
            html.Br(),
            html.Label("MEAL DESCRIPTION & MASS / QUANTITY"),
            dcc.Textarea(id='lm-desc', placeholder='e.g. "200g grilled salmon, 150g quinoa, 1 avocado"', style={'height': '90px'}, className='neo-input'),
            html.Label("UPLOAD MEAL PHOTO (OPTIONAL)"),
            dcc.Upload(id='lm-upload', children=html.Div(['Drag and Drop or ', html.A('Select Files', style={"color": PULSAR_CYAN})]), 
                       style={'width': '100%', 'height': '60px', 'lineHeight': '60px', 'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '10px', 'textAlign': 'center', 'marginBottom': '16px', 'borderColor': PULSAR_CYAN, 'color': '#FFFFFF'}),
            html.Div(id='lm-preview'),
            html.Button("🤖 Analyze with Space AI", id='btn-analyze', n_clicks=0, className='neo-btn')
        ]),
        html.Div(id='lm-ai-result-container')
    ])

# --------------------------------------------------------------------------- #
# Core Routing Callback
# --------------------------------------------------------------------------- #
@app.callback(
    Output('page-container', 'children'),
    [Input('url', 'pathname'), Input('session-store', 'data')]
)
def display_page(pathname, session_data):
    user_id = session_data.get('user_id') if session_data else None
    
    if not user_id:
        return render_auth_page()
    
    profile = db.get_profile(user_id)
    if not profile or not profile.get("onboarding_complete"):
        return render_onboarding_page()

    # --- Populating Space Station Cadet Details ---
    unit_label = "kg" if profile.get("unit_pref") == "metric" else "lbs"
    weight_val = profile.get("weight_kg", "--")
    goal_val = profile.get("goal", "Maintenance")
    cal_target = profile.get("calorie_target", 2000)
    user_identifier = profile.get("identifier", f"Cadet #{user_id}")

    cadet_info_card = html.Div(style={
        "background": "rgba(0, 242, 254, 0.08)",
        "borderRadius": "12px",
        "padding": "14px",
        "border": f"1px solid rgba(0, 242, 254, 0.3)",
        "marginBottom": "20px"
    }, children=[
        html.Div("👨‍🚀 SPACE STATION CADET", style={"color": PULSAR_CYAN, "fontSize": "11px", "fontWeight": "bold", "letterSpacing": "1px"}),
        html.Div(f"ID: {user_identifier}", style={"color": "#FFFFFF", "fontSize": "13px", "fontWeight": "600", "marginTop": "4px"}),
        html.Hr(style={"borderColor": "rgba(0, 242, 254, 0.2)", "margin": "8px 0"}),
        html.Div(f"🎯 Goal: {goal_val}", style={"color": "#E0E6ED", "fontSize": "12px"}),
        html.Div(f"⚖️ Weight: {weight_val} {unit_label}", style={"color": "#E0E6ED", "fontSize": "12px", "marginTop": "3px"}),
        html.Div(f"🔥 Target: {cal_target:.0f} kcal/day", style={"color": HYPERDRIVE_GREEN, "fontSize": "12px", "marginTop": "3px", "fontWeight": "600"}),
    ])

    nav_links = [
        {"path": "/", "label": "Dashboard"},
        {"path": "/log-meal", "label": "Log Meal"},
        {"path": "/analytics", "label": "Calendar & Analytics"}
    ]
    
    sidebar = html.Div(className='sidebar', children=[
        html.H2("🚀 NeoFit AI", style={"background": f"linear-gradient(90deg,{PULSAR_CYAN},{COSMIC_PURPLE})", "WebkitBackgroundClip": "text", "WebkitTextFillColor": "transparent"}),
        cadet_info_card,
        html.Hr(style={"borderColor": "rgba(123, 44, 191, 0.3)", "width": "100%"}),
        *[dcc.Link(html.Button(link["label"], className=f"neo-btn neo-btn-nav {'active' if pathname == link['path'] else ''}"), href=link["path"]) for link in nav_links],
        html.Hr(style={"borderColor": "rgba(123, 44, 191, 0.3)", "width": "100%", "marginTop": "auto"}),
        html.Button("Log Out", id='btn-logout', className='neo-btn', style={"background": "transparent", "border": f"1px solid {NEBULA_PINK}", "color": NEBULA_PINK})
    ])

    if pathname == "/log-meal":
        content = render_log_meal()
    elif pathname == "/analytics":
        content = html.Div(className='main-content', children=[header("Analytics", "Coming soon to the Dash module.")])
    else:
        content = render_dashboard(user_id, profile)

    return [sidebar, content]


# --------------------------------------------------------------------------- #
# Action Callbacks
# --------------------------------------------------------------------------- #

# 1. Login Callback
@app.callback(
    [Output('session-store', 'data', allow_duplicate=True), Output('auth-error', 'children', allow_duplicate=True)],
    Input('btn-login', 'n_clicks'),
    [State('login-id', 'value'), State('login-pw', 'value')],
    prevent_initial_call=True
)
def handle_login(n_clicks, lid, lpw):
    if not n_clicks:
        return dash.no_update, dash.no_update
    if not lid or not lpw:
        return dash.no_update, "Please enter both Email/Phone and Password."
    
    norm_id = normalize_identifier(lid)
    user = db.authenticate(norm_id, lpw)
    if user:
        return {'user_id': user['id']}, ""
    return dash.no_update, "Invalid credentials. Check your details or create an account."


# 2. Signup Callback
@app.callback(
    [Output('session-store', 'data', allow_duplicate=True), Output('auth-error', 'children', allow_duplicate=True)],
    Input('btn-signup', 'n_clicks'),
    [State('signup-id', 'value'), State('signup-pw', 'value'), State('signup-pw2', 'value')],
    prevent_initial_call=True
)
def handle_signup(n_clicks, sid, spw, spw2):
    if not n_clicks:
        return dash.no_update, dash.no_update
    if not sid or not spw or not spw2:
        return dash.no_update, "Please fill in all signup fields."
    if spw != spw2:
        return dash.no_update, "Passwords do not match."
    
    norm_id = normalize_identifier(sid)
    auth_type = detect_identifier_type(norm_id)
    if not auth_type:
        return dash.no_update, "Please enter a valid email or phone number."
    if not is_valid_password(spw):
        return dash.no_update, "Password is too weak (must be at least 6 characters)."
    
    user_id = db.create_user(norm_id, auth_type, spw)
    if user_id:
        return {'user_id': user_id}, ""
    return dash.no_update, "An account with this email/phone already exists."


# 3. Logout Callback
@app.callback(
    Output('session-store', 'data', allow_duplicate=True),
    Input('btn-logout', 'n_clicks'),
    prevent_initial_call=True
)
def handle_logout(n_clicks):
    if n_clicks:
        return {}
    return dash.no_update


# 4. Onboarding Callback
@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    Input('btn-onboard', 'n_clicks'),
    [State('session-store', 'data'), State('ob-age', 'value'), State('ob-gender', 'value'),
     State('ob-weight', 'value'), State('ob-height', 'value'), State('ob-activity', 'value'), State('ob-goal', 'value'), State('unit-pref', 'value')],
    prevent_initial_call=True
)
def complete_onboarding(n_clicks, session_data, age, gender, weight, height, activity, goal, unit_pref):
    if n_clicks > 0 and session_data.get('user_id'):
        user_id = session_data['user_id']
        targets = calc.calculate_targets(weight, height, int(age), gender, activity, goal)
        db.save_profile(
            user_id, age=int(age), gender=gender, weight_kg=weight, height_cm=height,
            activity_level=activity, goal=goal, unit_pref=unit_pref or "metric",
            calorie_target=targets["calories"], protein_target=targets["protein"],
            carb_target=targets["carbs"], fat_target=targets["fats"], custom_override=0, onboarding_complete=1
        )
        return "/"
    return dash.no_update


# 5. Meal AI Analysis
@app.callback(
    [Output('lm-ai-result-container', 'children'), Output('ai-result-store', 'data')],
    Input('btn-analyze', 'n_clicks'),
    [State('lm-desc', 'value'), State('lm-upload', 'contents'), State('lm-type', 'value'),
     State('lm-date', 'value'), State('session-store', 'data')],
    prevent_initial_call=True
)
def analyze_meal(n_clicks, desc, upload_contents, meal_type, log_date, session_data):
    if n_clicks > 0:
        if not desc and not upload_contents:
            return html.Div("Please add a description or photo.", style={"color": NEBULA_PINK}), dash.no_update
        
        image_bytes = None
        if upload_contents:
            content_type, content_string = upload_contents.split(',')
            image_bytes = base64.b64decode(content_string)

        profile = db.get_profile(session_data['user_id'])
        targets = display_targets(profile)
        
        result = ai_engine.analyze_meal(desc or "", image_bytes, profile.get("goal", "Maintenance"), targets)
        
        store_data = {
            "cal": result["calories"], "pro": result["protein"], "carb": result["carbs"], "fat": result["fats"],
            "desc": desc or "Scanned Meal", "type": meal_type, "date": log_date, "feedback": result.get("feedback", ""),
            "img_str": upload_contents.split(',')[1] if upload_contents else None
        }

        ui = neo_card(title="AI Analysis Complete", children=[
            Row([
                Col([html.Label("CALORIES (KCAL)"), dcc.Input(id='edit-cal', type='number', value=result["calories"], className='neo-input')]),
                Col([html.Label("PROTEIN (G)"), dcc.Input(id='edit-pro', type='number', value=result["protein"], className='neo-input')]),
                Col([html.Label("CARBS (G)"), dcc.Input(id='edit-carb', type='number', value=result["carbs"], className='neo-input')]),
                Col([html.Label("FATS (G)"), dcc.Input(id='edit-fat', type='number', value=result["fats"], className='neo-input')]),
            ]),
            html.P(f"🤖 Space Coach Advice: {result.get('feedback', '')}", style={"color": HYPERDRIVE_GREEN, "fontWeight": "bold"}),
            html.Button("✅ Confirm & Save Fuel Log", id='btn-save-meal', n_clicks=0, className='neo-btn'),
            html.Div(id='save-meal-status', style={"marginTop": "10px"})
        ])
        return ui, store_data
    return dash.no_update, dash.no_update


# 6. Save Meal Log
@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    Input('btn-save-meal', 'n_clicks'),
    [State('edit-cal', 'value'), State('edit-pro', 'value'), State('edit-carb', 'value'), State('edit-fat', 'value'),
     State('ai-result-store', 'data'), State('session-store', 'data')],
    prevent_initial_call=True
)
def save_meal(n_clicks, cal, pro, carb, fat, ai_data, session_data):
    if n_clicks > 0 and ai_data:
        image_path = None
        if ai_data.get("img_str"):
            image_path = os.path.join(UPLOAD_DIR, f"{session_data['user_id']}_{datetime.now().timestamp():.0f}.jpg")
            with open(image_path, "wb") as f:
                f.write(base64.b64decode(ai_data["img_str"]))

        db.log_meal(
            user_id=session_data['user_id'], log_date=ai_data['date'], log_time=datetime.now().strftime("%H:%M"),
            meal_type=ai_data['type'], description=ai_data['desc'],
            calories=cal, protein=pro, carbs=carb, fats=fat,
            image_path=image_path, ai_feedback=ai_data['feedback'], source="dash-app"
        )
        return "/"
    return dash.no_update


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True)