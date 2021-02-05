from datetime import datetime
from urllib.parse import quote
from urllib.error import HTTPError
from time import sleep
from random import uniform


# Not global unless own module?
rate_limit_total = 0
rate_limit_used = 0
rate_limit_remaining = 0


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


"""
TODO: Perhaps move to class
        - To find out, does a new class get created every function call?
        - If this class gets created once, then perhaps it is fine
class RequestDecorator:
    def __init__(self, function):
        self._function = function
        self.rate_limit_available = 0
        self.rate_limit_used = 0
        self.rate_limit_remaining = 0

    def __call__(self, *args, **kwargs):
        result = self._function(*args, **kwargs)
        return result
"""


def jitter(delay: int) -> int:
    return uniform(0, delay)

def get_backoff_duration(exponent: int) -> int:
    sleep_duration = 2 ** exponent
    return jitter(sleep_duration)

def backoff(f):
    def wrapper(*args, **kwargs):
        # TODO: Don't particularly like the use of global variables
        global rate_limit_total
        global rate_limit_used
        global rate_limit_remaining

        attempts = 0
        # TODO: Don't particularly like the use of infinite loop
        while True:
            attempts += 1

            try:
                result = f(*args, **kwargs)
            except HTTPError as e:
                # Only capture rate limiting status codes
                if e.response.status_code != 429:
                    raise e
                # elif MAX_ATTEMPTS == attempts:
                    # raise TooManyAttemptsError

                # Wait
                duration = get_backoff_duration()
                sleep(duration)
                # How to incoporate the headers? Do we need them?
                rate_limit_total = result.headers.get("X-Discogs-Ratelimit")
                rate_limit_used = result.headers.get("X-Discogs-Ratelimit-Used")
                rate_limit_remaining = result.headers.get("X-Discogs-Ratelimit-Remaining")
                # Try again
                continue
            else:
                break

        return result

    return wrapper
