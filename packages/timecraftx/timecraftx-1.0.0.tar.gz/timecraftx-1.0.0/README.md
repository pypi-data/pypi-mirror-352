# ⏳ Timecraftx

**Lightweight, readable, and powerful date utilities for Python.**  
Get common date calculations like `start_of_week`, `end_of_week`, `yesterday`, and `tomorrow`—with beautiful, clean code.

---

## 🔧 Features

- ✅ `start_of_week()` and `end_of_week()` with customizable week start (Sunday or Monday)
- ✅ `yesterday()` and `tomorrow()` with optional reference date
- ✅ Works with `date` objects directly (no timezone mess)
- ✅ Enum-based safety for weekdays
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
from timecraftx import start_of_week, end_of_week, yesterday, tomorrow, Day

today = date(2024, 5, 30)

print(start_of_week(today))                          # Monday of the current week
print(start_of_week(today, week_start=Day.SUNDAY))   # Sunday of the current week

print(end_of_week(today))                            # Saturday (if week starts Monday)
print(yesterday(today))                              # 2024-05-29
print(tomorrow(today))                               # 2024-05-31
```

---

## 📘 API Reference

### `start_of_week(from_date: Optional[date] = None, week_start: Day = Day.MONDAY) -> date`

Returns the first day of the week for a given date. Defaults to today and Monday as the first day.

### `end_of_week(from_date: Optional[date] = None, week_start: Day = Day.MONDAY) -> date`

Returns the last day of the week (6 days after `start_of_week`).

### `tomorrow(from_date: Optional[date] = None) -> date`

Returns the next day.

### `yesterday(from_date: Optional[date] = None) -> date`

Returns the previous day.

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
