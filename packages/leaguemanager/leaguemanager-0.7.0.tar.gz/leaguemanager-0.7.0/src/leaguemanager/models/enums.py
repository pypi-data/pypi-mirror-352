from enum import Enum


class FixtureStatus(str, Enum):
    P = "Played"
    U = "Unplayed"
    F = "Forfeit"
    A = "Abandoned"
    D = "Postponed"


class FixtureResult(str, Enum):
    W = "Win"
    D = "Draw"
    L = "Loss"
    F = "Forfeit"
    S = "Suspended"
    N = "None"


class Category(str, Enum):
    """League categories."""

    MEN = "Men's"
    WOMEN = "Women's"
    COED = "Coed"


class Division(str, Enum):
    """League divisions."""

    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    H = "H"


class MatchDay(str, Enum):
    """Day of week."""

    MON = "Monday"
    TUE = "Tuesday"
    WED = "Wednesday"
    THU = "Thursday"
    FRI = "Friday"
    SAT = "Saturday"
    SUN = "Sunday"


class Gender(str, Enum):
    """Gender."""

    M = "Male"
    F = "Female"
    NB = "Non-Binary"
    O = "Other"  # noqa: E741
    P = "Prefer not to say"


class Field(str, Enum):
    """Field of play."""

    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    H = "H"
    I = "I"  # noqa: E741
    J = "J"
    K = "K"
    L = "L"
