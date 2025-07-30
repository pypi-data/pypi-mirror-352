# 📋 Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),  
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [1.0.0] - 2025-06-04

### Added
- New `@ensure_date` decorator to automatically default `from_date` to `today` if `None`.
- `next_weekday()` function to compute the next occurrence of a given weekday.
- Convenience functions: `next_monday()`, `next_tuesday()`, ..., `next_sunday()`.
- `prev_weekday()` function to compute the previous occurrence of a given weekday.
- Convenience functions: `prev_monday()`, `prev_tuesday()`, ..., `prev_sunday()`.
- Full unit test coverage for all weekday-related functions.
- Improved docstrings across all core functions and decorators.

### Changed
- Updated `__init__.py` to expose all new weekday functions and the `Day` enum via `__all__`.

### Fixed
- Corrected tests to use fixed dates and mocked `date.today()` for deterministic results.

## [0.5.1] - 2025-05-30

### Changed
- Renamed project from `timecraft` to `timecraftx` due to namespace conflict on PyPI.

## [0.5.0] - 2025-05-30

### Added
- `start_of_week(from_date, week_start)` to calculate week start from a given date.
- `end_of_week(from_date, week_start)` to get the week's end.
- `yesterday(from_date)` and `tomorrow(from_date)` for simple date deltas.
- `Day` enum for explicit weekday handling.
- Internal normalization utilities (`_normalize_week_inputs`, `_add_days_to_date`).
- Full test coverage using `pytest`.

---

### Planned
- `week_of`, `weeks_between`.
- `first_day_of_month`, `last_day_of_month`.