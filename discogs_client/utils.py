from datetime import datetime
from dateutil.parser import parse
from urllib.parse import quote
from enum import Enum


def parse_timestamp(timestamp: str) -> datetime:
    """Convert an ISO 8601 timestamp into a datetime."""
    return parse(timestamp)


def update_qs(url, params):
    """A not-very-intelligent function to glom parameters onto a query string."""
    joined_qs = '&'.join('='.join((str(k), quote(str(v))))
                         for k, v in params.items())
    separator = '&' if '?' in url else '?'
    return url + separator + joined_qs


def omit_none(dict_):
    """Removes any key from a dict that has a value of None."""
    return {k: v for k, v in dict_.items() if v is not None}


class Condition(Enum):
    """Conditions for media and sleeve"""
    MINT = 'Mint (M)'
    NEAR_MINT = 'Near Mint (NM or M-)'
    VERY_GOOD_PLUS = 'Very Good Plus (VG+)'
    VERY_GOOD = 'Very Good (VG)'
    GOOD_PLUS = 'Good Plus (G+)'
    GOOD = 'Good (G)'
    FAIR = 'Fair (F)'
    POOR = 'Poor (P)'
    # Special conditions for sleeve only
    GENERIC = 'Generic'
    NOT_GRADED = 'Not Graded'
    NO_COVER = 'No Cover'

    def __get__(self, object, type):
        return self.value


class Status(Enum):
    """Status for a listing"""
    FOR_SALE = 'For Sale'
    DRAFT = 'Draft'
    EXPIRED = 'Expired'

    def __get__(self, object, type):
        return self.value


class Sort(Enum):
    class By(Enum):
        ADDED = 'added'
        ARTIST = 'artist'
        AUDIO = 'audio'
        BUYER = 'buyer'
        COUNTRY = 'country'
        CREATED = 'created'
        CATALOG_NUMBER = 'catno'
        FORMAT = 'format'
        ID = 'id'
        ITEM = 'item'
        LABEL = 'label'
        LAST_ACTIVITY = 'last_activity'
        LISTED = 'listed'
        LOCATION = 'location'
        PRICE = 'price'
        RELEASED = 'released'
        STATUS = 'status'
        TITLE = 'title'
        YEAR = 'year'

    class Order(Enum):
        ASCENDING = 'asc'
        DESCENDING = 'desc'

    # Return value of the child Enum item
    def __getattr__(self, item):
        if item != '_value_':
            return getattr(self.value, item).value
        raise AttributeError
