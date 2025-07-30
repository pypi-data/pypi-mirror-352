from datetime import date
from unittest.mock import MagicMock, patch

from timecraftx import start_of_week
from timecraftx.day import Day

FIXED_TODAY = date(year=1998, month=6, day=11)


class TestStartOfWeek:
    @patch("timecraftx.utils.date")
    def test_start_of_week(self, mock_date: MagicMock):
        mock_date.today.return_value = FIXED_TODAY
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        start_of_week_date = start_of_week()
        assert start_of_week_date == date(year=1998, month=6, day=8)

        start_of_week_date = start_of_week(week_start=Day.SUNDAY)
        assert start_of_week_date == date(year=1998, month=6, day=7)

    def test_start_of_week_from_date(self):
        from_date = date(year=2025, month=6, day=12)

        start_of_week_date = start_of_week(from_date=from_date)
        assert start_of_week_date == date(year=2025, month=6, day=9)

        start_of_week_date = start_of_week(from_date=from_date, week_start=Day.SUNDAY)
        assert start_of_week_date == date(year=2025, month=6, day=8)
