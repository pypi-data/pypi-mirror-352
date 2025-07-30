from datetime import date
from unittest.mock import patch

from timecraftx.utils import ensure_date


@ensure_date
def identity_function(from_date: date) -> date:
    return from_date


def test_ensure_date_with_explicit_date():
    fixed_date = date(2020, 1, 1)
    result = identity_function(fixed_date)
    assert result == fixed_date


@patch("timecraftx.utils.date")
def test_ensure_date_defaults_to_today(mock_date):
    mock_date.today.return_value = date(2021, 12, 25)
    result = identity_function(None)
    assert result == date(2021, 12, 25)
