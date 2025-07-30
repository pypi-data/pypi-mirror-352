from datetime import date
from unittest.mock import MagicMock, patch

from pytest import raises

from timecraftx.day import Day
from timecraftx.utils import normalize_week_inputs

FIXED_TODAY = date(year=2017, month=12, day=18)


class TestNormalizeWeekInputs:
    @patch("timecraftx.utils.date")
    def test_validate_normalized_inputs(self, mock_date: MagicMock):
        mock_date.today.return_value = FIXED_TODAY
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)

        from_date, weekday = normalize_week_inputs()
        assert from_date == FIXED_TODAY
        assert weekday == 0
        mock_date.today.assert_called_once()

        from_date, weekday = normalize_week_inputs(week_start=Day.SUNDAY)
        assert from_date == FIXED_TODAY
        assert weekday == 1

    def test_validate_normalized_inputs_with_date(self):
        custom_date = date(year=2025, month=6, day=11)
        from_date, weekday = normalize_week_inputs(from_date=custom_date)
        assert from_date == custom_date
        assert weekday == 2

        from_date, weekday = normalize_week_inputs(
            from_date=custom_date, week_start=Day.SUNDAY
        )
        assert from_date == custom_date
        assert weekday == 3

    def test_validate_normalized_inputs_exceptions(self):
        with raises(ValueError):
            normalize_week_inputs(week_start="monday")

        with raises(ValueError):
            normalize_week_inputs(week_start=Day.THURSDAY)
