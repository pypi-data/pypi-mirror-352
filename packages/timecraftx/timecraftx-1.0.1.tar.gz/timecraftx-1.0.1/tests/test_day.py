from pytest import raises

from timecraftx.day import Day


class TestDay:
    def test_day_from_num(self):
        valid_days = {
            0: Day.MONDAY,
            1: Day.TUESDAY,
            2: Day.WEDNESDAY,
            3: Day.THURSDAY,
            4: Day.FRIDAY,
            5: Day.SATURDAY,
            6: Day.SUNDAY,
        }

        for num, day in valid_days.items():
            assert Day.day_from_num(value=num) == day

        with raises(ValueError):
            Day.day_from_num(value=-1)
            Day.day_from_num(value=7)

    def test_day_from_str(self):
        valid_days = {
            "MONDAY": Day.MONDAY,
            "tuESDay": Day.TUESDAY,
            "wednesday": Day.WEDNESDAY,
            "THURSDAY": Day.THURSDAY,
            "FRiDAy": Day.FRIDAY,
            "saturday": Day.SATURDAY,
            "SUNDAY": Day.SUNDAY,
        }

        for name, day in valid_days.items():
            assert Day.day_from_str(value=name) == day

        with raises(ValueError):
            Day.day_from_str(value="juevebes")
            Day.day_from_str(value="catursday")
