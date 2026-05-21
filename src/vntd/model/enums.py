from enum import Enum


class SellerType(Enum):
    BUSINESS = "business"
    INDIVIDUAL = "individual"
    ALL = "all"


class Sort(Enum):
    RELEVANCE = "relevance"
    NEWEST = "newest_first"
    PRICE_LOW_TO_HIGH = "price_low_to_high"
    PRICE_HIGH_TO_LOW = "price_high_to_low"
