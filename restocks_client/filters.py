from enum import IntEnum, StrEnum


class ListingDuration(IntEnum):
    Days30 = 30
    Days60 = 60
    Days90 = 90


class SellMethod(StrEnum):
    Consign = "consignment"
    Resell = "resale"


class AutoMode(StrEnum):
    Auto = "auto"
    Auto2 = "auto2"
