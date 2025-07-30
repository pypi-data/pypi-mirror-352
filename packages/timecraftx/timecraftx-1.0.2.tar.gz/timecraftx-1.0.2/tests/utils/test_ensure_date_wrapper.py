from datetime import date
from unittest.mock import MagicMock, patch

from timecraftx.utils import ensure_date

FIXED_TODAY = date(year=2021, month=12, day=25)


@ensure_date
def identity_function(from_date: date) -> date:
    return from_date


class TestEnsureDate:
    @patch("timecraftx.utils.date")
    def test_defaults_to_today(self, mock_date: MagicMock):
        mock_date.today.return_value = FIXED_TODAY
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        result = identity_function()
        assert result == FIXED_TODAY

    def test_with_explicit_date(self):
        custom_date = date(year=2020, month=1, day=1)
        result = identity_function(custom_date)
        assert result == custom_date
