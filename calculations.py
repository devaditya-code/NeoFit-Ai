"""
calculations.py
----------------
Evidence-based formulas for estimating daily calorie and macro targets.

Uses the Mifflin-St Jeor equation for BMR (widely regarded as the most
accurate simple formula for the general population), standard activity
multipliers for TDEE, and goal-based calorie/protein adjustments.
"""

ACTIVITY_MULTIPLIERS = {
    "Sedentary (little or no exercise)": 1.2,
    "Lightly active (1-3 days/week)": 1.375,
    "Moderately active (3-5 days/week)": 1.55,
    "Very active (6-7 days/week)": 1.725,
    "Athlete (2x/day training)": 1.9,
}

GOALS = [
    "Weight Loss",
    "Muscle Building",
    "Recomposition (Fat Loss + Muscle Gain)",
    "Maintenance",
]

# Calorie adjustment relative to TDEE, per goal
GOAL_CALORIE_ADJUSTMENT = {
    "Weight Loss": -0.20,               # ~20% deficit
    "Muscle Building": 0.12,            # ~12% surplus
    "Recomposition (Fat Loss + Muscle Gain)": -0.05,  # slight deficit, high protein
    "Maintenance": 0.0,
}

# Protein target in grams per kg of bodyweight, per goal
GOAL_PROTEIN_PER_KG = {
    "Weight Loss": 2.2,
    "Muscle Building": 2.0,
    "Recomposition (Fat Loss + Muscle Gain)": 2.4,
    "Maintenance": 1.8,
}

# Fraction of total calories allocated to fat, per goal (remainder -> carbs)
GOAL_FAT_PERCENT = {
    "Weight Loss": 0.30,
    "Muscle Building": 0.25,
    "Recomposition (Fat Loss + Muscle Gain)": 0.28,
    "Maintenance": 0.28,
}


def lbs_to_kg(lbs: float) -> float:
    return lbs * 0.453592


def kg_to_lbs(kg: float) -> float:
    return kg / 0.453592


def ft_in_to_cm(feet: float, inches: float) -> float:
    return (feet * 12 + inches) * 2.54


def cm_to_ft_in(cm: float):
    total_inches = cm / 2.54
    feet = int(total_inches // 12)
    inches = round(total_inches % 12, 1)
    return feet, inches


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """
    Mifflin-St Jeor Equation:
        Men:   BMR = 10*weight + 6.25*height - 5*age + 5
        Women: BMR = 10*weight + 6.25*height - 5*age - 161
    A neutral average of the two offsets is used for non-binary/other selections.
    """
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    if gender == "Male":
        return base + 5
    elif gender == "Female":
        return base - 161
    else:
        return base - 78  # average offset for other/unspecified


def calculate_tdee(bmr: float, activity_level: str) -> float:
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
    return bmr * multiplier


def calculate_targets(weight_kg: float, height_cm: float, age: int, gender: str,
                       activity_level: str, goal: str) -> dict:
    """
    Full pipeline: BMR -> TDEE -> goal-adjusted calories -> protein/fat/carb split.
    Returns a dict with calories, protein, carbs, fats (all in whole grams/kcal).
    """
    bmr = calculate_bmr(weight_kg, height_cm, age, gender)
    tdee = calculate_tdee(bmr, activity_level)

    adjustment = GOAL_CALORIE_ADJUSTMENT.get(goal, 0.0)
    calories = tdee * (1 + adjustment)

    protein_per_kg = GOAL_PROTEIN_PER_KG.get(goal, 1.8)
    protein_g = protein_per_kg * weight_kg
    protein_kcal = protein_g * 4

    fat_percent = GOAL_FAT_PERCENT.get(goal, 0.28)
    fat_kcal = calories * fat_percent
    fat_g = fat_kcal / 9

    remaining_kcal = max(calories - protein_kcal - fat_kcal, 0)
    carb_g = remaining_kcal / 4

    return {
        "calories": round(calories),
        "protein": round(protein_g),
        "carbs": round(carb_g),
        "fats": round(fat_g),
        "bmr": round(bmr),
        "tdee": round(tdee),
    }
