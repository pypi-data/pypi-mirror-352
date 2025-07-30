from enum import Enum

from timecraftx.constants import WEEKDAY_NAME_TO_NUM


class Day(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    @classmethod
    def day_from_str(cls, value: str) -> "Day":
        """
        Converts a weekday string (e.g., 'monday') into a Day enum.

        Args:
            value: A string representing the day of the week.

        Returns:
            A Day enum member corresponding to the given string.

        Raises:
            ValueError: If the string is not a valid day.
        """
        value = value.lower()
        if value not in WEEKDAY_NAME_TO_NUM:
            raise ValueError(f"Invalid weekday name: {value}")

        return Day.day_from_num(value=WEEKDAY_NAME_TO_NUM[value])

    @classmethod
    def day_from_num(cls, value: int) -> "Day":
        """
        Converts a number (0 - 6) into a Day enum.

        Args:
            value: An integer between 0 (Monday) and 6 (Sunday).

        Returns:
            A Day enum member corresponding to the given number.

        Raises:
            ValueError: If the number is not in the range 0 - 6.
        """
        if value == 0:
            return Day.MONDAY
        elif value == 1:
            return Day.TUESDAY
        elif value == 2:
            return Day.WEDNESDAY
        elif value == 3:
            return Day.THURSDAY
        elif value == 4:
            return Day.FRIDAY
        elif value == 5:
            return Day.SATURDAY
        elif value == 6:
            return Day.SUNDAY
        else:
            raise ValueError(f"Invalid day number: {value}")
