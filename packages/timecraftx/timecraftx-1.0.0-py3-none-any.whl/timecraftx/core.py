from datetime import date, timedelta
from typing import Optional

from timecraftx.day import Day
from timecraftx.utils import ensure_date, normalize_week_inputs


def start_of_week(
    from_date: Optional[date] = None, week_start: Day = Day.MONDAY
) -> date:
    """
    Returns the date corresponding to the first day of the week for the given date.

    Args:
        from_date: The reference date. Defaults to today if None.
        week_start: The starting day of the week (MONDAY or SUNDAY).

    Returns:
        A date object representing the start of the week.

    Raises:
        ValueError: If week_start is not an instance of Day.
        ValueError: If week_start is not Day.MONDAY or Day.SUNDAY.
    """
    from_date, weekday = normalize_week_inputs(from_date, week_start)
    return from_date - timedelta(days=weekday)


def end_of_week(from_date: Optional[date] = None, week_start: Day = Day.MONDAY) -> date:
    """
    Returns the date corresponding to the last day of the week for the given date.

    Args:
        from_date: The reference date. Defaults to today if None.
        week_start: The starting day of the week (MONDAY or SUNDAY).

    Returns:
        A date object representing the end of the week.

    Raises:
        ValueError: If week_start is not an instance of Day.
        ValueError: If week_start is not Day.MONDAY or Day.SUNDAY.
    """
    from_date, weekday = normalize_week_inputs(from_date, week_start)
    return from_date + timedelta(days=(6 - weekday))


@ensure_date
def tomorrow(from_date: Optional[date] = None) -> date:
    """
    Returns the date for tomorrow relative to a given date.

    Args:
        from_date: The reference date. Defaults to today if None.

    Returns:
        The date for tomorrow.
    """
    return from_date + timedelta(days=1)


@ensure_date
def yesterday(from_date: Optional[date] = None) -> date:
    """
    Returns the date for yesterday relative to a given date.

    Args:
        from_date: The reference date. Defaults to today if None.

    Returns:
        The date for yesterday.
    """
    return from_date - timedelta(days=1)


@ensure_date
def next_weekday(from_date: Optional[date] = None, target: Day = Day.MONDAY) -> date:
    """
    Calculates the next occurrence of a specific weekday after the given date.

    If the given date is already the target weekday, the function returns the date
    for the following week's occurrence of that weekday.

    Args:
        from_date (Optional[date]): The starting date. If None, defaults to today.
        target (Day): The target weekday to find the next occurrence of.

    Returns:
        date: The date of the next occurrence of the specified weekday.
    """
    current = from_date.weekday()
    target_day = target.value

    days_ahead = (target_day - current + 7) % 7
    if days_ahead == 0:
        days_ahead = 7

    return from_date + timedelta(days=days_ahead)


def next_monday(from_date: Optional[date] = None) -> date:
    """Returns the next Monday after the given date (or today if not provided)."""
    return next_weekday(from_date, Day.MONDAY)


def next_tuesday(from_date: Optional[date] = None) -> date:
    """Returns the next Tuesday after the given date (or today if not provided)."""
    return next_weekday(from_date, Day.TUESDAY)


def next_wednesday(from_date: Optional[date] = None) -> date:
    """Returns the next Wednesday after the given date (or today if not provided)."""
    return next_weekday(from_date, Day.WEDNESDAY)


def next_thursday(from_date: Optional[date] = None) -> date:
    """Returns the next Thursday after the given date (or today if not provided)."""
    return next_weekday(from_date, Day.THURSDAY)


def next_friday(from_date: Optional[date] = None) -> date:
    """Returns the next Friday after the given date (or today if not provided)."""
    return next_weekday(from_date, Day.FRIDAY)


def next_saturday(from_date: Optional[date] = None) -> date:
    """Returns the next Saturday after the given date (or today if not provided)."""
    return next_weekday(from_date, Day.SATURDAY)


def next_sunday(from_date: Optional[date] = None) -> date:
    """Returns the next Sunday after the given date (or today if not provided)."""
    return next_weekday(from_date, Day.SUNDAY)


@ensure_date
def prev_weekday(from_date: Optional[date] = None, target: Day = Day.MONDAY) -> date:
    """
    Calculates the previous occurrence of a specific weekday before the given date.
    If the date is already the target day, returns the previous week's occurrence.

    Args:
        from_date (Optional[date]): The starting date. Defaults to today.
        target (Day): The weekday to find.

    Returns:
        date: The previous occurrence of the specified weekday.
    """
    current = from_date.weekday()
    target_day = target.value
    days_behind = (current - target_day + 7) % 7 or 7

    return from_date - timedelta(days=days_behind)


def prev_monday(from_date: Optional[date] = None) -> date:
    """Returns the previous Monday before the given date (or today if not provided)."""
    return prev_weekday(from_date, Day.MONDAY)


def prev_tuesday(from_date: Optional[date] = None) -> date:
    """Returns the previous Tuesday before the given date (or today if not provided)."""
    return prev_weekday(from_date, Day.TUESDAY)


def prev_wednesday(from_date: Optional[date] = None) -> date:
    """Returns the previous Wednesday before the given date (or today if not provided)."""
    return prev_weekday(from_date, Day.WEDNESDAY)


def prev_thursday(from_date: Optional[date] = None) -> date:
    """Returns the previous Thursday before the given date (or today if not provided)."""
    return prev_weekday(from_date, Day.THURSDAY)


def prev_friday(from_date: Optional[date] = None) -> date:
    """Returns the previous Friday before the given date (or today if not provided)."""
    return prev_weekday(from_date, Day.FRIDAY)


def prev_saturday(from_date: Optional[date] = None) -> date:
    """Returns the previous Saturday before the given date (or today if not provided)."""
    return prev_weekday(from_date, Day.SATURDAY)


def prev_sunday(from_date: Optional[date] = None) -> date:
    """Returns the previous Sunday before the given date (or today if not provided)."""
    return prev_weekday(from_date, Day.SUNDAY)
