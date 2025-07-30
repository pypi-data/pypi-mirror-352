from datetime import date
from functools import wraps
from typing import Callable, Optional, Tuple

from timecraftx.day import Day

VALID_WEEK_STARTS = {Day.MONDAY, Day.SUNDAY}


def ensure_date(func: Callable) -> Callable:
    """
    Decorator that ensures the 'from_date' argument is not None.

    If 'from_date' is None when the decorated function is called,
    it will be replaced with the current date (i.e., date.today()).

    This is useful for functions that operate on dates and want to default
    to "today" without repeating boilerplate checks.

    Note:
        The decorated function must accept 'from_date' as its first parameter.

    Args:
        func: A function that takes 'from_date' as its first positional or keyword argument.

    Returns:
        A wrapped function where 'from_date' defaults to today if not provided.
    """

    @wraps(func)
    def wrapper(from_date: Optional[date] = None, *args, **kwargs):
        if from_date is None:
            from_date = date.today()
        return func(from_date, *args, **kwargs)

    return wrapper


@ensure_date
def normalize_week_inputs(
    from_date: Optional[date] = None, week_start: Day = Day.MONDAY
) -> Tuple[date, int]:
    """
    Normalizes and validates the input date and week_start.

    Ensures the week_start is a supported Day enum (MONDAY or SUNDAY), defaults
    from_date to today if None, and returns both the date and the adjusted weekday index.

    For week_start = SUNDAY, adjusts the weekday so Sunday becomes 0 and Saturday 6.

    Args:
        from_date: The reference date. If None, uses today's date.
        week_start: The starting day of the week (MONDAY or SUNDAY).

    Returns:
        A tuple of (normalized date, adjusted weekday index).

    Raises:
        ValueError: If week_start is not an instance of Day.
        ValueError: If week_start is not Day.MONDAY or Day.SUNDAY.
    """
    if not isinstance(week_start, Day):
        raise ValueError("week_start must be an instance of Day enum")

    if week_start not in VALID_WEEK_STARTS:
        raise ValueError("week_start must be Day.MONDAY or Day.SUNDAY")

    weekday = from_date.weekday()
    if week_start == Day.SUNDAY:
        weekday = (weekday + 1) % 7

    return from_date, weekday
