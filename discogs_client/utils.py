try:
    from enum import member
except ImportError:
    def member(func):
        return func

from datetime import datetime
from dateutil.parser import parse
from urllib.parse import quote
from discogs_client.exceptions import TooManyAttemptsError
from time import sleep
from random import uniform
from functools import wraps
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


def jitter(delay: int) -> float:
    return uniform(0, delay)


def get_backoff_duration(exponent: int) -> float:
    sleep_duration = 2 ** exponent
    return jitter(sleep_duration)


def backoff(f):
    """
    Wraps the request method of the Fetcher class to provide
    exponential backoff if rate limit is hit.
    """
    @wraps(f)
    def wrapper(self, *args, **kwargs):

        MAX_ATTEMPTS = 100

        if not hasattr(self, "backoff_enabled"):
            raise AttributeError(
                "backoff decorator needs class with the decorated method "
                "to have backoff_enabled attribute."
            )

        if not self.backoff_enabled:
            return f(self, *args, **kwargs)

        for i in range(0, MAX_ATTEMPTS):
            result = f(self, *args, **kwargs)

            if result.status_code != 429:
                return result

            duration = get_backoff_duration(i)
            sleep(duration)

        # Max attempts reached without returning, raise error
        raise TooManyAttemptsError

    return wrapper


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
    @member
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

    @member
    class Order(Enum):
        ASCENDING = 'asc'
        DESCENDING = 'desc'

    # Return value of the child Enum item
    def __getattr__(self, item):
        if item != '_value_':
            return getattr(self.value, item).value
        raise AttributeError
