# nano_duration: Operations with ISO 8601 durations.

## What is this.

ISO 8601 is most commonly known as a way to exchange date-times in textual format.
to have more precision duration this package included milliseconds, microseconds, and nanoseconds
A lesser-known aspect of the standard is the representation of durations. They have a
shape similar to this:

```
P3Y6M4DT12H30M5S80m90u120n
```

which symbols defined as blow:<br />

```
"Y" -> "years"
"M" -> "months"
"D" -> "days"
"H" -> "hours"
"M" -> "minutes"
"S" -> "seconds"
"m" -> "miliseconds"
"u" -> "microseconds"
"n" -> "nanoseconds"
```

As this module maps ISO 8601 dates/times to standard Python data type.

### Parse:

parses an ISO 8601 duration string into Duration object.

```python
from nano_duration import parse

duration = parse("P3Y6M4DT12H24M12S10m80u12n")
```

### Generate:

generate a duration object into ISO 8601 duration string

```python
from nano_duration import Duration, generate

generate(
    Duration(
        years=3,
        months=2,
        days=3,
        hours=5,
        seconds=57,
        miliseconds=8,
        microseconds=30,
        nanoseconds=20,
    )
)
```