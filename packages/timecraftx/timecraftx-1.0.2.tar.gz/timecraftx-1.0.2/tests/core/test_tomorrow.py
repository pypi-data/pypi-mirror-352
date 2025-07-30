from datetime import date
from unittest.mock import MagicMock, patch

from timecraftx import tomorrow

FIXED_TODAY = date(year=2017, month=12, day=18)


class TestTomorrow:
    @patch("timecraftx.utils.date")
    def test_tomorrow(self, mock_date: MagicMock):
        mock_date.today.return_value = FIXED_TODAY
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        result = tomorrow()
        assert result == date(year=2017, month=12, day=19)

    def test_tomorrow_with_date(self):
        result = tomorrow(from_date=date(year=2016, month=10, day=4))
        assert result == date(year=2016, month=10, day=5)
