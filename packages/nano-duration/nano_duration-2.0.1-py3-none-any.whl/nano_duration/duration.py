from decimal import Decimal

from nano_duration import calendar, iso_duration
from nano_duration.exceptions import IncorrectValue


class Duration(object):
    def __init__(
        self,
        years: float = 0,
        months: float = 0,
        days: float = 0,
        hours: float = 0,
        minutes: float = 0,
        seconds: float = 0,
        miliseconds: float = 0,
        microseconds: float = 0,
        nanoseconds: float = 0,
    ):
        self.years = years
        self.months = months
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.miliseconds = miliseconds
        self.microseconds = microseconds
        self.nanoseconds = nanoseconds

    def get_seconds(self) -> Decimal:
        days_seconds = (
            Decimal(self.years) * Decimal(calendar.SECONDS_IN_YEAR)
            + Decimal(self.months) * Decimal(calendar.SECONDS_IN_MONTH)
            + Decimal(self.days) * Decimal(calendar.SECONDS_IN_DAY)
            + Decimal(self.hours) * Decimal(calendar.SECONDS_IN_HOUR)
            + Decimal(self.minutes) * Decimal(calendar.SECONDS_IN_MINUTE)
            + Decimal(self.seconds)
            + Decimal(self.miliseconds) * Decimal(calendar.SECONDS_IN_MILI)
            + Decimal(self.microseconds) * Decimal(calendar.SECONDS_IN_MICRO)
            + Decimal(self.nanoseconds) * Decimal(calendar.SECONDS_IN_NANO)
        )
        return days_seconds

    def __setattr__(self, key, value):
        if isinstance(value, int) and value >= 0:
            super(Duration, self).__setattr__(key, value)
        else:
            raise IncorrectValue()

    def __str__(self):
        return iso_duration.generate(self)

    def __repr__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        if isinstance(other, Duration):
            return self.get_seconds() == other.get_seconds()
        else:
            return self.get_seconds() == other

    def __gt__(self, other):
        if isinstance(other, Duration):
            return self.get_seconds() > other.get_seconds()
        else:
            return self.get_seconds() > other

    def __lt__(self, other):
        if isinstance(other, Duration):
            return self.get_seconds() < other.get_seconds()
        return self.get_seconds() < other

    def __ge__(self, other):
        if isinstance(other, Duration):
            return self.get_seconds() >= other.get_seconds()
        return self.get_seconds() >= other

    def __le__(self, other):
        if isinstance(other, Duration):
            return self.get_seconds() <= other.get_seconds()
        return self.get_seconds() <= other

    def __hash__(self):
        """
        Return a hash of this instance so that it can be used in, for
        example, dicts and sets.
        """
        return hash(self.get_seconds())
