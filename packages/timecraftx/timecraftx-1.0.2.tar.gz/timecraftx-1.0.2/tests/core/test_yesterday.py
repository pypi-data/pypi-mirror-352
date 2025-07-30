from datetime import date
from unittest.mock import MagicMock, patch

from timecraftx import yesterday

FIXED_TODAY = date(year=2017, month=12, day=18)


class TestYesterday:
    @patch("timecraftx.utils.date")
    def test_yesterday(self, mock_date: MagicMock):
        mock_date.today.return_value = FIXED_TODAY
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        result = yesterday()
        assert result == date(year=2017, month=12, day=17)

    def test_yesterday_with_date(self):
        result = yesterday(from_date=date(year=2016, month=10, day=4))
        assert result == date(year=2016, month=10, day=3)
