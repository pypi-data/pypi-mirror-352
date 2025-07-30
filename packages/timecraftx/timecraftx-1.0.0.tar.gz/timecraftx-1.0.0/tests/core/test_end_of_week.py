from datetime import date
from unittest.mock import MagicMock, patch

from timecraftx import end_of_week
from timecraftx.day import Day

FIXED_TODAY = date(year=1998, month=6, day=11)


class TestEndOfWeek:
    @patch("timecraftx.utils.date")
    def test_end_of_week(self, mock_date: MagicMock):
        mock_date.today.return_value = FIXED_TODAY
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        end_of_week_date = end_of_week()
        assert end_of_week_date == date(year=1998, month=6, day=14)

        end_of_week_date = end_of_week(week_start=Day.SUNDAY)
        assert end_of_week_date == date(year=1998, month=6, day=13)

    def test_start_of_week_from_date(self):
        from_date = date(year=2025, month=6, day=12)

        end_of_week_date = end_of_week(from_date=from_date)
        assert end_of_week_date == date(year=2025, month=6, day=15)

        end_of_week_date = end_of_week(from_date=from_date, week_start=Day.SUNDAY)
        assert end_of_week_date == date(year=2025, month=6, day=14)
