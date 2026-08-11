"""
ai_engine.py
------------
AI-powered nutrition analysis and coaching feedback.

Tries, in order:
    1. OpenAI GPT-4o (vision + text) if OPENAI_API_KEY is set
    2. Google Gemini Flash (vision + text) if GOOGLE_API_KEY is set
    3. Local mock estimator (keyword-matches FOOD_DB, deterministic coaching
       rules) - this ALWAYS works with zero configuration, so the app is
       fully functional offline / without any API key for local testing.

The public entry point is `analyze_meal()`.
"""

import os
import re
import json
import base64

from food_database import FOOD_DB

SYSTEM_PROMPT = """You are NeoFit AI, an expert sports nutritionist and coach embedded in a \
gym meal-tracking app. Given a meal photo and/or text description (with quantities), estimate \
total nutrition and return STRICT JSON only, no markdown, no commentary, in this exact shape:

{
  "calories": <number>,
  "protein": <number, grams>,
  "carbs": <number, grams>,
  "fats": <number, grams>,
  "feedback": "<2-3 sentence coaching feedback tailored to the user's stated fitness goal>"
}

Be realistic and use standard nutrition knowledge. The feedback should be specific, encouraging, \
and actionable relative to the user's goal (e.g. protein density, portion size, fat/oil usage, \
fiber, meal timing)."""


def _build_user_prompt(description: str, goal: str, targets: dict) -> str:
    return (
        f"User's fitness goal: {goal}\n"
        f"Daily targets: {targets.get('calories')} kcal, {targets.get('protein')}g protein, "
        f"{targets.get('carbs')}g carbs, {targets.get('fats')}g fats.\n"
        f"Meal description provided by user: {description or '(no text description given, rely on image)'}\n"
        "Analyze this meal and return the JSON result now."
    )


# --------------------------------------------------------------------------- #
# Provider 1: OpenAI GPT-4o
# --------------------------------------------------------------------------- #
def _try_openai(description, image_bytes, goal, targets):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        content = [{"type": "text", "text": _build_user_prompt(description, goal, targets)}]
        if image_bytes:
            b64 = base64.b64encode(image_bytes).decode()
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
            })

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": content},
            ],
            max_tokens=500,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content
        return _parse_json_response(raw)
    except Exception as e:
        print(f"[ai_engine] OpenAI call failed, falling back: {e}")
        return None


# --------------------------------------------------------------------------- #
# Provider 2: Google Gemini Flash
# --------------------------------------------------------------------------- #
def _try_gemini(description, image_bytes, goal, targets):
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=SYSTEM_PROMPT)

        parts = [_build_user_prompt(description, goal, targets)]
        if image_bytes:
            parts.append({"mime_type": "image/jpeg", "data": image_bytes})

        response = model.generate_content(parts)
        return _parse_json_response(response.text)
    except Exception as e:
        print(f"[ai_engine] Gemini call failed, falling back: {e}")
        return None


def _parse_json_response(raw: str):
    if not raw:
        return None
    cleaned = raw.strip().replace("```json", "").replace("```", "").strip()
    try:
        data = json.loads(cleaned)
        return {
            "calories": float(data.get("calories", 0)),
            "protein": float(data.get("protein", 0)),
            "carbs": float(data.get("carbs", 0)),
            "fats": float(data.get("fats", 0)),
            "feedback": data.get("feedback", ""),
            "engine": "ai",
        }
    except (json.JSONDecodeError, ValueError, TypeError):
        return None


# --------------------------------------------------------------------------- #
# Provider 3: Local mock estimator (zero-config fallback)
# --------------------------------------------------------------------------- #
_QTY_PATTERN = re.compile(
    r"(?P<qty>\d+(?:\.\d+)?)\s*(?P<unit>g|grams|gram|pcs|piece|pieces|scoop|scoops)?\s*(?:of\s+)?(?P<food>[a-zA-Z /()\-]+)"
)


def _find_best_food_match(food_text: str, food_names_lower: dict):
    """
    Score every FOOD_DB entry against a snippet of free text and return the best match.
    A full-phrase substring match (e.g. "fried chicken" found verbatim) always outranks
    a partial word-overlap match (e.g. only "chicken" found) - this avoids generic shared
    words like "chicken" or "egg" causing an early, wrong match in dict-iteration order.
    """
    best_name, best_score = None, 0
    for key_lower, original_name in food_names_lower.items():
        clean_key = key_lower.replace("(", "").replace(")", "")
        if clean_key in food_text:
            score = 100 + len(clean_key)  # whole-phrase match: strongest signal
        else:
            key_words = [w for w in clean_key.split() if len(w) > 3]
            matched_words = [w for w in key_words if w in food_text]
            if not matched_words:
                continue
            score = len(matched_words) * 10 + sum(len(w) for w in matched_words)
        if score > best_score:
            best_score, best_name = score, original_name
    return best_name


def _mock_parse_description(description: str):
    """Best-effort regex parse of free text into (food_name, quantity) matches against FOOD_DB."""
    matches = []
    if not description:
        return matches

    # Split on commas / 'and' so each clause is parsed independently
    clauses = re.split(r",|\band\b", description)
    food_names_lower = {name.lower(): name for name in FOOD_DB}

    for clause in clauses:
        clause = clause.strip()
        if not clause:
            continue
        m = _QTY_PATTERN.search(clause)
        qty = float(m.group("qty")) if m else 1.0
        unit = (m.group("unit") or "").lower() if m else ""
        food_text = (m.group("food") if m else clause).strip().lower()

        best_match = _find_best_food_match(food_text, food_names_lower)

        if best_match:
            food_data = FOOD_DB[best_match]
            if food_data["unit_type"] == "weight" and unit in ("g", "gram", "grams", ""):
                quantity = qty if qty > 3 else qty * 100  # assume grams; guard tiny numbers
            elif food_data["unit_type"] == "count":
                quantity = qty
            else:
                quantity = qty
            matches.append((best_match, quantity))

    return matches


def _mock_estimate(description, goal, targets):
    from food_database import calculate_nutrition

    matches = _mock_parse_description(description)
    totals = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fats": 0.0}
    matched_names = []

    if matches:
        for name, qty in matches:
            result = calculate_nutrition(name, qty)
            if result:
                for k in totals:
                    totals[k] += result[k]
                matched_names.append(name)
    else:
        # No recognizable foods -> generic balanced-plate estimate so the app never breaks
        totals = {"calories": 450.0, "protein": 30.0, "carbs": 45.0, "fats": 15.0}

    feedback = _generate_coaching_feedback(totals, goal, targets, matched_names)
    totals["feedback"] = feedback
    totals["engine"] = "mock"
    return totals


def _generate_coaching_feedback(totals, goal, targets, matched_names) -> str:
    """Rule-based coaching feedback, tailored to the user's goal and this meal's macro profile."""
    calories = totals["calories"] or 1
    protein_pct = (totals["protein"] * 4) / calories
    fat_pct = (totals["fats"] * 9) / calories
    per_meal_cal_target = (targets.get("calories", 2000)) / 4  # rough per-meal budget

    lines = []
    if matched_names:
        lines.append(f"Logged: {', '.join(matched_names)}.")
    else:
        lines.append("Couldn't confidently identify specific items, so this is a general estimate.")

    if goal == "Muscle Building":
        if totals["protein"] < 25:
            lines.append("For muscle building, aim for at least 25-30g of protein per meal — consider adding a protein source like chicken, eggs, or whey.")
        else:
            lines.append("Great protein density for muscle building — this supports your daily target well.")
        if calories < per_meal_cal_target * 0.7:
            lines.append("This meal is a bit light on calories for a surplus goal; a bigger portion or an extra side would help.")
    elif goal == "Weight Loss":
        if fat_pct > 0.40:
            lines.append("Fat content is fairly high for a cutting phase — consider lowering oil/butter usage to reduce total calories.")
        if calories > per_meal_cal_target * 1.3:
            lines.append("This meal runs above your typical per-meal budget — smaller portions or more veggies could help stay in your deficit.")
        else:
            lines.append("Solid portion size for a fat-loss goal — keep prioritizing protein and fiber to stay full longer.")
    elif goal == "Recomposition (Fat Loss + Muscle Gain)":
        if protein_pct < 0.30:
            lines.append("For recomposition, push protein higher relative to calories — it's the key lever for building muscle while losing fat.")
        else:
            lines.append("Good protein-to-calorie ratio for recomposition — this is exactly the balance you want.")
    else:  # Maintenance / default
        lines.append("This fits reasonably well within a maintenance approach — just keep an eye on overall daily balance.")

    return " ".join(lines)


# --------------------------------------------------------------------------- #
# Public entry point
# --------------------------------------------------------------------------- #
def analyze_meal(description: str, image_bytes: bytes, goal: str, targets: dict) -> dict:
    """
    Analyze a meal (text description and/or image bytes) and return:
        {calories, protein, carbs, fats, feedback, engine}
    Tries real AI providers first, falls back to local mock estimator.
    """
    result = _try_openai(description, image_bytes, goal, targets)
    if result:
        return result

    result = _try_gemini(description, image_bytes, goal, targets)
    if result:
        return result

    return _mock_estimate(description, goal, targets)
