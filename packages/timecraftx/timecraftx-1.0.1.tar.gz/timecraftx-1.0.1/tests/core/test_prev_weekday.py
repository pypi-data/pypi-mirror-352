from datetime import date
from unittest.mock import MagicMock, patch

from timecraftx import (
    Day,
    prev_friday,
    prev_monday,
    prev_saturday,
    prev_sunday,
    prev_thursday,
    prev_tuesday,
    prev_wednesday,
    prev_weekday,
)

FIXED_TODAY = date(year=2025, month=6, day=4)


class TestPrevWeekDay:
    @patch("timecraftx.utils.date")
    def test_prev_weekday_default(self, mock_date: MagicMock):
        mock_date.today.return_value = FIXED_TODAY
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        assert prev_weekday(target=Day.THURSDAY) == date(year=2025, month=5, day=29)
        assert prev_thursday() == date(year=2025, month=5, day=29)

        assert prev_weekday(target=Day.FRIDAY) == date(year=2025, month=5, day=30)
        assert prev_friday() == date(year=2025, month=5, day=30)

        assert prev_weekday(target=Day.SATURDAY) == date(year=2025, month=5, day=31)
        assert prev_saturday() == date(year=2025, month=5, day=31)

        assert prev_weekday(target=Day.SUNDAY) == date(year=2025, month=6, day=1)
        assert prev_sunday() == date(year=2025, month=6, day=1)

        assert prev_weekday(target=Day.MONDAY) == date(year=2025, month=6, day=2)
        assert prev_monday() == date(year=2025, month=6, day=2)

        assert prev_weekday(target=Day.TUESDAY) == date(year=2025, month=6, day=3)
        assert prev_tuesday() == date(year=2025, month=6, day=3)

        assert prev_weekday(target=Day.WEDNESDAY) == date(year=2025, month=5, day=28)
        assert prev_wednesday() == date(year=2025, month=5, day=28)

    def test_prev_weekday_with_date(self):
        from_date = date(year=2025, month=7, day=8)

        assert prev_weekday(from_date=from_date, target=Day.WEDNESDAY) == date(
            year=2025, month=7, day=2
        )
        assert prev_wednesday(from_date=from_date) == date(year=2025, month=7, day=2)

        assert prev_weekday(from_date=from_date, target=Day.THURSDAY) == date(
            year=2025, month=7, day=3
        )
        assert prev_thursday(from_date=from_date) == date(year=2025, month=7, day=3)

        assert prev_weekday(from_date=from_date, target=Day.FRIDAY) == date(
            year=2025, month=7, day=4
        )
        assert prev_friday(from_date=from_date) == date(year=2025, month=7, day=4)

        assert prev_weekday(from_date=from_date, target=Day.SATURDAY) == date(
            year=2025, month=7, day=5
        )
        assert prev_saturday(from_date=from_date) == date(year=2025, month=7, day=5)

        assert prev_weekday(from_date=from_date, target=Day.SUNDAY) == date(
            year=2025, month=7, day=6
        )
        assert prev_sunday(from_date=from_date) == date(year=2025, month=7, day=6)

        assert prev_weekday(from_date=from_date, target=Day.MONDAY) == date(
            year=2025, month=7, day=7
        )
        assert prev_monday(from_date=from_date) == date(year=2025, month=7, day=7)

        assert prev_weekday(from_date=from_date, target=Day.TUESDAY) == date(
            year=2025, month=7, day=1
        )
        assert prev_tuesday(from_date=from_date) == date(year=2025, month=7, day=1)
