from datetime import datetime
from urllib.parse import quote
from discogs_client.exceptions import TooManyAttemptsError
from time import sleep
from random import uniform
from functools import wraps


def parse_timestamp(timestamp):
    """Convert an ISO 8601 timestamp into a datetime."""
    return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')


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
