"""
app.py
------
NeoFit AI - Gym Meal Tracking & AI Nutrition Buddy
Main Streamlit application entry point.

Run with:
    streamlit run app.py

Optional environment variables (enable real AI vision/text analysis;
the app works fully without them via a local mock estimator):
    OPENAI_API_KEY   - enables GPT-4o meal analysis
    GOOGLE_API_KEY   - enables Gemini 1.5 Flash meal analysis (used if OpenAI key absent)
"""

import os
import calendar as pycalendar
from datetime import datetime, date

import streamlit as st

import database as db
import calculations as calc
import ai_engine
import notifications
from food_database import FOOD_DB, search_food, calculate_nutrition
from auth_utils import detect_identifier_type, is_valid_password
from styles import (
    inject_global_css, render_progress_ring, neo_card_open, NEO_CARD_CLOSE,
    TURQUOISE, PURPLE, GREEN, PINK,
)

# --------------------------------------------------------------------------- #
# App config & bootstrap
# --------------------------------------------------------------------------- #
st.set_page_config(page_title="NeoFit AI", page_icon="⚡", layout="wide",
                    initial_sidebar_state="expanded")
st.markdown(inject_global_css(), unsafe_allow_html=True)
db.init_db()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

MEAL_TYPES = ["Breakfast", "Lunch", "Dinner", "Snack"]

if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "ai_result" not in st.session_state:
    st.session_state.ai_result = None


# --------------------------------------------------------------------------- #
# Small shared helpers
# --------------------------------------------------------------------------- #
def header(title: str, subtitle: str = ""):
    st.markdown(f"## {title}")
    if subtitle:
        st.markdown(f"<div style='color:#7A8AA5; margin-top:-10px; margin-bottom:18px;'>{subtitle}</div>",
                     unsafe_allow_html=True)


def display_targets(profile: dict) -> dict:
    return {
        "calories": profile.get("calorie_target") or 2000,
        "protein": profile.get("protein_target") or 120,
        "carbs": profile.get("carb_target") or 200,
        "fats": profile.get("fat_target") or 60,
    }


def recompute_and_maybe_save(profile: dict, save: bool = True):
    targets = calc.calculate_targets(
        weight_kg=profile["weight_kg"], height_cm=profile["height_cm"],
        age=profile["age"], gender=profile["gender"],
        activity_level=profile["activity_level"], goal=profile["goal"],
    )
    if save:
        db.save_profile(
            profile["user_id"],
            calorie_target=targets["calories"], protein_target=targets["protein"],
            carb_target=targets["carbs"], fat_target=targets["fats"],
        )
    return targets


# --------------------------------------------------------------------------- #
# AUTH PAGE
# --------------------------------------------------------------------------- #
def show_auth_page():
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown(
            f"<h1 style='text-align:center; background:linear-gradient(90deg,{TURQUOISE},{PURPLE});"
            f"-webkit-background-clip:text; -webkit-text-fill-color:transparent; font-size:42px;'>"
            f"⚡ NeoFit AI</h1>",
            unsafe_allow_html=True,
        )
        st.markdown("<p style='text-align:center; color:#7A8AA5;'>Your futuristic AI-powered gym nutrition buddy</p>",
                     unsafe_allow_html=True)
        st.markdown(neo_card_open(), unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["Log In", "Create Account"])

        with tab_login:
            with st.form("login_form"):
                identifier = st.text_input("Email or Phone Number", placeholder="you@example.com or +1234567890")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Log In", use_container_width=True)
                if submitted:
                    user = db.authenticate(identifier.strip(), password)
                    if user:
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please try again.")

        with tab_signup:
            with st.form("signup_form"):
                identifier = st.text_input("Email or Phone Number", key="su_id",
                                            placeholder="you@example.com or +1234567890")
                password = st.text_input("Create Password", type="password", key="su_pw")
                confirm = st.text_input("Confirm Password", type="password", key="su_pw2")
                submitted = st.form_submit_button("Create Account", use_container_width=True)
                if submitted:
                    auth_type = detect_identifier_type(identifier)
                    if not auth_type:
                        st.error("Enter a valid email address or phone number.")
                    elif not is_valid_password(password):
                        st.error("Password must be at least 6 characters.")
                    elif password != confirm:
                        st.error("Passwords do not match.")
                    else:
                        user_id = db.create_user(identifier.strip(), auth_type, password)
                        if user_id is None:
                            st.error("An account with this email/phone already exists.")
                        else:
                            st.session_state.user = db.get_user_by_identifier(identifier.strip())
                            st.success("Account created! Let's set up your profile...")
                            st.rerun()

        st.markdown(NEO_CARD_CLOSE, unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
# ONBOARDING
# --------------------------------------------------------------------------- #
def show_onboarding_page(user_id: int):
    header("Welcome! Let's build your profile ⚡", "This takes 30 seconds and powers your personalized targets.")
    st.markdown(neo_card_open("Step 1 — About You"), unsafe_allow_html=True)

    unit_pref = st.radio("Preferred units", ["Metric (kg/cm)", "Imperial (lbs/ft-in)"], horizontal=True)
    c1, c2 = st.columns(2)
    with c1:
        age = st.number_input("Age", min_value=13, max_value=100, value=25)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    with c2:
        if unit_pref.startswith("Metric"):
            weight = st.number_input("Current Weight (kg)", min_value=30.0, max_value=300.0, value=70.0, step=0.5)
            height = st.number_input("Height (cm)", min_value=120.0, max_value=230.0, value=170.0, step=0.5)
        else:
            weight_lbs = st.number_input("Current Weight (lbs)", min_value=66.0, max_value=660.0, value=154.0, step=1.0)
            feet = st.number_input("Height - feet", min_value=3, max_value=7, value=5)
            inches = st.number_input("Height - inches", min_value=0.0, max_value=11.9, value=7.0, step=0.5)
            weight = calc.lbs_to_kg(weight_lbs)
            height = calc.ft_in_to_cm(feet, inches)

    activity_level = st.selectbox("Activity Level", list(calc.ACTIVITY_MULTIPLIERS.keys()))
    goal = st.selectbox("Primary Goal", calc.GOALS)

    st.markdown(NEO_CARD_CLOSE, unsafe_allow_html=True)
    st.markdown(neo_card_open("Step 2 — Your Daily Targets"), unsafe_allow_html=True)

    preview = calc.calculate_targets(weight, height, int(age), gender, activity_level, goal)
    pc1, pc2, pc3, pc4 = st.columns(4)
    pc1.metric("Calories", f"{preview['calories']} kcal")
    pc2.metric("Protein", f"{preview['protein']} g")
    pc3.metric("Carbs", f"{preview['carbs']} g")
    pc4.metric("Fats", f"{preview['fats']} g")
    st.caption(f"Based on Mifflin-St Jeor: BMR ≈ {preview['bmr']} kcal, TDEE ≈ {preview['tdee']} kcal.")

    customize = st.checkbox("Manually override these targets instead")
    final_targets = dict(preview)
    if customize:
        oc1, oc2, oc3, oc4 = st.columns(4)
        final_targets["calories"] = oc1.number_input("Calories target", value=preview["calories"], step=10)
        final_targets["protein"] = oc2.number_input("Protein target (g)", value=preview["protein"], step=5)
        final_targets["carbs"] = oc3.number_input("Carbs target (g)", value=preview["carbs"], step=5)
        final_targets["fats"] = oc4.number_input("Fats target (g)", value=preview["fats"], step=5)

    st.markdown(NEO_CARD_CLOSE, unsafe_allow_html=True)

    if st.button("Finish Setup & Enter Dashboard", use_container_width=True):
        db.save_profile(
            user_id, age=int(age), gender=gender, weight_kg=weight, height_cm=height,
            activity_level=activity_level, goal=goal,
            unit_pref="metric" if unit_pref.startswith("Metric") else "imperial",
            calorie_target=int(final_targets["calories"]), protein_target=int(final_targets["protein"]),
            carb_target=int(final_targets["carbs"]), fat_target=int(final_targets["fats"]),
            custom_override=1 if customize else 0, onboarding_complete=1,
        )
        st.rerun()


# --------------------------------------------------------------------------- #
# DASHBOARD
# --------------------------------------------------------------------------- #
def show_dashboard(user_id: int, profile: dict):
    header("Today's Dashboard", datetime.now().strftime("%A, %B %d, %Y"))

    today_str = date.today().isoformat()
    totals = db.get_daily_totals(user_id, today_str)
    targets = display_targets(profile)
    logged_types = db.get_logged_meal_types(user_id, today_str)

    # Notifications
    reminders = notifications.get_missed_meal_reminders(logged_types)
    hint = notifications.get_upcoming_meal_hint(logged_types)
    if reminders:
        for r in reminders:
            st.markdown(f"<span class='neo-badge-warn'>🔔 {r}</span>", unsafe_allow_html=True)
        st.write("")
    elif hint:
        st.markdown(f"<span class='neo-badge'>💡 {hint}</span>", unsafe_allow_html=True)
        st.write("")

    st.markdown(neo_card_open("Daily Progress"), unsafe_allow_html=True)
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.markdown(render_progress_ring("Calories", totals["calories"], targets["calories"], TURQUOISE),
                     unsafe_allow_html=True)
    with r2:
        st.markdown(render_progress_ring("Protein", totals["protein"], targets["protein"], GREEN, "g"),
                     unsafe_allow_html=True)
    with r3:
        st.markdown(render_progress_ring("Carbs", totals["carbs"], targets["carbs"], PURPLE, "g"),
                     unsafe_allow_html=True)
    with r4:
        st.markdown(render_progress_ring("Fats", totals["fats"], targets["fats"], PINK, "g"),
                     unsafe_allow_html=True)
    st.markdown(NEO_CARD_CLOSE, unsafe_allow_html=True)

    st.markdown(neo_card_open(f"Today's Logged Meals ({profile.get('goal', '')})"), unsafe_allow_html=True)
    meals = db.get_meals_by_date(user_id, today_str)
    if not meals:
        st.info("No meals logged yet today. Head to 'Log Meal' to get started!")
    else:
        for m in meals:
            with st.expander(f"{m['meal_type']} · {m['log_time']} — {m['calories']:.0f} kcal"):
                st.write(m["description"] or "(logged via food search)")
                mc1, mc2, mc3, mc4 = st.columns(4)
                mc1.metric("Calories", f"{m['calories']:.0f}")
                mc2.metric("Protein", f"{m['protein']:.1f} g")
                mc3.metric("Carbs", f"{m['carbs']:.1f} g")
                mc4.metric("Fats", f"{m['fats']:.1f} g")
                if m.get("ai_feedback"):
                    st.markdown(f"🤖 **AI Coach:** {m['ai_feedback']}")
                if st.button("Delete entry", key=f"del_{m['id']}"):
                    db.delete_meal(m["id"], user_id)
                    st.rerun()
    st.markdown(NEO_CARD_CLOSE, unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
# LOG MEAL
# --------------------------------------------------------------------------- #
def show_log_meal(user_id: int, profile: dict):
    header("Log a Meal", "Describe it, snap it, or both — the AI Nutrition Buddy handles the math.")

    st.markdown(neo_card_open("Meal Details"), unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        meal_type = st.selectbox("Meal Type", MEAL_TYPES)
    with c2:
        log_date = st.date_input("Date", value=date.today())
    with c3:
        log_time = st.time_input("Time", value=datetime.now().time())

    description = st.text_area(
        "Text Description & Quantity",
        placeholder='e.g. "3 boiled eggs, 150g white rice, 100g grilled chicken breast"',
        height=90,
    )
    image_file = st.file_uploader("Upload a photo of your meal (optional)", type=["jpg", "jpeg", "png"])
    if image_file:
        st.image(image_file, caption="Meal photo preview", width=280)

    analyze_clicked = st.button("🤖 Analyze with AI Nutrition Buddy", use_container_width=True)
    st.markdown(NEO_CARD_CLOSE, unsafe_allow_html=True)

    if analyze_clicked:
        if not description and not image_file:
            st.warning("Please add a description or upload a photo first.")
        else:
            image_bytes = image_file.getvalue() if image_file else None
            targets = display_targets(profile)
            with st.spinner("Analyzing your meal..."):
                result = ai_engine.analyze_meal(description, image_bytes, profile.get("goal", "Maintenance"), targets)
            st.session_state.ai_result = result
            st.session_state.ai_result["_description"] = description
            st.session_state.ai_result["_image_bytes"] = image_bytes
            st.session_state.ai_result["_meal_type"] = meal_type
            st.session_state.ai_result["_log_date"] = log_date.isoformat()
            st.session_state.ai_result["_log_time"] = log_time.strftime("%H:%M")

    if st.session_state.ai_result:
        result = st.session_state.ai_result
        engine_label = "Live AI Model" if result.get("engine") == "ai" else "Local Estimator (no API key configured)"
        st.markdown(neo_card_open(f"AI Analysis — {engine_label}"), unsafe_allow_html=True)

        e1, e2, e3, e4 = st.columns(4)
        cal = e1.number_input("Calories (kcal)", value=float(result["calories"]), step=5.0, key="edit_cal")
        prot = e2.number_input("Protein (g)", value=float(result["protein"]), step=1.0, key="edit_prot")
        carb = e3.number_input("Carbs (g)", value=float(result["carbs"]), step=1.0, key="edit_carb")
        fat = e4.number_input("Fats (g)", value=float(result["fats"]), step=1.0, key="edit_fat")

        st.markdown(f"🤖 **AI Coach Feedback:** {result.get('feedback', '')}")

        if st.button("✅ Save to Meal Log", use_container_width=True):
            image_path = None
            if result.get("_image_bytes"):
                image_path = os.path.join(UPLOAD_DIR, f"{user_id}_{datetime.now().timestamp():.0f}.jpg")
                with open(image_path, "wb") as f:
                    f.write(result["_image_bytes"])
            db.log_meal(
                user_id=user_id, log_date=result["_log_date"], log_time=result["_log_time"],
                meal_type=result["_meal_type"], description=result.get("_description", ""),
                calories=cal, protein=prot, carbs=carb, fats=fat,
                image_path=image_path, ai_feedback=result.get("feedback", ""),
                source="image+text" if result.get("_image_bytes") else "text",
            )
            st.session_state.ai_result = None
            st.success("Meal logged successfully!")
            st.rerun()


# --------------------------------------------------------------------------- #
# FOOD SEARCH
# --------------------------------------------------------------------------- #
def show_food_search(user_id: int, profile: dict):
    header("Food Search Engine", "Quickly look up and log foods from our fitness food database.")

    query = st.text_input("Search foods", placeholder="e.g. chicken, oats, whey, paneer...")
    results = search_food(query)

    st.markdown(neo_card_open(f"Results ({len(results)})"), unsafe_allow_html=True)
    if not results:
        st.info("No matching foods found. Try a different search term.")
    for name, data in results[:20]:
        with st.expander(f"{name}  ·  {data['calories']} kcal per {data['unit_label']}"):
            n1, n2, n3, n4 = st.columns(4)
            n1.metric("Calories", data["calories"])
            n2.metric("Protein", f"{data['protein']} g")
            n3.metric("Carbs", f"{data['carbs']} g")
            n4.metric("Fats", f"{data['fats']} g")

            qc1, qc2, qc3, qc4 = st.columns(4)
            with qc1:
                if data["unit_type"] == "count":
                    qty = st.number_input("Quantity (pieces)", min_value=0.5, value=1.0, step=0.5, key=f"qty_{name}")
                else:
                    qty = st.number_input("Quantity (g)", min_value=1.0, value=100.0, step=10.0, key=f"qty_{name}")
            with qc2:
                meal_type = st.selectbox("Meal", MEAL_TYPES, key=f"meal_{name}")
            with qc3:
                log_date = st.date_input("Date", value=date.today(), key=f"date_{name}")
            with qc4:
                st.write("")
                st.write("")
                add_clicked = st.button("➕ Add to Log", key=f"add_{name}")

            if add_clicked:
                nutrition = calculate_nutrition(name, qty)
                db.log_meal(
                    user_id=user_id, log_date=log_date.isoformat(),
                    log_time=datetime.now().strftime("%H:%M"), meal_type=meal_type,
                    description=f"{qty}{'x' if data['unit_type']=='count' else 'g'} {name}",
                    calories=nutrition["calories"], protein=nutrition["protein"],
                    carbs=nutrition["carbs"], fats=nutrition["fats"],
                    source="search",
                )
                st.success(f"Added {name} to your {meal_type} log!")
    st.markdown(NEO_CARD_CLOSE, unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
# CALENDAR & ANALYTICS
# --------------------------------------------------------------------------- #
def show_calendar_analytics(user_id: int, profile: dict):
    header("Calendar & Progress Analytics", "Track your consistency and macro trends over time.")
    targets = display_targets(profile)

    today = date.today()
    c1, c2 = st.columns(2)
    year = c1.selectbox("Year", list(range(today.year - 2, today.year + 1)), index=2)
    month = c2.selectbox("Month", list(range(1, 13)), index=today.month - 1,
                          format_func=lambda m: pycalendar.month_name[m])

    month_meals = db.get_meals_by_month(user_id, year, month)
    by_day = {}
    for m in month_meals:
        by_day.setdefault(m["log_date"], {"calories": 0, "protein": 0, "carbs": 0, "fats": 0})
        by_day[m["log_date"]]["calories"] += m["calories"] or 0
        by_day[m["log_date"]]["protein"] += m["protein"] or 0
        by_day[m["log_date"]]["carbs"] += m["carbs"] or 0
        by_day[m["log_date"]]["fats"] += m["fats"] or 0

    # --- Visual calendar grid ---
    st.markdown(neo_card_open(f"{pycalendar.month_name[month]} {year} — Goal Completion Heatmap"),
                 unsafe_allow_html=True)
    weeks = pycalendar.monthcalendar(year, month)
    day_headers = "".join(f"<th style='color:#7A8AA5; font-weight:500; padding:4px;'>{d}</th>"
                           for d in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"])
    rows_html = ""
    for week in weeks:
        row = "<tr>"
        for day_num in week:
            if day_num == 0:
                row += "<td></td>"
                continue
            d_str = f"{year:04d}-{month:02d}-{day_num:02d}"
            day_totals = by_day.get(d_str)
            if not day_totals:
                bg, txt_color = "rgba(255,255,255,0.03)", "#4A5568"
            else:
                pct = day_totals["calories"] / max(targets["calories"], 1)
                if 0.9 <= pct <= 1.1:
                    bg, txt_color = "rgba(0,255,136,0.25)", GREEN
                elif pct < 0.9:
                    bg, txt_color = "rgba(79,172,254,0.22)", PURPLE
                else:
                    bg, txt_color = "rgba(255,46,159,0.22)", PINK
            row += (f"<td style='background:{bg}; color:{txt_color}; border-radius:8px; "
                    f"text-align:center; padding:10px; font-weight:600;'>{day_num}</td>")
        row += "</tr>"
        rows_html += row
    st.markdown(
        f"<table style='width:100%; border-collapse:separate; border-spacing:4px;'>"
        f"<tr>{day_headers}</tr>{rows_html}</table>",
        unsafe_allow_html=True,
    )
    st.caption("🟢 On target (±10%)   🔵 Under target   🌸 Over target   ⬛ No log")
    st.markdown(NEO_CARD_CLOSE, unsafe_allow_html=True)

    # --- Drill into a specific day ---
    st.markdown(neo_card_open("Daily Breakdown"), unsafe_allow_html=True)
    pick_date = st.date_input("Select a date to inspect", value=today,
                               min_value=date(year, month, 1),
                               max_value=date(year, month, pycalendar.monthrange(year, month)[1]))
    day_totals = db.get_daily_totals(user_id, pick_date.isoformat())
    dc1, dc2, dc3, dc4 = st.columns(4)
    dc1.markdown(render_progress_ring("Calories", day_totals["calories"], targets["calories"], TURQUOISE),
                 unsafe_allow_html=True)
    dc2.markdown(render_progress_ring("Protein", day_totals["protein"], targets["protein"], GREEN, "g"),
                 unsafe_allow_html=True)
    dc3.markdown(render_progress_ring("Carbs", day_totals["carbs"], targets["carbs"], PURPLE, "g"),
                 unsafe_allow_html=True)
    dc4.markdown(render_progress_ring("Fats", day_totals["fats"], targets["fats"], PINK, "g"),
                 unsafe_allow_html=True)
    st.markdown(NEO_CARD_CLOSE, unsafe_allow_html=True)

    # --- Monthly trend chart ---
    st.markdown(neo_card_open("Monthly Macro Trends"), unsafe_allow_html=True)
    if not by_day:
        st.info("No logged data for this month yet.")
    else:
        try:
            import plotly.graph_objects as go
            days_sorted = sorted(by_day.keys())
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=days_sorted, y=[by_day[d]["calories"] for d in days_sorted],
                                       name="Calories", line=dict(color=TURQUOISE, width=3)))
            fig.add_trace(go.Scatter(x=days_sorted, y=[targets["calories"]] * len(days_sorted),
                                       name="Calorie Target", line=dict(color=TURQUOISE, dash="dot", width=1)))
            fig.update_layout(
                template="plotly_dark", height=340,
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.15),
            )
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            st.warning("Install `plotly` for interactive trend charts (`pip install plotly`).")

        # Goal completion rate
        days_on_target = sum(
            1 for d in by_day if 0.9 <= (by_day[d]["calories"] / max(targets["calories"], 1)) <= 1.1
        )
        completion_rate = round(100 * days_on_target / len(by_day)) if by_day else 0
        st.metric("Goal Completion Rate (days within ±10% of calorie target)", f"{completion_rate}%")
    st.markdown(NEO_CARD_CLOSE, unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
# ACCOUNT
# --------------------------------------------------------------------------- #
def show_account(user_id: int, profile: dict, user: dict):
    header("Account & Profile", "Manage your credentials, metrics, and macro targets.")

    st.markdown(neo_card_open("Login Credentials"), unsafe_allow_html=True)
    with st.form("update_identifier_form"):
        new_identifier = st.text_input("Email or Phone", value=user["identifier"])
        submitted = st.form_submit_button("Update Identifier")
        if submitted:
            auth_type = detect_identifier_type(new_identifier)
            if not auth_type:
                st.error("Enter a valid email or phone number.")
            elif db.update_identifier(user_id, new_identifier.strip()):
                st.session_state.user["identifier"] = new_identifier.strip()
                st.success("Identifier updated.")
                st.rerun()
            else:
                st.error("That email/phone is already in use.")

    with st.form("update_password_form"):
        st.write("Change Password")
        current_pw = st.text_input("Current Password", type="password")
        new_pw = st.text_input("New Password", type="password")
        submitted_pw = st.form_submit_button("Update Password")
        if submitted_pw:
            if not db.authenticate(user["identifier"], current_pw):
                st.error("Current password is incorrect.")
            elif not is_valid_password(new_pw):
                st.error("New password must be at least 6 characters.")
            else:
                db.update_password(user_id, new_pw)
                st.success("Password updated.")
    st.markdown(NEO_CARD_CLOSE, unsafe_allow_html=True)

    st.markdown(neo_card_open("Physical Metrics & Goal"), unsafe_allow_html=True)
    with st.form("update_metrics_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            age = st.number_input("Age", min_value=13, max_value=100, value=profile["age"] or 25)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"],
                                   index=["Male", "Female", "Other"].index(profile["gender"] or "Male"))
        with c2:
            weight_kg = st.number_input("Weight (kg)", min_value=30.0, max_value=300.0,
                                         value=float(profile["weight_kg"] or 70.0), step=0.5)
            height_cm = st.number_input("Height (cm)", min_value=120.0, max_value=230.0,
                                         value=float(profile["height_cm"] or 170.0), step=0.5)
        with c3:
            activity_level = st.selectbox("Activity Level", list(calc.ACTIVITY_MULTIPLIERS.keys()),
                                           index=list(calc.ACTIVITY_MULTIPLIERS.keys()).index(
                                               profile["activity_level"]) if profile["activity_level"] in calc.ACTIVITY_MULTIPLIERS else 0)
            goal = st.selectbox("Primary Goal", calc.GOALS,
                                 index=calc.GOALS.index(profile["goal"]) if profile["goal"] in calc.GOALS else 0)

        recalc_submitted = st.form_submit_button("💾 Save & Recalculate Targets", use_container_width=True)
        if recalc_submitted:
            db.save_profile(user_id, age=int(age), gender=gender, weight_kg=weight_kg, height_cm=height_cm,
                             activity_level=activity_level, goal=goal, custom_override=0)
            recompute_and_maybe_save({**profile, "user_id": user_id, "age": int(age), "gender": gender,
                                       "weight_kg": weight_kg, "height_cm": height_cm,
                                       "activity_level": activity_level, "goal": goal}, save=True)
            st.success("Metrics saved and targets recalculated!")
            st.rerun()
    st.markdown(NEO_CARD_CLOSE, unsafe_allow_html=True)

    st.markdown(neo_card_open("Manual Macro Override"), unsafe_allow_html=True)
    st.caption("Prefer to set your own numbers instead of the calculated recommendation? Do it here.")
    with st.form("override_form"):
        targets = display_targets(profile)
        oc1, oc2, oc3, oc4 = st.columns(4)
        cal = oc1.number_input("Calories", value=targets["calories"], step=10)
        prot = oc2.number_input("Protein (g)", value=targets["protein"], step=5)
        carb = oc3.number_input("Carbs (g)", value=targets["carbs"], step=5)
        fat = oc4.number_input("Fats (g)", value=targets["fats"], step=5)
        override_submitted = st.form_submit_button("Save Custom Targets", use_container_width=True)
        if override_submitted:
            db.save_profile(user_id, calorie_target=int(cal), protein_target=int(prot),
                             carb_target=int(carb), fat_target=int(fat), custom_override=1)
            st.success("Custom targets saved.")
            st.rerun()
    if profile.get("custom_override"):
        st.markdown("<span class='neo-badge'>Custom targets active</span>", unsafe_allow_html=True)
    st.markdown(NEO_CARD_CLOSE, unsafe_allow_html=True)

    st.markdown(neo_card_open("AI Engine Status"), unsafe_allow_html=True)
    if os.environ.get("OPENAI_API_KEY"):
        st.markdown("<span class='neo-badge'>🤖 OpenAI GPT-4o connected</span>", unsafe_allow_html=True)
    elif os.environ.get("GOOGLE_API_KEY"):
        st.markdown("<span class='neo-badge'>🤖 Google Gemini Flash connected</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span class='neo-badge-warn'>⚙️ No API key set — using local mock estimator</span>",
                     unsafe_allow_html=True)
        st.caption("Set the OPENAI_API_KEY or GOOGLE_API_KEY environment variable to enable live AI vision analysis.")
    st.markdown(NEO_CARD_CLOSE, unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
# MAIN ROUTER
# --------------------------------------------------------------------------- #
def main():
    if not st.session_state.user:
        show_auth_page()
        return

    user = st.session_state.user
    user_id = user["id"]
    profile = db.get_profile(user_id)

    if not profile or not profile.get("onboarding_complete"):
        show_onboarding_page(user_id)
        return

    with st.sidebar:
        st.markdown(
            f"<h2 style='background:linear-gradient(90deg,{TURQUOISE},{PURPLE}); -webkit-background-clip:text; "
            f"-webkit-text-fill-color:transparent;'>⚡ NeoFit AI</h2>",
            unsafe_allow_html=True,
        )
        st.caption(f"Logged in as {user['identifier']}")
        st.markdown("---")
        page = st.radio("Navigate", ["Dashboard", "Log Meal", "Food Search", "Calendar & Analytics", "Account"],
                         index=["Dashboard", "Log Meal", "Food Search", "Calendar & Analytics", "Account"].index(
                             st.session_state.page),
                         label_visibility="collapsed")
        st.session_state.page = page
        st.markdown("---")
        st.markdown(f"<span class='neo-badge'>{profile.get('goal', 'Maintenance')}</span>", unsafe_allow_html=True)
        if st.button("Log Out", use_container_width=True):
            st.session_state.user = None
            st.session_state.page = "Dashboard"
            st.session_state.ai_result = None
            st.rerun()

    if page == "Dashboard":
        show_dashboard(user_id, profile)
    elif page == "Log Meal":
        show_log_meal(user_id, profile)
    elif page == "Food Search":
        show_food_search(user_id, profile)
    elif page == "Calendar & Analytics":
        show_calendar_analytics(user_id, profile)
    elif page == "Account":
        show_account(user_id, profile, user)


if __name__ == "__main__":
    main()
