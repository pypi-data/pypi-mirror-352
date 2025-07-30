from datetime import date
from unittest.mock import MagicMock, patch

from timecraftx import (
    Day,
    next_friday,
    next_monday,
    next_saturday,
    next_sunday,
    next_thursday,
    next_tuesday,
    next_wednesday,
    next_weekday,
)

FIXED_TODAY = date(year=2025, month=6, day=4)


class TestNextWeekDay:
    @patch("timecraftx.utils.date")
    def test_next_weekday_default(self, mock_date: MagicMock):
        mock_date.today.return_value = FIXED_TODAY
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        assert next_weekday(target=Day.THURSDAY) == date(year=2025, month=6, day=5)
        assert next_thursday() == date(year=2025, month=6, day=5)

        assert next_weekday(target=Day.FRIDAY) == date(year=2025, month=6, day=6)
        assert next_friday() == date(year=2025, month=6, day=6)

        assert next_weekday(target=Day.SATURDAY) == date(year=2025, month=6, day=7)
        assert next_saturday() == date(year=2025, month=6, day=7)

        assert next_weekday(target=Day.SUNDAY) == date(year=2025, month=6, day=8)
        assert next_sunday() == date(year=2025, month=6, day=8)

        assert next_weekday(target=Day.MONDAY) == date(year=2025, month=6, day=9)
        assert next_monday() == date(year=2025, month=6, day=9)

        assert next_weekday(target=Day.TUESDAY) == date(year=2025, month=6, day=10)
        assert next_tuesday() == date(year=2025, month=6, day=10)

        assert next_weekday(target=Day.WEDNESDAY) == date(year=2025, month=6, day=11)
        assert next_wednesday() == date(year=2025, month=6, day=11)

    def test_tomorrow_with_date(self):
        from_date = date(year=2025, month=7, day=8)

        assert next_weekday(from_date=from_date, target=Day.WEDNESDAY) == date(
            year=2025, month=7, day=9
        )
        assert next_wednesday(from_date=from_date) == date(year=2025, month=7, day=9)

        assert next_weekday(from_date=from_date, target=Day.THURSDAY) == date(
            year=2025, month=7, day=10
        )
        assert next_thursday(from_date=from_date) == date(year=2025, month=7, day=10)

        assert next_weekday(from_date=from_date, target=Day.FRIDAY) == date(
            year=2025, month=7, day=11
        )
        assert next_friday(from_date=from_date) == date(year=2025, month=7, day=11)

        assert next_weekday(from_date=from_date, target=Day.SATURDAY) == date(
            year=2025, month=7, day=12
        )
        assert next_saturday(from_date=from_date) == date(year=2025, month=7, day=12)

        assert next_weekday(from_date=from_date, target=Day.SUNDAY) == date(
            year=2025, month=7, day=13
        )
        assert next_sunday(from_date=from_date) == date(year=2025, month=7, day=13)

        assert next_weekday(from_date=from_date, target=Day.MONDAY) == date(
            year=2025, month=7, day=14
        )
        assert next_monday(from_date=from_date) == date(year=2025, month=7, day=14)

        assert next_weekday(from_date=from_date, target=Day.TUESDAY) == date(
            year=2025, month=7, day=15
        )
        assert next_tuesday(from_date=from_date) == date(year=2025, month=7, day=15)
