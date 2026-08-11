"""
notifications.py
-----------------
Smart meal-reminder engine. Compares the current time of day against
expected meal windows (Breakfast / Lunch / Dinner) and the set of meal
types already logged today, then surfaces reminders for anything missed.

In this local prototype, "sending a notification" means surfacing a
styled in-app alert banner (st.toast / st.warning in app.py). The logic
here is transport-agnostic, so it could equally drive a desktop
notification (e.g. via `plyer`) or a push/email notification in a
production deployment.
"""

from datetime import datetime, time as dtime

# (meal_type, window_start_hour, window_end_hour)
MEAL_WINDOWS = [
    ("Breakfast", 6, 10),
    ("Lunch", 12, 15),
    ("Dinner", 18, 21),
]


def get_missed_meal_reminders(logged_meal_types: set, current_dt: datetime = None) -> list:
    """
    Return a list of human-readable reminder strings for any meal window that
    has already CLOSED today but was not logged.
    """
    current_dt = current_dt or datetime.now()
    current_hour = current_dt.hour + current_dt.minute / 60

    reminders = []
    for meal_type, start_hour, end_hour in MEAL_WINDOWS:
        window_closed = current_hour > end_hour
        already_logged = meal_type in logged_meal_types
        if window_closed and not already_logged:
            reminders.append(
                f"You haven't logged {meal_type} yet today. Don't forget to track it to stay on target!"
            )
    return reminders


def get_upcoming_meal_hint(logged_meal_types: set, current_dt: datetime = None) -> str:
    """Return a friendly hint about the CURRENT meal window, if inside one and not yet logged."""
    current_dt = current_dt or datetime.now()
    current_hour = current_dt.hour + current_dt.minute / 60

    for meal_type, start_hour, end_hour in MEAL_WINDOWS:
        if start_hour <= current_hour <= end_hour and meal_type not in logged_meal_types:
            return f"It's {meal_type} time — log your meal to keep your streak going!"
    return ""
