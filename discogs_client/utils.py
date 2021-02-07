from datetime import datetime
from urllib.parse import quote
from urllib.error import HTTPError
from discogs_client.exceptions import TooManyAttemptsError
from time import sleep
from random import uniform


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


def jitter(delay: int) -> int:
    return uniform(0, delay)


def get_backoff_duration(exponent: int) -> int:
    sleep_duration = 2 ** exponent
    return jitter(sleep_duration)


def backoff(enabled: bool = True):
    def inner(f):
        MAX_ATTEMPTS = 100

        def wrapper(*args, **kwargs):

            if not enabled:
                return f(*args, **kwargs)

            result = None
            attempts = 0
            while True:
                attempts += 1
                result = f(*args, **kwargs)

                if result.status_code != 429:
                    return result
                elif attempts == MAX_ATTEMPTS:
                    raise TooManyAttemptsError

                duration = get_backoff_duration(attempts)
                sleep(duration)

            return result
        return wrapper
    return inner
