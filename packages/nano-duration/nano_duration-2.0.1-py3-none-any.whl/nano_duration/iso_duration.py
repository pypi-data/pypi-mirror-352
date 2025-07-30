from __future__ import annotations

import re

from nano_duration.duration import Duration
from nano_duration.exceptions import IncorrectPattern

ISO8601_PERIOD_REGEX = re.compile(
    r"P(?!\b)"
    r"(?P<years>\d(\d+)?Y)?"
    r"(?P<months>\d(\d+)?M)?"
    r"(?P<days>\d(\d+)?D)?"
    r"((?P<separator>T)(?P<hours>\d+(\d+)?H)?"
    r"(?P<minutes>\d(\d+)?M)?"
    r"(?P<seconds>\d(\d+)?S)?"
    r"(?P<miliseconds>\d(\d+)?m)?"
    r"(?P<microseconds>\d+(\d+)?u)?"
    r"(?P<nanoseconds>\d+(\d+)?n)?)?$"
)


def generate(duration: Duration) -> str:
    duration_dict = duration.__dict__
    _ = (
        lambda key, symbol: f"{duration_dict[key]}{symbol}"
        if duration_dict.get(key, 0) > 0
        else ""
    )
    _date = "P" + "".join([_("years", "Y"), _("months", "M"), _("days", "D")])

    _time = "".join(
        [
            _("hours", "H"),
            _("minutes", "M"),
            _("seconds", "S"),
            _("miliseconds", "m"),
            _("microseconds", "u"),
            _("nanoseconds", "n"),
        ]
    )
    if _time:
        _time = "T" + _time
    return f"{_date}{_time}"


def parse(duration: str) -> Duration:
    match = ISO8601_PERIOD_REGEX.match(duration)
    if duration[-1] == "T":
        raise IncorrectPattern()
    if match:
        group = match.groupdict()
        duration_dict = {
            key: int(value[:-1]) if value and value[:-1] else 0
            for key, value in group.items()
        }
        duration_dict.pop("separator", None)
    else:
        raise IncorrectPattern()
    return Duration(**duration_dict)
