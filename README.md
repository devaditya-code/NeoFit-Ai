# ⚡ NeoFit AI — Gym Meal Tracking & AI Nutrition Buddy

A fully functional Streamlit prototype: dark-mode, neon-cyber UI, SQLite persistence,
AI-powered meal analysis (with a zero-config local fallback), a searchable fitness
food database, monthly calendar analytics, and a smart meal-reminder engine.

## 1. Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

`openai` and `google-generativeai` are only required if you want **live AI** analysis.
The app works immediately without them, using a local mock nutrition estimator.

## 2. (Optional) Enable live AI meal analysis

Set **one** of these environment variables before launching:

```bash
export OPENAI_API_KEY="sk-..."        # enables GPT-4o vision + text analysis
# or
export GOOGLE_API_KEY="..."           # enables Gemini 1.5 Flash (used if no OpenAI key)
```

If neither is set, the app automatically uses `ai_engine._mock_estimate()` — a
deterministic local estimator that keyword-matches your description against the
built-in food database and generates goal-aware coaching feedback. This means the
app is **fully operational out of the box** for local testing/demos.

## 3. Run

```bash
streamlit run app.py
```

Then open the URL Streamlit prints (typically `http://localhost:8501`).

## 4. Project Structure

```
neofit_app/
├── app.py              # Main Streamlit app: routing, pages, UI composition
├── database.py         # SQLite persistence (users, profiles, meals) + password hashing
├── calculations.py     # Mifflin-St Jeor BMR/TDEE + goal-based macro target formulas
├── ai_engine.py         # AI meal analysis: OpenAI -> Gemini -> local mock, in that order
├── food_database.py    # Pre-loaded fitness food dictionary + search/quantity math
├── notifications.py    # Meal-reminder window logic (Breakfast/Lunch/Dinner)
├── auth_utils.py        # Email/phone validation helpers
├── styles.py            # Dark/neon CSS theme + glassmorphism cards + progress rings
├── requirements.txt
└── neofit.db            # Created automatically on first run (SQLite file)
```

## 5. Feature Walkthrough

- **Auth & Onboarding** — sign up with an email or phone number, then complete a
  one-time questionnaire (age, gender, weight, height, activity level, goal).
  Your recommended calorie/protein/carb/fat targets are calculated instantly, with
  an explicit option to override them manually.
- **AI Meal Logging** — describe a meal in plain text ("3 boiled eggs, 150g white
  rice, 100g chicken breast"), optionally attach a photo, and hit **Analyze**. You
  get back editable calorie/macro numbers plus a short AI coaching note tailored to
  your goal, before you confirm and save the entry.
- **Food Search Engine** — search the built-in database of ~34 popular fitness
  foods, adjust the quantity, and log directly to any meal slot.
- **Calendar & Analytics** — a color-coded monthly heatmap (on target / under /
  over / no log), a per-day macro breakdown with progress rings, a monthly calorie
  trend chart, and a goal-completion-rate metric.
- **Account** — update your email/phone, change your password, edit your physical
  stats/goal (auto-recalculates targets), or set fully custom macro targets.
- **Smart Reminders** — the Dashboard surfaces a banner if a meal window
  (Breakfast/Lunch/Dinner) has closed without a logged meal, or a friendly nudge if
  you're currently inside an unlogged meal window.

## 6. Data Storage

All data is stored locally in a single SQLite file (`neofit.db`), created
automatically on first run. Uploaded meal photos are saved under `uploads/`.
No data leaves your machine except the meal description/photo sent to the AI
provider you've explicitly configured (if any).

## 7. Notes on the AI Integration

`ai_engine.py` is written so swapping or adding providers is straightforward —
`_try_openai()` and `_try_gemini()` are independent, short functions that return
`None` on any failure (missing key, network error, malformed response), causing
the pipeline to fall through to the next provider and ultimately to the local
mock estimator. This means the app never crashes due to AI issues; it degrades
gracefully.
