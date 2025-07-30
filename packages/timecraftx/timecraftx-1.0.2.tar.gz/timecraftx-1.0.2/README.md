# ⏳ Timecraftx

**Lightweight, readable, and powerful date utilities for Python.**  
Get common date calculations like `start_of_week`, `end_of_week`, `yesterday`, `tomorrow`, or even `next_friday` and `prev_monday` — with beautiful, clean code.

---

## 🔧 Features

- ✅ `start_of_week()` and `end_of_week()` with customizable week start (Sunday or Monday)
- ✅ `yesterday()` and `tomorrow()` with optional reference date
- ✅ `next_weekday()` and `prev_weekday()` with helpers like `next_monday()`, `prev_sunday()`, etc.
- ✅ Works with `date` objects directly (no timezone mess)
- ✅ Enum-based safety for weekdays via `Day`
- ✅ Fully tested, no external dependencies

---

## 📦 Installation

```bash
pip install timecraftx
```

---

## 🚀 Quickstart

```python
from datetime import date
from timecraftx import (
    start_of_week, end_of_week, yesterday, tomorrow,
    next_friday, prev_monday, Day
)

today = date(2025, 6, 4)

print(start_of_week(today))               # 2025-06-02 (Monday)
print(end_of_week(today))                 # 2025-06-08 (Sunday if Monday is week start)

print(yesterday(today))                   # 2025-06-03
print(tomorrow(today))                    # 2025-06-05

print(next_friday(today))                 # 2025-06-06
print(prev_monday(today))                 # 2025-06-02
```

---

## 📘 API Reference

### Week Utilities

#### `start_of_week(from_date: Optional[date] = None, week_start: Day = Day.MONDAY) -> date`

Returns the first day of the week. Defaults to today and Monday.

#### `end_of_week(from_date: Optional[date] = None, week_start: Day = Day.MONDAY) -> date`

Returns the last day of the week (6 days after `start_of_week`).

---

### Relative Days

#### `yesterday(from_date: Optional[date] = None) -> date`

Returns the day before the given date.

#### `tomorrow(from_date: Optional[date] = None) -> date`

Returns the day after the given date.

---

### Next Weekday Utilities

#### `next_weekday(from_date: Optional[date] = None, target: Day = Day.MONDAY) -> date`

Returns the next occurrence of a specific weekday.

#### Day-specific helpers:
- `next_monday()`
- `next_tuesday()`
- `next_wednesday()`
- `next_thursday()`
- `next_friday()`
- `next_saturday()`
- `next_sunday()`

---

### Previous Weekday Utilities

#### `prev_weekday(from_date: Optional[date] = None, target: Day = Day.MONDAY) -> date`

Returns the most recent past occurrence of a specific weekday.

#### Day-specific helpers:
- `prev_monday()`
- `prev_tuesday()`
- `prev_wednesday()`
- `prev_thursday()`
- `prev_friday()`
- `prev_saturday()`
- `prev_sunday()`

---

### Enum

#### `Day`

Enum values for each day of the week, from `Day.MONDAY` to `Day.SUNDAY`.

---

## 🛡️ License

MIT License. See [LICENSE](./LICENSE).

---

## 👤 Author

**Jacobo Tapia**  
GitHub: [@Jatapiaro](https://github.com/Jatapiaro)  
Project: [https://github.com/Jatapiaro/timecraftx](https://github.com/Jatapiaro/timecraftx)

---

## 🌟 Contribute

Found a bug or have an idea? PRs welcome. Open an issue or submit a patch.
