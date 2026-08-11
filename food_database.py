"""
food_database.py
-----------------
A pre-loaded local dictionary of popular fitness/gym foods, used by:
    - the in-app Food Search Engine (direct logging)
    - the mock AI nutrition engine (keyword-matching fallback when no
      external LLM/vision API key is configured)

Each entry's `unit_type` is either:
    "count"  -> nutrition values are PER PIECE  (e.g. 1 egg, 1 scoop)
    "weight" -> nutrition values are PER 100 GRAMS
"""

FOOD_DB = {
    "Boiled Egg":            {"unit_type": "count",  "unit_label": "egg (50g)",     "calories": 78,  "protein": 6.3, "carbs": 0.6,  "fats": 5.3},
    "Poached Egg":           {"unit_type": "count",  "unit_label": "egg (50g)",     "calories": 75,  "protein": 6.3, "carbs": 0.4,  "fats": 5.0},
    "Fried Egg":             {"unit_type": "count",  "unit_label": "egg (50g)",     "calories": 90,  "protein": 6.3, "carbs": 0.4,  "fats": 7.0},
    "Egg Whites":            {"unit_type": "count",  "unit_label": "white (33g)",   "calories": 17,  "protein": 3.6, "carbs": 0.2,  "fats": 0.1},
    "Grilled Chicken Breast": {"unit_type": "weight", "unit_label": "100g cooked",  "calories": 165, "protein": 31,  "carbs": 0,    "fats": 3.6},
    "Fried Chicken":         {"unit_type": "weight", "unit_label": "100g",          "calories": 246, "protein": 24,  "carbs": 8,    "fats": 14},
    "Chicken Thigh (grilled)": {"unit_type": "weight", "unit_label": "100g",        "calories": 209, "protein": 26,  "carbs": 0,    "fats": 10.9},
    "Salmon (cooked)":       {"unit_type": "weight", "unit_label": "100g",          "calories": 208, "protein": 20,  "carbs": 0,    "fats": 13},
    "Tuna (canned in water)": {"unit_type": "weight", "unit_label": "100g",         "calories": 116, "protein": 26,  "carbs": 0,    "fats": 1},
    "Lean Ground Beef (90/10)": {"unit_type": "weight", "unit_label": "100g cooked", "calories": 176, "protein": 20, "carbs": 0,    "fats": 10},
    "Whey Protein (1 scoop)": {"unit_type": "count",  "unit_label": "scoop (30g)",  "calories": 120, "protein": 24,  "carbs": 3,    "fats": 1.5},
    "Cottage Cheese / Paneer": {"unit_type": "weight", "unit_label": "100g",        "calories": 265, "protein": 18,  "carbs": 3.4,  "fats": 20},
    "Low-fat Cottage Cheese": {"unit_type": "weight", "unit_label": "100g",         "calories": 98,  "protein": 11,  "carbs": 3.4,  "fats": 4.3},
    "Greek Yogurt (plain)":  {"unit_type": "weight", "unit_label": "100g",          "calories": 59,  "protein": 10,  "carbs": 3.6,  "fats": 0.4},
    "Milk (whole)":          {"unit_type": "weight", "unit_label": "100ml",         "calories": 61,  "protein": 3.2, "carbs": 4.8,  "fats": 3.3},
    "White Rice (cooked)":   {"unit_type": "weight", "unit_label": "100g",          "calories": 130, "protein": 2.7, "carbs": 28,   "fats": 0.3},
    "Brown Rice (cooked)":   {"unit_type": "weight", "unit_label": "100g",          "calories": 123, "protein": 2.7, "carbs": 26,   "fats": 1.0},
    "Oats (dry)":            {"unit_type": "weight", "unit_label": "100g",          "calories": 389, "protein": 17,  "carbs": 66,   "fats": 7},
    "Whole Wheat Roti/Chapati": {"unit_type": "count", "unit_label": "piece (40g)", "calories": 104, "protein": 3.1, "carbs": 18,   "fats": 2.5},
    "Sweet Potato (baked)":  {"unit_type": "weight", "unit_label": "100g",          "calories": 90,  "protein": 2,   "carbs": 21,   "fats": 0.1},
    "White Potato (boiled)": {"unit_type": "weight", "unit_label": "100g",          "calories": 87,  "protein": 1.9, "carbs": 20,   "fats": 0.1},
    "Whole Wheat Bread":     {"unit_type": "count",  "unit_label": "slice (30g)",   "calories": 82,  "protein": 4,   "carbs": 14,   "fats": 1.1},
    "Banana":                {"unit_type": "count",  "unit_label": "medium (118g)", "calories": 105, "protein": 1.3, "carbs": 27,   "fats": 0.4},
    "Apple":                 {"unit_type": "count",  "unit_label": "medium (182g)", "calories": 95,  "protein": 0.5, "carbs": 25,   "fats": 0.3},
    "Almonds":               {"unit_type": "weight", "unit_label": "100g",          "calories": 579, "protein": 21,  "carbs": 22,   "fats": 50},
    "Peanut Butter":         {"unit_type": "weight", "unit_label": "100g",          "calories": 588, "protein": 25,  "carbs": 20,   "fats": 50},
    "Avocado":               {"unit_type": "count",  "unit_label": "medium (150g)", "calories": 240, "protein": 3,   "carbs": 13,   "fats": 22},
    "Olive Oil":             {"unit_type": "weight", "unit_label": "100ml (~7 tbsp)", "calories": 884, "protein": 0, "carbs": 0,    "fats": 100},
    "Broccoli (steamed)":    {"unit_type": "weight", "unit_label": "100g",          "calories": 35,  "protein": 2.4, "carbs": 7,    "fats": 0.4},
    "Mixed Salad Greens":    {"unit_type": "weight", "unit_label": "100g",          "calories": 20,  "protein": 1.5, "carbs": 3.8,  "fats": 0.2},
    "Lentils / Dal (cooked)": {"unit_type": "weight", "unit_label": "100g",         "calories": 116, "protein": 9,   "carbs": 20,   "fats": 0.4},
    "Chickpeas (cooked)":    {"unit_type": "weight", "unit_label": "100g",          "calories": 164, "protein": 8.9, "carbs": 27,   "fats": 2.6},
    "Tofu":                  {"unit_type": "weight", "unit_label": "100g",          "calories": 76,  "protein": 8,   "carbs": 1.9,  "fats": 4.8},
    "Protein Bar (avg)":     {"unit_type": "count",  "unit_label": "bar (60g)",     "calories": 220, "protein": 20,  "carbs": 22,   "fats": 8},
}


def search_food(query: str):
    """Case-insensitive substring search over the food database. Returns list of (name, data) tuples."""
    if not query:
        return list(FOOD_DB.items())
    q = query.strip().lower()
    return [(name, data) for name, data in FOOD_DB.items() if q in name.lower()]


def calculate_nutrition(food_name: str, quantity: float):
    """
    Compute total macros for a given food and quantity.
    For 'count' items, quantity is number of pieces.
    For 'weight' items, quantity is grams (nutrition data is per 100g, so scale by /100).
    """
    food = FOOD_DB.get(food_name)
    if not food:
        return None
    if food["unit_type"] == "count":
        factor = quantity
    else:
        factor = quantity / 100.0
    return {
        "calories": round(food["calories"] * factor, 1),
        "protein": round(food["protein"] * factor, 1),
        "carbs": round(food["carbs"] * factor, 1),
        "fats": round(food["fats"] * factor, 1),
    }
