class DurationParsingException(ValueError):
    ...


class IncorrectPattern(DurationParsingException):
    def __init__(self):
        super().__init__("The pattern is incorrect")


class IncorrectValue(DurationParsingException):
    def __init__(self):
        super().__init__("Value must be positive integer")
